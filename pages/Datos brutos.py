import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px
import warnings
import streamlit as st
import time
from pandas import Grouper

warnings.filterwarnings('ignore')

#convertir el archivo y descargarlo desde el inico
@st.cache_data
def convierte_csv(df):
    return df.to_csv(index=False, sep='#').encode('utf-8')


def mensaje_exito():
    exito = st.success('Archivo descargado con exito',icon='✅')
    time.sleep(8)

##Funciones para el format

def formato_numero(valor, prefijo=''):
    for unidad in['','mil']:
        if valor < 1000:
            return f'{prefijo} {valor:.2f} {unidad}'
        valor /= 1000
    return f'{prefijo} {valor:.2f} millones'


st.set_page_config(layout='wide')

st.title('Datos en Bruto') #els hopping trolleyt  es un icono

url = 'https://ahcamachod.github.io/productos'

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')#se crtea un objeto navegable con el soup y se traduce a html
datos = pd.read_json(soup.pre.contents[0])#se traen del objeto sub los datos
datos['Fecha de Compra'] = pd.to_datetime(datos['Fecha de Compra'], format='%d/%m/%Y')


with st.expander('Columnas'):
    columnas = st.multiselect('Selecciona las columnas',list
    (datos.columns),list(datos.columns))

st.sidebar.title('Filtros')

with st.sidebar.expander('Nombre del producto'):
    productos =  st.multiselect('Selecciona el Precio',datos['Producto'].unique(), datos['Producto'].unique())

with st.sidebar.expander('Precio del producto'):
  precio = st.slider('Selecciona el precio',0,5000000,(0,5000000))

with st.sidebar.expander('Fecha de compra'):
  fecha_compra = st.date_input('Selecciona la fecha',(datos['Fecha de Compra'].min(),datos['Fecha de Compra'].max()))

#se genera un filtrado query string
query = """
Producto in @productos and \
@precio[0] <= Precio <= @precio[1] and \
@fecha_compra[0] <= `Fecha de Compra` <= @fecha_compra[1]
"""

#### Actividad de Práctica ->  Creación de filtros ####

with st.sidebar.expander('Categoría del Producto'):
    categoria = st.multiselect('Selecciona las categorías', datos['Categoría del Producto'].unique(), datos['Categoría del Producto'].unique())
with st.sidebar.expander('Costo de envío'):
    envio = st.slider('Costo de envío', 0,200000, (0,200000))
with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecciona los vendedores', datos['Vendedor'].unique(), datos['Vendedor'].unique())
with st.sidebar.expander('Lugar de Compra'):
    lugar_compra = st.multiselect('Selecciona el Lugar de Compra', datos['Lugar de Compra'].unique(), datos['Lugar de Compra'].unique())
with st.sidebar.expander('Calificación de la Compra'):
    calificacion = st.slider('Calificación',1,5, value = (1,5))
with st.sidebar.expander('Método de pago'):
    tipo_pago = st.multiselect('Selecciona el método de pago',datos['Método de pago'].unique(), datos['Método de pago'].unique())
with st.sidebar.expander('Cantidad de cuotas'):
    ct_cuotas = st.slider('Cantidad de cuotas', 1, 24, (1,24))

query = '''
Producto in @productos and \
@precio[0] <= Precio <= @precio[1] and \
@fecha_compra[0] <= `Fecha de Compra` <= @fecha_compra[1] and \
`Categoría del Producto` in @categoria and \
@envio[0] <= `Costo de envío` <= @envio[1] and \
Vendedor in @vendedores and \
`Lugar de Compra` in @lugar_compra and \
@calificacion[0]<= Calificación <= @calificacion[1] and \
`Método de pago` in @tipo_pago and \
@ct_cuotas[0] <= `Cantidad de cuotas` <= @ct_cuotas[1]
'''
###

datos_filtrados = datos.query(query)
datos_filtrados = datos_filtrados[columnas]

st.dataframe(datos_filtrados)
st.markdown(f'La tabla posee :blue[{datos_filtrados.shape[0]}], filas y :blue[{datos_filtrados.shape[1]}] columnas')

st.markdown('Escriba un nombre para el archivo')

col1, col2 = st.columns(2)

with col1:
    nombre_archivo = st.text_input('',
    label_visibility='collapsed', value='datos')
    nombre_archivo += '.csv'

with col2:
    st.download_button('Realiza la descarga de la tabla en formato csv',
                       data=convierte_csv(datos_filtrados),
                       file_name=nombre_archivo, mime='text/csv',
                       on_click=mensaje_exito)