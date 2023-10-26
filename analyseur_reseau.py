from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import numpy as np
import pyvisa
import threading
import time
import codecs
import csv
import pandas as pd
import tkinter

# MARBOUH OTHMANE (Ce code est une propriété scientifique de Marbouh Othmane, toute utilisation ou modification
# de ce dernier doit rester dans le cadre d'un travail de recherche de l'équipe AIMAN)


print("Creating class")


class FieldFox():

    def __init__(self, visa_id="USB0::0x2A8D::0x5C18::MY59221135::0::INSTR"):
        print("Creating instance of FieldFox")
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(visa_id, read_termination='\n')
        self.inst.timeout = 1000000
        self.spectrum = None
        self.amplitude = None
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

        center_freq = center_freq.get()
        center_freq = float(center_freq)
        print(center_freq)

        span = span.get()
        span = float(span)
        print(span)

        bandwidth = bandwidth.get()
        bandwidth = float(bandwidth)
        print(bandwidth)

        averages = averages.get()
        averages = int(averages)
        print(averages)

        coefficient = coefficient.get()
        print(coefficient)

        self.averages = averages
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
        print("Data de Normalisation du spectre faite")
        return array_normalisation_spectrum

    def get_data_normalisation_amplitude(self):
        for a in range(self.averages):
            self.inst.write("INIT:IMMediate")
            self.wait_for_completed()
        self.inst.write("CALC:PAR2:SEL")
        data_normalisation_amplitude = self.inst.query("CALC:DATA:FDATa?")
        array_normalisation_amplitude = np.array(list(map(float, data_normalisation_amplitude.split(','))))
        self.data_normalisation_amplitude = array_normalisation_amplitude
        print("Data de Normalisation amplitude faite")
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
        while self.frequencies[counter] < Frequence:
            counter = counter + 1
        return counter

    def poll_single_value(self, Frequence, fichier):

        self.buffer_array = np.zeros((2, 10000)) * np.nan
        self.buffer_array2 = np.zeros((2, 10000)) * np.nan
        self.Liste = np.zeros((1601, 3)) * np.nan
        self.running = True
        self.start_time = None
        counter = self.find_frequence(Frequence)
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
            self.spectrum_normalisation = data / self.data_normalisation_spectrum
            self.amplitude_normalisation = data2 / self.data_normalisation_amplitude
            self.spectrum = data
            self.amplitude = data2
            # fichier="Graphe_Complet.csv"
            self.Liste[:, 0] = self.frequencies
            self.Liste[:, 1] = self.spectrum
            self.Liste[:, 2] = self.amplitude
            df = pd.DataFrame(self.Liste, columns=['Frequence', 'Phase', 'Amplitude'])
            df.to_csv(fichier)

            self.buffer_array[0].append(temps)
            self.buffer_array[1].append(data[counter])
            self.buffer_array2[0].append(temps)
            self.buffer_array2[1].append(data2[counter])

    def affichage(self, fichier2, fichier3):

        win = pg.GraphicsLayoutWidget(show=True, title="FieldFox View")
        win.resize(1000, 600)
        win.setWindowTitle("FieldFox View")

        # # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)

        time_plot = win.addPlot(title="Phase in real time")
        time_curve = time_plot.plot(pen='y')

        win.nextRow()

        time_plot2 = win.addPlot(title="Amplitude in real time")
        time_curve2 = time_plot2.plot(pen='y')

        def update():
            if self.spectrum is not None:
                time_curve.setData(self.buffer_array[0], self.buffer_array[1])
                time_curve2.setData(self.buffer_array2[0], self.buffer_array2[1])

        timer = QtCore.QTimer()
        timer.timeout.connect(update)
        timer.start(100)

        pg.exec()

        self.Liste1 = list(self.buffer_array)
        self.Liste1.append(self.buffer_array2[1])

        self.Liste2 = np.zeros((1601, 4)) * np.nan
        self.Liste2[:, 1] = self.frequencies
        self.Liste2[:, 2] = self.spectrum_normalisation
        self.Liste2[:, 3] = self.amplitude_normalisation

        df1 = pd.DataFrame(self.Liste1)
        df1.to_csv(fichier2)
        df2 = pd.DataFrame(self.Liste2, columns=['', 'Frequence', 'Phase normalise', 'Amplitude normalise'])
        df2.to_csv(fichier3)

    def start_poller(self, Frequence, fichier, fichier2, fichier3):
        print("Entrer votre frequence en Hz:")
        Frequence = Frequence.get()
        Frequence = float(Frequence)

        fichier = fichier.get()
        fichier2 = fichier2.get()
        fichier3 = fichier3.get()
        self.thread = threading.Thread(target=self.poll_single_value, args=[Frequence, fichier])
        self.thread.start()
        self.affichage(fichier2, fichier3)
        myff.stop()

    def stop(self):
        self.running = False


