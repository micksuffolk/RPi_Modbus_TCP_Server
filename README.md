# Modbus_TCP_Server_Python

This project contains two 'main' Python files...
main.py = Mikes Raspberry Pi Project, contains code specific to this projects requirements.
main_ModbusTCPserverBase = A good starting point to make another Modbus TCP Server project.

Modbus TCP Server, responds to the following function codes...
04 Read Input Registers (3xxxxx)
03 Read Holding Registers (4xxxxx)
06 Write Single Holding Register (4xxxxx)
16 Write Multiple Holding Registers (4xxxxx)
