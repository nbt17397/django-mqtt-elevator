from dmqtt.signals import connect, regex, topic
from django.dispatch import receiver

@receiver(connect)
def on_connect(sender, **kwargs):
    print('on_connect')
    sender.subscribe("#")
    sender.subscribe("clients/connected") 
    sender.subscribe("clients/disconnected")


# Hàm này được gọi khi có một tin nhắn được (publish) đến topic "some/mqtt/topic"
@topic("some/mqtt/topic")
def simple_topic(sender, topic, data, **kwargs):
    print(topic)
    print(data)


@receiver(topic("clients/connected")) 
def client_connected_topic(sender, topic, data, **kwargs): 
    print(f"Client connected: {data}") 


@receiver(topic("clients/disconnected"))     
def client_disconnected_topic(sender, topic, data, **kwargs): 
    print(f"Client disconnected: {data}")


# Hàm này được gọi khi có một tin nhắn được xuất bản đến bất kỳ topic nào khớp với biểu thức chính quy (regex) ^some/(?P<username>[^/]+)/(?P<device>[^/]+)$
@regex("^some/(?P<username>[^/]+)/(?P<device>[^/]+)$")
def regex_topic(match, data, **kwargs):
    device = match.groupdict()
    print(device['username'], device['device'])
    print(data)
