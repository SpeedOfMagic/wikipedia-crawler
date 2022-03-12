from concurrent import futures
import grpc
import socket

import crawler_pb2_grpc
from crawler_pb2 import Request, Response
from crawler_pb2_grpc import WikipediaCrawlerServicer
from server_config import PORT


class Servicer(WikipediaCrawlerServicer):
    def find_connection(self, request: Request, context) -> Response:
        return Response(articles=[request.start_article, request.end_article])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    crawler_pb2_grpc.add_WikipediaCrawlerServicer_to_server(Servicer(), server)
    ip = socket.gethostbyname(socket.gethostname())
    server.add_insecure_port(f'{ip}:{PORT}')
    server.start()
    print(f'Running on IP: {ip}')
    print(f'Running on port: {PORT}')
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
