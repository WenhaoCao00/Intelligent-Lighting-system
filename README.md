# Home‑Automation Monitoring Stack

A Docker Compose stack that bundles Plugwise smart‑plug control, an OpenZWave REST API, and a lightweight monitoring suite (InfluxDB 2.3 + Grafana 9.0).

---

## Prerequisites

| Requirement | Notes |
| ----------- | ----- |
|             |       |

| **Docker Engine 20+**                             | [https://docs.docker.com/engine/](https://docs.docker.com/engine/)                             |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **docker‑compose v1.29+ (or the Compose Plugin)** | [https://docs.docker.com/compose/](https://docs.docker.com/compose/)                           |
| **Hardware**                                      | • Z‑Wave USB stick exposed as **/dev/ttyACM0**• Plugwise USB stick exposed as **/dev/ttyUSB0** |

> 🛡️ **Linux:** be sure your user has read/write access to the serial devices (usually by adding the user to the `dialout` group).**Windows WSL 2:** enable [USBIPD‑win](https://github.com/dorssel/usbipd-win) and attach the devices to the distro.

---

## Project structure

```text
.
├── docker-compose.yml          # Service definitions
├── openzwave_service/          # OpenZWave REST image
│   └── Dockerfile
├── plugwise_service/           # Plugwise control image
│   ├── Dockerfile
│   └── manully_plugwise_control.py
└── README.md                   # This file
```

---

## Quick start

```bash
# 1. Clone the repo
git clone <your-repo-url> home-automation-stack && cd home-automation-stack

# 2. Build and start all services in the background
docker-compose up --build -d

# 3. Wait a few seconds for the containers to become healthy
```

### Port overview

| Service           | URL                                            | Default credentials                                  |
| ----------------- | ---------------------------------------------- | ---------------------------------------------------- |
| **Grafana**       | [http://localhost:3000](http://localhost:3000) | `admin / admin` (you will be asked to change it)     |
| **InfluxDB UI**   | [http://localhost:8086](http://localhost:8086) | Create Organisation, Bucket and Token on first visit |
| **OpenZWave API** | [http://localhost:5000](http://localhost:5000) | Swagger docs are available at the root path          |

---

## Usage examples

### 1. Verify that the serial devices are mapped

```bash
# Z‑Wave
docker-compose exec openzwave ls -l /dev/ttyACM0

# Plugwise
docker-compose exec plugwise ls -l /dev/ttyUSB0
```

### 2. Manually toggle a Plugwise Circle

```bash
# Open an interactive shell in the container
docker-compose exec plugwise bash

# Run the control script (toggles relay on/off)
python manully_plugwise_control.py
```

The script will:

1. Synchronise the Circle / Circle+ clock to the container time
2. Read the current relay state
3. Flip the state (on → off / off → on)

### 3. Import dashboards into Grafana

1. Log in to Grafana → **Connections → Data sources** → add **InfluxDB** with URL `http://influxdb:8086`, your Org and Token.
2. Go to **Dashboards → New → Import**, paste a JSON model or upload a file to visualise Z‑Wave sensors, Plugwise power usage, etc.

---

## Customisation

| Need                    | How                                                                                                                                 |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Persist data**        | Add `volumes:` to the `influxdb` and `grafana` services:` - ./data/influxdb:/var/lib/influxdb2``- ./data/grafana:/var/lib/grafana ` |
| **Change serial paths** | Replace `/dev/ttyACM0` and `/dev/ttyUSB0` in `devices:` with your actual paths                                                      |
| **Upgrade images**      | `docker-compose pull` or modify a `Dockerfile`, then `docker-compose up --build`                                                    |

---

## Shutdown & cleanup

```bash
# Stop and remove containers, keep volumes
docker-compose down

# Remove volumes as well
docker-compose down -v
```

---

## License

Released under the **MIT License**. See `LICENSE` for details.
