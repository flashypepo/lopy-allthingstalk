from settings import app_eui, app_key
from network import LoRa

import cbor
import random
import socket
import time
import pycom
import struct
import binascii
import sys

# Disable the heartbeat LED
pycom.heartbeat(False)

# Make the LED light up in black
pycom.rgbled(0x000000)

# Initialize LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN, adr=True)

# Retrieve the dev_eui from the LoRa chip (Only needed for OTAA to retrieve once)
dev_eui = binascii.hexlify(lora.mac()).upper().decode('utf-8')

# Join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)


# Wait until the module has joined the network
count = 0
while not lora.has_joined():
    pycom.rgbled(0xffa500) # Make the LED light up in orange
    time.sleep(0.2)
    pycom.rgbled(0x000000) # Make the LED light up in black
    time.sleep(2)
    print("retry join count is:" ,  count)
    count = count + 1

print("join procedure succesfull")

# Show that LoRa OTAA has been succesfull by blinking blue
pycom.rgbled(0x0000ff)
time.sleep(0.5)
pycom.rgbled(0x000000)
time.sleep(0.1)
pycom.rgbled(0x0000ff)
time.sleep(0.5)
pycom.rgbled(0x000000)

# Create a raw LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
# Set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
# Make the socket non-blocking
s.setblocking(False)

def lora_callback(lora):
    print('A LoRa event occured: ', end='')
    events = lora.events()
    if events & LoRa.RX_PACKET_EVENT:
        print('LoRa packet received')
        received = s.recv(64)
        received_object = cbor.loads(received)

        led_color_value = received_object.get('led-color', None)
        led_value = received_object.get('led', None)

        if led_color_value:
            pycom.rgbled(int(led_color_value))

        if led_value:
            if led_value == False:
                pycom.rgbled(0x000000)

    elif events & LoRa.TX_PACKET_EVENT:
        print('LoRa packet sent')


lora.callback(LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT, lora_callback)


while True:

    temperature = random.randint(1, 30)
    pressure = random.randint(50, 80)

    print(temperature)
    print(pressure)

    value_object =  {'temperature': temperature, 'pressure': pressure }
    cbor_value_object = cbor.dumps(value_object)

    # send the data over LPWAN network
    s.send(cbor_value_object)

    pycom.rgbled(0x007f00) # Make the LED light up in green
    time.sleep(0.2)
    pycom.rgbled(0x000000)
    time.sleep(2.8)

    # Wait for 60 seconds before moving to the next iteration
    time.sleep(60)
