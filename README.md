# Serial Check
This test code was written in Micropython (v1.17) to assess the serial connection with stm32/esp32 devices.
Tested on WeActStudios F411CE devboard with STM32F411CE and ESP32-WROVER devkitC boards.<br />

## Requirements
- matplotlib==3.5.0
- pyserial==3.5

## Usage
- Depending on the board you use, rename either the main_esp32.py or main_stm32.py to main.py and transfer the file to the board.<br />
- On your system open a terminal and enter `python3 serialChk.py 20`
<br />

Note: The value passed as an argument will be used to generate a list of coordinates associated with an astroid-graph on the microcontroller as a data-sample and the list will be returned over serial connection to be plotted. The larger the argument the larger list, hence a larger file, will be generated.<br />
The algorithm establishes a handshake to ensure the integrity of the data being transferred over serial to/from the microcontroller.

## License
[MIT License](https://opensource.org/licenses/MIT)
