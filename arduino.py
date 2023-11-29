from PyQt6.QtCore import QThread, pyqtSignal
import serial
import time

class ArduinoThread(QThread):
    finished_signal = pyqtSignal(str)

    def __init__(self, port, input_config_eletrov1, input_config_eletrov2, input_controlador_debito, input_controlador_pressao, main_class):
        super().__init__()
        self.port = port
        self.input_config_eletrov1 = input_config_eletrov1
        self.input_config_eletrov2 = input_config_eletrov2
        self.input_controlador_debito = input_controlador_debito
        self.input_controlador_pressao = input_controlador_pressao
        self.main_class = main_class

    def run(self):
        #print('111111')
        #try:
        #print('aqui1')
        arduino = serial.Serial(self.port, 9600)
        #time.sleep(2)  # Aguarda a inicialização do Arduino

        message_arduino = f"{self.main_class.config_eletrov1_value};{self.main_class.config_eletrov2_value};{self.main_class.input_controlador_pressao};{self.main_class.input_controlador_debito}"


        print(self.main_class.input_controlador_pressao)
        print(self.main_class.input_controlador_debito)
        print(self.main_class.config_eletrov1_value)
        print(self.main_class.config_eletrov2_value)
        #print()

        #print('aqui3')
        arduino.write(message_arduino.encode())


        #print('aqui4')
        #answer_arduino = arduino.readline().decode().strip()
        
        #print(f"Arduino says: {answer_arduino}")

        arduino.close()
        #self.finished_signal.emit("Comunicação bem-sucedida!")
        #print('deu certo')
        # except Exception as e:
        #     self.finished_signal.emit(f"Erro: {str(e)}")
        #     print('nao foi')
