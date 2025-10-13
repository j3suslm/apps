# libraries
import streamlit as st
import pandas as pd
import numpy as np
import polars as pl
import plotly.express as px
from PIL import Image


# Datos de ejemplo para diferentes regiones/municipios
data = {
    'Región': ['Central', 'Norte', 'Sur-Este', 'Occidente', 'Metropolitana'],
    'Gasto por Hab': [500, 320, 780, 450, 610], # Gasto público en USD/habitante
    'Policías por 100k': [350, 210, 420, 280, 500], # Policías por 100,000 habitantes
    'Tasa de Criminalidad': [4500, 6800, 3100, 5500, 4000] # Delitos por 100,000 habitantes (variable negativa)
}
df_original = pd.DataFrame(data)
df_original = df_original.set_index('Región')
df_original2 = pd.read_csv('fasp_datos_entrada.csv')


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
st.markdown("<h1><span style='color: #691c32;'>Asignación del Fondo FASP</span></h1>",
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

    
# customize color of sidebar and text
st.markdown("""
    <style>
        /* 1. Target the main content area background */
        [data-testid="stAppViewBlockContainer"] {
            background-color: #f6f6f6;
        }
        /* Sidebar background */
        [data-testid=stSidebar] {
            background-color: #f6f6f6;
            color: #28282b;
        }
        /* Target all text elements within the sidebar (labels, markdown, sliders, etc.) */
        [data-testid="stSidebar"] * {
            color: #28282b !important;
        }
    </style>
    """, unsafe_allow_html=True)


# Sliders for weights
# Los valores se limitan para que la suma siempre sea 1
w_gasto = st.sidebar.slider(
    'Población (Alto=Bueno)',
    min_value=0.0, max_value=1.0, value=0.40, step=0.05, key='gasto'
)
w_policia = st.sidebar.slider(
    'Incidencia delicitiva (Alto=Bueno)',
    min_value=0.0, max_value=1.0, value=0.30, step=0.05, key='policia'
)
w_crimen = st.sidebar.slider(
    'Victimización (Alto=Malo)',
    min_value=0.0, max_value=1.0, value=0.30, step=0.05, key='crimen'
)
#w_penitenciario = st.sidebar.slider(
#    'Sobrepoblación penitenciaria (Alto=Malo)',
#    min_value=0.0, max_value=1.0, value=0.30, step=0.05, key='crimen'
#)


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
    'Crimen': w_crimen,
#    'Sobrepoblación penitenciaria': w_penitenciario,
}


# --- Cálculo y Visualización ---
# Calcular el índice
df_results = calculate_index(df_original.copy(), weights)


# tab layout
tab1, tab2, tab3 = st.tabs(['1.Introducción', '2.Fórmula', '3.Nota metodológica'])

with tab1:
    # header
    st.subheader('1. Introducción')
    st.markdown('''
    
    ##### 1.1 Antecedentes

    El Secretariado debe someter a aprobación del Consejo Nacional de Seguridad Pública los criterios para la distribución del FASP.   
    _**Ley de Coordinación Fiscal, artículo 44.**_

    - En 2020 se realizó el último diseño de los criterios de distribución. 
    - Las asignaciones subsecuentes aumentaban de manera proporcional al aumento de los recursos del Fondo, con base en el diseño de 2020.
    ''')

    st.image('antecedentes.png',
        caption='Categorías comprendidas para el cálculo de asignación.',
        width=700)

    st.markdown('''
    ##### 1.2 ¿Cómo funciona esta aplicación?
    
    Esta aplicación interactiva sirve como una herramienta de análisis de escenarios que utiliza un Índice de Asignación de Seguridad Pública Normalizado.
    
    El corazón de la aplicación es la ponderación.
    Al usar los controles deslizantes en la barra lateral, se pueden simular diferentes prioridades de política pública.
    
    Al ajustar estos pesos, la aplicación recalcula el índice en tiempo real, permitiéndo ver cómo los
     supuestos de ponderación impactan la clasificación final de las regiones.
    Esto proporciona una base objetiva para discutir y justificar las decisiones de asignación de fondos,
     asegurando que los recursos se dirijan donde son más necesarios o donde generarán el mayor impacto.

    ##### Referencias

    [Lineamientos Generales de Evaluación del Fondo de Aportaciones para la Seguridad Pública (FASP) 2025](https://www.gob.mx/sesnsp/documentos/lineamientos-generales-de-evaluacion-del-fondo-de-aportaciones-para-la-seguridad-publica-fasp-2025?state=published)
    
    ---

    *Dirección General de Planeación*
    ''')


with tab2:
    st.header('2. Fórmula de Asignación')

    st.image('indicadores.png',
        caption='Indicadores comprendidos para el cálculo de asignación.',
        width=700)
    
    st.subheader("2.1 Datos de Entrada")
    st.markdown("Estos son los datos utilizados en el modelo:")
    st.dataframe(df_original2, use_container_width=True)

    st.subheader("2.2 Normalización de datos")
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
    st.subheader("2.3 Resultados")
    st.dataframe(df_results[['Índice Normalizado', 'Índice Final (0-1)']].sort_values(by='Índice Final (0-1)', ascending=False),
                use_container_width=True,
                column_config={
                    "Índice Final (0-1)": st.column_config.ProgressColumn("Índice Final (0-1)", format="%.3f", min_value=0.0, max_value=1.0)
                })


    st.subheader("2.4 Asignación Final por Entidad Federativa")

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

    fig.update_traces(texttemplate='%{text:.3f}',
        textposition='outside',
        marker_color='#bc955c')

    fig.update_layout(
        uniformtext_minsize=8, uniformtext_mode='hide',
        yaxis_range=[0, 1.1],
        hovermode="x unified"
        )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown('---')
    st.markdown('*Dirección General de Planeación*')


with tab3:
    st.header('3. Nota metodológica')
    st.markdown("""
    1. **Normalización Min-Max:** Todos los indicadores se escalan al rango [0, 1].
    2. **Inversión:** La 'Tasa de Criminalidad' (una variable negativa) se invierte para que una tasa baja resulte en un valor normalizado alto (cercano a 1).
    3. **Agregación:** Se aplica la suma ponderada de las tres variables normalizadas.
    4. **Re-escalado:** El índice final se re-escala de 0 a 1 para facilitar la interpretación del rendimiento relativo.
    """)

    st.subheader('3.1 Fórmula de normalización')
    st.latex(r'''
    V_{i,j} = \frac{X_{i,j} - X_{i, \min}}{X_{i, \max} - X_{i, \min}}\\
    \text{ }\\
    \text{donde:}\\
    \text{ }\\
    V_{i,j} = \text{Valor normalizado del indicador i para la Entidad Federativa j}\\
    X_{i,j} = \text{Indicador i de la Entidad Federativa j}\\
    ''')

    st.subheader('3.2 Fórmula del Índice de Asignación')
    st.latex(r'''
    I_j = \sum_{i=1}^{n}( V_{i,j} \times W_i)\\
    \text{ }\\
    \text{donde:}\\
    \text{ }\\
    I_j = \text{Índice de asignación de fondos para la Entidad Federativa j}\\
    V_{i,j} = \text{Valor normalizado del indicador i para la Entidad Federativa j}\\
    W_i = \text{Ponderación del indicador i}\\
    ''')

    st.markdown('---')
    st.markdown('*Dirección General de Planeación*')

    # Inject custom CSS to left-align KaTeX elements
    st.markdown(
        """
        <style>
        .katex-html {
            text-align: left;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
