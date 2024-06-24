The following repository contains the necessary codes that should be implemented for this project (Advanced control of electronic wheelchairs to enhance mobility for individuals with Cerebral Palsy). The main components of the system include an Arduino for hardware control and several Python scripts for different control interfaces and sensor integrations.

Note that some libraries might need to be installed in order for the programs to work.

**Repository Contents**

      Control_Arduino_Grid3.py: Main Python script that reads and receives controls commands and sends them to the Arduino.
      
      Arduino_Control_Wheelchair.ino: Main Arduino program for controlling the wheelchair.
      
      Arduino_ESP32.ino: Arduino program for connecting with Amazon Alexa via ESP32.
      
      Control_Arduino_Amazon.py: Python script for controlling the Arduino using Amazon Alexa.
      
      Control_Arduino_prueba_camaras.py: Python script for integrating depth camera sensors.
      
      Control_Arduino_witmotion.py: Python script for angular movement control using Witmotion sensors.


The main programs that need to be running at all times are:

      Arduino_Control_Wheelchair.ino
      Control_Arduino_Grid3.py
      
Ensure the serial ports in both programs are correctly configured to match your hardware setup.

**Adaptive Control Systems**

    Depending on the adaptive control system you wish to use, follow the instructions below:

1. Angular Movement Control with Witmotion Sensor
   
   To enable angular movement control, run the following script:
   
          Control_Arduino_witmotion.py
   
   Ensure Bluetooth is activated on your computer for proper connection with the Witmotion sensor.
        
2. Amazon Alexa Integration
   
   For Amazon Alexa control, the following programs need to be running:
   
          Arduino_ESP32.ino
          Control_Arduino_Amazon.py
   
   This setup allows voice control of the wheelchair via Amazon Alexa.

3. Vision control is already implemented onto the file. However, you must configure the program you will be using in order to simulate the established keys when slecting a command direction via eye gaze so that the Python program recognizes them
        
**Obstacle Detection System**

   The ultrasound sensors are already integrated into the Arduino_Control_Wheelchair.ino program. For additional obstacle detection using depth camera sensors, run the following script:   
        
          Control_Arduino_prueba_camaras.py
          
   If you do not wish to use the camera sensors, simply comment out the relevant sections in the main Python program.

