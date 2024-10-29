import paho.mqtt.client as mqttClient
import time
import json
import ssl
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

# Ubidots configurations
connected = False  # Stores the connection status
BROKER_ENDPOINT = "industrial.api.ubidots.com"
TLS_PORT = 8883  # Secure port
MQTT_USERNAME = os.getenv("UBIDOTS_TOKEN")  # Put here your Ubidots TOKEN
MQTT_PASSWORD = ""  # Leave this in blank
TOPIC = "/v1.6/devices/"
DEVICE_LABEL = "retropie"
VARIABLE_LABEL = ["reqtemperatura", "reqcpu"]
TLS_CERT_PATH = "./industrial.pem"  # Put here the path of your TLS cert
sub1 = TOPIC + DEVICE_LABEL + "/" + VARIABLE_LABEL[0] + "/lv"
sub2 = TOPIC + DEVICE_LABEL + "/" + VARIABLE_LABEL[1] + "/lv"
MQTT_TOPICS = [(sub1, 0), (sub2, 0)]


def on_connect(client, userdata, flags, rc):
    global connected  # Use global variable
    if rc == 0:

        print("[INFO] Connected to broker")
        connected = True  # Signal connection
        client.subscribe(MQTT_TOPICS)
    else:
        print("[INFO] Error, connection failed")


def on_message(client, userdata, msg):
    topic = msg.topic

    try:
        data = json.loads(msg.payload)
        print(data)

        if "reqtemperatura" in topic:
            send_temperature(data)
        elif "reqcpu" in topic:
            #send_cpu(data)
            print("CPU: ", data)

    except Exception as e:
        print(e)


def send_temperature(data):
    data = int(data)

    if data == 0: # Enviar temperatura apenas quando botão for ON
        return

    # Rodar script para pegar temperatura antes

    # temperatura = subprocess.run(["caminho/do/script", "args"], capture_output=true)
    # data = temperatura
    
    subprocess.run(["python", "main.py", "-v", str(data), "-l", "temperatura"]) # Executa comando
    # Por conta do sleep do main.py, pode atrasar caso chame CPU em seguida 
    # --> Ver se é possível executar em segundo plano

def send_cpu(data):
    data = int(data)

    if data == 0:
        return

    # Rodar script para pegar % cpu antes

    # cpu = subprocess.run(["caminho/do/script", "args"], capture_output=true)
    # data = cpu

    subprocess.run(["python", "main.py", "-v", str(data), "-l", "temperatura"]) # Executa comando
    # Por conta do sleep do main.py, pode atrasar caso chame Temperatura em seguida 
    # --> Ver se é possível executar em segundo plano


def connect(mqtt_client, mqtt_username, mqtt_password, broker_endpoint, port):
    global connected  # Use global variable

    if not connected:
        mqtt_client.username_pw_set(mqtt_username, password=mqtt_password)
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.tls_set(ca_certs=TLS_CERT_PATH,
                            certfile=None,
                            keyfile=None,
                            cert_reqs=ssl.CERT_REQUIRED,
                            tls_version=ssl.PROTOCOL_TLSv1_2,
                            ciphers=None)
        mqtt_client.tls_insecure_set(False)
        mqtt_client.connect(broker_endpoint, port=port)
        mqtt_client.loop_start()

        attempts = 0

        while not connected and attempts < 5:  # Wait for connection
            print(connected)
            time.sleep(1)
            attempts += 1

        if not connected:
            print("[ERROR] Could not connect to broker. Aborting...")
            return False

    return True


if __name__ == "__main__":
    mqtt_client = mqttClient.Client()
    connect(mqtt_client, MQTT_USERNAME, MQTT_PASSWORD, BROKER_ENDPOINT,
            TLS_PORT)

    while True:
        time.sleep(1)
