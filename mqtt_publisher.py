import paho.mqtt.client as mqttClient
import time
import json
import ssl
import os
from dotenv import load_dotenv
import sys, getopt


load_dotenv()

# Argumentos
arg_list = sys.argv[1:]

# Opções de argumentos na execução do programa
arg_options = "v:hc:l:"

# Opções de argumentos na execução do programa (long)
arg_long_options = ["valor=", "help", "context=", "label="]

# Definição de labels existentes
labels = ["temperatura", "tempodejogo", "nomedojogo", "usocpu"]

# Definição de variáveis para conexão com ubidots
connected = False
BROKER_ENDPOINT = "industrial.api.ubidots.com"
TLS_PORT = 8883
MQTT_USERNAME = os.getenv("UBIDOTS_TOKEN")
MQTT_PASSWORD = ""  # Leave this in blank
TOPIC = "/v1.6/devices/"
DEVICE_LABEL = "retropie"
TLS_CERT_PATH = "./industrial.pem"



def on_connect(client, userdata, flags, rc):
    global connected 
    if rc == 0:

        print("[INFO] Connected to broker")
        connected = True
    else:
        print("[INFO] Error, connection failed")


def on_publish(client, userdata, result):
    print("Published!")


def connect(mqtt_client, mqtt_username, mqtt_password, broker_endpoint, port):
    global connected

    if not connected:
        mqtt_client.username_pw_set(mqtt_username, password=mqtt_password)
        mqtt_client.on_connect = on_connect
        mqtt_client.on_publish = on_publish
        mqtt_client.tls_set(ca_certs=TLS_CERT_PATH, certfile=None,
                            keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
                            tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
        mqtt_client.tls_insecure_set(False)
        mqtt_client.connect(broker_endpoint, port=port)
        mqtt_client.loop_start()

        attempts = 0

        while not connected and attempts < 5:  # Wait for connection
            print(connected)
            print("Attempting to connect...")
            time.sleep(1)
            attempts += 1

    if not connected:
        print("[ERROR] Could not connect to broker")
        return False

    return True


def publish(mqtt_client, topic, payload):

    try:
        mqtt_client.publish(topic, payload)

    except Exception as e:
        print("[ERROR] Could not publish data, error: {}".format(e))

def get_payload(context, valor):
    if valor is None:
        valor = 0
    if context is None:
        return {"value": int(valor)}
    else:
        return {"value": int(valor), "context": {"name": context}}


def handle_publish(mqtt_client, valor, context, label):
    payload = json.dumps({label: get_payload(context, valor)})
    print(payload)
    topic = "{}{}".format(TOPIC, DEVICE_LABEL)

    if not connect(mqtt_client, MQTT_USERNAME,
                   MQTT_PASSWORD, BROKER_ENDPOINT, TLS_PORT):
        return False

    publish(mqtt_client, topic, payload)

    return True

def main():
    try:
        valor, context, label = None, None, None
        args, values = getopt.getopt(arg_list, arg_options, arg_long_options)

        for current_argument, current_value in args:
            if current_argument in ("-v", "--valor"):
                valor = current_value
                if str.upper(valor) == "HELP" or str.upper(valor) == "-H" or valor is None:
                    print("Valor é o valor do dado que será enviado para o servidor MQTT")
                    sys.exit()
                elif valor.isnumeric() is False:
                    print("Valor não é um número")
                    sys.exit()
            elif current_argument in ("-c", "--context"):
                context = current_value
                if str.upper(context) == "HELP" or str.upper(context) == "-H" or context is None:
                    print("Context é o contexto do dado que será enviado para o servidor MQTT (uso para nome do jogo)")
                    sys.exit()
            elif current_argument in ("-l", "--label"):
                label = current_value
                if str.upper(label) == "HELP" or str.upper(label) == "-H":
                    print("Label é o nome da variável que será alterada no servidor MQTT")
                    sys.exit()
                elif label is None:
                    print("Label é o nome da variável que será alterada no servidor MQTT")
                    print("Label é obrigatório")
                    sys.exit()
                elif label not in labels:
                    print("Label não é válido")
                    print("Labels válidos: ", labels)
                    sys.exit()
            elif current_argument in ("-h", "--help"):
                print("Usos: mqttserver.py -v <valor> -l <label> \n mqttserver.py -c <context> -l <label> \n mqttserver.py -h \n mqttserver.py --help")
                sys.exit()

    except getopt.error as err:
        print(str(err))
        sys.exit(2)

    handle_publish(mqtt_client, valor, context, label)

if __name__ == '__main__':
    mqtt_client = mqttClient.Client()
    main()
    time.sleep(5) # Sleep necessário para programa não acabar antes de concluir publish