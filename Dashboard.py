import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px
import warnings
import streamlit as st
from pandas import Grouper

warnings.filterwarnings('ignore')


##Funciones para el format

def formato_numero(valor, prefijo=''):
    for unidad in['','mil']:
        if valor < 1000:
            return f'{prefijo} {valor:.2f} {unidad}'
        valor /= 1000
    return f'{prefijo} {valor:.2f} millones'


st.set_page_config(layout='wide')

st.title('Dashboard de Ventas:shopping_trolley:') #els hopping trolleyt  es un icono

url = 'https://ahcamachod.github.io/productos'

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')#se crtea un objeto navegable con el soup y se traduce a html
datos = pd.read_json(soup.pre.contents[0])#se traen del objeto sub los datos
datos['Fecha de Compra'] = pd.to_datetime(datos['Fecha de Compra'], format='%d/%m/%Y')

#Desafío: cantidad de ventas


#Nuestro dashboard estaba comenzando a cargarse de información y, para agregar gráficos y expandir el análisis de los datos, creamos nuevas pestañas usando el método st.tabs().
# Esta es una solución excelente para segmentar el contenido en la aplicación y facilitar la navegación del usuario.

#En una de estas pestañas, se planteó el desafío de incluir gráficos relacionados con la cantidad de ventas. Ha llegado el momento de practicar y resolver este desafío, que se puede dividir en 4 partes:

#Construir un gráfico de mapa con la cantidad de ventas por estado.
#Construir un gráfico de líneas con la cantidad de ventas mensual.
#Construir un gráfico de barras con los 5 estados con mayor cantidad de ventas.
#Construir un gráfico de barras con la cantidad de ventas por categoría de producto.

ventas_region = pd.DataFrame(datos.groupby('Lugar de Compra')['Precio'].count())
ventas_region = datos.drop_duplicates(subset='Lugar de Compra')[['Lugar de Compra', 'lat', 'lon']].merge(ventas_region, left_on='Lugar de Compra', right_index=True).sort_values('Precio', ascending=False)


#tabla de contenido con la cantidad de ventas mensual
ventas_mensual = pd.DataFrame(datos.set_index('Fecha de Compra').groupby(pd.Grouper(freq='M'))['Precio'].sum()).reset_index()
ventas_mensual['Año'] = ventas_mensual['Fecha de Compra'].dt.year
ventas_mensual['Mes'] = ventas_mensual['Fecha de Compra'].dt.month_name()

#tabla de cantidad de ventas por categoria del producto
ventas_categorias = pd.DataFrame(datos.groupby('Categoría del Producto')['Precio'].count().sort_values(ascending=False))


#Filtrado por regon y año
regiones_dict = {'Bogotá':'Andina', 'Medellín':'Andina', 'Cali':'Pacífica', 'Pereira':'Andina','Barranquilla':'Caribe', 'Cartagena':'Caribe','Cúcuta':'Andina', 'Bucaramanga':'Andina', 'Riohacha':'Caribe', 'Santa Marta':'Caribe', 'Leticia':'Amazónica', 'Pasto':'Andina','Manizales':'Andina', 'Neiva':'Andina', 'Villavicencio':'Orinoquía', 'Armenia':'Andina', 'Soacha':'Andina','Valledupar':'Caribe', 'Inírida':'Amazónica'}

datos['Region'] = datos['Lugar de Compra'].map(regiones_dict)
datos['Año'] = datos['Fecha de Compra'].dt.year

#sidebar para la interaccion con la api
regiones = ['Colombia','Caribe','Andina','Pacífica','Orinoquía','Amazónica']

st.sidebar.title('Filtro')
region = st.sidebar.selectbox('region', regiones)
if region == 'Colombia':
    datos = datos.loc[datos['Region'] != 'Colombia']
else:
    datos = datos.loc[datos['Region'] == 'region']

todos_anos = st.sidebar.checkbox('Datos de todo el periodo', value=True)
if todos_anos:
    datos = datos
else:
    ano = st.sidebar.slider('Año', 2020,2023)
    datos = datos.loc[datos['Año'] == ano]

filtro_vendedores = st.sidebar.multiselect('Vendedores', datos.Vendedor.unique())
if filtro_vendedores:
    datos = datos[datos['Vendedor'].isin(filtro_vendedores)]# con esto se genera un multiselefty para poder seleccionar multiples vendedores

##Creacion de features

fact_ciudades = datos.groupby('Lugar de Compra')[['Precio']].sum()


fact_ciudades = datos.drop_duplicates(subset='Lugar de Compra')[['Lugar de '
                                                                 'Compra', 'lat', 'lon']].merge(fact_ciudades, left_on='Lugar de Compra',
                                                                                                right_index=True).sort_values('Precio', ascending=False)

facturacion_mensual = datos.set_index('Fecha de Compra').groupby(pd.Grouper
(freq='ME'))['Precio'].sum().reset_index()

facturacion_mensual['Año'] = facturacion_mensual['Fecha de Compra'].dt.year
facturacion_mensual['Año'] = facturacion_mensual['Fecha de Compra'].dt.year
facturacion_mensual['Mes'] = facturacion_mensual['Fecha de Compra'].dt.month_name('es')

facturacion_cat = datos.groupby('Categoría del Producto')[['Precio']].sum().sort_values('Precio', ascending=False)

vendedores = pd.DataFrame(datos.groupby('Vendedor')['Precio'].agg(['sum', 'count']))


