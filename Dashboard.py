import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px
import warnings
import streamlit as st

warnings.filterwarnings('ignore')

##Funciones para el format

def formato_numero(valor, prefijo=''):
    for unidad in['','mil']:
        if valor < 1000:
            return f'{prefijo} {valor:.2f} {unidad}'
        valor /= 1000
    return f'{prefijo} {valor:.2f} millones'

st.title('Dashboard de Ventas:shopping_trolley:') #els hopping trolleyt  es un icono

url = 'https://ahcamachod.github.io/productos'

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')#se crtea un objeto navegable con el soup y se traduce a html
datos = pd.read_json(soup.pre.contents[0])#se traen del objeto sub los datos

col1,col2 = st.columns(2) #se generan dos columnas por las dos variablesque tenemos

with col1:
    st.metric('Facturación Total',formato_numero(datos['Precio'].sum(),'COP'))
with col2:
    st.metric('Cantidad de Ventas',formato_numero(datos.shape[0]))


#streamlit va mostrasndo en el orden que colocamos el codigo por lo que hay que tener cuidadp
#por lo que el st.dataframe toca ponerlo después de otros parametros

st.dataframe(datos) #con esto se llama la base de datos en el localhost