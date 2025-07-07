# OpenAI MCP Circuit Breaker Server

This directory contains a lightweight circuit breaker daemon for monitoring OpenAI API usage on your account. It allows you to automatically stop further API usage (or notify you) if costs are incurred, acting as a safety layer to help prevent exceeding your usage or budget limits (e.g., the common 1M token allowance).

## Features

- **Runs as a simple MCP TCP server** (default: port 5555).
- **Command: `STATUS`**  
  Connect via TCP and send `STATUS\n` (case-insensitive) — receive `TRUE` (if cost incurred in the current or previous UTC day) or `FALSE`.  
- **Daily Cost Circuit Breaker**  
  Queries OpenAI's billing endpoint for usage cost today and yesterday, using your API key from [`pass`](https://www.passwordstore.org/).
- **Extensively unit-tested**  
  Only the core business logic (cost checking/circuit breaking) is tested for reliability using `pytest`.

## Quick Start

### Prerequisites

- Python 3.7+
- `curl` (for API requests)
- [`pass`](https://www.passwordstore.org/) with your OpenAI API key saved as `OPENAI_API_KEY`
- `pytest` (for running tests, optional)

### Setup

1. **Store your OpenAI API key securely:**
   ```sh
   pass insert OPENAI_API_KEY
   ```
   (Paste your key when prompted)

2. **Start the MCP server:**
   ```sh
   make -C hallo3/scripts run
   ```
   (Or directly: `python3 openai_circuit_breaker_mcp.py`)

3. **Check server status:**
   ```sh
   echo "STATUS" | nc localhost 5555
   ```
   - `TRUE` — Cost detected for today or yesterday
   - `FALSE` — No cost detected for today or yesterday

4. **Stop the server:**
   ```sh
   make -C hallo3/scripts stop
   ```

### Running the Tests

```sh
make -C hallo3/scripts test
```
or
```sh
pytest test_openai_circuit_breaker_mcp.py
```

All tests are focused on the business logic — ensuring that cost checks behave as expected for:
- Normal costs
- No costs
- Partial costs
- API/network errors

## Implementation Highlights

- **Makefile:** Includes targets to run, stop, and test the server.
- **Server script:** Receives commands via TCP and responds according to API usage over the last two days.
- **Business logic:** Defensive handling for API errors and cost accumulation.

## Troubleshooting

- Make sure `pass` is initialized and contains the `OPENAI_API_KEY` entry.
- Ensure `curl` and Python are in your `$PATH`.
- The server listens on all interfaces (`0.0.0.0:5555`) by default; change in the script if needed.
- The OpenAI usage API `/v1/dashboard/billing/usage` only supports whole-day queries (UTC).

## Extending

- Adjust MCP response logic or add new commands by editing `openai_circuit_breaker_mcp.py`.
- To make this a true "breaker" (disabling automation, alerting, etc.), integrate with your workflow or monitoring stack.
- For stricter token accounting, parse and log OpenAI API responses per request.

## License

This directory and its contents are provided as-is under your project's main license.

---