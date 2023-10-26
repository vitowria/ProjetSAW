import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtGui import QFont
import time
import os
import pyqtgraph as pg
import propar
import pyfirmata

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_eletrov1_value = None
        self.config_eletrov2_value = None
        self.controlador_debito_value = None
        self.controlador_pressao_value = None

        self.setWindowTitle("Trouver une title")
        self.setGeometry(100, 100, 1000, 400)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout()

        # Coloca duas colunas -> esquerda
        left_layout = QVBoxLayout()

        # Configurations des electrovannes
        label_configuracoes = QLabel("Configurations Electrovannes")
        left_layout.addWidget(label_configuracoes)
        fonte_grande = QFont()
        fonte_grande.setPointSize(16)
        label_configuracoes.setFont(fonte_grande)

        label_electrovannes1 = QLabel("Concentration finale (ppm)")
        left_layout.addWidget(label_electrovannes1)
        self.input_config_eletrov1 = QLineEdit()
        left_layout.addWidget(self.input_config_eletrov1)
        
        label_electrovannes2 = QLabel("Concentration initale (ppm)")
        left_layout.addWidget(label_electrovannes2)
        self.input_config_eletrov2 = QLineEdit()
        left_layout.addWidget(self.input_config_eletrov2)

        # Contrôleur de Débit
        label_debito = QLabel("Contrôleur de Débit")
        left_layout.addWidget(label_debito)
        fonte_grande = QFont()
        fonte_grande.setPointSize(16)
        label_debito.setFont(fonte_grande)

        label_debit1 = QLabel("Débit (ml/min)")
        left_layout.addWidget(label_debit1)

        self.input_controlador_debito = QLineEdit()
        left_layout.addWidget(self.input_controlador_debito)

        # Contrôleur de Pression
        label_pressao = QLabel("Contrôleur de Pression")
        left_layout.addWidget(label_pressao)
        fonte_grande = QFont()
        fonte_grande.setPointSize(16)
        label_pressao.setFont(fonte_grande)

        label_pressao1 = QLabel("Pression (atm)")
        left_layout.addWidget(label_pressao1)

        self.input_controlador_pressao = QLineEdit()
        left_layout.addWidget(self.input_controlador_pressao)

        # Buttons
        self.start_button = QPushButton("Démarrer")
        self.start_button.setStyleSheet("background-color: green;")
        left_layout.addWidget(self.start_button)
        self.start_button.clicked.connect(self.demarrer)

        self.stop_button = QPushButton("Arreter")
        self.stop_button.setStyleSheet("background-color: red;")
        left_layout.addWidget(self.stop_button)

        self.ar_button = QPushButton("AR")
        self.ar_button.setStyleSheet("background-color: blue;")
        left_layout.addWidget(self.ar_button)
        self.ar_button.clicked.connect(self.analiseur)

        layout.addLayout(left_layout)

        # Layout graphes -> droit
        right_layout = QVBoxLayout()
        
        #######(Não é tempo real ainda)
        # Graph 1
        self.plot_widget1 = pg.PlotWidget(title="Amplitude")
        right_layout.addWidget(self.plot_widget1)
        self.plot1 = self.plot_widget1.plot(pen=pg.mkPen('b', width=2))
        self.plot_data1 = []

        # Graph 2 
        self.plot_widget2 = pg.PlotWidget(title="Phase")
        right_layout.addWidget(self.plot_widget2)
        self.plot2 = self.plot_widget2.plot(pen=pg.mkPen('r', width=2))
        self.plot_data2 = []

        layout.addLayout(right_layout)

        central_widget.setLayout(layout)

    

    def demarrer(self):
        # os valores das entradas e armazenados nas variáveis
        self.config_eletrov1_value = self.input_config_eletrov1.text()
        self.config_eletrov2_value = self.input_config_eletrov2.text()
        self.controlador_debito_value = self.input_controlador_debito.text()
        self.controlador_pressao_value = self.input_controlador_pressao.text()

        # Verificação dos numeros reais
        if not self.is_real_number(self.config_eletrov1_value) or not self.is_real_number(self.config_eletrov2_value) or \
                not self.is_real_number(self.controlador_debito_value) or not self.is_real_number(self.controlador_pressao_value):
            self.show_warning("Saissi incorrecte", "Metez des nombres réeles.")
            return
        
        print("Configurations Electrovannes:", self.config_eletrov1_value, self.config_eletrov2_value)
        print("Contrôleur Débit:", self.controlador_debito_value)
        print("Contrôleur de Pression:", self.controlador_pressao_value)

        # Chama as funções
        #self.eletrovannes()
        self.debit(int(self.controlador_debito_value))
        self.pression()
        #self.analiseur()

    def InitArduino(self):
        import serial
    
        porta_serial = '/dev/cu.usbmodem14101' 
        arduino = serial.Serial(porta_serial, 9600)

        # período pra que a conexão seja estabelecida
        time.sleep(2)
        variavel1 = self.config_eletrov1_value 
        variavel2 = self.config_eletrov2_value
        # Abre o arquivo com o código do Arduino que você deseja carregar
        with open('Dillution_puls', 'r') as arquivo:
            codigo_arduino = arquivo.read()

        codigo_arduino = codigo_arduino.replace("{{variavel1}}", variavel1)
        codigo_arduino = codigo_arduino.replace("{{variavel2}}", variavel2)

        # Envie o código para o Arduino
        arduino.write(codigo_arduino.encode())

        # Aguarde o Arduino processar o código (você pode ajustar esse tempo de acordo com o seu código)
        #time.sleep(10)
        #arduino.close()


    def eletrovannes(self):
        #print("Fonction Eletrovannes Test")
        HIGH = True
        LOW = False

        port = '/dev/cu.usbmodem1414401'  # Port sur lequel est branché la carte arduino
        carte = pyfirmata.Arduino(port)
        Valve1 = carte.get_pin('d:9:o')
        Valve2 = carte.get_pin('d:11:o')
        Valve3 = carte.get_pin('d:12:o')

        n = float(self.config_eletrov1_value)  # nombre à revoir®
        m = float(self.config_eletrov2_value)  # à revoir aussi

        for i in range(int(n)):
            for j in range(int(m)):
                # gaz
                Valve1.write(LOW)
                Valve2.write(HIGH)
                Valve3.write(HIGH)
                time.sleep(1)
                # air
                Valve1.write(LOW)
                Valve2.write(HIGH)
                Valve3.write(LOW)
                time.sleep(1)

        # Nettoyage
        Valve1.write(LOW)
        Valve2.write(LOW)
        Valve3.write(LOW)
        time.sleep(180)

    def debit(self, controlador_debito_value):
        # Prends le valeur donné par l'utilisateurs sur l'interface 
        v_debit = float(controlador_debito_value) 
    
        # Connexion au contrôleur de débit (par défaut channel=1), ajuster le port COM
        instrument = propar.instrument('/dev/tty.usbserial-1410', channel=1)

        # Mettre le paramètre 12 à 0 pour contrôler par le bus RS232
        instrument.writeParameter(12, 0)

        # Moduler la valeur du débit entre 0 et 32000 (0 - 100%)
        instrument.writeParameter(9, int(v_debit))
        # Verification de la valeur envoyée précédemment
        print(instrument.readParameter(9))
    
    def pression(self):
        # Prends le valeur donné par l'utilisateurs sur l'interface 
        v_pression = float(self.controlador_pressao_value) 
        # Connexion au contrôleur de débit (par défaut channel=1), ajuster le port COM
        instrument = propar.instrument('/dev/tty.usbserial-1410', channel=1)

        # Mettre le paramètre 12 à 0 pour contrôler par le bus RS232
        instrument.writeParameter(12, 0)

        # Moduler la valeur du débit entre 0 et 32000 (0 - 100%)
        instrument.writeParameter(9, int(v_pression))
        # Verification de la valeur envoyée précédemment
        print(instrument.readParameter(9))

    def analiseur(self):
        cmd3 = 'python3 analyseur_reseau.py'
        os.system(cmd3)
        print("Configurations Electrovannes:", self.config_eletrov1_value, self.config_eletrov2_value)
        print("Contrôleur Débit:", self.controlador_debito_value)
        print("Contrôleur de Pression:", self.controlador_pressao_value)

    def is_real_number(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def show_warning(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
