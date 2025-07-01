from influxdb_client import InfluxDBClient
import os

def get_current_luminance():
    url     = os.environ["INFLUX_URL"]
    token   = os.environ["INFLUX_TOKEN"]
    org     = os.environ["INFLUX_ORG"]
    bucket  = "zwave"                    

    flux_query = f'''
    from(bucket: "{bucket}")
      |> range(start: -5s)                              
      |> filter(fn: (r) =>
          r._measurement == "sensor_data" and
          r._field == "luminance" and
          r.topic == "zwave/sensor_data"
      )
      |> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
      |> last()                                        
    '''

    with InfluxDBClient(url=url, token=token, org=org) as client:
        tables = client.query_api().query(org=org, query=flux_query)
        for table in tables:
            for record in table.records:
                return float(record.get_value())

    # if no data,return None
    return None


def get_current_ultraviolet():
    url     = os.environ["INFLUX_URL"]
    token   = os.environ["INFLUX_TOKEN"]
    org     = os.environ["INFLUX_ORG"]
    bucket  = "zwave"                    

    flux_query = f'''
    from(bucket: "{bucket}")
      |> range(start: -5s)                              
      |> filter(fn: (r) =>
          r._measurement == "sensor_data" and
          r._field == "ultraviolet" and
          r.topic == "zwave/sensor_data"
      )
      |> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
      |> last()                                        
    '''

    with InfluxDBClient(url=url, token=token, org=org) as client:
        tables = client.query_api().query(org=org, query=flux_query)
        for table in tables:
            for record in table.records:
                return float(record.get_value())

    # if no data,return None
    return None

