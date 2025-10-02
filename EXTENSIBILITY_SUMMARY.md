# Extensibility Architecture Summary

## The Problem We Solved

**Before:** Adding new tools required:
1. Updating `tools.py` ✅
2. Updating ChatGPT instructions ❌ (tedious, error-prone)
3. Testing ChatGPT behavior with new hardcoded names ❌
4. Maintaining documentation manually ❌

**After:** Adding new tools requires:
1. Updating `tools.py` ✅
2. Push to Render ✅
3. Done! ChatGPT discovers tools automatically ✅

## How It Works

### 1. Dynamic Tool Discovery

ChatGPT calls `listTools` to see what's available:

```json
{
  "name": "listTools"
}
```

Response:
```json
{
  "success": true,
  "result": {
    "tools": [
      {
        "name": "search_candidate",
        "description": "Search for a candidate by email address...",
        "inputSchema": {
          "type": "object",
          "properties": {
            "email": {"type": "string", "description": "Email address..."}
          },
          "required": ["email"]
        }
      },
      ...all other tools...
    ],
    "count": 16
  }
}
```

### 2. Self-Documenting Tools

Each tool includes:
- **Name**: What to call it
- **Description**: What it does
- **InputSchema**: What parameters it needs

ChatGPT reads these and knows how to use each tool.

### 3. Extensible Instructions

ChatGPT instructions say:
```
At the start of conversations, call {"name": "listTools"}
to discover available tools.

Use the tool descriptions and schemas to call tools correctly.
```

**No hardcoded tool names!** ChatGPT adapts to whatever tools exist.

## Architecture Diagram

```
┌─────────────────┐
│   ChatGPT GPT   │
│                 │
│  Instructions:  │
│  "Call          │
│   listTools"    │
└────────┬────────┘
         │
         │ 1. {"name": "listTools"}
         │
         ▼
┌─────────────────────────────────┐
│   HTTP/SSE Server               │
│                                 │
│   • Converts camelCase →        │
│     snake_case                  │
│   • Handles flat/nested params  │
│   • Special case: listTools     │
│     returns all tool definitions│
└────────┬────────────────────────┘
         │
         │ 2. Get tools from registry
         │
         ▼
┌─────────────────────────────────┐
│   ViterbitTools                 │
│                                 │
│   • get_tools() returns list    │
│   • Each Tool has:              │
│     - name                      │
│     - description               │
│     - inputSchema               │
│   • handle_tool_call() executes │
└─────────────────────────────────┘
         │
         │ 3. Returns tool list
         │
         ▼
┌─────────────────┐
│   ChatGPT GPT   │
│                 │
│  Now knows:     │
│  • search_cand  │
│  • get_details  │
│  • update_xyz   │
│  • ...etc       │
└─────────────────┘
```

## Adding a New Tool (Checklist)

### Step 1: Define the Tool
In `tools.py`, add to `get_tools()`:
```python
Tool(
    name="my_new_tool",
    description="What it does",
    inputSchema={...}
)
```

### Step 2: Implement the Handler
In `tools.py`, add to `handle_tool_call()`:
```python
elif name == "my_new_tool":
    result = await self.client.my_method(arguments["param"])
    return [TextContent(type="text", text=json.dumps(result))]
```

### Step 3: Deploy
```bash
git add tools.py
git commit -m "Add my_new_tool"
git push
```

### Step 4: Done!
ChatGPT automatically sees it on next `listTools` call.

## Example: Adding "Bulk Update Status" Tool

### Code Changes

**tools.py - Add to `get_tools()`:**
```python
Tool(
    name="bulk_update_status",
    description="Update subscription status for multiple candidates at once",
    inputSchema={
        "type": "object",
        "properties": {
            "emails": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of candidate emails"
            },
            "is_subscriber": {
                "type": "boolean",
                "description": "New subscription status"
            }
        },
        "required": ["emails", "is_subscriber"]
    }
)
```

**tools.py - Add to `handle_tool_call()`:**
```python
elif name == "bulk_update_status":
    emails = arguments["emails"]
    is_subscriber = arguments["is_subscriber"]
    results = []

    for email in emails:
        try:
            candidate = await self.client.search_candidate_by_email(email)
            await self.client.update_candidate_subscription_status(
                candidate["id"],
                is_subscriber
            )
            results.append({"email": email, "success": True})
        except Exception as e:
            results.append({"email": email, "success": False, "error": str(e)})

    return [TextContent(type="text", text=json.dumps(results, indent=2))]
```

### Usage in ChatGPT

**User:** "What tools do you have?"

**ChatGPT:** Calls `listTools`, sees new `bulk_update_status` tool

**User:** "Update subscription status for these candidates: user1@test.com, user2@test.com, make them subscribers"

**ChatGPT:** Automatically constructs:
```json
{
  "name": "bulk_update_status",
  "emails": ["user1@test.com", "user2@test.com"],
  "is_subscriber": true
}
```

**No instruction changes needed!**

## Benefits

### For You (Developer)
- ✅ Add tools in one place (`tools.py`)
- ✅ Tools are self-documenting
- ✅ No need to maintain separate docs
- ✅ ChatGPT adapts automatically

### For ChatGPT
- ✅ Always knows current capabilities
- ✅ Understands how to use each tool
- ✅ Can explain available tools to users
- ✅ Adapts to changes without retraining

### For End Users
- ✅ Can ask "what can you do?" and get accurate answers
- ✅ New features appear automatically
- ✅ Consistent experience across tools

## Advanced: Tool Registry System

For even more extensibility, see:
- `tool_registry.py` - Registry pattern for tools
- `tools_extended.py` - Example custom tools
- `ADDING_NEW_TOOLS.md` - Complete guide

Use the registry to:
- Add tools via decorators
- Load tools from plugins
- Enable/disable tools dynamically
- Version tools independently

## Summary

**The key insight:** Don't hardcode tool names in ChatGPT instructions. Instead:

1. Make ChatGPT call `listTools` to discover tools
2. Each tool self-describes its purpose and parameters
3. ChatGPT reads schemas and uses tools correctly
4. Add new tools anytime without touching ChatGPT config

**Result:** Truly extensible system that scales with your needs! 🚀
