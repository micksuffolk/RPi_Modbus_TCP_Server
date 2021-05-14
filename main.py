import threading
import netifaces
from threading import Thread
from socketserver import TCPServer
from collections import defaultdict
from umodbus import conf
from umodbus.server.tcp import RequestHandler, get_server
from datetime import datetime
from random import uniform
from gpiozero import LED



######################################################################################################################
# Initialize some variables...
Program_Counter = int(0)
Program_Status_Code = int(1)
Modbus_Heartbeat_Counter = int(0)
Modbus_Heartbeat_Counter_Limit = int(200)
Modbus_Comms_Timeout = bool(False)
Scan_Pulse = bool(False)
Status_LED_Function_run = bool(False)
event = threading.Event()



######################################################################################################################
# Create Modbus data tables...
data_store_hr = defaultdict(int)  # Holding Register Table (4xxxxx)
data_store_ir = defaultdict(int)  # Input Register Table (3xxxxx)

# Enable signed integers (default is False)...
conf.SIGNED_VALUES = True

# Setup server IP address & port number where clients can access the data...
# Ethernet IP...
#ip_address = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
#print('IP Address of eth0 =', ip_address)

# Wireless IP...
ip_address = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
print('IP Address of wlan0 =', ip_address)

# Use one of the discovered IP addresses...
TCPServer.allow_reuse_address = True
app = get_server(TCPServer, (ip_address, 7777), RequestHandler)



######################################################################################################################
# Holding Register Data Mapping (4xxxxx)...
@app.route(slave_ids=[1], function_codes=[3], addresses=list(range(0, 99999)))
def read_data_store(slave_id, function_code, address):
    datetimenow = datetime.now()

    """" Return value of address. """

#   data_store_hr[0] = int(Modbus_Heartbeat) # Needs to be disabled here for heartbeat to work!!!
    data_store_hr[1] = int(datetimenow.hour)
    data_store_hr[2] = int(datetimenow.minute)
    data_store_hr[3] = int(datetimenow.second)
    data_store_hr[4] = int(datetimenow.year)
    data_store_hr[5] = int(datetimenow.month)
    data_store_hr[6] = int(datetimenow.day)
    data_store_hr[7] = int(uniform(-32768, 32767))

    return data_store_hr[address]



######################################################################################################################
# Input Register Data Mapping (3xxxxx)...
@app.route(slave_ids=[1], function_codes=[4], addresses=list(range(0, 99999)))
def read_data_store(slave_id, function_code, address):
    """" Return value of address. """

    data_store_ir[0] = int(uniform(0, 10))

    return data_store_ir[address]



######################################################################################################################
# Holding register write (single or multiple register write)...
@app.route(slave_ids=[1], function_codes=[6, 16], addresses=list(range(0, 99999)))
def write_data_store(slave_id, function_code, address, value):
    """" Set value for address. """
    data_store_hr[address] = value
    #print("HR Write Received at Register:", address, "Value:", value)



######################################################################################################################
def Program_Status_LED(Prg_Status_Code):

    # Link LED Output to GPIO pin number...
    led = LED(17)

    # Pause before pulsing status LED...
    event.wait(2)

    # Pulse LED the same amount of times as program status code...
    for x in range(Prg_Status_Code):

        led.on()
        event.wait(0.2)
        print("LED On", Prg_Status_Code)

        led.off()
        event.wait(0.2)
        print("LED Off", Prg_Status_Code)



Thread_01 = Thread(target=Program_Status_LED, args=(Program_Status_Code,))



######################################################################################################################
# Initialize Values (This block will test the excepted error to occur)...
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
    Thread(target=app.serve_forever).start()
    print('app.serve_forever...')



    # Main Program Loop...
    while True:

        event.wait(0.01)


        ##############################################
        ####### Status LED for Program Code... #######
        ##############################################
        # Start Status LED Thread...
        if (not Thread_01.is_alive()) and (not Status_LED_Function_run):
            Thread_01.start()
            Status_LED_Function_run = True
        # Terminate Status LED Thread...
        if (not Thread_01.is_alive()) and Status_LED_Function_run:
            Thread_01.join()
            Status_LED_Function_run = False
            Thread_01 = Thread(target=Program_Status_LED, args=(Program_Status_Code,))



        #########################################################
        ####### Heartbeat over Modbus (Comms Watchdog...) #######
        #########################################################
        # Heartbeat register written to 1 by master, reset to 0 by slave...
        if (data_store_hr[0] == 1):
            Modbus_Heartbeat_Counter = 0
            data_store_hr[0] = 0

        # Every second increment the heartbeat counter...
        if Scan_Pulse:
            Modbus_Heartbeat_Counter += 1

        # If the heartbeat exceeds limit, we must have a communications loss, raise alarm...
        if Modbus_Heartbeat_Counter > Modbus_Heartbeat_Counter_Limit and (not Modbus_Comms_Timeout):
            Modbus_Comms_Timeout = True
            print("Modbus Heartbeat Timeout")
        else:
            if (Modbus_Heartbeat_Counter <= Modbus_Heartbeat_Counter_Limit) and (Modbus_Comms_Timeout):
                Modbus_Comms_Timeout = False
                print("Modbus Heartbeat Healthy")

        # Generate a pulse every scan cycle and increment a program scan counter...
        if (Program_Counter == 65535):
            Program_Counter = 0

        if (not Scan_Pulse):
            Scan_Pulse = True
            Program_Counter += 1
            #print(Program_Counter)
        else:
            Scan_Pulse = False



######################################################################################################################
# Finally block always gets executed either exception is generated or not...
finally:

    print('Program Status LED Killed...')
    Thread_01.join()

    print('Modbus.app.shutdown...')
    app.shutdown()

    print('Modbus.app.server_close...')
    app.server_close()

    print('Code Stopped...')
    exit()


