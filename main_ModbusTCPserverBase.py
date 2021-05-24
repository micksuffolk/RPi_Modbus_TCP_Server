import netifaces
from threading import Thread
from socketserver import TCPServer
from collections import defaultdict
from umodbus import conf
from umodbus.server.tcp import RequestHandler, get_server
from datetime import datetime
from random import uniform



######################################################################################################################
# This is a 'blank' Modbus TCP server (Slave), which can be configured as required & read by a Modbus client (Master)



######################################################################################################################
# Create Modbus data tables...
data_store_hr = defaultdict(int)  # Holding Register Table (4xxxxx)
data_store_ir = defaultdict(int)  # Input Register Table (3xxxxx)

# Enable signed integers (default is False)...
conf.SIGNED_VALUES = True

# Setup server (Modbus Slave) IP address & port number where clients (Modbus Master) can access the data...
# Ethernet IP... (Activate as necessary)
#ip_address = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
#print('IP Address of eth0 =', ip_address)

# Wireless IP... (Activate as necessary)
ip_address = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
print('IP Address of wlan0 =', ip_address)

# Use one of the discovered IP addresses above for the Modbus Server...
# (Note, to use port 502, or any port number below 1024, the python script must be run with high
# privilege level, i.e. run the script with a 'sudo' command, port numbers above 1024 don't need this.)
TCPServer.allow_reuse_address = True
app = get_server(TCPServer, (ip_address, 7777), RequestHandler)
#app = get_server(TCPServer, (ip_address, 502), RequestHandler) # Needs high privilege level for port 502



######################################################################################################################
# Read the Holding Register Data Store (4xxxxx)...
@app.route(slave_ids=[1], function_codes=[3], addresses=list(range(0, 99999)))
def read_data_store(slave_id, function_code, address):
    """" Return value of address. """
    return data_store_hr[address]



######################################################################################################################
# Read the Input Register Data Store (3xxxxx)...
@app.route(slave_ids=[1], function_codes=[4], addresses=list(range(0, 99999)))
def read_data_store(slave_id, function_code, address):
    """" Return value of address. """
    return data_store_ir[address]



######################################################################################################################
# Write to the Holding register data store (single or multiple register write)...
@app.route(slave_ids=[1], function_codes=[6, 16], addresses=list(range(0, 99999)))
def write_data_store(slave_id, function_code, address, value):
    """" Set value for address. """
    data_store_hr[address] = value



######################################################################################################################
# Initialize/Startup (This block will test the excepted error to occur)...
# Nothing of note to go here yet, variables are initialised at the top of the code instead...
try:
    print("Code Initializing...")



######################################################################################################################
# The try section has failed (handle the error)...
except:
    print('Something went wrong with Try block...')
    app.shutdown()
    app.server_close()
    exit()



######################################################################################################################
# The try section has been successful (If there is no exception then this block will be executed)...
else:
    print('Code Running...')



    #####################################################################################################
    ####### Run Modbus server thread, must only be called once to start, very important!!!!!!!... #######
    #####################################################################################################
    Thread_Modbus_Server = Thread(target=app.serve_forever)
    Thread_Modbus_Server.start()
    print('Modbus.app.serve_forever...')



    # Main Program Loop...
    while True:

        ########################################################
        ####### Read the system date and time from Pi... #######
        ########################################################
        datetimenow = datetime.now()



        ###########################################################
        ####### Modbus Holding Register Mapping (4xxxxx)... #######
        ###########################################################

        # Example Modbus Command registers (written to by the Modbus Client/Master)
        if data_store_hr[0] != 0:
            Modbus_ControlCommandWord1 = data_store_hr[0]
            data_store_hr[0] = 0

        if data_store_hr[1] != 0:
            Modbus_ControlCommandWord2 = data_store_hr[1]
            data_store_hr[1] = 0

        if data_store_hr[2] != 0:
            Modbus_ControlCommandWord3 = data_store_hr[2]
            data_store_hr[2] = 0

        if data_store_hr[3] != 0:
            Modbus_ControlCommandWord4 = data_store_hr[3]
            data_store_hr[3] = 0

        if data_store_hr[4] != 0:
            Modbus_ControlDataWord1 = data_store_hr[4]
            data_store_hr[4] = 0

        if data_store_hr[5] != 0:
            Modbus_ControlDataWord2 = data_store_hr[5]
            data_store_hr[5] = 0

        if data_store_hr[6] != 0:
            Modbus_ControlDataWord3 = data_store_hr[6]
            data_store_hr[6] = 0

        if data_store_hr[7] != 0:
            Modbus_ControlDataWord4 = data_store_hr[7]
            data_store_hr[7] = 0

        # Example Modbus Status registers (read by the Modbus Client/Master)
        data_store_hr[100] = int(datetimenow.hour)
        data_store_hr[101] = int(datetimenow.minute)
        data_store_hr[102] = int(datetimenow.second)
        data_store_hr[103] = int(datetimenow.microsecond/1000)
        data_store_hr[104] = int(datetimenow.year)
        data_store_hr[105] = int(datetimenow.month)
        data_store_hr[106] = int(datetimenow.day)
        data_store_hr[107] = int(uniform(-32768, 32767)) # random number generator



        #########################################################
        ####### Modbus Input Register Mapping (3xxxxx)... #######
        #########################################################
        data_store_ir[0] = 1
        data_store_ir[1] = 2
        data_store_ir[2] = 3
        data_store_ir[3] = 4
        data_store_ir[4] = int(uniform(0, 10)) # random number generator



######################################################################################################################
# Finally block always gets executed either exception is generated or not...
finally:

    app.shutdown()
    print('Modbus.app.shutdown...')

    app.server_close()
    print('Modbus.app.server_close...')

    Thread_Modbus_Server.join()
    print('Modbus Server Thread closed...')

    print('Code Stopped...')
    exit()