##Creacion de graficos
fig_fact = px.scatter_geo(fact_ciudades, lat='lat', lon='lon',
                          scope='south america', size='Precio',
                          template='seaborn', hover_name='Lugar de Compra',
                          hover_data={'lat':False, 'lon':False},
                          title= 'Facturación or Ciudad')

fig_fact.update_geos(fitbounds='locations')

fig_facturacion_mensual = px.line(facturacion_mensual, x='Mes', y='Precio',
markers=True, range_y=(0,facturacion_mensual.max()),color='Año',
line_dash='Año', title = 'Facturación menusal')

fig_facturacion_mensual.update_layout(yaxis_title='Facturación')

###creacion de lgrafico de barras
fig_facturacion_ciudades = px.bar(fact_ciudades.head(), x='Lugar de Compra', y='Precio',
                                  text_auto=True, title='Top de Ciudades(Facturacion)')

fig_facturacion_ciudades.update_layout(yaxis_title='Facturacion')

fig_facturacion_cat = px.bar(facturacion_cat, text_auto=True, title='Facturacion por Categoria')

fig_facturacion_cat.update_layout(yaxis_title='Facturacion')

# grafico de mapa cantidad de ventas por region
fig_mapa_ventas = px.scatter_geo(ventas_region,
                                 lat='lat',
                                 lon='lon',
                                 scope='south america',
                                 # fitbounds='locations',
                                 template='seaborn',
                                 size='Precio',
                                 hover_name='Lugar de Compra',
                                 hover_data={'lat': False, 'lon': False},
                                 title='Ventas por Estado')

# grafico de cantidad de ventas mensual

fig_ventas_mensual = px.line(ventas_mensual,
                             x='Mes',
                             y='Precio',
                             markers=True,
                             range_y=(0, ventas_mensual['Precio'].max()),  # Cambié esto
                             color='Año',
                             line_dash='Año',
                             title='Cantidad de ventas mensual'
                             )

fig_ventas_mensual.update_layout(yaxis_title='Cantidad de ventas')

###Grafico de las 5 regiones con mayor cantidad de ventas
fig_ventas_region = px.bar(ventas_region.head(),
                           x='Lugar de Compra',
                           y='Precio',
                           text_auto=True,
                           title='Top 5 estados')
fig_ventas_region.update_layout(yaxis_title='Cantidad de Ventas')

###Grafico de cantidad de ventas por categoria de p;roducto

fig_ventas_categorias = px.bar(ventas_categorias,
                               text_auto=True,
                               title='Ventas por Categorias'
                               )
fig_ventas_categorias.update_layout(showlegend=False, yaxis_title = 'Cantidad de Ventas')





###

#uso de tab
tab1,tab2,tab3 =st.tabs(['Facturación', 'Cantidad de Ventas', 'Vendedores'])

with tab1:
    col1,col2 = st.columns(2) #se generan dos columnas por las dos variablesque tenemos

    with col1:
        st.metric('Facturación Total',formato_numero(datos['Precio'].sum(),'COP'))
        st.plotly_chart(fig_fact, use_container_width=True)
        st.plotly_chart(fig_facturacion_ciudades, use_container_width=True)
    with col2:
        st.metric('Cantidad de Ventas',formato_numero(datos.shape[0]))
        st.plotly_chart(fig_facturacion_mensual, use_container_width=True)
        st.plotly_chart(fig_facturacion_cat, use_container_width=True)

with tab2:
    col1,col2 = st.columns(2) #se generan dos columnas por las dos variablesque tenemos

    with col1:
        st.metric('Facturación Total',formato_numero(datos['Precio'].sum(),'COP'))
        st.plotly_chart(fig_mapa_ventas, use_container_width=True)
        st.plotly_chart(fig_ventas_region, use_container_width=True)
    with col2:
        st.metric('Cantidad de Ventas',formato_numero(datos.shape[0]))
        st.plotly_chart(fig_ventas_mensual, use_container_width=True)
        st.plotly_chart(fig_ventas_categorias, use_container_width=True)


with tab3:

    ct_vendedores = st.number_input('Cantidad de vendedores', 2,10,5) #los numros generan el min, max y el valor en default
    col1,col2 = st.columns(2) #se generan dos columnas por las dos variablesque tenemos

    with col1:
        st.metric('Facturación Total',formato_numero(datos['Precio'].sum(),'COP'))
        fig_facturacion_vendedores = px.bar(vendedores[['sum']].sort_values('sum').head(ct_vendedores),x='sum',
                                    y=vendedores[['sum']].sort_values('sum').head(ct_vendedores).index,
                                    text_auto=True, title=f'Top {ct_vendedores} vendedores (Facturación)')
        st.plotly_chart(fig_facturacion_vendedores)
    with col2:
        st.metric('Cantidad de Ventas',formato_numero(datos.shape[0]))
        fig_cantidad_vendedores = px.bar(vendedores[['count']].sort_values('count').head(ct_vendedores), x='count',
                                            y=vendedores[['count']].sort_values('count').head(ct_vendedores).index,
                                            text_auto=True, title=f'Top {ct_vendedores} vendedores (Cantidad de Ventas)')


#streamlit va mostrasndo en el orden que colocamos el codigo por lo que hay que tener cuidadp
#por lo que el st.dataframe toca ponerlo después de otros parametros

st.dataframe(datos) #con esto se llamcda la base de datos en el localhost

