# libraries
import streamlit as st
from PIL import Image
import os


# core script
def main():
    
    # load image
    im = Image.open('sspc-sesnsp-small.png')
    # add image
    st.set_page_config(page_title="ENSU", page_icon = im, layout='centered')
    

    # hide streamlit logo and footer
    hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
    st.markdown(hide_default_format, unsafe_allow_html=True)


    # set image
    st.image('https://www.primeraplanadigital.com.mx/wp-content/uploads/2019/06/5-inseguridad-1-750x450.jpg', width=200)
    # set title and subtitle
    st.markdown("<h1><span style='color: #691c32;'>Percepción de Confianza en Policías Estatales</span></h1>",
        unsafe_allow_html=True)
    # author, date
    st.caption('Autor: Jesús LM')
    st.caption('Fecha de publicación: Ago, 2025')
    

    # sidebar image and text
    st.sidebar.image('sesnsp.png')
    st.sidebar.caption("Dirección General de Planeación")
    # header
    st.sidebar.markdown('### Introducción')
    st.sidebar.write('''
        La confianza de la ciudadanía en sus cuerpos policiales es un pilar fundamental para la seguridad y la
        gobernabilidad en cualquier nación.
        En México, esta percepción es monitoreada de cerca por el Instituto Nacional de Estadística y Geografía
        (INEGI) a través de encuestas como la Encuesta Nacional de Seguridad Pública Urbana (ENSU), cuyos
        resultados de 2025 ofrecen una valiosa fotografía sobre el sentir de la población respecto al desempeño y
        la fiabilidad de la policía estatal.
    ''')
    st.sidebar.write('')
    st.sidebar.caption("© 2025")
    
    # customize color of sidebar and text
    st.markdown("""
        <style>
            [data-testid=stSidebar] {
                background-color: #691c32;
                color: #ffff;
            }
        </style>
        """, unsafe_allow_html=True)

    # contents
    # --- section I ---
    st.markdown('### Evolución Trimestral por Entidad Federativa')
    
    # --- Define a dictionary of images ---
    line_images = {
        "Aguascalientes": "figures_new/Aguascalientes.svg",
        "Baja California Sur": "figures_new/Baja California Sur.svg",
        "Baja California": "figures_new/Baja California.svg",
        "Campeche": "figures_new/Campeche.svg",
        "Chiapas": "figures_new/Chiapas.svg",
        "Chihuahua": "figures_new/Chihuahua.svg",
        "Ciudad de México": "figures_new/Ciudad de México.svg",
        "Coahuila": "figures_new/coahuila.svg",
        "Colima": "figures_new/Colima.svg",
        "Durango": "figures_new/Durango.svg",
        "Guanajuato": "figures_new/Guanajuato.svg",
        "Guerrero": "figures_new/Guerrero.svg",
        "Hidalgo": "figures_new/Hidalgo.svg",
        "Jalisco": "figures_new/Jalisco.svg",
        "México": "figures_new/México.svg",
        "Michoacán": "figures_new/Michoacán.svg",
        "Morelos": "figures_new/Morelos.svg",
        "Nayarit": "figures_new/Nayarit.svg",
        "Nuevo León": "figures_new/Nuevo León.svg",
        "Oaxaca": "figures_new/Oaxaca.svg",
        "Puebla": "figures_new/Puebla.svg",
        "Querétaro": "figures_new/Querétaro.svg",
        "Quintana Roo": "figures_new/Quintana Roo.svg",
        "San Luis Potosí": "figures_new/San Luis Potosí.svg",
        "Sinaloa": "figures_new/Sinaloa.svg",
        "Sonora": "figures_new/Sonora.svg",
        "Tabasco": "figures_new/Tabasco.svg",
        "Tamaulipas": "figures_new/Tamaulipas.svg",
        "Tlaxcala": "figures_new/Tlaxcala.svg",
        "Veracruz": "figures_new/Veracruz.svg",
        "Yucatán": "figures_new/Yucatán.svg",
        "Zacatecas": "figures_new/Zacatecas.svg",
    }
    
    # Apply custom CSS to modify the selectbox width
    st.markdown(
    """
        <style>
        .stSelectbox > div > div {
            width: 240px;  /* Adjust this value to your desired width */
        }
        </style>
        """,
    unsafe_allow_html=True
    )

    # Create a selectbox using the keys from the 'images' dictionary
    selected_line_image = st.selectbox(
        "Selecciona un trimestre",
        list(line_images.keys()),
    )

    # --- Display the selected image ---
    if selected_line_image:
        # Get the URL for the selected image
        line_image_url = line_images[selected_line_image]

        # Use st.image to display the image from the URL
        st.image(line_image_url, caption=f"Evolución trimestral de {selected_line_image}.")


    # --- section II ---
    #st.markdown("---")
    st.markdown('### Comparativo por Entidad Federativa')

    # --- Define a dictionary of images ---
    bar_images = {
        "2015-03": "figures_new/2015-03.svg",
        "2015-06": "figures_new/2015-06.svg",
        "2015-09": "figures_new/2015-09.svg",
        "2015-12": "figures_new/2015-12.svg",
        "2016-03": "figures_new/2016-03.svg",
        "2016-06": "figures_new/2016-06.svg",
        "2016-09": "figures_new/2016-09.svg",
        "2016-12": "figures_new/2016-12.svg",
        "2017-03": "figures_new/2017-03.svg",
        "2017-06": "figures_new/2017-06.svg",
        "2017-09": "figures_new/2017-09.svg",
        "2017-12": "figures_new/2017-12.svg",
        "2018-03": "figures_new/2018-03.svg",
        "2018-06": "figures_new/2018-06.svg",
        "2018-09": "figures_new/2018-09.svg",
        "2018-12": "figures_new/2018-12.svg",
        "2019-03": "figures_new/2019-03.svg",
        "2019-06": "figures_new/2019-06.svg",
        "2019-09": "figures_new/2019-09.svg",
        "2019-12": "figures_new/2019-12.svg",
        "2020-03": "figures_new/2020-03.svg",
        "2020-06": "figures_new/2020-06.svg",
        "2020-12": "figures_new/2020-12.svg",
        "2021-03": "figures_new/2021-03.svg",
        "2021-06": "figures_new/2021-06.svg",
        "2021-09": "figures_new/2021-09.svg",
        "2021-12": "figures_new/2021-12.svg",
        "2022-03": "figures_new/2022-03.svg",
        "2022-06": "figures_new/2022-06.svg",
        "2022-09": "figures_new/2022-09.svg",
        "2022-12": "figures_new/2022-12.svg",
        "2023-03": "figures_new/2023-03.svg",
        "2023-06": "figures_new/2023-06.svg",
        "2023-09": "figures_new/2023-09.svg",
        "2023-12": "figures_new/2023-12.svg",
        "2024-03": "figures_new/2024-03.svg",
        "2024-06": "figures_new/2024-06.svg",
        "2024-09": "figures_new/2024-09.svg",
        "2024-12": "figures_new/2024-12.svg",
        "2025-03": "figures_new/2025-03.svg",
        "2025-06": "figures_new/2025-06.svg",
    }
    
    

    # Create a selectbox using the keys from the 'images' dictionary
    selected_bar_image = st.selectbox(
        "Selecciona un trimestre",
        list(bar_images.keys()),
    )

    # --- Display the selected image ---
    if selected_bar_image:
        # Get the URL for the selected image
        bar_image_url = bar_images[selected_bar_image]

        # Use st.image to display the image from the URL
        st.image(bar_image_url, caption=f"Comparativo por Entidad Federativa del trimestre {selected_bar_image}.")
    
    
if __name__ == "__main__":
    main()
