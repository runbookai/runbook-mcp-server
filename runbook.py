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

from database import Config
from database import Store
from database import Runbook


conf = Config('./config.yaml')
store = Store(conf.database_uri)
store.run_migrations(conf.migration_dir)

# Create a runbook file dir if it does not exist.
runbook_file_dir = conf.runbook_file_dir

if not os.path.exists(conf.runbook_file_dir):
    os.makedirs(conf.runbook_file_dir)

if not os.path.exists(conf.runbook_log_dir):
    os.makedirs(conf.runbook_log_dir)


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
    # Generate a uuid and set to the external_id
    external_id = uuid4()

    # Create a runbook file and save the content.
    file_path = f"{name}_{external_id}.md"
    with open(os.path.join(runbook_file_dir, file_path), 'w') as f:
        f.write(content)

    r = Runbook(external_id, name, file_path)
    store.create_runbook(r)
    return "Created a new runbook"


@mcp.tool()
async def delete_runbook(name: str) -> str:
    r = store.get_runbook_by_name(name)

    file_path = os.path.join(runbook_file_dir, r.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    store.delete_runbook_by_name(name)
    return "Deleted the runbook"


@mcp.prompt()
def get_runbook_as_prompt(name: str) -> str:
    # TODO(kenji): Consider taking additional argument for
    # substituting template parameters.
    r = store.get_runbook_by_name(name)

    content = ""
    with open(os.path.join(runbook_file_dir, r.file_path), 'r') as f:
        content = f.read()

    return f"Run the following prompt:\n{content}"


if __name__ == "__main__":
    mcp.run(transport='stdio')
