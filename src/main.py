import asyncio
from server import run_opcua_server

async def main():
    await run_opcua_server()

if __name__ == '__main__':
    asyncio.run(main())
