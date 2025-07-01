# Intelligent‑Lighting Control Stack

A **Docker Compose** bundle that fuses real‑time sensing, automated planning and rich dashboards.

- **Mosquitto** – MQTT backbone for inter‑service messages
- **OpenZWave** – REST gateway exposing your Z‑Wave network
- **Plugwise** – Helper that drives Plugwise smart plugs & reports power draw
- **InfluxDB 2.3 + Grafana 9.0** – Time‑series storage & visualisation
- **Planner** – Polls InfluxDB for lux values, builds PDDL problems, runs **Fast Downward** and publishes lighting actions

All containers share the same **monitoring** network, so they reach each other by service name (e.g. `mosquitto`, `influxdb`).

---

## Prerequisites

| Requirement        | Version ≥ | Notes                                                                        |
| ------------------ | --------- | ---------------------------------------------------------------------------- |
| **Docker Engine**  | 20.x      | [https://docs.docker.com/engine/](https://docs.docker.com/engine/)           |
| **docker compose** | 1.29      | v2 plugin also fine                                                          |
| **Hardware**       | –         | • Z‑Wave USB stick → **/dev/ttyACM0**• Plugwise USB stick → **/dev/ttyUSB0** |

> **Linux:** add your user to the serial group (e.g. `dialout`).\
> **WSL 2:** enable [USBIPD‑win](https://github.com/dorssel/usbipd-win) and attach devices.

---

## USB device passthrough on WSL 2

If you run the stack inside **WSL Ubuntu** you have to attach your USB sticks (Z‑Wave / Plugwise) from Windows to the WSL2 VM. Steps:

```powershell
# 1. List all Windows USB devices (admin PowerShell)
usbipd list

# 2. Share the device you want (replace <busid>)
usbipd bind --busid <busid>

# 3. Attach the shared device to the current WSL distro
usbipd attach --wsl --busid <busid>
```

Inside your WSL shell you can now verify:

```bash
lsusb        # the device should appear
```

When finished, detach (or unplug) the device from Windows:

```powershell
usbipd detach --busid <busid>
```

> As long as the device is attached to WSL it is **not** available to Windows.

---

## Quick start

```bash
# 1 — clone & enter
git clone https://github.com/WenhaoCao00/Intelligent-Lighting-system.git
cd Intelligent-Lighting-system

# 2 — build custom images (openzwave, plugwise, planner)
docker compose build

# 3 — bring the stack up
docker compose up -d
```

After a few seconds all services should be healthy.

### Exposed ports / default credentials

| Service           | URL                                            | Login                                      |
| ----------------- | ---------------------------------------------- | ------------------------------------------ |
| **Grafana**       | [http://localhost:3000](http://localhost:3000) | `admin / admin` (change on 1st login)      |
| **InfluxDB**      | [http://localhost:8086](http://localhost:8086) | Create **Org/Bucket/Token** on first visit |
| **Mosquitto**     | MQTT TCP `1883`                                | –                                          |
|                   | WebSocket `9001`                               | –                                          |
| **OpenZWave API** | [http://localhost:5000](http://localhost:5000) | Swagger docs at `/`                        |

Planner has no exposed port – check its logs for action decisions.

---

## Service catalogue

| Name          | Image / Build           | Purpose                                                                                                   |
| ------------- | ----------------------- | --------------------------------------------------------------------------------------------------------- |
| **mosquitto** | `eclipse-mosquitto:2.0` | MQTT broker                                                                                               |
| **influxdb**  | `influxdb:2.3.0`        | Time‑series store                                                                                         |
| **telegraf**  | `telegraf:1.30`         | Subscribes to MQTT, writes to InfluxDB                                                                    |
| **grafana**   | `grafana/grafana:9.0.4` | Dashboards                                                                                                |
| **openzwave** | `./openzwave_service`   | Publishes Z‑Wave state / control                                                                          |
| **plugwise**  | `./plugwise_service`    | Controls Plugwise smart plugs                                                                             |
| **planner**   | `./planner`             | Reads lux from InfluxDB → generates PDDL → runs Fast Downward → publishes `lighting/action` MQTT messages |

> **mqtt-listener** exists only for ad‑hoc testing and is _not_ required in production.

---

## Usage snippets

### 1 — Verify serial devices inside containers

```bash
docker compose exec openzwave ls -l /dev/ttyACM0
docker compose exec plugwise  ls -l /dev/ttyUSB0
```

### 2 — Monitor planner output

```bash
docker compose logs -f planner
```

You should see lines like `我准备开灯` when lux < 100 lx.

### 3 — Publish a fake lux reading (for quick test)

```bash
mosquitto_pub -h localhost -t zwave/sensor_data -m '{"luminance":85}'
```

Planner will detect darkness and generate a **turn‑on** action.

---

## Customisation

| Need                            | How                                                                                             |
| ------------------------------- | ----------------------------------------------------------------------------------------------- |
| Persist InfluxDB / Grafana data | Bind‑mount host directories or named volumes (already defined: `influxdb-data`, `grafana-data`) |
| Change serial paths             | Edit `devices:` lines in `docker-compose.yml`                                                   |
| Adjust lux threshold            | Adapt logic in `planner/influx_utils.py` and PDDL generation                                    |
| Upgrade images                  | `docker compose pull` or rebuild custom services                                                |

---

## Shutdown & cleanup

```bash
# Stop containers, keep volumes
docker compose down

# Remove volumes as well
docker compose down -v
```

---

## License

Released under the **MIT License** – see [`LICENSE`](LICENSE) for details.
