# pyinstaller --onefile --console --name TFG_LARA --add-data "Control_Arduino_witmotion.py;." --add-data "Control_Arduino_Amazon.py;."--add-data "x_value.txt;." --add-data "datos_witmotion_referencia.txt;." --add-data "commands.txt;."Control_Arduino_Grid3.py
# pyinstaller --onefile --console --name ejecutable_wit --add-data "x_value.txt;." --add-data "datos_witmotion_referencia.txt;." Control_Arduino_witmotion.py

# pyinstaller --onefile --console --name cadira_Lara `
# --add-data "C:\Users\Lara\Desktop\TFG\Control_Arduino_witmotion.py;." `
# --add-data "C:\Users\Lara\Desktop\TFG\x_value.txt;." `
# --add-data "C:\Users\Lara\Desktop\TFG\datos_witmotion_referencia.txt;." `
# C:\Users\Lara\Desktop\TFG\Control_Arduino_Grid3.py

import serial  # For serial communication with Arduino
import time  
from pynput import keyboard  # Keyboard listener
import subprocess  # To execute other programs from this main one
import re
import threading
import os
import cv2


# Configure depending on what the Arduine port is for your computer
puerto_serial = serial.Serial('COM10', 9600)  
time.sleep(2)  

script_dir = os.path.dirname(os.path.abspath(__file__))

datos_refencia = os.path.join(script_dir, 'datos_witmotion_referencia.txt')
x_value_file = os.path.join(script_dir, 'x_value.txt')
commands_file = os.path.join(script_dir, 'commands.txt')
distancias_file = os.path.join(script_dir, 'distancias.txt')

ultimo_estado_distancias = None

ultimo_numero = ""
ultimo_valor = ""

# Variable to control the keyboard listener
finalizar = False  

ultima_tecla = None
process = None
ultimo_numero_previo = None
last_key = None
last_control = None
stop_threads = False

# For the following ejecutar_subprocess_ adapt the location of the .py files in archivo_a_ejecutar

def ejecutar_subprocess():
    global process
    archivo_a_ejecutar = r'C:/Users/Lara/Desktop/TFG/Control_Arduino_witmotion.py'
    process = subprocess.Popen(['python', archivo_a_ejecutar])
    process.wait()  # until it is done
    print("Subproceso terminado. Cerrando proceso principal.")
    os._exit(0)  

def ejecutar_subprocess_amazon():
    global process
    archivo_a_ejecutar = r'C:/Users/Lara/Desktop/TFG/Control_Arduino_Amazon.py'
    process = subprocess.Popen(['python', archivo_a_ejecutar])
    process.wait()   # until it is done
    print("Subproceso terminado. Cerrando proceso principal.")
    os._exit(0)  
    
def ejecutar_subprocess_detectar_distancias():
    global process
    archivo_a_ejecutar = r'C:/Users/Lara/Desktop/TFG/Control_Arduino_prueba_camaras.py'
    process = subprocess.Popen(['python', archivo_a_ejecutar])
    process.wait()   # until it is done
    print("Subproceso terminado. Cerrando proceso principal.")
    os._exit(0)  
    

# in order to read the .txt with the information from the camera sensors 
thread_leer = threading.Thread(target=ejecutar_subprocess_detectar_distancias)
thread_leer.start()

def leer_distancias():
    with open(distancias_file, 'r') as f:
        contenido = f.read().strip()
    return contenido

def verificar_y_enviar():
    global puerto_serial
    global last_key
    global last_control
    global stop_threads

    ultimo_estado_enviado = None
    tiempo_ultimo_envio = time.time()  # Inicializar temporizador

    while not stop_threads:
        contenido = leer_distancias()
        current_time = time.time()

        if contenido == '0':
            if ultimo_estado_enviado != '0' or (current_time - tiempo_ultimo_envio) >= 5: 
