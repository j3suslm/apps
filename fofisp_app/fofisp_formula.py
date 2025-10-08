# libraries
import streamlit as st
import pandas as pd
import numpy as np
import polars as pl
import plotly.express as px
from PIL import Image
from great_tables import GT, md


# web app settings
# blog home link
st.markdown('<a href="https://tinyurl.com/sesnsp-dgp-blog" target="_self">Home</a>', unsafe_allow_html=True)

# hide streamlit logo and footer
hide_default_format = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """

# load icon image
im = Image.open('logo.png')

# page layout config and add image
st.set_page_config(layout="wide", page_title="Fórmula FOFISP", page_icon=im)

# set title and subtitle
st.markdown("<h1><span style='color: #691c32;'>Fórmula para la Asignación FOFISP</span></h1>",
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
w_pob = st.sidebar.slider(
    'Población (Alto=Bueno)',
    min_value=0.0, max_value=1.0, value=0.75, step=0.05, key='Población'
)
w_var_edo_fza = st.sidebar.slider(
    'Incremento estado de fuerza (Alto=Bueno)',
    min_value=0.0, max_value=1.0, value=0.10, step=0.05, key='Incremento estado de fuerza'
)
w_var_incidencia_del = st.sidebar.slider(
    'Variación incidencia delictiva (Alto=Malo)',
    min_value=0.0, max_value=1.0, value=0.10, step=0.05, key='Variación incidencia delictiva'
)
w_academias = st.sidebar.slider(
    'Academias (Alto=Bueno)',
    min_value=0.0, max_value=1.0, value=0.05, step=0.05, key='Academias'
)


# Asegurar que la suma sea 1.0 y ajustar el peso del último slider para cuadrar
total_sum = w_pob + w_var_edo_fza + w_var_incidencia_del + w_academias
st.sidebar.markdown('---')
st.sidebar.markdown(f'Suma de ponderaciones: {total_sum:.2f}')

if total_sum != 1.0:
    # Ajustar el peso más pequeño (o cualquier otro) para que sume 1
    w_pob = w_pob / total_sum
    w_var_edo_fza = w_var_edo_fza / total_sum
    w_var_incidencia_del = w_var_incidencia_del / total_sum
    w_academias = w_academias / total_sum
    # Redondeamos para fines de presentación, aunque los cálculos usan el valor exacto
    st.sidebar.markdown(f"**Suma Ajustada:** {w_pob:.2f} + {w_var_edo_fza:.2f} + {w_var_incidencia_del:.2f} + {w_academias:.2f} = 1.00")

weights = {
    'Población': w_pob,
    'Var_edo_fza': w_var_edo_fza,
    'Var_incidencia_del': w_var_incidencia_del,
    'Academias': w_academias,
}


# tabla de indicadores
indicadores_fofisp = pd.read_csv('indicadores_fofisp.csv')
indicadores_fofisp['Categoría'] = indicadores_fofisp['Categoría'].fillna('')
indicadores_fofisp['Ponderación_categoría'] = indicadores_fofisp['Ponderación_categoría'].fillna(0)

# tabla formateada
indicadores = (
    GT(indicadores_fofisp)
    .tab_stub()
    .tab_header(
        title=md('**Indicadores de Distribución**'),
        subtitle='Fondo para el Fortalecimiento de las Instituciones de Seguridad Pública'
        )
    .fmt_currency(columns=['Monto_asignado'])
    .fmt_percent(columns=['Ponderación_categoría','Ponderación_indicador'], decimals=1).sub_zero(zero_text=md(''))
    .cols_width(cases={
            "Categoría": "23%",
            "Ponderación_categoría": "15%",
            "Indicador": "27%",
            "Ponderación_indicador": "15%",
            "Monto_asignado": "20%"
            })
    .cols_label(
        Categoría = md('**Categoría**'),
        Ponderación_categoría = md('**Ponderación categoría**'),
        Indicador = md('**Indicador**'),
        Ponderación_indicador = md('**Ponderación indicador**'),
        Monto_asignado = md('**Monto asignado**')
    )
    .tab_options(
        container_width="100%",
        container_height="100%",
        heading_background_color="#691c32",
        column_labels_background_color="#ddc9a3",
        source_notes_background_color="#ddc9a3",
        row_striping_include_table_body=True,
        row_striping_background_color='#f8f8f8',
    )
    .tab_source_note(
        source_note=md("Fuente: *Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública*")
    )
)

# entry variables dataset
fofisp_datos_entrada = pd.read_csv('fofisp_datos_entrada.csv')
# change index to start at 1, must specify last limit
fofisp_datos_entrada2 = fofisp_datos_entrada.copy()
fofisp_datos_entrada2.index = pd.RangeIndex(start=1, stop=33, step=1)
fofisp_datos_entrada2 = (
    fofisp_datos_entrada2
        .style.format(
            {'Población': '{:,.2f}',
            'Var_incidencia_del':'{:.2f}%',
            'Var_edo_fza':'{:.2f}%',
            }
        )
)


# --- Funciones de Cálculo del Índice ---
def min_max_normalize(series, direction='positive'):
    """
    Normaliza una serie de datos entre 0 y 1 usando el método Min-Max.
    Si la dirección es 'negativa', se invierte (Alto = Malo se convierte en Alto = Bueno).
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
        raise ValueError("La dirección debe ser 'positiva' o 'negativa'")

