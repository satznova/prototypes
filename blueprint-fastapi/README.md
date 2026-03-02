## FASTAPI

Reference Documentation for implementing FastAPI Application

- FastAPI on its own is just a Python object. 
- It has no ability to listen on a port or accept network connections. Uvicorn is what gives it that ability.

- Uvicorn is the Web Server that actually runs your FastAPI application
- Sits between the outside world (Users) and our Python code
- Uvicorn is the network layer that lets your FastAPI app speak HTTP with the outside world — FastAPI handles what to do with requests, Uvicorn handles receiving and sending them.

Browser / curl / Client
         ↓
      Uvicorn          ← the web server (handles HTTP, network, connections)
         ↓
     FastAPI           ← your Python code (handles routing, business logic)



#### Run FastAPI Application

- `uvicorn <PYTHON_FILE_NAME>:<FASTAPI_INSTANCE_VAR_NAME> --reload`

`uvicorn hello-world:app --reload` --> http://127.0.0.1:8000
- `-reload` : Enables Auto-reloading (Hot-reloading) during development. Tells Uvicorn to watch for changes in source code and restart the server automatically when a change detected.
- Use `--port 8000` to specify the port explicitly 

`fastapi dev hello-world.py`  --> http://127.0.0.1:8000
- Concise command provided by the fastapi-cloud-cli
- Internally uses uvicorn

- FastAPI instance variable can be something other than `app` as well.
- ```
  from fastapi import FastAPI

  api_instance = FastAPI()
  
  @api_instance.get("/")
  def read_root():
    return {"Hello": "World"}
  ```
- `uvicorn hello-world:app_instance --reload`


##### To Access Automatic Docs

- **Swagger UI** http://127.0.0.1:8000/docs
- **ReDoc** http://127.0.0.1:8000/redoc
- **OpenAPI Schema** http://127.0.0.1:8000/openapi.json

- **Path Operation Decorator** : 
  - `@app.get("/")`: This decorator tells FastAPI that the function below corresponds to the **path** / with an **operation** get.


##### Route Ordering

`uvicorn path-query-param:app --reload` --> http://127.0.0.1:8000

- Parameterized Routes should come AFTER Specific hardcoded routes
