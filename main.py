# Dependencias Kivy:
import kivy
kivy.require('1.9.0')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
## from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ObjectProperty
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
## from kivy.uix.filechooser import FileChooser # por ahora prefiero evitarlo

# Dependencias bases de datos:
from peewee import  SqliteDatabase, Model, DateField, FloatField, CharField, CompositeKey
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

# Otras dependencias
import time
import os
from plyer import filechooser
import re
import configparser


Config.set('graphics', 'width', 500)
Config.set('graphics', 'height', 300)
RUTA = os.getcwd()
FECHA_SIS = time.strftime("%d/%m/%Y", time.localtime(time.time()))

def hora() -> str:
    '''Para generar claves primarias.'''
    hora = time.strftime("%d/%m/%Y-%H:%M:%S", time.localtime(time.time()))
    return hora

# Archivo de configuración
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
            self.ruta_xlsx = self.config["RUTAS"]["xlsx"]
            self.ruta_xlsx_pr = self.config["RUTAS"]["xlsx_pr"]
            self.ARCH = self.config["NOMBRES"]["xlsx_pr"]
        except:
            self.config["RUTAS"] = {"xlsx": "0"}
            with open(self.NOMBRE, 'w') as segpeso:
                self.config.write(segpeso)
            raise Exception("Sin archivo cfg, creado con valor nulo")
        
        print("Ruta a xlsx: ",self.ruta_xlsx)

    def guardar_ruta(self, nueva_ruta:str):
        '''Guardar la ruta en .cfg
        (llamar en método del botón)'''
        self.config["RUTAS"] = {"xlsx": nueva_ruta}
        with open(self.ruta_cfg, 'w') as segpeso:
            self.config.write(segpeso)

# Clases de conexión a bases ###############################
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

## Conexión con libro excel
class LibroExcel:
    '''Conexión con archivo excel'''
    def __init__(self):
        config = Confg()
        self.RUTA_XLSX = os.path.join(config.ruta_xlsx_pr, config.ARCH) 
        dir_cont = os.listdir(RUTA)
        ARCH = config.ARCH
        # Algoritmo para crear/leer condicionalmente el xlsx
        if not ARCH in dir_cont:
            print("Archivo excel faltante en directorio elegido.")
            print("Creando... ", "\n\t", self.RUTA_XLSX,"\n")
            self.libro = openpyxl.Workbook()
            hoja = self.libro.active
            hoja.title = "Tabla_medidas"
            self.hoja = self.libro["Tabla_medidas"]
            self.hoja.append(("fecha", "peso", "medsomx", "medsomn", "medbomx", "medbomn"))

            self.libro.save(self.RUTA_XLSX)

            self.libro = openpyxl.load_workbook(self.RUTA_XLSX)
        else:
            print("Cargando excel... : ", "\n\t", self.RUTA_XLSX,"\n")
            self.libro = openpyxl.load_workbook(self.RUTA_XLSX)

        self.hoja = self.libro["Tabla_medidas"]
    
    def ult_fila(self, hoja):
        for i in range(1, hoja.max_column + 1): 
            cell_obj = hoja.cell(row = hoja.max_row, column = i) 
            print(cell_obj.value, end = " ")

###############################


class Verificar:
    '''Verificación de campos.'''
    def __init__(self) -> None:
        #lista_datos = lista_datos
        pass

    def formato(lista_datos:list[str]) -> list[bool]:
        '''Aviso emergente sobre caracteres no válidos y doble coma'''
        l_e = [True for _ in range(len(lista_datos))]
        for i in range(len(lista_datos)):
            if re.search(r'[$%&"\'()a-zA-Z¡!¿?#\][/\\]', lista_datos[i]):
                print(f"Valor no válido       \n # EN: {lista_datos[i]} (Verificar.formato)")
                l_e[i] = False 
        for i in range(len(lista_datos)):
            if lista_datos[i].count(".") > 1 or lista_datos[i].count(",") > 1:
                print(lista_datos[i], "tiene +1 dec",  l_e[i])
                l_e[i] = False
        return l_e

    def decim_a_punt(lista_datos:list[str]) -> list[str]:
        '''Corregir marcador decimales.'''
        salida = []
        for dato in  lista_datos:
            if "," in dato:
                dato_modificado = dato.replace(",", ".")
                salida.append(dato_modificado)
            else:
                salida.append(dato)
        return salida


class MensErr(BoxLayout):
    mens_err = StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mens_err = kwargs["mens_err"]


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
        self.lib_excel = LibroExcel()

    def alta(self, fecha_s:str, datos_v:list):

        # ALTA en SQL
        try:
            self.tb.create(
                    fecha = fecha_s,
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
    
        # ALTA en Excel
        try:
            regis_exc = tuple([fecha_s] + datos_v)
            print(regis_exc)

            self.lib_excel.hoja.append(regis_exc)
            
            self.lib_excel.libro.save(self.lib_excel.RUTA_XLSX)
        except:
            raise Exception("Excel: Error de guardado")
    def baja():
        ...

    def modificacion():
        ...

# Eventos bontones y declaración de app ###############################
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

        datos = [self.peso.text, self.medsomx.text, self.medsomn.text, 
                 self.medbomx.text, self.medbomn.text]
        print(datos)
        ## Verificar campos ##
        err_form = Verificar.formato(datos) 

        # Si las entradas son válidas:
        if False not in err_form:

            # Pasar todos las comas a puntos
            datos_v = Verificar.decim_a_punt(datos)
        
            # introduce nulo (None) para salvar el error de coerción  
            try:
                for i in range(len(datos_v)):
                    if datos_v[i]== '': 
                        datos_v[i] = None
                    else:
                        datos_v[i] = float(datos_v[i])
            except:
                raise Exception("Imposible convertir a float")
            
            # >>> Entrada a Crud.Alta >>>
            try:
                self.salida_datos.alta(self.fechainput, datos_v)
            except:
                raise Exception("Error en alta de registro.")
        
        # Si hay entradas erroneas:
        else:
            errores = []
            print(err_form)
            for i in range(len(err_form)):
                if err_form[i] == False:
                    errores.append(datos[i])
            errores = '\n                 -> '.join(errores)
            PesoApp.adv_emerg(error=f"Valor/es no válido/s:\n                 -> {errores}")

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

    # Métodos AVISO emergente ####
    @classmethod
    def adv_emerg(self, error):
        '''Declaración y apertura de ventana de aviso emergente.'''
        print(error, "(dentro de adv_emerg)")
        self.aviso = Popup(title="Advertencia",
            title_size=25,
            content=MensErr(mens_err=error),
            size_hint=(None, None),
            size=(300,300))
        
        self.aviso.open()

    @classmethod
    def cerrar(self):
        '''Evento de cierre para el botón del aviso emergente'''
        print("cierra emerg")
        self.aviso.dismiss()


class MainApp(App):
    title = "Seguimiento Peso"
    def build(self):
        return PesoApp()


if __name__ == '__main__':
    MainApp().run()