# Makefile for OpenAI MCP Circuit Breaker Server

.PHONY: run stop test

PYTHON=python3
SERVER=scripts/openai_circuit_breaker_mcp.py
PIDFILE=scripts/mcp_server.pid

run:
	@echo "Starting MCP server..."
	@nohup $(PYTHON) $(SERVER) > scripts/server.log 2>&1 & echo $$! > $(PIDFILE)
	@echo "MCP server started on port 5555. PID: $$(cat $(PIDFILE))"

stop:
	@if [ -f $(PIDFILE) ]; then \
		echo "Stopping MCP server..."; \
		kill $$(cat $(PIDFILE)) && rm -f $(PIDFILE); \
		echo "Stopped."; \
	else \
		echo "No PID file found, MCP server may not be running."; \
	fi

test:
	pytest test_openai_circuit_breaker_mcp.py


install-tools:
	apt update && apt install -y tmux vim ffmpeg


install-conda:
	mkdir -p ~/miniconda3
	wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
	bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
	rm ~/miniconda3/miniconda.sh
