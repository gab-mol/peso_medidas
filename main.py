import kivy
kivy.require('1.9.0')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.config import Config
Config.set('graphics', 'width', 500)
Config.set('graphics', 'height', 300)

import configparser

class PesoApp(BoxLayout):
    peso = ObjectProperty(None)
    medsomx = ObjectProperty(None)
    medsomn = ObjectProperty(None)
    medbomx = ObjectProperty(None)
    medbomn = ObjectProperty(None)

    def guardar(self):
        print(self.peso.text)
        print(self.medsomx.text)
        print(self.medsomn.text)
        print(self.medbomx.text)
        print(self.medbomn.text)
        
    def limpiar(self):
        print("anda")
    def mod_rut(self):
        print("anda")
    def abrir_xlsx(self):
        print("anda")

class Archivo:
    '''Para guardar ruta a archivo.
    (Quiero que sea editable por el usuario y persistente)'''
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        try:
            self.config.read('segpeso.cfg')
            self.ruta = self.config["RUTAS"]["xlsx"]
        except:
            self.config["RUTAS"] = {"xlsx": "0"}
            with open('segpeso.cfg', 'w') as segpeso:
                self.config.write(segpeso)
            raise Exception("Sin archivo cfg, creado con valor nulo")
        
        print("Ruta a xlsx: ",self.ruta)

    def crear_archivo():
        ...
    


class MainApp(App):
    title = "Seguimiento Peso"
    def build(self):
        return PesoApp()
        
if __name__ == '__main__':
    #MainApp().run()
    r = Archivo()