FROM python:3.9-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 安装 plugwise 以及 paho-mqtt
RUN pip install --no-cache-dir \
        git+https://github.com/aequitas/python-plugwise.git \
        paho-mqtt

WORKDIR /app
COPY manully_plugwise_control.py .

CMD ["/bin/bash"]
