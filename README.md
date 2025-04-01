# Runbook MCP Server 

Runbook MCP Server executes a given runbook with a terminal and a browser. The goal is to support the following use cases:

- Run ops runbooks (e.g., deploy a service, upgrade a Kubernetes cluster)
- Run manual test plans (e.g., create a new EC2 instance, ssh into the instance, and run the integration test there).

# A Design Sketch 

Commands:
- run runbook X
- run runbook template X that is instantiated with given inputs
- show an execution plan for runbook X (dry-run)
- convert a conversation into a runbook

# Rest API Specification 

- `/v1/organizations`
- `/v1/organizations/<org-id>/projects`
- `/v1/organizations/<org-id>/projects/<project-id>/runbooks`
- `/v1/organizations/<org-id>/projects/<project-id>/runbooks/<runbook-id>/logs`

# MCP Server Specification

## Resources

Runbook:
- Path: `runbook://<host>/<runbook-id>`
- Type: text resources

Runbook execution log:
- Path: `runbook-execution-log:/<runbook-id>/logs/<log-id>`
- Type: text resources

## Prompts

For each runbook, a corresponding prompt is created. Here is an example request.

```
{
  method: "prompts/get",
  params: {
    name: "execute-runbook",
    arguments: {
      runbookName: "backend-service-deploy"
    }
  }
}
```

## Tools

- CRUD opsfor runbooks?

## Roots

TBD

# Alternative Design Considered

Instead of using Prompts, we initially considered making the Runbook MCP server act as a MCP 
client so that it can execute a runbook by interacting with other MCP servers.

Sampling is another approach that allows the MCP server to talk to LLM, but it is not currently supported in the Claude Desktop client.

We might revisit the design, but for now, we will see if Prompts are sufficient to handle our use cases.

# Development Notes

- All the actions taken are stored in an audit log.
- We would like to support the dry-run mode if possible. https://github.com/modelcontextprotocol/specification/issues/97 might be related.
- We would like to recursively call MCP if possible. https://github.com/modelcontextprotocol/specification/discussions/94 is somewhat relevant.

See also https://modelcontextprotocol.io/development/roadmap#agent-support 
