# Viterbit MCP Server

A Model Context Protocol (MCP) server that provides Claude and other MCP-compatible clients with access to Viterbit recruitment API functionality.

## Overview

This MCP server exposes comprehensive Viterbit API operations including candidate management, job operations, and candidature (application) handling. It allows Claude to interact with your Viterbit recruitment system autonomously.

## Features

### 🧑‍💼 Candidate Management
- **Search candidates** by email address
- **Get detailed candidate information** including custom fields and addresses
- **Update candidate data** (Discord ID, subscription status, stage information)
- **Filter candidates** with enriched data for reporting
- **🆕 Search subscribers** with advanced filtering by activity status, coach, mobility, etc.
- **🆕 Get candidate counts** efficiently for statistical queries without loading all data

### 💼 Job Management
- **Retrieve job details** with comprehensive information
- **Access job custom fields** and company information

### 📋 Candidature (Application) Management
- **Find active applications** for any candidate
- **Disqualify applications** individually or in bulk
- **Manage candidature lifecycle** with proper reasons and timestamps

### 🛠️ Utility Functions
- **Get custom field definitions** to understand Viterbit schema
- **Check candidate eligibility** for reports and filtering
- **Access department and location mappings**
- **Extract specific data** from custom fields

## Installation

1. **Clone or copy** the `mcp_viterbit` directory to your desired location
2. **Install dependencies**:
   ```bash
   cd mcp_viterbit
   pip install -r requirements.txt
   ```
