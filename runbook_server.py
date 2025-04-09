import httpx
import json
import os
import mcp.types as types

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


conf = Config('./config.yaml')
conf.validate()

if not os.path.exists(conf.runbook_logs_dir):
    os.makedirs(conf.runbook_logs_dir)

search_engine = RunbookSearchEngine(conf.runbooks_dir, conf.runbooks_index_dir)


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
    with open(os.path.join(runbook_file_dir, file_path), "w") as f:
        f.write(content)

    # TODO(kenji): Reindex the runbook.

    return "Created a new runbook"


@mcp.tool()
async def delete_runbook(name: str) -> str:
    r = store.get_runbook_by_name(name)

    # TODO(kenji): Reindex the runbook.

    file_path = os.path.join(runbook_file_dir, r)
    if os.path.exists(file_path):
        os.remove(file_path)

    return "Deleted the runbook"


@mcp.prompt()
def get_runbook_as_prompt(name: str) -> str:

    rs = search_engine.search_runbooks(name, limit=1)
    if not rs:
        raise ValueError(f"Runbook {name} not found")
    r = rs[0]

    content = ""
    with open(r["path"], "r") as f:
        content = f.read()

    return f"Run the following prompt:\n{content}"


if __name__ == "__main__":
    mcp.run(transport='stdio')
