import asyncio
import logging
import os
import grpc
from grpc_interfaces import copilot_pb2
from grpc_interfaces import copilot_pb2_grpc
from dotenv import load_dotenv

load_dotenv()
PORT = os.getenv("PORT")

prompt = "Generate a hello world api"

async def run() -> None:
    async with grpc.aio.insecure_channel("localhost:" + PORT) as channel:
        stub = copilot_pb2_grpc.CopilotStub(channel)
        chat = copilot_pb2.Chat(messages=[
            copilot_pb2.Message(role=copilot_pb2.Message.USER, content=prompt),
            ])
        async for response in stub.GenerateIntegration(chat):
            print(response.data, end="")

if __name__ == "__main__":
    logging.basicConfig()
    asyncio.run(run())
