# mi-copilot

### Steps to run the backend locally
1. Clone the repository and navigate to the backend directory
2. Install Python 3.8 or higher
3. Create a virtual environment and activate it
```bash
python -m venv .venv
source .venv/bin/activate
```

4. Install the dependencies
```bash 
pip install -r requirements.txt
```

5. Add the environment variables to a .env file in the backend directory
```bash
echo "OPENAI_API_KEY=<your_openai_api_key>" > .env
```
6. Start Copilot server
* With Gunicorn process manager - multi worker
```bash
gunicorn server:api
```

* With Uvicorn single worker (for development)
```bash
uvicorn server:api --reload
```
### Docs
* OpenAPI - http://127.0.0.1:8000/docs
* Redoc - http://127.0.0.1:8000/redoc
* OpenAPI JSON - http://127.0.0.1:8000/openapi.json
* OpenAPI YAML - http://127.0.0.1:8000/openapi.yaml
