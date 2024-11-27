import serial

from koradserial import KoradSerial
from simple_pid import PID
from time import sleep

__MAX_VOLTAGE = 30.00


class MagneticFieldDriver:
    def __init__(
        serial_port_write: str, serial_port_read: str, channel: int, memory: int
    ):
        self._ser_read = serial.Serial(port=serial_port, baudrate=115200)
        self._serial_port_write = serial_port_write
        self._channel = channel
        self._memory = memory
        self._amps = 0.0

    @property
    def amps(self) -> float:
        return self._amps

    @amps.setter
    def amps(self, new_amps: float) -> None:
        if new_amps > 5.0 or new_amps < 0.0:
            raise ValueError("Out of range values for Korad.")
        self._amps = new_amps

    def set_magnetic_field_value(self) -> None:
        with KoradSerial(self._serial_port_write) as pwr:
            channel = pwr.channels[self._channel]
            m1 = pwr.memories[self._memory]

            m1.recall()
            channel.voltage = __MAX_VOLTAGE
            channel.current = self._amps
            m1.save()

    def get_magnetic_field_value(self) -> int:
        self._ser_read.reset_input_buffer()

        while True:
            if ser.in_waiting:
                try:
                    line = ser.readline().decode("utf-8").strip()
                    return int(line)
                except serial.SerialException as e:
                    print(f"Serial port error: {e}")
                    return None
                except UnicodeDecodeError as e:
                    print(f"Decoding error: {e}")
                    pass
                except ValueError as e:
                    print(f"Invalid data received: {e}")
                    pass
            time.sleep(0.01)
