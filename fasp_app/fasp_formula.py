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
        .tab_stub()
        .tab_header(
            title=md('Fondo de Aportaciones para la Seguridad Pública'),
            subtitle=md('## Indicadores de Distribución')
            )
        .fmt_percent(columns=['Ponderación_categoría','Ponderación_subcategoría','Ponderación_indicador',], decimals=1).sub_zero(zero_text=md(''))
        .cols_width(cases={
                "Categoría": "15%",
                "Ponderación_categoría": "10%",
                "Subcategoría": "25%",
                "Indicador": "35%",
                "Ponderación_subcategoría": "10%",
                "Ponderación_indicador": "10%",
                })
        .cols_label(
            Categoría = md('**Categoría**'),
            Subcategoría = md('**Subcategoría**'),
            Ponderación_categoría = md('**Ponderación categoría**'),
            Indicador = md('**Indicador**'),
            Ponderación_subcategoría = md('**Ponderación subcategoría**'),
            Ponderación_indicador = md('**Ponderación indicador**'),
        )
        .cols_align(align='center',
            columns=['Ponderación_categoría','Ponderación_subcategoría','Ponderación_indicador'])
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

        base = presupuesto * 0.06
        

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
            """Calcula el Índice Compuesto Normalizado con 16 variables."""
            
            # Define Variable Directions (High Value = Good/Positive vs. High Value = Bad/Negative)
            # The direction determines if normalization is standard or inverted.
            directions = {
                'Pob': 'positive',               # More population = Higher score
                'Tasa_policial': 'positive',     # Higher police rate (more officers) = Higher score
                'Dig_salarial': 'positive',      # Better salary dignification = Higher score
                'Profesionalizacion': 'positive',# More professionalization = Higher score
                'Ctrl_conf': 'positive',         # More control of confidence = Higher score
                'Disp_camaras': 'positive',      # More cameras = Higher score
                'Disp_lectores_veh': 'positive', # More vehicle readers = Higher score
                'Cump_presup': 'positive',       # Better budget compliance = Higher score
                'Proc_justicia': 'positive',     # Better justice process = Higher score
                'Servs_forenses': 'positive',    # Better forensic services = Higher score
                'Eficiencia_procesal': 'positive',# More procedural efficiency = Higher score
                
                'Var_inc_del': 'negative',        # Higher crime incidence variation (worse) = Lower score
                'Tasa_abandono_llamadas911': 'negative', # Higher abandonment rate = Lower score
                'Tasa_abandono_llamadas089': 'negative', # Higher abandonment rate = Lower score
                'Sobrepob_penitenciaria': 'negative', # More overcrowding = Lower score
            }
            
            # 1. Normalización de Variables
            normalized_columns = []
            for col, direction in directions.items():
                norm_col_name = f'{col}_norm'
                df[norm_col_name] = min_max_normalize(df[col], direction=direction)
                normalized_columns.append(norm_col_name)

            # 2. Aplicación de Ponderadores
            # Create the index calculation dynamically based on the available weights
            index_calculation = 0
            for col in weights:
                norm_col_name = f'{col}_norm'
                if norm_col_name in df.columns:
                    index_calculation += df[norm_col_name] * weights[col]

            df['Indice Normalizado'] = index_calculation

            # 3. Normalización Final (Corrimiento)
            df['Indice Final (0-1)'] = min_max_normalize(df['Indice Normalizado'], direction='positive')
            epsilon = 0.01
            df['Indice Final (Corrimiento)'] = (df['Indice Final (0-1)'] * (1 - epsilon)) + epsilon

            return df


        # Replicating original index setting and Var_incidencia_del multiplication
        # Assuming 'data' contains the new columns and 'Entidad Federativa'
        fasp_datos_entrada = data.copy()
        data.index = pd.RangeIndex(start=1, stop=len(data) + 1, step=1) 
        data['Var_inc_del'] = data['Var_inc_del'] * 100 # Adjusting column name to new list

        #fasp_datos_entrada2 = (
        #    data
        #        .style.format({
        #            'Pob': '{:,.2f}',
        #            'Var_inc_del':'{:.2f}%',
        #            'Tasa_policial':'{:.2f}',
        #            'Asignacion_2025': '${:,.2f}',
        #            })
        #        )

        st.dataframe(data, use_container_width=True)
        st.caption('Tabla 2. Variables utilizadas en el modelo para la asignación de fondos.')

        # Calculate the index
        df_results = calculate_index(fasp_datos_entrada, weights)

        # 1. Allocation Calculation
        total_indice = df_results['Indice Final (Corrimiento)'].sum()
        df_results['Reparto'] = df_results['Indice Final (Corrimiento)'] / total_indice
        df_results['Asignacion_2026'] = df_results['Reparto'] * presupuesto
        df_results['Var%'] = df_results['Asignacion_2026'] / df_results['Asignacion_2025'] - 1

        # 2. Rebalanceo (Applying ±10% band)
        df_results['Min'] = df_results['Asignacion_2025'] * (1 - lower_limit)
        df_results['Max'] = df_results['Asignacion_2025'] * (1 + upper_limit)

        df_results['Superavit'] = np.where(df_results['Asignacion_2026'] > df_results['Max'],
                                        df_results['Asignacion_2026'] - df_results['Max'],
                                        0)

        df_results['Deficit'] = np.where(df_results['Asignacion_2026'] < df_results['Min'],
                                        df_results['Min'] - df_results['Asignacion_2026'],
                                        0)

        total_superavit = df_results['Superavit'].sum()
        total_deficit = df_results['Deficit'].sum()
        remanente = total_superavit - total_deficit

        # Determine Interim Allocation: Apply the caps and floors
        df_results['Reasignacion'] = df_results['Asignacion_2026'].clip(lower=df_results['Min'], upper=df_results['Max'])
        df_results['Elegibles'] = np.where(df_results['Reasignacion'] < df_results['Max'],
                                            1,
                                            0)
        total_basis = df_results['Elegibles'].sum()

        if total_basis > 0:
            df_results['Reparto_neto'] = (df_results['Elegibles'] / total_basis) * remanente
        else:
            df_results['Reparto_neto'] = 0

        # Calculate Final Adjusted Allocation
        df_results['Asignacion_ajustada'] = df_results['Reasignacion'] + df_results['Reparto_neto']
        df_results['Var%_ajustada'] = (df_results['Asignacion_ajustada'] - df_results['Asignacion_2025']) / df_results['Asignacion_2025']

        # 3. Plotly Figure 2 (Replicating the target structure)
        # Gráfico de barras de reasignacion de remanente 2026 vs 2025
        fig2 = go.Figure(data=[
            go.Bar(
                name='Ejercicio 2025',
                x=df_results['Entidad Federativa'],
                y=df_results['Asignacion_2025'],
                marker_color='#bc955c',
                # ADDED: customdata for the hover template
                customdata=df_results[['Entidad Federativa', 'Var%_ajustada']],
                hovertemplate=(
                    # Template to show Entidad_Federativa (x) and Var%_ajustada (customdata[1])
                    'Entidad Federativa: %{x}<br>'
                    'Var%_ajustada: %{customdata[1]:.2%}<extra></extra>' # .2% for two decimal percentage
                )
            ),
            go.Bar(
                name='Ejercicio 2026',
                x=df_results['Entidad Federativa'],
                y=df_results['Asignacion_ajustada'],
                marker_color='#691c32',
                # ADDED: customdata for the hover template (must be the same for both bars)
                customdata=df_results[['Entidad Federativa', 'Var%_ajustada']],
                hovertemplate=(
                    # Template to show Entidad_Federativa (x) and Var%_ajustada (customdata[1])
                    'Entidad Federativa: %{x}<br>'
                    'Var%_ajustada: %{customdata[1]:.2%}<extra></extra>' # .2% for two decimal percentage
                )
            ),
        ])

        # Update layout to group bars
        fig2.update_traces(
            textposition='outside',
            opacity=0.9,
            marker_line_color='#6f7271',
            marker_line_width=1.2,
            # NOTE: texttemplate is removed here as it was removed in the original fig2, but
            # it was present in fig1. I'll re-add it based on your original fig2 code.
            texttemplate='$%{y:,.2f}', # Changed to %{y} since text=y is not explicitly set
            textfont_size=20,
            )

        # Dynamically create the weight-based title (example for 3 variables)
        weight_title = ", ".join([f"{col}={w*100:.0f}%" for col, w in list(weights.items())[:4]]) + "..." # Showing only first 4 weights

        fig2.update_layout(
            barmode='group',
            title=f"Reasignación de Fondos por Entidad Federativa después de Remanente de la banda de ±10% - Variables: {weight_title}",
            template='ggplot2',
            uniformtext_minsize=8, uniformtext_mode='hide',
            hovermode="x unified",
            autosize=True,
            height=600,
            xaxis_title='',
            yaxis_title='Asignacion 2026',
            hoverlabel=dict(
                bgcolor="#fff",
                font_size=16,
                font_family="Noto Sans",
                )
            )

        fig2.update_xaxes(
            showgrid=True,
            title_font=dict(size=18, family='Noto Sans', color='#691c32'),
            tickfont=dict(size=15, family='Noto Sans', color='#4f4f4f'),
            tickangle=-75,
            )

        fig2.update_yaxes(
            tickprefix="$",
            tickformat=',.0f',
            showgrid=True,
            title_font=dict(size=16, family='Noto Sans', color='#28282b'),
            tickfont=dict(size=15, family='Noto Sans', color='#4f4f4f'),
            tickangle=0,
            )

        st.plotly_chart(fig2, use_container_width=True)

        
        st.markdown('---')
        st.markdown('*© Dirección General de Planeación*')
























    
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
