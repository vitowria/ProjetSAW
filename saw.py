import tkinter
from tkinter import messagebox
from tkinter import Tk, Button, Label, Frame
import os
import time
import pyfirmata
import propar
import pandas as pd 
from time import perf_counter
import numpy as np
import pyqtgraph as pg


# Fonction qui regle le arduino et donc les electrovannes
def electrovanne():
    HIGH = True
    LOW = False

    port = 'COM4'  # Port sur lequel est branché la carte arduino
    carte = pyfirmata.Arduino(port)
    Valve1 = board.get_pin('d:9:o')
    Valve2 = board.get_pin('d:11:o')
    Valve3 = board.get_pin('d:12:o')

    n = parametre1.get()  # nombre à revoir
    m = parametre2.get()  # à revoir aussi
    for i in range(n):
        for j in range(m):
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

# Fonction qui active le contrôleur de debit
def debimeter():
  
# Prends le valeur donné par l'utilisateurs sur l'interface    
  v_debit = parametre3.get()
  #print(parametre3.get())
# Connexion au contrôleur de débit (par défaut channel=1), ajuster le port COM
  instrument = propar.instrument('/dev/tty.usbserial-1410', channel=1)
#Mettre le paramètre 12 à 1 pour contrôler par le bus RS232
  instrument.writeParameter(12, 0) 
  #print(v_debit)
  instrument.writeParameter(9, int(v_debit))
  
# Verification de la valeur envoyée précédemment
  print(instrument.readParameter(9))

def to_cvs(liste, time_measurements):
    dict = {'voltage (V)': liste, 'time (sec)': time_measurements}  
    df = pd.DataFrame(dict) 
    df.to_csv('DataSAW.csv', index = False)

# Function that run the RF Analizer's code
def demarrer():
    debimeter()
    controlepr()
    electrovanne()

def analiseur():
    #demarrer()
    cmd3 = 'python3 analyseur_reseau.py'
    os.system(cmd3)
# Fonction qui active le contrôleur de pression
def controlepr():
# Prends le valeur donné par l'utilisateurs sur l'interface  
  v_pression = parametre4.get()

# Connexion au contrôleur de débit (par défaut channel=1), ajuster le port COM
  instrument = propar.instrument('COM5', channel=1)

# Mettre le paramètre 12 à 0 pour contrôler par le bus RS232
  instrument.writeParameter(12, 0)

# Moduler la valeur du débit entre 0 et 32000 (0 - 100%)
  instrument.writeParameter(9, v_pression)
# Verification de la valeur envoyée précédemment
  print(instrument.readParameter(9))



# Fonction qui regle la geometry de la fenetre
def geometry():
    app.minsize(200, 150)
    app.maxsize(500, 450)
    app.geometry("400x450")

# Definition de caracteristique de la font principale
myfont = ('Times New Roman', 12)
myfontTitle = ('Times New Roman', 14)

def winflag(*args):
    parametre1.set(parametre1.get())
    parametre2.set(parametre2.get())
    parametre3.set(parametre3.get())
    parametre4.set(parametre4.get())

app = tkinter.Tk()
app.title("Configurations")  # Titre fenetre

geometry()  # Appelle le fonction geometry

#Repérage des valeurs de saisie
parametre1 = tkinter.DoubleVar()
parametre1.trace("w", winflag)

parametre2 = tkinter.DoubleVar()
parametre2.trace("w", winflag)

parametre3 = tkinter.DoubleVar()
parametre3.trace("w", winflag)

parametre4 = tkinter.DoubleVar()
parametre4.trace("w", winflag)

# Network Analyser
button_na = tkinter.Button(app, text="Configurations Analyseur Reseau", width=30, height=1, command=analiseur, font=myfont)
button_na.pack()

# Capteurs
#button_capteurs = tkinter.Button(app, text="Configurations Capteurs", width=30, height=1, command=capteurs)
#button_capteurs.pack()


# Button that calls the funcion of the electrovannes code
vannes_label = tkinter.Label(app, text="Electrovannes",height=2, font=('Times New Roman', 14, 'bold'))  # Text showing
vannes_label.pack()

label_parametre1 = tkinter.Label(app,text="Concentration finale (ppm)", font=myfont)
label_parametre1.pack()

entry_parametre1 = tkinter.Entry(app, textvariable = parametre1, width = 30)
entry_parametre1.pack()



label_parametre2 = tkinter.Label(app,text="Concentration mère (ppm)", font=myfont)
label_parametre2.pack()

entry_parametre2 = tkinter.Entry(app, textvariable = parametre2, width = 30)
entry_parametre2.pack()

button_parametre1 = tkinter.Button(app, text="Ok", width=15, height=1, command=controlepr, font=myfont)
button_parametre1.pack()


#Controleur de debit
debimeter_label = tkinter.Label(app, text="Controleur de Débit",height=2, font=('Times New Roman', 14, 'bold'))  
debimeter_label.pack()

label_parametre3 = tkinter.Label(app,text="Débit (ml/min)", font=myfont)
label_parametre3.pack()

entry_parametre3 = tkinter.Entry(app, textvariable = parametre3, width = 30)
entry_parametre3.pack()

# Bouton qui appelle la fonction du code controleur de debit
button_debimeter = tkinter.Button(app, text="Ok", width=15, height=1, command=debimeter, font=myfont)
button_debimeter.pack()


#Controleur de pression
controlepr_label = tkinter.Label(app, text="Controleur de pression",height=2, font=('Times New Roman', 14, 'bold'))  # Text showing
controlepr_label.pack()

label_parametre4 = tkinter.Label(app,text="Pression (Pa)", font=myfont)
label_parametre4.pack()
entry_parametre4 = tkinter.Entry(app, textvariable = parametre4, width = 30)
entry_parametre4.pack()

# Bouton qui appelle la fonction du code controleur de pression
button_controlepr = tkinter.Button(app, text="Ok", width=15, height=1, command=controlepr, font=myfont)
button_controlepr.pack()




# CVS definition
#cvsname = tkinter.StringVar()
#cvsname.trace("w", winflag)

#label_range = tkinter.Label(app, text="Filename")
# label_range.grid(row = 0, column = 0, sticky = 'e', pady = 2)
#label_range.pack()

#entry = tkinter.Entry(app, textvariable=cvsname, width=15)
# label_range.grid(row = 1, column = 0, sticky = 'e', pady = 2)
#entry.pack()

#button_demarrer = tkinter.Button(app, text="Démarrer la mesure", width=15, height=1, command=demarrer, font=myfont)
#button_demarrer.pack()


app.mainloop()