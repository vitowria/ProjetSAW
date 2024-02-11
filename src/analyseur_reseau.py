import sys
import time
import pyvisa
import codecs
import csv
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import threading
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from dotenv import dotenv_values
from PyQt6.QtCore import QObject, pyqtSignal



class DataMonitor(QObject):
    warning_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.phase_variation_limit = 40  # Limite de variação de fase
        self.amplitude_variation_limit = 0.007  # Limite de variação de amplitude
        self.counter = 0  # Contador de ocorrências consecutivas
        self.initial_phase_value = None  # Valor inicial de fase
        self.initial_amplitude_value = None  # Valor inicial de amplitude

    def update_and_check(self, current_phase, current_amplitude):
        # Inicializa os valores iniciais se ainda não definidos
        if self.initial_phase_value is None or self.initial_amplitude_value is None:
            self.initial_phase_value = current_phase
            self.initial_amplitude_value = current_amplitude
            return
        
        # Calcula variações em relação aos valores iniciais
        phase_variation = abs(current_phase - self.initial_phase_value)
        amplitude_variation = abs(current_amplitude - self.initial_amplitude_value)

        # Verifica se as variações excedem os limites
        if phase_variation > self.phase_variation_limit or amplitude_variation > self.amplitude_variation_limit:
            self.counter += 1
            if self.counter >= 4:
                self.emit_warning()  # Emite o aviso
                # Não resete o contador aqui se você quiser que o aviso seja emitido
                # para cada ocorrência após as 4 iniciais
        else:
            self.counter = 0  # Reset o contador se as variações estiverem dentro dos limites

    def emit_warning(self):
        self.warning_signal.emit("Warning: Data variation exceeded limits 4 times in a row.")

