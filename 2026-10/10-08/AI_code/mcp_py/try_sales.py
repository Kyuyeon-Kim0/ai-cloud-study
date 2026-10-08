import asyncio
import json

from mcp import Client

from sales_server import mcp


async def main() -> None:
    async with Client(mcp) as client:
        for tool in (await client.list_tools()).tools:
            print(tool.name, json.dumps(tool.input_schema, ensure_ascii=False))

        cases = [
            ("region_total", {"region": "서울"}),
            ("region_total", {"region": "광주"}),
            ("top_regions", {"n": 2}),
            ("top_regions", {"n": 5}),
            ("add_sale", {"sale": {"region": "부산", "amount": 50}}),
            ("add_sale", {"sale": {"region": "인천", "amount": 50}}),
            ("broken", {}),
        ]
        for name, args in cases:
            r = await client.call_tool(name, args)
            print(f"{name} {args} → isError={r.is_error}")
            print("  ", r.structured_content if not r.is_error else r.content[0].text.splitlines()[0])


asyncio.run(main())