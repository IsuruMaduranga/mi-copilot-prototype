import grpc
from grpc_interfaces.copilot_pb2 import Chat, StringChunk
from grpc_interfaces.copilot_pb2_grpc import CopilotServicer
from app.llm import generate_synapse

class Copilot(CopilotServicer):
    
    async def GenerateIntegration(self, request: Chat, context: grpc.aio.ServicerContext) -> StringChunk:
            async for chunk in generate_synapse(request):
                yield chunk
