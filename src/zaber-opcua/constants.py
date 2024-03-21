import logging

# The time interval in seconds in which the OPC-UA server refreshes and sends values
OPCUA_REFRESH_TIME = 0.5

# The namespace of the OPC-UA server. Not really necessary but should be set as specification
OPCUA_NAMESPACE = "zaber-opcua"

# The IP address of incoming connections (0.0.0.0 = all IPs)
OPCUA_IP = '0.0.0.0'

# The port of the OPC-UA server
OPCUA_PORT = 4840

# The level for logging
LOG_LEVEL = logging.WARN

# The serial port of the Zaber controller
ZABER_SERIAL_PORT = '/dev/ttyACM0'
