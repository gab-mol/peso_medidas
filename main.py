import kivy
kivy.require('1.9.0')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ObjectProperty
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout

# from kivy.uix.filechooser import FileChooser # por ahora prefiero evitarlo

# Provisorio, previsto usar kivy para diseñar popupwindow
import messagebox

import time
import os
from plyer import filechooser

import re
from peewee import  SqliteDatabase, Model, DateField, FloatField, CharField, CompositeKey

Config.set('graphics', 'width', 500)
Config.set('graphics', 'height', 300)

import configparser

RUTA = os.getcwd()
FECHA_SIS = time.strftime("%d/%m/%Y", time.localtime(time.time()))

def hora() -> str:
    hora = time.strftime("%d/%m/%Y-%H:%M:%S", time.localtime(time.time()))
    return hora

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
class Registro(Model):
    fecha = DateField()
    fecha_regist = CharField()
    peso = FloatField(null = True)
    diametr_sob_ombl_mx = FloatField(null = True)
    diametr_sob_ombl_mn = FloatField(null = True)
    diametr_baj_ombl_mx = FloatField(null = True)
    diametr_baj_ombl_mn = FloatField(null = True)
    class Meta():
        database = bd
        db_table='Medidas'
        primary_key=CompositeKey('fecha', 'fecha_regist')

try:
    bd.connect()
    bd.create_tables([Registro])
    print(f"\n**\nÉxito al conectar con bd:\n {os.path.join(RUTA,nombr_bd)}\n**\n")
except:
    raise Exception("\nError de Conexión con bd SQL\n")




class Verificar:
    '''Verificación de campos.'''
    def __init__(self) -> None:
        pass

    def formato(lista_datos):
        '''Aviso emergente sobre caracteres no válidos y doble coma'''
        for i in range(len(lista_datos)):
            if re.search(r'[$%&"\'()a-zA-Z¡!¿?#\][/\\]', lista_datos[i]):
                messagebox.showwarning("Advertencia", f"Valor no válido       \n\
EN: {lista_datos[i]}")
                
        for dato in lista_datos:
            if dato.count(".") > 1 or dato.count(",") > 1:
                messagebox.showwarning("Advertencia", f"Decimal no válido     \n\
EN: {dato}")

    def decim_a_punt(lista_datos:list[str]):
        '''Corregir marcador decimales.'''
        salida = []
        for dato in lista_datos:
            if "," in dato:
                dato_modificado = dato.replace(",", ".")
                salida.append(dato_modificado)
            else:
                salida.append(dato)
        return salida


class MensErr(FloatLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        
        
        
    def cerrar(self):
        self.dismis()


class Crud():
    '''Registrar medidas: al Excel que venía usando,
    y a una base SQL (métodos CRUD).
    \nSQLite\n
    Permite nulos en todos los campos menos fecha.\n 
    La clave primaria es compuesta de la fecha y la
    fecha y hora del registro.
    '''
    
    def __init__(self) -> None:
        self.tb = Registro

    def alta(self, fecha, peso, medsomx, medsomn, medbomx, medbomn):
        datos = [peso.text, medsomx.text, medsomn.text, medbomx.text, medbomn.text]
        
        # Verificar campos
        Verificar.formato(datos)
        datos_v = Verificar.decim_a_punt(datos)
        
        # introduce nulo (None) para salvar el error de coerción  
        for i in range(len(datos_v)):
            if datos_v[i]== '': 
                datos_v[i] = None
            else:
                datos_v[i] = float(datos_v[i])

        try:
            self.tb.create(
                    fecha = fecha,
                    fecha_regist = hora(),
                    peso = datos_v[0],
                    diametr_sob_ombl_mx = datos_v[1],
                    diametr_sob_ombl_mn = datos_v[2],
                    diametr_baj_ombl_mx = datos_v[3],
                    diametr_baj_ombl_mn = datos_v[4],
            )
            print("Guardado registro en SQL")
        except:
            raise Exception("ERROR al crear registro")
    
    def baja():
        ...

    def modificacion():
        ...

# Eventos bontones y declaración de app
class PesoApp(BoxLayout):

    # Esto es un enlace bidireccional (entra al .kv por 
    #  root.fechainput, vuelve como fechainput: fecha.text) *
    fechainput = StringProperty()

    peso = ObjectProperty(None)
    medsomx = ObjectProperty(None)
    medsomn = ObjectProperty(None)
    medbomx = ObjectProperty(None)
    medbomn = ObjectProperty(None)

    def __init__(self, **kwargs):
        '''root'''
        super().__init__(**kwargs)
        self.segpeso_cfg = Confg()
        self.fechainput = FECHA_SIS # * el valor defoult  
        self.salida_datos = Crud()

    def guardar(self):
        self.salida_datos.alta(self.fechainput, 
            self.peso, self.medsomx,
            self.medsomn, self.medbomx,
            self.medbomn)

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

    def adv_form_emerg(e):
        aviso = Popup(title="Advertencia",
            content=MensErr(error=e),
            size_hint=(None, None),
            size=(500,500))
            
        aviso.open()

class MainApp(App):
    title = "Seguimiento Peso"
    def build(self):
        return PesoApp()
        
        
if __name__ == '__main__':
    MainApp().run()