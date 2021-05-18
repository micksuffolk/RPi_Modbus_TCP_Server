import netifaces
from threading import Thread, Event
from multiprocessing import Process
from socketserver import TCPServer
from collections import defaultdict
from umodbus import conf
from umodbus.server.tcp import RequestHandler, get_server
from datetime import datetime
from random import uniform
from gpiozero import LED



######################################################################################################################
# Initialize some variables...
Program_Counter = int(0) # Counts up to 65535 and returns to zero, always incrementing
Program_Status_Code = int(1) # Program status, for diagnostics mainly
Modbus_Heartbeat_Counter = int(0) # Counter which resets to zero when heartbeat received over Modbus link
Modbus_Heartbeat_Counter_Limit = int(200) # Limit for determining a Modbus communications timeout
Modbus_Comms_Timeout = bool(False) # Modbus communications timeout
Scan_Pulse = bool(False) # pulse which alternates every scan cycle, for general programming use
Status_LED_Function_run = bool(False) # The status LED flashing function is running
event = Event() # Generate a variable for the event.wait() function, alternative to sleep() function



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
# A function to flash a status LED the required number of pulses to indicate realtime program status...
def Program_Status_LED(Prg_Status_Code):

    # Link LED Output to GPIO pin number 17...
    led = LED(17)

    # Pause before pulsing status LED...
    event.wait(2)

    # Pulse LED the same amount of times as program status code...
    for x in range(Prg_Status_Code):

        led.on()
        event.wait(0.4)
        #print("LED On", Prg_Status_Code)

        led.off()
        event.wait(0.4)
        #print("LED Off", Prg_Status_Code)



# Create a process so the LED function can run in parallel with other tasks (multiprocessing)...
Process_Program_Status_LED = Process(target=Program_Status_LED, args=(Program_Status_Code,))



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

        # Keep the program loop running at a steady pace (i.e. 10ms delay)...
        event.wait(0.01)


        ##############################################
        ####### Status LED for Program Code... #######
        ##############################################
        # Start the Status LED flashing function...
        if (not Process_Program_Status_LED.is_alive()) and (not Status_LED_Function_run):
            Process_Program_Status_LED.start()
            Status_LED_Function_run = True
        # Terminate Status LED Process...
        if (not Process_Program_Status_LED.is_alive()) and Status_LED_Function_run:
            Process_Program_Status_LED.terminate()
            Process_Program_Status_LED.join()
            Status_LED_Function_run = False
            Process_Program_Status_LED = Process(target=Program_Status_LED, args=(Program_Status_Code,))



        #########################################################
        ####### Heartbeat over Modbus (Comms Watchdog...) #######
        #########################################################
        # Heartbeat register (400000) written to 1 by master, reset to 0 by slave...
        # With every 'pulse' to 1, the communications link must be alive, reset the heartbeat counter...
        if (data_store_hr[0] == 1):
            Modbus_Heartbeat_Counter = 0
            data_store_hr[0] = 0

        # Every scan pulse increment the heartbeat counter...
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



        ##########################################################
        ####### Program counter for general programming... #######
        ##########################################################
        # Generate a pulse every scan cycle and increment a program scan counter...
        if (Program_Counter == 65535):
            Program_Counter = 0

        if (not Scan_Pulse):
            Scan_Pulse = True
            Program_Counter += 1
            #print(Program_Counter)
        else:
            Scan_Pulse = False



        ########################################################
        ####### Read the system date and time from Pi... #######
        ########################################################
        datetimenow = datetime.now()



        ###########################################################
        ####### Modbus Holding Register Mapping (4xxxxx)... #######
        ###########################################################
#       data_store_hr[0] = int(Modbus_Heartbeat) # Needs to be disabled here for heartbeat to work!!!
        data_store_hr[1] = int(datetimenow.hour)
        data_store_hr[2] = int(datetimenow.minute)
        data_store_hr[3] = int(datetimenow.second)
        data_store_hr[4] = int(datetimenow.year)
        data_store_hr[5] = int(datetimenow.month)
        data_store_hr[6] = int(datetimenow.day)
        data_store_hr[7] = int(uniform(-32768, 32767)) # random number generator



        #########################################################
        ####### Modbus Input Register Mapping (3xxxxx)... #######
        #########################################################
        data_store_ir[0] = int(uniform(0, 10)) # random number generator



######################################################################################################################
# Finally block always gets executed either exception is generated or not...
finally:

    Process_Program_Status_LED.terminate()
    Process_Program_Status_LED.join()
    print('Program Status LED Killed...')

    app.shutdown()
    print('Modbus.app.shutdown...')

    app.server_close()
    print('Modbus.app.server_close...')

    Thread_Modbus_Server.join()
    print('Modbus Server Thread closed...')

    print('Code Stopped...')
    exit()


