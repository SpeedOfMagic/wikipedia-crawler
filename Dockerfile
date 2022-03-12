FROM python:3.9.10-slim

COPY requirements.txt .
COPY src .

RUN pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. crawler.proto

CMD python3 server.py