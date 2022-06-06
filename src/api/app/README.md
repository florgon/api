# Florgon API server application.
Provides full FastAPI API application with tests.

### How to run
Please see root source directory of the repository. 
For now application is based on Docker + Docker Compose.

### Tests
For testing please run `pytest` inside your docker server container.

### Configuration
Please specify settings inside `.server.env` in the repository source directory (Docker-Compose).

### Requirements
See `requirements.txt` in `..`. Should be installed at build time of docker container.

### Docker
Server should be instantiated with docker-compose as it requires PostgreSQL and Redis instances.

### Running without Docker
Notice that this is not recommended and supported, but you may try
to run own instances of PostgreSQL + Redis and setup config, this will may work as should, but currently
this way of instantiating the server is not recommended, please use docker and docker-compose instead.
