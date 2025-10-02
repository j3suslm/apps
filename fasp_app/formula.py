import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image


# --- Funciones de Cálculo del Índice ---
def min_max_normalize(series, direction='positive'):
    """
    Normaliza una serie de datos entre 0 y 1 usando el método Min-Max.
    Si la dirección es 'negative', se invierte (Alto = Malo se convierte en Alto = Bueno).
    """
    min_val = series.min()
    max_val = series.max()

    if max_val == min_val:
        return pd.Series(0.5, index=series.index) # Retorna 0.5 si todos los valores son iguales

    if direction == 'positive':
        # (X - Min) / (Max - Min) -> Un valor más alto resulta en una puntuación más alta
        return (series - min_val) / (max_val - min_val)
    elif direction == 'negative':
        # (Max - X) / (Max - Min) -> Un valor más bajo (mejor) resulta en una puntuación más alta
        return (max_val - series) / (max_val - min_val)
    else:
        raise ValueError("La dirección debe ser 'positive' o 'negative'")

def calculate_index(df, weights):
    """Calcula el Índice Compuesto Normalizado."""

    # 1. Normalización de Variables
    # Gasto y Policías son variables POSITIVAS (más es mejor)
    df['Gasto_norm'] = min_max_normalize(df['Gasto por Hab'], direction='positive')
    df['Policia_norm'] = min_max_normalize(df['Policías por 100k'], direction='positive')

    # Tasa de Criminalidad es una variable NEGATIVA (menos es mejor, por lo tanto, se invierte)
    df['Crimen_norm'] = min_max_normalize(df['Tasa de Criminalidad'], direction='negative')

    # 2. Aplicación de Ponderadores
    df['Índice Normalizado'] = (
        df['Gasto_norm'] * weights['Gasto'] +
        df['Policia_norm'] * weights['Policía'] +
        df['Crimen_norm'] * weights['Crimen']
    )

    # El índice final también se normaliza a un rango de 0 a 1 para asegurar comparabilidad
    df['Índice Final (0-1)'] = min_max_normalize(df['Índice Normalizado'], direction='positive')

    return df


# Datos de ejemplo para diferentes regiones/municipios
data = {
    'Región': ['Central', 'Norte', 'Sur-Este', 'Occidente', 'Metropolitana'],
    'Gasto por Hab': [500, 320, 780, 450, 610], # Gasto público en USD/habitante
    'Policías por 100k': [350, 210, 420, 280, 500], # Policías por 100,000 habitantes
    'Tasa de Criminalidad': [4500, 6800, 3100, 5500, 4000] # Delitos por 100,000 habitantes (variable negativa)
}
df_original = pd.DataFrame(data)
df_original = df_original.set_index('Región')


# page settings
# blog home link
st.markdown('<a href="https://tinyurl.com/sesnsp-dgp-blog" target="_self">Home</a>', unsafe_allow_html=True)

# hide streamlit logo and footer
hide_default_format = """
    <style>
    #MainMenu {visibility: hidden; }
    footer {visibility: hidden;}
    </style>
    """

# load icon image
im = Image.open('logo.png')

# page layout config and add image
st.set_page_config(layout="wide", page_title="Fórmula FASP", page_icon=im)

# set title and subtitle
st.markdown("<h1><span style='color: #691c32;'>Asignación de Fondos FASP para Seguridad Pública</span></h1>",
    unsafe_allow_html=True)

# author, date
st.caption('Jesús LM')
st.caption('Octubre, 2025')


# --- sidebar
# sidebar image and text
st.sidebar.image('sesnsp.png')

# ponderadores
st.markdown(hide_default_format, unsafe_allow_html=True)
st.sidebar.header("Ponderaciones")
st.sidebar.markdown("Utiliza los sliders para cambiar la ponderación de cada indicador.")
    
# customize color of sidebar and text
st.markdown("""
    <style>
        /* 1. Target the main content area background */
        [data-testid="stAppViewBlockContainer"] {
            background-color: #808080;
        }
        /* Sidebar background */
        [data-testid=stSidebar] {
            background-color: #691c32;
            color: #ffff;
        }
        /* Target all text elements within the sidebar (labels, markdown, sliders, etc.) */
        [data-testid="stSidebar"] * {
            color: white !important; 
        }
    </style>
    """, unsafe_allow_html=True)


# Sliders for weights
# Los valores se limitan para que la suma siempre sea 1
w_gasto = st.sidebar.slider(
    'Peso: Gasto por Habitante (Alto = Bueno)',
    min_value=0.0, max_value=1.0, value=0.40, step=0.05, key='gasto'
)
w_policia = st.sidebar.slider(
    'Peso: Policías por 100k (Alto = Bueno)',
    min_value=0.0, max_value=1.0, value=0.30, step=0.05, key='policia'
)
w_crimen = st.sidebar.slider(
    'Peso: Tasa de Criminalidad (Alto = Malo)',
    min_value=0.0, max_value=1.0, value=0.30, step=0.05, key='crimen'
)

# Asegurar que la suma sea 1.0 y ajustar el peso del último slider para cuadrar
total_sum = w_gasto + w_policia + w_crimen
if total_sum != 1.0:
    # Ajustar el peso más pequeño (o cualquier otro) para que sume 1
    w_gasto = w_gasto / total_sum
    w_policia = w_policia / total_sum
    w_crimen = w_crimen / total_sum
    # Redondeamos para fines de presentación, aunque los cálculos usan el valor exacto
    st.sidebar.markdown(f"**Suma Ajustada:** {w_gasto:.2f} + {w_policia:.2f} + {w_crimen:.2f} = 1.00")

