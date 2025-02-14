import paho.mqtt.client as mqtt
import requests
import uuid, re

DJANGO_SERVER_URL = "http://localhost:8000/mqtt/event/"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    if rc == 0:
        print("Kết nối thành công")
        client.subscribe("$SYS/broker/clients/connected")
        client.subscribe("$SYS/broker/clients/disconnected")
    else:
        print(f"Kết nối thất bại với mã lỗi {rc}")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} -> {msg.payload.decode()}")
    if msg.topic == "$SYS/broker/clients/connected":
        event_data = {
            "event": "connected",
            "client_id": msg.payload.decode()
        }
    elif msg.topic == "$SYS/broker/clients/disconnected":
        event_data = {
            "event": "disconnected",
            "client_id": msg.payload.decode()
        }
    else:
        event_data = {
            "topic": msg.topic,
            "payload": msg.payload.decode()
        }
    print(event_data)
    # response = requests.post(DJANGO_SERVER_URL, json=event_data)
    # print(f"Event sent to Django: {response.status_code}")

def on_disconnect(client, userdata, rc):
    print("Mất kết nối với mã lỗi " + str(rc))
    if rc != 0:
        print("Mất kết nối không mong muốn. Đang thử kết nối lại...")
        client.reconnect()


def check_topic(topic):
    pattern = r"^control/user(?P<username>\d+)/device(?P<device>\d+)$"
    match = re.match(pattern, topic)
    if match:
        print("Topic khớp với biểu thức chính quy.")
        print("Username:", match.group("username"))
        print("Device:", match.group("device"))
    else:
        print("Topic không khớp với biểu thức chính quy.")

client = mqtt.Client(client_id=str(uuid.uuid4()))
username = "admin" 
password = "admin" 
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Cài đặt thời gian chờ trước khi thử kết nối lại
client.reconnect_delay_set(min_delay=1, max_delay=120)

client.connect("192.168.18.20", 1883, 60)
client.loop_forever()
