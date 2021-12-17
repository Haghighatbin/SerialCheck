import sys, os, serial, time
import serial.tools.list_ports as lp
import json
import matplotlib, matplotlib.pyplot as plt
matplotlib.use('TkAgg')

# Colour codes
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
WHITE = '\033[97m'

class serialChk:
    def __init__(self) -> None:
        """Initialising the serial communication with the STM32/ESP32 device"""
        self.content = ''
        self.counter = 0
        self.delay = 0.001
        self.start, self.end = 0, 0
        try:
            if lp.comports():
                for idx, port in enumerate(lp.comports()):
                    print("Available port: {}".format(str(port.device)))
                    # ESP32 on MACOS
                    if "usbmodem" in str(port.device) or "wch" in str(port.device) or "SLAB" in str(port.device):
                        serial_port = str(port.device)
                        serial_port = serial_port.replace("cu", "tty")
                    # ESP32 on WinOS
                    if "CP210x" in str(port):
                        serial_port = str(port.device)
                    # STM32/ESP32 on Ubuntu
                    if "ttyUSB0" in str(port.device) or "ttyACM0" in str(port.device):
                        serial_port = str(port.device)

                if serial_port:
                    self.operator = serial.Serial(serial_port, baudrate=115200)
                    print(GREEN + "connection established: \n{}".format(str(self.operator)) + WHITE)
            else:
                print(RED + "no serial connections were found." + WHITE)
                sys.exit(1)

        except Exception as e:
            print(e)

    def sender(self, command):
        """This method encapsulates and encodes the commands to the STM32/ESP32-device."""
        print('waiting for invitation', end='')
        
        while b'receiver: READY\n' not in self.operator.read_all():
            print('.', end='')
            time.sleep(1)
        print('\ninvited!')
        
        while b'got it.\n' not in self.operator.read_all():
            self.operator.write('go#'.encode())
            time.sleep(1)

        # __SERIAL SENDER__ 
        try:
            command += '*#'
            print(CYAN + "Command: {}".format(command) + WHITE)
            self.operator.write(command.encode())
            time.sleep(0.5) 
            resp = self.operator.read_all()
            while 'EOF received.\n' not in resp.decode():
                self.operator.write(command.encode())
                time.sleep(1)
                resp = self.operator.read_all()
                if 'EOF received.\n' in resp.decode():
                    break
                elif 'got it.\n' in resp.decode():
                    break
                else:
                    pass
            print('command received by the microcontroller.')
            self.receiver()

        except KeyboardInterrupt:
            return "aborted."
        except Exception as e:
            print(e)
            return "something's wrong."

    def receiver(self):
        """This method decapsulates and decodes the responses from the STM32/ESP32-device."""
        print('waiting for the response...')
        self.content = ''
        self.counter = 0
        self.start = time.time()

        while '*' not in self.content:
            try:
                time.sleep(0.5)
                data = self.operator.read_all()
                data_decd = data.decode()
                a_idx = data_decd.find('<') - len(data_decd)
                current_idx = data_decd[a_idx+1:data_decd.find('/')]
                z_idx = data_decd[data_decd.find('/')+1:data_decd.find('>')]
                if '#' in data_decd :
                    if '*' in data_decd:
                        self.content += data_decd[:-1]
                        print(GREEN + 'response received.' + WHITE)
                        time.sleep(0.002)
                        break
                    elif '_' in data_decd and int(current_idx) > self.counter:
                        self.content += data_decd[:a_idx]
                        self.operator.write('got it.#'.encode())
                        progress = round((int(current_idx) / int(z_idx)) * 100)
                        sys.stdout.write("[Received]: {}%\r".format(progress))
                        sys.stdout.flush()
                        self.counter += 1
                        time.sleep(0.002)
                    else:
                        pass
                else:
                    time.sleep(0.125)
            except:
                pass
        if '*' in self.content:
            self.operator.write('EOF received.#'.encode())
            self.end = time.time()
            with open('resp.txt', 'w') as raw_resp:
                raw_resp.write(self.content[:-1])
            file_size = os.path.getsize('resp.txt')
            elapsed_time = round(self.end - self.start, 3)
            print(f"response file size is: {round(file_size/1024,2)} kbytes.")
            print(f"took {elapsed_time} seconds to receive the response file.")
            print(f"receiving rate was roughly: {round(file_size/elapsed_time)} B/s.")
            with open('resp.txt', 'r') as f:
                for line in f:
                    return eval(line)
        else:
            return "corrupted data."
        
    def plot(self, _list):
        """Plots the astroid's coordinates to validate the received data."""
        plt.axis('off')
        for _ in range(1):
            for i in range(len(_list)):
                plt.plot(_list[i][0], _list[i][1], 'b-')
                plt.pause(self.delay)
                plt.plot(_list[i][0], _list[i][2], 'b-')
                plt.pause(self.delay)
            for i in reversed(range(len(_list))):
                plt.pause(self.delay)
                plt.plot(_list[i][0], _list[i][1], 'w-')
                plt.pause(self.delay)
                plt.plot(_list[i][0], _list[i][2], 'w-')
                plt.pause(self.delay)
        plt.show()

    def run(self, iterations=5) -> None:
        """Prepares the serial test command; 
        Sending the request to the microcontroller to generate the data (astroid's coordinates).
        """
        if os.path.exists("resp.txt"):
            os.remove("resp.txt")

        command = ({'header': 'test'})
        command.update({'body': {'it': iterations}})
        jsnd_cmd = json.dumps(command)
        resp = self.sender(jsnd_cmd)

        try:
            with open('resp.txt', 'r') as f:
                for line in f:
                    if 'test' in eval(line)['header']:
                        list_t = eval(line)['body']
                        self.plot(list_t)
                    else:
                        print('Something is wrong with the received list.')
        except Exception as e:
            print(e)

if __name__ == "__main__":
    s = serialChk()

    # example: python3 serialChk.py 50
    s.run(int(sys.argv[1]))
    print("done.")

