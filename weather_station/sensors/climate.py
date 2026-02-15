from PiicoDev_BME280 import PiicoDev_BME280

sensor = PiicoDev_BME280()

def read_climate():
    tempC, presPa, humRH = sensor.values()
    pres_hPa = presPa / 100

    return {
        "temperature": round(tempC, 2),
        "pressure": round(pres_hPa, 2),
        "humidity": round(humRH, 2)
    }
