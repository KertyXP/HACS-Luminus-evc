import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from custom_components.luminus_evc.luminus_api import LuminusApiClient

async def main():
    u = sys.argv[1] if len(sys.argv) > 1 else os.getenv("LUMINUS_USER", "simon.marchal")
    p = sys.argv[2] if len(sys.argv) > 2 else os.getenv("LUMINUS_PASS", "")
    s = sys.argv[3] if len(sys.argv) > 3 else os.getenv("LUMINUS_SPOT", "1234606393")

    if not p:
        print("Usage: python test_async_client.py <username> <password> [spot_id]")
        return

    client = LuminusApiClient(u, p, s)
    try:
        print("[*] Logging in...")
        await client.async_login()
        print("[+] Logged in successfully!")

        print("[*] Fetching data...")
        data = await client.async_fetch_data()
        print("[+] Parsed data successfully:")
        print(json.dumps(data, indent=2))
    finally:
        await client.async_close()

if __name__ == "__main__":
    asyncio.run(main())