# 5s is the time between moving the wheelchair again once the value '0' is read from the file
                char = contenido
                puerto_serial.write(b'y\n')
                time.sleep(1)  
                
                if last_control == 'j':
                    puerto_serial.write(b'j\n')
                elif last_control == 'o':
                    puerto_serial.write(b'o\n')
                
                ultimo_estado_enviado = '0'
                tiempo_ultimo_envio = current_time
                time.sleep(3)
              
        if contenido == '6':
            if ultimo_estado_enviado != '6' or (current_time - tiempo_ultimo_envio) >= 5: 
                char = contenido
                puerto_serial.write(b'z\n')
                    
                if last_key == 'a':
                    puerto_serial.write(b'a\n')
                elif last_key == 'b':
                    puerto_serial.write(b'b\n')
                elif last_key == 'r':
                    puerto_serial.write(b'r\n')
                elif last_key== 'l':
                    puerto_serial.write(b'l\n')
                elif last_key == 'p':
                    puerto_serial.write(b'p\n')
                ultimo_estado_enviado = '6'
                tiempo_ultimo_envio = current_time
                
            elif ultimo_estado_enviado == '0' or (current_time - tiempo_ultimo_envio) >= 5:
                char = contenido
                puerto_serial.write(b'z\n')
                ultimo_estado_enviado = '6'
                tiempo_ultimo_envio = current_time
                
        time.sleep(0.1)  # Read every 0.1 second

thread_verificar = threading.Thread(target=verificar_y_enviar)
thread_verificar.start()

