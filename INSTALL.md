````markdown
# Intelligent Lighting System Installation Guide

## Environment Requirements

- **macOS**
- **Homebrew** 3.6.0+
- **Docker** 20.10.0+
- **Python** 3.9+

## Dependency Installation

### 1. MQTT Broker (Mosquitto)

```bash
# Install and start service
brew install mosquitto
brew services start mosquitto

# Verify running status (default port 1883)
lsof -i :1883
```

### 2. Time-Series Database (InfluxDB v2)

```bash
# Run via Docker
docker run -d -p 8086:8086 \
  -v influxdb:/var/lib/influxdb2 \
  --name influxdb \
  influxdb:2.7

# Initialize setup (create org/bucket/token)
docker exec -it influxdb influx setup \
  --username admin \
  --password your_secure_password \
  --org my-org \
  --bucket telegraf \
  --token my-super-secret-token \
  --force

or

manully
export INFLUX_TOKEN=<INFLUX_TOKEN>
```

### 3. Data Collector (Telegraf)

```bash
# Install and generate default config
brew install telegraf
telegraf --config config/telegraf.conf

# Edit config file (configure InfluxDB output)
vim config/telegraf.conf
```

### 4. Visualization Platform (Grafana)

```bash
# Run via Docker
docker run -d -p 3000:3000 \
  -v grafana:/var/lib/grafana \
  --name grafana \
  grafana/grafana-enterprise
```

### 5. Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

## Service Integration

### Telegraf → InfluxDB

Configure `telegraf.conf` output plugin:

```ini
[[outputs.influxdb_v2]]
  urls = ["http://localhost:8086"]
  token = "my-super-secret-token"
  organization = "my-org"
  bucket = "telegraf"
```

### Grafana → InfluxDB

1. Access http://localhost:3000
2. Add data source: Select **InfluxDB**
3. Configure parameters:
   - **URL**: http://host.docker.internal:8086
   - **Auth**: Use pre-created token
   - **Organization**: my-org
   - **Bucket**: telegraf

## Service Management Commands

| Service    | Start Command                     | Stop Command                   |
| ---------- | --------------------------------- | ------------------------------ |
| Mosquitto  | `brew services start mosquitto`   | `brew services stop mosquitto` |
| Telegraf   | `telegraf --config telegraf.conf` | `pkill telegraf`               |
| InfluxDB   | `docker start influxdb`           | `docker stop influxdb`         |
| Grafana    | `docker start grafana`            | `docker stop grafana`          |
| Python Env | `source venv/bin/activate`        | `deactivate`                   |

## Verification

```bash
# Check Mosquitto
nc -zv localhost 1883

# Test Telegraf data collection
telegraf --config telegraf.conf --test

# Access InfluxDB UI
open http://localhost:8086

# Access Grafana Dashboard
open http://localhost:3000

# Verify Python dependencies
pip list
```

## Troubleshooting

**Port Conflicts**:

```bash
# Find process using port
lsof -i :1883  # MQTT
lsof -i :8086  # InfluxDB
lsof -i :3000  # Grafana
```

**Docker Logs**:

```bash
docker logs influxdb --tail 100
docker logs grafana --tail 100
```

**Data Write Test**:

```bash
curl -X POST "http://localhost:8086/api/v2/write?org=my-org&bucket=telegraf" \
  --header "Authorization: Token my-super-secret-token" \
  --data-raw "test_metric value=123"
```

**Python Dependency Issues**:

```bash
# Recreate virtual environment
rm -rf venv && python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
````

---

### Key Enhancements:

1. **Python Environment Isolation**: Added dedicated section for virtual environment setup
2. **Dependency Management**: Clear `pip install` instructions with verification step
3. **Unified Service Control**: Includes commands for both system services and Python env
4. **Error Recovery**: Added Python dependency troubleshooting steps
5. **Activation Reminder**: Virtual env activation command in service management table

This template ensures cross-platform consistency while maintaining macOS-specific instructions. All service interactions use standard ports for easier debugging.