class FieldFox():
    def __init__(self):
        config = dotenv_values('src/.env')
        visa_id=f"USB0::0x2A8D::0x5C18::{config['SERIAL_NETWORK_ANALYSER']}::0::INSTR"
        print("Creating FieldFox's instancy ")
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(visa_id, read_termination='\n')
        self.inst.timeout = 1000000
        self.spectrum = None
        #self.spectrum_normalisation = None 
        self.amplitude = None
        self.averages = 1
        self.frequencies = np.linspace(self.start_frequency, self.stop_frequency, self.sweep_point_number)
        self.data_monitor = DataMonitor()
        self.Frequence = 0
        self.counter = 0

    def identity(self):
        return self.inst.query("*IDN?")

    @property
    def sweep_point_number(self):
        return int(self.inst.query("SENS:SWE:POIN?"))

    @sweep_point_number.setter
    def sweep_point_number(self, point_number):
        self.inst.write(f"SENS:SWE:POIN {point_number}")

    @property
    def start_frequency(self):
        return float(self.inst.query("SENS:FREQ:START?"))

    @property
    def stop_frequency(self):
        return float(self.inst.query("SENS:FREQ:STOP?"))

    def set_analyzer_mode(self):
        self.inst.write("INST:SEL 'NA'")

    def wait_for_completed(self):
        self.inst.query("*OPC?")

    def set_continous_mode(self, mode):
        self.inst.write(f"INIT:CONT {mode}")

    def initialize(self, center_freq, span,
                   bandwidth, averages, coefficient):


        self.set_analyzer_mode()
        self.inst.write("DISP:WIND:SPL D12H")

        self.inst.write(f"CALC:PAR1:DEF {coefficient}")
        self.inst.write("CALC:PAR1:SEL")
        self.inst.write("CALC:FORMat PHASe")
        self.inst.write("DISP:WIND:TRAC1:Y:AUTO")

        self.inst.write(f"CALC:PAR2:DEF {coefficient}")
        self.inst.write("CALC:PAR2:SEL")
        self.inst.write("CALC:FORMat MLINear")
        self.inst.write("DISP:WIND:TRAC2:Y:AUTO")

        self.inst.write(f"SENS:FREQ:CENT {center_freq}")
        self.inst.write(f"SENS:FREQ:SPAN {span}")
        self.inst.write(f"BWID {bandwidth}")
        self.inst.write(f"AVER:COUNt {averages}")

        self.set_continous_mode(0)
        self.wait_for_completed()

        self.frequencies = np.linspace(self.start_frequency,
                                       self.stop_frequency,
                                       self.sweep_point_number)

    def get_data_normalisation_spectrum(self):
        for a in range(self.averages):
            self.inst.write("INIT:IMMediate")
            self.wait_for_completed()
        self.inst.write("CALC:PAR1:SEL")
        data_normalisation_spectrum = self.inst.query("CALC:DATA:FDATa?")
        array_normalisation_spectrum = np.array(list(map(float, data_normalisation_spectrum.split(','))))
        self.data_normalisation_spectrum = array_normalisation_spectrum
        print("Data of normalisation of spectrum done")
        return array_normalisation_spectrum

    def get_data_normalisation_amplitude(self):
        for a in range(self.averages):
            self.inst.write("INIT:IMMediate")
            self.wait_for_completed()
        self.inst.write("CALC:PAR2:SEL")
        data_normalisation_amplitude = self.inst.query("CALC:DATA:FDATa?")
        array_normalisation_amplitude = np.array(list(map(float, data_normalisation_amplitude.split(','))))
        self.data_normalisation_amplitude = array_normalisation_amplitude
        print("Data of normalisation amplitude done")
        return array_normalisation_amplitude

    def get_data(self):
        for i in range(self.averages):
            self.inst.write("INIT:IMMediate")
            self.wait_for_completed()
        self.inst.write("CALC:PAR1:SEL")
        data = self.inst.query("CALC:DATA:FDATa?")
        array = np.array(list(map(float, data.split(','))))
        return array

    def get_data2(self):
        for T in range(self.averages):
            self.inst.write("INIT:IMMediate")
            self.wait_for_completed()
        self.inst.write("CALC:PAR2:SEL")
        data2 = self.inst.query("CALC:DATA:FDATa?")
        array2 = np.array(list(map(float, data2.split(','))))
        return array2

    def find_frequence(self, Frequence):
        counter = 0  
        while counter < len(self.frequencies) and float(self.frequencies[counter]) < float(Frequence):
            counter = counter + 1
        return counter

    def poll_single_value(self, Frequence, fichier):
        counter = self.find_frequence(Frequence)
        self.buffer_array = np.zeros((2, 10000)) * np.nan
        self.buffer_array2 = np.zeros((2, 10000)) * np.nan
        self.Liste = np.zeros((1601, 3)) * np.nan
        self.running = True
        self.start_time = None
        #counter = self.find_frequence(Frequence)
        print(counter)
        self.buffer_array = ([], [])
        self.buffer_array2 = ([], [])
        while self.running:
            t = time.time()
            if self.start_time is None:
                self.start_time = t
            temps = t - self.start_time
            data = self.get_data()
            data2 = self.get_data2()

            current_phase = data[-1]  # Acessa o último elemento da lista/array de fase
            current_amplitude = data2[-1]  # Acessa o último elemento da lista/array de amplitude

            self.data_monitor.update_and_check(current_phase, current_amplitude)

            self.spectrum_normalisation = data / self.data_normalisation_spectrum
            self.amplitude_normalisation = data2 / self.data_normalisation_amplitude
            self.spectrum = data
            self.amplitude = data2
            self.Liste[:, 0] = self.frequencies
            self.Liste[:, 1] = self.spectrum
            self.Liste[:, 2] = self.amplitude
            df = pd.DataFrame(self.Liste, columns=['Frequence', 'Phase', 'Amplitude'])
            df.to_csv(fichier)
            #df.to_csv('fichier.csv', index=False)

            self.buffer_array[0].append(temps)
            self.buffer_array[1].append(data[counter])
            self.buffer_array2[0].append(temps)
            self.buffer_array2[1].append(data2[counter])

    def affichage(self, fichier2, fichier3):
        #self.spectrum_normalization()
        app = QApplication(sys.argv)
        win = QMainWindow()
        central_widget = QWidget()
        win.setCentralWidget(central_widget)
        layout = QHBoxLayout()

        time_plot = pg.PlotWidget(title="Phase in real time")
        time_curve = time_plot.plot(pen='y')
        layout.addWidget(time_plot)

        time_plot2 = pg.PlotWidget(title="Amplitude in real time")
        time_curve2 = time_plot2.plot(pen='y')
        layout.addWidget(time_plot2)

        central_widget.setLayout(layout)

        def update():
            if self.spectrum is not None:
                time_curve.setData(self.buffer_array[0], self.buffer_array[1])
                time_curve2.setData(self.buffer_array2[0], self.buffer_array2[1])

        timer = QTimer()
        timer.timeout.connect(update)
        timer.start(10)

        win.show()
        app.exec()

        self.Liste1 = list(self.buffer_array)
        self.Liste1.append(self.buffer_array2[1])

        self.Liste2 = np.zeros((1601, 4)) * np.nan
        self.Liste2[:, 1] = self.frequencies
        self.Liste2[:, 2] = self.get_data_normalisation_spectrum
        self.Liste2[:, 3] = self.get_data_normalisation_amplitude

        df1 = pd.DataFrame(self.Liste1)
        df1.to_csv(fichier2)
        df1.to_csv('fichier2.csv', index=False)
        df2 = pd.DataFrame(self.Liste2, columns=['', 'Frequence', 'Phase normalise', 'Amplitude normalise'])
        df2.to_csv(fichier3)
        #df2.to_csv('fichier3.csv', index=False)


    def start_poller(self, Frequence, fichier, fichier2, fichier3):
        self.thread = threading.Thread(target=self.poll_single_value, args=[Frequence, fichier])
        self.thread.start()
        self.affichage(fichier2, fichier3)
        myff.stop()

    def stop(self):
        self.running = False

