import serial
import time

# Define supported commands
HANDSHAKE_CODE = '512'
START_SMOOTH = '127'
STOP_SMOOTH = '128'
QUERY = '129'
START_HARSH = '130'
STOP_HARSH = '131'
SET_LOW = '1024'
SET_HIGH = '2048'
MAX_CURRENT_TARGET = 5.0

class TDCS_Connection:

    def __init__(self):
        self.arduino = None

    def set_target(self, value):
        """
        Sets target current for arduino
        The target current is quantized into 1024 buckets (0...10mA) and the id of the bucket is sent to the arduino
        :param value:
        :return: True, if value is within the supported range, False, otherwise
        """
        if 0 <= value <= MAX_CURRENT_TARGET:
            quant = str(1024 + int(value*1024/MAX_CURRENT_TARGET))
            self.arduino.write(quant.encode())
            self.arduino.write('\n')
            return True
        else:
            return False

    def start_tdcs(self, smooth=False):
        """
        Starts the tdcs procedure
        :param smooth:
        :return:
        """
        if smooth:
            self.arduino.write(START_SMOOTH)
        else:
            self.arduino.write(START_HARSH)
        self.arduino.write('\n')

    def stop_tdcs(self, smooth=True):
        """
        Stops the tdcs procedure
        :param smooth:
        :return:
        """
        global arduino
        if smooth:
            self.arduino.write(STOP_SMOOTH)
        else:
            self.arduino.write(STOP_HARSH)
        self.arduino.write('\n')

    def connect(self, port='/dev/ttyUSB0'):
        """
        Connects to arduino and handshakes
        :param port:
        :return:
        """
        try:
            self.arduino = serial.Serial(port, 9600)
            # Allow time for arduino reset and initialization
            time.sleep(2)
            self.arduino.write(HANDSHAKE_CODE)
            answer = self.arduino.readline()[:2]
            return answer == "OK"
        except:
            return False

    def is_arduino_available(self):
        """
        Returns true if a connection to arduino has been established
        :return:
        """
        return self.arduino is not None

    def get_status(self):
        """
        Queries the arduino and gets its status
        :return: (voltage, current, resistance, potentiometer value)
        """
        self.arduino.write(QUERY)
        self.arduino.write('\n')

        voltage = float(self.arduino.readline())
        current = float(self.arduino.readline())
        resistance = float(self.arduino.readline())
        potentiometer = float(self.arduino.readline())

        return voltage, current, resistance, potentiometer

