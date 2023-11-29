#mets le temps total, elever le concentration initial

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtGui import QFont
import time
import os
import pyqtgraph as pg
import propar
from analyseur_reseauV2 import (FieldFox)
from analyseur_reseauV2 import MyApp as AffichageAR
from arduino import ArduinoThread
import serial
#import pyserial
#from PyQt6.QtCore import QCoreApplication

def InitPropar():
        cmd2 = 'pip install bronkhorst-propar'
        os.system(cmd2)

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Find a title")
        self.setGeometry(200, 200, 1200, 800)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        

    
        try:
            self.fox = FieldFox()
        except ValueError as e:
            error_message = "Error: Can't find the FieldFox.\n Error's detail: " + str(e)
            QMessageBox.critical(self, "Error", error_message)
            #error_message = QLabel("Erro: O dispositivo FieldFox não foi encontrado.", self)
            #error_label.move(100, 50)
        layout = QHBoxLayout()

        # Put 3 rows -> left
        left_layout = QVBoxLayout()

        #Defines font
        fonte_grande = QFont()
        fonte_grande.setPointSize(16)

        #Configurations Analyseur de Reseau
        label_ARconfiguracoes = QLabel("Network Analyzer's Configurations ")
        left_layout.addWidget(label_ARconfiguracoes)
        label_ARconfiguracoes.setFont(fonte_grande)
        layout.addLayout(left_layout)

        label_ar9 = QLabel("\nS-parameter\n    [S11,S12,S21,S22] :")
        left_layout.addWidget(label_ar9)
        self.input_AR_entry9 = QLineEdit()
        left_layout.addWidget(self.input_AR_entry9)

        label_ar1 = QLabel("Center frequency [Hz] :")
        left_layout.addWidget(label_ar1)
        self.input_AR_entry1 = QLineEdit()
        left_layout.addWidget(self.input_AR_entry1)

        label_ar2 = QLabel("Span [Hz] :")
        left_layout.addWidget(label_ar2)
        self.input_AR_entry2 = QLineEdit()
        left_layout.addWidget(self.input_AR_entry2)

        label_ar3 = QLabel("Bandwidth [Hz]\n      [10,100,1000,10000,100000] :\n")
        left_layout.addWidget(label_ar3)
        self.input_AR_entry3 = QLineEdit()
        left_layout.addWidget(self.input_AR_entry3)

        label_ar4 = QLabel("Average measurement :\n")
        left_layout.addWidget(label_ar4)
        self.input_AR_entry4 = QLineEdit()
        left_layout.addWidget(self.input_AR_entry4)
        
        #Button of AR
        self.button1 = QPushButton("Initialization of the network analyzer")
        self.button1.setStyleSheet("background-color:  #33b2ff;")
        left_layout.addWidget(self.button1)
        self.button1.clicked.connect(self.initialize_fieldfox)

        label_ar5 = QLabel("Target frequency [Hz] :\n")
        left_layout.addWidget(label_ar5)
        self.input_AR_entry5 = QLineEdit()
        left_layout.addWidget(self.input_AR_entry5)
        
        #Button of AR
        button_spectrum_normalization = QPushButton("Spectrum normalization")
        button_spectrum_normalization.setStyleSheet("background-color: #33b2ff")
        left_layout.addWidget(button_spectrum_normalization)
        button_spectrum_normalization.clicked.connect(self.spectrum_normalization)
        
        #Button of AR
        self.button4 = QPushButton("Amplitude normalization")
        self.button4.setStyleSheet("background-color:  #33b2ff;")
        left_layout.addWidget(self.button4)
        self.button4.clicked.connect(self.amplitude_normalization)

        label_ar6 = QLabel("File name for the complete graph :")
        left_layout.addWidget(label_ar6)
        self.input_AR_entry6 = QLineEdit()
        left_layout.addWidget(self.input_AR_entry6)

        label_ar7 = QLabel("File name for the target frequency :")
        left_layout.addWidget(label_ar7)
        self.input_AR_entry7 = QLineEdit()
        left_layout.addWidget(self.input_AR_entry7)

        label_ar8 = QLabel("File name for the normalization graph :")
        left_layout.addWidget(label_ar8)
        self.input_AR_entry8 = QLineEdit()
        left_layout.addWidget(self.input_AR_entry8)
        
        label_0 = QLabel(" ")
        left_layout.addWidget(label_0)
        
        #Button of AR       
        self.button2 = QPushButton("Plot the graph")
        self.button2.setStyleSheet("background-color:  #33b2ff;")
        left_layout.addWidget(self.button2)
        self.button2.clicked.connect(self.plot_graphs)
       


        center_layout = QVBoxLayout()
        
        # Configurations electrovannes
        label_configuracoes = QLabel("Electrovanne's Configurations")
        center_layout.addWidget(label_configuracoes)

        label_configuracoes.setFont(fonte_grande)

        label_electrovannes1 = QLabel("Final Concentration [ppm]")
        center_layout.addWidget(label_electrovannes1)
        self.input_config_eletrov1 = QLineEdit()
        center_layout.addWidget(self.input_config_eletrov1)
        
        label_electrovannes2 = QLabel("Total time [sec]")
        center_layout.addWidget(label_electrovannes2)
        self.input_config_eletrov2 = QLineEdit()
        center_layout.addWidget(self.input_config_eletrov2)

        # Débit controler
        label_debito = QLabel("Flow controler")
        center_layout.addWidget(label_debito)
        fonte_grande = QFont()
        fonte_grande.setPointSize(16)
        label_debito.setFont(fonte_grande)

        label_debit1 = QLabel("Flux [ml/min]")
        center_layout.addWidget(label_debit1)

        self.input_controlador_debito = QLineEdit()
        center_layout.addWidget(self.input_controlador_debito)

        # Pression controler
        label_pressao = QLabel("Pression Controler")
        center_layout.addWidget(label_pressao)
        fonte_grande = QFont()
        fonte_grande.setPointSize(16)
        label_pressao.setFont(fonte_grande)

        label_pressao1 = QLabel("Pression [atm]")
        center_layout.addWidget(label_pressao1)

        self.input_controlador_pressao = QLineEdit()
        center_layout.addWidget(self.input_controlador_pressao)
    
        center_layout.addWidget(label_0)
        # Buttons
        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet("background-color: green;")
        center_layout.addWidget(self.start_button)
        self.start_button.clicked.connect(self.InitControlers)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("background-color: red;")
        center_layout.addWidget(self.stop_button)

        layout.addLayout(center_layout)

        # Layout graphs -> right
        right_layout = QVBoxLayout()
        
        #######(not yet in real time)
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

        # Variables to store the entry values for the controlers
        self.config_eletrov1_value = None
        self.config_eletrov2_value = None
        self.controlador_debito_value = None
        self.controlador_pressao_value = None

        # Variables to store the entry values from the AR
        self.AR_entry1 = None
        self.AR_entry2 = None
        self.AR_entry3 = None
        self.AR_entry4 = None
        self.AR_entry5 = None
        self.AR_entry6 = None
        self.AR_entry7 = None
        self.AR_entry8 = None
        self.AR_entry9 = None

       
    
    def InitControlers(self):
        

        #variables to save the entry values for the controlers and arduino

        self.config_eletrov1_value = self.input_config_eletrov1.text()
        self.config_eletrov2_value = self.input_config_eletrov2.text()
        self.controlador_debito_value = self.input_controlador_debito.text()
        self.controlador_pressao_value = self.input_controlador_pressao.text()

        #variables to save the entry values for the AR
        self.AR_entry1 = self.input_AR_entry1.text()
        self.AR_entry2 = self.input_AR_entry2.text()
        self.AR_entry3 = self.input_AR_entry3.text()
        self.AR_entry4 = self.input_AR_entry4.text()
        self.AR_entry5 = self.input_AR_entry5.text()
        self.AR_entry6 = self.input_AR_entry6.text()
        self.AR_entry7 = self.input_AR_entry7.text()
        self.AR_entry8 = self.input_AR_entry8.text()
        self.AR_entry9 = self.input_AR_entry9.text()

        
        # Real number verification
        #if not self.is_real_number(self.config_eletrov1_value) or not self.is_real_number(self.config_eletrov2_value) or \
        #        not self.is_real_number(self.controlador_debito_value) or not self.is_real_number(self.controlador_pressao_value):
        #    self.show_warning("Incorrect input", "Put real numbers")
        #    return
        # Verificação outra inventar

        # calls the functions
        self.InitArduino()
        self.debit_pression()

    def InitArduino(self):
        # Iniciar a thread do Arduino
        self.config_eletrov1_value = self.input_config_eletrov1.text()
        self.config_eletrov2_value = self.input_config_eletrov2.text()
        self.controlador_debito_value = self.input_controlador_debito.text()
        self.controlador_pressao_value = self.input_controlador_pressao.text()

        self.arduino_thread = ArduinoThread('/dev/cu.usbmodem14101', self.input_config_eletrov1, self.input_config_eletrov2,self.input_controlador_debito, self.input_controlador_pressao, self)
        self.arduino_thread.finished_signal.connect(self.arduino_finished) 

        self.arduino_thread.start()

    def arduino_finished(self, result):
        # Manipular o resultado (exibição, etc.)
        print('cabou')


    def debit_pression(self):
        InitPropar()
        # Prends le valeur donné par l'utilisateurs sur l'interface 
        v_debit = float(self.controlador_debito_value) 
        v_pression = float(self.controlador_pressao_value) 

        # Connexion au contrôleur de débit (par défaut channel=1), ajuster le port COM
        instrument_debit = propar.instrument('COM4', channel=1) #Changer les COM4 et COM5 en function du port USB
        instrument_pression = propar.instrument('COM5', channel=1)
        
        # Mettre le paramètre 12 à 0 pour contrôler par le bus RS232
        instrument_debit.writeParameter(12, 0)
        instrument_pression.writeParameter(12, 0)
        
        # Moduler la valeur du débit entre 0 et 32000 (0 - 100%)
        instrument_pression.writeParameter(9, int(v_pression))
        instrument_debit.writeParameter(9, int(v_debit))
        
        # Verification de la valeur envoyée précédemment
        print(instrument_pression.readParameter(9))
        print(instrument_debit.readParameter(9))
    

    def is_real_number(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def show_warning(self, title, message):
        # show error messages in the interface
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def initialize_fieldfox(self):
        self.fox.initialize(
            self.input_AR_entry1.text(),
            self.input_AR_entry2.text(),
            self.input_AR_entry3.text(),
            self.input_AR_entry4.text(),
            self.input_AR_entry9.text()
        )
    
    def spectrum_normalization(self):
        center_freq_text = self.input_AR_entry1.text()
        span_text = self.input_AR_entry2.text()
        bandwidth_text = self.input_AR_entry3.text()
        averages_text = self.input_AR_entry4.text()
        coefficient_text = self.input_AR_entry9.text()
    
        self.fox.initialize(center_freq_text, span_text, bandwidth_text, averages_text, coefficient_text)

        data_normalization_spectrum = self.fox.get_data_normalisation_spectrum()
        if data_normalization_spectrum is not None:
            self.show_info("Normalization Complete", "Spectrum normalization is complete.")
        else:
            self.show_warning("Normalization Error", "Failed to perform spectrum normalization.")

    def amplitude_normalization(self):
        self.initialize_fieldfox()
        data_normalisation_amplitude = self.fox.get_data_normalisation_amplitude()
        if data_normalisation_amplitude is not None:
            self.show_info("Amplitude Complete", "Spectrum amplitude is complete.")
        else:
            self.show_warning("Amplitude Error", "Failed to perform spectrum amplitude.")

    def plot_graphs(self):
        Frequence_text = self.input_AR_entry1.text()
        fichier_text = self.input_AR_entry6.text()
        fichier2_text = self.input_AR_entry7.text()
        fichier3_text = self.input_AR_entry8.text()

        try:
            Frequence = float(Frequence_text)
        except ValueError:
            self.show_warning("Invalid Input", "Please enter a valid numeric value for Target Frequency.")
            return
        
        self.fox.start_poller(
           Frequence_text,
           fichier_text,
           fichier2_text,
           fichier3_text 
        )


def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
