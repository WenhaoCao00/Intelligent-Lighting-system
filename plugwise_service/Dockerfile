FROM python:3.9-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# install plugwise and paho-mqtt
RUN pip install --no-cache-dir \
        git+https://github.com/aequitas/python-plugwise.git \
        paho-mqtt

WORKDIR /app
COPY on_and_off_MQTT.py .

#CMD ["/bin/bash"]
CMD ["python", "on_and_off_MQTT.py"]
