# mi-copilot

### How to generate Proto buf code
```
python -m grpc_tools.protoc -Iprotos --python_out=generated --pyi_out=generated --grpc_python_out=generated protos/copilot.proto
```

### How to run
1. Set `OPENAI_API_KEY` and `PORT` environment variables
2. Run `python -m app.server` from the root directory
3. Run `python -m tests.client` from the root directory
4. Change `prompt` in `client.py` to test different prompts