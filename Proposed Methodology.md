## Phase 1 – Automated Monitoring System Development

In the first phase, an automated agricultural monitoring system will be developed. The core hardware platform will consist of **a programmable computing unit, an image acquisition module, environmental sensors, and a stable power supply**.

### 1.1 Hardware Components and Cost Breakdown

| **Module**              | **Product**                                        | **Link**                                                                                               | **Price (AUD)** |
|-------------------------|----------------------------------------------------|--------------------------------------------------------------------------------------------------------|-----------------|
| Central Controller      | Raspberry Pi 4 Model B (4 GB RAM)                 | [Raspberry Pi 4 Model B](https://core-electronics.com.au/raspberry-pi-4-model-b-8gb.html)             | 145.00          |
| Image Acquisition       | Raspberry Pi Camera Module v2 (8 MP)              | [Raspberry Pi Camera Board v2](https://core-electronics.com.au/raspberry-pi-camera-board-v2-8-megapixels-38552.html) | 35.65           |
| Environmental Sensors   | BME280 (Temperature & Humidity)                   | [PiicoDev Atmospheric Sensor BME280](https://core-electronics.com.au/piicodev-atmospheric-sensor-bme280.html) | 22.70           |
|                         | BH1750 (Light Intensity)                          | [BH1750 Light Sensor](https://core-electronics.com.au/light-sensor-bh1750.html)                       | 8.90            |
| Storage                 | 32 GB MicroSD Card                                | [Raspberry Pi A2 Class SD Card 32 GB](https://core-electronics.com.au/raspberry-pi-a2-class-sd-card-32gb.html) | 27.50           |
| Wiring                  | 20 cm Jumper Wire Ribbon (F/F, 40 pcs)            | [Female–Female Jumper Wires](https://core-electronics.com.au/solderless-breadboard-jumper-cable-wires-female-female-40-pieces.html) | 3.95            |
|                         | 20 cm Jumper Wire Ribbon (M/F, 40 pcs)            | (as above or equivalent product)                                                                       | –               |
| Sensor Interconnection  | PiicoDev Cable 50 mm                              | [PiicoDev Cable 50 mm](https://core-electronics.com.au/piicodev-cable-50mm.html)                      | 0.90            |
| Power Supply            | Raspberry Pi 4 Official Power Supply (USB‑C 5.1 V, 15.3 W, White) | [Raspberry Pi 4 Power Supply](https://core-electronics.com.au/raspberry-pi-4-official-power-supply-usb-c-5v-15w-white.html) | 11.90           |

**Subtotal:** **AUD 256.50**

This hardware configuration provides sufficient computing capability for on-board data acquisition and preliminary processing, while remaining cost-effective and modular for extension with additional sensors if required.

---

## Phase 2 – Data Transmission, Web-Based Monitoring and System Control

This phase focuses on transmitting the collected environmental and image data from the field-deployed monitoring system to a web-based platform, enabling continuous monitoring of fruit tree growth without the need for manual data retrieval.

The key objectives are to:

- **Enable automatic upload** of sensor data and captured images to a web server.
- **Provide a web-based dashboard** for real-time and historical data visualization.
- **Allow remote configuration** of the image capture interval to support flexible data acquisition strategies.

### 2.1 Data Upload and Storage

The Raspberry Pi will periodically transmit collected data to the web server using standard HTTP-based communication (e.g., RESTful APIs). Environmental sensor data will be stored in a structured database (such as PostgreSQL or MySQL), while image data will be stored as files on the server, with metadata (e.g., timestamp and associated sensor readings) recorded in the database.

Each data record will include:

- Timestamp of acquisition  
- Environmental measurements (temperature, humidity, light intensity)  
- Reference to the corresponding image file (where applicable)  

This design ensures that environmental conditions and visual observations can be linked and retrieved efficiently for subsequent analysis.

---

### 2.2 Web-Based Monitoring Interface

A web-based dashboard will be developed to provide an intuitive interface for researchers and stakeholders. The dashboard will support:

- **Visualization of real-time and historical environmental data** using time-series plots and summary statistics.  
- **Display of the most recent captured image**, providing an up-to-date visual view of the monitored trees.  
- **Access to historical image data**, enabling visual inspection of plant growth and canopy development over time.  

The interface will be designed to be responsive and user-friendly, accessible from both desktop and mobile devices.

---

### 2.3 Configurable Image Capture Interval

To support flexible and experiment-specific data collection, the system will allow the **image capture interval** to be configured remotely through the web interface.

- Configuration parameters (e.g., capture interval in minutes or hours) will be stored on the server.
- The Raspberry Pi will periodically retrieve the latest configuration from the server.
- Upon detecting a configuration change, the Raspberry Pi will update its image capture schedule accordingly, either by:
  - Modifying scheduled tasks (e.g., using `cron`), or  
  - Adjusting the internal timing logic within the acquisition software.

This mechanism ensures that the monitoring strategy can be adapted in real time (for example, increasing image frequency during critical growth stages or under stress conditions) without requiring physical access to the device.

![Example of a web-based agricultural monitoring dashboard](./images/1_reference%20example.png)