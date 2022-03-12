#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

channel.queue_declare(queue='queries_queue', durable=True)


def find_path(start, end) -> list[str]:
    return [start, end]


def on_request(ch, method, props, body):
    start, end = eval(body)

    response = find_path(start, end)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id,  delivery_mode=2),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='queries_queue', on_message_callback=on_request)

print(" [x] Awaiting requests")
channel.start_consuming()
