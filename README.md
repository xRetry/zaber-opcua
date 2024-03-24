# Description

This program creates an OPC-UA server, acting as middleware between a Zaber controller and OPC-UA clients.
It is build for the setup, where two axis are placed in parallel and move together, while third axis is mounted perpendicular and can move independently.

# Usage

Install Python 3.9 with `pip` (higher versions may work as well)

1. Clone this repository

```sh
git clone https://github.com/xRetry/zaber-opcua
```

2. Install the required Python packages 

```sh
pip install -r requirements.txt
```

3. Connect the Zaber controller. 

4. Adjust the settings in `src/zaber-opcua/settings.py`. Alternatively, this can be done via environment variables.

5. Make sure the user has read/write access to the device

```sh
sudo chmod a+rw /dev/<device>
```

6. Start the OPC-UA server

```sh
python src/zaber-opcua/main.py
```

7. Use any OPC-UA client to interact with the server (e.g. [UaExpert](https://www.unified-automation.com/products/development-tools/uaexpert.html))

