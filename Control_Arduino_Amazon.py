import serial
import time
import sys
import keyboard 

serial_port = 'COM9'  
baud_rate = 115200
file_name = 'commands.txt'

ser = serial.Serial(serial_port, baud_rate, timeout=1)
time.sleep(2)  

def initialize_file():
    with open(file_name, 'w') as file:
        file.write('p\n')
    print('Initialized file with "p"')

def write_to_file(command):
    with open(file_name, 'w') as file:
        file.write(command)
        file.write('\n')
    print(f'Command written to file: {command}')

initialize_file()

try:
    while True:
        if ser.in_waiting > 0:
            command = ser.read(1).decode('utf-8')
            write_to_file(command)
        
        if keyboard.is_pressed('q'):
            break

except KeyboardInterrupt:
    print('Exiting...')
finally:
    ser.close()
