import asyncio
import os
import uvloop
import logging
import signal
import grpc
from app.copilot import Copilot
from grpc_interfaces.copilot_pb2_grpc import add_CopilotServicer_to_server

from dotenv import load_dotenv
load_dotenv()

PORT = os.getenv("PORT")

# Make uvloop the default event loop for asyncio
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def serve():
    server = grpc.aio.server()
    add_CopilotServicer_to_server(Copilot(), server)
    server.add_insecure_port("[::]:" + PORT)
    
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(shutdown_server(server)))
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(shutdown_server(server)))
    loop.add_signal_handler(signal.SIGTSTP, lambda: asyncio.create_task(shutdown_server(server)))

    logging.info("Starting server")
    await server.start()
    try:
        await server.wait_for_termination()
    finally:
        await server.stop(None)

async def shutdown_server(server):
    await server.stop(None)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
