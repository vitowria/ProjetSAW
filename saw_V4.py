import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget
)
from PyQt6.QtGui import QFont
import time
import os
import pyqtgraph as pg
import propar
from analyseur_reseauV2 import (FieldFox)
from analyseur_reseauV2 import MyApp as AffichageAR
import serial
import pandas as pd
import serial.tools.list_ports


def list_serial_devices():
    devices = []
    for port in serial.tools.list_ports.comports():
        devices.append({
            'device': port.device,
            'name': port.name,
            'description': port.description,
            'hwid': port.hwid,
                # Uncomment if you need to match by VID:PID
                # 'vid': port.vid,
                # 'pid': port.pid,
            })
        return devices

def find_com_port(expected_description):
    for device in list_serial_devices():
        if expected_description in device['description']:
            return device['device']
    return None        

class MyApp(QMainWindow):

    def create_label(self, text, font_size=10):
        label = QLabel(text)
        font = label.font()
        font.setPointSize(font_size)
        label.setFont(font)
        return label

    def create_button(self, text, on_click=None, background_color=None):
        button = QPushButton(text)
        if on_click:
            button.clicked.connect(on_click)
        if background_color:
            button.setStyleSheet(f"background-color: {background_color};")
        return button
    
    def create_line_edit(self, placeholder_text=''):
        #create_label(placeholder_text)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)
        return line_edit
    


    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("")
        self.setGeometry(200, 200, 1200, 1000)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()

        try:
            self.fox = FieldFox()
        except ValueError as e:
            error_message = "Error: Can't find the FieldFox.\n Error's detail: " + str(e)
            QMessageBox.critical(self, "Error", error_message)

        # Example of refactored UI setup
        left_layout = QVBoxLayout()

        # Using the helper function to create a label
        label_ARconfiguracoes = self.create_label("Network Analyzer's Configurations", font_size=16)
        left_layout.addWidget(label_ARconfiguracoes)

        # Simplified QLineEdit creation
        left_layout.addWidget(self.create_label('Enter center frequency'))
        self.input_AR_entry1 = self.create_line_edit("")
        left_layout.addWidget(self.input_AR_entry1)

        left_layout.addWidget(self.create_label('\nS-parameter\n    [S11,S12,S21,S22] :'))
        self.input_AR_entry9 = self.create_line_edit("")
        left_layout.addWidget(self.input_AR_entry9)

        left_layout.addWidget(self.create_label('Span [Hz] :'))
        self.input_AR_entry2 = self.create_line_edit("")
        left_layout.addWidget(self.input_AR_entry2)

        left_layout.addWidget(self.create_label('Bandwidth [Hz]\n      [10,100,1000,10000,100000] :\n'))
        self.input_AR_entry3 = self.create_line_edit("")
        left_layout.addWidget(self.input_AR_entry3)

        left_layout.addWidget(self.create_label('Average measurement :\n'))
        self.input_AR_entry4 = self.create_line_edit("")
        left_layout.addWidget(self.input_AR_entry4)

        # Simplified QPushButton creation
        self.button1 = self.create_button("Initialization of the network analyzer", self.initialize, "#33b2ff")
        left_layout.addWidget(self.button1)

        left_layout.addWidget(self.create_label('Target frequency [Hz] :\n'))
        self.input_AR_entry5 = self.create_line_edit("Target frequency [Hz] :\n")
        left_layout.addWidget(self.input_AR_entry5)

        # Simplified QPushButton creation
        self.button2 = self.create_button("Spectrum normalization", self.spectrum_normalization, "#33b2ff")
        left_layout.addWidget(self.button2)

        # Simplified QPushButton creation
        self.button3 = self.create_button("Amplitude normalization", self.amplitude_normalization, "#33b2ff")
        left_layout.addWidget(self.button3)

        self.input_AR_entry6 = self.create_line_edit("File name for the complete graph :")
        left_layout.addWidget(self.input_AR_entry6)

        self.input_AR_entry7 = self.create_line_edit("File name for the target frequency :")
        left_layout.addWidget(self.input_AR_entry7)

        self.input_AR_entry8 = self.create_line_edit("File name for the normalization graph :")
        left_layout.addWidget(self.input_AR_entry8)

        # Simplified QPushButton creation
        self.button4 = self.create_button("Plot the graphs", self.plot_graphs, "#33b2ff")
        left_layout.addWidget(self.button4)

        label_0 = QLabel(" ")
        left_layout.addWidget(label_0)
        layout.addLayout(left_layout)

        center_layout = QVBoxLayout()
        

        # Configurations electrovannes

        label_EVconfigurations = self.create_label("Electrovanne's Configurations", font_size=16)
        center_layout.addWidget(label_EVconfigurations)
  
        center_layout.addWidget(self.create_label("Final Concentration [mol/L]"))
        self.input_config_eletrov1 = self.create_line_edit("")
        center_layout.addWidget(self.input_config_eletrov1)

        center_layout.addWidget(self.create_label("Initial Concentration [mol/L]"))
        self.input_config_eletrov2 = self.create_line_edit("")
        center_layout.addWidget(self.input_config_eletrov2)
        

        # Débit controler
        label_debit = self.create_label("Flow controler", font_size=16)
        center_layout.addWidget(label_debit)

        center_layout.addWidget(self.create_label("Flux [ml/s]"))
        self.input_controlador_debito = self.create_line_edit("")
        center_layout.addWidget(self.input_controlador_debito)
        
        # Pression controler
        label_pression = self.create_label("Pression Controler", font_size=16)
        center_layout.addWidget(label_pression)

        center_layout.addWidget(self.create_label("Pression [bar]"))
        self.input_controlador_pressao = self.create_line_edit("")
        center_layout.addWidget(self.input_controlador_pressao)
    
        center_layout.addWidget(label_0)


        # Buttons
        self.button5 = self.create_button("Start", self.InitControlers, "#background-color: green")
        center_layout.addWidget(self.button5)

        self.button6 = self.create_button("Stop", self.stop_button, "#background-color: red")
        center_layout.addWidget(self.button6)

        layout.addLayout(center_layout)

        
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

        alarm_layout = QVBoxLayout()
        layout.addLayout(alarm_layout)

        label_alarm1 = QLabel("Banana")
        alarm_layout.addWidget(label_alarm1)

        self.table_widget1 = QTableWidget(2, 2)
        alarm_layout.addWidget(self.table_widget1)
        
        self.table_widget1.setColumnWidth(0, 70)
        self.table_widget1.setColumnWidth(1, 70)
        
        self.table_widget1.setHorizontalHeaderLabels(["Amplitude", "Phase"])
        self.table_widget1.setVerticalHeaderLabels(["Old","Young"])



        label_alarm2 = QLabel("Apple")
        alarm_layout.addWidget(label_alarm2)

        self.table_widget2 = QTableWidget(2, 2)
        alarm_layout.addWidget(self.table_widget2)
        
        self.table_widget2.setColumnWidth(0, 70)
        self.table_widget2.setColumnWidth(1, 70)
        
        self.table_widget2.setHorizontalHeaderLabels(["Amplitude", "Phase"])
        self.table_widget2.setVerticalHeaderLabels(["Old","Young"])


        central_widget.setLayout(layout)

       
    
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

        self.debit_pression()
        self.InitArduino()
  

    def InitArduino(self):
        # initialize the eletrovannes
        self.config_eletrov1_value = self.input_config_eletrov1.text()
        self.config_eletrov2_value = self.input_config_eletrov2.text()
        self.controlador_debito_value = self.input_controlador_debito.text()
        self.controlador_pressao_value = self.input_controlador_pressao.text()

        port = '/dev/tty.usbmodem1424401'

        ard = serial.Serial(port, 9600)
        ard.write(f'{self.config_eletrov1_value};{self.config_eletrov2_value};'.encode())



    def debit_pression(self):
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

  
    def initialize(self):
        center_freq = self.input_AR_entry1.text()
        span = self.input_AR_entry2.text()
        bandwidth = self.input_AR_entry3.text()
        averages = self.input_AR_entry4.text()
        coefficient = self.input_AR_entry9.text()

        # Debugging: Print the values to verify they are not empty
        print(f"Center Frequency: {center_freq}")
        print(f"Span: {span}")
        print(f"Bandwidth: {bandwidth}")
        print(f"Averages: {averages}")
        print(f"Coefficient: {coefficient}")

        try:
            center_freq = float(center_freq)
            span = float(span)
            bandwidth = float(bandwidth)
            averages = int(averages)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values (bandwitdh, span, center frequency, averages ).")
            return

        self.fox.initialize(center_freq, span, bandwidth, averages, coefficient)
    
    def spectrum_normalization(self):
        center_freq_text = self.input_AR_entry1.text()
        span_text = self.input_AR_entry2.text()
        bandwidth_text = self.input_AR_entry3.text()
        averages_text = self.input_AR_entry4.text()
        coefficient_text = self.input_AR_entry9.text()
    
        self.fox.initialize(center_freq_text, span_text, bandwidth_text, averages_text, coefficient_text)

        data_normalization_spectrum = self.fox.get_data_normalisation_spectrum()
        if data_normalization_spectrum is not None:
            print("Normalization Complete\n", "Spectrum normalization is complete.")
        else:
            self.show_warning("Normalization Error", "Failed to perform spectrum normalization.")

    def amplitude_normalization(self):
        self.initialize()
        data_normalisation_amplitude = self.fox.get_data_normalisation_amplitude()
        if data_normalisation_amplitude is not None:
            print("Amplitude Complete\n" "Spectrum amplitude is complete.")
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
