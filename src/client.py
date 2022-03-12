import grpc

from crawler_pb2 import Request, Response
from crawler_pb2_grpc import WikipediaCrawlerStub
from server_config import PORT


def main():
    ip = input('Enter IP address of server: ').strip()
    print(f'Using port {PORT}')

    with grpc.insecure_channel(f'{ip}:{PORT}') as channel:
        stub = WikipediaCrawlerStub(channel)
        try:
            print('Interrupt to abort.')
            while True:
                start_article = input('Enter article to start from: ').strip()
                end_article = input('Enter article to finish on: ').strip()
                print('Looking for path...')
                response: Response = stub.find_connection(Request(start_article=start_article, end_article=end_article))
                path = response.articles
                print('Path found!')
                for article in path[:-1]:
                    print(f'Go to {article}, then')
                print(f'Go to {path[-1]}, and you are done!')
        except InterruptedError:
            pass
        except EOFError:
            pass


if __name__ == '__main__':
    main()