if __name__ == "__main__":
    myff = FieldFox()
    window = tkinter.Tk()
    # window.iconbitmap("o.ico")

    label_0 = tkinter.Label(window,
                            text="\n                                                                            Interface for real-time measurement of the S-parameter                                                                               ",
                            fg='#3f33ff')
    label_0.grid(row=0, column=1)

    label_0 = tkinter.Label(window, text="")
    label_0.grid(row=1, column=1)

    label_10 = tkinter.Label(window, text="\nS-parameter\n    [S11,S12,S21,S22] :", fg='#ff3333')
    label_10.grid(row=2, column=0)
    entry_9 = tkinter.Entry(window)
    entry_9.grid(row=2, column=1)

    label_1 = tkinter.Label(window, text="\nCenter frequency in Hz :\n", fg='#ff3333')
    label_1.grid(row=3, column=0)
    entry_1 = tkinter.Entry(window)
    entry_1.grid(row=3, column=1)

    label_2 = tkinter.Label(window, text="Span in Hz :\n", fg='#ff3333')
    label_2.grid(row=4, column=0)
    entry_2 = tkinter.Entry(window)
    entry_2.grid(row=4, column=1)

    label_3 = tkinter.Label(window, text="    Bandwidth in Hz\n      [10,100,1000,10000,100000] :\n", fg='#ff3333')
    label_3.grid(row=5, column=0)
    entry_3 = tkinter.Entry(window)
    entry_3.grid(row=5, column=1)

    label_4 = tkinter.Label(window, text="Average measurement :\n", fg='#ff3333')
    label_4.grid(row=6, column=0)
    entry_4 = tkinter.Entry(window)
    entry_4.grid(row=6, column=1)

    label_0 = tkinter.Label(window, text=" ")
    label_0.grid(row=7, column=1)

    button_1 = tkinter.Button(window, text="Initialization of the network analyzer", bg='#33b2ff')
    button_1.grid(row=8, column=1)

    label_0 = tkinter.Label(window, text=" ")
    label_0.grid(row=9, column=1)

    label_5 = tkinter.Label(window, text="Target frequency in Hz :\n", fg='#ff3333')
    label_5.grid(row=10, column=0)
    entry_5 = tkinter.Entry(window)
    entry_5.grid(row=10, column=1)

    label_0 = tkinter.Label(window, text=" ")
    label_0.grid(row=11, column=1)

    button_3 = tkinter.Button(window, text="Spectrum normalization", bg='#33b2ff')
    button_3.grid(row=12, column=1)

    button_4 = tkinter.Button(window, text="Amplitude normalization", bg='#33b2ff')
    button_4.grid(row=13, column=1)

    label_0 = tkinter.Label(window, text=" ")
    label_0.grid(row=14, column=1)

    label_6 = tkinter.Label(window, text="     File name for the complete \n graph :", fg='#ff3333')
    label_6.grid(row=15, column=0)
    entry_6 = tkinter.Entry(window)
    entry_6.grid(row=15, column=1)

    label_7 = tkinter.Label(window, text="     File name for the target \n frequency :", fg='#ff3333')
    label_7.grid(row=16, column=0)
    entry_7 = tkinter.Entry(window)
    entry_7.grid(row=16, column=1)

    label_8 = tkinter.Label(window, text="     File name for the normalization \n graph :", fg='#ff3333')
    label_8.grid(row=17, column=0)
    entry_8 = tkinter.Entry(window)
    entry_8.grid(row=17, column=1)

    label_0 = tkinter.Label(window, text=" ")
    label_0.grid(row=18, column=1)

    button_2 = tkinter.Button(window, text="Plot the graph", bg='#33b2ff')
    button_2.grid(row=19, column=1)

    label_0 = tkinter.Label(window, text=" ")
    label_0.grid(row=20, column=1)
    label_0 = tkinter.Label(window, text=" ")
    label_0.grid(row=21, column=1)

    button_1.bind("<Button-1>", lambda a: myff.initialize(entry_1, entry_2, entry_3, entry_4, entry_9))
    button_2.bind("<Button-1>", lambda b: myff.start_poller(entry_5, entry_6, entry_7, entry_8))
    button_3.bind("<Button-1>", lambda d: myff.get_data_normalisation_spectrum())
    button_4.bind("<Button-1>", lambda r: myff.get_data_normalisation_amplitude())

    window.title("Interface that automizes the data acquisition via the KEYSIGHT FieldFox network analyzer")
    myff.stop()
    window.mainloop()
