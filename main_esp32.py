"""
This test code was written in Micropython (loboris port) to assess the serial connection with a esp32 device.
Tested on Espressif DevKitC devboard with ESP32-WROVER-I.

author: aminhb@tutanota.com
"""
import sys
from utime import sleep
import ujson as json
from machine import stdin_get, stdout_put

class Clear:
    def __repr__(self):
        return "\x1b[2J\x1b[H"
    def __call__(self):
        return self.__repr__()

class Astroid:
    """Generates a list of coordinates for the astroid plot."""
    def list_generator(self, iterations=10):
        n = iterations
        response = ({'header': 'test'})
        response.update({'body': [[(i, 0), (0, abs(abs(i) - n)), (0, -(abs(abs(i) - n)))] for i in range(-n, n + 1)]})
        jsnd_response = json.dumps(response)
        return jsnd_response

class SerialHandler:
    """Handles the commands/responses over serial."""
    def __init__(self):
        self.clear = Clear()
        self.seg_size = 1024
        self.read, self.signal, self.content = '', '', ''

    def read_until(self, ending, timeout=10000):
        self.read = stdin_get(1, timeout)
        if self.read is None:
            return '\n'

        timeout_count = 0
        while True:
            if self.read is not None:
                if self.read.endswith(ending):
                    break
                else:
                    new_data = stdin_get(1, timeout)
                    self.read += new_data
                    timeout_count = 0
            else:
                timeout_count += 1
                if timeout is not None and timeout_count >= timeout:
                    break
        return self.read

    def sender(self, response):
        """Sends the response back over serial."""
        self.clear()
        def chopper(cmd):
            data = []
            segments = [cmd[i:i + self.seg_size] for i in range(0, len(cmd), self.seg_size)]
            for idx, segment in enumerate(segments, start=1):
                if segment == segments[-1]:
                    data.append(segment + '*#')
                else:
                    data.append(segment + '<{}/{}>_#'.format(idx, len(segments)))
            return data
        if len(response) > self.seg_size:
            for data in ([chunk for chunk in chopper(response)]):
                for _ in range(3):
                    stdout_put(data)
                    sleep(0.125) # 0.1
                    resp = self.read_until('#', 5000)
                    if 'EOF received.' in resp:
                        sleep(0.002)
                        return '\nresponse was sent, exiting the sender, chopper involved.'
                    elif 'got it.' in resp:
                        sleep(0.002)
                        break
                    else:
                        sleep(0.125) #0.5
        else:
            for _ in range(3):
                stdout_put(response + "*#")
                sleep(0.125) #1
                resp = self.read_until('#', 5000)
                if 'EOF received.' in resp:
                    sleep(0.002)
                    return '\nresponse was sent, exiting the sender, no chopper involved.'
                else:
                    sleep(0.125) # 1
        return '\nsender: done.'

    def receiver(self):
        """Receives the commands over serial.
        type !# to exit.
        """
        self.clear
        self.content, self.signal = '', ''
        
        while True:
            while 'go#' not in self.signal and '!#' not in self.signal:
                stdout_put('receiver: READY\n')
                sleep(1) # 2
                self.signal = self.read_until('#')
            if '!#' in self.signal:
                print('receiver: aborted!')
                sys.exit(0)
            else:
                stdout_put('got it.\n')
                self.clear()
                self.signal = ''
            while '*' not in self.content:
                try:
                    sleep(0.125)
                    data = self.read_until('#')
                    if '#' in data and data[:-2] not in self.content:
                        if data[-2] == '*':
                            self.content += data[:-1]
                            break
                        elif data[-2] == '_':
                            self.content += data[:-2]
                            stdout_put('got it.\n')
                            sleep(0.125)
                        else:
                            sleep(0.125) # 1
                    else:
                        sleep(0.125) # 1 
                except Exception as e:
                    print(e)
                    break
            sleep(0.25) # 1
            if '*' in self.content:
                stdout_put('EOF received.\n')
                sleep(1) # 2
                raw_cmd = eval(self.content[:-1])
                if raw_cmd['header'] == 'test':
                    astroid = Astroid().list_generator(raw_cmd['body']['it'])
                    self.sender(astroid)
                else:
                    return "operator: invalid command."
                self.receiver()

        return "receiver: done."

if __name__ == '__main__':
    from upysh import * # comment this out if upysh has not been implemented in the firmware modules.
    Clear()
    s = SerialHandler()
    s.receiver()
