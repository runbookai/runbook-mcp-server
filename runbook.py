import httpx
import json
import mcp.types as types

from uuid import uuid4

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from mcp.server import Server
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.prompts import base
from typing import Any

from database import Config
from database import Store
from database import Runbook


conf = Config('./config.yaml')
store = Store(conf.database_uri)
store.run_migrations(conf.migration_dir)


mcp = FastMCP("Runbook")

# TODO(kenji): Use Context once https://github.com/modelcontextprotocol/python-sdk/issues/244 is fixed.

@mcp.resource("runbooks://runbooks")
def list_runbooks() -> str:
    rs = store.list_runbooks()
    return json.dumps([r.to_json() for r in rs])


@mcp.resource("runbooks://runbooks/{name}")
def get_runbook(name: str) -> str:
    r = store.get_runbook_by_name(name)
    return json.dumps(r.to_json())


@mcp.tool()
async def create_runbook(name: str, content: str) -> str:
    external_id = uuid4()
    r = Runbook(external_id, name, content)
    store.create_runbook(r)
    return "Created a new runbook"

@mcp.tool()
async def delete_runbook(name: str) -> str:
    store.delete_runbook_by_name(name)
    return "Deleted the runbook"


@mcp.prompt()
def get_runbook_as_prompt(name: str) -> str:
    # TODO(kenji): Consider taking additional argument for
    # substituting template parameters.
    r = store.get_runbook_by_name(name)
    return f"Run the following prompt:\n{r.content}"


if __name__ == "__main__":
    mcp.run(transport='stdio')
