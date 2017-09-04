import boto3

class MQ(object):
    _queue = None
    
    def __init__(self, config):
        client = boto3.resource('sqs', region_name=config.get("region", None))
        self._queue = client.get_queue_by_name(QueueName=config["queue"])
        
    def send(self, message):
        response = self._queue.send_message(MessageBody=message)
        