class MyApp(QMainWindow):
    def __init__(self):
            super().__init__()
            self.initUI()
            # Initialize QLineEdit widgets
            self.center_freq = None
            self.span = None
            self.bandwidth = None
            self.averages = None
            self.coefficient = None
            self.Frequence = None
            self.fichier = None
            self.fichier2 = None
            self.fichier3 = None
            #self.myff = FieldFox()
        
    
    def initUI(self):
        self.setWindowTitle("Interface FieldFox")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("icon.png"))

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        label_title = QLabel("Interface for real-time measurement of the S-parameter")
        label_title.setStyleSheet("color: #3f33ff")
        layout.addWidget(label_title)



        label_center_freq = QLabel("Center frequency in Hz:")
        layout.addWidget(label_center_freq)
        self.input_center_freq = QLineEdit()
        self.input_center_freq.setValidator(QDoubleValidator())  # Allow double (floating-point) values
        layout.addWidget(self.input_center_freq)

        label_span = QLabel("Span in Hz:")
        layout.addWidget(label_span)
        self.input_span = QLineEdit()
        self.input_span.setValidator(QDoubleValidator())  # Allow double (floating-point) values
        layout.addWidget(self.input_span)

        label_bandwidth = QLabel("Bandwidth in Hz [10, 100, 1000, 10000, 100000]:")
        layout.addWidget(label_bandwidth)
        self.input_bandwidth = QLineEdit()
        self.input_bandwidth.setValidator(QDoubleValidator())  # Allow double (floating-point) values
        layout.addWidget(self.input_bandwidth)

        label_averages = QLabel("Average measurement:")
        layout.addWidget(label_averages)
        self.input_averages = QLineEdit()
        self.input_averages.setValidator(QIntValidator())  # Allow integer values
        layout.addWidget(self.input_averages)

        label_coefficient = QLabel("Coefficient:")
        layout.addWidget(label_coefficient)
        self.input_coefficient = QLineEdit()
        layout.addWidget(self.input_coefficient)

        label_Frequence = QLabel("Target frequency in Hz:")
        layout.addWidget(label_Frequence)
        self.input_Frequence = QLineEdit()
        layout.addWidget(self.input_Frequence)

        label_fichier = QLabel("File name for the complete graph:")
        layout.addWidget(label_fichier)
        self.input_fichier = QLineEdit()
        layout.addWidget(self.input_fichier)

        label_fichier2 = QLabel("File name for the target frequency:")
        layout.addWidget(label_fichier2)
        self.input_fichier2 = QLineEdit()
        layout.addWidget(self.input_fichier2)

        label_fichier3 = QLabel("File name for the normalization graph:")
        layout.addWidget(label_fichier3)
        self.input_fichier3 = QLineEdit()
        layout.addWidget(self.input_fichier3)


        #Buttons
        button_initialize = QPushButton("Initialization of the network analyzer")
        button_initialize.setStyleSheet("background-color: #33b2ff")
        layout.addWidget(button_initialize)
        button_initialize.clicked.connect(self.initialize)

        button_spectrum_normalization = QPushButton("Spectrum normalization")
        button_spectrum_normalization.setStyleSheet("background-color: #33b2ff")
        layout.addWidget(button_spectrum_normalization)
        button_spectrum_normalization.clicked.connect(self.spectrum_normalization)

        button_amplitude_normalization = QPushButton("Amplitude normalization")
        button_amplitude_normalization.setStyleSheet("background-color: #33b2ff")
        layout.addWidget(button_amplitude_normalization)
        button_amplitude_normalization.clicked.connect(self.amplitude_normalization)

        button_plot_graph = QPushButton("Plot the graph")
        button_plot_graph.setStyleSheet("background-color: #33b2ff")
        layout.addWidget(button_plot_graph)
        button_plot_graph.clicked.connect(self.plot_graph)

        central_widget.setLayout(layout)

  
    def initialize(self):
        center_freq = self.input_center_freq.text()
        span = self.input_span.text()
        bandwidth = self.input_bandwidth.text()
        averages = self.input_averages.text()
        coefficient = self.input_coefficient.text()

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

        #self.myff.averages = averages

        myff.initialize(center_freq, span, bandwidth, averages, coefficient)



    def spectrum_normalization(self):
        myff.get_data_normalisation_spectrum()

    def amplitude_normalization(self):
        myff.get_data_normalisation_amplitude()

    def plot_graph(self):
        Frequence = self.input_Frequence.text()
        fichier = self.input_fichier.text()
        fichier2 = self.input_fichier2.text()
        fichier3 = self.input_fichier3.text()


        try:
            Frequence = float(Frequence)
        except ValueError:
            self.show_warning("Invalid Input", "Please enter a valid numeric value for Target Frequency.")
            return
        
        #self.myff.start_poller(Frequence, fichier, fichier2, fichier3)      
        myff.start_poller(Frequence, fichier, fichier2, fichier3)



def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    myff = FieldFox()
    main()
