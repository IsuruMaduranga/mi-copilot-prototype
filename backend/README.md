# mi-copilot

### How to run the project
1. With Gunicorn process manager - multi worker
```bash
gunicorn gunicorn  app.main:api
```

2. With Uvicorn single worker (for development)
```bash
uvicorn app.main:api --reload
```
You can check swagger documentation at http://127.0.0.1:8000/docs
