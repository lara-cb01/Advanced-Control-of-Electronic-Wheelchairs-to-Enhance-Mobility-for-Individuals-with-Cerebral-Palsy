import asyncio
import threading
import time
import bleak
import keyboard
import sys

# Global variables for controlling the program
last_key_press_time = 0
comparing_data = False
finalizar = False
ultima_tecla = None
stop_flag = False
tasks = []
loop = None

async def main():
    global loop
    loop = asyncio.get_event_loop()
    # Store the current event loop

    async def callback_method(device):
        pass

    found_devices = await scan()
    if not found_devices:
        print("No devices found. Exiting program.")
        await exit_program()
    first_device = found_devices[0]

    device = DeviceModel(first_device.name, first_device.address, callback_method)
    task = asyncio.create_task(device.openDevice())
    tasks.append(task)
    try:
        await task
    except asyncio.CancelledError:
        pass

async def stop_asyncio():
    global stop_flag
    await asyncio.sleep(0.1)
    stop_flag = True

async def exit_program():
    print("Exiting the program...")
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    sys.exit(0)

async def scan():
    global devices
    found = []
    print("Searching for Bluetooth devices...")
    try:
        devices = await bleak.BleakScanner.discover()
        print("Search ended")
        for d in devices:
            if d.name and "WT" in d.name:
                found.append(d)
                print(f"{d.address}: {d.name}")
        if not devices:
            print("No devices found!")
        return found
    except Exception as ex:
        print("Bluetooth search failed to start")
        print(ex)
        await exit_program()

def is_within_margin(value, expected, margin):
    if value is None or expected is None:
        return False
    return abs(value - expected) <= margin

