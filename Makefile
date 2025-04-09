.PHONY: run-inspector
run-inspector:
	@npx @modelcontextprotocol/inspector uv run runbook_server.py

.PHONY: test
test:
	echo "Running tests..."