weights = {
    'Gasto': w_gasto,
    'Policía': w_policia,
    'Crimen': w_crimen
}

# sidebar caption
st.sidebar.caption('')
st.sidebar.caption("Dirección General de Planeación")


# --- Cálculo y Visualización ---
# Calcular el índice
df_results = calculate_index(df_original.copy(), weights)


# header
st.subheader('Introducción')
st.markdown('''
    ##### Analizando la Asignación de Fondos para Seguridad Pública.
    
    La toma de decisiones sobre cómo distribuir los recursos de seguridad pública es uno de los desafíos
     más complejos que enfrenta cualquier gobierno.
    Un error en la asignación puede dejar a las comunidades más vulnerables desprotegidas o resultar en
     un gasto ineficiente.
    Las decisiones suelen basarse en múltiples factores, como el gasto actual, la densidad policial y,
     lo más importante, las tasas de criminalidad.
    
    Esta aplicación interactiva sirve como una herramienta de análisis de escenarios que utiliza un
     Índice de Asignación de Seguridad Pública Normalizado.
    En lugar de depender de una única métrica, el índice combina datos crudos de diferentes regiones
     (como el Gasto por Habitante, la cantidad de Policías por 1,000 habitantes y la Tasa de Criminalidad)
      y los normaliza para hacerlos comparables.

    ##### ¿Cómo funciona?
    
    El corazón de la aplicación es la ponderación.
    Al usar los controles deslizantes en la barra lateral, se pueden simular diferentes prioridades de
     política pública.
    
    Por ejemplo, se puede asignar un peso mayor al "Gasto por habitante" si el enfoque es recompensar la
     inversión, o se puede dar más peso a la "Tasa de Criminalidad" si el objetivo principal es dirigir
      recursos a las zonas con peores resultados.
    
    Al ajustar estos pesos, la aplicación recalcula el índice en tiempo real, permitiéndo ver cómo los
     supuestos de ponderación impactan la clasificación final de las regiones.
    Esto proporciona una base objetiva para discutir y justificar las decisiones de asignación de fondos,
     asegurando que los recursos se dirijan donde son más necesarios o donde generarán el mayor impacto.
''')
st.markdown('---')

st.subheader("Datos de Entrada")
st.markdown("Estos son los datos crudos utilizados en el modelo:")
st.dataframe(df_original, use_container_width=True)

st.subheader("Normalización de datos")
st.markdown("Valores transformados en el rango [0, 1], listos para ser ponderados:")
df_normalized = df_results[['Gasto_norm', 'Policia_norm', 'Crimen_norm']]
# Renombrar columnas para mejor visualización
df_normalized.columns = ['Gasto_norm (Alto=Bueno)', 'Policia_norm (Alto=Bueno)', 'Crimen_norm (Bajo=Malo -> Invertida)']
st.dataframe(df_normalized, use_container_width=True,
            column_config={
                "Gasto_norm (Alto=Bueno)": st.column_config.ProgressColumn("Gasto_norm (Alto=Bueno)", format="%.2f", min_value=0.0, max_value=1.0),
                "Policia_norm (Alto=Bueno)": st.column_config.ProgressColumn("Policia_norm (Alto=Bueno)", format="%.2f", min_value=0.0, max_value=1.0),
                "Crimen_norm (Bajo=Malo -> Invertida)": st.column_config.ProgressColumn("Crimen_norm (Bajo=Malo -> Invertida)", format="%.2f", min_value=0.0, max_value=1.0)
            })

# Mostrar la tabla final de resultados
st.subheader("Resultados")
st.dataframe(df_results[['Índice Normalizado', 'Índice Final (0-1)']].sort_values(by='Índice Final (0-1)', ascending=False),
            use_container_width=True,
            column_config={
                "Índice Final (0-1)": st.column_config.ProgressColumn("Índice Final (0-1)", format="%.3f", min_value=0.0, max_value=1.0)
            })


st.subheader("Asignación Final por Entidad Federativa")

# Gráfico de barras interactivo con Plotly
df_plot = df_results.reset_index()
fig = px.bar(
    df_plot,
    x='Región',
    y='Índice Final (0-1)',
    color='Índice Final (0-1)',
    text='Índice Final (0-1)',
    title=f"Índice de Asignación por Región (Ponderadores: Gasto={w_gasto*100:.0f}%, Policía={w_policia*100:.0f}%, Crimen={w_crimen*100:.0f}%)",
    template='ggplot2'
)

fig.update_traces(texttemplate='%{text:.3f}', textposition='outside', marker_color='#bc955c')
fig.update_layout(
    uniformtext_minsize=8, uniformtext_mode='hide',
    yaxis_range=[0, 1.1],
    hovermode="x unified"
    )
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("""
#### Nota Metodológica.

1. **Normalización Min-Max:** Todos los indicadores se escalan al rango [0, 1].
2. **Inversión:** La 'Tasa de Criminalidad' (una variable negativa) se invierte para que una tasa baja resulte en un valor normalizado alto (cercano a 1).
3. **Agregación:** Se aplica la suma ponderada de las tres variables normalizadas.
4. **Re-escalado:** El índice final se re-escala de 0 a 1 para facilitar la interpretación del rendimiento relativo.
""")