class DeviceModel:
    def __init__(self, deviceName, mac, callback_method):
        print("Initialize device model")
        self.deviceName = deviceName
        self.mac = mac
        self.client = None
        self.writer_characteristic = None
        self.isOpen = False
        self.callback_method = callback_method
        self.deviceData = {}
        self.saved_data = {}
        self.TempBytes = []
        self.stop_keyboard_listener = False

    async def openDevice(self):
        print("Opening device......")
        async with bleak.BleakClient(self.mac) as client:
            self.client = client
            self.isOpen = True
            target_service_uuid = "0000ffe5-0000-1000-8000-00805f9a34fb"
            target_characteristic_uuid_read = "0000ffe4-0000-1000-8000-00805f9a34fb"
            target_characteristic_uuid_write = "0000ffe9-0000-1000-8000-00805f9a34fb"
            notify_characteristic = None
            print("Matching services......")
            await client.get_services()  # Ensure services are discovered
            for service in client.services:
                if service.uuid == target_service_uuid:
                    print(f"Service: {service}")
                    print("Matching characteristic......")
                    for characteristic in service.characteristics:
                        if characteristic.uuid == target_characteristic_uuid_read:
                            notify_characteristic = characteristic
                        if characteristic.uuid == target_characteristic_uuid_write:
                            self.writer_characteristic = characteristic
                        if notify_characteristic:
                            break
                    if self.writer_characteristic:
                        print("Reading magnetic field quaternions")
                        asyncio.create_task(self.sendDataTh())
                    if notify_characteristic:
                        print(f"Characteristic: {notify_characteristic}")
                        await client.start_notify(notify_characteristic.uuid, self.onDataReceived)
                    # Start keyboard listener in a separate thread
                    keyboard_thread = threading.Thread(target=self.start_keyboard_listener)
                    keyboard_thread.start()
                    try:
                        while self.isOpen:
                            await asyncio.sleep(1)
                    except asyncio.CancelledError:
                        pass
                    finally:
                        await client.stop_notify(notify_characteristic.uuid)
            else:
                print("No matching services or characteristic found")

    def closeDevice(self):
        self.isOpen = False
        print("The device is turned off")

    async def sendDataTh(self):
        await asyncio.sleep(3)
        while self.isOpen:
            await self.readReg(0x3A)
            await asyncio.sleep(0.1)
            await self.readReg(0x51)
            await asyncio.sleep(0.1)

    async def sendData(self, data):
        try:
            if self.client.is_connected and self.writer_characteristic is not None:
                await self.client.write_gatt_char(self.writer_characteristic.uuid, bytes(data))
        except Exception as ex:
            print(ex)

    async def readReg(self, regAddr):
        await self.sendData(self.get_readBytes(regAddr))

    async def writeReg(self, regAddr, sValue):
        self.unlock()
        await asyncio.sleep(0.1)
        await self.sendData(self.get_writeBytes(regAddr, sValue))
        await asyncio.sleep(0.1)
        self.save()

    @staticmethod
    def get_readBytes(regAddr):
        tempBytes = [None] * 5
        tempBytes[0] = 0xff
        tempBytes[1] = 0xaa
        tempBytes[2] = 0x27
        tempBytes[3] = regAddr
        tempBytes[4] = 0
        return tempBytes

    @staticmethod
    def get_writeBytes(regAddr, rValue):
        tempBytes = [None] * 5
        tempBytes[0] = 0xff
        tempBytes[1] = 0xaa
        tempBytes[2] = regAddr
        tempBytes[3] = rValue & 0xff
        tempBytes[4] = rValue >> 8
        return tempBytes

    def unlock(self):
        cmd = self.get_writeBytes(0x69, 0xb588)
        asyncio.run_coroutine_threadsafe(self.sendData(cmd), loop)

    @staticmethod
    def getSignInt16(num):
        if num >= pow(2, 15):
            num -= pow(2, 16)
        return num

    def save(self):
        cmd = self.get_writeBytes(0x00, 0x0000)
        asyncio.run_coroutine_threadsafe(self.sendData(cmd), loop)

    def processData(self, Bytes):
        if Bytes[1] == 0x61:
            AngX = self.getSignInt16(Bytes[15] << 8 | Bytes[14]) / 32768 * 180
            AngY = self.getSignInt16(Bytes[17] << 8 | Bytes[16]) / 32768 * 180
            AngZ = self.getSignInt16(Bytes[19] << 8 | Bytes[18]) / 32768 * 180
            self.deviceData["AngX"] = round(AngX, 3)
            self.deviceData["AngY"] = round(AngY, 3)
            self.deviceData["AngZ"] = round(AngZ, 3)
            asyncio.run_coroutine_threadsafe(self.callback_method(self), loop)

    def onDataReceived(self, sender, data):
        tempdata = bytes.fromhex(data.hex())
        for var in tempdata:
            self.TempBytes.append(var)
            if len(self.TempBytes) == 1 and self.TempBytes[0] != 0x55:
                del self.TempBytes[0]
                continue
            if len(self.TempBytes) == 2 and (self.TempBytes[1] != 0x61 and self.TempBytes[1] != 0x71):
                del self.TempBytes[0]
                continue
            if len(self.TempBytes) == 20:
                self.processData(self.TempBytes)
                self.TempBytes.clear()

    def save_data(self, key, nombre_archivo):
        # where key stands for the respective command directions (forward, backward, left, right and neutral)
        if key in ['0', '1', '2', '3', '4']:
            AngX = self.deviceData.get('AngX')
            AngY = self.deviceData.get('AngY')
            AngZ = self.deviceData.get('AngZ')
            self.saved_data[key] = {'AngX': AngX, 'AngY': AngY, 'AngZ': AngZ}
            print(f"{key}: {self.saved_data[key]}")                
        else:
            print("Se ha presionado una tecla no válida.")
        
        with open(nombre_archivo, 'w') as archivo:
            for saved_key, saved_value in self.saved_data.items():
                AngX = saved_value['AngX']
                AngY = saved_value['AngY']
                AngZ = saved_value['AngZ']
                archivo.write(f"{saved_key} {AngX if AngX is not None else 'None'} {AngY if AngY is not None else 'None'} {AngZ if AngZ is not None else 'None'}\n")


    def start_keyboard_listener(self):
        keyboard.on_press(self.on_press)
        while not self.stop_keyboard_listener:
            time.sleep(0.1)

    def on_press(self, event):
        global last_key_press_time, ultima_tecla
        debounce_time = 0.5
        current_time = time.time()
        datos_refencia = "datos_witmotion_referencia"
        x_value_file = "x_value.txt"
        
        if current_time - last_key_press_time >= debounce_time:
            last_key_press_time = current_time
            key = event.name
            if key  == '0':
                ultima_tecla = key
                self.save_data(key, "datos_witmotion_referencia.txt")
            elif key  == '1':
                ultima_tecla = key
                self.save_data(key, "datos_witmotion_referencia.txt")
            elif key  == '2':
                ultima_tecla = key
                self.save_data(key, "datos_witmotion_referencia.txt")
            elif key  == '3':
                ultima_tecla = key
                self.save_data(key, "datos_witmotion_referencia.txt")
            elif key  == '4':
                ultima_tecla = key
                self.save_data(key, "datos_witmotion_referencia.txt")
            elif key == 's':
                global comparing_data
                comparing_data = True
                print("Iniciando comparación de datos...")
                asyncio.run_coroutine_threadsafe(self.start_continuous_comparison('datos_witmotion_referencia.txt', self.compare_with_reference_data), loop)
            
            elif key == 'q':      
                print("Finalizando programa...")
                with open('x_value.txt', 'w') as f:
                    x = 0
                    f.write(str(x))
                time.sleep(0.5)
                self.closeDevice()
                self.stop_keyboard_listener = True
                asyncio.run_coroutine_threadsafe(exit_program(), loop)

    async def compare_with_reference_data(self, nombre_archivo):
        print("Performing comparison with reference data...")
        # Leer los datos de referencia del archivo
        reference_data = {}
        with open(nombre_archivo, 'r') as archivo:
            for linea in archivo:
                partes = linea.strip().split()
                if len(partes) == 4:
                    key = partes[0]
                    AngX = float(partes[1]) if partes[1] != 'None' else None
                    AngY = float(partes[2]) if partes[2] != 'None' else None
                    AngZ = float(partes[3]) if partes[3] != 'None' else None
                    reference_data[key] = {'AngX': AngX, 'AngY': AngY, 'AngZ': AngZ}

        # Get current measurements
        current_data = {
            'AngX': self.deviceData.get('AngX'),
            'AngY': self.deviceData.get('AngY'),
            'AngZ': self.deviceData.get('AngZ')
        }

        margin = 15
        x = self.deviceData.get("x", None)

        # Write x value to a file
        with open('x_value.txt', 'w') as f:
            for position, saved_data in reference_data.items():
                similarity = all(
                    is_within_margin(current_data[key], saved_data[key], margin) 
                    for key in current_data
                )
                if similarity:
                    print(f"Current measurements are similar to {position} position data.")
                    print(current_data)
                    x = position
                    f.write(str(x))
                    return  # Detener la comparación después de encontrar una coincidencia
                else:
                    x = 0
                    f.write(str(x))
                    print("Current measurements do not match any saved position within the margin of error.")

    async def start_continuous_comparison(self, file_name, comparison_method):
        await self.continuous_comparison(file_name, comparison_method)

    async def continuous_comparison(self, file_name, comparison_method):
        while comparing_data:
            await comparison_method(file_name)
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    try:
        asyncio.run(main())        
    except KeyboardInterrupt:
        pass
