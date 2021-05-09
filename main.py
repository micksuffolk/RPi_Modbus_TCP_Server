import threading
import netifaces
from threading import Thread
from LED_Function import LED_Function
from socketserver import TCPServer
from collections import defaultdict
from umodbus import conf
from umodbus.server.tcp import RequestHandler, get_server
from datetime import datetime
from random import uniform



# Event wait alternative to sleep() for threading purposes...
event_wait = threading.Event()



######################################################################################################################
# Initialize Values (This block will test the excepted error to occur)...
try:
    print("Code Initializing...")

    # Create Modbus data tables...
    data_store_hr = defaultdict(int)  # Holding Register Table (4xxxxx)
    data_store_ir = defaultdict(int)  # Input Register Table (3xxxxx)

    # Enable signed integers (default is False)...
    conf.SIGNED_VALUES = True

    # Setup server IP address & port number where clients can access the data...
    ip_address = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
    print('IP Address of wlan0 =', ip_address)
    TCPServer.allow_reuse_address = True
    app = get_server(TCPServer, (ip_address, 7777), RequestHandler)

    print('Initialize successful...')



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

        #############################################################
        ####### Run multiple threads (functions / scripts)... #######
        #############################################################
        Thread(target = LED_Function(17, event_wait)).start()



        #########################################################
        ####### Holding Register Data Mapping (4xxxxx)... #######
        #########################################################
        @app.route(slave_ids=[1], function_codes=[3], addresses=list(range(0, 99999)))
        def read_data_store(slave_id, function_code, address):
            datetimenow = datetime.now()

            """" Return value of address. """

            data_store_hr[0] = int(uniform(-32768, 32767))
            data_store_hr[1] = int(datetimenow.hour)
            data_store_hr[2] = int(datetimenow.minute)
            data_store_hr[3] = int(datetimenow.second)
            data_store_hr[4] = int(datetimenow.year)
            data_store_hr[5] = int(datetimenow.month)
            data_store_hr[6] = int(datetimenow.day)

            return data_store_hr[address]



        #######################################################
        ####### Input Register Data Mapping (3xxxxx)... #######
        #######################################################
        @app.route(slave_ids=[1], function_codes=[4], addresses=list(range(0, 99999)))
        def read_data_store(slave_id, function_code, address):
            """" Return value of address. """

            data_store_ir[0] = int(uniform(0, 10))

            return data_store_ir[address]



        #############################################################################
        ####### Holding register write (single or multiple register write)... #######
        #############################################################################
        @app.route(slave_ids=[1], function_codes=[6, 16], addresses=list(range(0, 99999)))
        def write_data_store(slave_id, function_code, address, value):
            """" Set value for address. """
            data_store_hr[address] = value



######################################################################################################################
# Finally block always gets executed either exception is generated or not...
finally:

    print('app.shutdown...')
    app.shutdown()
#    Thread(target=app.shutdown).start()
    event_wait.wait(2)

    print('app.server_close...')
    app.server_close()
#    Thread(target=app.server_close).start()
    event_wait.wait(2)

    print('Code Stopped...')
    exit()


