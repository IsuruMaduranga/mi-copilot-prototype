import aiohttp
import asyncio
import json

async def stream_data(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers={"Content-Type": "application/json"}) as response:
            async for chunk in response.content.iter_chunks():
                if not chunk[0]:
                    break
                res = json.loads(chunk[0])
                if res["content"]:
                    print(res["content"], end="")
                if res["questions"]:
                    print("\n\n ____ You may ask ____ \n")
                    print("\n".join(res["questions"]))

async def main():
    data = {
        "chat_history": [
            {
                "role": "user",
                "content": "Who are you"
            }
        ]
    }
    url = 'http://localhost:8000/generate-synapse'
    await stream_data(url, json.dumps(data))

if __name__ == "__main__":
    asyncio.run(main())