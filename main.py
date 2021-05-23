import netifaces
from threading import Thread, Event
from multiprocessing import Process
from socketserver import TCPServer
from collections import defaultdict
from umodbus import conf
from umodbus.server.tcp import RequestHandler, get_server
from datetime import datetime
from random import uniform
from gpiozero import LED, CPUTemperature



######################################################################################################################
# Function to check if a bit in an integer is ON or OFF...
# Integer range is 0 to 65535, bit range is 0 to 15...
def BitCheck(Integer_to_BitCheck, BitToCheck):
    if (Integer_to_BitCheck & (1 << BitToCheck)):
        return True # Bit is Logic 1 (one)
    else:
        return False # Bit is Logic 0 (zero)



######################################################################################################################
# Initialize some variables...
Program_Counter = int(0) # Counts up to 65535 and returns to zero, always incrementing
Program_Status_Code = int(5) # Program status, for diagnostics mainly
Modbus_Heartbeat = int(0) # Modbus Heartbeat pulse
Modbus_Heartbeat_Counter = int(0) # Counter which resets to zero when heartbeat received over Modbus link
Modbus_Heartbeat_Counter_Limit = int(200) # Limit for determining a Modbus communications timeout
Modbus_Comms_Timeout = bool(False) # Modbus communications timeout
Scan_Pulse = bool(False) # pulse which alternates every scan cycle, for general programming use
Status_LED_Function_run = bool(False) # The status LED flashing function is running
event = Event() # Generate a variable for the event.wait() function, alternative to sleep() function
CPU_Temp = int()

Modbus_ControlCommandWord1 = int()
Modbus_ControlCommandWord2 = int()
Modbus_ControlCommandWord3 = int()
Modbus_ControlCommandWord4 = int()
Modbus_ControlDataWord1 = int()
Modbus_ControlDataWord2 = int()
Modbus_ControlDataWord3 = int()
Modbus_ControlDataWord4 = int()
Modbus_ControlDataWord5 = int()
Modbus_ControlDataWord6 = int()
Modbus_ControlDataWord7 = int()
Modbus_ControlDataWord8 = int()

Modbus_ProgramStatus = int()
Modbus_Rasp_Pi_Temp = int()
Modbus_StatusDataWord1 = int()
Modbus_StatusDataWord2 = int()
Modbus_StatusDataWord3 = int()
Modbus_StatusDataWord4 = int()
Modbus_StatusDataWord5 = int()
Modbus_StatusDataWord6 = int()
Modbus_StatusDataWord7 = int()
Modbus_StatusDataWord8 = int()
Modbus_StatusDataWord9 = int()
Modbus_StatusDataWord10 = int()
Modbus_StatusDataWord11 = int()
Modbus_StatusDataWord12 = int()
Modbus_StatusDataWord13 = int()
Modbus_StatusDataWord14 = int()
Modbus_StatusDataWord15 = int()
Modbus_StatusDataWord16 = int()



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
        event.wait(0.1)
        #print("LED On", Prg_Status_Code)

        led.off()
        event.wait(0.4)
        #print("LED Off", Prg_Status_Code)



