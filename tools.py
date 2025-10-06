"""
MCP tools for Viterbit API functionality.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from mcp.types import Tool, TextContent
from typing import Any

from viterbit_client import ViterbitClient


class ViterbitTools:
    """MCP tools for Viterbit API operations."""

    def __init__(self, client: ViterbitClient):
        self.client = client

    def get_tools(self) -> List[Tool]:
        """Get all available MCP tools.

        Returns:
            List of MCP tool definitions
        """
        return [
            # Candidate Management Tools
            Tool(
                name="search_candidate",
                description="Search for a candidate by name, email address, or phone number. Returns basic candidate information including ID, name, email, and phone.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "search_term": {
                            "type": "string",
                            "description": "Candidate name, email address, or phone number to search for"
                        }
                    },
                    "required": ["search_term"]
                }
            ),
            Tool(
                name="get_candidate_details",
                description="Get full candidate details including custom fields and address information. Requires candidate ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "candidate_id": {
                            "type": "string",
                            "description": "The Viterbit candidate ID"
                        }
                    },
                    "required": ["candidate_id"]
                }
            ),
            Tool(
                name="get_candidate_with_filters",
                description="Get candidate details with enriched filtering data including subscription status, activity status, and location info. Useful for subscriber reports and filtering.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email address of the candidate"
                        }
                    },
                    "required": ["email"]
                }
            ),
            Tool(
                name="update_candidate_discord_id",
                description="Update a candidate's Discord username/ID in their custom fields.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "candidate_id": {
                            "type": "string",
                            "description": "The Viterbit candidate ID"
                        },
                        "discord_id": {
                            "type": "string",
                            "description": "Discord username or ID to set for the candidate"
                        }
                    },
                    "required": ["candidate_id", "discord_id"]
                }
            ),
            Tool(
                name="update_candidate_subscription",
                description="Update a candidate's subscription status (subscriber or non-subscriber).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "candidate_id": {
                            "type": "string",
                            "description": "The Viterbit candidate ID"
                        },
                        "is_subscriber": {
                            "type": "boolean",
                            "description": "Whether the candidate should be marked as a subscriber",
                            "default": True
                        }
                    },
                    "required": ["candidate_id"]
                }
            ),
            Tool(
                name="update_candidate_stage",
                description="Update a candidate's stage name and date. Sets the stage and current date in their custom fields.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email address of the candidate"
                        },
                        "stage_name": {
                            "type": "string",
                            "description": "Stage name to set (e.g., 'Match', 'Contratado', 'Preseleccionado')"
                        }
                    },
                    "required": ["email", "stage_name"]
                }
            ),

            # Job Management Tools
            Tool(
                name="get_job_details",
                description="Get comprehensive job information including custom fields, requirements, location, and salary details.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                            "description": "The Viterbit job ID"
                        }
                    },
                    "required": ["job_id"]
                }
            ),

            # Candidature Management Tools
            Tool(
                name="find_active_candidatures",
                description="Find all active job applications (candidatures) for a candidate by their email address.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email address of the candidate"
                        }
                    },
                    "required": ["email"]
                }
            ),
            Tool(
                name="disqualify_candidature",
                description="Disqualify a specific job application (candidature) with a reason.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "candidature_id": {
                            "type": "string",
                            "description": "The candidature ID to disqualify"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for disqualification",
                            "default": "Baja Servicio"
                        }
                    },
                    "required": ["candidature_id"]
                }
            ),
            Tool(
                name="disqualify_all_candidatures",
                description="Disqualify ALL active job applications for a candidate by their email address. Use with caution as this affects all active applications.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email address of the candidate whose applications should be disqualified"
                        }
                    },
                    "required": ["email"]
                }
            ),

            # Utility Tools
            Tool(
                name="get_custom_fields_definitions",
                description="Get all available custom field definitions and their schemas from Viterbit. Useful for understanding field structure and IDs.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="check_candidate_eligibility",
                description="Check if a candidate should be included in reports based on their activity status and other filtering criteria.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "viterbit_data": {
                            "type": "object",
                            "description": "Candidate data object with Viterbit fields (typically from get_candidate_with_filters)"
                        }
                    },
                    "required": ["viterbit_data"]
                }
            ),
            Tool(
                name="get_department_location_mappings",
                description="Get the department and location ID mappings used by Viterbit. Returns both department names to IDs and location names to IDs.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="extract_discord_username",
                description="Extract Discord username from a candidate's custom fields data.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "custom_fields": {
                            "type": "array",
                            "description": "Array of custom field objects from candidate details"
                        }
                    },
                    "required": ["custom_fields"]
                }
            ),
            Tool(
                name="search_subscribers",
                description="Search for candidates who are subscribers. Optionally filter by activity status, location, or other criteria. Returns candidates data plus metadata with total counts.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "is_subscriber": {
                            "type": "boolean",
                            "description": "Filter by subscription status (true for subscribers, false for non-subscribers)",
                            "default": True
                        },
                        "activity_status": {
                            "type": "string",
                            "description": "Filter by activity status (Activo/Inactivo)",
                            "enum": ["Activo", "Inactivo"]
                        },
                        "page": {
                            "type": "number",
                            "description": "Page number for pagination",
                            "default": 1
                        },
                        "page_size": {
                            "type": "number",
                            "description": "Number of results per page",
                            "default": 50
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="get_candidate_count",
                description="Get the total count of candidates matching specific criteria without returning all the data. Perfect for answering 'how many candidates are...' questions.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "is_subscriber": {
                            "type": "boolean",
                            "description": "Filter by subscription status (true for subscribers, false for non-subscribers)"
                        },
                        "activity_status": {
                            "type": "string",
                            "description": "Filter by activity status (Activo/Inactivo)",
                            "enum": ["Activo", "Inactivo"]
                        },
                        "coach": {
                            "type": "string",
                            "description": "Filter by coach (Alexia, Irene, Irina)",
                            "enum": ["Alexia", "Irene", "Irina"]
                        },
                        "has_driving_license": {
                            "type": "string",
                            "description": "Filter by driving license (Sí, No, Me lo estoy sacando)",
                            "enum": ["Sí", "No", "Me lo estoy sacando"]
                        },
                        "national_mobility": {
                            "type": "string",
                            "description": "Filter by national mobility (Sí, No, Puedo desplazarme pero no dormir fuera de casa)",
                            "enum": ["Sí", "No", "Puedo desplazarme pero no dormir fuera de casa"]
                        },
                        "has_experience": {
                            "type": "string",
                            "description": "Filter by related experience (Sí, No)",
                            "enum": ["Sí", "No"]
                        },
                        "zona": {
                            "type": "string",
                            "description": "Filter by zone/area (custom field Zona)"
                        },
                        "provincia": {
                            "type": "string",
                            "description": "Filter by province (custom field Provincia)"
                        },
                        "city": {
                            "type": "string",
                            "description": "Filter by city from address"
                        },
                        "state": {
                            "type": "string",
                            "description": "Filter by state/region from address"
                        },
                        "postal_code": {
                            "type": "string",
                            "description": "Filter by postal code from address"
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="search_candidates_by_location",
                description="Search candidates by geographic location using zones, provinces, cities, or address information.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "zona": {
                            "type": "string",
                            "description": "Search by zone/area (custom field)"
                        },
                        "provincia": {
                            "type": "string",
                            "description": "Search by province (custom field)"
                        },
                        "city": {
                            "type": "string",
                            "description": "Search by city from address"
                        },
                        "state": {
                            "type": "string",
                            "description": "Search by state/region from address"
                        },
                        "postal_code": {
                            "type": "string",
                            "description": "Search by postal code from address"
                        },
                        "is_subscriber": {
                            "type": "boolean",
                            "description": "Also filter by subscription status"
                        },
                        "activity_status": {
                            "type": "string",
                            "description": "Also filter by activity status (Activo/Inactivo)",
                            "enum": ["Activo", "Inactivo"]
                        },
                        "page": {
                            "type": "number",
                            "description": "Page number for pagination",
                            "default": 1
                        },
                        "page_size": {
                            "type": "number",
                            "description": "Number of results per page",
                            "default": 50
                        }
                    },
                    "required": []
                }
            ),

            # Candidature Stage History Tools
            Tool(
                name="get_candidature_stage_history",
                description="Get candidature details including complete stages history. Shows all stage transitions with timestamps.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "candidature_id": {
                            "type": "string",
                            "description": "The candidature ID to get stage history for"
                        }
                    },
                    "required": ["candidature_id"]
                }
            ),
            Tool(
                name="get_candidatures_changed_to_stage",
                description="Find all candidatures that changed to a specific stage (like 'Match') during a given month. Perfect for monthly reporting on stage transitions.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "stage_name": {
                            "type": "string",
                            "description": "Name of the stage to filter by (e.g., 'Match', 'Preseleccionado', 'Contratado')"
                        },
                        "year": {
                            "type": "integer",
                            "description": "Year to filter by (e.g., 2025)",
                            "minimum": 2020,
                            "maximum": 2030
                        },
                        "month": {
                            "type": "integer",
                            "description": "Month to filter by (1-12)",
                            "minimum": 1,
                            "maximum": 12
                        }
                    },
                    "required": ["stage_name", "year", "month"]
                }
            ),
            Tool(
                name="count_candidatures_changed_to_stage",
                description="Count how many candidatures changed to a specific stage during a given month. Returns just the count number for quick reporting.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "stage_name": {
                            "type": "string",
                            "description": "Name of the stage to filter by (e.g., 'Match', 'Preseleccionado', 'Contratado')"
                        },
                        "year": {
                            "type": "integer",
                            "description": "Year to filter by (e.g., 2025)",
                            "minimum": 2020,
                            "maximum": 2030
                        },
                        "month": {
                            "type": "integer",
                            "description": "Month to filter by (1-12)",
                            "minimum": 1,
                            "maximum": 12
                        }
                    },
                    "required": ["stage_name", "year", "month"]
                }
            ),
            Tool(
                name="get_candidatures_in_current_stage",
                description="Get all candidatures currently in a specific stage right now. Returns detailed candidature information for candidates in the specified stage at this moment.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "stage_name": {
                            "type": "string",
                            "description": "Name of the stage to filter by (e.g., 'Match', 'Preseleccionado', 'Contratado')"
                        },
                        "page": {
                            "type": "number",
                            "description": "Page number for pagination",
                            "default": 1
                        },
                        "page_size": {
                            "type": "number",
                            "description": "Number of results per page (max 100)",
                            "default": 50
                        }
                    },
                    "required": ["stage_name"]
                }
            ),
            Tool(
                name="count_candidatures_in_current_stage",
                description="Count how many candidatures are currently in a specific stage right now. Returns just the count number for quick reporting about current stage status.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "stage_name": {
                            "type": "string",
                            "description": "Name of the stage to filter by (e.g., 'Match', 'Preseleccionado', 'Contratado')"
                        }
                    },
                    "required": ["stage_name"]
                }
            )
        ]

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle MCP tool calls.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            List of text content responses
        """
        try:
            if name == "search_candidate":
                result = await self.client.search_candidate(str(arguments["search_term"]))
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "get_candidate_details":
                result = await self.client.get_candidate_details(str(arguments["candidate_id"]))
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "get_candidate_with_filters":
                result = await self.client.get_candidate_with_viterbit_fields(str(arguments["email"]))
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "update_candidate_discord_id":
                await self.client.update_candidate_discord_id(
                    str(arguments["candidate_id"]),
                    str(arguments["discord_id"])
                )
                return [TextContent(type="text", text="Discord ID updated successfully")]

            elif name == "update_candidate_subscription":
                is_subscriber = arguments.get("is_subscriber", True)
                await self.client.update_candidate_subscription_status(
                    str(arguments["candidate_id"]),
                    bool(is_subscriber)
                )
                status = "subscriber" if is_subscriber else "non-subscriber"
                return [TextContent(type="text", text=f"Candidate subscription status updated to: {status}")]

            elif name == "update_candidate_stage":
                await self.client.update_candidate_stage_fields(
                    str(arguments["email"]),
                    str(arguments["stage_name"])
                )
                return [TextContent(type="text", text=f"Candidate stage updated to: {arguments['stage_name']}")]

            elif name == "get_job_details":
                result = await self.client.get_job_details(str(arguments["job_id"]))
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "find_active_candidatures":
                result = await self.client.find_active_candidatures_by_email(str(arguments["email"]))
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "disqualify_candidature":
                reason = str(arguments.get("reason", "Baja Servicio"))
                success = await self.client.disqualify_candidature(
                    str(arguments["candidature_id"]),
                    reason
                )
                status = "successfully disqualified" if success else "failed to disqualify"
                return [TextContent(type="text", text=f"Candidature {status} with reason: {reason}")]

            elif name == "disqualify_all_candidatures":
                result = await self.client.disqualify_active_candidatures_by_email(str(arguments["email"]))
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "get_custom_fields_definitions":
                result = await self.client.get_custom_fields_definitions()
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "check_candidate_eligibility":
                viterbit_data = arguments["viterbit_data"]
                if isinstance(viterbit_data, str):
                    viterbit_data = json.loads(viterbit_data)
                result = self.client.should_include_candidate_in_report(viterbit_data)
                return [TextContent(type="text", text=json.dumps({
                    "eligible": result,
                    "reason": "Candidate is inactive" if not result else "Candidate is eligible"
                }, indent=2))]

            elif name == "get_department_location_mappings":
                result = {
                    "departments": self.client.get_department_mappings(),
                    "locations": self.client.get_location_mappings()
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "extract_discord_username":
                custom_fields = arguments["custom_fields"]
                if isinstance(custom_fields, str):
                    custom_fields = json.loads(custom_fields)
                result = self.client.extract_discord_user(custom_fields)
                return [TextContent(type="text", text=json.dumps({
                    "discord_username": result
                }, indent=2))]

            elif name == "search_subscribers":
                is_subscriber = arguments.get("is_subscriber", True)
                activity_status = arguments.get("activity_status")
                page = arguments.get("page", 1)
                page_size = arguments.get("page_size", 50)

                # Build filters for the search
                filters = {}

                # Add subscription filter using the custom field ID
                if is_subscriber is not None:
                    filters["67fe75c8f8e7996e110cb5a0"] = is_subscriber

                # Add activity status filter if provided
                if activity_status:
                    filters["68a455d5585b0d17c20bdcb1"] = activity_status

                result = await self.client.search_candidates_with_filters(
                    filters=filters,
                    page=page,
                    page_size=page_size
                )

                if result is None:
                    return [TextContent(type="text", text="Error: Failed to search subscribers")]

                # Format the response to highlight the metadata
                meta = result.get("meta", {})
                data = result.get("data", [])

                formatted_response = {
                    "summary": {
                        "total_found": meta.get("total", 0),
                        "showing": len(data),
                        "page": meta.get("page", 1),
                        "total_pages": meta.get("total_pages", 0),
                        "has_more": meta.get("has_more", False)
                    },
                    "filters_applied": {k: v for k, v in arguments.items() if v is not None},
                    "candidates": data,
                    "meta": meta
                }

                return [TextContent(type="text", text=json.dumps(formatted_response, indent=2))]

            elif name == "get_candidate_count":
                # Build filters based on provided criteria
                filters = {}

                # Subscription status
                is_subscriber = arguments.get("is_subscriber")
                if is_subscriber is not None:
                    filters["67fe75c8f8e7996e110cb5a0"] = is_subscriber

                # Activity status
                activity_status = arguments.get("activity_status")
                if activity_status:
                    filters["68a455d5585b0d17c20bdcb1"] = activity_status

                # Coach
                coach = arguments.get("coach")
                if coach:
                    filters["68c14707fdded0284e03159c"] = coach

                # Driving license
                has_driving_license = arguments.get("has_driving_license")
                if has_driving_license:
                    filters["6748889b1207a9f3040c4a8a"] = has_driving_license

                # National mobility
                national_mobility = arguments.get("national_mobility")
                if national_mobility:
                    filters["67c8200c62e3ae6c1006691b"] = national_mobility

                # Experience
                has_experience = arguments.get("has_experience")
                if has_experience:
                    filters["67c8412097b7cbb331024e09"] = has_experience

                # Location filters
                zona = arguments.get("zona")
                if zona:
                    filters["67c83def159fcdd58906e4c5"] = zona  # Zona field ID

                provincia = arguments.get("provincia")
                if provincia:
                    filters["67c84b1c21bda2b3c60fabea"] = provincia  # Provincia field ID

                # Address fields
                city = arguments.get("city")
                if city:
                    filters["address__city"] = city

                state = arguments.get("state")
                if state:
                    filters["address__state"] = state

                postal_code = arguments.get("postal_code")
                if postal_code:
                    filters["address__postal_code"] = postal_code

                # Search with page_size=1 to get just the count efficiently
                result = await self.client.search_candidates_with_filters(
                    filters=filters,
                    page=1,
                    page_size=1
                )

                if result is None:
                    return [TextContent(type="text", text="Error: Failed to get candidate count")]

                # Extract and format the count information
                meta = result.get("meta", {})
                count_summary = {
                    "total_candidates": meta.get("total", 0),
                    "filters_applied": {k: v for k, v in arguments.items() if v is not None},
                    "meta": meta
                }

                return [TextContent(type="text", text=json.dumps(count_summary, indent=2))]

            elif name == "search_candidates_by_location":
                # Build filters for location-based search
                filters = {}

                # Custom field location filters
                zona = arguments.get("zona")
                if zona:
                    filters["67c83def159fcdd58906e4c5"] = zona  # Zona field ID

                provincia = arguments.get("provincia")
                if provincia:
                    filters["67c84b1c21bda2b3c60fabea"] = provincia  # Provincia field ID

                # Address field filters
                city = arguments.get("city")
                if city:
                    filters["address__city"] = city

                state = arguments.get("state")
                if state:
                    filters["address__state"] = state

                postal_code = arguments.get("postal_code")
                if postal_code:
                    filters["address__postal_code"] = postal_code

                # Optional additional filters
                is_subscriber = arguments.get("is_subscriber")
                if is_subscriber is not None:
                    filters["67fe75c8f8e7996e110cb5a0"] = is_subscriber

                activity_status = arguments.get("activity_status")
                if activity_status:
                    filters["68a455d5585b0d17c20bdcb1"] = activity_status

                # Pagination
                page = arguments.get("page", 1)
                page_size = arguments.get("page_size", 50)

                result = await self.client.search_candidates_with_filters(
                    filters=filters,
                    page=page,
                    page_size=page_size
                )

                if result is None:
                    return [TextContent(type="text", text="Error: Failed to search candidates by location")]

                # Format the response to highlight the metadata
                meta = result.get("meta", {})
                data = result.get("data", [])

                formatted_response = {
                    "summary": {
                        "total_found": meta.get("total", 0),
                        "showing": len(data),
                        "page": meta.get("page", 1),
                        "total_pages": meta.get("total_pages", 0),
                        "has_more": meta.get("has_more", False)
                    },
                    "location_filters": {k: v for k, v in arguments.items() if v is not None and k in ["zona", "provincia", "city", "state", "postal_code"]},
                    "additional_filters": {k: v for k, v in arguments.items() if v is not None and k in ["is_subscriber", "activity_status"]},
                    "candidates": data,
                    "meta": meta
                }

                return [TextContent(type="text", text=json.dumps(formatted_response, indent=2))]

            elif name == "get_candidature_stage_history":
                result = await self.client.get_candidature_with_stage_history(str(arguments["candidature_id"]))
                if result is None:
                    return [TextContent(type="text", text="Error: Candidature not found or no access")]
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "get_candidatures_changed_to_stage":
                stage_name = str(arguments["stage_name"])
                year = int(arguments["year"])
                month = int(arguments["month"])

                result = await self.client.get_candidatures_changed_to_stage(stage_name, year, month)

                formatted_response = {
                    "summary": {
                        "total_found": len(result),
                        "stage_name": stage_name,
                        "period": f"{year}-{month:02d}",
                        "search_criteria": {
                            "stage_name": stage_name,
                            "year": year,
                            "month": month
                        }
                    },
                    "candidatures": result
                }

                return [TextContent(type="text", text=json.dumps(formatted_response, indent=2))]

            elif name == "count_candidatures_changed_to_stage":
                stage_name = str(arguments["stage_name"])
                year = int(arguments["year"])
                month = int(arguments["month"])

                count = await self.client.count_candidatures_changed_to_stage(stage_name, year, month)

                formatted_response = {
                    "count": count,
                    "stage_name": stage_name,
                    "period": f"{year}-{month:02d}",
                    "query": f"Candidatures changed to '{stage_name}' in {year}-{month:02d}"
                }

                return [TextContent(type="text", text=json.dumps(formatted_response, indent=2))]

            elif name == "get_candidatures_in_current_stage":
                stage_name = str(arguments["stage_name"])
                page = arguments.get("page", 1)
                page_size = arguments.get("page_size", 50)

                result = await self.client.get_candidatures_in_current_stage(stage_name, page, page_size)

                if result is None:
                    return [TextContent(type="text", text="Error: Failed to get candidatures in current stage")]

                meta = result.get("meta", {})
                data = result.get("data", [])

                formatted_response = {
                    "summary": {
                        "total_in_stage": meta.get("total", 0),
                        "showing": len(data),
                        "page": meta.get("page", 1),
                        "total_pages": meta.get("total_pages", 0),
                        "has_more": meta.get("has_more", False)
                    },
                    "stage_name": stage_name,
                    "query": f"Candidatures currently in '{stage_name}' stage",
                    "candidatures": data,
                    "meta": meta
                }

                return [TextContent(type="text", text=json.dumps(formatted_response, indent=2))]

            elif name == "count_candidatures_in_current_stage":
                stage_name = str(arguments["stage_name"])

                count = await self.client.count_candidatures_in_current_stage(stage_name)

                formatted_response = {
                    "count": count,
                    "stage_name": stage_name,
                    "query": f"Candidatures currently in '{stage_name}' stage"
                }

                return [TextContent(type="text", text=json.dumps(formatted_response, indent=2))]

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

        except Exception as e:
            error_msg = f"Error executing {name}: {str(e)}"
            logging.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]