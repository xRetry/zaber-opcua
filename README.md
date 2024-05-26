# Description

This project deploys an OPC-UA server for controlling the slide axes connected to a Zaber controller.
The server acts as middleware, translating messages from OPC-UA clients to the Zaber specific communication protocol.
It provides methods for controlling the axes and publishes measurement values.

## Hardware

The machine contains three axes: Two are placed in parallel and move together, while third is mounted perpendicular and can move independently.
The step motors for the parallel axes are connected a Zaber control unit, which is daisy-chained to a second control unit with the independent axis.
One control unit is further connected to a Raspberry Pi via USB, which is executing the OPC-UA server.

<img src="axis_diag.png" width="500" />

## Software

The OPC-UA server is written in Python and runs on a Raspberry Pi.

### Raspberry Pi

The Raspberry Pi is running Raspberry Pi OS Lite.
Its static IP address is `193.171.191.15`.
To connect via SSH, run:

```sh
ssh root@193.171.191.15
```

The source code for the OPC-UA server can be found in the directory `/zaber-opcua`.
The configuration of the server is done using environment variables.
The script `/run_zaber_opcua.sh` sets all environment variables and starts the server.

The OPC-UA server automatically restarts after reboots.

### OPC-UA Server

An OPC-UA server provides endpoints for other clients to connect to.
The endpoints are structured in a nested node tree.

The server provides two nodes:
- Parallel Slide
- Cross Slide

Each node contains the following methods to control the corresponding axis:
- `move_absolute`: Moves to the absolute position
- `move_relative`: Moves relative to the current position
- `move_velocity`: Moves the axis with the provided velocity
- `stop`: Stops the movement of the axis

Additionally, the following values are published for each node:
- `status`: An error description, or `Ok`
- `position`: The position of the slide
- `busy`: `true` if the axis is moving, else `false`

A further node called `Recording Trigger` is provided with the boolean value `recording`.
It is used to start and stop data recording in ibaPDA.
To change its value, a mouse needs to be connected to the Raspberry Pi.
By pressing any mouse button, the signal is toggled between `true` and `false`.

# Setup

## Device Access

The user running the OPC-UA server needs to have read/write access to the device file of the Zaber controller.

To find the correct device:

1. Disconnect the Zaber controller

2. Run `ls /dev`

3. Connect the Zaber controller

4. Run `ls /dev` again and check which device is new

Then, run the following command to grant read/write access to all users:

```sh
chmod a+rw /dev/<device>
```

## OPC-UA Server

1. Install the dependencies:

```sh
apt-get update && apt-get install -y git python3.9 xorg openbox xserver-xorg-video-dummy
```

2. Clone this repository to the directory `/zaber-opcua`

```sh
git clone https://github.com/xRetry/zaber-opcua /zaber-opcua
```

3. Enable headless mode for X11

```sh
cp /zaber-opcua/10-headless.conf /etc/X11/xorg.conf.d/
```

4. Install the required Python packages 

```sh
pip install -r /zaber-opcua/requirements.txt
```

5. Create a shell script, which sets the environment variables and starts the server

```sh
cat > /run_zaber_opcua.sh << EOF
#!/bin/sh
export ZABER_SERIAL_PORT=/dev/ttyACM0
export OPCUA_REFRESH_RATE=0.1
export OPCUA_LOG_LEVEL=ERROR

startx &
python /zaber-opcua/src/zaber-opcua/main.py
EOF
```

6. Copy the service file to the correct location
```sh
cp /zaber-opcua/zaber-opcua.service /etc/systemd/system/
```

7. Start and enable the service

```sh
systemctl daemon-reload && systemctl start zaber-opcua.service && sudo systemctl enable zaber-opcua.service
```

After this, the following command should show, that the service is running:

```sh
systemctl status zaber-opcua.service
```

To be sure, try to connect to the server using an OPC-UA client of your choice (e.g. [UaExpert](https://www.unified-automation.com/products/development-tools/uaexpert.html)).

