# Copyright (c) 2026 victor256sd
# All rights reserved.
# Changelog:
# 1/18/2026: Changed age range from 10 to 99, adjusted questions 
# to short form of 10 questions (GL provided) and included Spanish 
# option (GL provided), changed verbiage from Often to Always.
# 1/17/2026: Initial development.
#-------------------------------------------------------------------

import streamlit as st
import streamlit_authenticator as stauth
import openai
from openai import OpenAI
import os
import time
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from cryptography.fernet import Fernet
import re

# Disable the button called via on_click attribute.
def disable_button():
    st.session_state.disabled = True        

# Definitive CSS selectors for Streamlit 1.45.1+
st.markdown("""
<style>
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    div[data-testid="stStatusWidget"] {
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# Load config file with user credentials.
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initiate authentication.
authenticator = stauth.Authenticate(
    config['credentials'],
)

# Call user login form.
result_auth = authenticator.login("main")
    
# If login successful, continue to aitam page.
if st.session_state.get('authentication_status'):
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{st.session_state.get('name')}* !')

    # # Initialize chat history.
    # if "ai_response" not in st.session_state:
    #     st.session_state.ai_response = []
    
    # Model list, Vector store ID, assistant IDs (one for initial upload eval, 
    # the second for follow-up user questions).
    MODEL_LIST = ["gpt-4o-mini"] #, "gpt-4.1-nano", "gpt-4.1", "o4-mini"] "gpt-5-nano"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    VECTOR_STORE_ID = st.secrets["VECTOR_STORE_ID"]
    INSTRUCTION_ENCRYPTED = b'gAAAAABpbXsMkt_BC6C4XuxVk2ybwnUHMC62RjEYc9RZKoQd6l-ndeiagHULy5tFKHkdlkO2BJ0DfP93QW5c7MNiaf7-YWTOra1YfoYbITL3n4FdjbuqRP5Jhk9pMzcvqLDc_q3_3x4ayG6j2pcwpk7vB3rjXM3T1FqbDKiJ707bQjEIm05FbMRxRDh6FCZ-nXedVwr9096bzZnsVBf7omLJC8yl4zMuJKHNUu_kodvzUvatXw8geCJxul__0I5wkTFJiuqOwaibGfVdsJpP0UDbfEu1PCgg3sqJ_QcuJsZJEl5P-PHvzqajw7WxsEaC-j-trcova-TjpmEASnnKq9zE5VRIkOoauuYeuAP4ykvAxYe9c8X2iDIaM3pi8J3kw2kWCqN9lgiLHL7QQS6xmstddraKWVobJrkb-BI31ffS0GdlDQXeFvw5S5dPnDPK_PYRxbZpzUxblGvvlYtnGpgzpzffEJt4rrZ99G40xsvfIx0OpqmXwdUgZrjQ0r41RxY7UznMZmzh-s2PSTI-9dK51BmgEUV3D6tkBIfo9f6lFfmV08jR-Ri8YDpu3kslrYJCWSAbc3Zr2SL4q5UkLOl-1YGEiaQ_GNW3GrbjFpPkdKj84kvMJqianDh54ww5-9BOa9ZEYmC2bjrDb99IDQYw5IW5CAS-_x7DsnjDyeDCOfYK7RvzmJd8E-hzR1WZbZd02DxQcIjVnp0T4HeT6b8Zw_Ek0Yav5cV9ZoyDkRDWneZRIMjjbeoACypvOJlsr2WkGY9XSrt_Y-wC7mnKVAE1hfrSOi-PY69DZOw8JMay3uXiLVjisrQIOkDgsMx-Qe6TtvqjHjweWU6zjc-lhWkGlsuiHKkoUW7MVqyD2dBgieb6a1EcL3ig_UhgL7oEw1G_NVUPsDMy4Odh4-r2qZi133TfKDAzpzCc4WMTR7JJYFglH8aOnS8KLBnXSK0Fn-mo8UTd6pQbogEMPl5spFkIbXZPLitpAG3o7lSXeI0Em8WPrWiz6FOGU1xZSjEFbkGWdNHHNLAJZd_NAWYRqdDSmLI9-hDeSVtmlFo6qqsfIosI197y6cDmJMlZHa7ppJ_d3JHX-4ie8yP9vaQE8A_Xp_OC12ruW9meRiFkMuysT238E1ztgT4egbehKnBJl583SeAP4wjLlPkb6yrU-v4gDb0OcdCdlWOb2j0NV1Gu9YiVYfJVyXt2JMG_FAK0Rtc0WSI65mjZdZshS725mdNmNHzeOiOFq7S89mbhYvttsxhoB0otf9_yYqVWW-mUPqruy9879Gj8sXHHo4HsvOMwXpG43uZ3QOlqjoQTbZCTB_QQ94mHz1Kn_EWMw_Xi48ryLPcH0N8Ns9WAQPq8WEv04pvQmUBdlTXdPnjO7g62Sm8mvadXleAWKy_V5EOc-FknhXhqJTC0euPDBXzTt5KooR2Algfz4DHfJ0SlmcaN47WUCCCv10AGBM2QpnSO8vtb-3VGfFzA2wA1AANFj0QPdSXdOCBw5MZKlS7p3Hv2AMDnLAFhs31cJdYWy75QbTNmmZnpG42UhKaLrpSLSyDwakgc5Hiq376ltSpkTONqgvqgls26P0k2qtzeg751uXioI_dyrE8aaQZQZ9hW6joa6jEn3wL9vcnvhcwA_6K6t8X7Eh0UFUdX46DfJVbe8MHFPuZoTmzajQABPeooVQFKvzmnaNk0kbq3AL0E1GNCpzHQ3E8NSEA='

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()

    # Set page layout and title.
    st.set_page_config(page_title="Qué Sopa AI", page_icon=":hibiscus:", layout="wide")
    st.header(":hibiscus: Qué Sopa AI")
    st.markdown("###### An assessment of loneliness.")
    # st.markdown("###### Your starting point for educator ethics")
    st.markdown("*The below assessment is the UCLA Short Form Loneliness Scale, which is used to assess an individual's subjective feelings of loneliness and social isolation.*")
    
    # Field for OpenAI API key.
    openai_api_key = os.environ.get("OPENAI_API_KEY", None)

    # Retrieve user-selected openai model.
    # model: str = st.selectbox("Model", options=MODEL_LIST)
    model = "gpt-4o-mini"
        
    # If there's no openai api key, stop.
    if not openai_api_key:
        st.error("Please enter your OpenAI API key!")
        st.stop()

    name = st.text_input("Name")
    row1 = st.columns([2,2])
    age = row1[0].slider("Age", 10, 99)
    language = row1[1].selectbox("Language",["English", "Spanish"])

    # Create loneliness survey form.
    if language == "English":
        with st.form("ucla-short_form"):
            st.write("Please fill out the form below:")
            Q1 = st.selectbox("#1. How often do people respond kindly when you share your feelings or worries?", ["","Never", "Rarely", "Sometimes", "Always"])
            Q2 = st.selectbox("#2. Do you feel that people understand you, encourage you, and know you well?", ["","Never", "Rarely", "Sometimes", "Always"])
            Q3 = st.selectbox("#3. When you want to talk with someone or do something together, is it easy to connect with others?", ["","Never", "Rarely", "Sometimes", "Always"])
            Q4 = st.selectbox("#4. How often do you feel separate from others, even when you are with them?", ["","Never", "Rarely", "Sometimes", "Always"])
            Q5 = st.selectbox("#5. I have someone to eat with when I want to share a meal.", ["","Never", "Rarely", "Sometimes", "Always"])
            Q6 = st.selectbox("#6. Is it hard for you to make friends?", ["","Never", "Rarely", "Sometimes", "Always"])
            Q7 = st.selectbox("#7. How often do you wait a long time for others to contact you or reply to your messages?", ["","Never", "Rarely", "Sometimes", "Always"])
            Q8 = st.selectbox("#8. Is it easier for you to play games or watch events by yourself?", ["","Never", "Rarely", "Sometimes", "Always"])
            Q9 = st.selectbox("#9. How often do you feel left out when others get together without inviting you?", ["","Never", "Rarely", "Sometimes", "Always"])
            Q10 = st.selectbox("#10. How often do you feel hurt because you don’t have someone to laugh with or talk to about your thoughts and feelings?", ["","Never", "Rarely", "Sometimes", "Always"])

            submit = st.form_submit_button("Submit")

    # Q1 = st.selectbox("#1. How often do you feel that you are *in tune* with the people around you?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q2 = st.selectbox("#2. How often do you feel that you lack companionship?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q3 = st.selectbox("#3. How often do you feel that there is no one you can turn to?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q4 = st.selectbox("#4. How often do you feel alone?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q5 = st.selectbox("#5. How often do you feel part of a group of friends?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q6 = st.selectbox("#6. How often do you feel that you have a lot in common with the people around you?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q7 = st.selectbox("#7. How often do you feel that you are no longer close to anyone?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q8 = st.selectbox("#8. How often do you feel that your interests and ideas are not shared by those around you?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q9 = st.selectbox("#9. How often do you feel outgoing and friendly?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q10 = st.selectbox("#10. How often do you feel close to people?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q11 = st.selectbox("#11. How often do you feel left out?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q12 = st.selectbox("#12. How often do you feel that your relationships with others are not meaningful?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q13 = st.selectbox("#13. How often do you feel that no one really knows you well?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q14 = st.selectbox("#14. How often do you feel isolated from others?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q15 = st.selectbox("#15. How often do you feel you can find companionship when you want it?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q16 = st.selectbox("#16. How often do you feel that there are people who really understand you?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q17 = st.selectbox("#17. How often do you feel shy?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q18 = st.selectbox("#18. How often do you feel that people are around you but not with you?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q19 = st.selectbox("#19. How often do you feel that there are people you can talk to?", ["","Never", "Rarely", "Sometimes", "Often"])
        # Q20 = st.selectbox("#20. How often do you feel that there are people you can turn to?", ["","Never", "Rarely", "Sometimes", "Often"])
        
    elif language == "Spanish":
        with st.form("ucla-short_form"):
            st.write("Favor de completar el formulario abajo:")
            Q1 = st.selectbox("#1. ¿Con qué frecuencia las personas responden con amabilidad cuando compartes tus sentimientos o preocupaciones?", ["", "Nunca", "Casi Nunca", "A Veces", "Siempre"])
            Q2 = st.selectbox("#2. ¿Sientes que las personas te entienden, te apoyan y te conocen bien?", ["", "Nunca", "Casi Nunca", "A Veces", "Siempre"])
            Q3 = st.selectbox("#3. Cuando quieres hablar con alguien o hacer algo juntos, ¿te resulta fácil conectar con esa persona?", ["", "Nunca", "Casi Nunca", "A Veces", "Siempre"])
            Q4 = st.selectbox("#4. ¿Con qué frecuencia te sientes separado de los demás, incluso cuando estás con ellos?", ["", "Nunca", "Casi Nunca", "A Veces", "Siempre"])
            Q5 = st.selectbox("#5. Tengo a alguien con quien comer cuando quiero compartir una comida.", ["", "Nunca", "Casi Nunca", "A Veces", "Siempre"])
            Q6 = st.selectbox("#6. ¿Te resulta difícil hacer amigos?", ["", "Nunca", "Casi Nunca", "A Veces", "Siempre"])
            Q7 = st.selectbox("#7. ¿Con qué frecuencia esperas mucho tiempo a que otras personas se comuniquen contigo o respondan a tus mensajes?", ["", "Nunca", "Casi Nunca", "A Veces", "Siempre"])
            Q8 = st.selectbox("#8. ¿Te resulta más fácil jugar o ver eventos tú solo(a)?", ["", "Nunca", "Casi Nunca", "A Veces", "Siempre"])
            Q9 = st.selectbox("#9. ¿Con qué frecuencia te sientes excluido(a) cuando otras personas se reúnen sin invitarte?", ["", "Nunca", "Casi Nunca", "A Veces", "Siempre"])
            Q10 = st.selectbox("#10. ¿Con qué frecuencia te sientes herido(a) porque no tienes a alguien con quien reír o hablar de tus pensamientos y sentimientos?", ["", "Nunca", "Casi Nunca", "A Veces", "Siempre"])

            submit = st.form_submit_button("Enviar")
    
    if submit and language == "English":
        Q_total = 0
        Q_response = ""
        Q_rawdata = name + "," + str(age) + ","

        # Questions 1, 2, 3, and 5 scored in reverse.
        # Scored in reverse.
        if Q1 == "Never": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q1:How often do people respond kindly when you share your feelings or worries?=Never,"
        elif Q1 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q1:How often do people respond kindly when you share your feelings or worries?=Rarely,"
        elif Q1 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q1:How often do people respond kindly when you share your feelings or worries?=Sometimes,"
        elif Q1 == "Always":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q1:How often do people respond kindly when you share your feelings or worries?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q1:How often do people respond kindly when you share your feelings or worries?=No Answer,"
        
        # Scored in reverse.
        if Q2 == "Never": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people understand you, encourage you, and know you well?=Never,"
        elif Q2 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people understand you, encourage you, and know you well?=Rarely,"
        elif Q2 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people understand you, encourage you, and know you well?=Sometimes,"
        elif Q2 == "Always":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people understand you, encourage you, and know you well?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people understand you, encourage you, and know you well?=No Answer,"

        # Scored in reverse.
        if Q3 == "Never": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q3:When you want to talk with someone or do something together, is it easy to connect with others?=Never,"
        elif Q3 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q3:When you want to talk with someone or do something together, is it easy to connect with others?=Rarely,"
        elif Q3 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q3:When you want to talk with someone or do something together, is it easy to connect with others?=Sometimes,"
        elif Q3 == "Always":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q3:When you want to talk with someone or do something together, is it easy to connect with others?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q3:When you want to talk with someone or do something together, is it easy to connect with others?=No Answer,"

        if Q4 == "Never": 
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q4:How often do you feel separate from others, even when you are with them?=Never,"
        elif Q4 == "Rarely":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q4:How often do you feel separate from others, even when you are with them?=Rarely,"
        elif Q4 == "Sometimes":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q4:How often do you feel separate from others, even when you are with them?=Sometimes,"
        elif Q4 == "Always":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q4:How often do you feel separate from others, even when you are with them?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q4:How often do you feel separate from others, even when you are with them?=No Answer,"

        # Scored in reverse.
        if Q5 == "Never": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q5:I have someone to eat with when I want to share a meal.=Never,"
        elif Q5 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q5:I have someone to eat with when I want to share a meal.=Rarely,"
        elif Q5 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q5:I have someone to eat with when I want to share a meal.=Sometimes,"
        elif Q5 == "Always":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q5:I have someone to eat with when I want to share a meal.=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q5:I have someone to eat with when I want to share a meal.=No Answer,"
        
        if Q6 == "Never": 
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q6:Is it hard for you to make friends?=Never,"
        elif Q6 == "Rarely":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q6:Is it hard for you to make friends?=Rarely,"
        elif Q6 == "Sometimes":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q6:Is it hard for you to make friends?=Sometimes,"
        elif Q6 == "Always":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q6:Is it hard for you to make friends?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q6:Is it hard for you to make friends?=No Answer,"
    
        if Q7 == "Never": 
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q7:How often do you wait a long time for others to contact you or reply to your messages?=Never,"
        elif Q7 == "Rarely":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q7:How often do you wait a long time for others to contact you or reply to your messages?=Rarely,"
        elif Q7 == "Sometimes":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q7:How often do you wait a long time for others to contact you or reply to your messages?=Sometimes,"
        elif Q7 == "Always":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q7:How often do you wait a long time for others to contact you or reply to your messages?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q7:How often do you wait a long time for others to contact you or reply to your messages?=No Answer,"

        if Q8 == "Never": 
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or watch events by yourself?=Never,"
        elif Q8 == "Rarely":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or watch events by yourself?=Rarely,"
        elif Q8 == "Sometimes":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or watch events by yourself?=Sometimes,"
        elif Q8 == "Always":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or watch events by yourself?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or watch events by yourself?=No Answer,"

        if Q9 == "Never": 
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q9:How often do you feel left out when others get together without inviting you?=Never,"
        elif Q9 == "Rarely":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q9:How often do you feel left out when others get together without inviting you?=Rarely,"
        elif Q9 == "Sometimes":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q9:How often do you feel left out when others get together without inviting you?=Sometimes,"
        elif Q9 == "Always":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q9:How often do you feel left out when others get together without inviting you?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q9:How often do you feel left out when others get together without inviting you?=No Answer,"

        if Q10 == "Never": 
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q10:How often do you feel hurt because you don’t have someone to laugh with or talk to about your thoughts and feelings?=Never,"
        elif Q10 == "Rarely":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q10:How often do you feel hurt because you don’t have someone to laugh with or talk to about your thoughts and feelings?=Rarely,"
        elif Q10 == "Sometimes":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q10:How often do you feel hurt because you don’t have someone to laugh with or talk to about your thoughts and feelings?=Sometimes,"
        elif Q10 == "Always":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q10:How often do you feel hurt because you don’t have someone to laugh with or talk to about your thoughts and feelings?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q10:How often do you feel hurt because you don’t have someone to laugh with or talk to about your thoughts and feelings?=No Answer,"

        if Q_total < 10:
            st.markdown("Please answer all questions.")
        elif Q_total < 25:
            st.write(f"#### Total Score: {Q_total} (Average)")
            Q_response = "Average."
        elif Q_total >= 25 and Q_total <= 29:
            st.write(f"#### Total Score: {Q_total} (High level of loneliness)")
            Q_response = "High level of loneliness."
        elif Q_total >= 30:
            st.write(f"#### Total Score: {Q_total} (Very high level of loneliness)")
            Q_response = "Very high level of loneliness."

        if Q_total >= 10:
            st.markdown("For additional information and resources, please visit: [US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")
            Q_rawdata = Q_rawdata + "Score=" + str(Q_total)

    if submit and language == "Spanish":
        Q_total = 0
        Q_response = ""
        Q_rawdata = name + "," + str(age) + ","

        # Questions 1, 2, 3, and 5 scored in reverse.
        # Scored in reverse.
        if Q1 == "Nunca": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q1:¿Con qué frecuencia las personas responden con amabilidad cuando compartes tus sentimientos o preocupaciones?=Nunca,"
        elif Q1 == "Casi Nunca":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q1:¿Con qué frecuencia las personas responden con amabilidad cuando compartes tus sentimientos o preocupaciones?=Casi Nunca,"
        elif Q1 == "A Veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q1:¿Con qué frecuencia las personas responden con amabilidad cuando compartes tus sentimientos o preocupaciones?=A Veces,"
        elif Q1 == "Siempre":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q1:¿Con qué frecuencia las personas responden con amabilidad cuando compartes tus sentimientos o preocupaciones?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q1:¿Con qué frecuencia las personas responden con amabilidad cuando compartes tus sentimientos o preocupaciones?=No Contesta,"
        
        # Scored in reverse.
        if Q2 == "Nunca": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te entienden, te apoyan y te conocen bien?=Nunca,"
        elif Q2 == "Casi Nunca":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te entienden, te apoyan y te conocen bien?=Casi Nunca,"
        elif Q2 == "A Veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te entienden, te apoyan y te conocen bien?=A Veces,"
        elif Q2 == "Siempre":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te entienden, te apoyan y te conocen bien?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te entienden, te apoyan y te conocen bien?=No Contesta,"

        # Scored in reverse.
        if Q3 == "Nunca": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q3:Cuando quieres hablar con alguien o hacer algo juntos, ¿te resulta fácil conectar con esa persona?=Nunca,"
        elif Q3 == "Casi Nunca":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q3:Cuando quieres hablar con alguien o hacer algo juntos, ¿te resulta fácil conectar con esa persona?=Casi Nunca,"
        elif Q3 == "A Veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q3:Cuando quieres hablar con alguien o hacer algo juntos, ¿te resulta fácil conectar con esa persona?=A Veces,"
        elif Q3 == "Siempre":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q3:Cuando quieres hablar con alguien o hacer algo juntos, ¿te resulta fácil conectar con esa persona?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q3:Cuando quieres hablar con alguien o hacer algo juntos, ¿te resulta fácil conectar con esa persona?=No Contesta,"

        if Q4 == "Nunca": 
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q4:¿Con qué frecuencia te sientes separado de los demás, incluso cuando estás con ellos?=Nunca,"
        elif Q4 == "Casi Nunca":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q4:¿Con qué frecuencia te sientes separado de los demás, incluso cuando estás con ellos?=Casi Nunca,"
        elif Q4 == "A Veces":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q4:¿Con qué frecuencia te sientes separado de los demás, incluso cuando estás con ellos?=A Veces,"
        elif Q4 == "Siempre":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q4:¿Con qué frecuencia te sientes separado de los demás, incluso cuando estás con ellos?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q4:¿Con qué frecuencia te sientes separado de los demás, incluso cuando estás con ellos?=No Contesta,"

        # Scored in reverse.
        if Q5 == "Nunca": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q5:Tengo a alguien con quien comer cuando quiero compartir una comida.=Nunca,"
        elif Q5 == "Casi Nunca":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q5:Tengo a alguien con quien comer cuando quiero compartir una comida.=Casi Nunca,"
        elif Q5 == "A Veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q5:Tengo a alguien con quien comer cuando quiero compartir una comida.=A Veces,"
        elif Q5 == "Siempre":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q5:Tengo a alguien con quien comer cuando quiero compartir una comida.=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q5:Tengo a alguien con quien comer cuando quiero compartir una comida.=No Contesta,"
        
        if Q6 == "Nunca": 
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q6:¿Te resulta difícil hacer amigos?=Nunca,"
        elif Q6 == "Casi Nunca":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q6:¿Te resulta difícil hacer amigos?=Casi Nunca,"
        elif Q6 == "A Veces":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q6:¿Te resulta difícil hacer amigos?=A Veces,"
        elif Q6 == "Siempre":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q6:¿Te resulta difícil hacer amigos?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q6:¿Te resulta difícil hacer amigos?=No Contesta,"
    
        if Q7 == "Nunca": 
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q7:¿Con qué frecuencia esperas mucho tiempo a que otras personas se comuniquen contigo o respondan a tus mensajes?=Nunca,"
        elif Q7 == "Casi Nunca":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q7:¿Con qué frecuencia esperas mucho tiempo a que otras personas se comuniquen contigo o respondan a tus mensajes?=Casi Nunca,"
        elif Q7 == "A Veces":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q7:¿Con qué frecuencia esperas mucho tiempo a que otras personas se comuniquen contigo o respondan a tus mensajes?=A Veces,"
        elif Q7 == "Siempre":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q7:¿Con qué frecuencia esperas mucho tiempo a que otras personas se comuniquen contigo o respondan a tus mensajes?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q7:¿Con qué frecuencia esperas mucho tiempo a que otras personas se comuniquen contigo o respondan a tus mensajes?=No Contesta,"

        if Q8 == "Nunca": 
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q8:¿Te resulta más fácil jugar o ver eventos tú solo(a)?=Nunca,"
        elif Q8 == "Casi Nunca":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q8:¿Te resulta más fácil jugar o ver eventos tú solo(a)?=Casi Nunca,"
        elif Q8 == "A Veces":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q8:¿Te resulta más fácil jugar o ver eventos tú solo(a)?=A Veces,"
        elif Q8 == "Siempre":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q8:¿Te resulta más fácil jugar o ver eventos tú solo(a)?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q8:¿Te resulta más fácil jugar o ver eventos tú solo(a)?=No Contesta,"

        if Q9 == "Nunca": 
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q9:¿Con qué frecuencia te sientes excluido(a) cuando otras personas se reúnen sin invitarte?=Nunca,"
        elif Q9 == "Casi Nunca":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q9:¿Con qué frecuencia te sientes excluido(a) cuando otras personas se reúnen sin invitarte?=Casi Nunca,"
        elif Q9 == "A Veces":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q9:¿Con qué frecuencia te sientes excluido(a) cuando otras personas se reúnen sin invitarte?=A Veces,"
        elif Q9 == "Siempre":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q9:¿Con qué frecuencia te sientes excluido(a) cuando otras personas se reúnen sin invitarte?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q9:¿Con qué frecuencia te sientes excluido(a) cuando otras personas se reúnen sin invitarte?=No Contesta,"

        if Q10 == "Nunca": 
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q10:¿Con qué frecuencia te sientes herido(a) porque no tienes a alguien con quien reír o hablar de tus pensamientos y sentimientos?=Nunca,"
        elif Q10 == "Casi Nunca":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q10:¿Con qué frecuencia te sientes herido(a) porque no tienes a alguien con quien reír o hablar de tus pensamientos y sentimientos?=Casi Nunca,"
        elif Q10 == "A Veces":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q10:¿Con qué frecuencia te sientes herido(a) porque no tienes a alguien con quien reír o hablar de tus pensamientos y sentimientos?=A Veces,"
        elif Q10 == "Siempre":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q10:¿Con qué frecuencia te sientes herido(a) porque no tienes a alguien con quien reír o hablar de tus pensamientos y sentimientos?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q10:¿Con qué frecuencia te sientes herido(a) porque no tienes a alguien con quien reír o hablar de tus pensamientos y sentimientos?=No Contesta,"

        if Q_total < 10:
            st.markdown("Contesta todas preguntas, por favor.")
        elif Q_total < 25:
            st.write(f"#### Puntos Totales: {Q_total} (Medio)")
            Q_response = "Medio."
        elif Q_total >= 25 and Q_total <= 29:
            st.write(f"#### Puntos Totales: {Q_total} (Alto nivel de soledad)")
            Q_response = "Alto nivel de soledad."
        elif Q_total >= 30:
            st.write(f"#### Puntos Totales: {Q_total} (Muy alto nivel de soledad)")
            Q_response = "Muy alto nivel de soledad."

        if Q_total >= 10:
            st.markdown("Para más información y recursos, favor de visitar: [US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")
            Q_rawdata = Q_rawdata + "Score=" + str(Q_total)

        # Questions 1, 5, 6, 9, 10, 15, 16, 19, 20 are scored in reverse.
        # Questions 2, 3, 4, 7, 8, 11, 12, 13, 14, 17, 18 scored normally.
        # if Q11 == "Never": 
        #     Q_total = Q_total + 1
        #     Q_rawdata = Q_rawdata + "Q11=1,"
        # elif Q11 == "Rarely":
        #     Q_total = Q_total + 2
        #     Q_rawdata = Q_rawdata + "Q11=2,"
        # elif Q11 == "Sometimes":
        #     Q_total = Q_total + 3
        #     Q_rawdata = Q_rawdata + "Q11=3,"
        # elif Q11 == "Often":
        #     Q_total = Q_total + 4
        #     Q_rawdata = Q_rawdata + "Q11=4,"
        # else:
        #     Q_rawdata = Q_rawdata + "Q11=0,"
    
        # if Q12 == "Never": 
        #     Q_total = Q_total + 1
        #     Q_rawdata = Q_rawdata + "Q12=1,"
        # elif Q12 == "Rarely":
        #     Q_total = Q_total + 2
        #     Q_rawdata = Q_rawdata + "Q12=2,"
        # elif Q12 == "Sometimes":
        #     Q_total = Q_total + 3
        #     Q_rawdata = Q_rawdata + "Q12=3,"
        # elif Q12 == "Often":
        #     Q_total = Q_total + 4
        #     Q_rawdata = Q_rawdata + "Q12=4,"
        # else:
        #     Q_rawdata = Q_rawdata + "Q12=0,"

        # if Q13 == "Never": 
        #     Q_total = Q_total + 1
        #     Q_rawdata = Q_rawdata + "Q13=1,"
        # elif Q13 == "Rarely":
        #     Q_total = Q_total + 2
        #     Q_rawdata = Q_rawdata + "Q13=2,"
        # elif Q13 == "Sometimes":
        #     Q_total = Q_total + 3
        #     Q_rawdata = Q_rawdata + "Q13=3,"
        # elif Q13 == "Often":
        #     Q_total = Q_total + 4
        #     Q_rawdata = Q_rawdata + "Q13=4,"
        # else:
        #     Q_rawdata = Q_rawdata + "Q13=0,"

        # if Q14 == "Never": 
        #     Q_total = Q_total + 1
        #     Q_rawdata = Q_rawdata + "Q14=1,"
        # elif Q14 == "Rarely":
        #     Q_total = Q_total + 2
        #     Q_rawdata = Q_rawdata + "Q14=2,"
        # elif Q14 == "Sometimes":
        #     Q_total = Q_total + 3
        #     Q_rawdata = Q_rawdata + "Q14=3,"
        # elif Q14 == "Often":
        #     Q_total = Q_total + 4
        #     Q_rawdata = Q_rawdata + "Q14=4,"
        # else:
        #     Q_rawdata = Q_rawdata + "Q14=0,"

        # Scored in reverse.
        # if Q15 == "Never": 
        #     Q_total = Q_total + 4
        #     Q_rawdata = Q_rawdata + "Q15=4,"
        # elif Q15 == "Rarely":
        #     Q_total = Q_total + 3
        #     Q_rawdata = Q_rawdata + "Q15=3,"
        # elif Q15 == "Sometimes":
        #     Q_total = Q_total + 2
        #     Q_rawdata = Q_rawdata + "Q15=2,"
        # elif Q15 == "Often":
        #     Q_total = Q_total + 1
        #     Q_rawdata = Q_rawdata + "Q15=1,"
        # else:
        #     Q_rawdata = Q_rawdata + "Q15=0,"

        # Scored in reverse.
        # if Q16 == "Never": 
        #     Q_total = Q_total + 4
        #     Q_rawdata = Q_rawdata + "Q16=4,"
        # elif Q16 == "Rarely":
        #     Q_total = Q_total + 3
        #     Q_rawdata = Q_rawdata + "Q16=3,"
        # elif Q16 == "Sometimes":
        #     Q_total = Q_total + 2
        #     Q_rawdata = Q_rawdata + "Q16=2,"
        # elif Q16 == "Often":
        #     Q_total = Q_total + 1
        #     Q_rawdata = Q_rawdata + "Q16=1,"
        # else:
        #     Q_rawdata = Q_rawdata + "Q16=0,"
    
        # if Q17 == "Never": 
        #     Q_total = Q_total + 1
        #     Q_rawdata = Q_rawdata + "Q17=1,"
        # elif Q17 == "Rarely":
        #     Q_total = Q_total + 2
        #     Q_rawdata = Q_rawdata + "Q17=2,"
        # elif Q17 == "Sometimes":
        #     Q_total = Q_total + 3
        #     Q_rawdata = Q_rawdata + "Q17=3,"
        # elif Q17 == "Often":
        #     Q_total = Q_total + 4
        #     Q_rawdata = Q_rawdata + "Q17=4,"
        # else:
        #     Q_rawdata = Q_rawdata + "Q17=0,"

        # if Q18 == "Never": 
        #     Q_total = Q_total + 1
        #     Q_rawdata = Q_rawdata + "Q18=1,"
        # elif Q18 == "Rarely":
        #     Q_total = Q_total + 2
        #     Q_rawdata = Q_rawdata + "Q18=2,"
        # elif Q18 == "Sometimes":
        #     Q_total = Q_total + 3
        #     Q_rawdata = Q_rawdata + "Q18=3,"
        # elif Q18 == "Often":
        #     Q_total = Q_total + 4
        #     Q_rawdata = Q_rawdata + "Q18=4,"
        # else:
        #     Q_rawdata = Q_rawdata + "Q18=0,"

        # Scored in reverse.
        # if Q19 == "Never": 
        #     Q_total = Q_total + 4
        #     Q_rawdata = Q_rawdata + "Q19=4,"
        # elif Q19 == "Rarely":
        #     Q_total = Q_total + 3
        #     Q_rawdata = Q_rawdata + "Q19=3,"
        # elif Q19 == "Sometimes":
        #     Q_total = Q_total + 2
        #     Q_rawdata = Q_rawdata + "Q19=2,"
        # elif Q19 == "Often":
        #     Q_total = Q_total + 1
        #     Q_rawdata = Q_rawdata + "Q19=1,"
        # else:
        #     Q_rawdata = Q_rawdata + "Q19=0,"
    
        # Scored in reverse.
        # if Q20 == "Never": 
        #     Q_total = Q_total + 4
        #     Q_rawdata = Q_rawdata + "Q20=4,"
        # elif Q20 == "Rarely":
        #     Q_total = Q_total + 3
        #     Q_rawdata = Q_rawdata + "Q20=3,"
        # elif Q20 == "Sometimes":
        #     Q_total = Q_total + 2
        #     Q_rawdata = Q_rawdata + "Q20=2,"
        # elif Q20 == "Often":
        #     Q_total = Q_total + 1
        #     Q_rawdata = Q_rawdata + "Q20=1,"
        # else:
        #     Q_rawdata = Q_rawdata + "Q20=0,"
    
    # Create new form to search aitam library vector store.    
    # with st.form(key="qa_form", clear_on_submit=False, height=300):
    #     query = st.text_area("**What would you like to discuss?**", height="stretch")
    #     submit = st.form_submit_button("Send")
        
    # If submit button is clicked, query the aitam library.            
    if submit and Q_total >= 10:
        # If form is submitted without a query, stop.
        query = f"(For later reference: {Q_rawdata}) Please provide insights and recommendations to me regarding loneliness in {language}. I scored a {Q_total} on the UCLA Short Form Loneliness Scale, which indicated the following: {Q_response}"
        # Setup output columns to display results.
        # answer_col, sources_col = st.columns(2)
        # Create new client for this submission.
        client2 = OpenAI(api_key=openai_api_key)
        # Query the aitam library vector store and include internet
        # serach results.
        with st.spinner('Searching...'):
            response2 = client2.responses.create(
                instructions = INSTRUCTION,
                input = query,
                model = model,
                temperature = 0.6,
                # text={
                #     "verbosity": "low"
                # },
                tools = [{
                            "type": "file_search",
                            "vector_store_ids": [VECTOR_STORE_ID],
                }],
                include=["output[*].file_search_call.search_results"]
            )
        # Write response to the answer column.    
        # with answer_col:
        try:
            cleaned_response = re.sub(r'【.*?†.*?】', '', response2.output_text) #output[1].content[0].text)
        except:
            cleaned_response = re.sub(r'【.*?†.*?】', '', response2.output[1].content[0].text)

        if language == "English":
            st.markdown("#### Qué Sopa AI Guidance")
            st.write("*The guidance and responses provided by this application are AI-generated and informed by the US Surgeon General's report Our Epidemic of Loneliness and Isolation and related professional resources. They are intended for informational and educational purposes only and do not constitute legal advice, official policy interpretation, or a substitute for professional judgment. Users should consult their professional policies, state regulations, or legal counsel for authoritative guidance on loneliness and isolation matters. This tool is designed to assist, not replace, professional decision-making or formal review processes.*")
        elif language == "Spanish":
            st.markdown("#### Qué Sopa AI Información")
            st.write("*La información y las respuestas proporcionadas por esta aplicación son generadas por IA y se basan en el informe del Cirujano General de EE. UU., Nuestro Epidemia de Soledad y Aislamiento, y en recursos profesionales relacionados. Están destinadas únicamente a fines informativos y educativos y no constituyen asesoramiento legal, interpretación oficial de políticas ni un sustituto del juicio profesional. Los usuarios deben consultar sus políticas profesionales, regulaciones estatales o asesoría legal para obtener orientación autorizada sobre asuntos de soledad y aislamiento. Esta herramienta está diseñada para asistir, no para reemplazar, la toma de decisiones profesional o los procesos de revisión formal.*")
            
        st.markdown(cleaned_response)

        if language == "English":
            st.markdown("#### Sources")
        elif language == "Spanish":
            st.markdown("#### Fuentes")
            
        # Extract annotations from the response, and print source files.
        try:
            annotations = response2.output[1].content[0].annotations
            retrieved_files = set([response2.filename for response2 in annotations])
            file_list_str = ", ".join(retrieved_files)
            if language == "English":
                st.markdown(f"**File(s):** {file_list_str}")
            elif language == "Spanish":
                st.markdown(f"**Archivo(s):** {file_list_str}")
        except (AttributeError, IndexError):
            if language == "English":
                st.markdown("**File(s): n/a**")
            elif language == "Spanish":
                st.markdown("**Archivo(s): n/a**")

        # st.session_state.ai_response = cleaned_response
        # Write files used to generate the answer.
        # with sources_col:
        #     st.markdown("#### Sources")
        #     # Extract annotations from the response, and print source files.
        #     annotations = response2.output[1].content[0].annotations
        #     retrieved_files = set([response2.filename for response2 in annotations])
        #     file_list_str = ", ".join(retrieved_files)
        #     st.markdown(f"**File(s):** {file_list_str}")

            # st.markdown("#### Token Usage")
            # input_tokens = response2.usage.input_tokens
            # output_tokens = response2.usage.output_tokens
            # total_tokens = input_tokens + output_tokens
            # input_tokens_str = f"{input_tokens:,}"
            # output_tokens_str = f"{output_tokens:,}"
            # total_tokens_str = f"{total_tokens:,}"

            # st.markdown(
            #     f"""
            #     <p style="margin-bottom:0;">Input Tokens: {input_tokens_str}</p>
            #     <p style="margin-bottom:0;">Output Tokens: {output_tokens_str}</p>
            #     """,
            #     unsafe_allow_html=True
            # )
            # st.markdown(f"Total Tokens: {total_tokens_str}")

            # if model == "gpt-4.1-nano":
            #     input_token_cost = .1/1000000
            #     output_token_cost = .4/1000000
            # elif model == "gpt-4o-mini":
            #     input_token_cost = .15/1000000
            #     output_token_cost = .6/1000000
            # elif model == "gpt-4.1":
            #     input_token_cost = 2.00/1000000
            #     output_token_cost = 8.00/1000000
            # elif model == "o4-mini":
            #     input_token_cost = 1.10/1000000
            #     output_token_cost = 4.40/1000000

            # cost = input_tokens*input_token_cost + output_tokens*output_token_cost
            # formatted_cost = "${:,.4f}".format(cost)
            
            # st.markdown(f"**Total Cost:** {formatted_cost}")

    # elif not submit:
    #         st.markdown("#### Response")
    #         st.markdown(st.session_state.ai_response)

elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