def on_press(key):
    global finalizar
    global ultima_tecla
    global last_key
    global last_control
    global ultimo_numero_previo 
    global process
    global primer_numero_leido_distancia
    global ultimo_estado_distancias
    global stop_threads


    primer_numero_leido_distancia = False
    primer_numero_leido_distancia = False
    ultimo_numero_distancia_previo = None
                
    try:

        if hasattr(key, 'char') and key.char is not None:
            char = key.char
            
            if char == 'q':
                puerto_serial.write(b'q\n')
                puerto_serial.write(b'p\n')
                print("You pressed 'q', closing everything...")
                finalizar = True
                puerto_serial.write(b'p\n')
                if process:
                    process.terminate()
                    process.wait() 
                stop_threads = True
                cv2.destroyAllWindows()
                time.sleep(1)
                os._exit(0)  # Exit the main process

                if  ultima_tecla != 'q':
                    puerto_serial.write(b'p\n')
                    puerto_serial.write(b'q\n')
                    puerto_serial.write(b'p\n')
                    if process:
                        process.terminate()
                    stop_threads = True
                    os._exit(0)

                
            if char == 'z':
                puerto_serial.write(b'z\n')
                print("Velocity configured to 12")
                if  ultima_tecla != 'z':
                    puerto_serial.write(b'z\n')
                ultima_tecla = char
                if last_key == 'a':
                    puerto_serial.write(b'a\n')
                elif last_key == 'b':
                    puerto_serial.write(b'b\n')
                elif last_key == 'r':
                    puerto_serial.write(b'r\n')
                elif last_key== 'l':
                    puerto_serial.write(b'l\n')
                elif last_key == 'p':
                    puerto_serial.write(b'p\n')

            elif char == 'x':
                puerto_serial.write(b'x\n')
                print("Velocity configured to 7")
                if  ultima_tecla != 'z':
                    puerto_serial.write(b'x\n')
                ultima_tecla = char
                if last_key == 'a':
                    puerto_serial.write(b'a\n')
                elif last_key == 'b':
                    puerto_serial.write(b'b\n')
                elif last_key == 'r':
                    puerto_serial.write(b'r\n')
                elif last_key== 'l':
                    puerto_serial.write(b'l\n')
                elif last_key == 'p':
                    puerto_serial.write(b'p\n')
                
            elif char == 'c':
                puerto_serial.write(b'c\n')
                print("Velocity configured to 1")
                if  ultima_tecla != 'c':
                    puerto_serial.write(b'c\n')
                ultima_tecla = char
                if last_key == 'a':
                    puerto_serial.write(b'a\n')
                elif last_key == 'b':
                    puerto_serial.write(b'b\n')
                elif last_key == 'r':
                    puerto_serial.write(b'r\n')
                elif last_key== 'l':
                    puerto_serial.write(b'l\n')
                elif last_key == 'p':
                    puerto_serial.write(b'p\n')
            
                
            elif char == 'j':  
                puerto_serial.write(b'j\n')
                print("Key 'j' joystick")
                if  ultima_tecla != 'j':
                    pass
                ultima_tecla = char
                last_control = char
                print({last_control})

                    
            elif char == 't':
                puerto_serial.write(b't\n')
                print("STOP to change control")
                if  ultima_tecla != 't':
                    puerto_serial.write(b't\n')    
                ultima_tecla = char
                
            elif char == 'o':
                puerto_serial.write(b'o\n')
                print("Key 'o' for eyes")
                if  ultima_tecla != 'o':
                    pass
                ultima_tecla = char
                last_control = char
                                     
            elif char == 'a':
                puerto_serial.write(b'a\n')
                print("Arrow up")                
                if ultima_tecla != 'a':
                    puerto_serial.write(b'a\n')
                ultima_tecla = char
                last_key = ultima_tecla
                
            elif char == 'b':
                puerto_serial.write(b'b\n')    
                print("Arrow down")            
                if ultima_tecla != 'b':
                    puerto_serial.write(b'b\n')
                ultima_tecla = char
                last_key = ultima_tecla
                
            elif char == 'l':
                puerto_serial.write(b'l\n')
                print("Arrow left")
                if ultima_tecla != 'l':
                    puerto_serial.write(b'l\n')
                ultima_tecla = char
                last_key = ultima_tecla
                
            elif char == 'r':
                puerto_serial.write(b'r\n')
                print("Arrow right")
                if ultima_tecla != 'r':
                    puerto_serial.write(b'r\n')
                ultima_tecla = char
                last_key = ultima_tecla
                
            elif char == 'p':
                puerto_serial.write(b'p\n')
                print("Stop")
                if ultima_tecla != 'p':
                    puerto_serial.write(b'p\n')
                ultima_tecla = char
                last_key = ultima_tecla
            
            elif hasattr(key, 'char') and key.char == 'v':
                puerto_serial.write(b'v\n')
                last_control = char
                try:
                    print("Initializing subprocess...")
                    threading.Thread(target=ejecutar_subprocess_amazon).start()
                    try: 
                        primer_numero_leido = False
                        ultimo_numero_previo = None
                        ultima_tecla = ''

                        while True:

                            with open('commands.txt', 'r') as archivo:
                                primera_linea = archivo.readline().strip()
                                time.sleep(0.01)
                                if char == 'q':
                                    puerto_serial.write(b'p\n')
                                    print("Exiting program...")
                                    subprocess.terminate()
                                    subprocess.kill()
                                    return

                            if primera_linea:
                                if not primer_numero_leido:
                                    primer_caracter = primera_linea[0]
                                    if primer_caracter != 'p':
                                        primer_numero_leido = True

                                ultimo_numero = primera_linea[-1]

                                if ultimo_numero_previo is not None and ultimo_numero != ultimo_numero_previo:
                                    puerto_serial.write(b'p\n')  
            # send a 'p' in between commands so there is no superposition between them

                                ultimo_numero_previo = ultimo_numero  

                                if ultimo_numero == 'p':
                                    char = 'p'
                                    ultima_tecla = ''
                                    puerto_serial.write(b'p\n')
                                    if ultima_tecla != 'p':
                                        puerto_serial.write(b'p\n')
                                    ultima_tecla = char  
                                    last_key = ultima_tecla 

                                elif ultimo_numero == 'a':
                                    char = 'a'
                                    puerto_serial.write(b'a\n')
                                    if ultima_tecla != 'a':
                                        puerto_serial.write(b'a\n')
                                    ultima_tecla = char  
                                    last_key = ultima_tecla
                                    
                                elif ultimo_numero == 'b':
                                    char = 'b'
                                    puerto_serial.write(b'b\n')
                                    if ultima_tecla != 'b':
                                        puerto_serial.write(b'b\n')
                                    ultima_tecla = char   
                                    last_key = ultima_tecla

                                elif ultimo_numero == 'l':
                                    char = 'l'
                                    puerto_serial.write(b'l\n')
                                    if ultima_tecla != 'l':
                                        puerto_serial.write(b'l\n')
                                    ultima_tecla = char   
                                    last_key = ultima_tecla

                                elif ultimo_numero == 'r':
                                    char = 'r'
                                    puerto_serial.write(b'r\n')
                                    if ultima_tecla != 'r':
                                        puerto_serial.write(b'r\n')
                                    ultima_tecla = char
                                    last_key = ultima_tecla
                                    
                                elif ultimo_numero == 'q':
                                    char = 'q'
                                    ultima_tecla = ''
                                    puerto_serial.write(b'p\n')
                                    os._exit(0)
                                    
                    except Exception as e:
                        print(f"Error when processing key: {e}")
   
                except Exception as e:
                    print(f"Error when processing key: {e}")
                    
            elif hasattr(key, 'char') and key.char == 'w':
                puerto_serial.write(b'm\n')
                puerto_serial.write(b'p\n')
                try: 
                    print("Initializing subprocess...")
                    threading.Thread(target=ejecutar_subprocess).start()
                    time.sleep(10)
                    try: 
                        primer_numero_leido = False
                        ultimo_numero_previo = None
                        ultima_tecla = ''

                        while True:
                            with open('x_value.txt', 'r') as archivo:   
                                primera_linea = archivo.readline().strip()
                                time.sleep(0.3)

                                if char == 'q':
                                    puerto_serial.write(b'p\n')
                                    time.sleep(1)
                                    print("Exiting program...")
                                    subprocess.terminate()
                                    subprocess.kill()
                                    finalizar = True
                                    process.terminate()
                                    process.wait() 
                                    stop_threads = True
                                    os.exit(0)
                                    return

                            if primera_linea:
                                if not primer_numero_leido:
                                    primer_caracter = primera_linea[0]
                                    if primer_caracter != '0':
                                        primer_numero_leido = True

                                ultimo_numero = primera_linea[-1]

                                if ultimo_numero_previo is not None and ultimo_numero != ultimo_numero_previo:
                                    puerto_serial.write(b'p\n')  
            # send a 'p' in between commands so there is no superposition between them

                                ultimo_numero_previo = ultimo_numero 

                                if ultimo_numero == '0':
                                    char = 'p'
                                    ultima_tecla = ''
                                    puerto_serial.write(b'p\n')
                                    if ultima_tecla != 'p':
                                        puerto_serial.write(b'p\n')
                                    ultima_tecla = char   
                                    last_key = ultima_tecla

                                elif ultimo_numero == '1':
                                    char = 'a'
                                    puerto_serial.write(b'a\n')
                                    if ultima_tecla != 'a':
                                        puerto_serial.write(b'a\n')
                                    ultima_tecla = char  
                                    last_key = ultima_tecla
                                    
                                elif ultimo_numero == '2':
                                    char = 'b'
                                    puerto_serial.write(b'b\n')
                                    if ultima_tecla != 'b':
                                        puerto_serial.write(b'b\n')
                                    ultima_tecla = char   
                                    last_key = ultima_tecla

                                elif ultimo_numero == '3':
                                    char = 'l'
                                    puerto_serial.write(b'l\n')
                                    if ultima_tecla != 'l':
                                        puerto_serial.write(b'l\n')
                                    ultima_tecla = char  
                                    last_key = ultima_tecla 

                                elif ultimo_numero == '4':
                                    char = 'r'
                                    puerto_serial.write(b'r\n')
                                    if ultima_tecla != 'r':
                                        puerto_serial.write(b'r\n')
                                    ultima_tecla = char
                                    last_key = ultima_tecla
                                    
                                elif ultimo_numero == '6':
                                    char = 'z'
                                    puerto_serial.write('f12\n'.encode())
                                    if ultima_tecla != 'z':
                                        puerto_serial.write('f12\n'.encode())
                                    ultima_tecla = char  
                                    last_key = ultima_tecla                              
                    except Exception as e:
                        print(f"Error when processing key: {e}")
                except Exception as e:
                    print(f"Error when processing key: {e}")
    except Exception as e:
        print(f"Error when processing key: {e}")

# Initialize the keyboard listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()  # until 'q' is pressed



# Puerto serial must be closed when finishing the program
if puerto_serial.is_open:
    puerto_serial.close()
    print("Puerto serial cerrado.")
    
