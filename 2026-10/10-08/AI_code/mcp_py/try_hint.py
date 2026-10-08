import asyncio
import json

from mcp import Client

from hint_server import mcp


async def main() -> None:
    async with Client(mcp) as client:
        for tool in (await client.list_tools()).tools:
            print(tool.name, json.dumps(tool.input_schema["properties"], ensure_ascii=False))
            print("  outputSchema:", tool.output_schema is not None)

        for name in ["add_hint", "add_nohint"]:
            for args in [{"a": "3", "b": 4}, {"a": "3", "b": "4"}]:
                r = await client.call_tool(name, args)
                print(name, args, "→", r.is_error, r.content[0].text)


asyncio.run(main())