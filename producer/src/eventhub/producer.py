import json

from azure.eventhub import EventHubProducerClient, EventData


class EventHubPublisher:

    def __init__(self, connection_string, eventhub_name):

        self.producer = EventHubProducerClient.from_connection_string(
            conn_str=connection_string,
            eventhub_name=eventhub_name
        )

    def publish(self, event):

        batch = self.producer.create_batch()

        batch.add(
            EventData(
                json.dumps(event)
            )
        )

        self.producer.send_batch(batch)