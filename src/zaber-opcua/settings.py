import logging
import os

# The time interval in seconds in which the OPC-UA server refreshes and sends values
OPCUA_REFRESH_TIME = float(os.environ.get('OPCUA_REFRESH_TIME', 0.1))

# The namespace of the OPC-UA server. Not really necessary but should be set as specification
OPCUA_NAMESPACE = os.environ.get('OPCUA_NAMESPACE', 'zaber-opcua')

# The IP address of incoming connections (0.0.0.0 = all IPs)
OPCUA_IP = os.environ.get('OPCUA_IP', '0.0.0.0')

# The port of the OPC-UA server
OPCUA_PORT = os.environ.get('OPCUA_PORT', 4840)

# The level for logging
OPCUA_LOG_LEVEL = logging.WARN
level = os.environ.get('OPCUA_LOG_LEVEL')
if level is not None:
    level = level.upper()
    if level == 'ERROR':
        OPCUA_LOG_LEVEL = logging.ERROR
    elif level == 'DEBUG':
        OPCUA_LOG_LEVEL = logging.DEBUG
    elif level == 'INFO':
        OPCUA_LOG_LEVEL = logging.INFO
    elif level == 'FATAL':
        OPCUA_LOG_LEVEL = logging.FATAL

# The serial port of the Zaber controller
ZABER_SERIAL_PORT = os.environ.get('ZABER_SERIAL_PORT', '/dev/ttyUSB0')

# The time to wait before trying to reconnect to the zaber controller
ZABER_RECONNECT_TIMEOUT = 10

