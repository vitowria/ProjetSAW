import serial
import binascii
import threading

class Arduino:

    porta = None
    mySerial = None
    value = None
    stopFlag = False

    def __init__(self, porta='COM1', baud_rate=9600):
        self.porta = porta
        self.baud_rate = baud_rate
        self.mySerial = serial.Serial(porta, baud_rate, timeout=0)
        self.value = None
        self.stopFlag = False
    
    def empty_buffer(self):
        msg = "Vazio"
        while msg!=b'':
            msg = self.mySerial.read()
    
    def start(self):
        self.thread = threading.Thread(target=self.read)
        self.thread.start()
    
    def stop(self):
        self.stopFlag = True

    def read(self):
        total = ""
        while self.stopFlag==False:
            try:
                readBytes = self.mySerial.read()
                msg = binascii.hexlify(readBytes)
                msg = msg.decode('utf-8')
                bytes_object = bytes.fromhex(msg)
                ascii_string = bytes_object.decode("ASCII")
                if ';' in ascii_string:
                    self.value = total
                    total=''
                else:
                    total += ascii_string
            except:
                pass
        return total