def calculate_index(df, weights):
    """Calcula el Índice Compuesto Normalizado."""

    # 1. Normalización de Variables
    # variables positivas
    df['Pob_norm'] = min_max_normalize(df['Población'], direction='positive')
    df['Var_edo_fza_norm'] = min_max_normalize(df['Var_edo_fza'], direction='positive')
    df['Academias_norm'] = min_max_normalize(df['Academias'], direction='positive')

    # variables negativas (menos es mejor, por lo tanto, se invierte)
    df['Var_incidencia_del_norm'] = min_max_normalize(df['Var_incidencia_del'], direction='negative')

    # 2. Aplicación de Ponderadores
    df['Indice Normalizado'] = (
        df['Pob_norm'] * weights['Población'] +
        df['Var_edo_fza_norm'] * weights['Var_edo_fza'] +
        df['Var_incidencia_del_norm'] * weights['Var_incidencia_del'] +
        df['Academias_norm'] * weights['Academias']
    )

    # El índice final también se normaliza a un rango de 0 a 1 para asegurar comparabilidad
    df['Indice Final (0-1)'] = min_max_normalize(df['Indice Normalizado'], direction='positive')
    epsilon = 0.05
    df['Indice Final (Corrimiento)'] = (df['Indice Final (0-1)'] * (1 - epsilon)) + epsilon

    return df

# --- Cálculo y Visualización ---
# Calcular el índice
df_results = calculate_index(fofisp_datos_entrada, weights)


# tab layout
tab1, tab2, tab3 = st.tabs(['1.Introducción', '2.Fórmula', '3.Nota metodológica'])

with tab1:
    presupuesto = 1_155_443_263.97

    # header
    st.subheader('1. Introducción')
    st.markdown('''

    El monto autorizado en el **Presupuesto de Egresos de la Federación (PEF)** para el **Fondo para el 
    Fortalecimiento de las Instituciones de Seguridad Pública (FOFISP) 2026** es:

    ##### $1,15,443,263.97

    Los Indicadores de asignación utilizados en este modelo son los siguientes:
    ''')

    st.html(indicadores)
    
    st.markdown('''
    ##### ¿Cómo funciona esta aplicación?
    
    Esta aplicación interactiva sirve como una herramienta de análisis de escenarios que utiliza un Índice de Asignación de Seguridad Pública Normalizado.
    
    El corazón de la aplicación es la ponderación.
    Al usar los controles deslizantes en la barra lateral, se pueden simular diferentes prioridades de política pública.
    
    Al ajustar estas ponderaciones, la aplicación recalcula el índice en tiempo real, permitiéndo ver cómo los
     supuestos de ponderación impactan la clasificación final de las Entidades Federativas.
    Esto proporciona una base objetiva para discutir y justificar las decisiones de asignación de fondos,
     asegurando que los recursos se dirijan donde son más necesarios o donde generarán el mayor impacto.

    ##### Referencias

    [Fondo para el Fortalecimiento de las Instituciones de Seguridad Pública (FOFISP) 2025](https://www.gob.mx/sesnsp/acciones-y-programas/fondo-para-el-fortalecimiento-de-las-instituciones-de-seguridad-publica-fofisp?state=published)
    
    ---

    *Dirección General de Planeación*
    ''')


