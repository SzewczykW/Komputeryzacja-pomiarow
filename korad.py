from koradserial import KoradSerial
from simple_pid import PID
from time import sleep

__MAX_VOLTAGE = 30.00

class MagneticFieldDriver:
    def __init__(serial_port: str, channel: int, memory: int):
        self.serial_port = serial_port
        self.channel = channel
        self.memory = memory
        self.tesla = 0.0

    def run():
        pid = PID(5, 0.01, 0.1, setpoint=tesla)
        pid.output_limits = (0, 0.4)
        
    def update(self, current, dt):
        if current > 0:
            # Boiler can only produce heat, not cold
            self.tesla += 1 * current * dt

        # Some heat dissipation
        self.tesla -= 0.02 * dt
        return self.tesla

    def set_magnetic_field(tesla: float) -> None:
        with KoradSerial(self.serial_port) as pwr:
            channel = pwr.channels[self.channel]
            m1 = pwr.memories[self.memory]

            m1.recall()
            channel.voltage = __MAX_VOLTAGE
            channel.current = amp
            m1.save()
