import logging

# The time interval in seconds in which the OPC-UA server refreshes and sends values
OPCUA_REFRESH_TIME = 0.5

# The namespace of the OPC-UA server. Not really necessary but should be set as specification
OPCUA_NAMESPACE = "localhost"

# The port of the OPC-UA server
OPCUA_PORT = 4840

# The level for logging
LOG_LEVEL = logging.INFO
