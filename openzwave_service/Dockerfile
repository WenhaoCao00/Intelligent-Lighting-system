###########################
# -------- build -------- #
###########################
FROM python:3.8-slim AS builder

# —— 构建依赖 —— #
RUN apt-get update && apt-get install -y --no-install-recommends \
        git build-essential libudev-dev libusb-1.0-0-dev libyaml-dev \
        cython3 python3-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "Cython>=0.29" six --no-cache-dir

# —— Build OpenZWave v1.4 —— #
WORKDIR /opt
RUN git clone --depth 1 -b v1.4 https://github.com/OpenZWave/open-zwave.git \
 && cd open-zwave \
 && sed -i 's/-Werror//g' Makefile cpp/build/support.mk cpp/build/Makefile \
 && make -j"$(nproc)" \
 && make install \
 && ldconfig                # 把 libopenzwave.so* 写入 linker cache

# —— Build python-openzwave v0.4.19 —— #
RUN git clone https://github.com/OpenZWave/python-openzwave.git /opt/python-openzwave \
 && cd /opt/python-openzwave \
 && git checkout v0.4.19 \
 && sed -i 's|git://github.com/|https://github.com/|g' Makefile \
 && sed -i 's/Cython==0.28.6/Cython>=0.29/' pyozw_setup.py \
 && python3 setup.py build --flavor=shared \
 && pip install . --no-cache-dir

###########################
# -------- run ---------- #
###########################
FROM python:3.8-slim

# —— 仅安装运行期必需库 —— #
RUN apt-get update && apt-get install -y --no-install-recommends \
        libudev1 libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# —— 把构建产物拷过来 —— #
# 1. 复制 /usr/local（只含 openzwave 相关 .so 和 site-packages）
COPY --from=builder /usr/local /usr/local

# 2. 复制 OpenZWave 配置目录
COPY --from=builder /opt/open-zwave/config /app/config

# —— 软链兼容 libopenzwave.so.1.4 ←→ 1.6 —— #
RUN set -e; \
    for d in /usr/local/lib /usr/local/lib64; do \
        [ -f "$d/libopenzwave.so.1.6" ] && \
        ln -sf "$d/libopenzwave.so.1.6" "$d/libopenzwave.so.1.4" || true; \
    done && ldconfig

# —— 业务依赖 & 代码 —— #
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt --no-cache-dir
COPY output_data.py /app/output_data.py

WORKDIR /app
ENV LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib64:$LD_LIBRARY_PATH

CMD ["python3", "output_data.py"]
