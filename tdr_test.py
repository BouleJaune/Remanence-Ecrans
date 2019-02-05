import serial
import cv2
import os
from threading import Thread, Event
import numpy as np
import struct
import serial.tools.list_ports
import matplotlib.pyplot as plt
import pandas as pd
#penser à la luminosité de l'écran qui compte

def nom_port_serial():
    comlist = serial.tools.list_ports.comports()
    connected = []
    desc = []
    port = None
    for element in comlist:
        connected.append(element.device)
        desc.append(element.description)
        if "Arduino Uno ("+element.device+")" == element.description:           
            port = element.device   
    return port
    
port = nom_port_serial()        
ser = serial.Serial(port, 115200) 

    ## MESSAGE D'ERREUR try/except si trouve pas le port## 


pathim = "./Images/"
liste_images = ["0.png",
                "50.png",
                "100.png",
                "150.png",
                "200.png",
                "255.png"]

             

### TROUVER LES BONS TEMPS POUR LES WAITKEY###
### TROUVER LES BONS TEMPS POUR LES WAITKEY###
temps_attente = {"Setup": 1000, "Avant-T": 300, "Apres-T": 350}                
nombre_repetitions_par_transition = 10

 
class data(Thread): ## créer les logs

    def __init__(self, liste_images, ser, nombre_repetitions_par_transition):    
        Thread.__init__(self)
        self.ser = ser
        self.liste_images = liste_images
        self.datas = []
        self.nombre_repetitions = nombre_repetitions_par_transition
        
    def run(self):
        for nom_image1 in self.liste_images:            
            for nom_image2 in self.liste_images:                    
                if self.liste_images.index(nom_image1) < self.liste_images.index(nom_image2):
                    for n in range(self.nombre_repetitions):  ##rise-time                        
                        path_log = "./binary_logs/"+"rise-time/"+nom_image1+"-"+nom_image2+"/"
                        os.makedirs(os.path.dirname(path_log), exist_ok=True)   
                        log = open(path_log+str(n)+".dat","wb")                        
                        DataLoopIsOn.wait()   
                        self.ser.read(self.ser.inWaiting())                       
                        while(1):                              
                            self.datas.append(self.ser.read(2))
                            if stopDataLoop.is_set():
                                break 
                        DataLoopIsOn.clear()
                        for data in self.datas:
                            log.write(data)
                        self.datas = []
                        log.close()                                                   
                if self.liste_images.index(nom_image1) > self.liste_images.index(nom_image2):
                    for n in range(self.nombre_repetitions):  ##fall-time                       
                        path_log = "./binary_logs/"+"fall-time/"+nom_image1+"-"+nom_image2+"/"
                        os.makedirs(os.path.dirname(path_log), exist_ok=True)                        
                        log = open(path_log+str(n)+".dat","wb")                       
                        DataLoopIsOn.wait()                       
                        self.ser.read(self.ser.inWaiting())                      
                        while(1):                               
                            self.datas.append(self.ser.read(2))
                            if stopDataLoop.is_set():
                                break 
                        DataLoopIsOn.clear()                           
                        for data in self.datas:
                            log.write(data)
                        self.datas = []
                        log.close()                                                   
                if self.liste_images.index(nom_image1) == self.liste_images.index(nom_image2):  
                    path_log = "./binary_logs/"+"constantes/"+nom_image1+"/"
                    print(nom_image1)
                    os.makedirs(os.path.dirname(path_log), exist_ok=True)                        
                    log = open(path_log+"valeurs.dat","wb")                   
                    DataLoopIsOn.wait()
                    self.ser.read(self.ser.inWaiting())     
                    while(1):                         
                        self.datas.append(self.ser.read(2))
                        if stopDataLoop.is_set():
                            break                        
                    DataLoopIsOn.clear()                           
                    for data in self.datas:
                        log.write(data)
                    self.datas = []
                    log.close()  
            if not AffichageImagesIsOn.is_set():
                return

