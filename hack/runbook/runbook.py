import httpx
import mcp.types as types

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from mcp.server import Server
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.prompts import base
from typing import Any

from db import Database

class db(object):

    async def disconnect():
        pass


class Database(object):

    async def connect():
        return db()


@dataclass
class AppContext:
    db: Database


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    # TODO(kenji): Also start the HTTP server and provide the Rest endpoint for managing the runbooks?
    db = await Database.connect()
    try:
        yield AppContext(db=db)
    finally:
        await db.disconnect()


# Pass lifespan to server
mcp = FastMCP("Runbook", lifespan=app_lifespan)



@mcp.resource("runbooks://runbooks")
def list_runbooks() -> str:
    return "App configuration here"


@mcp.resource("runbooks://runbooks/{runbook_id}")
def get_runbook(runbook_id: str) -> str:
    # TODO(kenji): Use Context once https://github.com/modelcontextprotocol/python-sdk/issues/244 is fixed.
    return f"Profile data for user {runbook_id}"


@mcp.tool()
async def create_runbook(name: str, ctx: Context) -> str:
    db = ctx.request_context.lifespan_context["db"]
    pass


@mcp.prompt()
def list_pods_in_namespace(namespace: str) -> str:
    # TODO(kenji): Figure out how to use Context for prompts.
    return f"List pods in a Kubernetes cluster's {namespace} namespace"



if __name__ == "__main__":
    mcp.run(transport='stdio')
