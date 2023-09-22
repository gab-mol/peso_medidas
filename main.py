import kivy
kivy.require('1.9.0')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.config import Config
# from kivy.uix.filechooser import FileChooser # por ahora prefiero evitarlo

import time
import os
from plyer import filechooser

from peewee import  SqliteDatabase, Model, DateField, FloatField

Config.set('graphics', 'width', 500)
Config.set('graphics', 'height', 300)

import configparser

RUTA = os.getcwd()
FECHA_SIS = time.strftime("%d/%m/%Y", time.localtime(time.time()))


# Bases de datos y archivo de configuración
class Confg:
    '''Para guardar ruta a   Archivos.
    (Quiero que sea editable por el usuario y persistente)'''
    def __init__(self) -> None:
        '''Lee/Crea .cfg en dir trabajo.'''
        self.config = configparser.ConfigParser()
        self.wdir = RUTA
        self.NOMBRE = 'segpeso.cfg'
        self.ruta_cfg = os.path.join(self.wdir, self.NOMBRE)

        try:
            self.config.read(self.NOMBRE)
            self.ruta = self.config["RUTAS"]["xlsx"]
        except:
            self.config["RUTAS"] = {"xlsx": "0"}
            with open(self.NOMBRE, 'w') as segpeso:
                self.config.write(segpeso)
            raise Exception("Sin archivo cfg, creado con valor nulo")
        
        print("Ruta a xlsx: ",self.ruta)

    def guardar_ruta(self, nueva_ruta:str):
        '''Guardar la ruta el .cfg
        (llamar en método del botón)'''
        self.config["RUTAS"] = {"xlsx": nueva_ruta}
        with open(self.ruta_cfg, 'w') as segpeso:
            self.config.write(segpeso)

## Conexión con base de datos SQL (ORM)
nombr_bd = "registro.db"
bd = SqliteDatabase(nombr_bd)
class Bd(Model):
    class Meta():
        database = bd
        db_table='Medidas'

class Registro(Bd):
    '''Declaración de tabla'''
    fecha = DateField(primary_key=True)
    peso = FloatField()
    diametr_sob_ombl_mx = FloatField()
    diametr_sob_ombl_mn = FloatField()
    diametr_baj_ombl_mx = FloatField()
    diametr_baj_ombl_mn = FloatField()

try:
    bd.connect()
    bd.create_tables([Registro])
    print(f"\n**\nÉxito al conectar con bd:\n {os.path.join(RUTA,nombr_bd)}\n**\n")
except:
    raise Exception("\nError de Conexión con bd SQL\n")


class VerifCamp:
    '''Verificación de campos.'''
    def __init__(self) -> None:
        ...


class Crud():
    '''Registrar medidas: al Excel que venía usando,
    y a una base SQL (métodos CRUD).'''
    def __init__(self, fecha:str, peso:float, medsomx:float,
            medsomn:float, medbomx:float, medbomn:float) -> None:
        self.reg_bd = Registro()

        self.fecha = fecha
        self.peso = peso
        self.medsomx = medsomx
        self.medsomn = medsomn
        self.medbomx = medbomx
        self.medbomn = medbomn
    
    def alta(self):
        self.reg_bd.fecha = self.fecha
        self.reg_bd.peso = self.peso
        self.reg_bd.diametr_sob_ombl_mx = self.medsomx
        self.reg_bd.diametr_sob_ombl_mn = self.medsomn
        self.reg_bd.diametr_baj_ombl_mx = self.medbomx
        self.reg_bd.diametr_baj_ombl_mn = self.medbomn
        self.reg_bd.save()

        print("Guardado registro en SQL")
    
    def baja():
        ...

    def modificacion():
        ...

# Eventos bontones y declaración de app
class PesoApp(BoxLayout):

    # Esto es un enlace bidireccional (entra al .kv por 
    #  root.fechainput, vuelve como fechainput: fecha.text) *
    fechainput = StringProperty()

    peso = NumericProperty()
    medsomx = NumericProperty()
    medsomn = NumericProperty()
    medbomx = NumericProperty()
    medbomn = NumericProperty()

    def __init__(self, **kwargs):
        '''root'''
        super().__init__(**kwargs)
        self.segpeso_cfg = Confg()
        self.fechainput = FECHA_SIS # * el valor defoult  

        # arreglar incosistencia en uso de propiedades y tipos de datos
        self.salida_datos = Crud(self.fechainput, 
            self.peso, self.medsomx,
            self.medsomn,self.medbomx,
            self.medbomn)

    def guardar(self):
        print("fechainput ",self.fechainput)
        print("peso ",self.peso.text)
        print("medsomx ",self.medsomx.text)
        print("medsomn ",self.medsomn.text)
        print("medbomx ",self.medbomx.text)
        print("medbomn ",self.medbomn.text)
        self.salida_datos.alta()

        
        


    def limpiar(self):
        print("anda")

    def mod_rut(self):
        print("Modificando ruta")
        ruta_usr = filechooser.open_file(
            title="Elegir ruta a archivo xlsx a crear..."
            )[0]
        self.segpeso_cfg.guardar_ruta(ruta_usr)
        print("Ruta guardada en .cgf = ", ruta_usr)
    def abrir_xlsx(self):
        print("anda")


class MainApp(App):
    title = "Seguimiento Peso"
    def build(self):
        return PesoApp()
        
if __name__ == '__main__':
    MainApp().run()