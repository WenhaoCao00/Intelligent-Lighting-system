# Home‑Automation Monitoring Stack

A **Docker Compose** stack combining:

- **Mosquitto** – lightweight MQTT broker
- **OpenZWave** REST API – exposes your Z‑Wave network over HTTP
- **Plugwise** service – Python helper to control Plugwise smart plugs
- **InfluxDB 2.3 + Grafana 9.0** – time‑series storage & dashboards

All containers share a single **monitoring** network, so they can discover each other by service‑name.

---

## Prerequisites

| Requirement                       | Version ≥ | Notes                                                                            |
| --------------------------------- | --------- | -------------------------------------------------------------------------------- |
| **Docker Engine**                 | 20.x      | <https://docs.docker.com/engine/>                                                |
| **docker‑compose** (v1 or Plugin) | 1.29      | <https://docs.docker.com/compose/>                                               |
| **Hardware**                      | –         | • Z‑Wave USB stick → **/dev/ttyACM0**<br>• Plugwise USB stick → **/dev/ttyUSB0** |

> **Linux:** add your user to the `dialout` (or similar) group to access the serial devices.  
> **WSL 2:** enable [USBIPD‑win](https://github.com/dorssel/usbipd-win) and attach the devices to the distro.

---

## Project layout

```text
.
├── docker-compose.yml
├── openzwave_service/
│   └── Dockerfile
├── plugwise_service/
│   ├── Dockerfile
│   └── manully_plugwise_control.py
├── mqtt_listener_service/
│   ├── Dockerfile
│   └── mqtt_listener.py
└── README.md   ← you are here
```

---

## Quick start

```bash
# 1 — clone & enter
git clone https://github.com/WenhaoCao00/Intelligent-Lighting-system.git Intelligent-Lighting-system
cd Intelligent-Lighting-system

# 2 — build and launch the whole stack
docker-compose up --build -d

# 3 — wait a few seconds until all services are healthy
```

### Exposed ports / credentials

| Service           | URL                                                         | Default login                                  |
| ----------------- | ----------------------------------------------------------- | ---------------------------------------------- |
| **Grafana**       | <http://localhost:3000>                                     | `admin / admin` (change on first login)        |
| **InfluxDB UI**   | <http://localhost:8086>                                     | Create **Org / Bucket / Token** on first visit |
| **Mosquitto**     | `mqtt://localhost:1883` (TCP)<br>`ws://localhost:9001` (WS) | –                                              |
| **OpenZWave API** | <http://localhost:5000>                                     | Swagger docs at `/`                            |

---

## Usage snippets

### 1 — Check serial mapping

```bash
docker-compose exec openzwave ls -l /dev/ttyACM0   # Z‑Wave stick
docker-compose exec plugwise  ls -l /dev/ttyUSB0   # Plugwise stick
```

### 2 — Toggle a Plugwise Circle manually

```bash
docker-compose exec plugwise bash
python manully_plugwise_control.py
```

The script:

1. Syncs the Circle / Circle+ clock
2. Reads current relay state
3. Flips the relay

### 3 — Subscribe to Z‑Wave sensor data

The `mqtt_listener_service` container runs Mosquitto **and** a Python subscriber that prints every message on `zwave/sensor_data`.

Publish from anywhere:

```bash
mosquitto_pub -h localhost -t zwave/sensor_data -m '{"hello":"world"}'
```

---

## Customisation

| Need                                | How                                                                                                                                                       |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Persist InfluxDB / Grafana data** | Mount host volumes:<br>`influxdb:`<br>&nbsp;&nbsp;`- ./data/influxdb:/var/lib/influxdb2`<br>`grafana:`<br>&nbsp;&nbsp;`- ./data/grafana:/var/lib/grafana` |
| **Change serial paths**             | Edit `devices:` lines in `docker-compose.yml`                                                                                                             |
| **Expose extra MQTT ports**         | Add more `ports:` mappings under **mosquitto**                                                                                                            |
| **Upgrade images**                  | `docker-compose pull` or modify a **Dockerfile**, then `docker-compose up --build`                                                                        |

---

## Shutdown & cleanup

```bash
# Stop & remove containers (volumes intact)
docker-compose down

# …or nuke everything including volumes
docker-compose down -v
```

---

## License

Released under the **MIT License** – see [`LICENSE`](LICENSE) for details.
