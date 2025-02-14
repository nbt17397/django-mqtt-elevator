from django.apps import AppConfig
import threading 
# from .mqtt import connect_mqtt

class ElevatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'elevator'

    # def ready(self):
    #     mqtt_thread = threading.Thread(target=self.start_mqtt)
    #     mqtt_thread.setDaemon(True) 
    #     mqtt_thread.start()

    # def start_mqtt(self): 
    #     client = connect_mqtt() 
    #     client.loop_forever()