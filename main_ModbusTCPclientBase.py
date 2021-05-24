import socket
from umodbus import conf
from umodbus.client import tcp
from time import sleep



######################################################################################################################
# This is a 'blank' Modbus TCP client (Master), which can be configured as needs be to read a Modbus server (Slave)



######################################################################################################################
# Initialize values (This block will test the excepted error to occur)...
try:
    print("Code Initializing...")

    # Modbus Client...
    # Enable values to be signed (default is False).
    conf.SIGNED_VALUES = True

    # Create TCP/IP connection. (Must be the IP address & port number of the connected server [slave] device)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.1.88', 7777))

    # Make some register arrays to store received Modbus Data.
    Received_Data_HR = list()
    Received_Data_IR = list()



######################################################################################################################
# The try section has failed (handle the error)...
except:
    print('Something went wrong with Try block...')
    print('Check the remote IP address is available...')
    print('Check the Modbus Slave is actually turned on...')
    exit()



######################################################################################################################
# The try section has been successful (If there is no exception then this block will be executed)...
else:
    print('Code Running...')

    # Main Program Loop...
    while True:

        # Modbus Write HR (continuously)...
        write_HR_message_01 = tcp.write_multiple_registers(slave_id=1, starting_address=0, values=[1])
        write_HR_message_01_response = tcp.send_message(write_HR_message_01, sock)


        # Modbus Read HR (continuously)...
        read_HR_message_01 = tcp.read_holding_registers(slave_id=1, starting_address=100, quantity=10)
        read_HR_message_01_response = tcp.send_message(read_HR_message_01, sock)


        # Modbus Read IR (continuously)...
        read_IR_message_01 = tcp.read_input_registers(slave_id=1, starting_address=0, quantity=10)
        read_IR_message_01_response = tcp.send_message(read_IR_message_01, sock)


        # Print some registers that have been read
        print(read_HR_message_01_response)



######################################################################################################################
# Finally block always gets executed either exception is generated or not...
finally:

    print('sock.close...')
    sock.close()
    sleep(0.5)

    print('Code Stopped...')
    exit()