3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Viterbit API key
   ```

## Configuration

### Required Environment Variables

- `VITERBIT_API_KEY`: Your Viterbit API key (required)

### Optional Environment Variables

If you're using a different Viterbit instance with different custom field IDs, you can override them:

- `DISCORD_ID_QUESTION_ID`
- `SUSCRIPTOR_QUESTION_ID`
- `CUSTOM_FIELD_STAGE_NAME_ID`
- `CUSTOM_FIELD_STAGE_DATE_ID`
- `CUSTOM_FIELD_SIN_DISCORD_ID`
- `CUSTOM_FIELD_NOMBRE_EMPRESA_ID`
- `GARANTIA_100_DIAS_ID`
- `ACTIVO_INACTIVO_ID`

## Usage

### Running the Server

To run the MCP server directly:

```bash
cd mcp_viterbit
python -m server
```

### Claude Desktop Integration

To integrate with Claude Desktop, add this configuration to your Claude Desktop settings:

```json
{
  "mcpServers": {
    "viterbit": {
      "command": "/path/to/mcp_viterbit/.venv/bin/python",
      "args": ["/path/to/mcp_viterbit/server.py"],
      "env": {
        "VITERBIT_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Important**: Use the full path to your virtual environment's Python interpreter and replace `/path/to/mcp_viterbit/` with the actual path to your server directory.

## Available Tools

### Candidate Management

#### `search_candidate`
Search for a candidate by email address.
- **Input**: `email` (string)
- **Output**: Basic candidate info (ID, name, email, phone)

#### `get_candidate_details`
Get comprehensive candidate information.
- **Input**: `candidate_id` (string)
- **Output**: Full candidate details including custom fields

#### `get_candidate_with_filters`
Get candidate with enriched filtering data.
- **Input**: `email` (string)
- **Output**: Candidate data optimized for reporting/filtering

#### `update_candidate_discord_id`
Update candidate's Discord username.
- **Input**: `candidate_id` (string), `discord_id` (string)
- **Output**: Success confirmation

#### `update_candidate_subscription`
Update subscription status.
- **Input**: `candidate_id` (string), `is_subscriber` (boolean, default: true)
- **Output**: Success confirmation

#### `update_candidate_stage`
Update candidate's stage and date.
- **Input**: `email` (string), `stage_name` (string)
- **Output**: Success confirmation

#### `search_subscribers` 🆕
Search for candidates who are subscribers with advanced filtering options.
- **Input**: `is_subscriber` (boolean, default: true), `activity_status` (string, optional), `page` (number), `page_size` (number)
- **Output**: Enhanced format with summary metadata, filters applied, and candidate data
- **Features**: Returns total count, pagination info, and filtered results

#### `get_candidate_count` 🆕
Get total count of candidates matching specific criteria efficiently.
- **Input**: Multiple optional filters including `is_subscriber`, `activity_status`, `coach`, `has_driving_license`, `national_mobility`, `has_experience`
- **Output**: Total count with applied filters summary
- **Performance**: Fast operation using minimal data transfer (page_size=1)

### Job Management

#### `get_job_details`
Get comprehensive job information.
- **Input**: `job_id` (string)
- **Output**: Full job details including custom fields

### Candidature Management

#### `find_active_candidatures`
Find all active applications for a candidate.
- **Input**: `email` (string)
- **Output**: List of active candidatures

#### `disqualify_candidature`
Disqualify a specific application.
- **Input**: `candidature_id` (string), `reason` (string, default: "Baja Servicio")
- **Output**: Success status

#### `disqualify_all_candidatures`
Disqualify ALL active applications for a candidate.
- **Input**: `email` (string)
- **Output**: Detailed results including counts and errors

### Utility Tools

#### `get_custom_fields_definitions`
Get all custom field schemas.
- **Input**: None
- **Output**: Custom field definitions

#### `check_candidate_eligibility`
Check if candidate should be included in reports.
- **Input**: `viterbit_data` (object)
- **Output**: Eligibility status and reason

#### `get_department_location_mappings`
Get department and location ID mappings.
- **Input**: None
- **Output**: Department and location mappings

#### `extract_discord_username`
Extract Discord username from custom fields.
- **Input**: `custom_fields` (array)
- **Output**: Discord username

## Example Usage with Claude

Once configured in Claude Desktop, you can use natural language to interact with Viterbit:

### Basic Operations
```
"Find me the candidate with email john.doe@example.com and show me their details"

"Update candidate ID 12345's Discord username to 'johndoe_discord'"

"Show me all active job applications for sara.smith@example.com"

"Disqualify all applications for candidate mike.jones@example.com because they unsubscribed"

"Get the details for job ID 67890 including custom fields"
```

### 🆕 Advanced Subscriber & Counting Queries
```
"How many active subscribers do we have?"
→ Uses get_candidate_count with subscriber and activity filters

"Show me 10 inactive subscribers"
→ Uses search_subscribers with activity_status: "Inactivo"

"How many candidates have a driving license?"
→ Uses get_candidate_count with has_driving_license: "Sí"

"Find subscribers assigned to coach Alexia"
→ Uses search_subscribers with coach filter

"What's the total number of candidates willing to travel nationally?"
→ Uses get_candidate_count with national_mobility: "Sí"

"Show me 5 subscribers and tell me the total count"
→ Uses search_subscribers which returns both data and total in summary
```

### Custom Field Queries
```
"Show me all available custom fields and their IDs"
→ Uses get_custom_fields_definitions

"How many candidates need personalized follow-up?"
→ Uses custom field filtering capabilities
```

## Error Handling

The server includes comprehensive error handling:

- **API Errors**: Viterbit API errors are caught and reported clearly
- **Validation**: Input parameters are validated before API calls
- **Logging**: Detailed logging for debugging and monitoring
- **Graceful Failures**: Tools return informative error messages instead of crashing

## Security

- **API Key Protection**: API keys are loaded from environment variables
- **No Data Storage**: The server doesn't store or cache any sensitive data
- **Minimal Permissions**: Only requires Viterbit API access

## Troubleshooting

### Common Issues

1. **"Viterbit API key is required"**
   - Ensure `VITERBIT_API_KEY` is set in your environment or .env file

2. **"Connection timeout"**
   - Check your internet connection and Viterbit API status

3. **"Candidate not found"**
   - Verify the email address exists in Viterbit
   - Check for typos in email addresses

4. **"Custom field errors"**
   - Ensure your Viterbit instance uses the default custom field IDs
   - Override with correct IDs in environment variables if needed

### Debugging

Enable debug logging by setting the logging level:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Development

The server is built with:

- **MCP SDK**: For Model Context Protocol implementation
- **httpx**: For async HTTP requests to Viterbit API
- **python-dotenv**: For environment variable management

### Project Structure

```
mcp_viterbit/
├── __init__.py           # Package initialization
├── server.py             # Main MCP server implementation
├── viterbit_client.py    # Viterbit API client with enhanced filtering
├── tools.py              # MCP tool definitions (16 tools total)
├── config.py             # Configuration and custom field ID mappings
├── requirements.txt      # Python dependencies
├── test_tools.py         # Test script for functionality verification
├── .env                  # Environment variables (with your API key)
└── README.md             # This documentation
```

### Key Features Added in Latest Version

- **🔢 Statistical Queries**: Fast candidate counting without data transfer overhead
- **🎯 Advanced Filtering**: Search by subscription, activity, coach, mobility, experience, driving license
- **📊 Enhanced Metadata**: All searches now return total counts, pagination info, and applied filters
- **⚡ Performance Optimized**: Counting operations use minimal bandwidth (page_size=1)
- **🗂️ Custom Field Integration**: Direct integration with all 27 Viterbit custom fields

## License

This project was generated by Claude Code for use with Viterbit recruitment systems.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the logs for detailed error messages
3. Ensure your Viterbit API key has the necessary permissions
4. Verify your Viterbit instance configuration matches the expected field IDs