# Create a process/thread so the LED function can run in parallel with other tasks (multiprocessing)...
#Process_Program_Status_LED = Process(target=Program_Status_LED, args=(Program_Status_Code,))
Thread_Program_Status_LED = Thread(target=Program_Status_LED, args=(Program_Status_Code,))



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
        CPU_Temp = CPUTemperature()



        ##############################################
        ####### Status LED for Program Code... #######
        ##############################################
        # Start the Status LED flashing function...
        if (not Thread_Program_Status_LED.is_alive()) and (not Status_LED_Function_run):
            Thread_Program_Status_LED.start()
            Status_LED_Function_run = True
        # Terminate Status LED Process/Thread...
        if (not Thread_Program_Status_LED.is_alive()) and Status_LED_Function_run:
            #Process_Program_Status_LED.terminate()
            Thread_Program_Status_LED.join()
            Status_LED_Function_run = False
            Thread_Program_Status_LED = Thread(target=Program_Status_LED, args=(Program_Status_Code,))



        #########################################################
        ####### Heartbeat over Modbus (Comms Watchdog...) #######
        #########################################################
        # Heartbeat register (400000) written to 1 by master, reset to 0 by slave...
        # With every 'pulse' to 1, the communications link must be alive, reset the heartbeat counter...
        if (Modbus_Heartbeat == 1):
            Modbus_Heartbeat_Counter = 0
            Modbus_Heartbeat = 0

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

        # Modbus Command registers (written to by the Modbus Client/Master)
        if data_store_hr[0] != 0:
            Modbus_Heartbeat = data_store_hr[0]
            data_store_hr[0] = 0

        if data_store_hr[1] != 0:
            Modbus_ControlCommandWord1 = data_store_hr[1]
            data_store_hr[1] = 0

        if data_store_hr[2] != 0:
            Modbus_ControlCommandWord2 = data_store_hr[2]
            data_store_hr[2] = 0

        if data_store_hr[3] != 0:
            Modbus_ControlCommandWord3 = data_store_hr[3]
            data_store_hr[3] = 0

        if data_store_hr[4] != 0:
            Modbus_ControlCommandWord4 = data_store_hr[4]
            data_store_hr[4] = 0

        if data_store_hr[5] != 0:
            Modbus_ControlDataWord1 = data_store_hr[5]
            data_store_hr[5] = 0

        if data_store_hr[6] != 0:
            Modbus_ControlDataWord2 = data_store_hr[6]
            data_store_hr[6] = 0

        if data_store_hr[7] != 0:
            Modbus_ControlDataWord3 = data_store_hr[7]
            data_store_hr[7] = 0

        if data_store_hr[8] != 0:
            Modbus_ControlDataWord4 = data_store_hr[8]
            data_store_hr[8] = 0

        if data_store_hr[9] != 0:
            Modbus_ControlDataWord5 = data_store_hr[9]
            data_store_hr[9] = 0

        if data_store_hr[10] != 0:
            Modbus_ControlDataWord6 = data_store_hr[10]
            data_store_hr[10] = 0

        if data_store_hr[11] != 0:
            Modbus_ControlDataWord7 = data_store_hr[11]
            data_store_hr[11] = 0

        if data_store_hr[12] != 0:
            Modbus_ControlDataWord8 = data_store_hr[12]
            data_store_hr[12] = 0

        # Modbus Status registers (read by the Modbus Client/Master)
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
        Modbus_ProgramStatus        = Program_Status_Code
        Modbus_Rasp_Pi_Temp         = int(CPU_Temp.temperature)
        Modbus_StatusDataWord1      = Modbus_ControlCommandWord1
        Modbus_StatusDataWord2      = Modbus_ControlCommandWord2
        Modbus_StatusDataWord3      = Modbus_ControlCommandWord3
        Modbus_StatusDataWord4      = Modbus_ControlCommandWord4
        Modbus_StatusDataWord5      = Modbus_ControlDataWord1
        Modbus_StatusDataWord6      = Modbus_ControlDataWord2
        Modbus_StatusDataWord7      = Modbus_ControlDataWord3
        Modbus_StatusDataWord8      = Modbus_ControlDataWord4
        Modbus_StatusDataWord9      = Modbus_ControlDataWord5
        Modbus_StatusDataWord10     = Modbus_ControlDataWord6
        Modbus_StatusDataWord11     = Modbus_ControlDataWord7
        Modbus_StatusDataWord12     = Modbus_ControlDataWord8
        Modbus_StatusDataWord13     = 0
        Modbus_StatusDataWord14     = 0
        Modbus_StatusDataWord15     = 0
        Modbus_StatusDataWord16     = 0

        data_store_ir[0] = Modbus_ProgramStatus
        data_store_ir[1] = Modbus_Rasp_Pi_Temp
        data_store_ir[2] = Modbus_StatusDataWord1
        data_store_ir[3] = Modbus_StatusDataWord2
        data_store_ir[4] = Modbus_StatusDataWord3
        data_store_ir[5] = Modbus_StatusDataWord4
        data_store_ir[6] = Modbus_StatusDataWord5
        data_store_ir[7] = Modbus_StatusDataWord6
        data_store_ir[8] = Modbus_StatusDataWord7
        data_store_ir[9] = Modbus_StatusDataWord8
        data_store_ir[10] = Modbus_StatusDataWord9
        data_store_ir[11] = Modbus_StatusDataWord10
        data_store_ir[12] = Modbus_StatusDataWord11
        data_store_ir[13] = Modbus_StatusDataWord12
        data_store_ir[14] = Modbus_StatusDataWord13
        data_store_ir[15] = Modbus_StatusDataWord14
        data_store_ir[16] = Modbus_StatusDataWord15
        data_store_ir[17] = Modbus_StatusDataWord16

        data_store_ir[100] = int(uniform(0, 10)) # random number generator



######################################################################################################################
# Finally block always gets executed either exception is generated or not...
finally:

    #Process_Program_Status_LED.terminate()
    #Process_Program_Status_LED.join()
    Thread_Program_Status_LED.join()
    print('Program Status LED Killed...')

    app.shutdown()
    print('Modbus.app.shutdown...')

    app.server_close()
    print('Modbus.app.server_close...')

    Thread_Modbus_Server.join()
    print('Modbus Server Thread closed...')

    print('Code Stopped...')
    exit()


