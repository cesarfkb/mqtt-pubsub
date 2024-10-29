# Programa para pub/sub com ubidots

## Ubidots
Criar um dashboard no ubidots com device **retropie** e a seguinte listas de variáveis (raw variable): 

 - reqcpu
 - usocpu
 - reqtemperatura
 - temperatura
 - tempodejogo
 - nomedojogo

Lista de variável -> widget:
 - reqcpu -> switch
 - usocpu -> metric
 - reqtemperatura -> switch
 - temperatura -> metric
 - tempodejogo -> metric
 - nomedojogo -> metric

Para nome do jogo é necessário alterar a aparência do widget e mudar o HTML para exibir {`context.name`}

## Requerimentos
Instalar requerimentos
```
pip install -r requirements.txt
```

## Rodar programa
Uso do mqtt_publisher.py

```python mqtt_publisher.py -h``` para ver usos.

Label é obrigatório e dashboard do Ubidots deve conter variáveis de mesmo nome

mqtt_sub.py deve ser executado junto à inicialização do emulador

## Observação
Criar um .env e definir UBIDOTS_TOKEN com a chave do Ubidots

mqtt_sub.py não está completo. Alterar ```send_temperature``` e ```send_cpu``` para executar o script necessário.

