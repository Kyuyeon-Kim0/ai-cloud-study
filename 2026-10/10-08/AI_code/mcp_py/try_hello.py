import asyncio

from mcp import Client

from hello_server import mcp


async def main() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print([t.name for t in tools.tools])

        r = await client.call_tool("say_hello", {"name": "규연"})
        print(r.content[0].text)
        print(r.structured_content)

        r = await client.call_tool("now", {})
        print(r.content[0].text)

        r = await client.call_tool("dday", {"target": "2026-11-25"})
        print(r.content[0].text)


asyncio.run(main())