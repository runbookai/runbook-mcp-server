# runbook-mcp-server

Runbook MCP Server executes a given runbook with a terminal and a browser. The goal is to support the following use cases:

- Run ops runbooks (e.g., deploy a service, upgrade a Kubernetes cluster)
- Run manual test plans (e.g., create a new EC2 instance, ssh into the instance, and run the integration test there).


# Development Notes

- All the actions taken are stored in an audit log.
- We would like to support the dry-run mode if possible. https://github.com/modelcontextprotocol/specification/issues/97 might be related.
- We would like to recursively call MCP if possible. This depends on https://github.com/modelcontextprotocol/specification/discussions/94.

See also https://modelcontextprotocol.io/development/roadmap#agent-support 
