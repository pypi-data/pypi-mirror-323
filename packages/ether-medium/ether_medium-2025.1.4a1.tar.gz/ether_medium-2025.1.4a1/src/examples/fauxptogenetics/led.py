import serial
from ether import ether_sub, ether_init, ether_cleanup

class LED:

    def __init__(
            self,
            port: str,
            baudrate: int = 9600,
    ):
        self._port = port
        self._baudrate = baudrate

    @ether_init
    def setup(self):
        self._device = serial.Serial(port = self._port, baudrate = self._baudrate)

    @staticmethod
    def _format_msg(duration: int = 0, red: int = 0, green: int = 0, blue: int = 0):
        return f"{duration} {red} {green} {blue}"
    
    @ether_sub
    def trigger(self, duration: int = 0, red: int = 0, green: int = 0, blue: int = 0):
        serial_msg = self._format_msg(duration, red, green, blue)
        self._device.write(serial_msg)

    @ether_cleanup
    def close(self):
        self._device.close