class AffichageTransitions(Thread): ## Affiche les images et envoie des flag pour record les données

    def __init__(self, liste_images, nombre_repetitions_par_transition, temps_attente):    
        Thread.__init__(self)
        self.liste_images = liste_images
        self.fenetre = ""
        self.nombre_repetitions = nombre_repetitions_par_transition
        self.temps_attente = temps_attente              
              
    def run(self):      
        cv2.namedWindow(self.fenetre, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(self.fenetre, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        ### POTENTIELLEMENT METTRE UNE IMAGE "D'ACCUEIL" ###      
        for nom_image1 in self.liste_images:
            for nom_image2 in self.liste_images:         
                if self.liste_images.index(nom_image1) < self.liste_images.index(nom_image2):              
                    for n in range(self.nombre_repetitions): ##rise-time     
                        img1 = cv2.imread(pathim + nom_image1, 0)
                        img2 = cv2.imread(pathim + nom_image2, 0)                          
                        cv2.imshow(self.fenetre, img1)                       
                        cv2.waitKey(self.temps_attente["Setup"])                       
                        stopDataLoop.clear()
                        DataLoopIsOn.set()                       
                        cv2.waitKey(self.temps_attente["Avant-T"])
                        cv2.imshow(self.fenetre, img2)
                        cv2.waitKey(self.temps_attente["Apres-T"])                        
                        stopDataLoop.set()                                                             
                if self.liste_images.index(nom_image1) > self.liste_images.index(nom_image2):
                    for n in range(self.nombre_repetitions): ##fall-time
                        img1 = cv2.imread(pathim + nom_image1, 0)
                        img2 = cv2.imread(pathim + nom_image2, 0)   
                        cv2.imshow(self.fenetre, img1)
                        cv2.waitKey(self.temps_attente["Setup"])
                        stopDataLoop.clear()
                        DataLoopIsOn.set()                        
                        cv2.waitKey(self.temps_attente["Avant-T"])
                        cv2.imshow(self.fenetre, img2)
                        cv2.waitKey(self.temps_attente["Apres-T"])
                        stopDataLoop.set()                       
                if  self.liste_images.index(nom_image1) == self.liste_images.index(nom_image2):  
                    img = cv2.imread(pathim + nom_image1, 0)  
                    cv2.imshow(self.fenetre, img)
                    cv2.waitKey(self.temps_attente["Setup"])
                    stopDataLoop.clear()
                    DataLoopIsOn.set()                 
                    cv2.waitKey(self.temps_attente["Avant-T"]+self.temps_attente["Apres-T"])
                    stopDataLoop.set()                  
        AffichageImagesIsOn.clear()        
        cv2.destroyAllWindows()

class DecodeData():
            
    def __init__(self):
        self.path_bin = "./binary_logs/"
        self.path_decoded = "./decoded_logs/"
        self.decode_all_data()
        
    def decode_data(self, data, data_path, path_decoded_log):
        decoded_data = []
        decaller = False
        log_decoded = open(path_decoded_log+data,"w")   
        with open(data_path+data, "rb") as f:
            for n in range(1000):
                byte = f.read(2)           
                if len(byte)!=2:
                    break
                decoded_byte = struct.unpack("H", byte)[0]
                if decoded_byte > 1500:
                    decaller = True            
        with open(data_path+data, "rb") as f:    
            if decaller == True:
                b = f.read(1)
            for n in range(int(os.stat(data_path+data).st_size/2)):
                byte = f.read(2)           
                if len(byte)!=2:
                    break
                decoded_byte = struct.unpack("H", byte)[0]                       
                log_decoded.write(str(decoded_byte)+"\n")
                decoded_data.append(decoded_byte)                   
            log_decoded.close()       
        return decoded_data
        
    def decode_all_data(self):
        for fall_rise_folder in os.listdir(self.path_bin):    
            for transition in os.listdir(self.path_bin+fall_rise_folder):
                for fichier_to_decode in os.listdir(self.path_bin+fall_rise_folder+"/"+transition):                 
                    path_decoded_log = self.path_decoded+fall_rise_folder+"/"+transition+"/"
                    os.makedirs(os.path.dirname(path_decoded_log), exist_ok=True)           
                    data_path = self.path_bin+fall_rise_folder+"/"+transition+"/"                                  
                    self.decode_data(fichier_to_decode, data_path, path_decoded_log)

class TraiteData():
    
    def __init__(self, tolerance, liste_images):
        self.path_decoded = "./decoded_logs/"    
        self.tolerance = tolerance
        self.liste_images = liste_images
        self.constantes = self.determine_constantes()             
        self.TempsDeReponses, self.OverShoot = self.DataFramesCreation()
        
    def recupere_decoded_data(self, fichier):
        data = []
        f = open(fichier, "r")
        data = f.readlines()
        return list(map(int,data))
    
    def determine_constantes(self):  
        self.constantes = {}
        for constante in os.listdir(self.path_decoded+"constantes"):
            fichier_data = self.path_decoded+"constantes"+"/"+constante+"/valeurs.dat"
            data = self.recupere_decoded_data(fichier_data)
            data = list(map(int,data))
            self.constantes[constante] = np.mean(data)           
        print("\nConstantes: ",self.constantes,"\n")
        return self.constantes       
      
    def determine_tdr(self, V_dep, V_arr, data):
        td_found = False
        tf_found = False
        tV = 0
        if V_dep < V_arr:           
            for V in data:                
                tV += 1
                if V > V_dep+(V_arr-V_dep)*self.tolerance and not td_found:
                    td = tV
                    td_found = True
                if all(V_arr-(V_arr-V_dep)*self.tolerance <= x <= V_arr+(V_arr-V_dep)*self.tolerance for x in data[tV:]) and (not tf_found):
                    tf = tV
                    tf_found = True
        if V_dep > V_arr:             
            for V in data:                    
                tV += 1                
                if V < V_dep-(V_dep-V_arr)*self.tolerance and not td_found:
                    td = tV
                    td_found = True
                if all(V_arr-(V_dep-V_arr)*self.tolerance <= x <= V_arr+(V_dep-V_arr)*self.tolerance for x in data[tV:]) and (not tf_found):
                    tf = tV
                    tf_found = True                       
        return tf-td
           
    def DataFramesCreation(self):        
        DF_tdr = np.zeros((6,6))
        DF_overshoot = np.zeros((6,6))
        tag = [im[:-4] for im in liste_images]
        for fall_rise_folder in os.listdir(self.path_decoded):    
            if fall_rise_folder != "constantes":
                for transition in os.listdir(self.path_decoded+fall_rise_folder):
                    k = transition.index("-")
                    depart = self.constantes[transition[:k]]
                    arrivee = self.constantes[transition[k+1:]]
                    tdr_temp = []   
                    OverShoot_temp = []
                    offset = False
                    if "0.png" == transition[:k] or transition[k+1:] =="0.png":
                        depart = depart + 50 
                        arrivee = arrivee + 50
                        offset = True
                    for fichier_data in os.listdir(self.path_decoded+fall_rise_folder+"/"+transition):
                        path = self.path_decoded+fall_rise_folder+"/"+transition+"/"+fichier_data                        
                        data = self.recupere_decoded_data(path)
                        if offset:
                            data = np.asarray(data)+50
                        tdr_temp.append(self.determine_tdr(depart, arrivee, data))
                        OverShoot_temp.append(self.calcul_OverShoot(depart, arrivee, data))
                    self.courbes(data, transition, fichier_data[:-4])     

                    ## LIGNES = DEPART, COLONNES = ARRIVEE 
                    
                    DF_tdr[self.liste_images.index(transition[:k]), self.liste_images.index(transition[k+1:])]= np.mean(tdr_temp)/2   
                    DF_overshoot[self.liste_images.index(transition[:k]), self.liste_images.index(transition[k+1:])]= np.mean(OverShoot_temp)   
                                                                                                                      
        DF_tdr = pd.DataFrame(DF_tdr, index=tag, columns=tag)
        DF_overshoot = pd.DataFrame(DF_overshoot, index=tag, columns=tag)
        DF_tdr = DF_tdr.replace(0.0, np.nan, regex=True)             
        return DF_tdr, DF_overshoot
    
    def courbes(self, data, transition, fichier_data):
        plt.plot(data)
        plt.savefig("./plots/"+transition+"-"+fichier_data+".png", dpi=300)
        plt.clf()
     
    def calcul_OverShoot(self, depart, arrivee, data):
        if depart < arrivee:
            overshoot = max(data)/arrivee
        elif depart > arrivee:
            overshoot = min(data)/arrivee
        overshoot = round((overshoot-1)*100,1)
        if abs(overshoot) < 5:
            overshoot = 0
        return overshoot

DataLoopIsOn = Event()
stopDataLoop = Event()
AffichageImagesIsOn = Event()
AffichageImagesIsOn.set()

thread_1 = data(liste_images, ser, nombre_repetitions_par_transition)
thread_2 = AffichageTransitions(liste_images, nombre_repetitions_par_transition, temps_attente)

ser.read(ser.inWaiting())
thread_2.start()
thread_1.start()

thread_1.join()
thread_2.join()


DecodeData()    
Traitement = TraiteData(tolerance = 0.1, liste_images = liste_images)   

T = Traitement.TempsDeReponses
O = Traitement.OverShoot

min_T = T.min().min()
max_T = T.max().max()
mean_T = T.mean().mean()
min_O = O.min().min()   
max_O = O.max().max()
mean_O = O.mean().mean()
Stats = np.array( [[min_T, max_T, mean_T], [min_O, max_O, mean_O]] ) 
lignes = ["Temps de réponse", "Overshoot"]
col = ["Minimum", "Maximum", "Moyenne"]


Stats = pd.DataFrame(Stats, index=lignes, columns=col)
os.makedirs(os.path.dirname("./-----RESULTATS------/"), exist_ok=True)
T.to_csv("./-----RESULTATS------/TempsDeReponses.csv",sep=";")
O.to_csv("./-----RESULTATS------/OverShoot.csv", sep=";")
Stats.to_csv("./-----RESULTATS------/Stats.csv", sep=";")

