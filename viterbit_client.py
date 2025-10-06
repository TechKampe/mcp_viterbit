"""
Viterbit API client for MCP server.
Adapted from the original services/viterbit.py with focus on API operations.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from config import (
    VITERBIT_API_KEY, BASE_URL, DISCORD_ID_QUESTION_ID, SUSCRIPTOR_QUESTION_ID,
    CUSTOM_FIELD_STAGE_NAME_ID, CUSTOM_FIELD_STAGE_DATE_ID, ACTIVO_INACTIVO_ID,
    GARANTIA_100_DIAS_ID, DEFAULT_DISQUALIFIED_BY_ID, DEPARTMENT_LOOKUP,
    LOCATION_LOOKUP
)


class ViterbitAPIError(Exception):
    """Custom exception for Viterbit API errors."""
    pass


class ViterbitClient:
    """Viterbit API client for MCP server."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Viterbit client.

        Args:
            api_key: Viterbit API key. If not provided, will use VITERBIT_API_KEY env var.
        """
        self.api_key = api_key or VITERBIT_API_KEY
        if not self.api_key:
            raise ValueError("Viterbit API key is required. Set VITERBIT_API_KEY environment variable.")

        self.base_url = BASE_URL
        self.headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.timeout = httpx.Timeout(10.0)

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the Viterbit API.

        Args:
            method: HTTP method (GET, POST, PATCH, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments passed to httpx.request

        Returns:
            API response data

        Raises:
            ViterbitAPIError: If the API request fails
        """
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            try:
                response = await client.request(method, f"{self.base_url}/{endpoint}", **kwargs)
                response.raise_for_status()
                # Handle cases where response body might be empty on success
                return response.json() if response.content else {}
            except httpx.HTTPStatusError as e:
                error_msg = f"Viterbit API error on {method} {endpoint}: {e.response.status_code} - {e.response.text}"
                logging.error(error_msg)
                raise ViterbitAPIError(error_msg) from e
            except Exception as e:
                error_msg = f"Unexpected error calling Viterbit API on {method} {endpoint}: {e}"
                logging.error(error_msg)
                raise ViterbitAPIError(error_msg) from e

    # --- Candidate Management ---

    async def get_candidate_details(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Fetch full candidate details, including custom fields.

        Args:
            candidate_id: The candidate ID

        Returns:
            Candidate details or None if not found
        """
        try:
            response = await self._request(
                "GET",
                f"candidates/{candidate_id}",
                params={"includes[]": ["address", "custom_fields"]}
            )
            return response.get("data")
        except ViterbitAPIError:
            return None

    async def search_candidate(self, search_term: str) -> Optional[Dict[str, Any]]:
        """Search for a candidate by name, email, or phone number.

        Args:
            search_term: Candidate name, email address, or phone number

        Returns:
            Candidate basic info or None if not found
        """
        try:
            response = await self._request("POST", "candidates/search", json={"search": search_term})
            candidates = response.get("data", [])
            if candidates:
                candidate_data = candidates[0]
                return {
                    "id": candidate_data.get("id"),
                    "full_name": candidate_data.get("full_name", ""),
                    "email": candidate_data.get("email", ""),
                    "phone_number": candidate_data.get("phone", "")
                }
            return None
        except ViterbitAPIError:
            return None

    async def get_candidate_id_by_email(self, email: str) -> Optional[str]:
        """Retrieve a candidate's ID using their email address.

        Args:
            email: Candidate email address

        Returns:
            Candidate ID or None if not found
        """
        candidate = await self.search_candidate(email)
        return candidate["id"] if candidate else None

    async def get_candidate_with_viterbit_fields(self, email: str) -> Optional[Dict[str, Any]]:
        """Get candidate details including custom fields by email.

        Args:
            email: Candidate email address

        Returns:
            Enriched candidate data for filtering or None if not found
        """
        try:
            # First find the candidate by email
            candidate_id = await self.get_candidate_id_by_email(email)
            if not candidate_id:
                return None

            # Get full candidate details with custom fields
            candidate_details = await self.get_candidate_details(candidate_id)
            if not candidate_details:
                return None

            # Extract custom field values
            custom_fields = candidate_details.get("custom_fields", [])

            # Create a map of field IDs to values for easy lookup
            field_values = {}
            for field in custom_fields:
                field_id = field.get("reference_id")
                if field_id:
                    field_values[field_id] = field.get("value")

            # Extract the specific fields we need
            suscriptor = field_values.get(SUSCRIPTOR_QUESTION_ID)
            garantia_100_dias = field_values.get(GARANTIA_100_DIAS_ID)
            activo_inactivo = field_values.get(ACTIVO_INACTIVO_ID)

            # Extract city from address data
            address_data = candidate_details.get("address", {})
            city = address_data.get("city", "") if address_data else ""

            return {
                "id": candidate_details.get("id"),
                "full_name": candidate_details.get("full_name", ""),
                "email": candidate_details.get("email", email),
                "phone": candidate_details.get("phone", ""),
                "city": city,
                "suscriptor": suscriptor,
                "garantia_100_dias": garantia_100_dias,
                "activo_inactivo": activo_inactivo,
                "raw_custom_fields": custom_fields
            }
        except Exception as e:
            logging.error(f"Error getting candidate with Viterbit fields for {email}: {e}")
            return None

    async def update_candidate_custom_fields(self, candidate_id: str, fields_to_update: List[Dict]):
        """Update custom fields for a candidate.

        Args:
            candidate_id: The candidate ID
            fields_to_update: List of custom field updates
        """
        logging.info(f"Updating custom fields for candidate {candidate_id}")
        candidate_data = await self.get_candidate_details(candidate_id)
        if not candidate_data:
            raise ViterbitAPIError(f"Could not retrieve details for candidate {candidate_id}")

        existing_fields = candidate_data.get("custom_fields", [])

        # Create a map of existing fields using their reference_id as the key
        updated_fields_map = {
            field['reference_id']: {
                "type": field.get('type'),
                "question_id": field.get('reference_id'),
                "value": field.get('value')
            }
            for field in existing_fields if 'reference_id' in field
        }

        # Merge the fields that need to be updated
        for new_field in fields_to_update:
            field_id = new_field.get("question_id")
            if field_id:
                updated_fields_map[field_id] = new_field

        # Convert the map back to the list format the API expects
        final_custom_fields = list(updated_fields_map.values())

        await self._request("PATCH", f"candidates/{candidate_id}", json={"custom_fields": final_custom_fields})
        logging.info(f"Successfully updated custom fields for candidate {candidate_id}")

    async def update_candidate_discord_id(self, candidate_id: str, discord_id: str):
        """Update a candidate's Discord ID.

        Args:
            candidate_id: The candidate ID
            discord_id: Discord username/ID to set
        """
        await self.update_candidate_custom_fields(candidate_id, [{
            "type": "text",
            "question_id": DISCORD_ID_QUESTION_ID,
            "value": discord_id
        }])

    async def update_candidate_subscription_status(self, candidate_id: str, is_subscriber: bool = True):
        """Update a candidate's subscription status.

        Args:
            candidate_id: The candidate ID
            is_subscriber: Whether the candidate is a subscriber
        """
        await self.update_candidate_custom_fields(candidate_id, [{
            "type": "boolean",
            "question_id": SUSCRIPTOR_QUESTION_ID,
            "value": is_subscriber
        }])

    async def update_candidate_stage_fields(self, email: str, stage_name: str):
        """Update the stage name and date for a candidate.

        Args:
            email: Candidate email address
            stage_name: Stage name to set
        """
        candidate_id = await self.get_candidate_id_by_email(email)
        if not candidate_id:
            raise ViterbitAPIError(f"No candidate found in Viterbit with email: {email}")

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        await self.update_candidate_custom_fields(candidate_id, [
            {"type": "text", "question_id": CUSTOM_FIELD_STAGE_NAME_ID, "value": stage_name},
            {"type": "date", "question_id": CUSTOM_FIELD_STAGE_DATE_ID, "value": today_str}
        ])

    # --- Job Management ---

    async def get_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Fetch full job details, including custom fields.

        Args:
            job_id: The job ID

        Returns:
            Job details or None if not found
        """
        try:
            response = await self._request(
                "GET",
                f"jobs/{job_id}",
                params={"includes[]": ["custom_fields"]}
            )
            return response.get("data")
        except ViterbitAPIError:
            return None

    # --- Candidature Management ---

    async def find_active_candidatures_by_email(self, email: str) -> List[Dict[str, Any]]:
        """Find all active candidatures for a candidate by their email address.

        Args:
            email: Candidate email address

        Returns:
            List of active candidatures
        """
        try:
            search_payload = {"search": email}
            response = await self._request("POST", "candidatures/search", json=search_payload)
            candidatures = response.get("data", [])

            # Filter for active candidatures only
            active_candidatures = [
                candidature for candidature in candidatures
                if candidature.get("status") == "active"
            ]

            logging.info(f"Found {len(active_candidatures)} active candidatures for {email}")
            return active_candidatures

        except Exception as e:
            logging.error(f"Error finding active candidatures for {email}: {e}")
            return []

    async def disqualify_candidature(self, candidature_id: str, reason: str = "Baja Servicio") -> bool:
        """Disqualify a specific candidature.

        Args:
            candidature_id: The candidature ID to disqualify
            reason: Reason for disqualification

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current timestamp in ISO format
            disqualified_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

            payload = {
                "disqualified_info": {
                    "disqualified_at": disqualified_at,
                    "disqualified_by_id": DEFAULT_DISQUALIFIED_BY_ID,
                    "reason": reason
                }
            }

            await self._request("POST", f"candidatures/{candidature_id}/stage", json=payload)
            logging.info(f"Successfully disqualified candidature {candidature_id} with reason: {reason}")
            return True

        except Exception as e:
            logging.error(f"Error disqualifying candidature {candidature_id}: {e}")
            return False

    async def disqualify_active_candidatures_by_email(self, email: str) -> Dict[str, Any]:
        """Disqualify all active candidatures for a candidate by their email address.

        Args:
            email: Candidate email address

        Returns:
            Dictionary with results of the disqualification process
        """
        results = {
            "email": email,
            "candidatures_found": 0,
            "candidatures_disqualified": 0,
            "errors": []
        }

        try:
            # Find all active candidatures for this email
            active_candidatures = await self.find_active_candidatures_by_email(email)
            results["candidatures_found"] = len(active_candidatures)

            if not active_candidatures:
                logging.info(f"No active candidatures found for {email}")
                return results

            # Disqualify each active candidature
            for candidature in active_candidatures:
                candidature_id = candidature.get("id")
                if not candidature_id:
                    error_msg = f"Candidature missing ID: {candidature}"
                    results["errors"].append(error_msg)
                    continue

                success = await self.disqualify_candidature(candidature_id, "Baja Servicio")
                if success:
                    results["candidatures_disqualified"] += 1
                else:
                    error_msg = f"Failed to disqualify candidature {candidature_id}"
                    results["errors"].append(error_msg)

            logging.info(f"Disqualified {results['candidatures_disqualified']}/{results['candidatures_found']} candidatures for {email}")
            return results

        except Exception as e:
            error_msg = f"Error during candidature disqualification for {email}: {e}"
            logging.error(error_msg)
            results["errors"].append(error_msg)
            return results

    # --- Utility Functions ---

    async def get_custom_fields_definitions(self) -> Optional[Dict[str, Any]]:
        """Fetch all custom fields definitions from Viterbit API.

        Returns:
            Custom fields definitions or None if error
        """
        try:
            response = await self._request("GET", "custom-fields/candidate")
            return response
        except Exception as e:
            logging.error(f"Error fetching custom fields definitions: {e}")
            return None

    async def search_candidates_with_filters(self, filters: Dict[str, Any], page: int = 1, page_size: int = 50) -> Optional[Dict[str, Any]]:
        """Search candidates with custom field filters using POST candidates/search.

        Args:
            filters: Dictionary of custom field ID -> value filters
            page: Page number (default: 1)
            page_size: Number of results per page (default: 50)

        Returns:
            Search results with candidates or None if error
        """
        try:
            # Build the filter groups structure expected by Viterbit API
            filter_conditions = []

            for field_id, value in filters.items():
                if value is not None:
                    # Handle boolean values for custom fields
                    if isinstance(value, bool):
                        filter_value = "Sí" if value else "No"
                    else:
                        filter_value = value

                    # Check if this is an address field or custom field
                    if field_id.startswith("address__"):
                        # Address fields don't need custom_fields__ prefix
                        field_name = field_id
                    else:
                        # Custom fields need the custom_fields__ prefix
                        field_name = f"custom_fields__{field_id}"

                    filter_conditions.append({
                        "field": field_name,
                        "operator": "equals",
                        "value": filter_value
                    })

            # Build the request payload
            payload = {
                "filters": {
                    "groups": [
                        {
                            "operator": "and",
                            "filters": filter_conditions
                        }
                    ]
                },
                "page": page,
                "page_size": page_size,
                "search": None
            }

            response = await self._request("POST", "candidates/search", json=payload)
            return response
        except Exception as e:
            logging.error(f"Error searching candidates with filters: {e}")
            return None

    @staticmethod
    def should_include_candidate_in_report(viterbit_data: Dict[str, Any]) -> bool:
        """Determine if a candidate should be included in reports.

        Args:
            viterbit_data: Candidate data from Viterbit

        Returns:
            True if candidate should be included, False otherwise
        """
        if not viterbit_data:
            return True  # Include if no Viterbit data

        activo_inactivo = viterbit_data.get("activo_inactivo")

        # Only exclude if explicitly set to "Inactivo"
        if activo_inactivo == "Inactivo":
            return False

        # Include all others
        return True

    @staticmethod
    def get_department_mappings() -> Dict[str, str]:
        """Get department name to ID mappings.

        Returns:
            Dictionary mapping department names to IDs
        """
        return DEPARTMENT_LOOKUP.copy()

    @staticmethod
    def get_location_mappings() -> Dict[str, str]:
        """Get location name to ID mappings.

        Returns:
            Dictionary mapping location names to IDs
        """
        return LOCATION_LOOKUP.copy()

    @staticmethod
    def extract_discord_user(custom_fields: List[Dict]) -> str:
        """Extract the Discord username from a list of custom fields.

        Args:
            custom_fields: List of custom field dictionaries

        Returns:
            Discord username or "Not found" if not present
        """
        for field in custom_fields:
            if field.get("title") == "Usuario en Discord":
                return field.get("value", "Not found")
        return "Not found"

    async def get_candidature_with_stage_history(self, candidature_id: str) -> Optional[Dict[str, Any]]:
        """Get candidature details including stages history.

        Args:
            candidature_id: The candidature ID

        Returns:
            Candidature data with stages_history or None if not found
        """
        try:
            response = await self._request(
                "GET",
                f"candidatures/{candidature_id}",
                params={"includes[]": ["stages_history"]}
            )
            return response.get("data")
        except ViterbitAPIError:
            return None

    async def get_candidatures_changed_to_stage(self, stage_name: str, year: int, month: int) -> List[Dict[str, Any]]:
        """Get candidatures that changed to a specific stage during a given month.

        Args:
            stage_name: Name of the stage to filter by (e.g., "Match")
            year: Year to filter by
            month: Month to filter by (1-12)

        Returns:
            List of candidatures that changed to the specified stage in the given month
        """
        try:
            # Use candidatures/search to filter by current stage first
            all_matching_candidatures = []
            page = 1
            page_size = 100
            candidature_ids = []

            logging.info(f"Searching for candidatures in stage '{stage_name}' for {year}-{month:02d}")

            # Step 1: Get all candidature IDs that are currently in the target stage
            while True:
                payload = {
                    "filters": {
                        "groups": [
                            {
                                "operator": "and",
                                "filters": [
                                    {
                                        "field": "current_stage__name",
                                        "operator": "equals",
                                        "value": stage_name
                                    }
                                ]
                            }
                        ]
                    },
                    "page": page,
                    "page_size": page_size,
                    "search": None
                }

                response = await self._request(
                    "POST",
                    "candidatures/search",
                    json=payload
                )

                candidatures = response.get("data", [])
                if not candidatures:
                    break

                logging.info(f"Page {page}: Found {len(candidatures)} candidatures in stage '{stage_name}'")
                candidature_ids.extend([c.get("id") for c in candidatures if c.get("id")])

                # Check if there are more pages
                meta = response.get("meta", {})
                if not meta.get("has_more", False):
                    break

                page += 1

            if not candidature_ids:
                logging.info(f"No candidatures found in stage '{stage_name}'")
                return []

            logging.info(f"Total candidatures in '{stage_name}' stage: {len(candidature_ids)}")

            # Step 2: Fetch stage histories in parallel (batch of 10 at a time)
            batch_size = 10
            for i in range(0, len(candidature_ids), batch_size):
                batch = candidature_ids[i:i + batch_size]
                logging.info(f"Fetching stage history for batch {i//batch_size + 1} ({len(batch)} candidatures)...")

                # Fetch stage histories in parallel for this batch
                tasks = [self.get_candidature_with_stage_history(cid) for cid in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for detailed_candidature in results:
                    if isinstance(detailed_candidature, Exception) or not detailed_candidature:
                        continue

                    stages_history = detailed_candidature.get("stages_history", [])

                    # Find when this candidature changed to the target stage
                    for stage in stages_history:
                        if stage.get("stage_name") == stage_name:
                            start_at = stage.get("start_at")
                            if start_at:
                                try:
                                    # Parse the datetime string
                                    stage_date = datetime.fromisoformat(start_at.replace('Z', '+00:00'))
                                    if stage_date.year == year and stage_date.month == month:
                                        all_matching_candidatures.append({
                                            "candidature_id": detailed_candidature.get("id"),
                                            "candidate_id": detailed_candidature.get("candidate_id"),
                                            "job_id": detailed_candidature.get("job_id"),
                                            "stage_change_date": start_at,
                                            "stage_name": stage_name,
                                            "candidature": detailed_candidature
                                        })
                                        break  # Only count once per candidature
                                except (ValueError, TypeError) as e:
                                    logging.warning(f"Failed to parse date {start_at}: {e}")

            logging.info(f"Total candidatures changed to '{stage_name}' in {year}-{month:02d}: {len(all_matching_candidatures)}")
            return all_matching_candidatures

        except ViterbitAPIError as e:
            logging.error(f"Error fetching candidatures for stage tracking: {e}")
            return []

    async def count_candidatures_changed_to_stage(self, stage_name: str, year: int, month: int) -> int:
        """Count candidatures that changed to a specific stage during a given month.

        Args:
            stage_name: Name of the stage to filter by (e.g., "Match")
            year: Year to filter by
            month: Month to filter by (1-12)

        Returns:
            Number of candidatures that changed to the specified stage in the given month
        """
        matching_candidatures = await self.get_candidatures_changed_to_stage(stage_name, year, month)
        return len(matching_candidatures)

    async def get_candidatures_in_current_stage(self, stage_name: str, page: int = 1, page_size: int = 50) -> Optional[Dict[str, Any]]:
        """Get all candidatures currently in a specific stage.

        Args:
            stage_name: Name of the stage to filter by (e.g., "Match")
            page: Page number (default: 1)
            page_size: Number of results per page (default: 50, max: 100)

        Returns:
            Dict with candidatures data and metadata, or None if error
        """
        try:
            payload = {
                "filters": {
                    "groups": [
                        {
                            "operator": "and",
                            "filters": [
                                {
                                    "field": "current_stage__name",
                                    "operator": "equals",
                                    "value": stage_name
                                }
                            ]
                        }
                    ]
                },
                "page": page,
                "page_size": min(page_size, 100),
                "search": None
            }

            response = await self._request("POST", "candidatures/search", json=payload)
            return response
        except ViterbitAPIError as e:
            logging.error(f"Error fetching candidatures in current stage: {e}")
            return None

    async def count_candidatures_in_current_stage(self, stage_name: str) -> int:
        """Count candidatures currently in a specific stage.

        Args:
            stage_name: Name of the stage to filter by (e.g., "Match")

        Returns:
            Number of candidatures currently in the specified stage
        """
        result = await self.get_candidatures_in_current_stage(stage_name, page=1, page_size=1)
        if result:
            meta = result.get("meta", {})
            return meta.get("total", 0)
        return 0