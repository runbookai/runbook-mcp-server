.PHONY: run-inspector
run-inspector:
	@npx @modelcontextprotocol/inspector uv run runbook.py

.PHONY: test
test:
	echo "Running tests..."
