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
from kivy.uix.screenmanager import Screen, ScreenManager
## from kivy.uix.filechooser import FileChooser # por ahora prefiero evitarlo

# Dependencias bases de datos:
from peewee import  SqliteDatabase, Model, DateField, FloatField, CharField, CompositeKey
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
# import xlwings as xw

# Otras dependencias
import time
import os
from platform import system
from plyer.facades import FileChooser
import re
import configparser
import threading

# valores defoult
SIS = system()
RUTA = os.getcwd()
FECHA_SIS = time.strftime("%d/%m/%Y", time.localtime(time.time()))
NOM_CFG = 'segpeso.cfg'
NOM_DEFOULT = {
    "xlsx": "registro_medidas.xlsx",
    "xlsx_pr": "prueba.xlsx",
    "bd_sql":"registro.db"}

global _config
if NOM_CFG in os.listdir():
    _config = True
else:
    _config = False

def hora() -> str:
    '''Para generar claves primarias.'''
    hora = time.strftime("%d/%m/%Y-%H:%M:%S", time.localtime(time.time()))
    return hora


class PrimEjec(Screen):
    pass


# Archivo de configuración
class Confg:
    '''Rutas a bases de datos.'''
    
    NOMBRE = NOM_CFG
    config = configparser.ConfigParser()
    wdir = RUTA
    ruta_cfg = os.path.join(wdir, NOMBRE)
    
    def __init__(self) -> None:
        '''Lee/Crea .cfg en dir trabajo.'''

        try:        
            Confg.cargar_conf()
        except:
            #Confg.cfg_defoult()
            print("!!! - Sin archivo .cfg en dir. de trabajo - !!!")
        # finally:
        #     Confg.cargar_conf()
        #     print("Ruta a xlsx: ",self.ruta_xlsx)
        
    @classmethod
    def cargar_conf(self):
        print("Cargando configuración...")
        self.config.read(self.NOMBRE)
        self.ruta_xlsx = self.config["RUTAS"]["xlsx"]
        #self.ARCH = self.config["NOMBRES"]["xlsx"]
        self.SIS = self.config["OPCIONES"]["sistema"]

        # "xlsx_pr"  es para el desarrollo !!!!
        self.ruta_xlsx_pr = self.config["RUTAS"]["xlsx_pr"]
        self.ARCH = self.config["NOMBRES"]["xlsx_pr"]
    
    @classmethod
    def cfg_defoult(self):    
        self.config["NOMBRES"] = NOM_DEFOULT
        # Directorio de ejecución por defercto
        self.config["RUTAS"] = {"xlsx": f"{RUTA}", "xlsx_pr": f"{RUTA}", 
            "bd_sql":f"{RUTA}"}

        # Guardad sistema (platform)
        self.config["OPCIONES"] = {"sistema":SIS}

        with open(Confg.NOMBRE, 'w') as segpeso:
            self.config.write(segpeso)
        #raise Exception("Sin archivo cfg, creado con valor nulo")
        print("Sin archivo cfg, creado con valor nulo")

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


