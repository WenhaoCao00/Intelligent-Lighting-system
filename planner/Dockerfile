###########################
# -------- build -------- #
###########################
FROM python:3.10-slim AS builder

# --- system build tools (removed later) ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git build-essential cmake python3-dev \
        curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# --- clone and compile Fast Downward (shallow clone) ---
WORKDIR /opt
RUN git clone --depth 1 https://github.com/aibasel/downward.git \
 && cd downward \
 && python3 build.py


###########################
# -------- run ---------- #
###########################
FROM python:3.10-slim

# --- copy compiled Fast Downward only ---
COPY --from=builder /opt/downward/fast-downward.py /usr/local/bin/fast-downward
COPY --from=builder /opt/downward/builds /opt/downward/builds
# optional: strip symbols to shrink a few extra MB
RUN find /opt/downward/builds -type f -executable -exec strip --strip-unneeded {} + || true

# --- copy your planner project code ---
WORKDIR /app
COPY . .

# --- Python dependencies ---
RUN pip install --no-cache-dir -r requirements.txt

# --- env var + entrypoint ---
ENV PLANNER=/usr/local/bin/fast-downward
CMD ["python", "planner_main.py"]