# Runbook MCP Server 

Runbook MCP Server executes a given runbook with a terminal and a browser. The goal is to support the following use cases:

- Run ops runbooks (e.g., deploy a service, upgrade a Kubernetes cluster)
- Run manual test plans (e.g., create a new EC2 instance, ssh into the instance, and run the integration test there).

# A Design Sketch 

Commands:
- run runbook X
- show an execution plan for runbook X (dry-run)

To run the runbook, the MCP server itself an MCP client. It reads the content of the runbook and execute as a prompt. 

# Development Notes

- All the actions taken are stored in an audit log.
- We would like to support the dry-run mode if possible. https://github.com/modelcontextprotocol/specification/issues/97 might be related.
- We would like to recursively call MCP if possible. https://github.com/modelcontextprotocol/specification/discussions/94 is somewhat relevant.

See also https://modelcontextprotocol.io/development/roadmap#agent-support 
