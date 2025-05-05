
<p align="center">
  <img title="Runbook.AI" alt="Runbook.AI" width="20%" src="./assets/images/runbook.ai.png">
</p>

# Runbook MCP Server

Runbook MCP Server enables you to run your own runbooks from Claude Desktop.

- Run ops runbooks (e.g., deploy a service, upgrade a Kubernetes cluster)
- Run manual test plans (e.g., create a new EC2 instance, ssh into the instance, and run the integration test there).

Please watch the demo video below to understand how it works!

![demo](./assets/images/demo.gif)

# How to Use

## Step 1. Start the MCP server with Claude Desktop.

Create `config.yaml`

Put the following configuration to `claude_desktop_config.json`.

```json
{
  "mcpServers": {
    "runbook": {
      "command": "uv",
      "args": [
        "--directory",
        "<ABSOLUTE_PATH>/runbook-mcp-server",
        "run",
        "runbook_server.py"
      ]
    }
  }
}
```

## Step 2. Create runbooks

You can use markdown files or text files as runbooks.  See [examples](./examples-runbooks/).

We support env/var substitution.

Define `env.yaml`.

```yaml
env:
  key: value
```

- `{env[key]}` is replaced with `value`.
- `{var.name}` is replaced with a variable value.

Rebuild the index when files are updated.

You can also create a new runbook, use the `create_runbook` tool. Here is an example prompt:

*Example 1*
```
Create a new runbook:

- name: list_pods
- content: List pods in all namespaces, find pods that are not ready, and send that to Slack.

You don't need to interpret the content. Please just pass it to the tool.
```

## Step 3. Run runbooks

To run a runbook, take the following steps:

1. Click "Attach from MCP" from Claude Desktop.
2. Select `get_runbook_as_prompt` from the list of integrations.
3. Pass the name of the runbook you would like to execute. Also specify variables with a comma-separated list (e.g., `var1=key1,var2=key2`).
4. Submit the generated prompt.

Then Claude Desktop will talk to other MCP servers to run the runbook.

# Example MCP Servers that can be used to Run Runbooks

- [GitHub](https://github.com/github/github-mcp-server)
- [Slack](https://github.com/modelcontextprotocol/servers/tree/main/src/slack)
- [DesktopCommanderMCP](https://github.com/wonderwhy-er/DesktopCommanderMCP)
- Web search and browser automation ([link](https://modelcontextprotocol.io/examples#web-and-browser-automation))
- Kubernetes. There are several implementations (e.g., [mcp-k8s-go](https://github.com/strowk/mcp-k8s-go))

# Development Plan

- Instead of saving the content of the runbook in the database, just save as a file. This helps easy editting. People can also
  simply use GitHub for versioning.
- Runbook template X that is instantiated with given inputs.
  -  Maybe this is not needed. A user just needs to put additional prompts when running the runbook.
- Save executing log (for auditting and refinement)
   - Remove secrets
   -  Also pass a past log to the runbook prompt if this helps better execution
- Approval flow.
  - Add a tool `request_approval`.
  - This sends a slack message to a channel.
  - Then the Runbook MCP server watches the channel. If someone responds (yes / no), it proceeeds or returns an error.
- Better runbook search
  - The exact name match is not great
- Registrtation to [Smithery](https://smithery.ai/server/@runbookai/runbook-mcp-server).

# Potential Work Items where its Feasibility is not clear

Note: Claude Desktop does not support "Sampling". This puts some limitations.

- Sub-runbook and reusable execution block
- Rest endpoint + frontend for managing runbooks.
- Be able to edit the runbook (with versioning)
- show an execution plan for runbook X (dry-run)
  - Restrict MCP servers and tools
- convert a previous conversation into a runbook
- fine-tuning.
- Be able to refine a runbook. If there is a successful execution, save it as an example
  and give it to Claude.
- Periodic execution
- Be able to provision an environment (VM, docker) for running MCP servers.


<a href="https://glama.ai/mcp/servers/p3mq5xzyof">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/p3mq5xzyof/badge" alt="Claude Desktop Commander MCP server" />
</a>

[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/runbookai-runbook-mcp-server-badge.png)](https://mseep.ai/app/runbookai-runbook-mcp-server)

