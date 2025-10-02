# Adding New Tools to Your MCP Server

This guide shows you how to add new tools without modifying existing code.

## Why This Matters

As your needs grow, you'll want to add new tools. This extensible architecture means:
- ✅ No need to modify ChatGPT instructions when adding tools
- ✅ ChatGPT discovers new tools automatically via `listTools`
- ✅ Tools are self-documenting through their schemas
- ✅ Easy to maintain and extend

## Quick Start: Adding a New Tool

### Option 1: Add to `tools.py` (Current Approach)

Add your tool definition to the `get_tools()` list in `tools.py`:

```python
Tool(
    name="your_new_tool",
    description="Clear description of what it does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "What this parameter does"
            },
            "param2": {
                "type": "number",
                "description": "Another parameter",
                "default": 10
            }
        },
        "required": ["param1"]  # List required params
    }
)
```

Then add the handler in `handle_tool_call()`:

```python
elif name == "your_new_tool":
    result = await self.client.your_new_method(
        str(arguments["param1"]),
        int(arguments.get("param2", 10))
    )
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
```

### Option 2: Use Tool Registry (Future-Proof Approach)

See `tool_registry.py` and `tools_extended.py` for examples.

## Complete Example: Adding a Batch Tool

Let's say you want to add a tool that searches multiple candidates at once.

### Step 1: Add to ViterbitClient (if needed)

In `viterbit_client.py`:

```python
async def batch_search_candidates(self, emails: List[str]) -> List[Dict]:
    """Search multiple candidates by email."""
    results = []
    for email in emails:
        try:
            candidate = await self.search_candidate_by_email(email)
            results.append(candidate)
        except Exception as e:
            results.append({"email": email, "error": str(e)})
    return results
```

### Step 2: Add Tool Definition

In `tools.py`, add to the `get_tools()` list:

```python
Tool(
    name="batch_search_candidates",
    description="Search for multiple candidates by email addresses at once. Returns results for all provided emails.",
    inputSchema={
        "type": "object",
        "properties": {
            "emails": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of email addresses to search for"
            }
        },
        "required": ["emails"]
    }
)
```

### Step 3: Add Handler

In `tools.py`, in `handle_tool_call()`:

```python
elif name == "batch_search_candidates":
    emails = arguments.get("emails", [])
    results = await self.client.batch_search_candidates(emails)
    return [TextContent(type="text", text=json.dumps(results, indent=2))]
```

### Step 4: Deploy

```bash
git add viterbit_client.py tools.py
git commit -m "Add batch candidate search tool"
git push
```

Render auto-deploys. That's it! No ChatGPT changes needed.

### Step 5: Test in ChatGPT

```
What tools do you have available?
```

ChatGPT calls `listTools` and sees your new `batch_search_candidates` tool.

```
Search for candidates: test1@example.com, test2@example.com, test3@example.com
```

ChatGPT automatically uses your new tool!

## Tool Schema Types

### String Parameter
```python
"param_name": {
    "type": "string",
    "description": "What it does"
}
```

### Number Parameter
```python
"count": {
    "type": "number",
    "description": "How many items",
    "default": 10
}
```

### Boolean Parameter
```python
"is_active": {
    "type": "boolean",
    "description": "Filter by active status",
    "default": true
}
```

### Enum (Fixed Options)
```python
"status": {
    "type": "string",
    "description": "Candidate status",
    "enum": ["Activo", "Inactivo", "Pendiente"]
}
```

### Array Parameter
```python
"emails": {
    "type": "array",
    "items": {"type": "string"},
    "description": "List of email addresses"
}
```

### Object Parameter
```python
"filters": {
    "type": "object",
    "description": "Filter criteria",
    "properties": {
        "location": {"type": "string"},
        "experience": {"type": "number"}
    }
}
```

## Best Practices

### 1. Clear Descriptions
```python
# ❌ Bad
description="Updates candidate"

# ✅ Good
description="Update a candidate's subscription status (subscriber or non-subscriber). Changes the suscriptor field in their custom fields."
```

### 2. Include Examples in Descriptions
```python
description="Update candidate stage. Common stages: 'Match', 'Contratado', 'Preseleccionado', 'En proceso', 'Descartado'"
```

### 3. Use Defaults for Optional Parameters
```python
"page_size": {
    "type": "number",
    "description": "Number of results per page",
    "default": 50
}
```

### 4. Validate Input in Handler
```python
elif name == "your_tool":
    email = arguments.get("email")
    if not email:
        return [TextContent(type="text", text=json.dumps({
            "error": "Email parameter is required"
        }))]

    # Continue with logic...
```

### 5. Return Consistent Format
```python
# Always return similar structure
return [TextContent(type="text", text=json.dumps({
    "success": True,
    "data": result,
    "count": len(result)
}, indent=2))]
```

## ChatGPT Behavior

With extensible instructions, ChatGPT will:

1. **Call `listTools`** when it needs to know what's available
2. **Read tool schemas** to understand parameters
3. **Construct correct calls** based on the schema
4. **Adapt automatically** when you add new tools

You never need to update ChatGPT instructions when adding tools!

## Testing New Tools

### 1. Test Locally First

```bash
# Start server locally
.venv/bin/python server_http.py

# Test with curl
curl -H "X-API-Key: test" \
  -H "Content-Type: application/json" \
  -d '{"name":"your_new_tool","param1":"value"}' \
  http://localhost:8000/tools/call
```

### 2. Check Render Logs

After deploying, check Render logs to see:
- Tool execution logs
- Any errors
- Request/response flow

### 3. Test in ChatGPT

```
Call listTools and show me what you find
```

Then use the tool naturally:
```
Use [your tool description] with [parameters]
```

## Common Patterns

### Read-Only Tool (Search/Get)
- No confirmation needed
- Return data directly
- Use clear, descriptive names

### Write Tool (Update/Delete)
- Mark as requiring confirmation in description
- Return success/failure clearly
- Include what changed in response

### Batch Tool (Multiple Operations)
- Accept arrays as input
- Return results for each item
- Handle partial failures gracefully

### Statistical Tool (Count/Aggregate)
- Return numbers with context
- Include filter summary in response
- Make filtering explicit in schema

## Troubleshooting

**Tool not appearing in listTools?**
- Check syntax in `get_tools()` list
- Ensure proper Tool() instantiation
- Verify no Python syntax errors

**ChatGPT not calling tool correctly?**
- Check tool description is clear
- Verify inputSchema matches actual parameters
- Look at Render logs to see what ChatGPT sent

**Tool executing but returning error?**
- Check handler logic in `handle_tool_call()`
- Verify client method exists
- Check parameter types match schema

## Next Steps

1. Identify new tools you need
2. Add them to `tools.py` following patterns above
3. Commit and push
4. Test with ChatGPT's `listTools`
5. Use naturally - no instruction updates needed!

The system is designed to scale with your needs. Add as many tools as you want! 🚀
