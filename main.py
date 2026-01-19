#-------------------------------------------------------------------
# Copyright (c) 2026 victor256sd
# All rights reserved.
#
# Changelog:
#
# 1/19/2026: Changed Medium interpretation to Low, point AI to 
# consider specific questions and answers on the assessment. Modi-
# fied the query prompt. Resources are 
#
# 1/18/2026: Changed age range from 10 to 99, adjusted questions 
# to short form of 10 questions (GL provided) and included Spanish 
# option (GL provided), changed verbiage from Often to Always.
#
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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpblWp8As_ClhCEVUnkgTWfKi19Nhxp8ZKMG8-8b-1XkT-rt8aFddEyy_-RYSzkMqzNLlksDP7LvmspiOieMiUBxKHMvRklMQM6tVNboXQD3iZBXio17qAEg6ljhz7Ub_hMBZrTn0xoj7AX897UUgyK0NUE2mU0AwFNchJZMJx3GEkUKuhNBWldgixwsSgtcZ9dmS2lgBxmbijnRq-BK80yLQba3n5-ZNFmtoNKmDd14p1SKOgggUcW9BYUohjap4UbHHuM8R9p1XxJtpC6WlVFZSfr0PpD7VSyXoM62ILke6uZeXPe_gaeNdr11FKKkpQGDYRhH3xNa9ySGiOmtzdHTw4_1ooxxQFp0I8HGQwbTEvWFe6brVm-_4-jHp2_iZ5rk9Ab08qdraN8JciZOyWHK1z0kbTE2zxDIsA1-WHNBqEY8OzVV-z3MlhqLUXVo73t57rCltu_JXHC0sUpYMfIMrcwXQwfuFiEWAghCRicYk3-MHuTYQBfKbgkqfs0Q8WP_17EtnpQDhAjL0FJLwAsau85x-7nU4PM6AWWoVKJra3hOZbE6m_ghflQdjQx284HlMu7knNyN6oGFLOjYBF7YwMtS9B8y_NsWqBHI9GGwi7ebApzaKXhhJMl7NEpoVQMHlgbcEW_vcwJevaEZt6MBoMh6OtDDeVNCWHDAA1XacOhvJCtMqWsR7xfGYTK6Hzav6tJpiMYNtUW5cFWOANZlvv50UYHGNA1tmn5NQk5siVSmH_zCDWFfwpEe1QrY4YpvDOMds_xt0W_WG_s5rvIDKeahn1ujgfMoEZ5LM2UrdDqycLRCjiHGAg63nnJQFoQtDPB2-5GcrFCzx8TXXYiVBp2clwiJo7TZu33pMxcGctyBUuDx-1uTsnVV5CeZN6S1AAmMKiP24uZASE0TfYnjSwjO6UwbKTQNsiGkSoZy8iJq3FKKye10qTWH6-aNkH1fzSkpzIaYCtYP7Kz4E44cnWTjAwgS1FWLlPHpHPe3Gdzh65QWfbcBol0ZFvjINGZxgctU2gFaKXsbl1v0zNbXFW8EeSlUY7pYkKjKaOQ25WsXYqk6_pVWfmTGLVdUERUEDVHSKzB9oTTPMec1MgNoCfK3G62yHkxxNVBfUtEJYp0y5eybj1kGt3qGsirsHE-VSYkJPP5jEdZurxXDPnUVZFH2_5m5OpqpLC_UxDWZduA5Wmf3LJswRiKoJgh4QK6Mu1rudEUN6LQAATBAUW6hpcr4o3LLNum6SKB3P7OWh3i2wAbJjK0fjai66YU_cISgpUFwX-w5zYNxDaxL4aUHwS5BotvPtU7CBW5HCa0tP_VdF9r-4MabyAA_bRzFnGBft0Z6aLLdjoq7qp6M3dfSnBgfbcc1mYjyG9SLBwix0J9moAKPXtThGI7wWCC7IZLjAER_vn9fVX5SWPyH2GUP3oxlAexcK49WCYtUFTG3W_0d34J9i87zd9i-zKE9YO8b8n7acz4z2Y0vqu_Pgv1reEsxX4je7TvXjSlh9FCr1F_H5WKrEr5-p_xjR5FB-YrzVKQu_pWWeePwP44b5CUdSRZdkO2MGMhe4iZN-tup4t-0aDACUg_YVsACliXuEJ6gSUNFgNfcOoz7JsZhf-SvjAJnk5Zbqux2aH_-VYPu1Kjnum9wHibOAGDQYLQP2YoW5zkJLrLJ5hwXt7kKoQAM1YPVF36pCvFIH40Dvfbf1NvrsUOKoDJ0aw6MJnreIpYuFOumAqRWlOkP_4kn8LJbUqBkppYWuVFWwtDHDSqwN_GhoXhjvbxLsUuP6sFOeKlwnA_1U3_7dLAeIbLl3nsVL1YHugsfH7LkiBu3-Kv4A8lEhs3Icpoj1_Xx4OYJ8S82y_CKjbGzAuAb6LqG1oVAj4f-N4WDddgBjnHFsUuOMXB8Z5kDHIkhSVze2Y3j9YZETKHBFrYlwH54BN7l3rTz7ScVmk0zI7EkE5FQUxIorTr3eTxhiMpxOCyZCT4xq8ya1TFC7lJoCnvgBXRJJl85Vj3eIwbt6_5MOKuVsaOGpMH44HaZU7AMLqoxRUuzmg4ddWlanmomHE65O5gu52MyWQNQArCMmVs77fXcAe2eKAJdXXQvDZBH1wnyFqoI8g02MvRR0jMCukcujy5Kg7rEn5mGJ-55BzG1qjNXrUJRXK9i1-gLqEesfCc74A0r3sAEgxtz-v_Mhc6nXX0_vujaX5PieqjECtWmgDfIGMgHiRkvV07oBhjqaQOEvFe5fiLGRJhGnd-bmmXSfXov-dbl7pk5EKX234OrDyXs_X-yZBONe5AZwVqrZwBirsuYbUT8LpRoKn_06ZPQ4lUadZAEoGICAwXzT5wiKQYSR1Hd722bvf06Sp-Z4oM3vHsh0j-S8Hq15Q1wcpfPjVzadB-qvFpsiUx-FkyDPhHoiDicBpNEfblbyC-9kr3sJS6cWr7xRVH1k5gaDRpjyDmV99VB2eUBtlYCH3u62su2yMcWvZXL-S5Bz3r_OBMkypwjYUX_xUE8Bo3GtFM1oDs7Ggyey-jxYRj3OesDYY9M-4MsvlomE3jNNa_1hMDrtaTyTBTUpI9LvOcqZxPJrkF2Q8Dg6oxNxWMRQKXGJ67DnCWssWmJW0XOsD2X8Nen1QLBJqPDvi3AobCYehIBIgw7-rvwF0n0pgj5hK9ZIBiqRDFXUDnCJjRIFMlACjthfM9Bl2StceJnh1F5dG8m7F1q6LqQLbKhQxusD4c-HAelUWKxyEIq4oud8vDC_-q5HEmWaNJ5_vsKphPKVdjfaHs30y3yimlaNQvX4a0zemj2JCen5oT5uZwOA4rdbNSdFaHwKelrsSAMW3npIyuC6D0cgHykxrUiU4Irs6EyrAjLCGuLZCYmbW-4Ke7YbXQai_Pi5j8bvOdkT-I0TBayM8xpe5UpeZodBtZVpntPlltoNGSjXoqbJIv_YMw19a6_INPAwkXWXkWyckmfjyCMhZ2rbQhc3lJtMyWB_vM2A9W9-Tf6RBN25vmGb8YSd31trDGih1aAwd0w2cHD0NFuUThYRPcoz1LvmLM_Isw7zrXuGuGEMqJxlPiYIW6Z2uepZa_ocXfBBgnCY8rSag29CREFH8UDOcf2jbx8MnDYitfrRgPFPp3gRYEvzHuIvKirYW5zOk4Tc_E-T94rBT0Jo1E7at6BNSIkMFJL1c5B612ixjYtwjmXcCrkRI9tyRR1kNIIGih9wap_kaDmmKokeKlk_heART92b7Jxfre_EtHcKRGQfyFClCYwAtxd8SqAu_smIBPucjFy6E7kNdY48gO86QkobFFUeSc5FbTjXCu0WaTplhYqDNjHuTcnYs1WL1xYfIZAX9qFosMGyVu-56srdf8DL2wLPBC4V896gVsOCAuY6cGOBSS96yQ-RuU2fyLTYZZpIYTSY6n-56gYDUF-IlJ5w1WWWsiUVdanvkRxmDIowbVx4n7LEoz48Y8G8Ce8EjzTRpTh0cvikJ3kPGhm7oDBg0KpNJCJNT0Qy33Z_Lphi44Ly69sEfGJqXlfJXzxO2QbBUkUtoODoLx_7abJWjU1ErYchCSvA5EcIAonz_6jyI1YA-nyOajkGNptQuo3Amg3_3Pqu1mBY0DOjtWCJWBzXyqZIT2kD1BEhzBimjKBijCPZC_HNStA0zI92VQ-iLQBR6w_gWdb_5rNanCp0K6zp9tblJegfJDlJACNQao2ciLxeU5JKhHLZZ5Aed-OGG645kSeZz9EGygUpBE3pygrJbRN8tkCZB90zv886CIgiImc8AhGnF238bBTIFLTHd1cWcvKV1qRfMYYLuv_NPvX9hXb34r-aP476b_1aFX5yyK_QI0HrrE8BWbUIB0UYs-sa5Hw08q6FGqg5Lct7Xneu5fJ3lQpj2x1UkJERS7lKl7ZbqPRnfe7dE7kNp6nYlflHZK74VS5s-ZMS6K4DC9lwARdwXnM4REzfQ3Lb-eb7DyobLv3-05YRACas2gi7uEfA-C-alNq-CiEhrZVsM49NgJ19me691x3BDlv7nZLkyoo2cTdwSmE4TSF5ocLA-KbGBARMT0m_zjtyAVBYJePGcg7f4wpfT0e3J-22sF7-OfhC4xvytu1Fkz-ZwJhZetZtchDNixqA6sar07F6in_BdDWTbid-xBfawzNpcRUonWR7iduiAMALuZP0GqZmGYg_MCJrnuvTT4LPByf94BN3shCgWQakvkvj3f4Mn4Dq9Ml5lckCXl4PFD_NEUFqS_pCyW2oDYIG4uQbKuVYSODN8W4vPmpDD61jZ7Cruf7BYcjbcJ-YJLZbNsVwSGxhSKOae3sWDOWktVBkwgZmlGfNl160E3FBM4gZC6fZ4cgRM3XrEcSwhD1NxZ68IXwUovTLyJJrx8-3UmBoKKtauv4xm42MKh1YL_A_5-GGouBIHJWxQ4kpJOah_ZEhIqvDGXO2sM-BO46yRFpLEB42QJp8SvW7L3aCLb7aQyza7_mh28fss5Fky7-BmAJ6Fz2rJ2sBKCB0j5K8I_ieEfsychtCYaHVc7OstN4DHvp9mx4aPs-DSV5tm4yIFzTfzjJeCPNa1zEU9nkxjlIUxarlRwaYf6_Dxjk84o5irmghzYEbGYhNbN79hNbyTITdjTvrp8Nx3HD3LEysdhXyRNdvDsqNQuFnv52AagVS5uFDSdV5l673VnycdiqamVYdRB4435pTsFelqqDvyv5R0BN8-fuhilO-979q7UGfaeq2kLWcQdLQcc4610ydGtB3WhAMS3lDB4liunTD-jV6FxP9wzQ4y6A=='

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
            st.write(f"#### Total Score: {Q_total} (Low level of loneliness)")
            Q_response = "Low level of loneliness."
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
            st.write(f"#### Puntos Totales: {Q_total} (Bajo nivel de soledad)")
            Q_response = "Bajo nivel de soledad."
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
        QUERY_ENCRYPTED = b'gAAAAABpblOd7Ia0Ega9SRFEq4_UC3RhaRQMuBRRwSBIWiQLQ4T0NSrLOAzkW0uyp7bFQe1pSycReELS0DAxQsAQE7nyzhRvtLa143CGNcvXNU2p8bPLWKt3L4u6j0UMDjOerbR9VX1jluRm9p4J-SRaOZp0L-m9sMRs_rNGoePSvg6sWOcYCSwudYKMHha711r6IrLL67f-gxJw1oRUyu3LExYEkYBgmP9KSNF29MDg-5YanMrCQuyLPdM6gAkMVgginGws7tkvibP2i0RExs0wazUwkR4NH8GD2TIIl8YFg2pRfXeS-oP2DnRt88XTPWWHpghJIzHBi-PtaB9ktyIs-Rnowg7LmnNufHPM1lekMd-j69NoQLXbod8fqZwkA0UbtDGPIl_ImtKmI07Kjp1d-2XDef5GH5HeTZmEtJ9JbwMXPVQrf4TKNqxTTTq0Gsm2JOEFWUltQy1Sp8x84dGw1Icmpu4LYkxUTiuw3ybqFVogM_5MyeFTNicS7Xqvr4esRmk50deRN488sDgPuka00bRY2TEfoCfoJhDNg3HkSPlVBH9fdWEEPysyo7k6odAgynvU0PZQnyNUhbU4bdhOlEawcWAL_ASpg6DRFqJle47f-97wWm9cw0Rkl8L-2Tok6qSW-0vZa0pISEUAwHUG5wPYfRv7K4GgvGniVySq1M8d-aU_LHybMft3JBXC5hNX6r8DnLuTQ-2VMeZmLBimAJrCNe6AA7iA8985J1OSXWA79cxM-BcBgRuK8skIGGhjvTjfaeNA3IBLnb8uG3K3syXLp-huXLiHCvmg9TURF9fpKsoUJec_JDk2upWq-iz-RMcFMxm5ZfjJvrKv5DtW0wijFdVJ-ZnAwuODepcOBNXDi3AfBeWGZPqHfTZs0Z4Jp3CKTPQ9r-rIjt0W7F_hj5RsABf7E_Kib_COMD0T93lowxv04LEGOXoGASxxxMhLdGgfsiDzIuoLYRbW4XsZsLhGfZQcmPbbH_VhEIB66OGFvK_LwYZDcIidgIwWrEAn5arJoJpRujw5hylSqPiGRqscpN5o7SNu2hcct91InMIubP_tcLRIQMIEj7hTiPq_kOIcexDW-3yKvnLqXMjYS2CyxN1mBKWmyFn76FMoWpPivlGfV9XqzNd__5EQIqT_Rzl7oB02te5SgR7QWhLZ6AiifKO5hGmIKVZV69KWFOBjyOlLIfnz7BB-pVow37R2LQvjv8jVkF39oBkvVBlOY1QzIf-_iadUeYdh081tABhZP2oYzqpUra957aBve6RMkxJKQ0Iz_nhEmiGh8xD7-KezTti8jg6v8I9v4QjLQp5bfbSkTyQLPCngZkXXi5-tVeWZTciYFhz9w283iaWWH-ycd5Vk2YQbkF8cxJTNTqE9euxYd-7TiQX3bpppt7KAmf_wvmkCB9afnRMuyTarl9pUmM41Az9m04oGFHvy9fIuPWQM3D9sR9i-q1qH_wg33nve82cVRGEWL10dygi3pIRFlsZrMuu7jPLiAxKwTaoRJdmM7h9vg9iklLKbuzGCLwRVGLXsEBxqfoAxFEnfb76JbXa8gOWrLwKOPFe-a9r8wwYjnRsxCAV9g2_A7x9VgVwEbmMk'
        key = st.secrets['INSTRUCTION_KEY'].encode()
        f = Fernet(key)
        QUERY = f.decrypt(QUERY_ENCRYPTED).decode()
        # Setup output columns to display results.
        # answer_col, sources_col = st.columns(2)
        # Create new client for this submission.
        client2 = OpenAI(api_key=openai_api_key)
        # Query the aitam library vector store and include internet
        # serach results.
        with st.spinner('Searching...'):
            response2 = client2.responses.create(
                instructions = INSTRUCTION,
                input = QUERY,
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

        # if language == "English":
        #     st.markdown("#### Sources")
        # elif language == "Spanish":
        #     st.markdown("#### Fuentes")
            
        # Extract annotations from the response, and print source files.
        # try:
        #     annotations = response2.output[1].content[0].annotations
        #     retrieved_files = set([response2.filename for response2 in annotations])
        #     file_list_str = ", ".join(retrieved_files)
        #     if language == "English":
        #         st.markdown(f"**File(s):** {file_list_str}")
        #     elif language == "Spanish":
        #         st.markdown(f"**Archivo(s):** {file_list_str}")
        # except (AttributeError, IndexError):
        #     if language == "English":
        #         st.markdown("**File(s): n/a**")
        #     elif language == "Spanish":
        #         st.markdown("**Archivo(s): n/a**")

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
