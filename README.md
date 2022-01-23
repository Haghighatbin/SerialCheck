# Serial Check
This test code was written in Micropython (v1.17) to assess the serial connection with stm32/esp32 devices.
Tested on WeActStudios F411CE devboard with STM32F411CE and ESP32-WROVER devkitC boards.<br />
author: aminhb@tutanota.com

## Requirements
- matplotlib==3.5.0
- pyserial==3.5

## Usage
- Depending on the board you use, rename either the main_esp32.py or main_stm32.py to main.py and copy to your board.<br />
- On your system open a terminal and enter: python3 serialChk.py 50<br />
Note: The number pass as an argument will be used to generate a list of coordinates of an astroid on the microcontroller as a data-sample and the list will be returned to be printed.<br />
The algorithm will use some kind of a handshake protocol to ensure the validity of the data being transferred.

## License
[MIT License](https://opensource.org/licenses/MIT)
