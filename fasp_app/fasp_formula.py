# libraries
import streamlit as st
import numpy as np
import pandas as pd
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from great_tables import GT, md
import os
import io
from dotenv import load_dotenv
load_dotenv('.env')

# --- app settings ---
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
im = Image.open('images/logo.png')

# page layout config and add image
st.set_page_config(layout="wide", page_title="FASP App", page_icon=im)

# set title and subtitle
st.markdown("<h1><span style='color: #691c32;'>Asignación del Fondo FASP</span></h1>",
    unsafe_allow_html=True)

# author, date
st.caption('Jesús LM')
st.caption('Octubre, 2025')

# authentication by password
password = os.getenv('PASSWORD')
# Initialize session state if not already set
if 'password_correct' not in st.session_state:
    st.session_state.password_correct = False

# if password is not correct, ask for it
if not st.session_state.password_correct:
    password_guess = st.text_input('¡Escribe el password para acceder!')
        
    if password_guess == password:
        st.session_state.password_correct = True
        st.rerun()
    else:
        st.stop()

# this code runs only when the password is correct
#st.success('¡Bienvenido!')

st.markdown(hide_default_format, unsafe_allow_html=True)
#st.sidebar.markdown("**Ponderaciones**")

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

# --- sidebar ---
# sidebar image and text
st.sidebar.image('images/sesnsp.png')

with st.sidebar.expander('Bandas'):
    # presupuesto estimado widget
    presupuesto = st.number_input(
        'Presupuesto estimado',
        value=9_840_407_024.0, placeholder='Monto del fondo', key='Presupuesto estimado', format="%.2f", 
    )
    presupuesto_formateado = f"${presupuesto:,.2f}"
    # presupuesto estimado widget
    upper_limit = st.number_input(
        'Banda superior',
        value=0.1, key='Limite superior',
    )
    # presupuesto estimado widget
    lower_limit = st.number_input(
        'Banda inferior',
        value=0.1, key='Limite inferior',
    )

# ponderadores
# sliders for weights
with st.sidebar.expander('Ponderadores'):
    w_pob = st.number_input(
        'Población (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.125, step=0.001, key='Población', format='%.4f',
    )
    w_incidencia_del = st.number_input(
        'Incidencia delictiva (Alto=Malo)',
        min_value=0.0, max_value=1.0, value=0.075, step=0.001, key='Incidencia delictiva', format='%.4f',
    )
    w_var_incidencia_del = st.number_input(
        'Variación incidencia delictiva (Alto=Malo)',
        min_value=0.0, max_value=1.0, value=0.05, step=0.001, key='Variación incidencia delictiva', format='%.4f',
    )
    w_victim = st.number_input(
        'Victimización (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.0675, step=0.001, key='Victimización', format='%.4f',
    )
    w_pob_penitenciaria = st.number_input(
        'Sobrepoblación penitenciaria (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.0525, step=0.001, key='Sobrepolación penitenciaria', format='%.4f',
    )
    w_imp_justicia = st.number_input(
        'Impartición justicia (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.03, step=0.001, key='Impartición justicia', format='%.4f',
    )
    w_servs_for = st.number_input(
        'Servicios Médicos Forenses (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.07, step=0.001, key='Servicios Médicos Forenses', format='%.4f',
    )
    w_edo_fza = st.number_input(
        'Tasa policial (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.0525, step=0.001, key='Tasa policial', format='%.4f',
    )
    w_dig_salarial = st.number_input(
        'Dignificación salarial (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.0525, step=0.001, key='Dignificación salarial', format='%.4f',
    )
    w_prof = st.number_input(
        'Profesionalización (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.0525, step=0.001, key='Profesionalización', format='%.4f',
    )
    w_ctrl_conf = st.number_input(
        'Control confianza (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.0438, step=0.001, key='Control confianza', format='%.4f',
    )
    w_desemp_pol = st.number_input(
        'Desempeño policial (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.075, step=0.001, key='Desempeño policial', format='%.4f',
    )
    w_conf_pol = st.number_input(
        'Confianza policial (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.0375, step=0.001, key='Confianza policial', format='%.4f',
    )
    w_ef_presupuestal = st.number_input(
        'Eficiencia presupuestal (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.05, step=0.001, key='Eficiencia presupuestal', format='%.4f',
    )
    w_base = st.number_input(
        'Base (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.05, step=0.001, key='Base', format='%.4f',
    )

    # asegurar que la suma sea 1.0 y ajustar el peso del último slider para cuadrar
    total_sum = (
        w_pob + w_incidencia_del + w_var_incidencia_del + w_victim + w_pob_penitenciaria + w_imp_justicia
        + w_servs_for + w_edo_fza + w_dig_salarial + w_prof + w_ctrl_conf + w_desemp_pol + w_conf_pol
        + w_ef_presupuestal + w_base
    )
    #st.sidebar.markdown('---')
    formatted_sum = f"{total_sum:.2%}"
    st.markdown(f'Suma: {formatted_sum}')

