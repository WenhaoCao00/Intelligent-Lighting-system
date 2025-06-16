# image
FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libudev-dev \
    libudev1 \
    libusb-1.0-0-dev \
    libyaml-dev \
    cython3 \
    python3-dev \
    python3-pip \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "Cython>=0.29" six --no-cache-dir
# Build OpenZWave v1.4
WORKDIR /opt
RUN git clone https://github.com/OpenZWave/open-zwave.git -b v1.4 \
    && cd open-zwave \
    && sed -i 's/-Werror//g' Makefile cpp/build/support.mk cpp/build/Makefile \
    && make -j4 \
    && make install \
    && ldconfig

# Build python-openzwave v0.4.19
WORKDIR /opt
RUN git clone https://github.com/OpenZWave/python-openzwave.git \
    && cd python-openzwave \
    && git checkout v0.4.19 \
    && sed -i 's|git://github.com/|https://github.com/|g' Makefile \
    && sed -i 's/Cython==0.28.6/Cython>=0.29/' pyozw_setup.py

WORKDIR /opt/python-openzwave
RUN python3 setup.py build --flavor=shared \
    && python3 -m pip install . --no-cache-dir

# install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# copy open-zwave config to running python code
RUN mkdir -p /app/config && cp -r /opt/open-zwave/config/* /app/config/

# copy entry code
COPY output_data.py /app/output_data.py
WORKDIR /app

ENV LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib64:$LD_LIBRARY_PATH
# start up order
CMD ["python3", "output_data.py"]
