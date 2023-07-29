"""
    API server application.
    Provides full FastAPI API application with tests.

    How to run: Please see readme in the source directory of the repository.
    For now application is based on Docker + Docker Compose.
    Tests: For testing please run `pytest` inside your server docker container.
    Configuration: Please read readme for further information.
    Requirements: Please read readme. Should be installed at build time of docker container.
    
    Docker: Server should be instantiated with docker-compose as it requires PostgreSQL, Redis, Celery and other instances.
    Running without Docker: Notice that this is not recommended and supported, but you may try
    to run own instances of requirements and setup config, this will may work as should, but currently
    this way of instantiating the server is not recommended, please use docker and docker-compose instead.
"""

from .__version__ import *