with tab2:
    st.header('2. Fórmula de Asignación')
    st.subheader("2.1 Datos de Entrada")
    st.markdown("Estos son los datos utilizados en el modelo:")
    st.dataframe(fofisp_datos_entrada2, use_container_width=True)

    st.subheader("2.2 Normalización de datos")
    st.markdown("Valores transformados en el rango [0, 1], listos para ser ponderados:")
    df_normalized = df_results[['Pob_norm', 'Var_edo_fza_norm', 'Var_incidencia_del_norm', 'Academias_norm']]
    # Renombrar columnas para mejor visualización
    df_normalized.columns = ['Pob_norm (Alto=Bueno)', 'Var_edo_fza_norm (Alto=Bueno)', 'Var_incidencia_del_norm (Bajo=Malo -> Invertida)', 'Academias_norm (Alto=Bueno)']
    st.dataframe(df_normalized, use_container_width=True,
                column_config={
                    "Pob_norm (Alto=Bueno)": st.column_config.ProgressColumn("Pob_norm (Alto=Bueno)", format="%.2f", min_value=0.0, max_value=1.0),
                    "Var_edo_fza_norm (Alto=Bueno)": st.column_config.ProgressColumn("Var_Edo_fza_norm (Alto=Bueno)", format="%.2f", min_value=0.0, max_value=1.0),
                    "Var_incidencia_del_norm (Bajo=Malo -> Invertida)": st.column_config.ProgressColumn("Var_incidencia_del_norm (Bajo=Malo -> Invertida)", format="%.2f", min_value=0.0, max_value=1.0),
                    "Academias_norm (Alto=Bueno)": st.column_config.ProgressColumn("Academias_norm (Alto=Bueno)", format="%.2f", min_value=0.0, max_value=1.0),
                })

    # Mostrar la tabla final de resultados
    st.subheader("2.3 Resultados")
    st.markdown('**Indices**')
    st.dataframe(df_results[['Indice Normalizado', 'Indice Final (0-1)', 'Indice Final (Corrimiento)']].sort_values(by='Indice Final (0-1)', ascending=False),
                use_container_width=True,
                column_config={
                    "Indice Final (Corrimiento)": st.column_config.ProgressColumn("Indice Final (Corrimiento)", format="%.3f", min_value=0.0, max_value=1.0)
                })

    st.markdown('**Importes Asignados por Entidad Federativa**')
    # reckon end allocated amount
    df_results['Importe_asignado'] = (presupuesto * df_results['Indice Final (Corrimiento)'])/1_000_000
    st.dataframe(df_results[['Entidad_Federativa','Pob_norm','Var_edo_fza_norm','Var_incidencia_del_norm',
        'Academias_norm','Indice Final (0-1)','Indice Final (Corrimiento)','Importe_asignado']])

    st.subheader("2.4 Asignación Final por Entidad Federativa")

    # Gráfico de barras interactivo con Plotly
    fig = px.bar(
        df_results,
        x='Entidad_Federativa',
        y='Importe_asignado',
        text='Importe_asignado',
        title=f"Ponderaciones: Población={w_pob*100:.0f}%, Estado de fuerza={w_var_edo_fza*100:.0f}%, Incidencia delictiva={w_var_incidencia_del*100:.0f}%, Academias={w_academias*100:.0f}%)",
        template='ggplot2',
        hover_data={
            'Indice Normalizado':False, # remove species from hover data
            'Importe_asignado':':,.2f', # customize hover for column of y attribute
            },
        labels={'Entidad_Federativa':'Entidad Federativa',
            'Importe_asignado':'Importe asignado',},
    )

    fig.update_traces(
        textposition='outside',
        marker_color='#691c32',
        opacity=0.9,
        marker_line_color='#6f7271',
        marker_line_width=1.2,
        texttemplate='$%{text:,.2f}',
        textfont_size=20,
        )

    fig.update_layout(
        uniformtext_minsize=8, uniformtext_mode='hide',
        hovermode="x unified",
        autosize=True,
        height=600,
        xaxis_title='',
        yaxis_title='Importe asignado (mdp)',
        hoverlabel=dict(
            bgcolor="#f8f8f8",
            font_size=14,
            font_family="Noto Sans",
            )
        )

    fig.update_xaxes(
        showgrid=True,
        title_font=dict(size=18, family='Noto Sans', color='#691c32'),  # X-axis title font size
        tickfont=dict(size=15, family='Noto Sans', color='#4f4f4f'),  # X-axis tick label font size
        tickangle=-75,
        )

    fig.update_yaxes(
        tickprefix="$",
        tickformat=',.0f',
        showgrid=True,
        title_font=dict(size=16, family='Noto Sans', color='#28282b'),
        tickfont=dict(size=15, family='Noto Sans', color='#4f4f4f'),
        tickangle=0,
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

    st.subheader('3.3 Fórmula de Corrimiento Estadístico')
    st.markdown('''
    La fórmula opera sobre el índice normalizado (con rango [0,1]) usando una constante pequeña y positiva, ϵ.

    1. Compresión del Rango: (indice_normalizado * (1−ϵ))

    **Objetivo: Comprimir el rango de los valores normalizados.**

    - Multiplicar por un factor ligeramente menor que 1, como (1−0.0001)=0.9999.
    - El rango original [0,1] se convierte en [0,1−ϵ].
    - El valor mínimo (0) se mantiene en 0×(1−ϵ)=0.
    - El valor máximo (1) se reduce a 1×(1−ϵ)=1−ϵ.

    2. Corrimiento hacia arriba (Shift): +ϵ

    **Objetivo: Desplazar todo el conjunto de datos hacia arriba por la cantidad ϵ.**

    Se suma ϵ al resultado del paso anterior.

    - El mínimo, que era 0, ahora es 0+ϵ=ϵ.
    - El máximo, que era 1−ϵ, ahora es (1−ϵ)+ϵ=1.
    
    
    ##### Tabla de Resultados del Corrimiento Estadístico

    |Indice normalizado|Transformación|Valor Final|
    |:---:|:---:|:---:|
    |0 (mínimo)|(0 * (1−ϵ)) + ϵ|ϵ|
    |1 (máximo)|(1 * (1−ϵ)) + ϵ|1|

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
