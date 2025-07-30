from influxdb_client import InfluxDBClient
import os

def get_current_luminance():
    url     = os.environ["INFLUX_URL"]
    token   = os.environ["INFLUX_TOKEN"]
    org     = os.environ["INFLUX_ORG"]
    bucket  = "zwave"

    flux_query = f'''
    from(bucket: "{bucket}")
      |> range(start: -2h)
      |> filter(fn: (r) =>
          r._measurement == "sensor_data" and
          r._field == "luminance" and
          r.topic == "zwave/sensor_data"
      )
      |> aggregateWindow(every: 10s, fn: mean, createEmpty: false)
      |> last()
    '''

    with InfluxDBClient(url=url, token=token, org=org) as client:
        tables = client.query_api().query(org=org, query=flux_query)
        for table in tables:
            for record in table.records:
                print(">>> Got record:", record)
                return float(record.get_value())

    print(">>> No luminance data found.")
    return None


def get_current_ultraviolet():
    url     = os.environ["INFLUX_URL"]
    token   = os.environ["INFLUX_TOKEN"]
    org     = os.environ["INFLUX_ORG"]
    bucket  = "zwave"                    

    flux_query = f'''
    from(bucket: "{bucket}")
        |> range(start: -2h)                           // last 2 hours
        |> filter(fn: (r) =>
            r._measurement == "sensor_data" and        // measurement
            r._field == "ultraviolet" and                // field
            r.topic == "zwave/sensor_data"             // MQTT topic
        )
        |> aggregateWindow(every: 10s, fn: mean, createEmpty: false)   // 10-s average
        |> last()
                                  
    '''

    with InfluxDBClient(url=url, token=token, org=org) as client:
        tables = client.query_api().query(org=org, query=flux_query)
        for table in tables:
            for record in table.records:
                return float(record.get_value())

    # if no data,return None
    return None



###############################plugwise###########
def _get_current_power(topic: str,
                       bucket: str = "zwave",
                       measurement: str = "plugwise_power",
                       field: str = "power",
                       window: str = "-15s") -> float | None:

    url   = os.environ["INFLUX_URL"]
    token = os.environ["INFLUX_TOKEN"]
    org   = os.environ["INFLUX_ORG"]

    flux_query = f'''
    from(bucket: "{bucket}")
      |> range(start: {window})
      |> filter(fn: (r) =>
          r._measurement == "{measurement}" and
          r._field       == "{field}"       and
          r.topic        == "{topic}"
      )
      |> last()
    '''

    with InfluxDBClient(url=url, token=token, org=org) as client:
        tables = client.query_api().query(org=org, query=flux_query)
        for table in tables:
            for record in table.records:
                return float(record.get_value())

    return None


# Plugwsie 1：Circle+ ───────────────────────────────────────
def get_power_circle_plus() -> float | None:
    return _get_current_power(topic="plugwise/status/plus")


# Plugwise 2：Circle ───────────────────────────────────────
def get_power_circle() -> float | None:
    return _get_current_power(topic="plugwise/status/circle")