weights = {
    'Población': w_pob,
    'Incidencia delictiva': w_incidencia_del,
    'Variación incidencia delictiva': w_var_incidencia_del,
    'Victimización': w_victim,
    'Sobrepoblación penitenciaria': w_pob_penitenciaria,
    'Imparticion justica': w_imp_justicia,
    'Servicios Médicos Forenses': w_servs_for,
    'Tasa policial': w_edo_fza,
    'Dignificación salarial': w_dig_salarial,
    'Profesionalización': w_prof,
    'Control confianza': w_ctrl_conf,
    'Desempeño policial': w_desemp_pol,
    'Confianza policial': w_conf_pol,
    'Eficiencia presupuestal': w_ef_presupuestal,
    'Base': w_base,
}


# upload final variables dataset
# widget para subir archivos
uploaded_file = st.file_uploader("", type=['csv'], )

if uploaded_file is None:
    st.text('Sube el archivo con las variables para la asignación del fondo en formato csv.')
else:
    data = pd.read_csv(io.BytesIO(uploaded_file.getvalue()))

    # tabla de indicadores
    indicadores_fasp = pd.read_csv('fasp_indicadores.csv')
    indicadores_fasp['Categoría'] = indicadores_fasp['Categoría'].fillna('')
    indicadores_fasp['Ponderación_categoría'] = indicadores_fasp['Ponderación_categoría'].fillna(0)

    # tabla formateada
    indicadores = (
        GT(indicadores_fasp)
        .cols_hide(columns='Monto_asignado')
        .tab_stub()
        .tab_header(
            title=md('Fondo de Aportaciones para la Seguridad Pública'),
            subtitle=md('## Indicadores de Distribución')
            )
        .fmt_percent(columns=['Ponderación_categoría','Ponderación_indicador'], decimals=1).sub_zero(zero_text=md(''))
        .cols_width(cases={
                "Categoría": "15%",
                "Ponderación_categoría": "10%",
                "Subcategoría": "25%",
                "Indicador": "35%",
                "Ponderación_indicador": "10%",
                "Ponderación_individual": "10%",
                })
        .cols_label(
            Categoría = md('**Categoría**'),
            Subcategoría = md('**Subcategoría**'),
            Ponderación_categoría = md('**Ponderación categoría**'),
            Indicador = md('**Indicador**'),
            Ponderación_indicador = md('**Ponderación indicador**'),
            Ponderación_individual = md('**Ponderación individual**'),
        )
        .cols_align(align='center',
            columns=['Ponderación_categoría','Ponderación_indicador','Ponderación_individual'])
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



    # tab layout
    tab1, tab2, tab3, tab4 = st.tabs(['1.Introducción', '2.Cálculo', '3.Nota metodológica', '4.Nota técnica'])

    with tab1:

        # header
        st.subheader('1. Introducción')
        st.markdown('''
        <div style="text-align: justify;">
        A continuación se enlistan los indicadores subyacentes para la asignación del <b>Fondo de Aportaciones
        para la Seguridad Pública</b> (FASP) <b>2026</b>.
        </div>''',
        unsafe_allow_html=True)

        st.html(indicadores)
        st.caption('Tabla 1. Indicadores utilizados para la asignación de fondos y ponderaciones predeterminadas.')

        st.markdown('''
        ##### ¿Cómo funciona esta aplicación?
        ''')

        st.markdown('''
        <div style="text-align: justify;">
        Esta aplicación interactiva sirve como una herramienta de análisis de escenarios que utiliza un Índice de Asignación de Seguridad Pública Normalizado.
        
        El corazón de la aplicación es la ponderación.
        Al usar los controles deslizantes en la barra lateral, se pueden simular diferentes prioridades de política pública.
        
        Al ajustar estas ponderaciones, la aplicación recalcula el índice en tiempo real, permitiéndo ver cómo los
        supuestos de ponderación impactan la clasificación final de las Entidades Federativas.
        Esto proporciona una base objetiva para discutir y justificar las decisiones de asignación de fondos,
        asegurando que los recursos se dirijan donde son más necesarios o donde generarán el mayor impacto.
        </div>''',
        unsafe_allow_html=True)

        st.markdown('''
        ##### Referencias

        [Fondo de Aportaciones para la Seguridad Pública (FASP) 2025](https://www.gob.mx/sesnsp/acciones-y-programas/fondo-de-aportaciones-para-la-seguridad-publica-fasp)
        
        ---

        *© Dirección General de Planeación*
        ''')

    with tab2:
        st.markdown(f'''
            ## 2. Escenarios de Asignación
            #### Cálculo con un Fondo Estimado de: *{presupuesto_formateado}*
        ''')
        st.subheader("2.1 Datos de Entrada")

        base = 1

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
            df['Pob_norm'] = min_max_normalize(df['Pob'], direction='positive')
            df['Inc_del_norm'] = min_max_normalize(df['Inc_del'], direction='positive')
            df['Var_inc_del_norm'] = min_max_normalize(df['Var_inc_del'], direction='positive')
            df['Victim_norm'] = min_max_normalize(df['Victim'], direction='positive')
            df['Pob_penitenciaria_norm'] = min_max_normalize(df['Pob_penitenciaria'], direction='positive')
            df['Imp_justicia_norm'] = min_max_normalize(df['Imp_justicia'], direction='positive')
            df['Servs_forenses_norm'] = min_max_normalize(df['Servs_forenses'], direction='positive')
            df['Edo_fzanorm'] = min_max_normalize(df['Edo_fza'], direction='positive')
            df['Dig_salarial_norm'] = min_max_normalize(df['Dig_salarial'], direction='positive')
            df['Profesionalizacion_norm'] = min_max_normalize(df['Profesionalizacion'], direction='positive')
            df['Ctrl_confianza_norm'] = min_max_normalize(df['Ctrl_confianza'], direction='positive')
            df['Desemp_pol_norm'] = min_max_normalize(df['Desemp_pol'], direction='positive')
            df['Conf_pol_norm'] = min_max_normalize(df['Conf_pol'], direction='positive')
            df['Eficiencia_presupuestal_norm'] = min_max_normalize(df['Eficiencia_presupuestal'], direction='positive')

            # variables negativas (menos es mejor, por lo tanto, se invierte)
            


            # 2. Aplicación de Ponderadores
            df['Indice Normalizado'] = (
                df['Pob_norm'] * weights['Población'] +
                df['Tasa_policial_norm'] * weights['Tasa_policial'] +
                df['Var_incidencia_del_norm'] * weights['Var_incidencia_del'] +
                df['Academias_norm'] * weights['Academias']
            )

            # El índice final también se normaliza a un rango de 0 a 1 para asegurar comparabilidad
            df['Indice Final (0-1)'] = min_max_normalize(df['Indice Normalizado'], direction='positive')
            epsilon = 0.05
            df['Indice Final (Corrimiento)'] = (df['Indice Final (0-1)'] * (1 - epsilon)) + epsilon

            return df

        # change index to start at 1, must specify last limit
        fasp_datos_entrada = data.copy()
        data.index = pd.RangeIndex(start=1, stop=33, step=1)
        data['Var_incidencia_del'] = data['Var_incidencia_del']*100
        fofisp_datos_entrada2 = (
            data
                .style.format({
                    'Población': '{:,.2f}',
                    'Var_incidencia_del':'{:.2f}%',
                    'Tasa_policial':'{:.2f}',
                    'Asignacion_2025': '${:,.2f}',
                    })
                )






    
    with tab3:
        st.header('3. Nota metodológica')
        st.markdown("""
        1. **Normalización:** Todos los indicadores se escalan al rango [0, 1].
        2. **Agregación:** Se aplica la suma ponderada de las variables normalizadas.
        3. **Corrimiento estadístico:** Se suma un valor epsilon para evitar coeficientes nulos.
        4. **Repartición:** Se reparte el presupuesto entre las Entidades Federativas según el valor de las ponderaciones de los indicadores.
        """)

        st.subheader('3.1 Normalización')
        st.latex(r'''
        V_{i,j} = \frac{X_{i,j} - X_{i, \min}}{X_{i, \max} - X_{i, \min}}\\
        \text{ }\\
        \text{donde:}\\
        \text{ }\\
        V_{i,j} = \text{Valor normalizado del indicador i para la Entidad Federativa j}\\
        X_{i,j} = \text{Indicador i de la Entidad Federativa j}\\
        ''')
        st.markdown('`Inversión: Las variables negativas se invierten para que una tasa baja resulte en un valor normalizado alto (cercano a 1).`')
        
        st.subheader('3.2 Agregación del Índice')
        st.latex(r'''
        I_j = \sum_{i=1}^{n}( V_{i,j} \times W_i)\\
        \text{ }\\
        \text{donde:}\\
        \text{ }\\
        I_j = \text{Índice de asignación de fondos para la Entidad Federativa j}\\
        V_{i,j} = \text{Valor normalizado del indicador i para la Entidad Federativa j}\\
        W_i = \text{Ponderación del indicador i}\\
        ''')
        st.markdown('`Re-escalado: El índice final se re-escala [0, 1] para facilitar la interpretación del rendimiento relativo.`')

        st.subheader('3.3 Corrimiento Estadístico')
        st.markdown('''
        La fórmula opera sobre el índice normalizado (con rango [0,1]) usando una constante pequeña y positiva, ϵ.

        ##### 3.3.1  Compresión del Rango: (indice_normalizado * (1−ϵ))

        **Objetivo: Comprimir el rango de los valores normalizados.**

        - Multiplicar por un factor ligeramente menor que 1, como (1−0.0001)=0.9999.
        - El rango original [0,1] se convierte en [0,1−ϵ].
        - El valor mínimo (0) se mantiene en 0×(1−ϵ)=0.
        - El valor máximo (1) se reduce a 1×(1−ϵ)=1−ϵ.
        
        ##### 3.3.2 Corrimiento hacia arriba (Shift): +ϵ

        **Objetivo: Desplazar todo el conjunto de datos hacia arriba por la cantidad ϵ.**

        Se suma ϵ al resultado del paso anterior.

        - El mínimo, que era 0, ahora es 0+ϵ=ϵ.
        - El máximo, que era 1−ϵ, ahora es (1−ϵ)+ϵ=1.
        
        
        |Indice normalizado|Transformación|Valor Final|
        |:---:|:---:|:---:|
        |0 (mínimo)|(0 * (1−ϵ)) + ϵ|ϵ|
        |1 (máximo)|(1 * (1−ϵ)) + ϵ|1|

        ''')

        st.subheader('3.4 Repartición del Presupuesto')
        st.markdown('''
        Se calcula la participación porcentual de cada Entidad Federativa en el índice total
        y se distribuye el fondo total entre cada una de acuerdo a su participación porcentual.
        ''')
        
        st.subheader('3.5 Repartición del Remanente')
        st.markdown('''
        <div style="text-align: justify;">
        Se aplican bandas del ±10% respecto al importe asignado del ejercicio anterior inmediato y se obtiene 
        el total de importe sobrante y faltante aplicando estas bandas.
        Posteriormente, se reparte este remanente entre las diversas Entidades Federativas para que ninguna rebase
        las bandas del ±10%.
        </div>''',
        unsafe_allow_html=True)

        st.markdown('---')
        st.markdown('*© Dirección General de Planeación*')

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

    with tab4:

        st.header('4. Nota técnica')
        st.markdown("""
        En este apartado, se muestra la sábana de datos con todos las fases del cálculo de asignación de fondos,
        incluyendo las bandas y reasignación del remanente.

        Por otra parte, se anexa hoja de cálculo en formato xlsx (Excel) con el desarrollo mencionado.
        """)

        #st.dataframe(df_results)

        st.markdown("[Hoja de cálculo](https://sspcgob-my.sharepoint.com/:x:/g/personal/oscar_avila_sspc_gob_mx/ETex8WWRzYdCnzXAmoHVfyEBgpWLUSsMuGtvv1wcHOgEyg?e=iiddzc)")
        
        st.markdown('---')
        st.markdown('*© Dirección General de Planeación*')
