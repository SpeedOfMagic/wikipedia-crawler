#!/usr/bin/env python
import pika
from server_config import QUERY_QUEUE_NAME, MAX_PATH_LEN
from crawler import get_links

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

channel = connection.channel()
channel.queue_declare(queue=QUERY_QUEUE_NAME, durable=True)


def on_request(ch, method, props, body):
    path, end = eval(body)
    print(f'Processing link {path[-1]} on path of length {len(path)}')
    if len(path) > MAX_PATH_LEN:
        print('Path limit exceeded')
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    nxt_pages = get_links(path[-1])

    lang_link = end.split('/wiki/')[0] + '/wiki/'
    nxt_link = list(filter(lambda l: l not in path, map(lambda page: lang_link + page, nxt_pages)))
    if end in nxt_link:
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=props,
                         body=str(path + [end]))
    else:
        if len(path) == MAX_PATH_LEN:
            print('Aborting, since path limit will be exceeded')
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        for link in nxt_link:
            new_path = path + [link]
            ch.basic_publish(exchange='',
                             routing_key=QUERY_QUEUE_NAME,
                             properties=props,
                             body=str((new_path, end)))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=QUERY_QUEUE_NAME, on_message_callback=on_request)

print(" [x] Awaiting requests")
channel.start_consuming()
