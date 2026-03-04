## Docker

### Prerequisites

https://docs.docker.com/desktop/setup/install/mac-install/

#### Verify Docker is installed
`docker --version`

#### Verify Docker Compose is installed
`docker-compose --version`

#### Verify Docker daemon is running
`docker info`


Getting Started: https://docs.docker.com/compose/gettingstarted/

Docker
The classic pain: "It works on my machine." Your app runs fine locally but breaks in production because the OS, Python version, library versions, or environment variables differ.
Docker packages your app together with everything it needs to run into a single portable unit called a Container

Dockerfile  →  Image  →     Container (running instance of an image)
(recipe)       (cake mold)  (actual cake)

Docker Engine:
- Docker Engine is the background daemon dockerd.
- `docker run` CLI sends a request to dockerd : Pulls the image if needed, Creates the container, and Starts it. 
- You never interact with containerd or runc directly — Docker Engine abstracts all of it.
docker CLI  →  REST API  →  dockerd (daemon)        →  containerd       →  runc
(you type)                  (orchestrates)              (manages)      (runs container)
                            (pulls the image if needed)

Docker Compose:
- Managing multiple services — API, database, Redis, worker `docker run` commands is painful -> Docker Compose solves this.
- Compose defines entire multi-container system in a single `docker-compose.yml`

- Images:
- Base Image: Standard Images (Ubuntu or Debian OS), Slim Images (minimal versions of standard images), Scratch Image (entirely empty initial layer).
- User-built Image: Custom image created using a Dockerfile that specifies a base image & Adds additional layers on top: like App code, dependencies, and specific configurations.


---

#### The General Principle: Dockerfiles

This pattern reveals a broader rule for writing efficient Dockerfiles:

> **Copy things that change less frequently first. Copy things that change more frequently last.**

Ranked from least to most frequently changing:

Base OS image          → never changes
System packages        → rarely changes  
Dependency file        → occasionally changes
Application code       → changes constantly


Goal:
- development of a basic Python web application using Docker


#### Run Docker 

##### 1. Build the image
`docker build -t MY_IMAGE_NAME .`
- `-t MY_IMAGE_NAME`: The optional tag (-t or --tag) which Gives a Human-Readable name. Without this Docker builds the image with Random ID 
- Optional: Version Tag (e.g., MY_IMAGE_NAME:Version_Tag) to the resulting image can be added. If not specified, Docker defaults to `:latest` automatically.
- `.`:  Build context tells Docker which directory to use as the root when executing the Dockerfile. `Dockerfile` should be available in this path

`docker build -t my-model-app .`
- Image `localhost/my-model-app:latest` will be created

- Images are stored: 
- `docker.io/library/` : Remote (Public) Registry. Images stored in Remote Docker Hub registry 
- `localhost` : Local Images/Registry. Images stores in our Local machine's image cache

##### 2. Run the container
`docker run -d -p HOST_PORT:CONTAINER_PORT --name CONTAINER_NAME IMAGE_NAME`
- `docker run`: The command is used to run a container
- `-d` (detach): Runs the Container in the background
- `-p` (publish): Maps <Host_Port : Container_Port>
- `--name`: Assigns Custom name to the container

`docker run -d -p 8000:8000 --name hello hello-fastapi`
`docker run -d --name python_test python:3.11-slim`

- Note: If the Image is not available in local, then it would be first copied from Public Registry

##### 3. Test it
curl http://localhost:8000
