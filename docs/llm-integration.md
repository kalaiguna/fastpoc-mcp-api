# LLM Integration Guide

This guide shows how to connect a Large Language Model to the FastPOC service so that the LLM can reason over your product data and call your APIs as tools. Three tracks are covered — pick the one that fits your setup.

---

## Track 1 — MCP Inspector (Validate Your Server)

**Best for:** Quickly verifying that your MCP server exposes the right tools and that they behave correctly — before wiring up an LLM. No API key, no code, no configuration beyond `npx`.

### How it works

MCP Inspector is an official developer tool from the MCP project. It launches a local web UI where you can browse tools, read their schemas, call them with custom arguments, and inspect the raw JSON-RPC messages — all in the browser.

### Setup

```bash
cd python
npx -y @modelcontextprotocol/inspector python mcp_entry.py
```

Open the URL printed in the terminal (e.g. `http://127.0.0.1:6274`). Click **Connect**, then navigate to the **Tools** tab.

You will see all 5 FastPOC tools listed. Select any tool, fill in the arguments, and click **Call Tool** to see the live response from your server.

### What it confirms

- All tools are registered and discoverable
- Input schemas are correct
- Tool calls return the expected data
- The full MCP JSON-RPC handshake works end-to-end

This is the fastest way to validate a new MCP server before integrating it with a real LLM.

---

### Want to use MCP with a browser AI (ChatGPT, Gemini, Deepseek)?

[MCP SuperAssistant](https://mcpsuperassistant.ai/) is a Chrome extension that can route tool calls from any browser-based AI chat to a local MCP server. It requires a proxy bridge between the extension and your server:

```bash
# In the python/ directory
npx -y supergateway --port 3006 --cors --stdio "python mcp_entry.py"
```

Then point the extension at `http://localhost:3006/sse`.

> **Note:** Browser extension MCP integrations are evolving rapidly and behaviour can vary by extension version and AI provider. Claude Desktop (Track 2) is the more stable option if you only need one AI.

---

## Track 2 — Claude Desktop (Native MCP)

**Best for:** The reference MCP experience. Claude Desktop has built-in MCP support — no extension needed, no code, no API key beyond your Claude account.

### Setup

1. Install [Claude Desktop](https://claude.ai/download).
2. Open the Claude Desktop configuration file:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
3. Add the FastPOC MCP server:
   ```json
   {
     "mcpServers": {
       "fastpoc": {
         "command": "python",
         "args": ["/absolute/path/to/fastpoc/python/mcp_entry.py"]
       }
     }
   }
   ```
4. Restart Claude Desktop.

### What you will see

A hammer icon appears in Claude's chat interface showing the available tools:

| Tool | What it does |
|---|---|
| `list_products` | Retrieve all products |
| `get_product` | Get a product by ID |
| `create_product` | Add a new product |
| `update_product` | Modify a product |
| `delete_product` | Remove a product |

### Sample interaction

```
You: What products do we have with a price under $20?

Claude: [calls list_products]
        I found 3 products under $20:
        - Widget A — $9.99, 45 in stock
        - Gadget B — $14.99, 12 in stock
        - Doohickey C — $19.50, 78 in stock

You: The stock on Gadget B is low. What would the pricing agent recommend?

Claude: [calls get_pricing_recommendation for product 2]
        For Gadget B with only 12 units in stock, the pricing agent
        recommends a premium range of $15.74 – $17.24. Low stock
        justifies a price increase — discount eligibility: No.
```

This is the cleanest way to see MCP working end-to-end. The AI autonomously decides which tools to call and in what order.

---

## Track 3 — Gemini API, Programmatic (Free Tier)

**Best for:** Understanding the engineering side — how you wire an LLM to your API as tools in code. This is what an AI engineer builds.

### How it works

Gemini's function calling feature lets you describe your API endpoints as tool schemas. When Gemini decides a tool is needed, it returns a structured `function_call` instead of text. Your code executes the call and feeds the result back. This loop continues until Gemini has enough information to answer.

```
User prompt
    ↓
Gemini (decides tool needed)
    ↓
function_call { name, args }
    ↓
Your code calls FastPOC REST API
    ↓
Result fed back to Gemini
    ↓
Gemini produces final answer
```

### Setup

1. Get a free API key at [Google AI Studio](https://aistudio.google.com/) — no credit card required.
2. Install the dependency:
   ```bash
   pip install google-generativeai httpx
   ```
3. Start the FastPOC server:
   ```bash
   cd python && python main.py
   ```
4. Run the example:
   ```bash
   GEMINI_API_KEY=your-key python examples/gemini_tool_client.py
   ```

See `examples/gemini_tool_client.py` for the full implementation with inline explanation of each step.

---

## Choosing a Track

| | Track 1 (MCP Inspector) | Track 2 (Claude Desktop) | Track 3 (Gemini API) |
|---|---|---|---|
| Cost | Zero | Zero (Claude account) | Zero (free tier) |
| Setup effort | Minimal (`npx` one-liner) | Low | Medium |
| Code required | No | No | Yes |
| Involves an LLM | No — manual testing UI | Yes | Yes |
| What you learn | Tool schemas, MCP protocol | MCP from a user's perspective | How to wire LLM tool use in code |
| Stability | High | High | High |

**Recommended path:** Start with Track 1 to confirm your server works, then Track 2 to see an LLM reason over your tools, then Track 3 to understand how to build the same thing in code.
