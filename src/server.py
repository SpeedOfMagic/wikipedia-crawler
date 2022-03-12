from concurrent import futures
import grpc
import socket
import pika
import uuid

import crawler_pb2_grpc
from crawler_pb2 import Request, Response
from crawler_pb2_grpc import WikipediaCrawlerServicer
from server_config import PORT


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
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='query_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
                delivery_mode=2,
            ),
            body=str([request.start_article, request.end_article]))
        while self.response is None:
            self.connection.process_data_events()
        assert self.response is not None
        return Response(articles=eval(self.response))


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
