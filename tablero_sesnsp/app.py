# libraries
from shiny import App, ui, Session, render
from shinywidgets import output_widget, render_widget
import plotly.express as px
import numpy as np
import pandas as pd

# datasets
prestaciones = pd.read_excel('tablero.xlsx', usecols=[1,6,7,9])
prestaciones['cantidad'] = prestaciones['cantidad'].fillna(0)
entidades_unicas = prestaciones['nom_entidad'].unique().tolist()

# core app
app_ui = ui.page_fluid(
    ui.page_auto(
        title=ui.a(
            ui.img(src='https://www.datos.gob.mx/uploads/group/2025-03-10-202801.641179LogoSESNSPpnghorizontal.png',
                alt='sesnsp', width='200'),
            href='https://www.gob.mx/sesnsp',
        target='_blank',),
        window_title="My app",
        fillable=True,
        id='page',
    ),
    ui.page_sidebar(
        # sidebar
        ui.sidebar(
            ui.markdown('<h4 style="color: #bc955c;">SESNSP</h4>'),
            ui.input_select(
                "entidad_select",
                "Entidad Federativa",
                choices=entidades_unicas,
                selected=entidades_unicas[0]
            ),
        ),
        # central grid
        ui.markdown(
            """
            <h1 style="color: #691c32;">Diagnóstico de las Instituciones Policiales en México</h1>
            
            <br>

            El presente diagnóstico se realizó con datos abiertos tales como:
            
            <br>
            
            - INEGI. Censo Nacional de Seguridad Pública Estatal 2024
            - INEGI. Censo Nacional de Procuración de Justicia Estatal 2024
            - Presupuestos de egresos estatales FASP

            ***
            """
        ),
        ui.page_fillable(
            ui.layout_columns(
                ui.card(
                    ui.card_header('Incidencia delictiva'),
                    ui.markdown('# 2,568'),
                    ui.card_footer('Fuente: SESNSP'),
                    ),
                ui.card(
                    ui.card_header('Estado de Fuerza'),
                    ui.markdown('# 216,968'),
                    ui.card_footer('Fuente: INEGI'),
                    ),
                ui.card(
                    ui.card_header('Gasto en Seguridad Pública'),
                    ui.markdown('# 2,568,065'),
                    ui.card_footer('Fuente: FASP Encuesta Institucional'),
                    ),
                ),
            ui.markdown('***'),
            output_widget("myplot"),
            ui.markdown('''
                ***
                © 2025 JLM
            '''),
            ),
        ),
)

# server
def server(input, output, session):
    @output
    @render_widget
    def myplot():
        fig = px.bar(prestaciones[prestaciones['nom_entidad'] == input.entidad_select()],
            x='cve_categoria',
            y='cantidad',
            hover_data=['cve_categoria','nom_categoria','cantidad'],
            labels={'cve_categoria':'Clave', 'nom_categoria':'Prestación', 'cantidad':'Total'},
            text='cantidad',
            )
        fig.update_traces(texttemplate='%{text:,.0f}',
            textfont_size=20,
            textangle=-90,
            textposition='auto',
            marker_color='#9f2241',
            marker_line_color='#323232',
            marker_line_width=1.5,
            opacity=0.9,
            )
        fig.update_layout(
            autosize=True,
            font_family="Noto Sans",
            title_font_family="Noto Sans",
            title_font_color="#691c32",
            title=dict(text=f'Prestaciones del Personal Policial - {input.entidad_select()}',
                font=dict(size=25),
                automargin=True,
                yref='paper'
                ),
            plot_bgcolor='#f8f8f8',
            yaxis_tickfont_size=11,
            xaxis_tickfont_size=11,
            xaxis_tickangle=0,
            xaxis=dict(
                tickvals=prestaciones['cve_categoria'],
                title=dict(
                    text="Clave prestación",
                    font=dict(
                        size=14
                    )
                ),
            ),
            yaxis=dict(
                tickformat=",.0f",
                title=dict(
                    text="Personal",
                    font=dict(
                        size=14
                    )
                ),
            ),
        )
        return fig

app = App(app_ui, server)
