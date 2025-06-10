# OpenZWave v1.4 + Python-OpenZWave 0.4.19 Installation Guide

A step-by-step guide for installing OpenZWave v1.4 and Python-OpenZWave 0.4.19 in a Python virtual environment (`venv`). Tested on Ubuntu / WSL.

---

## Directory Structure

```bash
~/desktop/Intelligent-Lighting-system/
├── open-zwave/          # OpenZWave v1.4
└── python-openzwave/    # Python-OpenZWave 0.4.19
```

# Install System Dependencies

```bash
sudo apt update
sudo apt install -y build-essential git cmake g++ pkg-config \
    libudev-dev libudev1 cython3 python3-dev python3-pip python3-venv
```

# Setup Python venv

```bash
cd ~/desktop/Intelligent-Lighting-system
python3 -m venv venv
source venv/bin/activate
```

# Build OpenZWave v1.4

```bash
git clone https://github.com/OpenZWave/open-zwave.git -b v1.4
cd open-zwave
make -j4
sudo make install
sudo ldconfig

nano cpp/build/Makefile
Remove or comment out -Werror
```

# Build Python-OpenZWave

```bash
cd ~/desktop/Intelligent-Lighting-system
git clone https://github.com/OpenZWave/python-openzwave.git
cd python-openzwave
sed -i 's/Cython==0.28.6/Cython>=0.29/' pyozw_setup.py
pip install six
./setup.py build --flavor=shared
./setup.py install --user --flavor=shared
```

# Configure Python Code

```bash
config_path = "/home/your_username/desktop/Intelligent-Lighting-system/open-zwave/config"
device_name = "/dev/ttyUSB0"  # or /dev/ttyACM0
```
