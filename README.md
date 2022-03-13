# wikipedia-crawler

Python client-server application that reads two Wikipedia articles and tries to find the shortest path between them.

Made for SOA-22 course in HSE.

# How to launch server

1. Launch rabbitmq: `docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.9-management`
2. Read config from `server_config.py` and be sure, that everything is exactly as you want it.
3. Launch worker: `python3 worker.py`
4. Launch server: `python3 server.py`
