import network
import urequests
import time
from machine import ADC, Pin
import onewire, ds18x20

# Wi-Fi credentials
SSID = "Net gone?"
PASSWORD = "Mahi@665"

# Flask API endpoint
FLASK_SERVER = "http://192.168.99.21:5000/api/submit"

# Pin configuration
soil = ADC(Pin(34))  # Soil moisture sensor
soil.atten(ADC.ATTN_11DB)

ds_pin = Pin(4)  # DS18B20 data pin (use GPIO 4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

relay = Pin(2, Pin.OUT)  # Relay for water motor

# Search for DS18B20 devices
roms = ds_sensor.scan()
print('DS sensor found:', roms)

# Thresholds
MOISTURE_THRESHOLD = 2000
TEMP_THRESHOLD = 30

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        time.sleep(1)
    print("Connected to Wi-Fi:", wlan.ifconfig())
    return wlan

def get_temperature():
    try:
        ds_sensor.convert_temp()
        time.sleep_ms(750)  # Wait for conversion
        temp = ds_sensor.read_temp(roms[0])
        return temp
    except Exception as e:
        print("DS18B20 error:", e)
        return -1

def send_data(moisture, temp, pump_status):
    try:
        data = {
            "moisture": moisture,
            "temperature": temp,
            "pump_status": pump_status
        }
        print("Sending:", data)
        res = urequests.post(FLASK_SERVER, json=data, timeout=5)
        print("Response:", res.text)
        res.close()
    except Exception as e:
        print("Failed to send:", e)

# Connect to Wi-Fi
wlan = connect_wifi()

# Main loop
while True:
    temp = get_temperature()
    moisture = soil.read()
    print("Moisture:", moisture, "Temp:", temp)

    if moisture > MOISTURE_THRESHOLD and temp > TEMP_THRESHOLD:
        relay.value(0)
        pump_status = "ON"
    else:
        relay.value(1)
        pump_status = "OFF"  

    send_data(moisture, temp, pump_status)
    time.sleep(10)
