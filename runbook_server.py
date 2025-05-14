import httpx
import json
import os
import mcp.types as types
import yaml
import logging

from datetime import datetime
from uuid import uuid4

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from mcp.server import Server
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.prompts import base
from typing import Any

from config import Config
from search import RunbookSearchEngine

log = logging.getLogger("runbook-server")

conf = Config('./config.yaml')
conf.validate()

if not os.path.exists(conf.runbook_logs_dir):
    os.makedirs(conf.runbook_logs_dir)

search_engine = RunbookSearchEngine(conf.runbooks_dir, conf.runbooks_index_dir)
search_engine.create_index()

mcp = FastMCP("Runbook")

# TODO(kenji): Use Context once https://github.com/modelcontextprotocol/python-sdk/issues/244 is fixed.

@mcp.resource("runbooks://runbooks")
def list_runbooks() -> str:
    rs = search_engine.runbook_names
    return json.dumps([{"name": r} for r in rs])


@mcp.resource("runbooks://runbooks/{name}")
def get_runbook(name: str) -> str:
    r = search_engine.get_runbook_by_name(name)
    if r:
        return json.dumps({"name": r})
    return json.dumps({})


@mcp.tool()
async def create_runbook(name: str, content: str) -> str:
    """Create a runbook file and save the content."""
    file_path = f"{name}.md"
    with open(os.path.join(conf.runbooks_dir, file_path), "w") as f:
        f.write(content)

    search_engine.create_index()
    return "Created a new runbook"


@mcp.tool()
async def delete_runbook(name: str) -> str:
    r = store.get_runbook_by_name(name)

    file_path = os.path.join(conf.runbooks_dir, r)
    if os.path.exists(file_path):
        os.remove(file_path)

    search_engine.create_index()
    return "Deleted the runbook"


@mcp.tool()
async def create_runbook_log(runbook_name: str, execution_log: str) -> str:
    time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    file_path = f"{runbook_name}_{time}.log"
    with open(os.path.join(conf.runbook_logs_dir, file_path), "w") as f:
        f.write(execution_log)
    return "Created the runbook log"


@mcp.tool()
async def reindex_runbooks() -> str:
    search_engine.create_index()
    return "Reindexed the runbook"


@mcp.prompt()
def get_runbook_as_prompt(runbook_search_keyword: str, vars: str) -> str:

    env_map = {}
    env_file = os.path.join(conf.runbooks_dir, "env.yaml")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            env_map = yaml.safe_load(f)

    var_map = {}
    for var_str in vars.split(","):
        # var is of the form key=value. Split it into key and value.
        l = var_str.split("=")
        if len(l) != 2:
            # Ignore.
            # TODO(kenji): better handling
            continue
        var_map[l[0]] = l[1]

    rs = search_engine.search_runbooks(runbook_search_keyword, limit=1)
    if not rs:
        raise ValueError(f"Runbook matching with {runbook_search_keyword} not found")
    r = rs[0]
    runbook_name = r["name"]
    log.info(f"Generating a prompt from runbook {runbook_name}")

    content = ""
    with open(r["path"], "r") as f:
        content = f.read()
    template = f"""Run the following prompt with MCP:

{content}

Once you complete the above runbook, call the tool 'create_runbook_log'. We pass the runbook name '{runbook_name}' and
and the conversation/execution log to the tool.
"""

    # First replace envs. This is a hack, but we don't use format_map()
    # as it allows only string literal for dictionary.
    #
    # For example, '{my_map[k]}'.format_map({'my_map': {'k': 'v'}}) works, but
    # '{my_map[k_var]}'.format_map({'my_map': {'k': 'v'}, 'k_var': 'k'}) returns
    # `KeyError: 'k_var'` as `k_var` in `{my_map[k_var]}` is treated as a string literal, not variable.
    #
    # TODO(kenji): Fix.
    for k, v in var_map.items():
        template = template.replace("{var.%s}" % k, v)

    m = {"env": env_map}
    return template.format_map(m)


if __name__ == "__main__":
    mcp.run(transport='stdio')
