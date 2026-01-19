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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpblaGsC_cuqUj1lupXpWKaYx4BidlmekKC1IGbtedHt7NHW_S2gFR2BpjAQEYQOMriftrC0TjeECwhkuOqxOaxmh5BDB-Fwe9T7gsns_vUxqcNqjLlskOL8nJTDPzKu69Vr2iKEnq0I-r6-lwAfgQTNyi26r4aWLy92WXfGq7uB2_EebLQF6rIk2vD_v43vNJBso-cAi8358PoTo-0_-UmTXNGK2hJBdMuDhE9AumZX55A6ANTwY84jZDskerQoAzUp2tspuArAfL1CWGpfN093w3oUY4iavvIw-M3l9wwN85G_DFU5QzxTW_dgfBzqT3HfHbDtqbAU4R2bhWO6eXduQglalvt6AiEoAKTTYSssMo-DGwEb51ImVUHR5ntkin-lS6OROgFbjUI0Vy3Qd3YM5s_rOdSUe4hJzsOKq3taQQFB6GjtshcBsTFSSevrnPeLO41Se0YBMDpWsn-wiw-V8CeYtF41vSG4KvUkolniU9DRvOmANX-CCH1wjysp6hr2T842srPIFeQ8mIU9EPwkcRrZlgPRtCjDCdo8TOxtz8P5ndnOva0Lha6t1mjzBzYOvito4jWROk5RX3bAWVG8l82BCh5SBbDguLXsJBvAkjiOMRHaRMeOUmeYo-j6szq1xB0ugEVxP8HSc19j-rT-Znc8vhJe1MnJlwJ60VEJZTNhsBQsl7uqeXctnC_yjnP7-gbD1pStaBNM8-DHDqI3mFsypmKexVdewgwJrurAgPrRYylDjOeKPCcBPXCpa_q67SWy_0RtghEBWroHUN6YZMzSjBY41JaL_yP9t2C7NB8PxnLBE9o_uqlwS3ENr7GtWW5gjGN3SoZmP0PR_TqGVYl7PU4PxEmtQJQLPqkMe_nyoq5Lxg-wa6tbhRKTmsyp-eUlFdvYhFpvulqB8KldU6yX7Hp31uDnzHBUMGqBs4Kd9PcBtP29lD-L03dqnrheb_W4FBdvF5uSJfuGEiRjaGXC5kUlQ6-_tiOUfaVMA6_udn6NpJL0zllwJ2B48LwvsacbVXLhN5jRAOC7SzS54cFtw2Ek-RDA3TWH6YWRI5LaC-Ri-On6wtv1KZAgTdIC1zAkrVXcKX7rRauE1iplKYjWfYaF1IQUyUfMCcoLnx9RHloqGncqc288sQqR0dwHfYGiEfeEpDo9L6NzMzbfYmnk0DthDTc7XPplsNQQugwjOH7pkPnidlFhUOS61ZfkNI9UPjPMNbOtxl1h-vWtDDUunSG3tnrj3AmKwvRQx_xuEBNd21B8EigJ5PW2o08pEvG5r-Zvf-cvRa6PL17Fmm9yEVH1VdSG7sDWqDJUhdVszCFWvC-ofjOc58sXnEDxQPJ61REKZ-IVxy5s80rDKeCH9gTCK9KraSMo9cI91yfeOFKm9gZYcll9Jxl75hh4yxsZKq8RDhcI1hMxZFKu7_O672hnY4XtGo5qDvXQlc2lbjMKGhMZ5C02avHNM-T3tyTdLgi138MTuotrRdOSSQH2VhAp8UzgPCK-EO_0QQ7pcYjdfaIuUW_eRNjwHOZqJLV6YeshMy_6oaazejN25ODC1MhgsbbCpOm0uPlAWVjTPx-WX9ppLksOTz0bLQdcuacWUAUq-emi-NR_5VsriukqrVF8Z7BySWERbMIH6yC-ZVPwHEmlHIn52zbo2rgrIZfWmXUGHr7LQnDUencqVzz7pkHDjRp57IymKFlMC5cleQn52VKHcXWdOoxFCmRqwE7yKCXgwFPTc3hwj0hnUiXMPiQawTWmg837RzHWmeZlM5HKsoG2Ps8uvHkCGTyvC8qcj1vIHHlJFcvRWzQa1OiDMSkBXUju_DYG6ixH6_peIBA51PXu_80NCe25G3hiKb81X7_FLE15F06BWEFwUdcPAIU505sYDMBbuAooEumcSjsBeWI__vfDrPG99LoxeyEhUiNiyFfdND9dMs4ohKRZF_XpZL5sDjcV8oRcmSltPgce89ZMhshdP3T1F4HHFxbe-UU7kGVY_C4L7QxnpAANXM6tT5xIo9d-ituYZTMgKPOmLIKWxGFMltGF3NUSdIPDRUdiwr_OZGVs2Vjq8AImVtVaQlt-x0-M8EVB_nRcZTa7RhmKRQayzGbvQd8QMSMNMi4-kuH11FeP79gEdO36xXC_mlmrHK6ZllCPk0xU7ZLPAqz9Mvt7n8RM5z2MmUGZqPQxhVYYV5eVqYgBVsbnhatoI2iYlbaqqiaYbTk72koeOQzi6EAeGfmzeJ_EM5lycKHMHUDfF6rWUYaQEWIPxYJ5G7f7lH3EA03Hqym0upB5dWSh1PCS2IOHANg5yue9hRn21-v3rZo8F6nK5XK-waoHP580UGxdMcrcUMLEqW9qXQkIEoS72N5PBuprDDh5DRRsZIeOT8T8ah2lvmOFWY0STli6YmSUzgTDuVBS23KZ8DOlEhyG9EV6tVvvoBLBAhImwBkjxb0BMgfvhM0mK7B_08wD-iZUQ93ZG84NgPEvfzCn9GSwaUSKbLBiqxHjH7XDEMrmsOqOQXi2urWdTAUrOhmm53fYlguko_I29Cst3fMZ4kBi_ZyciUvFgeVP9cNLjVBeQP26gvSz7ujBUXmnL08iv8-C_3mQktU1Cmz8iDsXAUXOEQ8AFymzxyJPF_49f0EEzdxym9CENnZ30TSJgJCJTX2w35OYtWVie1ZqD7DZ3V6slXL4_5z84YZeW2GJr3I7BcF2nNMsjfJQ7fOiQHjaaAOXN1NTr19WMPnm61kRkZIibpbOxC0HB2vq3nMODSsC5UQPr1r-kzsaRoTT751_KcqR1ybTGunDva1LxIXdIkJqMcv8BCJwHynW2FCfYFggwWTXYSGfgAHIynX8CsQfVHRyd-0TaX-suu1lE-7WfEra_t11gKq9Q4rgXuA_m7vWtLwAJW_UXQ-0EnhF6w-sNgBjoOX4AoZmOoxOxZCOnvsoZKv0q930mv2K9m2mvF_M2UjOIU-HVOfmFUhfxF0LJ2DLZTxxPHPVA7J3HmgVLOQP6IKCMy29DSxYfOehavMrpEiJAMYA5bky64keqpZuWr5yJCuHoC8l6fEUQqp3y4Ud8TwaXSrAcfOTOr_xbKthzrJ8hYGx4lu7KP_7tZuCR1a2B3_FIDu1uXvsNz59v7gHtTEruUTlVkRPBK3ltXJvkLH8t_wTlj_4OgmdwJQhc76VinS_N5GMhgnGUVjYRQibrXSevaKCFCFh_2M6CeIvt6Rqb2CqG-vAKMxhaFLoX38RaErQVVRNfh8V51VVyxtb5J-2_oayBE7WwAB32NPfaxTBE8LaNgqa6c46qFNOTDvIYBsoQoD2dlH2TF2ZGADrBNGbXlfSLMvKEYtVLYB55PSh8U3eKkt2nxlYy8CS2EieffneBuY2r1q6AOHRWVuGKubL1ecuuK0sS8A7mRED2vB0XUzte7qroRgxWV-q7kMYXjZ1lQU3Aq93qvkUWZlo3KJ9yyB16WwPydKlD3N1jQmXyiffCqc2IqWEgdko73BDCEB1RzFE1pdvWU3xlHOiGPxYxZt3k_xX1FGnauAleXKt1hqnQxhCGf7CWguQbAvmeKLw67Cs_tDtUrJPYzC3kuJs9ZMBUptxpvkOqLi2sT8Qw4pKDshQf74jr47HPIjA6e1O3_2KclTuIX0C66W2ZjoSAHzP6z17hGwPDKtjcEtX1y5-PMFPEa7Yip2VJFM1_L80Cwks5Ut6Mor0-FVDXwlZS9MKs2_4DQ-T2qBoIs3oaan_rWPKjYei2_UpkWZk-5nZje9j6ifM-xvgRofpQUV7FEefn4mY8_M109ryVZzFRV31wENlmhpozFTXHLpHLlH8vrebFe0feTqKG5TCdEmijgeyn9S4KOlC2XxAnUzCRh-7AHPxk5d-mcUPefQily6mCYvdbQEuQW6NGnHw2Hubvb4rQ66TQdsdmB2QTq2bq5b5q-g1FQJpQezJagS9zG1nh3pWTRmeHU_dZcNAwhQh5Ax0Yf3pVXoIn8vJS05eX8g1l33toQBckx1rKqMgOIkxCOYEPtGt05JkkKFvpXGQfSFWgx9BRm05MJhCP8gfT4eakk27Yqa2GFf14VkbtZiRML_XwuCbugP82S9D8BvOwaEneoqkfOVVNAJ-UBX2ikJACl9SerPsyOUYawpwqscfehDjgCVxw06tb67j0VnSabnqXuK1DBm-ZT8I0kNm-lESNpwcLbrhrBF2TiZgXj2rANUaEZ9IccnyXqCotN4XyVNAXi_nOylkdOXxJyw0w56x9bBUWQuu68RBFGR1XQQxkf6MpKdUv4l5FEp-sISZuyMgew6_xRz0xZSCXhUXtBr1I80ZsMZDAQOEtHGpKrazAwTIhvc2SdjXaw4IV2ufpw9PZWxYauS19HvHw-d-mEK_28yAb8Hb6QwtEl3TWvntg03YSQxWTyJegrm5Wh8sbg4WP8by-VZ4W_TekrKjRXLHY_82FRWSK0NY-tDtOGmUec9-OPJbvPkwUJKTaGZZ1oRf0sLLR7_soCJG0zSRaNJ9hHje2fZWjT5f4UdMT7neH8fEiiBoWAo1ws6w_TXOuSbu-ZtXfGhLdIiVyDAaEIZPZxK8NbMhWR52rPjQlc66wP6-RHcVHn3aTQX8MaxeKazZcgLFQPa37Er4gVlgKAD49ZXw=='

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
        QUERY_ENCRYPTED = b'gAAAAABpblcrW_BYKpkCPMeyzerazE3KKCECLcL0XlTJ9x482W-kFLjYE5d4BAvSE0E-PSzrDUMZ8BETrk9ezxHVxvWA7TZJDsJFqne-mxz_KmfklPMVONA929JER06_7Uw_TYrtDyMb9s6873mqWr9WuwzeqzSHtQjExxMKHB78eAZsDuKyj3Gxyx9YT5NeGm_FBbDMF1EkmyPwl1Vit1C6tSZVKqYSLBYVw9PU5EadAOU6ns-9-uDH3Q7v1jew0uPjubD5L3B0kWINucx3pHqq6OYCceAEyt9re_chbWv2jx7bOaCLSP6UHeD1Ydt95T4U2Kf8mXF40Yvq2GFAvuKqCjUE8ycj-XZB_F3enw4Xos1gva9iyoh4kEzJVIcNaslddAJ4i4-rnCQW6ztc-sTERnQQlegvNIXIKJAzWQACrUOXMjrZZtslIZL4whVa1p2RCSJUgs-obU89Hy2AjvNHxxYRahoyhbfbSNbudNtmInUy4C2CbRtVp39M6eDzRjYrSgz664lu7EypJyh84FEtsdAo87bIZmKgtoe-sHqER52P3y7oy8gFa6fHzP0eR2HdVkueO29cMozCjP5DGvkx11uBeqZYaHxJmtxOO_Gt4Y3eq5kE0l1c_e32YEcIFomc4NbJuR65hHprItHPohbfkSQb5yASqCaUwmIxWWsFcFKc-8_LleCnHJijXOskRISbXheW7QFWvde0QBK32_-goLuDnGxDYcUqElJ4XpvJDvXn4aWXxvvbYXxEj8liaEZfMhfcgDysbUSAe99qOjZ0X07e_8G4IIkc8TXvzC4Kzg6k0MI8YDRMbxzAwn-PyUrrpCad8k3Ov5NKbTOBybnGO9tF4dw8Px7eP5pGxs_fYVh4T5W4eJfPZ0ihtqfjG_tHzEs5RaXqX-jOokgedQN4-lwhfoCVcOaGy18eyw9w61b6prNBFQ6Mh_gyqlyOwiB1dv4PqzUjYngAbb3i9LyTZCl6zSluD6YmGMwUl_FA0CC7TnZi9KGYqKHjKoXFCD8kSrItbDaCsXeWpIQhZr0d74vB6ijZZ4Vee2PDnhOenmIdj4fmbnnlhjbROK9UohoUHVtxVeD46QVsfwW9Ss1aUkfQ_0__PHkjPrYe9Qd46yzhCUV7LupPiesz7mJCllk37nq5MqLLRMcZ2lby6i8Y9kd_lt71H6B3a16DdML7n0Fhe0e60zswOZfhGZ94NIKzoHq1iZz_Gtyo4cvU7an7d6L2_9AcWj5RsGQwP-7gh3mr73B8TWTf8VyewV1tll__MQ2-KkAkGnGNyaVIxPdORbilx-lA0ERlIyXnhaThcgYR2FmNGGOlR3ytJ29b1DVvoFLAvaovoASSil3d0_BdzwGMFVQOWwPge_P-oZptGXZFGN5JDQA1uj4JWy68sDQK8oLb6o3kHHV1aAnA_2rx9Syl51aXXYytGI5eAbFV-gFEBEwuF1D0rRhgVzUWxWbo6Ebk1LCiEbNOSNU1W5kviBdDnBSHoQ4j6pSrOPwuZ0YnVRhsHdTvV3ye79OcxVYa1of-KTqUW5yXUb15a7CA3p9VmBMAdLSwGDxfi1NiKc5sM_V9KZrDQ7A2mRkbRq0HXgCTLfX_'
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
