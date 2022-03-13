from concurrent import futures
import grpc
import socket
import pika
import requests
from time import sleep
import uuid

import crawler_pb2_grpc
from crawler_pb2 import Request, Response
from crawler_pb2_grpc import WikipediaCrawlerServicer
from server_config import PORT, QUERY_QUEUE_NAME, TTK


class Servicer(WikipediaCrawlerServicer):
    corr_id: str

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', heartbeat=0))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='', exclusive=True, durable=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)
        self.response = None

    def on_response(self, _, __, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def find_connection(self, request: Request, context) -> Response:
        print(f'Got request to find connection from "{request.start_article}" to "{request.end_article}"')
        try:
            assert requests.get(request.start_article).ok
            assert requests.get(request.end_article).ok
        except Exception:
            return Response(articles=[])
        print('Approved request')
        if request.start_article == request.end_article:
            return Response(articles=[request.start_article])

        self.corr_id = str(uuid.uuid4())
        self.response = None
        self.channel.basic_publish(
            exchange='',
            routing_key=QUERY_QUEUE_NAME,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                delivery_mode=2,
                correlation_id=self.corr_id,
            ),
            body=str(([request.start_article], request.end_article)))

        ttk = TTK
        while self.response is None and ttk > 0:
            print(ttk)
            self.connection.process_data_events()
            sleep(1)
            ttk -= 1
        return Response(articles=eval(self.response) if self.response is not None else [])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    crawler_pb2_grpc.add_WikipediaCrawlerServicer_to_server(Servicer(), server)
    ip = socket.gethostbyname(socket.gethostname())
    server.add_insecure_port(f'{ip}:{PORT}')
    server.start()
    print(f'Running on IP: {ip}')
    print(f'Running on port: {PORT}')
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