class ConfEmerg(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MensErr(BoxLayout):
    mens_err = StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mens_err = kwargs["mens_err"]


class Dialog(BoxLayout):
    mensaje = StringProperty()
    si = StringProperty()
    no = StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mensaje = kwargs["mensaje"]
        self.si = kwargs["si"]
        self.no = kwargs["no"]
    
    def ruta_sqlite(self):
        filec = FileChooser.choose_dir()
        print("\n", filec, "\n")
    def ruta_xlsx(self):
        ...


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

        # ALTA en SQLite
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


class Prueba(Screen):
    pass


# Eventos bontones y declaración de app ###############################

Config.set('graphics', 'width', 700)
Config.set('graphics', 'height', 350)


class PesoApp(Screen):
    '''ROOT'''
    # Esto es un enlace bidireccional (entra al .kv por 
    #  root.fechainput, vuelve como fechainput: fecha.text) *
    fechainput = StringProperty()
    rutaxlsx = StringProperty()

    peso = ObjectProperty(None)
    medsomx = ObjectProperty(None)
    medsomn = ObjectProperty(None)
    medbomx = ObjectProperty(None)
    medbomn = ObjectProperty(None)

    def __init__(self, **kwargs):
        '''root init. Secuencia de configuración inicial y
        conexiones.'''
        super().__init__(**kwargs)
        
        if _config:
            self.segpeso_cfg = Confg()
            self.sistem = self.segpeso_cfg.SIS
            self.fechainput = FECHA_SIS # * el valor defoult  
            self.salida_datos = Crud()
            self.rutaxlsx = self.segpeso_cfg.ruta_xlsx_pr
            self.nom_xlsx = self.segpeso_cfg.ARCH
        else:
            # seteo defoult
            self.sistem = SIS
            self.fechainput = FECHA_SIS 
            self.salida_datos = Crud()
            self.rutaxlsx = RUTA
            self.nom_xlsx = NOM_DEFOULT["xlsx_pr"]

    def guardar(self):
        if not self.archivo_cfg:        
            print("SIN cfg")
            PesoApp.dialog_emerg("SIN REFERENCIAS.", 
                "No se encuentra configuraración previa\n\
¿Elegir nombres / ubicaciones?", "Configurar",
                "          Usar\n Predeterminados")
            
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

    def mas(self):
        print("Próximamente...")

        # Pruebas eventos (no relacionado a funcionalidad de mas())
        '''print("Modificando ruta")
        ruta_usr = filechooser.open_file(
            title="Elegir ruta a archivo xlsx a crear..."
            )[0]
        self.segpeso_cfg.guardar_ruta(ruta_usr)
        print("Ruta guardada en .cgf = ", ruta_usr)'''
    
    def comando_cmd(self):
            '''Comando de apertura para el shell del os'''
            print(self.sistem)
            if self.sistem == "Windows":
                rut_compl = os.path.join(self.rutaxlsx, self.nom_xlsx)
                print(rut_compl)
                os.system(f'cmd /k start excel.exe {rut_compl}')
            elif self.sistem == "Linux":
                rut_compl = os.path.join(self.rutaxlsx, self.nom_xlsx)
                print(rut_compl)
                os.system(f'libreoffice {rut_compl}')            
            else:
                raise Exception("Abrir excel: sin comando válido")

    def abrir_xlsx(self):
        '''Lanzar app excel/equivalente en hilo.'''
        t = threading.Thread(target=self.comando_cmd)
        t.daemon = True
        t.start()

    # Métodos Ventanas emergentes ####
    @classmethod
    def dialog_emerg(self, titulo:str, mns:str, si:str, no:str):
        '''Dialogo emergente.'''
        print(mns)
        self.dialog = Popup(title=titulo,
            title_size=20,
            content=Dialog(mensaje=mns, si=si, no=no),
            size_hint=(None, None),
            size=(300,250))
        
        self.dialog.open()
        
    @classmethod
    def cerrar_dialog(self):
        self.dialog.dismiss()
    
    @classmethod
    def a_conf(self):
        PesoApp.configurar()
        self.dialog.dismiss()
        
    @classmethod
    def adv_emerg(self, error):
        '''Declaración y apertura de ventana de aviso emergente.'''
        print(error)
        self.aviso = Popup(title="Advertencia",
            title_size=25,
            content=MensErr(mens_err=error),
            size_hint=(None, None),
            size=(300,300))
        
        self.aviso.open()

    @classmethod
    def cerrar_adv_emerg(self):
        '''Evento de cierre para el botón del aviso emergente'''
        print("cierra emerg")
        self.aviso.dismiss()

    @classmethod
    def configurar(self):
        '''Declaración y apertura de ventana de configuración.'''
        print("Abrir ")
        self.v_config = Popup(title="Configuración",
            title_size=25,
            content=ConfEmerg(),
            size_hint=(None, None),
            size=(300,300))
        
        self.v_config.open()

    @classmethod
    def cerrar_configurar(self):
        '''Evento de cierre para el botón del aviso emergente'''
        print("cierra emerg")
        self.v_config.dismiss()


# Declaración de aplicación  #######################
class MainApp(App):
    title = "Seguimiento Peso"
    def build(self):
        # Administrador de pantallas
        inicio = ScreenManager()
        inicio.add_widget(PrimEjec(name = "sinconf"))
        inicio.add_widget(ConfEmerg(name = "configur"))
        inicio.add_widget(Prueba(name = "pr"))
        inicio.add_widget(PesoApp(name = "app"))
        
        ## lanzar aviso de config, si no hay .cfg
        if _config:
            print("intenta iniciar app")
            inicio.current = "app"
        else:
            print("No detecta .cfg")
            inicio.current = "sinconf"            

        return inicio

if __name__ == '__main__':
    MainApp().run()