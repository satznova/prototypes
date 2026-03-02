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