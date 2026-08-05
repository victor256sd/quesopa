#-------------------------------------------------------------------
# Copyright (c) 2026 victor256sd
# All rights reserved.
#
# CHANGELOG:
#
# 08.04.2026: Fixed Questions about yourself and others (loneliness)
# tool, where form wasn't showing on selection.
#
# 07.26.2026: Cleaned up the commenting. Adjusted language on FINE
# Q14.
#
# 06.16.2026: Added POC to questionnaires.
#
# 06.15.2026: Changed named of Questions About People You Know to
# Questions About Yourself and Others.
#
# 04.24.2026: Corrected NEIL Adult description, switched with DDCL.
#
# 03.29.2026: Added DDCL and Prong 2 Competency questionnaires after
# discussing with Glenn at Panera.
#
# 02.28.2026: Updates with Glenn at Starbucks.
#
# 02.15.2026: Started programming Future Inferred Narration of 
# Events (FINE) tool based on meeting with Glenn and materials 
# provided on 2/13/2026.
#
# 02.13.2026, 2/14/2026: Modified NEIL child version description, 
# added two questions at the end, and adjusted language on multiple 
# question numbers (Glenn email, 2/12/2026). Added NEIL adult 
# version (Glenn email, 2/12/2026).
#
# 01/26/2026: Modified page to accommodate the loneliness and NEIL
# child version surveys.
#
# 01.21.2026: Modifications to survey, question wording and adding
# two questions, verbiage for prompts changed, interpretation of
# scores changed (Glenn email, 1/21/2026).
#
# 01.19.2026: Changed Medium interpretation to Low, point AI to 
# consider specific questions and answers on the assessment. Modi-
# fied the query prompt. Resources are 
#
# 01.18.2026: Changed age range from 10 to 99, adjusted questions 
# to short form of 10 questions (GL provided) and included Spanish 
# option (GL provided), changed verbiage from Often to Always.
#
# 01.17.2026: Initial development.
#-------------------------------------------------------------------

#-------------------------------------------------------------------
# Correlation of Tools to form Submit #s:
#
# Submit1 - Questions About Yourself and Others
# Submit1 - Questions About Yourself and Others, in Spanish
# Submit2 - My Feelings and Needs, NEIL Child Version
# Submit2 - My Feelings and Needs, NEIL Child Version, in Spanish
# Submit3 - My Feelings and Needs, NEIL Adult Version
# Submit5 - Daily Digital Connected Life, DDCL
# Submit4 - Future Inferred Narration of Events, FINE
# Submit6 - Competency to Stand Trial
# Submit7 - Perceptions of Concern, POC
# Submit7 - Perceptions of Concern, POC, in Spanish
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
    VECTOR_STORE_ID2 = st.secrets["VECTOR_STORE_ID2"]
    INSTRUCTION_ENCRYPTED = b'gAAAAABpeDtGCB8EbbnDDzlWIzayPCcwJoxujN9dg-_2QxxlCfu5oeBrXaGoUHOCfOb_OL_U57vHhtHtjsPIoYPjn2TN5WQ0v_NRbF8r4UbsyMMoG_Hl-xaFzjLsT00SAxCA0KL1KMPOpxevnRoUGnHlZ48n0lrDf-1Wccfc7zXPVga_2bOS2J3BefcXM8u7mwbNUbdXJ69eIRAfTybBA57D0mGxodGp_uSR1EYHRVB8K3HjV1BD3FY0F6NKdbgOAd2zhpXD8BwCQBnz4ZQQMIkYgqdlvWwDgh0wNwKSUTMs-7A8I-vurKLvF12AwpBN6KRDZcBBGf49kwKExQa8N7Dnt6xR0XUUJ5Wq_vR0vZaf5jbEI1_E0-At4vrraqbIYHDhQP7xAnjUruhwmRwWN52cY-c8u7Rp8a8XXjciOEngxK2dhrd9KiU89dfShPko8qXVu2Url9UARuWz85YgLH6WChOIFo7DRtfabhiYv7_K36RykMbXITgqLV4AQvfOub1DiBE8lEVp83WqiqKrBVm2_DdDzzQXpuvJ0PizEAH5QAPYOWXqawZBLAqRG90s9PeCqR4ll9rWESPuRb66jWDmTzrzBZy1lWxL78TnW3KlPhOxxtCikc_suUy5DnSdiT_mR7WaQLqlgbwtfub5gMnfO3Ox7HlRF5WCDkJueCx0pj9UrwymGWpucmJk5-_hbCY_ZN0PSPp0lestHyjleSoVgfY23zbZe-VSrENrOcwmBl2no85OPVBshO_7TzfKQ0VUaQqNZyObHjuF_u_ShpVHMX8qF8PiebQBRzxNDkXfXPOoC-eagdSzuyOmLurzSj8C2RibnVPelA9K0hkggohzrgWTgNhA9BDf55P-VPMkT3vnGj6umP0udeWyi_VzcFXHhI7_tgMJtOvycPQv61Hy7GcYu0KWikirerfX9utS1CqonZEn8fqZYfTLTrCm8-5JJPZ1vbp19CpzNi4kNWMuq7ukc4b-L-f_W9yPOV5zY3fU78WWLrxJFN4kaJf1NOk-NFLNWpj8Ia7fvX54lt94oU5DnyzUKXORukwMmKf8SkirawLIzYwepi5mZEFP17IB4iUZdz8nhTbIpgETIoMMga_zGKFdd74541UkUxJ3APgA6AwoJ7rm5RM52lo-7_Hnx656J1rEAQYxmc4OtiTX90hno2gWz3lNO7zXommSf4J2zIJuCEorYI6X2xkF-Pj52fdepz8ExHQEh6CMCyq08cWNQy7Il_5MDsTJSUhxCgukJ0twNN5tW39rry25a5w7Ky2uVJsb1xxF20d4S6BDFT9fL38hudlg9OOWhmJx6ukFGLGywLXdRgsCSNxILuIAyTO8wlNNnh_-AWX-niApUcZ7b8mZQCgHt7vf1k0DZ_ZkgxcqjxjBXLUabKzIB2zadsa_geyEB84M9kFig-j5d_4pCcMWYO-l5rI1d0ydNBNt-PqSNUPX85v2oLb8wvOEqPMfL2Z_H0mmEDp_aQ3AftfE0O-4S9F5ZsjDlJON2lTee2_Oj6sQQHrSqXmb_I-lm7TC1Kr0oEv4dDT8jjrnv8BApjkUVjsPBTpQbONHAPeqF4CA_9h7K79PKoCqXXtAtenHh2Sf0yyfoTkNfWiKdBojTNBdulUlTzEDrI7Tz7Dox3fyBmXX82NZekov1hgMLHgSYTIx2iejdo3r3pHNVI94L0PUcArWoq8oWEWr4HRkhip4jcXVygNDY_7Jen9zB0xa47F0K80VLpbJKTLwF-xvSaSe3bes_aKK-DdY0UvqFxZunXeRfiNJ16_wbTYk2S1edl_8ciJ26AgAO6t-AP8aBBNj7R97f5gztiJG21b-C7z6K4-RoB8wZ0cWH4tCvR8W1VYob1NSsogjqPBvGuLYMtcLaID2UOY4au5dqCSuxSKPXQbKXhJCvtCJNy_Am6L4dRHllyEnzAbcON7-JiQjB63OnrwmWeFldvnN0fidrT0u5JDiAgSRHMWJC65n3CDd7D3OXRMaTxrrNLZ2cVSNXlF_6CjKpJbDnx--a4JxikD_qfOI-cOL2p4NnVLehA6GRQ8T890FH4CfCVZpK49IQSbxJ9dhkkyNKOlPRG5-QZ0vNf_MI4ARd2nGWju8bwYcK0rDIX6ZNKmHZNulxdy6yJqYvmOn_c7C3cl6K5345fG7EX77ucZ_d9_HqfnRxnMIRS_wqJQ3uv6uA9-ILkEPE4jlUnoXg8bFcdfmHJsmJa92PbhHXJsg53n_q_lmG17hnyF-y-xjYXwj6BOdRofxGbUruUimO6V8QQGwl4T8wA5AsVqj9IAlJNHLEfH2Xs-hb58XMfiAd7JT6pJJYCCerwnMfCbBnYilmUvkwPFkmIIBjQVYkWgKOmPTCYMRyDSpI1cp7WoTen-FcHO81fwUbPK00eRSf_jSB2qCk9fZ5J_UD8ArMTQDRhNyQOw-4V7FslhIZ9i4ThoGJ4vYkmcwrn_beKvKSttZej37J0AsIHos52NVYtw7mtiQVOCoNX99oGNmpFDxLSN57AxB1apD9XKbmbtrgBaqgQoZJ3ChNmWFC57xqG7YN0UmvUzOZs5PJifxPqs7KMOgqmW7xFBImRT5aAXgucwDmAbtOm09d3PnhT4V8kQ5v1Vaj04NwqHOWMBU_YWbN6yAHDwP0X__A7IPp-vbpeaqcFKwf7MVk0abCuyFdZInTL5rZ29F-ivWVxa6tJCdVxPVAELB5-_ilq9L9SsLfKKQsCMT8NURuWlo0isH4_KqTDMO_S82OYW1NAj__H_GxhsKxmveR3EI3pU9WMK-nwzjGRJVrk_ry8dU6nTwyJjv5ctEbUR3BR_n4LMDWLnAfzTVEZZUCsWhjxcilgN9sHJ7TCFr27-oXhCkzFz9R1aNNHgCbq_0I-w4doYJVpGI_9LWAOj-A7wEAGTBetii1oxbsgBMTxj7cYOd2oGRL7trBnaGllL15q84IX_yd7_2hKKd_DlUnbdg18WEMfdl_LVJ8WFalaRuQij2utdULVAP8CBHBINKcx4BQMlJE3I4pq2DJDSCbcjrgZedYP_-I3rvscWSUQWqvyv5Wjf1ZjFkF5YGjWqQ-9f378xPTrB5wzd4ef2D5QG9VfcNkv1dSVJdOqd-UN3Fvny-oF2mfMnnFrOMWAxXcHhURhj5FmuX49_AW6lyQdBWiWo9aJWV4c2juHAdg88hYHTNXNfLgdTxcIOixG-u0ONiBEbHWJES_zMFkffOG3VOeP9IXr4LHaFOMWq8g1S8zcPBGHAZb-Oi1stw0Gm1PaE7xQxdwsqkTCsj-N0Ie5DvgfzIFyWaPA6plIIb5xzrGvIbiVvbJOeuORLO9RNLMHW1JVVJarBkGUytIWFj1OlOFFOFBDvyU3M-N3WU1_svYlEr5ZdWzOQkL6PATCL7fceEOeZVYxd5SkE93CHnRxQdf9R1y7CT_jLA0gvy_k9jOYp095RB65iOLzc_DYTPMUX0hvyJbCfd7EMS_BnmqN9aFf6dMmcd5LAyu6KXzswyai8YzXYI-9W4RyKHjMq7zqAEpqIuwIlHuUFBPiyssScLk2MITeQuV9P55I6jjpFXrW5LgaB4zFeSWB3GpDAuSUBfM4M18QtSkQVY9T-pNF2iZqLabpXwNw-DPVuNUsq6wfTcfPqK1YE-O27COMOP-6S57bQI-6hxXXLVMOqa9fzJ2vtL_br-s_SsN0thEZttyhurDqSdgsT7Zod39xEJ8QONyR9Ji-tkgaESIcGzwMy8E8AdlsRnN9BczGDriO5WwCJVdcCLbjGzzSArCFDPb-8rjwbw_Bv0ziZ8dqM68csdrLiOzmgJQn5c--Y3ufaTWE1qfwA6mEvezzmiYO0kDZZN9a5DpdZj6q3mf-Lohf2OnP5apU-7Dy6hQFaz18U2c2iGK8dxHEcRzRcyFCkHr99Gqp8UWQq69oxOb4RvvWg7XwN48UjpC_DuHKIhfJCvUzgvU2yJ9zVNCIkzvL-q0sqGt-SxHNPzX0ZoHeAQdh77StCU-s1Z-xkyUBESTlHQ-qbN64u7CpJRBcAIt7qoCkKm3n5xSh7K7KaYtDK5suhYs1PD2zvGQt3JKW97wi8q42uGqwDVxkOZBDZer-SEOphJ1QAYI-Tmo0yzIpDdEn03H3ooPz_0fTEthJS5EI-tfIy_d5DzlMO_nbf8nuy-a5-dTpkcIz6DPuz8SBV2W5VII5axWIGZGCEJe4CqC0cIF_XUiL4YHvF5J-GMn_DQr0xMj6dai3LFX2YowifWEmkCzLSrBd-ktefyNXkLvBoFrOSNNDvRm3dPS-Uh-DbW7BbHKMeUImCfzDTcCaeRMTq6pSED96JQil3hijkbyqnHtuK7kpsg5O71y04RwxVCHlTopxIloHc-B4fN568fCqvi0eTt0ZfHzWDgshxOnGNaBNMPEcVAkRYAj-8IeztPTc34jEaUuTFbRvcmcwdAV9Rp5GVsaGQOfUkeavsTQU-2cNZORE2okU4P4CYOIQ8eTOhS02pByuvE41n5lcQSr49Z-80CpqyGme22qZMRkB5qbuy9pv5vf3QwtVHlvJu1OKZgAxcX-WrK5ECHG5XoIxo-IUHsUglC2RSiCNSdYeDqDkNIWcCgMriIVtKH-qAY31v-_XUkeBP7jvFQBr74vgBnNk4xEdLk2QuHV-USb6kWqX_G6N1ED3kbsN45Pzl_ziJ9j0PL_sJQGr1ZkadydnPvOJH5aA=='

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()

    # Set page layout and title.
    st.set_page_config(page_title="Qué Sopa AI", page_icon=":hibiscus:", layout="wide")
    st.header(":hibiscus: Qué Sopa AI")
    st.markdown("###### A Starting Point for Understanding Loneliness, Belonging, and Future Outlook")
    # st.markdown("###### Your starting point for educator ethics")
    st.markdown("*This platform brings together a suite of science‑informed self‑report tools designed to help you understand your emotions, social connections, and future outlook. Each questionnaire is supported by advanced AI to provide personalized, easy‑to‑understand insights, without diagnosing or replacing professional care. Whether exploring social connection, emotional needs, or future scenarios, users receive thoughtful reflections grounded in their own experiences. These tools are designed to assist you in connecting with others, fostering conversations, and seeking resources if you need them.*")
    
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
    age = row1[0].slider("Age", 7, 99)
    language = row1[1].selectbox("Language",["English", "Spanish"])

    #===================================================================

    #-------------------------------------------------------------------
    # TOOL SELECTION MENU
    #-------------------------------------------------------------------
    
    tool = st.radio("Select a tool:",
        ["Questions About Yourself and Others", "My Feelings and Needs (NEIL Child Version)", "My Feelings and Needs (NEIL Adult Version)", "Daily Digital Connected Life (DDCL)", "Future Inferred Narration of Events (FINE)", "Competency to Stand Trial", "Perceptions of Concern (POC)"], index=None,
        captions=[
            "A brief, non-diagnostic self-report measure designed to assess perceived social connection, loneliness, and online social engagement. Items are written at a 5th–6th grade reading level and are suitable for minimal-risk survey research.\n",
            "A questionnaire that helps measure how a child has been feeling and connecting with others over the past week.\n",
            "A questionnaire that helps measure how an adult has been feeling and connecting with others over the past month.\n",
            "A structured assessment that evaluates patterns of digital device use and online behavior.\n",
            "A scenario writing questionnaire that guides users to imagine detailed narratives of possible future events in order to clarify their current mindset.\n",        
            "An assessment designed to gather information relevant to an individual’s capacity to assist legal counsel as part of a competency to stand trial evaluation.\n",
            "Help identify concerns in the community and prevent harm before it occurs.\n",
        ],
    )
    
    #===================================================================
    
    #-------------------------------------------------------------------
    # TOOL: Questions About People You Know
    # DESRIPTION: To assess for lonliness.
    #-------------------------------------------------------------------
    
    # Create loneliness survey form.
    if tool == "Questions About Yourself and Others" and language == "English":
        with st.form("yvform"):
            st.write("Please answer each question based on how you usually feel. Choose one response.")
            Q1 = st.selectbox("#1. How often do people respond kindly when you share your feelings or worries?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q2 = st.selectbox("#2. Do you feel that people like you and help you?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            # Q2 = st.selectbox("#2. Do you feel that people understand you, encourage you, and know you well?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q3 = st.selectbox("#3. Is it easy to talk to someone and do something together?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            # Q3 = st.selectbox("#3. When you want to talk with someone or do something together, is it easy to connect?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q4 = st.selectbox("#4. How often do you feel separate from others, even when you are with them?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q5 = st.selectbox("#5. I have someone to eat with when I want to share a meal.", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q6 = st.selectbox("#6. It is not easy for me to make friends.", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q7 = st.selectbox("#7. You wait a long time for others to respond to you.", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q8 = st.selectbox("#8. Is it easier for you to play games or do other things by yourself?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q9 = st.selectbox("#9. How often do you feel left out when others get together without inviting you?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q10 = st.selectbox("#10. How often do you feel hurt because you don’t have someone to laugh with or talk to about your thoughts and feelings?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q11 = st.selectbox("#11. Most of my friends are online and not people I see in person.", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q12 = st.selectbox("#12. I spend most of my time online.", ["","Never", "Rarely", "Sometimes", "Often", "Always"])

            submit1 = st.form_submit_button("Submit")
            submit2 = False
            submit3 = False
            submit4 = False
            submit5 = False
            submit6 = False
            submit7 = False    

    #-------------------------------------------------------------------
    # TOOL: Questions About People You Know in Spanish
    # DESRIPTION: To assess for lonliness.
    #-------------------------------------------------------------------

    elif tool == "Questions About Yourself and Others" and language == "Spanish":
        with st.form("yvform"):
            st.write("Por favor, responde cada pregunta según cómo te sientes normalmente. Elige una respuesta.")
            Q1 = st.selectbox("#1. ¿Con qué frecuencia las personas responden con amabilidad cuando compartes tus sentimientos o preocupaciones?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q2 = st.selectbox("#2. ¿Sientes que las personas te quieren y te ayudan?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q3 = st.selectbox("#3. ¿Es fácil hablar con alguien y hacer algo juntos?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q4 = st.selectbox("#4. ¿Con qué frecuencia te sientes separado(a) de los demás, incluso cuando estás con ellos?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q5 = st.selectbox("#5. Tengo a alguien con quien comer cuando quiero compartir una comida.", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q6 = st.selectbox("#6. Es difícil hacer amigos.", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q7 = st.selectbox("#7. Esperas mucho tiempo para que otras personas te respondan.", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q8 = st.selectbox("#8. ¿Es más fácil para jugar o hacer otras cosas tú solo(a)?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q9 = st.selectbox("#9. ¿Con qué frecuencia te sientes excluido(a) cuando otras personas se reúnen sin invitarte?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q10 = st.selectbox("#10. ¿Con qué frecuencia te sientes herido(a) porque no tienes a alguien con quien reír o hablar sobre tus pensamientos y sentimientos?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q11 = st.selectbox("#11. La mayoría de mis amigos están en línea y no son personas que veo en persona.", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q12 = st.selectbox("#12. Paso la mayor parte de mi tiempo en línea.", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])

            submit1 = st.form_submit_button("Enviar")
            submit2 = False
            submit3 = False
            submit4 = False
            submit5 = False
            submit6 = False
            submit7 = False
            
    #-------------------------------------------------------------------
    # TOOL: My Feelings and Needs, NEIL Child Version
    # DESRIPTION: To be used to assess for lonliness in children.
    #-------------------------------------------------------------------

    # Create NEIL Child Version survey form.
    elif tool == "My Feelings and Needs (NEIL Child Version)" and language == "English":
        with st.form("neilform"):
            st.write("Think about how you have felt over the **last week**. Look at each sentence and select the answer that shows how often you felt that way. *If you don’t understand a word, you can skip it.*")
            Q1 = st.selectbox("#1. Other people included me.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q2 = st.selectbox("#2. Others want me to be with them.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q3 = st.selectbox("#3. Surprised.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q4 = st.selectbox("#4. Thankful.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q5 = st.selectbox("#5. Scared.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q6 = st.selectbox("#6. Looking forward to something.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q7 = st.selectbox("#7. Mad.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q8 = st.selectbox("#8. Safe.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q9 = st.selectbox("#9. Calm and peaceful.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q10 = st.selectbox("#10. Worried.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q11 = st.selectbox("#11. Happy.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q12 = st.selectbox("#12. Feeling good with how things are.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            # Q13 = st.selectbox("#13. Very excited.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q13 = st.selectbox("#13. I believe many people do not like me.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q14 = st.selectbox("#14. Uncomfortable or nervous.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q15 = st.selectbox("#15. Really disliking other people.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q16 = st.selectbox("#16. Friendly.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q17 = st.selectbox("#17. Rested and full of energy.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q18 = st.selectbox("#18. Relaxed.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q19 = st.selectbox("#19. Crying a lot.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q20 = st.selectbox("#20. Tired.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q21 = st.selectbox("#21. Lonely.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q22 = st.selectbox("#22. Laughing with others.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q23 = st.selectbox("#23. Like I wanted to cry.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q24 = st.selectbox("#24. Hopeful.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q25 = st.selectbox("#25. Liked.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q26 = st.selectbox("#26. Sad.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q27 = st.selectbox("#27. Jealous (wanting what others have).", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q28 = st.selectbox("#28. In a bad mood.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q29 = st.selectbox("#29. Others are better than you.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q30 = st.selectbox("#30. Part of a group.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q31 = st.selectbox("#31. Liking myself.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q32 = st.selectbox("#32. Having good choices.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q33 = st.selectbox("#33. Interested in learning new things.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q34 = st.selectbox("#34. Hurt by other people.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q35 = st.selectbox("#35. Picked on or made fun of.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q36 = st.selectbox("#36. Understood.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q37 = st.selectbox("#37. Loved.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            # Q38 = st.selectbox("#38. Happy.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q38 = st.selectbox("#38. Left out.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q39 = st.selectbox("#39. Proud of myself.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q40 = st.selectbox("#40. Wishing I was someone else.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q41 = st.selectbox("#41. Wishing I wasn’t here anymore.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            
            submit2 = st.form_submit_button("Submit")
            submit1 = False
            submit3 = False
            submit4 = False
            submit5 = False
            submit6 = False
            submit7 = False
    
    #-------------------------------------------------------------------
    # TOOL: My Feelings and Needs, NEIL Child Version, in Spanish
    # DESRIPTION: To be used to assess for lonliness in children.
    #-------------------------------------------------------------------

    # Create NEIL Child Version survey form in Spanish.
    elif tool == "My Feelings and Needs (NEIL Child Version)" and language == "Spanish":
        with st.form("neilform"):
            st.write("Piensa en cómo te has sentido en la última semana. Mira cada oración y circula el número que mejor refleje cuántas veces te sentiste así.")
            Q1 = st.selectbox("#1. Otras personas me incluyeron.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q2 = st.selectbox("#2. Otros quieren estar conmigo.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q3 = st.selectbox("#3. Sorprendido(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q4 = st.selectbox("#4. Agradecido(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q5 = st.selectbox("#5. Con miedo.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q6 = st.selectbox("#6. Con ganas de que pase algo bueno.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q7 = st.selectbox("#7. Enojado(a) o molesto(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q8 = st.selectbox("#8. Seguro(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q9 = st.selectbox("#9. Tranquilo(a) y en paz.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q10 = st.selectbox("#10. Preocupado(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q11 = st.selectbox("#11. Feliz.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q12 = st.selectbox("#12. Siento bien con cómo están las cosas.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            #Q13 = st.selectbox("#13. Súper emocionado(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q13 = st.selectbox("#13. Siento que no le caía bien a la gente.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q14 = st.selectbox("#14. Incómodo(a) o nervioso(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q15 = st.selectbox("#15. Siento que me caen mal los demás.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q16 = st.selectbox("#16. Amigable.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q17 = st.selectbox("#17. Descansado(a) y con mucha energía.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q18 = st.selectbox("#18. Relajado(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q19 = st.selectbox("#19. Llorando mucho.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q20 = st.selectbox("#20. Cansado(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q21 = st.selectbox("#21. Solo(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q22 = st.selectbox("#22. Riendo con otros.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q23 = st.selectbox("#23. Con ganas de llorar.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q24 = st.selectbox("#24. Con esperanza.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q25 = st.selectbox("#25. Le agrado a los demás.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q26 = st.selectbox("#26. Triste.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q27 = st.selectbox("#27. Celoso(a) (queriendo lo que otros tienen).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q28 = st.selectbox("#28. De mal humor.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q29 = st.selectbox("#29. Siento que otros son mejores que yo.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q30 = st.selectbox("#30. Parte de un grupo.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q31 = st.selectbox("#31. Gustarme a mí mismo(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q32 = st.selectbox("#32. Tengo buenas opciones.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q33 = st.selectbox("#33. Con ganas de aprender cosas nuevas.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q34 = st.selectbox("#34. Lastimado(a) por otras personas.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q35 = st.selectbox("#35. Molestado(a) o que se burlan de mí.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q36 = st.selectbox("#36. Comprendido(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q37 = st.selectbox("#37. Amado(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            #Q38 = st.selectbox("#38. Feliz.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q38 = st.selectbox("#38. Dejado(a) fuera.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q39 = st.selectbox("#39. Orgulloso(a) de mí mismo(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q40 = st.selectbox("#40. Deseando ser otra persona.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q41 = st.selectbox("#41. Deseando ya no estar aquí.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])

            submit2 = st.form_submit_button("Submit")
            submit1 = False
            submit3 = False
            submit4 = False
            submit5 = False
            submit6 = False
            submit7 = False

    #-------------------------------------------------------------------
    # TOOL: My Feelings and Needs, NEIL Adult Version
    # DESRIPTION: To be used to assess for lonliness in adults.
    #-------------------------------------------------------------------

    # Create NEIL Adult Version survey form.
    elif tool == "My Feelings and Needs (NEIL Adult Version)" and language == "English":
        with st.form("neilform-adult"):
            st.write("Please indicate how often you experienced each of the following in the *last month*. Not everyone experiences everything on this list. If you don't understand a word or choose not to answer the question, you can just go ahead and skip the item. Could you try to rate as many as possible?")
            Q1 = st.selectbox("#1. Included by others.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q2 = st.selectbox("#2. Surprised.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q3 = st.selectbox("#3. Thankful.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q4 = st.selectbox("#4. Afraid.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q5 = st.selectbox("#5. Looking forward to tomorrow.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q6 = st.selectbox("#6. Angry.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q7 = st.selectbox("#7. Safe.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q8 = st.selectbox("#8. Calm.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q9 = st.selectbox("#9. Worried.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q10 = st.selectbox("#10. Glad.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q11 = st.selectbox("#11. Satisfied.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q12 = st.selectbox("#12. Thrilled.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q13 = st.selectbox("#13. Disliked.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q14 = st.selectbox("#14. Uncomfortable.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q15 = st.selectbox("#15. Hate.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q16 = st.selectbox("#16. Friendly.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q17 = st.selectbox("#17. Rested.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q18 = st.selectbox("#18. Relaxed.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q19 = st.selectbox("#19. Anxious.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q20 = st.selectbox("#20. Tired.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q21 = st.selectbox("#21. Lonely.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q22 = st.selectbox("#22. Able to laugh.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q23 = st.selectbox("#23. Tearful.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q24 = st.selectbox("#24. Hopeful.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q25 = st.selectbox("#25. Respected.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q26 = st.selectbox("#26. Sadness.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q27 = st.selectbox("#27. Envious.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q28 = st.selectbox("#28. Irritated.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q29 = st.selectbox("#29. Shame.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q30 = st.selectbox("#30. Part of a group.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q31 = st.selectbox("#31. Liking yourself.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q32 = st.selectbox("#32. Having good choices.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q33 = st.selectbox("#33. Curiosity.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q34 = st.selectbox("#34. Hurt by others.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q35 = st.selectbox("#35. Understood.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q36 = st.selectbox("#36. Loved.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q37 = st.selectbox("#37. Happy.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q38 = st.selectbox("#38. Left-out.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q39 = st.selectbox("#39. Proud.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q40 = st.selectbox("#40. Wishing you were not here.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q41 = st.selectbox("#41. Believing life will get better.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q42 = st.selectbox("#42. Feeling the discomfort of stress in your body.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])

            submit3 = st.form_submit_button("Submit")
            submit1 = False
            submit2 = False
            submit4 = False
            submit5 = False
            submit6 = False
            submit7 = False
    
    #-------------------------------------------------------------------
    # TOOL: Daily Digital Connected life, DDCL
    # DESRIPTION: To be used to assess for isolation due to online
    # activity.
    #-------------------------------------------------------------------

    # Create DDCL survey form.
    elif tool == "Daily Digital Connected Life (DDCL)" and language == "English":
        with st.form("ddclform"):
            st.write("These qusetions provide an overview of your Daily Digital Connected Life (DDCL). Please rate the following.")
            Q1 = st.selectbox("#1. I use my DDCL devices as the primary source of the music I listen to.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q2 = st.selectbox("#2. I frequently use digital devices to entertain myself when I'm bored.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q3 = st.selectbox("#3. With the pace of my life, it is much easier to text and digitally chat than talk on the phone or sometimes find the time to meet in person.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q4 = st.selectbox("#4. Have you ever downloaded an app like Tinder, OkCupid, Bumble, Grindr, Her, BeNaughty, Plenty of Fish, etc.?", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q5 = st.selectbox("#5. It is easier for me to express my feelings in the messages I send rather than trying to express them to someone in person.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q6 = st.selectbox("#6. My strongest connections with others are facilitated through the apps that I am using.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q7 = st.selectbox("#7. Just in case I ever feel it is necessary at some point, I have looked online at ways I might be able to end my own life.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q8 = st.selectbox("#8. I manage my anxiety by reading posts or articles on my DDCL devices.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q9 = st.selectbox("#9. When I need to distract myself, I use my DDCL devices.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q10 = st.selectbox("#10. Some of what I enjoy is illegal and I appreciate that online I can anonymously interact with others with similar interests.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q11 = st.selectbox("#11. I am using my DDCL devices to meet new people.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q12 = st.selectbox("#12. I have never been on the Internet.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q13 = st.selectbox("#13. I use the World Wide Web often to fuel my most intimate fantasies.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q14 = st.selectbox("#14. To be prepared, I have looked online at ways to protect myself and also at ways to harm others that may be a real threat to me.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q15 = st.selectbox("#15. The best way to get to know me is through what I post and the pictures or videos I share. These are availabe online or through my messaging.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q16 = st.selectbox("#16. Have you ever used an app to meet someone?", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q17 = st.selectbox("#17. Because explaining to someone my reactions to what they said or did can be difficult, I often send messages rather than meet face-to-face.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q18 = st.selectbox("#18. I often lose track of time, go to bed too late, or lose windows of opportunity for other activities because I'm at times engaged in the digital world or with messaging.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q19 = st.selectbox("#19. When I'm not feeling well, I go online to research my symptoms.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q20 = st.selectbox("#20. I frequently spend my downtime gaming, watching videos, or reading on my DDCL devices.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q21 = st.selectbox("#21. I have felt hurt by what other people, including friends, have posted or shared in our mutual DDCL.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q22 = st.selectbox("#22. I am currently using virtual reality gear (HoloLens, Oculus Rift, Samsung Gear VR, Google DayDream View, PlayStation VR, etc.).", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q23 = st.selectbox("#23. Just in case I ever feel it is necessary at some point, I have looked online at ways I might be able to end my own life.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q24 = st.selectbox("#24. At times I wish there were an \"unsend\" or \"delete\" button for a text that I have sent or for something that I posted on a social media outlet.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q25 = st.selectbox("#25. I am aware that others have felt upset with what I have posted or shared in our mutual DDCL.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q26 = st.selectbox("#26. I have downloaded an online dating app.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q27 = st.selectbox("#27. I'd rather purchase items online than go to a neighborhood store.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q28 = st.selectbox("#28. I have needed to block the access of someone I know to my DDCL.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q29 = st.selectbox("#29. I have multiple social network accounts with different names that I selectively share with only a few of my friends or family.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q30 = st.selectbox("#30. I have pictures and other items on my DDCL devices that I do not want other people to see.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q31 = st.selectbox("#31. Some of the people who say they care about me would disapprove of the webpages I visit, the peope I chat with online, or some of what I post anonymously.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q32 = st.selectbox("#32. I have looked at the images of others online to feel better about my weight and size.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q33 = st.selectbox("#33. It is hard for me to imagine staying current with those in my networks without extensively using my DDCL devices.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q34 = st.selectbox("#34. I have deleted photographs and/or videos from my DDCL.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q35 = st.selectbox("#35. I'd rather purchase items in a store than online.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q36 = st.selectbox("#36. I enjoy fooling others online by pretending to be a different person.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q37 = st.selectbox("#37. I use apps to help me find new places to eat or drink.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q38 = st.selectbox("#38. I have another phone or device that no one knows about to keep aspects of my life private.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])
            Q39 = st.selectbox("#39. I look at more items online than I actually purchase.", ["","False", "Seldom True", "At Times True", "Frequently True", "Extremely True"])

            submit5 = st.form_submit_button("Submit")
            submit1 = False
            submit2 = False
            submit3 = False
            submit4 = False
            submit6 = False
            submit7 = False

    #-------------------------------------------------------------------
    # TOOL: Future Inferred Narration of Events, FINE
    # DESRIPTION: To assess for an individual's perception of self.
    #-------------------------------------------------------------------

    # Create FINE Version survey form.
    elif tool == "Future Inferred Narration of Events (FINE)" and language == "English":
        with st.form("fineform"):
            st.write("The sentences below describe events that may happen in your future. Respond to each future event as if you are the main character. Text what you would send describing what happened.")

            Q1 = st.text_area("#1. Something you always wanted happens.", placeholder="Write your thoughts here...", height=150)
            Q2 = st.text_area("#2. A valued possession is damaged.", placeholder="Write your thoughts here...", height=150)
            Q3 = st.text_area("#3. You have an argument/disagreement with someone.", placeholder="Write your thoughts here...", height=150)
            Q4 = st.text_area("#4. You go on vacation.", placeholder="Write your thoughts here...", height=150)
            Q5 = st.text_area("#5. You break something.", placeholder="Write your thoughts here...", height=150)
            Q6 = st.text_area("#6. You are successful.", placeholder="Write your thoughts here...", height=150)
            Q7 = st.text_area("#7. An important relationship changes.", placeholder="Write your thoughts here...", height=150)
            Q8 = st.text_area("#8. You move.", placeholder="Write your thoughts here...", height=150)
            Q9 = st.text_area("#9. You forgive.", placeholder="Write your thoughts here...", height=150)
            Q10 = st.text_area("#10. You go to court.", placeholder="Write your thoughts here...", height=150)
            Q11 = st.text_area("#11. You go to the doctor.", placeholder="Write your thoughts here...", height=150)
            Q12 = st.text_area("#12. You find something you have been looking for.", placeholder="Write your thoughts here...", height=150)
            Q13 = st.text_area("#13. You are forgiven and feel understood.", placeholder="Write your thoughts here...", height=150)
            Q14 = st.text_area("#14. You believe life is on track to accomplish what?", placeholder="Write your thoughts here...", height=150)

            submit4 = st.form_submit_button("Submit")
            submit1 = False
            submit2 = False
            submit3 = False    
            submit5 = False
            submit6 = False
            submit7 = False

    #-------------------------------------------------------------------
    # TOOL: Competency to Stand Trial
    # DESRIPTION: To assess for an individual's competency to stand 
    # trial, prong two test.
    #-------------------------------------------------------------------

    # Create Competency to Stand Trial, prong two assessment.
    elif tool == "Competency to Stand Trial" and language == "English":
        with st.form("competencyform"):
            st.write("These questions help assess whether a defendant can understand the legal proceedings and communicate rationally with counsel to assist in their defense. Please answer the following.")
            Q1 = st.selectbox("#1. Does the defendant remember officers of the court?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q2 = st.selectbox("#2. Does the defendant remember their own counsel and team members?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q3 = st.selectbox("#3. Does the defendant follow advisement, such as not discussing their case with anyone not involved while it is being adjudicated?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q4 = st.selectbox("#4. Does the defendant recall prior conversations and can explain why their perceptions have changed?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q5 = st.selectbox("#5. In the investigation, was the defendant able to answer the questions asked?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q6 = st.selectbox("#6. Did the defendant appear to understand the seriousness of the accusations or allegations?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q7 = st.selectbox("#7. Do you believe the defendant can assist counsel or provide information addressing the circumstances of the current charges being considered?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q8 = st.selectbox("#8. Does the defendant have better interactions with others that you work with?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q9 = st.selectbox("#9. Is the defendant able to calm down if needed?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q10 = st.selectbox("#10. If the defendant is acting inappropriately, is counsel, the bailiff, sheriff, marshal, or judge able to address the conduct of the defendant in a manner that facilitates due process?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q11 = st.selectbox("#11. Do you believe court outbursts by the defendant are intentional?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q12 = st.selectbox("#12. Does the defendant respond appropriately to those present in the courthouse?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q13 = st.selectbox("#13. Does the defendant appear to comprehend what is taking place?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q14 = st.selectbox("#14. Does the defendant appear as if in their own world, responding to internal stimuli inappropriately, such as laughing, talking to themselves, or uttering unrestrained words or statements?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q15 = st.selectbox("#15. Are others uneasy in the presence of the defendant as if they may suddenly act inappropriately, whether verbally or physically?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])
            Q16 = st.selectbox("#16. Does the defendant remember the charges with breaks in contact?", ["","Cannot Answer", "Affirmative of Ability", "Compromised", "Inability"])

            submit6 = st.form_submit_button("Submit")
            submit1 = False
            submit2 = False
            submit3 = False    
            submit4 = False
            submit5 = False
            submit7 = False

    #-------------------------------------------------------------------
    # TOOL: Perceptions of Concern, POC
    # DESRIPTION: To survey possible witnesses about concerning
    # behaviors.
    #-------------------------------------------------------------------

    # Create POC survey form.
    elif tool == "Perceptions of Concern (POC)" and language == "English":
        with st.form("pocform"):
            st.write("This survey is a tool for early intervention and prevention. We aim to address concerns, distrust, and potential conflicts before they escalate. This is not a platform for blame, but a proactive way to ensure a safe environment for everyone.")

            Q1 = st.text_area("#1. Is there an individual or group causing you to fear for your safety or the safety of others?", placeholder="Write your thoughts here...", height=150)
            Q2 = st.text_area("#2. Have you observed any behaviors or incidents of concern? Please describe them briefly (as if writing a text message).", placeholder="Write your thoughts here...", height=150)
            Q3 = st.text_area("#3. Have you heard or read anything (in person, online, or in writing) suggestive of potential harm or violence? Please share what was said and where it was found.", placeholder="Write your thoughts here...", height=150)
            Q4 = st.text_area("#4. Are you aware of this person/group possessing or mentioning weapons (firearms, etc.), or have you heard reports of gunfire or explosions?", placeholder="Write your thoughts here...", height=150)
            Q5 = st.text_area("#5. Has the individual shown signs of instability, such as extreme mood swings, sudden isolation, or reactions to a major personal loss (job, relationship, etc.)?", placeholder="Write your thoughts here...", height=150)
            Q6 = st.text_area("#6. Does this person/group target specific individuals or communities with blame, insults, or expressions of hatred?", placeholder="Write your thoughts here...", height=150)
            Q7 = st.text_area("#7. Has this situation impacted your daily routine, physical health (sleep/stress), or caused you to change your habits to avoid contact?", placeholder="Write your thoughts here...", height=150)
            Q8 = st.text_area("#8. Based on what you know, what is the \"story\" of what might happen? Who is involved and what is the specific concern?", placeholder="Write your thoughts here...", height=150)
            Q9 = st.text_area("#9. What intervention or solution do you believe would best resolve this conflict in your neighborhood or workplace?", placeholder="Write your thoughts here...", height=150)

            submit7 = st.form_submit_button("Submit")
            submit1 = False
            submit2 = False
            submit3 = False
            submit4 = False
            submit5 = False
            submit6 = False
    
    #-------------------------------------------------------------------
    # TOOL: Perceptions of Concern, POC, in Spanish
    # DESRIPTION: To survey possible witnesses about concerning
    # behaviors.
    #-------------------------------------------------------------------

    elif tool == "Perceptions of Concern (POC)" and language == "Spanish":
        with st.form("pocform"):
            st.write("Esta encuesta es una herramienta para la intervención temprana y la prevención. Nuestro objetivo es abordar inquietudes, desconfianza y posibles conflictos antes de que se intensifiquen. Esta no es una plataforma para culpar, sino una forma proactiva de garantizar un entorno seguro para todos.")

            Q1 = st.text_area("#1. ¿Existe alguna persona o grupo que le haga temer por su seguridad o la de los demás?", placeholder="Escriba aquí...", height=150)
            Q2 = st.text_area("#2. ¿Ha observado algún comportamiento o incidente preocupante? Por favor, descríbalos brevemente (como si escribiera un mensaje de texto).", placeholder="Escriba aquí...", height=150)
            Q3 = st.text_area("#3. ¿Ha escuchado o leído algo (en persona, en línea o por escrito) que sugiera un posible daño o violencia? Por favor, comparta lo que se dijo y dónde se encontró.", placeholder="Escriba aquí...", height=150)
            Q4 = st.text_area("#4. ¿Tiene conocimiento de que esta persona o grupo posea o mencione armas (armas de fuego, etc.), o ha escuchado informes de disparos o explosiones?", placeholder="Escriba aquí...", height=150)
            Q5 = st.text_area("#5. ¿Ha mostrado el individuo signos de inestabilidad, como cambios extremos de humor, aislamiento repentino o reacciones ante una pérdida personal importante (trabajo, relación, etc.)?", placeholder="Escriba aquí...", height=150)
            Q6 = st.text_area("#6. ¿Esta persona o grupo ataca a individuos o comunidades específicas con culpas, insultos o expresiones de odio?", placeholder="Escriba aquí...", height=150)
            Q7 = st.text_area("#7. ¿Ha afectado esta situación su rutina diaria, su salud física (sueño/estrés) o le ha obligado a cambiar sus hábitos para evitar el contacto?", placeholder="Escriba aquí...", height=150)
            Q8 = st.text_area("#8. Según lo que sabe, ¿cuál es la \"historia\" de lo que podría suceder? ¿Quién está involucrado y cuál es la preocupación específica?", placeholder="Escriba aquí...", height=150)
            Q9 = st.text_area("#9. ¿Qué intervención o solución cree que resolvería mejor este conflicto en su vecindario o lugar de trabajo?", placeholder="Escriba aquí...", height=150)

            submit7 = st.form_submit_button("Submit")
            submit1 = False
            submit2 = False
            submit3 = False
            submit4 = False
            submit5 = False
            submit6 = False

    else:
        submit1 = False
        submit2 = False
        submit3 = False
        submit4 = False
        submit5 = False
        submit6 = False
        submit7 = False

    #===================================================================

    #-------------------------------------------------------------------
    # TOOL SCORING
    # TOOL: Questions About Yourself and Others
    #-------------------------------------------------------------------

    if submit1 and language == "English":
        Q_total = 0
        Q_response = ""
        Q_rawdata = name + "," + str(age) + ","

        # Questions 4, 6 thru 12, scored in reverse.
        if Q1 == "Never": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q1:How often do people respond kindly when you share your feelings or worries?=Never,"
        elif Q1 == "Rarely":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q1:How often do people respond kindly when you share your feelings or worries?=Rarely,"
        elif Q1 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q1:How often do people respond kindly when you share your feelings or worries?=Sometimes,"
        elif Q1 == "Often":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q1:How often do people respond kindly when you share your feelings or worries?=Often,"
        elif Q1 == "Always":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q1:How often do people respond kindly when you share your feelings or worries?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q1:How often do people respond kindly when you share your feelings or worries?=No Answer,"
        
        if Q2 == "Never": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people like you and help you?=Never,"
        elif Q2 == "Rarely":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people like you and help you?=Rarely,"
        elif Q2 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people like you and help you?=Sometimes,"
        elif Q2 == "Often":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people like you and help you?=Often,"
        elif Q2 == "Always":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people like you and help you?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people like you and help you?=No Answer,"

        if Q3 == "Never": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q3:Is it easy to talk to someone and do something together?=Never,"
        elif Q3 == "Rarely":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q3:Is it easy to talk to someone and do something together?=Rarely,"
        elif Q3 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q3:Is it easy to talk to someone and do something together?=Sometimes,"
        elif Q3 == "Often":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q3:Is it easy to talk to someone and do something together?=Often,"
        elif Q3 == "Always":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q3:Is it easy to talk to someone and do something together?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q3:Is it easy to talk to someone and do something together?=No Answer,"

        # Scored in reverse.
        if Q4 == "Never": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q4:How often do you feel separate from others, even when you are with them?=Never,"
        elif Q4 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q4:How often do you feel separate from others, even when you are with them?=Rarely,"
        elif Q4 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q4:How often do you feel separate from others, even when you are with them?=Sometimes,"
        elif Q4 == "Often":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q4:How often do you feel separate from others, even when you are with them?=Often,"
        elif Q4 == "Always":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q4:How often do you feel separate from others, even when you are with them?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q4:How often do you feel separate from others, even when you are with them?=No Answer,"

        if Q5 == "Never": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q5:I have someone to eat with when I want to share a meal.=Never,"
        elif Q5 == "Rarely":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q5:I have someone to eat with when I want to share a meal.=Rarely,"
        elif Q5 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q5:I have someone to eat with when I want to share a meal.=Sometimes,"
        elif Q5 == "Often":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q5:I have someone to eat with when I want to share a meal.=Often,"
        elif Q5 == "Always":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q5:I have someone to eat with when I want to share a meal.=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q5:I have someone to eat with when I want to share a meal.=No Answer,"
        
        # Scored in reverse.
        if Q6 == "Never": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q6:It is not easy for me to make friends.=Never,"
        elif Q6 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q6:It is not easy for me to make friends.=Rarely,"
        elif Q6 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q6:It is not easy for me to make friends.=Sometimes,"
        elif Q6 == "Often":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q6:It is not easy for me to make friends.=Often,"
        elif Q6 == "Always":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q6:It is not easy for me to make friends.=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q6:It is not easy for me to make friends.=No Answer,"
    
        # Scored in reverse.
        if Q7 == "Never": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q7:You wait a long time for others to respond to you.=Never,"
        elif Q7 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q7:You wait a long time for others to respond to you.=Rarely,"
        elif Q7 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q7:You wait a long time for others to respond to you.=Sometimes,"
        elif Q7 == "Often":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q7:You wait a long time for others to respond to you.=Often,"
        elif Q7 == "Always":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q7:You wait a long time for others to respond to you.=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q7:You wait a long time for others to respond to you.=No Answer,"

        # Scored in reverse.
        if Q8 == "Never": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or do other things by yourself?=Never,"
        elif Q8 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or do other things by yourself?=Rarely,"
        elif Q8 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or do other things by yourself?=Sometimes,"
        elif Q8 == "Often":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or do other things by yourself?=Often,"
        elif Q8 == "Always":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or do other things by yourself?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or do other things by yourself?=No Answer,"

        # Scored in reverse.
        if Q9 == "Never": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q9:How often do you feel left out when others get together without inviting you?=Never,"
        elif Q9 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q9:How often do you feel left out when others get together without inviting you?=Rarely,"
        elif Q9 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q9:How often do you feel left out when others get together without inviting you?=Sometimes,"
        elif Q9 == "Often":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q9:How often do you feel left out when others get together without inviting you?=Often,"
        elif Q9 == "Always":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q9:How often do you feel left out when others get together without inviting you?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q9:How often do you feel left out when others get together without inviting you?=No Answer,"

        # Scored in reverse.
        if Q10 == "Never": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q10:How often do you feel hurt because you don’t have someone to laugh with or talk to about your thoughts and feelings?=Never,"
        elif Q10 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q10:How often do you feel hurt because you don’t have someone to laugh with or talk to about your thoughts and feelings?=Rarely,"
        elif Q10 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q10:How often do you feel hurt because you don’t have someone to laugh with or talk to about your thoughts and feelings?=Sometimes,"
        elif Q10 == "Often":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q10:How often do you feel hurt because you don’t have someone to laugh with or talk to about your thoughts and feelings?=Often,"
        elif Q10 == "Always":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q10:How often do you feel hurt because you don’t have someone to laugh with or talk to about your thoughts and feelings?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q10:How often do you feel hurt because you don’t have someone to laugh with or talk to about your thoughts and feelings?=No Answer,"

        # Scored in reverse.
        if Q11 == "Never": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q11:Most of my friends are online and not people I see in person.=Never,"
        elif Q11 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q11:Most of my friends are online and not people I see in person.=Rarely,"
        elif Q11 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q11:Most of my friends are online and not people I see in person.=Sometimes,"
        elif Q11 == "Often":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q11:Most of my friends are online and not people I see in person.=Often,"
        elif Q11 == "Always":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q11:Most of my friends are online and not people I see in person.=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q11:Most of my friends are online and not people I see in person.=No Answer,"
        
        # Scored in reverse.
        if Q12 == "Never": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q12:I spend most of my time online.=Never,"
        elif Q12 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q12:I spend most of my time online.=Rarely,"
        elif Q12 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q12:I spend most of my time online.=Sometimes,"
        elif Q12 == "Often":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q12:I spend most of my time online.=Often,"
        elif Q12 == "Always":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q12:I spend most of my time online.=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q12:I spend most of my time online.=No Answer,"

        if Q_total >= 0 and Q_total <= 15:
            st.write(f"#### Total Score: {Q_total} (High social isolation)")
            Q_response = "High social isolation."
        elif Q_total >= 16 and Q_total <= 31:
            st.write(f"#### Total Score: {Q_total} (Mixed/moderate social connection)")
            Q_response = "Mixed/moderate connection."
        elif Q_total >= 32 and Q_total <= 48:
            st.write(f"#### Total Score: {Q_total} (Strong social connection)")
            Q_response = "Strong social connection."

        st.markdown("For additional information and resources, please visit: [US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")
        Q_rawdata = Q_rawdata + "Score=" + str(Q_total)

    #-------------------------------------------------------------------
    # TOOL SCORING
    # TOOL: Questions About Yourself and Others, in Spanish
    #-------------------------------------------------------------------

    if submit1 and language == "Spanish":
        Q_total = 0
        Q_response = ""
        Q_rawdata = name + "," + str(age) + ","

        # Questions 4, 6 thru 12, scored in reverse.
        if Q1 == "Nunca": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q1:¿Con qué frecuencia las personas responden con amabilidad cuando compartes tus sentimientos o preocupaciones?=Nunca,"
        elif Q1 == "Rara vez":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q1:¿Con qué frecuencia las personas responden con amabilidad cuando compartes tus sentimientos o preocupaciones?=Rara vez,"
        elif Q1 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q1:¿Con qué frecuencia las personas responden con amabilidad cuando compartes tus sentimientos o preocupaciones?=A veces,"
        elif Q1 == "A menudo":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q1:¿Con qué frecuencia las personas responden con amabilidad cuando compartes tus sentimientos o preocupaciones?=A menudo,"
        elif Q1 == "Siempre":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q1:¿Con qué frecuencia las personas responden con amabilidad cuando compartes tus sentimientos o preocupaciones?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q1:¿Con qué frecuencia las personas responden con amabilidad cuando compartes tus sentimientos o preocupaciones?=No Contesta,"
        
        if Q2 == "Nunca": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te quieren y te ayudan?=Nunca,"
        elif Q2 == "Rara vez":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te quieren y te ayudan?=Rara vez,"
        elif Q2 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te quieren y te ayudan?=A veces,"
        elif Q2 == "A menudo":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te quieren y te ayudan?=A menudo,"
        elif Q2 == "Siempre":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te quieren y te ayudan?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te quieren y te ayudan?=No Contesta,"

        if Q3 == "Nunca": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q3:¿Es fácil hablar con alguien y hacer algo juntos?=Nunca,"
        elif Q3 == "Rara vez":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q3:¿Es fácil hablar con alguien y hacer algo juntos?=Rara vez,"
        elif Q3 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q3:¿Es fácil hablar con alguien y hacer algo juntos?=A veces,"
        elif Q3 == "A menudo":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q3:¿Es fácil hablar con alguien y hacer algo juntos?=A menudo,"
        elif Q3 == "Siempre":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q3:¿Es fácil hablar con alguien y hacer algo juntos?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q3:¿Es fácil hablar con alguien y hacer algo juntos?=No Contesta,"

        # Scored in reverse.
        if Q4 == "Nunca": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q4:¿Con qué frecuencia te sientes separado(a) de los demás, incluso cuando estás con ellos?=Nunca,"
        elif Q4 == "Rara vez":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q4:¿Con qué frecuencia te sientes separado(a) de los demás, incluso cuando estás con ellos?=Rara vez,"
        elif Q4 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q4:¿Con qué frecuencia te sientes separado(a) de los demás, incluso cuando estás con ellos?=A veces,"
        elif Q4 == "A menudo":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q4:¿Con qué frecuencia te sientes separado(a) de los demás, incluso cuando estás con ellos?=A menudo,"
        elif Q4 == "Siempre":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q4:¿Con qué frecuencia te sientes separado(a) de los demás, incluso cuando estás con ellos?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q4:¿Con qué frecuencia te sientes separado(a) de los demás, incluso cuando estás con ellos?=No Contesta,"

        if Q5 == "Nunca": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q5:Tengo a alguien con quien comer cuando quiero compartir una comida.=Nunca,"
        elif Q5 == "Rara vez":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q5:Tengo a alguien con quien comer cuando quiero compartir una comida.=Rara vez,"
        elif Q5 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q5:Tengo a alguien con quien comer cuando quiero compartir una comida.=A veces,"
        elif Q5 == "A menudo":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q5:Tengo a alguien con quien comer cuando quiero compartir una comida.=A menudo,"
        elif Q5 == "Siempre":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q5:Tengo a alguien con quien comer cuando quiero compartir una comida.=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q5:Tengo a alguien con quien comer cuando quiero compartir una comida.=No Contesta,"
        
        # Scored in reverse.
        if Q6 == "Nunca": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q6:Es difícil hacer amigos.=Nunca,"
        elif Q6 == "Rara vez":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q6:Es difícil hacer amigos.=Rara vez,"
        elif Q6 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q6:Es difícil hacer amigos.=A veces,"
        elif Q6 == "A menudo":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q6:Es difícil hacer amigos.=A menudo,"
        elif Q6 == "Siempre":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q6:Es difícil hacer amigos.=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q6:Es difícil hacer amigos.=No Contesta,"
    
        # Scored in reverse.
        if Q7 == "Nunca": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q7:Esperas mucho tiempo para que otras personas te respondan.=Nunca,"
        elif Q7 == "Rara vez":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q7:Esperas mucho tiempo para que otras personas te respondan.=Rara vez,"
        elif Q7 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q7:Esperas mucho tiempo para que otras personas te respondan.=A veces,"
        elif Q7 == "A menudo":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q7:Esperas mucho tiempo para que otras personas te respondan.=A menudo,"
        elif Q7 == "Siempre":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q7:Esperas mucho tiempo para que otras personas te respondan.=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q7:Esperas mucho tiempo para que otras personas te respondan.=No Contesta,"

        # Scored in reverse.
        if Q8 == "Nunca": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q8:¿Es más fácil para jugar o hacer otras cosas tú solo(a)?=Nunca,"
        elif Q8 == "Rara vez":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q8:¿Es más fácil para jugar o hacer otras cosas tú solo(a)?=Rara vez,"
        elif Q8 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q8:¿Es más fácil para jugar o hacer otras cosas tú solo(a)?=A veces,"
        elif Q8 == "A menudo":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q8:¿Es más fácil para jugar o hacer otras cosas tú solo(a)?=A menudo,"
        elif Q8 == "Siempre":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q8:¿Es más fácil para jugar o hacer otras cosas tú solo(a)?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q8:¿Es más fácil para jugar o hacer otras cosas tú solo(a)?=No Contesta,"

        # Scored in reverse.
        if Q9 == "Nunca": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q9:¿Con qué frecuencia te sientes excluido(a) cuando otras personas se reúnen sin invitarte?=Nunca,"
        elif Q9 == "Rara vez":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q9:¿Con qué frecuencia te sientes excluido(a) cuando otras personas se reúnen sin invitarte?=Rara vez,"
        elif Q9 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q9:¿Con qué frecuencia te sientes excluido(a) cuando otras personas se reúnen sin invitarte?=A veces,"
        elif Q9 == "A menudo":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q9:¿Con qué frecuencia te sientes excluido(a) cuando otras personas se reúnen sin invitarte?=A menudo,"
        elif Q9 == "Siempre":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q9:¿Con qué frecuencia te sientes excluido(a) cuando otras personas se reúnen sin invitarte?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q9:¿Con qué frecuencia te sientes excluido(a) cuando otras personas se reúnen sin invitarte?=No Contesta,"

        # Scored in reverse.
        if Q10 == "Nunca": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q10:¿Con qué frecuencia te sientes herido(a) porque no tienes a alguien con quien reír o hablar sobre tus pensamientos y sentimientos?=Nunca,"
        elif Q10 == "Rara vez":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q10:¿Con qué frecuencia te sientes herido(a) porque no tienes a alguien con quien reír o hablar sobre tus pensamientos y sentimientos?=Rara vez,"
        elif Q10 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q10:¿Con qué frecuencia te sientes herido(a) porque no tienes a alguien con quien reír o hablar sobre tus pensamientos y sentimientos?=A veces,"
        elif Q10 == "A menudo":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q10:¿Con qué frecuencia te sientes herido(a) porque no tienes a alguien con quien reír o hablar sobre tus pensamientos y sentimientos?=A menudo,"
        elif Q10 == "Siempre":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q10:¿Con qué frecuencia te sientes herido(a) porque no tienes a alguien con quien reír o hablar sobre tus pensamientos y sentimientos?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q10:¿Con qué frecuencia te sientes herido(a) porque no tienes a alguien con quien reír o hablar sobre tus pensamientos y sentimientos?=No Contesta,"

        # Scored in reverse.
        if Q11 == "Nunca": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q11:La mayoría de mis amigos están en línea y no son personas que veo en persona.=Nunca,"
        elif Q11 == "Rara vez":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q11:La mayoría de mis amigos están en línea y no son personas que veo en persona.=Rara vez,"
        elif Q11 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q11:La mayoría de mis amigos están en línea y no son personas que veo en persona.=A veces,"
        elif Q11 == "A menudo":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q11:La mayoría de mis amigos están en línea y no son personas que veo en persona.=A menudo,"
        elif Q11 == "Siempre":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q11:La mayoría de mis amigos están en línea y no son personas que veo en persona.=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q11:La mayoría de mis amigos están en línea y no son personas que veo en persona.=No Contesta,"

        # Scored in reverse.
        if Q12 == "Nunca": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q12:Paso la mayor parte de mi tiempo en línea.=Nunca,"
        elif Q12 == "Rara vez":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q12:Paso la mayor parte de mi tiempo en línea.=Rara vez,"
        elif Q12 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q12:Paso la mayor parte de mi tiempo en línea.=A veces,"
        elif Q12 == "A menudo":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q12:Paso la mayor parte de mi tiempo en línea.=A menudo,"
        elif Q12 == "Siempre":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q12:Paso la mayor parte de mi tiempo en línea.=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q12:Paso la mayor parte de mi tiempo en línea.=No Contesta,"
        
        if Q_total >= 0 and Q_total <= 15:
            st.write(f"#### Puntos Totales: {Q_total} (Alto aislamiento social)")
            Q_response = "Alta soledad social."
        elif Q_total >= 16 and Q_total <= 31:
            st.write(f"#### Puntos Totales: {Q_total} (Conexión social mixta/moderada)")
            Q_response = "Conexión mixta/moderada."
        elif Q_total >= 32 and Q_total <= 48:
            st.write(f"#### Puntos Totales: {Q_total} (Conexión social fuerte)")
            Q_response = "Conexión social fuerte."

        st.markdown("Para más información y recursos, favor de visitar: [US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")
        Q_rawdata = Q_rawdata + "Score=" + str(Q_total)

    #-------------------------------------------------------------------
    # TOOL SCORING
    # TOOL: My Feelings and Needs, NEIL Child Version
    #-------------------------------------------------------------------

    if submit2 and language == "English":
        Q_connection = 0
        Q_inclusion = 0
        Q_isolation = 0
        Q_happy_feelings = 0
        Q_bad_feelings = 0
        Q_total = 0
        Q_response = ""
        Q_rawdata = name + "," + str(age) + ","

        # Connection Score is total from questions 1, 2, 22, 25, 30, 36, 37.
        # Inclusion Score is total from questions 1, 2, 16, 22, 25, 30, 36, 37.
        # Isolation Score is total from questions 13, 21, 34, 35, 38.
        # Happy Feelings Score is total from questions 3, 4, 6, 8, 9, 11, 12, 17, 18, 24, 31, 32, 33, 39.
        # Scores for bad feelings (questions 5, 7, 10, 14, 15, 19, 20, 23, 26, 27, 28, 29, 35) and 
        # isoluation (questions 13, 21, 34, 35, 38) will be subtracted from other question totals.
        if Q1 == "Not at all": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q1:Other people included me.=Not at all,"
        elif Q1 == "Only a little":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q1:Other people included me.=Only a little,"
        elif Q1 == "Sometimes":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q1:Other people included me.=Sometimes,"
        elif Q1 == "Often":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q1:Other people included me.=Often,"
        elif Q1 == "A lot of the time (almost always)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q1:Other people included me.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q1:Other people included me.=No Answer,"

        if Q2 == "Not at all": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q2:Others want me to be with them.=Not at all,"
        elif Q2 == "Only a little":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q2:Others want me to be with them.=Only a little,"
        elif Q2 == "Sometimes":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q2:Others want me to be with them.=Sometimes,"
        elif Q2 == "Often":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q2:Others want me to be with them.=Often,"
        elif Q2 == "A lot of the time (almost always)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q2:Others want me to be with them.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q2:Others want me to be with them.=No Answer,"

        if Q3 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q3:Surprised.=Not at all,"
        elif Q3 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q3:Surprised.=Only a little,"
        elif Q3 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q3:Surprised.=Sometimes,"
        elif Q3 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q3:Surprised.=Often,"
        elif Q3 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q3:Surprised.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q3:Surprised.=No Answer,"

        if Q4 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q4:Thankful.=Not at all,"
        elif Q4 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q4:Thankful.=Only a little,"
        elif Q4 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q4:Thankful.=Sometimes,"
        elif Q4 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q4:Thankful.=Often,"
        elif Q4 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q4:Thankful.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q4:Thankful.=No Answer,"

        if Q5 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q5:Scared.=Not at all,"
        elif Q5 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q5:Scared.=Only a little,"
        elif Q5 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q5:Scared.=Sometimes,"
        elif Q5 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q5:Scared.=Often,"
        elif Q5 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q5:Scared.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q5:Scared.=No Answer,"

        if Q6 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q6:Looking forward to something.=Not at all,"
        elif Q6 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q6:Looking forward to something.=Only a little,"
        elif Q6 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q6:Looking forward to something.=Sometimes,"
        elif Q6 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q6:Looking forward to something.=Often,"
        elif Q6 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q6:Looking forward to something.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q6:Looking forward to something.=No Answer,"

        if Q7 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q7:Mad.=Not at all,"
        elif Q7 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q7:Mad.=Only a little,"
        elif Q7 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q7:Mad.=Sometimes,"
        elif Q7 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q7:Mad.=Often,"
        elif Q7 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q7:Mad.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q7:Mad.=No Answer,"

        if Q8 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q8:Safe.=Not at all,"
        elif Q8 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q8:Safe.=Only a little,"
        elif Q8 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q8:Safe.=Sometimes,"
        elif Q8 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q8:Safe.=Often,"
        elif Q8 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q8:Safe.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q8:Safe.=No Answer,"

        if Q9 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q9:Calm and peaceful.=Not at all,"
        elif Q9 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q9:Calm and peaceful.=Only a little,"
        elif Q9 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q9:Calm and peaceful.=Sometimes,"
        elif Q9 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q9:Calm and peaceful.=Often,"
        elif Q9 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q9:Calm and peaceful.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q9:Calm and peaceful.=No Answer,"

        if Q10 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q10:Worried.=Not at all,"
        elif Q10 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q10:Worried.=Only a little,"
        elif Q10 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q10:Worried.=Sometimes,"
        elif Q10 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q10:Worried.=Often,"
        elif Q10 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q10:Worried.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q10:Worried.=No Answer,"

        if Q11 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q11:Happy.=Not at all,"
        elif Q11 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q11:Happy.=Only a little,"
        elif Q11 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q11:Happy.=Sometimes,"
        elif Q11 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q11:Happy.=Often,"
        elif Q11 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q11:Happy.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q11:Happy.=No Answer,"

        if Q12 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q12:Feeling good with how things are.=Not at all,"
        elif Q12 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q12:Feeling good with how things are.=Only a little,"
        elif Q12 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q12:Feeling good with how things are.=Sometimes,"
        elif Q12 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q12:Feeling good with how things are.=Often,"
        elif Q12 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q12:Feeling good with how things are.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q12:Feeling good with how things are.=No Answer,"

        #if Q13 == "Not at all": 
        #    Q_happy_feelings = Q_happy_feelings + 0
        #    Q_total = Q_total + 0
        #    Q_rawdata = Q_rawdata + "Q13:Very excited.=Not at all,"
        #elif Q13 == "Only a little":
        #    Q_happy_feelings = Q_happy_feelings + 1
        #    Q_total = Q_total + 1
        #    Q_rawdata = Q_rawdata + "Q13:Very excited.=Only a little,"
        #elif Q13 == "Sometimes":
        #    Q_happy_feelings = Q_happy_feelings + 2
        #    Q_total = Q_total + 2
        #    Q_rawdata = Q_rawdata + "Q13:Very excited.=Sometimes,"
        #elif Q13 == "Often":
        #    Q_happy_feelings = Q_happy_feelings + 3
        #    Q_total = Q_total + 3
        #    Q_rawdata = Q_rawdata + "Q13:Very excited.=Often,"
        #elif Q13 == "A lot of the time (almost always)":
        #    Q_happy_feelings = Q_happy_feelings + 4
        #    Q_total = Q_total + 4
        #    Q_rawdata = Q_rawdata + "Q13:Very excited.=A lot of the time (almost always),"
        #else:
        #    Q_rawdata = Q_rawdata + "Q13:Very excited.=No Answer,"

        if Q13 == "Not at all": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q13:I believe many people do not like me.=Not at all,"
        elif Q13 == "Only a little":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q13:I believe many people do not like me.=Only a little,"
        elif Q13 == "Sometimes":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q13:I believe many people do not like me.=Sometimes,"
        elif Q13 == "Often":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q13:I believe many people do not like me.=Often,"
        elif Q13 == "A lot of the time (almost always)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q13:I believe many people do not like me.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q13:I believe many people do not like me.=No Answer,"

        if Q14 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q14:Uncomfortable or nervous.=Not at all,"
        elif Q14 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q14:Uncomfortable or nervous.=Only a little,"
        elif Q14 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q14:Uncomfortable or nervous.=Sometimes,"
        elif Q14 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q14:Uncomfortable or nervous.=Often,"
        elif Q14 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q14:Uncomfortable or nervous.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q14:Uncomfortable or nervous.=No Answer,"

        if Q15 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q15:Really disliking other people.=Not at all,"
        elif Q15 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q15:Really disliking other people.=Only a little,"
        elif Q15 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q15:Really disliking other people.=Sometimes,"
        elif Q15 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q15:Really disliking other people.=Often,"
        elif Q15 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q15:Really disliking other people.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q15:Really disliking other people.=No Answer,"

        if Q16 == "Not at all": 
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q16:Friendly.=Not at all,"
        elif Q16 == "Only a little":
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q16:Friendly.=Only a little,"
        elif Q16 == "Sometimes":
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q16:Friendly.=Sometimes,"
        elif Q16 == "Often":
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q16:Friendly.=Often,"
        elif Q16 == "A lot of the time (almost always)":
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q16:Friendly.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q16:Friendly.=No Answer,"

        if Q17 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q17:Rested and full of energy.=Not at all,"
        elif Q17 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q17:Rested and full of energy.=Only a little,"
        elif Q17 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q17:Rested and full of energy.=Sometimes,"
        elif Q17 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q17:Rested and full of energy.=Often,"
        elif Q17 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q17:Rested and full of energy.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q17:Rested and full of energy.=No Answer,"

        if Q18 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q18:Relaxed.=Not at all,"
        elif Q18 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q18:Relaxed.=Only a little,"
        elif Q18 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q18:Relaxed.=Sometimes,"
        elif Q18 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q18:Relaxed.=Often,"
        elif Q18 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q18:Relaxed.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q18:Relaxed.=No Answer,"

        if Q19 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q19:Crying a lot.=Not at all,"
        elif Q19 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q19:Crying a lot.=Only a little,"
        elif Q19 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q19:Crying a lot.=Sometimes,"
        elif Q19 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q19:Crying a lot.=Often,"
        elif Q19 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q19:Crying a lot.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q19:Crying a lot.=No Answer,"

        if Q20 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q20:Tired.=Not at all,"
        elif Q20 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q20:Tired.=Only a little,"
        elif Q20 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q20:Tired.=Sometimes,"
        elif Q20 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q20:Tired.=Often,"
        elif Q20 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q20:Tired.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q20:Tired.=No Answer,"

        if Q21 == "Not at all": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q21:Lonely.=Not at all,"
        elif Q21 == "Only a little":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q21:Lonely.=Only a little,"
        elif Q21 == "Sometimes":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q21:Lonely.=Sometimes,"
        elif Q21 == "Often":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q21:Lonely.=Often,"
        elif Q21 == "A lot of the time (almost always)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q21:Lonely.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q21:Lonely.=No Answer,"

        if Q22 == "Not at all": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q22:Laughing with others.=Not at all,"
        elif Q22 == "Only a little":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q22:Laughing with others.=Only a little,"
        elif Q22 == "Sometimes":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q22:Laughing with others.=Sometimes,"
        elif Q22 == "Often":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q22:Laughing with others.=Often,"
        elif Q22 == "A lot of the time (almost always)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q22:Laughing with others.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q22:Laughing with others.=No Answer,"

        if Q23 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q23:Like I wanted to cry.=Not at all,"
        elif Q23 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q23:Like I wanted to cry.=Only a little,"
        elif Q23 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q23:Like I wanted to cry.=Sometimes,"
        elif Q23 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q23:Like I wanted to cry.=Often,"
        elif Q23 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q23:Like I wanted to cry.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q23:Like I wanted to cry.=No Answer,"

        if Q24 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q24:Hopeful.=Not at all,"
        elif Q24 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q24:Hopeful.=Only a little,"
        elif Q24 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q24:Hopeful.=Sometimes,"
        elif Q24 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q24:Hopeful.=Often,"
        elif Q24 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q24:Hopeful.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q24:Hopeful.=No Answer,"

        if Q25 == "Not at all": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q25:Liked.=Not at all,"
        elif Q25 == "Only a little":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q25:Liked.=Only a little,"
        elif Q25 == "Sometimes":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q25:Liked.=Sometimes,"
        elif Q25 == "Often":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q25:Liked.=Often,"
        elif Q25 == "A lot of the time (almost always)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q25:Liked.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q25:Liked.=No Answer,"

        if Q26 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q26:Sad.=Not at all,"
        elif Q26 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q26:Sad.=Only a little,"
        elif Q26 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q26:Sad.=Sometimes,"
        elif Q26 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q26:Sad.=Often,"
        elif Q26 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q26:Sad.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q26:Sad.=No Answer,"

        if Q27 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q27:Jealous (wanting what others have).=Not at all,"
        elif Q27 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q27:Jealous (wanting what others have).=Only a little,"
        elif Q27 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q27:Jealous (wanting what others have).=Sometimes,"
        elif Q27 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q27:Jealous (wanting what others have).=Often,"
        elif Q27 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q27:Jealous (wanting what others have).=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q27:Jealous (wanting what others have).=No Answer,"

        if Q28 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q28:In a bad mood.=Not at all,"
        elif Q28 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q28:In a bad mood.=Only a little,"
        elif Q28 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q28:In a bad mood.=Sometimes,"
        elif Q28 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q28:In a bad mood.=Often,"
        elif Q28 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q28:In a bad mood.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q28:In a bad mood.=No Answer,"

        if Q29 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q29:Others are better than you.=Not at all,"
        elif Q29 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q29:Others are better than you.=Only a little,"
        elif Q29 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q29:Others are better than you.=Sometimes,"
        elif Q29 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q29:Others are better than you.=Often,"
        elif Q29 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q29:Others are better than you.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q29:Others are better than you.=No Answer,"

        if Q30 == "Not at all": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q30:Part of a group.=Not at all,"
        elif Q30 == "Only a little":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q30:Part of a group.=Only a little,"
        elif Q30 == "Sometimes":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q30:Part of a group.=Sometimes,"
        elif Q30 == "Often":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q30:Part of a group.=Often,"
        elif Q30 == "A lot of the time (almost always)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q30:Part of a group.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q30:Part of a group.=No Answer,"

        if Q31 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q31:Liking myself.=Not at all,"
        elif Q31 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q31:Liking myself.=Only a little,"
        elif Q31 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q31:Liking myself.=Sometimes,"
        elif Q31 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q31:Liking myself.=Often,"
        elif Q31 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q31:Liking myself.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q31:Liking myself.=No Answer,"

        if Q32 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q32:Having good choices.=Not at all,"
        elif Q32 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q32:Having good choices.=Only a little,"
        elif Q32 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q32:Having good choices.=Sometimes,"
        elif Q32 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q32:Having good choices.=Often,"
        elif Q32 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q32:Having good choices.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q32:Having good choices.=No Answer,"

        if Q33 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q33:Interested in learning new things.=Not at all,"
        elif Q33 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q33:Interested in learning new things.=Only a little,"
        elif Q33 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q33:Interested in learning new things.=Sometimes,"
        elif Q33 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q33:Interested in learning new things.=Often,"
        elif Q33 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q33:Interested in learning new things.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q33:Interested in learning new things.=No Answer,"

        if Q34 == "Not at all": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q34:Hurt by other people.=Not at all,"
        elif Q34 == "Only a little":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q34:Hurt by other people.=Only a little,"
        elif Q34 == "Sometimes":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q34:Hurt by other people.=Sometimes,"
        elif Q34 == "Often":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q34:Hurt by other people.=Often,"
        elif Q34 == "A lot of the time (almost always)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q34:Hurt by other people.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q35:Hurt by other people.=No Answer,"

        if Q35 == "Not at all": 
            Q_isolation = Q_isolation + 0
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q35:Picked on or made fun of.=Not at all,"
        elif Q35 == "Only a little":
            Q_isolation = Q_isolation + 1
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q35:Picked on or made fun of.=Only a little,"
        elif Q35 == "Sometimes":
            Q_isolation = Q_isolation + 2
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q35:Picked on or made fun of.=Sometimes,"
        elif Q35 == "Often":
            Q_isolation = Q_isolation + 3
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q35:Picked on or made fun of.=Often,"
        elif Q35 == "A lot of the time (almost always)":
            Q_isolation = Q_isolation + 4
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q35:Picked on or made fun of.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q35:Picked on or made fun of.=No Answer,"

        if Q36 == "Not at all": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q36:Understood.=Not at all,"
        elif Q36 == "Only a little":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q36:Understood.=Only a little,"
        elif Q36 == "Sometimes":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q36:Understood.=Sometimes,"
        elif Q36 == "Often":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q36:Understood.=Often,"
        elif Q36 == "A lot of the time (almost always)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q36:Understood.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q36:Understood.=No Answer,"

        if Q37 == "Not at all": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q37:Loved.=Not at all,"
        elif Q37 == "Only a little":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q37:Loved.=Only a little,"
        elif Q37 == "Sometimes":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q37:Loved.=Sometimes,"
        elif Q37 == "Often":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q37:Loved.=Often,"
        elif Q37 == "A lot of the time (almost always)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q37:Loved.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q37:Loved.=No Answer,"

        #if Q38 == "Not at all": 
        #    Q_happy_feelings = Q_happy_feelings + 0
        #    Q_total = Q_total + 0
        #    Q_rawdata = Q_rawdata + "Q38:Happy.=Not at all,"
        #elif Q38 == "Only a little":
        #    Q_happy_feelings = Q_happy_feelings + 1
        #    Q_total = Q_total + 1
        #    Q_rawdata = Q_rawdata + "Q38:Happy.=Only a little,"
        #elif Q38 == "Sometimes":
        #    Q_happy_feelings = Q_happy_feelings + 2
        #    Q_total = Q_total + 2
        #    Q_rawdata = Q_rawdata + "Q38:Happy.=Sometimes,"
        #elif Q38 == "Often":
        #    Q_happy_feelings = Q_happy_feelings + 3
        #    Q_total = Q_total + 3
        #    Q_rawdata = Q_rawdata + "Q38:Happy.=Often,"
        #elif Q38 == "A lot of the time (almost always)":
        #    Q_happy_feelings = Q_happy_feelings + 4
        #    Q_total = Q_total + 4
        #    Q_rawdata = Q_rawdata + "Q38:Happy.=A lot of the time (almost always),"
        #else:
        #    Q_rawdata = Q_rawdata + "Q38:Happy.=No Answer,"

        if Q38 == "Not at all": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q38:Left out.=Not at all,"
        elif Q38 == "Only a little":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q38:Left out.=Only a little,"
        elif Q38 == "Sometimes":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q38:Left out.=Sometimes,"
        elif Q38 == "Often":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q38:Left out.=Often,"
        elif Q38 == "A lot of the time (almost always)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q38:Left out.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q38:Left out.=No Answer,"

        if Q39 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q39:Proud of myself.=Not at all,"
        elif Q39 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q39:Proud of myself.=Only a little,"
        elif Q39 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q39:Proud of myself.=Sometimes,"
        elif Q39 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q39:Proud of myself.=Often,"
        elif Q39 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q39:Proud of myself.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q39:Proud of myself.=No Answer,"    

        if Q40 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q40:Wishing I was someone else.=Not at all,"
        elif Q40 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q40:Wishing I was someone else.=Only a little,"
        elif Q40 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q40:Wishing I was someone else.=Sometimes,"
        elif Q40 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q40:Wishing I was someone else.=Often,"
        elif Q40 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q40:Wishing I was someone else.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q41:Wishing I was someone else.=No Answer,"

        if Q41 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q41:Wishing I wasn’t here anymore.=Not at all,"
        elif Q41 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q41:Wishing I wasn’t here anymore.=Only a little,"
        elif Q41 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q41:Wishing I wasn’t here anymore.=Sometimes,"
        elif Q41 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q41:Wishing I wasn’t here anymore.=Often,"
        elif Q41 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q41:Wishing I wasn’t here anymore.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q41:Wishing I wasn’t here anymore.=No Answer,"

        Q_total = Q_connection + Q_inclusion + Q_happy_feelings - Q_isolation - Q_bad_feelings

        if Q_total >= 20:
            st.write(f"#### Total Score: {Q_total}")
            Q_response = "Thriving, strong emotional reserves and high resilience."
        elif Q_total >= 0 and Q_total <= 19:
            st.write(f"#### Total Score: {Q_total}")
            Q_response = "Stable, typical emotional ups and downs."
        elif Q_total >= -10 and Q_total <= -1:
            st.write(f"#### Total Score: {Q_total}")
            Q_response = "At Risk, the child is experiencing more distress than joy."
        elif Q_total <= -11:
            st.write(f"#### Total Score: {Q_total}")
            Q_response = "High Distress, may require immediate clinical or school intervention."

        st.write(f"#### Score Interpretation: {Q_response}")

        if (Q35 == "Often" or Q35 == "A lot of the time (almost always)") and Q_connection >= 14:
            st.write(f"**The Victimization Gap** - Question 35 is high ({Q35}) and the Connection Score ({Q_connection}) is also high. *Recommendation*: Investigate \"toxic\" friendships or bullying within a close group.")
        if (Q20 == "Often" or Q20 == "A lot of the time (almost always)") and Q17 == "Not at all":
            st.write(f"**The Exhaustion Marker** - Question 20 (Tired) is high ({Q20}), but Question 17 (Rested) is \"Not at all\". *Recommendation*: Consider screening for sleep issues or high-level environmental stress.")
        if (Q_connection + Q_inclusion + Q_happy_feelings + Q_isolation + Q_bad_feelings) == 0:
            st.write(f"**Skewed Responding** - the test taker answered \"Not at all\" for every single item. The results may be invalid due to \"all-or-nothing\" thinking or a lack of engagement with the questions.")
        elif (Q_connection + Q_inclusion + Q_happy_feelings + Q_isolation + Q_bad_feelings) == 196:
            st.write(f"**Skewed Responding** - the test taker answered \"A lot of the time (almost always)\" for every single item. The results may be invalid due to \"all-or-nothing\" thinking or a lack of engagement with the questions.")
        
        st.markdown("For additional information and resources, please visit: [US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")
        Q_rawdata = Q_rawdata + "Score=" + str(Q_total)

    #-------------------------------------------------------------------
    # TOOL SCORING
    # TOOL: My Feelings and Needs, NEIL Child Version, in Spanish
    #-------------------------------------------------------------------

    if submit2 and language == "Spanish":
        Q_connection = 0
        Q_inclusion = 0
        Q_isolation = 0
        Q_happy_feelings = 0
        Q_bad_feelings = 0
        Q_total = 0
        Q_response = ""
        Q_rawdata = name + "," + str(age) + ","

        # Connection Score is total from questions 1, 2, 22, 25, 30, 36, 37.
        # Inclusion Score is total from questions 1, 2, 16, 22, 25, 30, 36, 37.
        # Isolation Score is total from questions 13, 21, 34, 35, 38.
        # Happy Feelings Score is total from questions 3, 4, 6, 8, 9, 11, 12, 17, 18, 24, 31, 32, 33, 39.
        # Scores for bad feelings (questions 5, 7, 10, 14, 15, 19, 20, 23, 26, 27, 28, 29, 35) and 
        # isoluation (questions 13, 21, 34, 35, 38) will be subtracted from other question totals.
        if Q1 == "Para nada": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q1:Otras personas me incluyeron.=Para nada,"
        elif Q1 == "Solo un poco":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q1:Otras personas me incluyeron.=Solo un poco,"
        elif Q1 == "A veces":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q1:Otras personas me incluyeron.=A veces,"
        elif Q1 == "Seguido":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q1:Otras personas me incluyeron.=Seguido,"
        elif Q1 == "Mucho del tiempo (casi siempre)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q1:Otras personas me incluyeron.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q1:Otras personas me incluyeron.=No Contesta,"

        if Q2 == "Para nada": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q2:Otros quieren estar conmigo.=Para nada,"
        elif Q2 == "Solo un poco":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q2:Otros quieren estar conmigo.=Solo un poco,"
        elif Q2 == "A veces":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q2:Otros quieren estar conmigo.=A veces,"
        elif Q2 == "Seguido":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q2:Otros quieren estar conmigo.=Seguido,"
        elif Q2 == "Mucho del tiempo (casi siempre)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q2:Otros quieren estar conmigo.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q2:Otros quieren estar conmigo.=No Contesta,"

        if Q3 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q3:Sorprendido(a).=Para nada,"
        elif Q3 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q3:Sorprendido(a).=Solo un poco,"
        elif Q3 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q3:Sorprendido(a).=A veces,"
        elif Q3 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q3:Sorprendido(a).=Seguido,"
        elif Q3 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q3:Sorprendido(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q3:Sorprendido(a).=No Contesta,"

        if Q4 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q4:Agradecido(a).=Para nada,"
        elif Q4 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q4:Agradecido(a).=Solo un poco,"
        elif Q4 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q4:Agradecido(a).=A veces,"
        elif Q4 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q4:Agradecido(a).=Seguido,"
        elif Q4 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q4:Agradecido(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q4:Agradecido(a).=No Contesta,"

        if Q5 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q5:Con miedo.=Para nada,"
        elif Q5 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q5:Con miedo.=Solo un poco,"
        elif Q5 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q5:Con miedo.=A veces,"
        elif Q5 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q5:Con miedo.=Seguido,"
        elif Q5 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q5:Con miedo.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q5:Con miedo.=No Contesta,"

        if Q6 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q6:Con ganas de que pase algo bueno.=Para nada,"
        elif Q6 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q6:Con ganas de que pase algo bueno.=Solo un poco,"
        elif Q6 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q6:Con ganas de que pase algo bueno.=A veces,"
        elif Q6 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q6:Con ganas de que pase algo bueno.=Seguido,"
        elif Q6 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q6:Con ganas de que pase algo bueno.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q6:Con ganas de que pase algo bueno.=No Contesta,"

        if Q7 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q7:Enojado(a) o molesto(a).=Para nada,"
        elif Q7 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q7:Enojado(a) o molesto(a).=Solo un poco,"
        elif Q7 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q7:Enojado(a) o molesto(a).=A veces,"
        elif Q7 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q7:Enojado(a) o molesto(a).=Seguido,"
        elif Q7 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q7:Enojado(a) o molesto(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q7:Enojado(a) o molesto(a).=No Contesta,"

        if Q8 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q8:Seguro(a).=Para nada,"
        elif Q8 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q8:Seguro(a).=Solo un poco,"
        elif Q8 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q8:Seguro(a).=A veces,"
        elif Q8 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q8:Seguro(a).=Seguido,"
        elif Q8 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q8:Seguro(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q8:Seguro(a).=No Contesta,"

        if Q9 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q9:Tranquilo(a) y en paz.=Para nada,"
        elif Q9 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q9:Tranquilo(a) y en paz.=Solo un poco,"
        elif Q9 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q9:Tranquilo(a) y en paz.=A veces,"
        elif Q9 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q9:Tranquilo(a) y en paz.=Seguido,"
        elif Q9 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q9:Tranquilo(a) y en paz.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q9:Tranquilo(a) y en paz.=No Contesta,"

        if Q10 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q10:Preocupado(a).=Para nada,"
        elif Q10 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q10:Preocupado(a).=Solo un poco,"
        elif Q10 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q10:Preocupado(a).=A veces,"
        elif Q10 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q10:Preocupado(a).=Seguido,"
        elif Q10 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q10:Preocupado(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q10:Preocupado(a).=No Contesta,"

        if Q11 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q11:Feliz.=Para nada,"
        elif Q11 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q11:Feliz.=Solo un poco,"
        elif Q11 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q11:Feliz.=A veces,"
        elif Q11 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q11:Feliz.=Seguido,"
        elif Q11 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q11:Feliz.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q11:Feliz.=No Contesta,"

        if Q12 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q12:Siento bien con cómo están las cosas.=Para nada,"
        elif Q12 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q12:Siento bien con cómo están las cosas.=Solo un poco,"
        elif Q12 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q12:Siento bien con cómo están las cosas.=A veces,"
        elif Q12 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q12:Siento bien con cómo están las cosas.=Seguido,"
        elif Q12 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q12:Siento bien con cómo están las cosas.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q12:Siento bien con cómo están las cosas.=No Contesta,"

        #if Q13 == "Para nada": 
        #    Q_happy_feelings = Q_happy_feelings + 0
        #    Q_total = Q_total + 0
        #    Q_rawdata = Q_rawdata + "Q13:Súper emocionado(a).=Para nada,"
        #elif Q13 == "Solo un poco":
        #    Q_happy_feelings = Q_happy_feelings + 1
        #    Q_total = Q_total + 1
        #    Q_rawdata = Q_rawdata + "Q13:Súper emocionado(a).=Solo un poco,"
        #elif Q13 == "A veces":
        #    Q_happy_feelings = Q_happy_feelings + 2
        #    Q_total = Q_total + 2
        #    Q_rawdata = Q_rawdata + "Q13:Súper emocionado(a).=A veces,"
        #elif Q13 == "Seguido":
        #    Q_happy_feelings = Q_happy_feelings + 3
        #    Q_total = Q_total + 3
        #    Q_rawdata = Q_rawdata + "Q13:Súper emocionado(a).=Seguido,"
        #elif Q13 == "Mucho del tiempo (casi siempre)":
        #    Q_happy_feelings = Q_happy_feelings + 4
        #    Q_total = Q_total + 4
        #    Q_rawdata = Q_rawdata + "Q13:Súper emocionado(a).=Mucho del tiempo (casi siempre),"
        #else:
        #    Q_rawdata = Q_rawdata + "Q13:Súper emocionado(a).=No Contesta,"

        if Q13 == "Para nada": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q13:Siento que no le caía bien a la gente.=Para nada,"
        elif Q13 == "Solo un poco":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q13:Siento que no le caía bien a la gente.=Solo un poco,"
        elif Q13 == "A veces":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q13:Siento que no le caía bien a la gente.=A veces,"
        elif Q13 == "Seguido":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q13:Siento que no le caía bien a la gente.=Seguido,"
        elif Q13 == "Mucho del tiempo (casi siempre)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q13:Siento que no le caía bien a la gente.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q13:Siento que no le caía bien a la gente.=No Contesta,"

        if Q14 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q14:Incómodo(a) o nervioso(a).=Para nada,"
        elif Q14 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q14:Incómodo(a) o nervioso(a).=Solo un poco,"
        elif Q14 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q14:Incómodo(a) o nervioso(a).=A veces,"
        elif Q14 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q14:Incómodo(a) o nervioso(a).=Seguido,"
        elif Q14 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q14:Incómodo(a) o nervioso(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q15:Incómodo(a) o nervioso(a).=No Contesta,"

        if Q15 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q15:Siento que me caen mal los demás.=Para nada,"
        elif Q15 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q15:Siento que me caen mal los demás.=Solo un poco,"
        elif Q15 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q15:Siento que me caen mal los demás.=A veces,"
        elif Q15 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q15:Siento que me caen mal los demás.=Seguido,"
        elif Q15 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q15:Siento que me caen mal los demás.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q15:Siento que me caen mal los demás.=No Contesta,"

        if Q16 == "Para nada": 
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q16:Amigable.=Para nada,"
        elif Q16 == "Solo un poco":
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q16:Amigable.=Solo un poco,"
        elif Q16 == "A veces":
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q16:Amigable.=A veces,"
        elif Q16 == "Seguido":
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q16:Amigable.=Seguido,"
        elif Q16 == "Mucho del tiempo (casi siempre)":
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q16:Amigable.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q16:Amigable.=No Contesta,"

        if Q17 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q17:Descansado(a) y con mucha energía.=Para nada,"
        elif Q17 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q17:Descansado(a) y con mucha energía.=Solo un poco,"
        elif Q17 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q17:Descansado(a) y con mucha energía.=A veces,"
        elif Q17 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q17:Descansado(a) y con mucha energía.=Seguido,"
        elif Q17 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q17:Descansado(a) y con mucha energía.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q17:Descansado(a) y con mucha energía.=No Contesta,"

        if Q18 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q18:Relajado(a).=Para nada,"
        elif Q18 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q18:Relajado(a).=Solo un poco,"
        elif Q18 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q18:Relajado(a).=A veces,"
        elif Q18 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q18:Relajado(a).=Seguido,"
        elif Q18 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q18:Relajado(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q18:Relajado(a).=No Contesta,"

        if Q19 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q19:Llorando mucho.=Para nada,"
        elif Q19 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q19:Llorando mucho.=Solo un poco,"
        elif Q19 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q19:Llorando mucho.=A veces,"
        elif Q19 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q19:Llorando mucho.=Seguido,"
        elif Q19 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q19:Llorando mucho.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q19:Llorando mucho.=No Contesta,"

        if Q20 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q20:Cansado(a).=Para nada,"
        elif Q20 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q20:Cansado(a).=Solo un poco,"
        elif Q20 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q20:Cansado(a).=A veces,"
        elif Q20 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q20:Cansado(a).=Seguido,"
        elif Q20 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q20:Cansado(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q20:Cansado(a).=No Contesta,"

        if Q21 == "Para nada": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q21:Solo(a).=Para nada,"
        elif Q21 == "Solo un poco":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q21:Solo(a).=Solo un poco,"
        elif Q21 == "A veces":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q21:Solo(a).=A veces,"
        elif Q21 == "Seguido":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q21:Solo(a).=Seguido,"
        elif Q21 == "Mucho del tiempo (casi siempre)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q21:Solo(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q21:Solo(a).=No Contesta,"

        if Q22 == "Para nada": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q22:Riendo con otros.=Para nada,"
        elif Q22 == "Solo un poco":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q22:Riendo con otros.=Solo un poco,"
        elif Q22 == "A veces":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q22:Riendo con otros.=A veces,"
        elif Q22 == "Seguido":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q22:Riendo con otros.=Seguido,"
        elif Q22 == "Mucho del tiempo (casi siempre)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q22:Riendo con otros.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q22:Riendo con otros.=No Contesta,"

        if Q23 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q23:Con ganas de llorar.=Para nada,"
        elif Q23 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q23:Con ganas de llorar.=Solo un poco,"
        elif Q23 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q23:Con ganas de llorar.=A veces,"
        elif Q23 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q23:Con ganas de llorar.=Seguido,"
        elif Q23 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q23:Con ganas de llorar.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q23:Con ganas de llorar.=No Contesta,"

        if Q24 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q24:Con esperanza.=Para nada,"
        elif Q24 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q24:Con esperanza.=Solo un poco,"
        elif Q24 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q24:Con esperanza.=A veces,"
        elif Q24 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q24:Con esperanza.=Seguido,"
        elif Q24 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q24:Con esperanza.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q24:Con esperanza.=No Contesta,"

        if Q25 == "Para nada": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q25:Le agrado a los demás.=Para nada,"
        elif Q25 == "Solo un poco":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q25:Le agrado a los demás.=Solo un poco,"
        elif Q25 == "A veces":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q25:Le agrado a los demás.=A veces,"
        elif Q25 == "Seguido":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q25:Le agrado a los demás.=Seguido,"
        elif Q25 == "Mucho del tiempo (casi siempre)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q25:Le agrado a los demás.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q25:Le agrado a los demás.=No Contesta,"

        if Q26 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q26:Triste.=Para nada,"
        elif Q26 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q26:Triste.=Solo un poco,"
        elif Q26 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q26:Triste.=A veces,"
        elif Q26 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q26:Triste.=Seguido,"
        elif Q26 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q26:Triste.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q26:Triste.=No Contesta,"

        if Q27 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q27:Celoso(a) (queriendo lo que otros tienen).=Para nada,"
        elif Q27 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q27:Celoso(a) (queriendo lo que otros tienen).=Solo un poco,"
        elif Q27 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q27:Celoso(a) (queriendo lo que otros tienen).=A veces,"
        elif Q27 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q27:Celoso(a) (queriendo lo que otros tienen).=Seguido,"
        elif Q27 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q27:Celoso(a) (queriendo lo que otros tienen).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q27:Celoso(a) (queriendo lo que otros tienen).=No Contesta,"

        if Q28 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q28:De mal humor.=Para nada,"
        elif Q28 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q28:De mal humor.=Solo un poco,"
        elif Q28 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q28:De mal humor.=A veces,"
        elif Q28 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q28:De mal humor.=Seguido,"
        elif Q28 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q28:De mal humor.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q28:De mal humor.=No Contesta,"

        if Q29 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q29:Siento que otros son mejores que yo.=Para nada,"
        elif Q29 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q29:Siento que otros son mejores que yo.=Solo un poco,"
        elif Q29 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q29:Siento que otros son mejores que yo.=A veces,"
        elif Q29 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q29:Siento que otros son mejores que yo.=Seguido,"
        elif Q29 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q29:Siento que otros son mejores que yo.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q29:Siento que otros son mejores que yo.=No Contesta,"

        if Q30 == "Para nada": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q30:Parte de un grupo.=Para nada,"
        elif Q30 == "Solo un poco":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q30:Parte de un grupo.=Solo un poco,"
        elif Q30 == "A veces":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q30:Parte de un grupo.=A veces,"
        elif Q30 == "Seguido":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q30:Parte de un grupo.=Seguido,"
        elif Q30 == "Mucho del tiempo (casi siempre)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q30:Parte de un grupo.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q30:Parte de un grupo.=No Contesta,"

        if Q31 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q31:Gustarme a mí mismo(a).=Para nada,"
        elif Q31 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q31:Gustarme a mí mismo(a).=Solo un poco,"
        elif Q31 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q31:Gustarme a mí mismo(a).=A veces,"
        elif Q31 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q31:Gustarme a mí mismo(a).=Seguido,"
        elif Q31 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q31:Gustarme a mí mismo(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q31:Gustarme a mí mismo(a).=No Contesta,"

        if Q32 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q32:Tengo buenas opciones.=Para nada,"
        elif Q32 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q32:Tengo buenas opciones.=Solo un poco,"
        elif Q32 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q32:Tengo buenas opciones.=A veces,"
        elif Q32 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q32:Tengo buenas opciones.=Seguido,"
        elif Q32 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q32:Tengo buenas opciones.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q32:Tengo buenas opciones.=No Contesta,"

        if Q33 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q33:Con ganas de aprender cosas nuevas.=Para nada,"
        elif Q33 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q33:Con ganas de aprender cosas nuevas.=Solo un poco,"
        elif Q33 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q33:Con ganas de aprender cosas nuevas.=A veces,"
        elif Q33 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q33:Con ganas de aprender cosas nuevas.=Seguido,"
        elif Q33 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q33:Con ganas de aprender cosas nuevas.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q33:Con ganas de aprender cosas nuevas.=No Contesta,"

        if Q34 == "Para nada": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q34:Lastimado(a) por otras personas.=Para nada,"
        elif Q34 == "Solo un poco":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q34:Lastimado(a) por otras personas.=Solo un poco,"
        elif Q34 == "A veces":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q34:Lastimado(a) por otras personas.=A veces,"
        elif Q34 == "Seguido":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q34:Lastimado(a) por otras personas.=Seguido,"
        elif Q34 == "Mucho del tiempo (casi siempre)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q34:Lastimado(a) por otras personas.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q34:Lastimado(a) por otras personas.=No Contesta,"

        if Q35 == "Para nada": 
            Q_isolation = Q_isolation + 0
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q35:Molestado(a) o que se burlan de mí.=Para nada,"
        elif Q35 == "Solo un poco":
            Q_isolation = Q_isolation + 1
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q35:Molestado(a) o que se burlan de mí.=Solo un poco,"
        elif Q35 == "A veces":
            Q_isolation = Q_isolation + 2
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q35:Molestado(a) o que se burlan de mí.=A veces,"
        elif Q35 == "Seguido":
            Q_isolation = Q_isolation + 3
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q35:Molestado(a) o que se burlan de mí.=Seguido,"
        elif Q35 == "Mucho del tiempo (casi siempre)":
            Q_isolation = Q_isolation + 4
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q35:Molestado(a) o que se burlan de mí.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q35:Molestado(a) o que se burlan de mí.=No Contesta,"

        if Q36 == "Para nada": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q36:Comprendido(a).=Para nada,"
        elif Q36 == "Solo un poco":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q36:Comprendido(a).=Solo un poco,"
        elif Q36 == "A veces":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q36:Comprendido(a).=A veces,"
        elif Q36 == "Seguido":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q36:Comprendido(a).=Seguido,"
        elif Q36 == "Mucho del tiempo (casi siempre)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q36:Comprendido(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q36:Comprendido(a).=No Contesta,"

        if Q37 == "Para nada": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q37:Amado(a).=Para nada,"
        elif Q37 == "Solo un poco":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q37:Amado(a).=Solo un poco,"
        elif Q37 == "A veces":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q37:Amado(a).=A veces,"
        elif Q37 == "Seguido":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q37:Amado(a).=Seguido,"
        elif Q37 == "Mucho del tiempo (casi siempre)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q37:Amado(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q37:Amado(a).=No Contesta,"

        #if Q38 == "Para nada": 
        #    Q_happy_feelings = Q_happy_feelings + 0
        #    Q_total = Q_total + 0
        #    Q_rawdata = Q_rawdata + "Q38:Feliz.=Para nada,"
        #elif Q38 == "Solo un poco":
        #    Q_happy_feelings = Q_happy_feelings + 1
        #    Q_total = Q_total + 1
        #    Q_rawdata = Q_rawdata + "Q38:Feliz.=Solo un poco,"
        #elif Q38 == "A veces":
        #    Q_happy_feelings = Q_happy_feelings + 2
        #    Q_total = Q_total + 2
        #    Q_rawdata = Q_rawdata + "Q38:Feliz.=A veces,"
        #elif Q38 == "Seguido":
        #    Q_happy_feelings = Q_happy_feelings + 3
        #    Q_total = Q_total + 3
        #    Q_rawdata = Q_rawdata + "Q38:Feliz.=Seguido,"
        #elif Q38 == "Mucho del tiempo (casi siempre)":
        #    Q_happy_feelings = Q_happy_feelings + 4
        #    Q_total = Q_total + 4
        #    Q_rawdata = Q_rawdata + "Q38:Feliz.=Mucho del tiempo (casi siempre),"
        #else:
        #    Q_rawdata = Q_rawdata + "Q38:Feliz.=No Contesta,"

        if Q38 == "Para nada": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q38:Dejado(a) fuera.=Para nada,"
        elif Q38 == "Solo un poco":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q38:Dejado(a) fuera.=Solo un poco,"
        elif Q38 == "A veces":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q38:Dejado(a) fuera.=A veces,"
        elif Q38 == "Seguido":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q38:Dejado(a) fuera.=Seguido,"
        elif Q38 == "Mucho del tiempo (casi siempre)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q38:Dejado(a) fuera.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q38:Dejado(a) fuera.=No Contesta,"

        if Q39 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q39:Orgulloso(a) de mí mismo(a).=Para nada,"
        elif Q39 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q39:Orgulloso(a) de mí mismo(a).=Solo un poco,"
        elif Q39 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q39:Orgulloso(a) de mí mismo(a).=A veces,"
        elif Q39 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q39:Orgulloso(a) de mí mismo(a).=Seguido,"
        elif Q39 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q39:Orgulloso(a) de mí mismo(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q39:Orgulloso(a) de mí mismo(a).=No Contesta,"    

        if Q40 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q40:Deseando ser otra persona.=Para nada,"
        elif Q40 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q40:Deseando ser otra persona.=Solo un poco,"
        elif Q40 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q40:Deseando ser otra persona.=A veces,"
        elif Q40 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q40:Deseando ser otra persona.=Seguido,"
        elif Q40 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q40:Deseando ser otra persona.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q40:Deseando ser otra persona.=No Contesta,"

        if Q41 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q41:Deseando ya no estar aquí.=Para nada,"
        elif Q41 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q41:Deseando ya no estar aquí.=Solo un poco,"
        elif Q41 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q41:Deseando ya no estar aquí.=A veces,"
        elif Q41 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q41:Deseando ya no estar aquí.=Seguido,"
        elif Q41 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q41:Deseando ya no estar aquí.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q41:Deseando ya no estar aquí.=No Contesta,"

        Q_total = Q_connection + Q_inclusion + Q_happy_feelings - Q_isolation - Q_bad_feelings

        if Q_total >= 20:
            st.write(f"#### Puntos Totales: {Q_total}")
            Q_response = "Prosperando, con fuertes reservas emocionales y alta resiliencia."
        elif Q_total >= 0 and Q_total <= 19:
            st.write(f"#### Puntos Totales: {Q_total}")
            Q_response = "Estables, altibajos emocionales típicos."
        elif Q_total >= -10 and Q_total <= -1:
            st.write(f"#### Puntos Totales: {Q_total}")
            Q_response = "En riesgo, el niño está experimentando más angustia que alegría."
        elif Q_total <= -11:
            st.write(f"#### Puntos Totales: {Q_total}")
            Q_response = "Alto nivel de angustia, puede requerir intervención clínica o escolar inmediata."

        st.write(f"#### Interpretación de la puntuación: {Q_response}")

        if (Q35 == "Seguido" or Q35 == "Mucho del tiempo (casi siempre)") and Q_connection >= 14:
            st.write(f"**La brecha de victimización** - La pregunta 35 es alta ({Q35}) y la Puntuación de Conexión ({Q_connection}) también es alta. *Recomendación*: Investigar las amistades \"tóxicas\" o el acoso dentro de un grupo cercano.")
        if (Q20 == "Seguido" or Q20 == "Mucho del tiempo (casi siempre)") and Q17 == "Para nada":
            st.write(f"**El marcador de agotamiento** - Pregunta 20 (Cansado) es alto ({Q20}), pero la Pregunta 17 (Descansado) es \"Para nada\". *Recomendación*: Considerar la evaluación de problemas de sueño o estrés ambiental elevado.")
        if (Q_connection + Q_inclusion + Q_happy_feelings + Q_isolation + Q_bad_feelings) == 0:
            st.write(f"**Respuesta Sesgada** - el evaluado respondió \"Para nada\" en cada ítem. Los resultados pueden ser inválidos debido a un pensamiento de \"todo o nada\" o a la falta de compromiso con las preguntas.")
        elif (Q_connection + Q_inclusion + Q_happy_feelings + Q_isolation + Q_bad_feelings) == 196:
            st.write(f"**Respuesta Sesgada** - el evaluado respondió \"Mucho del tiempo (casi siempre)\" en cada ítem. Los resultados pueden ser inválidos debido a un pensamiento de \"todo o nada\" o a la falta de compromiso con las preguntas.")
        
        st.markdown("Para más información y recursos, favor de visitar: [US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")
        Q_rawdata = Q_rawdata + "Score=" + str(Q_total)
        
    #-------------------------------------------------------------------
    # TOOL SCORING
    # TOOL: My Feelings and Needs, NEIL Adult Version
    #-------------------------------------------------------------------

    if submit3 and language == "English":
        Q_positive_well_being_resilience = 0
        Q_internal_psychological_somatic_distress = 0
        Q_social_support_security = 0
        Q_social_isolation_rejection = 0
        Q_total = 0

        Q_hopeful_sum = 0
        Q_despairing_sum = 0
        Q_outlook_balance = 0
        Q_included_sum = 0
        Q_isolated_sum = 0
        Q_social_connectivity_balance = 0
        
        Q_response = ""
        Q_rawdata = name + "," + str(age) + ","

        # Positive Well-Being & Resilience (15 items)
        # Items: 3, 5, 8, 10, 11, 12, 17, 18, 22, 24, 31, 33, 37, 39, 41
        # Total Max Score: 60
        #
        # Internal Psychological & Somatic Distress (14 items)
        # Items: 4, 6, 9, 14, 15, 19, 20, 23, 26, 27, 28, 29, 40, 42
        # Total Max Score: 56
        #
        # Social Support & Security (8 items)
        # Items: 1, 7, 16, 25, 30, 32, 35, 36
        # Total Max Score: 32
        #
        # Social Isolation & Rejection (4 items)
        # Items: 13, 21, 34, 38
        # Total Max Score: 16
        if Q1 == "Not at all": 
            Q_social_support_security = Q_social_support_security + 0
            Q_included_sum = Q_included_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q1:Included by others.=Not at all,"
        elif Q1 == "Only a little":
            Q_social_support_security = Q_social_support_security + 1
            Q_included_sum = Q_included_sum + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q1:Included by others.=Only a little,"
        elif Q1 == "Sometimes":
            Q_social_support_security = Q_social_support_security + 2
            Q_included_sum = Q_included_sum + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q1:Included by others.=Sometimes,"
        elif Q1 == "Often":
            Q_social_support_security = Q_social_support_security + 3
            Q_included_sum = Q_included_sum + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q1:Included by others.=Often,"
        elif Q1 == "A lot of the time (almost always)":
            Q_social_support_security = Q_social_support_security + 4
            Q_included_sum = Q_included_sum + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q1:Included by others.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q1:Included by others.=No Answer,"

        if Q2 == "Not at all": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q2:Surprised.=Not at all,"
        elif Q2 == "Only a little":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q2:Surprised.=Only a little,"
        elif Q2 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q2:Surprised.=Sometimes,"
        elif Q2 == "Often":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q2:Surprised.=Often,"
        elif Q2 == "A lot of the time (almost always)":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q2:Surprised.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q2:Surprised.=No Answer,"

        if Q3 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q3:Thankful.=Not at all,"
        elif Q3 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q3:Thankful.=Only a little,"
        elif Q3 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q3:Thankful.=Sometimes,"
        elif Q3 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q3:Thankful.=Often,"
        elif Q3 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q3:Thankful.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q3:Thankful.=No Answer,"

        if Q4 == "Not at all": 
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q4:Afraid.=Not at all,"
        elif Q4 == "Only a little":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q4:Afraid.=Only a little,"
        elif Q4 == "Sometimes":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q4:Afraid.=Sometimes,"
        elif Q4 == "Often":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q4:Afraid.=Often,"
        elif Q4 == "A lot of the time (almost always)":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q4:Afraid.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q4:Afraid.=No Answer,"

        if Q5 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_hopeful_sum = Q_hopeful_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q5:Looking forward to tomorrow.=Not at all,"
        elif Q5 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_hopeful_sum = Q_hopeful_sum + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q5:Looking forward to tomorrow.=Only a little,"
        elif Q5 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_hopeful_sum = Q_hopeful_sum + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q5:Looking forward to tomorrow.=Sometimes,"
        elif Q5 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_hopeful_sum = Q_hopeful_sum + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q5:Looking forward to tomorrow.=Often,"
        elif Q5 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_hopeful_sum = Q_hopeful_sum + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q5:Looking forward to tomorrow.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q5:Looking forward to tomorrow.=No Answer,"

        if Q6 == "Not at all": 
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q6:Angry.=Not at all,"
        elif Q6 == "Only a little":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q6:Angry.=Only a little,"
        elif Q6 == "Sometimes":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q6:Angry.=Sometimes,"
        elif Q6 == "Often":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q6:Angry.=Often,"
        elif Q6 == "A lot of the time (almost always)":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q6:Angry.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q6:Angry.=No Answer,"

        if Q7 == "Not at all": 
            Q_social_support_security = Q_social_support_security + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q7:Safe.=Not at all,"
        elif Q7 == "Only a little":
            Q_social_support_security = Q_social_support_security + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q7:Safe.=Only a little,"
        elif Q7 == "Sometimes":
            Q_social_support_security = Q_social_support_security + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q7:Safe.=Sometimes,"
        elif Q7 == "Often":
            Q_social_support_security = Q_social_support_security + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q7:Safe.=Often,"
        elif Q7 == "A lot of the time (almost always)":
            Q_social_support_security = Q_social_support_security + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q7:Safe.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q7:Safe.=No Answer,"

        if Q8 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q8:Calm.=Not at all,"
        elif Q8 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q8:Calm.=Only a little,"
        elif Q8 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q8:Calm.=Sometimes,"
        elif Q8 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q8:Calm.=Often,"
        elif Q8 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q8:Calm.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q8:Calm.=No Answer,"

        if Q9 == "Not at all": 
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q9:Worried.=Not at all,"
        elif Q9 == "Only a little":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q9:Worried.=Only a little,"
        elif Q9 == "Sometimes":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q9:Worried.=Sometimes,"
        elif Q9 == "Often":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q9:Worried.=Often,"
        elif Q9 == "A lot of the time (almost always)":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q9:Worried.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q9:Worried.=No Answer,"

        if Q10 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q10:Glad.=Not at all,"
        elif Q10 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q10:Glad.=Only a little,"
        elif Q10 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q10:Glad.=Sometimes,"
        elif Q10 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q10:Glad.=Often,"
        elif Q10 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q10:Glad.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q10:Glad.=No Answer,"

        if Q11 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q11:Satisfied.=Not at all,"
        elif Q11 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q11:Satisfied.=Only a little,"
        elif Q11 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q11:Satisfied.=Sometimes,"
        elif Q11 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q11:Satisfied.=Often,"
        elif Q11 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q11:Satisfied.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q11:Satisfied.=No Answer,"

        if Q12 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q12:Thrilled.=Not at all,"
        elif Q12 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q12:Thrilled.=Only a little,"
        elif Q12 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q12:Thrilled.=Sometimes,"
        elif Q12 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q12:Thrilled.=Often,"
        elif Q12 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q12:Thrilled.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q12:Thrilled.=No Answer,"

        if Q13 == "Not at all": 
            Q_social_isolation_rejection = Q_social_isolation_rejection + 0
            Q_isolated_sum = Q_isolated_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q13:Disliked.=Not at all,"
        elif Q13 == "Only a little":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 1
            Q_isolated_sum = Q_isolated_sum + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q13:Disliked.=Only a little,"
        elif Q13 == "Sometimes":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 2
            Q_isolated_sum = Q_isolated_sum + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q13:Disliked.=Sometimes,"
        elif Q13 == "Often":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 3
            Q_isolated_sum = Q_isolated_sum + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q13:Disliked.=Often,"
        elif Q13 == "A lot of the time (almost always)":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 4
            Q_isolated_sum = Q_isolated_sum + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q13:Disliked.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q13:Disliked.=No Answer,"

        if Q14 == "Not at all": 
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q14:Uncomfortable.=Not at all,"
        elif Q14 == "Only a little":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q14:Uncomfortable.=Only a little,"
        elif Q14 == "Sometimes":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q14:Uncomfortable.=Sometimes,"
        elif Q14 == "Often":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q14:Uncomfortable.=Often,"
        elif Q14 == "A lot of the time (almost always)":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q14:Uncomfortable.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q14:Uncomfortable.=No Answer,"

        if Q15 == "Not at all": 
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q15:Hate.=Not at all,"
        elif Q15 == "Only a little":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q15:Hate.=Only a little,"
        elif Q15 == "Sometimes":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q15:Hate.=Sometimes,"
        elif Q15 == "Often":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q15:Hate.=Often,"
        elif Q15 == "A lot of the time (almost always)":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q15:Hate.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q15:Hate.=No Answer,"

        if Q16 == "Not at all": 
            Q_social_support_security = Q_social_support_security + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q16:Friendly.=Not at all,"
        elif Q16 == "Only a little":
            Q_social_support_security = Q_social_support_security + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q16:Friendly.=Only a little,"
        elif Q16 == "Sometimes":
            Q_social_support_security = Q_social_support_security + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q16:Friendly.=Sometimes,"
        elif Q16 == "Often":
            Q_social_support_security = Q_social_support_security + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q16:Friendly.=Often,"
        elif Q16 == "A lot of the time (almost always)":
            Q_social_support_security = Q_social_support_security + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q16:Friendly.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q16:Friendly.=No Answer,"

        if Q17 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q17:Rested.=Not at all,"
        elif Q17 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q17:Rested.=Only a little,"
        elif Q17 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q17:Rested.=Sometimes,"
        elif Q17 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q17:Rested.=Often,"
        elif Q17 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q17:Rested.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q17:Rested.=No Answer,"

        if Q18 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q18:Relaxed.=Not at all,"
        elif Q18 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q18:Relaxed.=Only a little,"
        elif Q18 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q18:Relaxed.=Sometimes,"
        elif Q18 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q18:Relaxed.=Often,"
        elif Q18 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q18:Relaxed.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q18:Relaxed.=No Answer,"

        if Q19 == "Not at all": 
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q19:Anxious.=Not at all,"
        elif Q19 == "Only a little":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q19:Anxious.=Only a little,"
        elif Q19 == "Sometimes":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q19:Anxious.=Sometimes,"
        elif Q19 == "Often":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q19:Anxious.=Often,"
        elif Q19 == "A lot of the time (almost always)":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q19:Anxious.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q19:Anxious.=No Answer,"

        if Q20 == "Not at all": 
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q20:Tired.=Not at all,"
        elif Q20 == "Only a little":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q20:Tired.=Only a little,"
        elif Q20 == "Sometimes":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q20:Tired.=Sometimes,"
        elif Q20 == "Often":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q20:Tired.=Often,"
        elif Q20 == "A lot of the time (almost always)":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q20:Tired.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q20:Tired.=No Answer,"

        if Q21 == "Not at all": 
            Q_social_isolation_rejection = Q_social_isolation_rejection + 0
            Q_isolated_sum = Q_isolated_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q21:Lonely.=Not at all,"
        elif Q21 == "Only a little":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 1
            Q_isolated_sum = Q_isolated_sum + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q21:Lonely.=Only a little,"
        elif Q21 == "Sometimes":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 2
            Q_isolated_sum = Q_isolated_sum + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q21:Lonely.=Sometimes,"
        elif Q21 == "Often":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 3
            Q_isolated_sum = Q_isolated_sum + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q21:Lonely.=Often,"
        elif Q21 == "A lot of the time (almost always)":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 4
            Q_isolated_sum = Q_isolated_sum + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q21:Lonely.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q21:Lonely.=No Answer,"

        if Q22 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q22:Able to laugh.=Not at all,"
        elif Q22 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q22:Able to laugh.=Only a little,"
        elif Q22 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q22:Able to laugh.=Sometimes,"
        elif Q22 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q22:Able to laugh.=Often,"
        elif Q22 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q22:Able to laugh.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q22:Able to laugh.=No Answer,"

        if Q23 == "Not at all": 
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_despairing_sum = Q_despairing_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q23:Tearful.=Not at all,"
        elif Q23 == "Only a little":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 1
            Q_despairing_sum = Q_despairing_sum + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q23:Tearful.=Only a little,"
        elif Q23 == "Sometimes":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 2
            Q_despairing_sum = Q_despairing_sum + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q23:Tearful.=Sometimes,"
        elif Q23 == "Often":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 3
            Q_despairing_sum = Q_despairing_sum + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q23:Tearful.=Often,"
        elif Q23 == "A lot of the time (almost always)":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 4
            Q_despairing_sum = Q_despairing_sum + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q23:Tearful.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q23:Tearful.=No Answer,"

        if Q24 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_hopeful_sum = Q_hopeful_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q24:Hopeful.=Not at all,"
        elif Q24 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_hopeful_sum = Q_hopeful_sum + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q24:Hopeful.=Only a little,"
        elif Q24 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_hopeful_sum = Q_hopeful_sum + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q24:Hopeful.=Sometimes,"
        elif Q24 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_hopeful_sum = Q_hopeful_sum + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q24:Hopeful.=Often,"
        elif Q24 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_hopeful_sum = Q_hopeful_sum + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q24:Hopeful.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q24:Hopeful.=No Answer,"

        if Q25 == "Not at all": 
            Q_social_support_security = Q_social_support_security + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q25:Respected.=Not at all,"
        elif Q25 == "Only a little":
            Q_social_support_security = Q_social_support_security + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q25:Respected.=Only a little,"
        elif Q25 == "Sometimes":
            Q_social_support_security = Q_social_support_security + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q25:Respected.=Sometimes,"
        elif Q25 == "Often":
            Q_social_support_security = Q_social_support_security + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q25:Respected.=Often,"
        elif Q25 == "A lot of the time (almost always)":
            Q_social_support_security = Q_social_support_security + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q25:Respected.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q25:Respected.=No Answer,"

        if Q26 == "Not at all": 
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_despairing_sum = Q_despairing_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q26:Sadness.=Not at all,"
        elif Q26 == "Only a little":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 1
            Q_despairing_sum = Q_despairing_sum + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q26:Sadness.=Only a little,"
        elif Q26 == "Sometimes":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 2
            Q_despairing_sum = Q_despairing_sum + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q26:Sadness.=Sometimes,"
        elif Q26 == "Often":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 3
            Q_despairing_sum = Q_despairing_sum + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q26:Sadness.=Often,"
        elif Q26 == "A lot of the time (almost always)":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 4
            Q_despairing_sum = Q_despairing_sum + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q26:Sadness.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q26:Sadness.=No Answer,"

        if Q27 == "Not at all": 
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q27:Envious.=Not at all,"
        elif Q27 == "Only a little":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q27:Envious.=Only a little,"
        elif Q27 == "Sometimes":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q27:Envious.=Sometimes,"
        elif Q27 == "Often":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q27:Envious.=Often,"
        elif Q27 == "A lot of the time (almost always)":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q27:Envious.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q27:Envious.=No Answer,"

        if Q28 == "Not at all": 
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q28:Irritated.=Not at all,"
        elif Q28 == "Only a little":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q28:Irritated.=Only a little,"
        elif Q28 == "Sometimes":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q28:Irritated.=Sometimes,"
        elif Q28 == "Often":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q28:Irritated.=Often,"
        elif Q28 == "A lot of the time (almost always)":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q28:Irritated.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q28:Irritated.=No Answer,"

        if Q29 == "Not at all": 
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_despairing_sum = Q_despairing_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q29:Shame.=Not at all,"
        elif Q29 == "Only a little":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 1
            Q_despairing_sum = Q_despairing_sum + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q29:Shame.=Only a little,"
        elif Q29 == "Sometimes":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 2
            Q_despairing_sum = Q_despairing_sum + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q29:Shame.=Sometimes,"
        elif Q29 == "Often":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 3
            Q_despairing_sum = Q_despairing_sum + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q29:Shame.=Often,"
        elif Q29 == "A lot of the time (almost always)":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 4
            Q_despairing_sum = Q_despairing_sum + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q29:Shame.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q29:Shame.=No Answer,"

        if Q30 == "Not at all": 
            Q_social_support_security = Q_social_support_security + 0
            Q_included_sum = Q_included_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q30:Part of a group.=Not at all,"
        elif Q30 == "Only a little":
            Q_social_support_security = Q_social_support_security + 1
            Q_included_sum = Q_included_sum + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q30:Part of a group.=Only a little,"
        elif Q30 == "Sometimes":
            Q_social_support_security = Q_social_support_security + 2
            Q_included_sum = Q_included_sum + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q30:Part of a group.=Sometimes,"
        elif Q30 == "Often":
            Q_social_support_security = Q_social_support_security + 3
            Q_included_sum = Q_included_sum + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q30:Part of a group.=Often,"
        elif Q30 == "A lot of the time (almost always)":
            Q_social_support_security = Q_social_support_security + 4
            Q_included_sum = Q_included_sum + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q30:Part of a group.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q30:Part of a group.=No Answer,"

        if Q31 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_hopeful_sum = Q_hopeful_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q31:Liking yourself.=Not at all,"
        elif Q31 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_hopeful_sum = Q_hopeful_sum + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q31:Liking yourself.=Only a little,"
        elif Q31 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_hopeful_sum = Q_hopeful_sum + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q31:Liking yourself.=Sometimes,"
        elif Q31 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_hopeful_sum = Q_hopeful_sum + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q31:Liking yourself.=Often,"
        elif Q31 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_hopeful_sum = Q_hopeful_sum + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q31:Liking yourself.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q31:Liking yourself.=No Answer,"

        if Q32 == "Not at all": 
            Q_social_support_security = Q_social_support_security + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q32:Having good choices.=Not at all,"
        elif Q32 == "Only a little":
            Q_social_support_security = Q_social_support_security + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q32:Having good choices.=Only a little,"
        elif Q32 == "Sometimes":
            Q_social_support_security = Q_social_support_security + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q32:Having good choices.=Sometimes,"
        elif Q32 == "Often":
            Q_social_support_security = Q_social_support_security + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q32:Having good choices.=Often,"
        elif Q32 == "A lot of the time (almost always)":
            Q_social_support_security = Q_social_support_security + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q32:Having good choices.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q32:Having good choices.=No Answer,"

        if Q33 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q33:Curiosity.=Not at all,"
        elif Q33 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q33:Curiosity.=Only a little,"
        elif Q33 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q33:Curiosity.=Sometimes,"
        elif Q33 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q33:Curiosity.=Often,"
        elif Q33 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q33:Curiosity.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q33:Curiosity.=No Answer,"

        if Q34 == "Not at all": 
            Q_social_isolation_rejection = Q_social_isolation_rejection + 0
            Q_isolated_sum = Q_isolated_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q34:Hurt by others.=Not at all,"
        elif Q34 == "Only a little":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 1
            Q_isolated_sum = Q_isolated_sum + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q34:Hurt by others.=Only a little,"
        elif Q34 == "Sometimes":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 2
            Q_isolated_sum = Q_isolated_sum + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q34:Hurt by others.=Sometimes,"
        elif Q34 == "Often":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 3
            Q_isolated_sum = Q_isolated_sum + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q34:Hurt by others.=Often,"
        elif Q34 == "A lot of the time (almost always)":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 4
            Q_isolated_sum = Q_isolated_sum + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q34:Hurt by others.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q34:Hurt by others.=No Answer,"

        if Q35 == "Not at all": 
            Q_social_support_security = Q_social_support_security + 0
            Q_included_sum = Q_included_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q35:Understood.=Not at all,"
        elif Q35 == "Only a little":
            Q_social_support_security = Q_social_support_security + 1
            Q_included_sum = Q_included_sum + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q35:Understood.=Only a little,"
        elif Q35 == "Sometimes":
            Q_social_support_security = Q_social_support_security + 2
            Q_included_sum = Q_included_sum + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q35:Understood.=Sometimes,"
        elif Q35 == "Often":
            Q_social_support_security = Q_social_support_security + 3
            Q_included_sum = Q_included_sum + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q35:Understood.=Often,"
        elif Q35 == "A lot of the time (almost always)":
            Q_social_support_security = Q_social_support_security + 4
            Q_included_sum = Q_included_sum + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q35:Understood.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q35:Understood.=No Answer,"

        if Q36 == "Not at all": 
            Q_social_support_security = Q_social_support_security + 0
            Q_included_sum = Q_included_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q36:Loved.=Not at all,"
        elif Q36 == "Only a little":
            Q_social_support_security = Q_social_support_security + 1
            Q_included_sum = Q_included_sum + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q36:Loved.=Only a little,"
        elif Q36 == "Sometimes":
            Q_social_support_security = Q_social_support_security + 2
            Q_included_sum = Q_included_sum + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q36:Loved.=Sometimes,"
        elif Q36 == "Often":
            Q_social_support_security = Q_social_support_security + 3
            Q_included_sum = Q_included_sum + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q36:Loved.=Often,"
        elif Q36 == "A lot of the time (almost always)":
            Q_social_support_security = Q_social_support_security + 4
            Q_included_sum = Q_included_sum + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q36:Loved.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q36:Loved.=No Answer,"

        if Q37 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_hopeful_sum = Q_hopeful_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q37:Happy.=Not at all,"
        elif Q37 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_hopeful_sum = Q_hopeful_sum + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q37:Happy.=Only a little,"
        elif Q37 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_hopeful_sum = Q_hopeful_sum + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q37:Happy.=Sometimes,"
        elif Q37 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_hopeful_sum = Q_hopeful_sum + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q37:Happy.=Often,"
        elif Q37 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_hopeful_sum = Q_hopeful_sum + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q37:Happy.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q37:Happy.=No Answer,"

        if Q38 == "Not at all": 
            Q_social_isolation_rejection = Q_social_isolation_rejection + 0
            Q_isolated_sum = Q_isolated_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q38:Left-out.=Not at all,"
        elif Q38 == "Only a little":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 1
            Q_isolated_sum = Q_isolated_sum + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q38:Left-out.=Only a little,"
        elif Q38 == "Sometimes":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 2
            Q_isolated_sum = Q_isolated_sum + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q38:Left-out.=Sometimes,"
        elif Q38 == "Often":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 3
            Q_isolated_sum = Q_isolated_sum + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q38:Left-out.=Often,"
        elif Q38 == "A lot of the time (almost always)":
            Q_social_isolation_rejection = Q_social_isolation_rejection + 4
            Q_isolated_sum = Q_isolated_sum + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q38:Left-out.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q38:Left-out.=No Answer,"

        if Q39 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q39:Proud.=Not at all,"
        elif Q39 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q39:Proud.=Only a little,"
        elif Q39 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q39:Proud.=Sometimes,"
        elif Q39 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q39:Proud.=Often,"
        elif Q39 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q39:Proud.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q39:Proud.=No Answer,"

        if Q40 == "Not at all": 
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_despairing_sum = Q_despairing_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q40:Wishing you were not here.=Not at all,"
        elif Q40 == "Only a little":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 1
            Q_despairing_sum = Q_despairing_sum + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q40:Wishing you were not here.=Only a little,"
        elif Q40 == "Sometimes":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 2
            Q_despairing_sum = Q_despairing_sum + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q40:Wishing you were not here.=Sometimes,"
        elif Q40 == "Often":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 3
            Q_despairing_sum = Q_despairing_sum + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q40:Wishing you were not here.=Often,"
        elif Q40 == "A lot of the time (almost always)":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 4
            Q_despairing_sum = Q_despairing_sum + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q40:Wishing you were not here.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q40:Wishing you were not here.=No Answer,"

        if Q41 == "Not at all": 
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 0
            Q_hopeful_sum = Q_hopeful_sum + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q41:Believing life will get better.=Not at all,"
        elif Q41 == "Only a little":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 1
            Q_hopeful_sum = Q_hopeful_sum + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q41:Believing life will get better.=Only a little,"
        elif Q41 == "Sometimes":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 2
            Q_hopeful_sum = Q_hopeful_sum + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q41:Believing life will get better.=Sometimes,"
        elif Q41 == "Often":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 3
            Q_hopeful_sum = Q_hopeful_sum + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q41:Believing life will get better.=Often,"
        elif Q41 == "A lot of the time (almost always)":
            Q_positive_well_being_resilience = Q_positive_well_being_resilience + 4
            Q_hopeful_sum = Q_hopeful_sum + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q41:Believing life will get better.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q41:Believing life will get better.=No Answer,"    

        if Q42 == "Not at all": 
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q42:Feeling the discomfort of stress in your body.=Not at all,"
        elif Q42 == "Only a little":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q42:Feeling the discomfort of stress in your body.=Only a little,"
        elif Q42 == "Sometimes":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q42:Feeling the discomfort of stress in your body.=Sometimes,"
        elif Q42 == "Often":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q42:Feeling the discomfort of stress in your body.=Often,"
        elif Q42 == "A lot of the time (almost always)":
            Q_internal_psychological_somatic_distress = Q_internal_psychological_somatic_distress + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q42:Feeling the discomfort of stress in your body.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q42:Feeling the discomfort of stress in your body.=No Answer,"

        Q_total = Q_positive_well_being_resilience + Q_social_support_security - Q_internal_psychological_somatic_distress - Q_social_isolation_rejection
        
        if Q_total >= 20:
            st.write(f"#### Total Score: {Q_total}")
            Q_response = "Thriving, strong emotional reserves and high resilience."
        elif Q_total >= 0 and Q_total <= 19:
            st.write(f"#### Total Score: {Q_total}")
            Q_response = "Stable, typical emotional ups and downs."
        elif Q_total >= -10 and Q_total <= -1:
            st.write(f"#### Total Score: {Q_total}")
            Q_response = "At Risk, the adult is experiencing more distress than joy."
        elif Q_total <= -11:
            st.write(f"#### Total Score: {Q_total}")
            Q_response = "High Distress, may require immediate clinical or community intervention."
        
        st.write(f"#### Score Interpretation: {Q_response}")

        # Outlook Balance=Sum(Hopeful)−Sum(Despairing)
        # Balanced range -16 to +20
        Q_outlook_balance = Q_hopeful_sum - Q_despairing_sum

        if Q_outlook_balance > 20:
            st.write(f"#### Outlook Balance (Hope vs. Despair) Score: {Q_outlook_balance} (Hopeful)")            
        elif Q_outlook_balance >= -16 and Q_outlook_balance <= 20:
            st.write(f"#### Outlook Balance (Hope vs. Despair) Score: {Q_outlook_balance} (Balanced)")
        elif Q_outlook_balance < -16:
            st.write(f"#### Outlook Balance (Hope vs. Despair) Score: {Q_outlook_balance} (Despair)")
        
        # Social Balance=Sum(Included)−Sum(Isolated)
        # Balanced range -16 to +16
        Q_social_connectivity_balance = Q_included_sum - Q_isolated_sum

        if Q_outlook_balance > 16:
            st.write(f"#### Social Connectivity Balance (Included vs. Isolated) Score: {Q_outlook_balance} (Included)")            
        elif Q_outlook_balance >= -16 and Q_outlook_balance <= 16:
            st.write(f"#### Outlook Balance (Hope vs. Despair) Score: {Q_outlook_balance} (Balanced)")
        elif Q_outlook_balance < -16:
            st.write(f"#### Outlook Balance (Hope vs. Despair) Score: {Q_outlook_balance} (Isolated)")

        # Special conditions.
        # Clinical Note on Items 40 & 42
        # Item 40 (Wishing you were not here): Any rating of 1 or higher on this item should trigger a standard risk assessment protocol.
        # Item 42 (Somatic Stress): High ratings here suggest the individual may benefit from “bottom-up” regulatory strategies (e.g., grounding, breathing) in addition to cognitive interventions.
        if Q40 == "Only a little" or Q40 == "Sometimes" or Q40 == "Often" or Q36 == "A lot of the time (almost always)":
            st.write(f"Answer to Item 40 (Wishing you were not here) is non-zero ({Q40}). A standard risk assessment protocol is recommended.")
        if Q42 == "Often" or Q42 == "A lot of the time (almost always)":
            st.write(f"Answer to Item 42 (Somatic stress) is high ({Q42}). High ratings here suggest the individual may benefit from \“bottom-up\” regulatory strategies (e.g., grounding, breathing) in addition to cognitive interventions.")
        
        st.markdown("For additional information and resources, please visit: [US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")
        Q_rawdata = Q_rawdata + "Score=" + str(Q_total)

    #-------------------------------------------------------------------
    # TOOL SCORING
    # TOOL: Daily Digital Connected Life, DDCL
    #-------------------------------------------------------------------

    if submit5 and language == "English":
        Q_total = 0
        Q_response = ""
        Q_rawdata = name + "," + str(age) + ","

        # Questions scored in reverse?
        if Q1 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q1:I use my DDCL devices as the primary source of the music I listen to.=False,"
        elif Q1 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q1:I use my DDCL devices as the primary source of the music I listen to.=Seldom True,"
        elif Q1 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q1:I use my DDCL devices as the primary source of the music I listen to.=At Times True,"
        elif Q1 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q1:I use my DDCL devices as the primary source of the music I listen to.=Frequently True,"
        elif Q1 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q1:I use my DDCL devices as the primary source of the music I listen to.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q1:I use my DDCL devices as the primary source of the music I listen to.=No Answer,"

        if Q2 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q2:I frequently use digital devices to entertain myself when I'm bored.=False,"
        elif Q2 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q2:I frequently use digital devices to entertain myself when I'm bored.=Seldom True,"
        elif Q2 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q2:I frequently use digital devices to entertain myself when I'm bored.=At Times True,"
        elif Q2 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q2:I frequently use digital devices to entertain myself when I'm bored.=Frequently True,"
        elif Q2 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q2:I frequently use digital devices to entertain myself when I'm bored.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q2:I frequently use digital devices to entertain myself when I'm bored.=No Answer,"

        if Q3 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q3:With the pace of my life, it is much easier to text and digitally chat than talk on the phone or sometimes find the time to meet in person.=False,"
        elif Q3 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q3:With the pace of my life, it is much easier to text and digitally chat than talk on the phone or sometimes find the time to meet in person.=Seldom True,"
        elif Q3 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q3:With the pace of my life, it is much easier to text and digitally chat than talk on the phone or sometimes find the time to meet in person.=At Times True,"
        elif Q3 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q3:With the pace of my life, it is much easier to text and digitally chat than talk on the phone or sometimes find the time to meet in person.=Frequently True,"
        elif Q3 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q3:With the pace of my life, it is much easier to text and digitally chat than talk on the phone or sometimes find the time to meet in person.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q3:With the pace of my life, it is much easier to text and digitally chat than talk on the phone or sometimes find the time to meet in person.=No Answer,"

        if Q4 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q4:Have you ever downloaded an app like Tinder, OkCupid, Bumble, Grindr, Her, BeNaughty, Plenty of Fish, etc.?=False,"
        elif Q4 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q4:Have you ever downloaded an app like Tinder, OkCupid, Bumble, Grindr, Her, BeNaughty, Plenty of Fish, etc.?=Seldom True,"
        elif Q4 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q4:Have you ever downloaded an app like Tinder, OkCupid, Bumble, Grindr, Her, BeNaughty, Plenty of Fish, etc.?=At Times True,"
        elif Q4 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q4:Have you ever downloaded an app like Tinder, OkCupid, Bumble, Grindr, Her, BeNaughty, Plenty of Fish, etc.?=Frequently True,"
        elif Q4 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q4:Have you ever downloaded an app like Tinder, OkCupid, Bumble, Grindr, Her, BeNaughty, Plenty of Fish, etc.?=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q4:Have you ever downloaded an app like Tinder, OkCupid, Bumble, Grindr, Her, BeNaughty, Plenty of Fish, etc.?=No Answer,"

        if Q5 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q5:It is easier for me to express my feelings in the messages I send rather than trying to express them to someone in person.=False,"
        elif Q5 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q5:It is easier for me to express my feelings in the messages I send rather than trying to express them to someone in person.=Seldom True,"
        elif Q5 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q5:It is easier for me to express my feelings in the messages I send rather than trying to express them to someone in person.=At Times True,"
        elif Q5 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q5:It is easier for me to express my feelings in the messages I send rather than trying to express them to someone in person.=Frequently True,"
        elif Q5 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q5:It is easier for me to express my feelings in the messages I send rather than trying to express them to someone in person.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q5:It is easier for me to express my feelings in the messages I send rather than trying to express them to someone in person.=No Answer,"

        if Q6 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q6:My strongest connections with others are facilitated through the apps that I am using.=False,"
        elif Q6 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q6:My strongest connections with others are facilitated through the apps that I am using.=Seldom True,"
        elif Q6 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q6:My strongest connections with others are facilitated through the apps that I am using.=At Times True,"
        elif Q6 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q6:My strongest connections with others are facilitated through the apps that I am using.=Frequently True,"
        elif Q6 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q6:My strongest connections with others are facilitated through the apps that I am using.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q6:My strongest connections with others are facilitated through the apps that I am using.=No Answer,"

        if Q7 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q7:Just in case I ever feel it is necessary at some point, I have looked online at ways I might be able to end my own life.=False,"
        elif Q7 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q7:Just in case I ever feel it is necessary at some point, I have looked online at ways I might be able to end my own life.=Seldom True,"
        elif Q7 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q7:Just in case I ever feel it is necessary at some point, I have looked online at ways I might be able to end my own life.=At Times True,"
        elif Q7 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q7:Just in case I ever feel it is necessary at some point, I have looked online at ways I might be able to end my own life.=Frequently True,"
        elif Q7 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q7:Just in case I ever feel it is necessary at some point, I have looked online at ways I might be able to end my own life.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q7:Just in case I ever feel it is necessary at some point, I have looked online at ways I might be able to end my own life.=No Answer,"

        if Q8 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q8:I manage my anxiety by reading posts or articles on my DDCL devices.=False,"
        elif Q8 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q8:I manage my anxiety by reading posts or articles on my DDCL devices.=Seldom True,"
        elif Q8 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q8:I manage my anxiety by reading posts or articles on my DDCL devices.=At Times True,"
        elif Q8 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q8:I manage my anxiety by reading posts or articles on my DDCL devices.=Frequently True,"
        elif Q8 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q8:I manage my anxiety by reading posts or articles on my DDCL devices.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q8:I manage my anxiety by reading posts or articles on my DDCL devices.=No Answer,"

        if Q9 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q9:When I need to distract myself, I use my DDCL devices.=False,"
        elif Q9 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q9:When I need to distract myself, I use my DDCL devices.=Seldom True,"
        elif Q9 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q9:When I need to distract myself, I use my DDCL devices.=At Times True,"
        elif Q9 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q9:When I need to distract myself, I use my DDCL devices.=Frequently True,"
        elif Q9 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q9:When I need to distract myself, I use my DDCL devices.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q9:When I need to distract myself, I use my DDCL devices.=No Answer,"

        if Q10 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q10:Some of what I enjoy is illegal and I appreciate that online I can anonymously interact with others with similar interests.=False,"
        elif Q10 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q10:Some of what I enjoy is illegal and I appreciate that online I can anonymously interact with others with similar interests.=Seldom True,"
        elif Q10 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q10:Some of what I enjoy is illegal and I appreciate that online I can anonymously interact with others with similar interests.=At Times True,"
        elif Q10 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q10:Some of what I enjoy is illegal and I appreciate that online I can anonymously interact with others with similar interests.=Frequently True,"
        elif Q10 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q10:Some of what I enjoy is illegal and I appreciate that online I can anonymously interact with others with similar interests.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q10:Some of what I enjoy is illegal and I appreciate that online I can anonymously interact with others with similar interests.=No Answer,"

        if Q11 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q11:I am using my DDCL devices to meet new people.=False,"
        elif Q11 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q11:I am using my DDCL devices to meet new people.=Seldom True,"
        elif Q11 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q11:I am using my DDCL devices to meet new people.=At Times True,"
        elif Q11 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q11:I am using my DDCL devices to meet new people.=Frequently True,"
        elif Q11 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q11:I am using my DDCL devices to meet new people.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q11:I am using my DDCL devices to meet new people.=No Answer,"

        if Q12 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q12:I have never been on the Internet.=False,"
        elif Q12 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q12:I have never been on the Internet.=Seldom True,"
        elif Q12 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q12:I have never been on the Internet.=At Times True,"
        elif Q12 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q12:I have never been on the Internet.=Frequently True,"
        elif Q12 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q12:I have never been on the Internet.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q12:I have never been on the Internet.=No Answer,"

        if Q13 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q13:I use the World Wide Web often to fuel my most intimate fantasies.=False,"
        elif Q13 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q13:I use the World Wide Web often to fuel my most intimate fantasies.=Seldom True,"
        elif Q13 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q13:I use the World Wide Web often to fuel my most intimate fantasies.=At Times True,"
        elif Q13 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q13:I use the World Wide Web often to fuel my most intimate fantasies.=Frequently True,"
        elif Q13 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q13:I use the World Wide Web often to fuel my most intimate fantasies.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q13:I use the World Wide Web often to fuel my most intimate fantasies.=No Answer,"

        if Q14 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q14:To be prepared, I have looked online at ways to protect myself and also at ways to harm others that may be a real threat to me.=False,"
        elif Q14 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q14:To be prepared, I have looked online at ways to protect myself and also at ways to harm others that may be a real threat to me.=Seldom True,"
        elif Q14 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q14:To be prepared, I have looked online at ways to protect myself and also at ways to harm others that may be a real threat to me.=At Times True,"
        elif Q14 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q14:To be prepared, I have looked online at ways to protect myself and also at ways to harm others that may be a real threat to me.=Frequently True,"
        elif Q14 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q14:To be prepared, I have looked online at ways to protect myself and also at ways to harm others that may be a real threat to me.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q14:To be prepared, I have looked online at ways to protect myself and also at ways to harm others that may be a real threat to me.=No Answer,"

        if Q15 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q15:The best way to get to know me is through what I post and the pictures or videos I share. These are availabe online or through my messaging.=False,"
        elif Q15 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q15:The best way to get to know me is through what I post and the pictures or videos I share. These are availabe online or through my messaging.=Seldom True,"
        elif Q15 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q15:The best way to get to know me is through what I post and the pictures or videos I share. These are availabe online or through my messaging.=At Times True,"
        elif Q15 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q15:The best way to get to know me is through what I post and the pictures or videos I share. These are availabe online or through my messaging.=Frequently True,"
        elif Q15 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q15:The best way to get to know me is through what I post and the pictures or videos I share. These are availabe online or through my messaging.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q15:The best way to get to know me is through what I post and the pictures or videos I share. These are availabe online or through my messaging.=No Answer,"

        if Q16 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q16:Have you ever used an app to meet someone?=False,"
        elif Q16 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q16:Have you ever used an app to meet someone?=Seldom True,"
        elif Q16 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q16:Have you ever used an app to meet someone?=At Times True,"
        elif Q16 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q16:Have you ever used an app to meet someone?=Frequently True,"
        elif Q16 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q16:Have you ever used an app to meet someone?=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q16:Have you ever used an app to meet someone?=No Answer,"

        if Q17 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q17:Because explaining to someone my reactions to what they said or did can be difficult, I often send messages rather than meet face-to-face.=False,"
        elif Q17 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q17:Because explaining to someone my reactions to what they said or did can be difficult, I often send messages rather than meet face-to-face.=Seldom True,"
        elif Q17 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q17:Because explaining to someone my reactions to what they said or did can be difficult, I often send messages rather than meet face-to-face.=At Times True,"
        elif Q17 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q17:Because explaining to someone my reactions to what they said or did can be difficult, I often send messages rather than meet face-to-face.=Frequently True,"
        elif Q17 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q17:Because explaining to someone my reactions to what they said or did can be difficult, I often send messages rather than meet face-to-face.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q17:Because explaining to someone my reactions to what they said or did can be difficult, I often send messages rather than meet face-to-face.=No Answer,"

        if Q18 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q18:I often lose track of time, go to bed too late, or lose windows of opportunity for other activities because I'm at times engaged in the digital world or with messaging.=False,"
        elif Q18 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q18:I often lose track of time, go to bed too late, or lose windows of opportunity for other activities because I'm at times engaged in the digital world or with messaging.=Seldom True,"
        elif Q18 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q18:I often lose track of time, go to bed too late, or lose windows of opportunity for other activities because I'm at times engaged in the digital world or with messaging.=At Times True,"
        elif Q18 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q18:I often lose track of time, go to bed too late, or lose windows of opportunity for other activities because I'm at times engaged in the digital world or with messaging.=Frequently True,"
        elif Q18 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q18:I often lose track of time, go to bed too late, or lose windows of opportunity for other activities because I'm at times engaged in the digital world or with messaging.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q18:I often lose track of time, go to bed too late, or lose windows of opportunity for other activities because I'm at times engaged in the digital world or with messaging.=No Answer,"

        if Q19 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q19:When I'm not feeling well, I go online to research my symptoms.=False,"
        elif Q19 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q19:When I'm not feeling well, I go online to research my symptoms.=Seldom True,"
        elif Q19 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q19:When I'm not feeling well, I go online to research my symptoms.=At Times True,"
        elif Q19 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q19:When I'm not feeling well, I go online to research my symptoms.=Frequently True,"
        elif Q19 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q19:When I'm not feeling well, I go online to research my symptoms.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q19:When I'm not feeling well, I go online to research my symptoms.=No Answer,"
    
        if Q20 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q20:I frequently spend my downtime gaming, watching videos, or reading on my DDCL devices.=False,"
        elif Q20 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q20:I frequently spend my downtime gaming, watching videos, or reading on my DDCL devices.=Seldom True,"
        elif Q20 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q20:I frequently spend my downtime gaming, watching videos, or reading on my DDCL devices.=At Times True,"
        elif Q20 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q20:I frequently spend my downtime gaming, watching videos, or reading on my DDCL devices.=Frequently True,"
        elif Q20 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q20:I frequently spend my downtime gaming, watching videos, or reading on my DDCL devices.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q20:I frequently spend my downtime gaming, watching videos, or reading on my DDCL devices.=No Answer,"

        if Q21 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q21:I have felt hurt by what other people, including friends, have posted or shared in our mutual DDCL.=False,"
        elif Q21 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q21:I have felt hurt by what other people, including friends, have posted or shared in our mutual DDCL.=Seldom True,"
        elif Q21 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q21:I have felt hurt by what other people, including friends, have posted or shared in our mutual DDCL.=At Times True,"
        elif Q21 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q21:I have felt hurt by what other people, including friends, have posted or shared in our mutual DDCL.=Frequently True,"
        elif Q21 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q21:I have felt hurt by what other people, including friends, have posted or shared in our mutual DDCL.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q21:I have felt hurt by what other people, including friends, have posted or shared in our mutual DDCL.=No Answer,"

        if Q22 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q22:I am currently using virtual reality gear (HoloLens, Oculus Rift, Samsung Gear VR, Google DayDream View, PlayStation VR, etc.).=False,"
        elif Q22 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q22:I am currently using virtual reality gear (HoloLens, Oculus Rift, Samsung Gear VR, Google DayDream View, PlayStation VR, etc.).=Seldom True,"
        elif Q22 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q22:I am currently using virtual reality gear (HoloLens, Oculus Rift, Samsung Gear VR, Google DayDream View, PlayStation VR, etc.).=At Times True,"
        elif Q22 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q22:I am currently using virtual reality gear (HoloLens, Oculus Rift, Samsung Gear VR, Google DayDream View, PlayStation VR, etc.).=Frequently True,"
        elif Q22 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q22:I am currently using virtual reality gear (HoloLens, Oculus Rift, Samsung Gear VR, Google DayDream View, PlayStation VR, etc.).=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q22:I am currently using virtual reality gear (HoloLens, Oculus Rift, Samsung Gear VR, Google DayDream View, PlayStation VR, etc.).=No Answer,"
    
        if Q23 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q23:Just in case I ever feel it is necessary at some point, I have looked online at ways I might be able to end my own life.=False,"
        elif Q23 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q23:Just in case I ever feel it is necessary at some point, I have looked online at ways I might be able to end my own life.=Seldom True,"
        elif Q23 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q23:Just in case I ever feel it is necessary at some point, I have looked online at ways I might be able to end my own life.=At Times True,"
        elif Q23 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q23:Just in case I ever feel it is necessary at some point, I have looked online at ways I might be able to end my own life.=Frequently True,"
        elif Q23 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q23:Just in case I ever feel it is necessary at some point, I have looked online at ways I might be able to end my own life.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q23:Just in case I ever feel it is necessary at some point, I have looked online at ways I might be able to end my own life.=No Answer,"

        if Q24 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q24:At times I wish there were an \"unsend\" or \"delete\" button for a text that I have sent or for something that I posted on a social media outlet.=False,"
        elif Q24 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q24:At times I wish there were an \"unsend\" or \"delete\" button for a text that I have sent or for something that I posted on a social media outlet.=Seldom True,"
        elif Q24 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q24:At times I wish there were an \"unsend\" or \"delete\" button for a text that I have sent or for something that I posted on a social media outlet.=At Times True,"
        elif Q24 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q24:At times I wish there were an \"unsend\" or \"delete\" button for a text that I have sent or for something that I posted on a social media outlet.=Frequently True,"
        elif Q24 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q24:At times I wish there were an \"unsend\" or \"delete\" button for a text that I have sent or for something that I posted on a social media outlet.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q24:At times I wish there were an \"unsend\" or \"delete\" button for a text that I have sent or for something that I posted on a social media outlet.=No Answer,"

        if Q25 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q25:I am aware that others have felt upset with what I have posted or shared in our mutual DDCL.=False,"
        elif Q25 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q25:I am aware that others have felt upset with what I have posted or shared in our mutual DDCL.=Seldom True,"
        elif Q25 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q25:I am aware that others have felt upset with what I have posted or shared in our mutual DDCL.=At Times True,"
        elif Q25 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q25:I am aware that others have felt upset with what I have posted or shared in our mutual DDCL.=Frequently True,"
        elif Q25 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q25:I am aware that others have felt upset with what I have posted or shared in our mutual DDCL.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q25:I am aware that others have felt upset with what I have posted or shared in our mutual DDCL.=No Answer,"

        if Q26 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q26:I have downloaded an online dating app.=False,"
        elif Q26 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q26:I have downloaded an online dating app.=Seldom True,"
        elif Q26 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q26:I have downloaded an online dating app.=At Times True,"
        elif Q26 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q26:I have downloaded an online dating app.=Frequently True,"
        elif Q26 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q26:I have downloaded an online dating app.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q26:I have downloaded an online dating app.=No Answer,"
    
        if Q27 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q27:I'd rather purchase items online than go to a neighborhood store.=False,"
        elif Q27 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q27:I'd rather purchase items online than go to a neighborhood store.=Seldom True,"
        elif Q27 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q27:I'd rather purchase items online than go to a neighborhood store.=At Times True,"
        elif Q27 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q27:I'd rather purchase items online than go to a neighborhood store.=Frequently True,"
        elif Q27 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q27:I'd rather purchase items online than go to a neighborhood store.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q27:I'd rather purchase items online than go to a neighborhood store.=No Answer,"

        if Q28 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q28:I have needed to block the access of someone I know to my DDCL.=False,"
        elif Q28 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q28:I have needed to block the access of someone I know to my DDCL.=Seldom True,"
        elif Q28 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q28:I have needed to block the access of someone I know to my DDCL.=At Times True,"
        elif Q28 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q28:I have needed to block the access of someone I know to my DDCL.=Frequently True,"
        elif Q28 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q28:I have needed to block the access of someone I know to my DDCL.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q28:I have needed to block the access of someone I know to my DDCL.=No Answer,"
    
        if Q29 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q29:I have multiple social network accounts with different names that I selectively share with only a few of my friends or family.=False,"
        elif Q29 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q29:I have multiple social network accounts with different names that I selectively share with only a few of my friends or family.=Seldom True,"
        elif Q29 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q29:I have multiple social network accounts with different names that I selectively share with only a few of my friends or family.=At Times True,"
        elif Q29 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q29:I have multiple social network accounts with different names that I selectively share with only a few of my friends or family.=Frequently True,"
        elif Q29 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q29:I have multiple social network accounts with different names that I selectively share with only a few of my friends or family.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q29:I have multiple social network accounts with different names that I selectively share with only a few of my friends or family.=No Answer,"

        if Q30 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q30:I have pictures and other items on my DDCL devices that I do not want other people to see.=False,"
        elif Q30 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q30:I have pictures and other items on my DDCL devices that I do not want other people to see.=Seldom True,"
        elif Q30 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q30:I have pictures and other items on my DDCL devices that I do not want other people to see.=At Times True,"
        elif Q30 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q30:I have pictures and other items on my DDCL devices that I do not want other people to see.=Frequently True,"
        elif Q30 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q30:I have pictures and other items on my DDCL devices that I do not want other people to see.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q30:I have pictures and other items on my DDCL devices that I do not want other people to see.=No Answer,"
    
        if Q31 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q31:Some of the people who say they care about me would disapprove of the webpages I visit, the peope I chat with online, or some of what I post anonymously.=False,"
        elif Q31 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q31:Some of the people who say they care about me would disapprove of the webpages I visit, the peope I chat with online, or some of what I post anonymously.=Seldom True,"
        elif Q31 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q31:Some of the people who say they care about me would disapprove of the webpages I visit, the peope I chat with online, or some of what I post anonymously.=At Times True,"
        elif Q31 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q31:Some of the people who say they care about me would disapprove of the webpages I visit, the peope I chat with online, or some of what I post anonymously.=Frequently True,"
        elif Q31 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q31:Some of the people who say they care about me would disapprove of the webpages I visit, the peope I chat with online, or some of what I post anonymously.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q31:Some of the people who say they care about me would disapprove of the webpages I visit, the peope I chat with online, or some of what I post anonymously.=No Answer,"

        if Q32 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q32:I have looked at the images of others online to feel better about my weight and size.=False,"
        elif Q32 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q32:I have looked at the images of others online to feel better about my weight and size.=Seldom True,"
        elif Q32 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q32:I have looked at the images of others online to feel better about my weight and size.=At Times True,"
        elif Q32 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q32:I have looked at the images of others online to feel better about my weight and size.=Frequently True,"
        elif Q32 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q32:I have looked at the images of others online to feel better about my weight and size.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q32:I have looked at the images of others online to feel better about my weight and size.=No Answer,"

        if Q33 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q33:It is hard for me to imagine staying current with those in my networks without extensively using my DDCL devices.=False,"
        elif Q33 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q33:It is hard for me to imagine staying current with those in my networks without extensively using my DDCL devices.=Seldom True,"
        elif Q33 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q33:It is hard for me to imagine staying current with those in my networks without extensively using my DDCL devices.=At Times True,"
        elif Q33 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q33:It is hard for me to imagine staying current with those in my networks without extensively using my DDCL devices.=Frequently True,"
        elif Q33 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q33:It is hard for me to imagine staying current with those in my networks without extensively using my DDCL devices.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q33:It is hard for me to imagine staying current with those in my networks without extensively using my DDCL devices.=No Answer,"

        if Q34 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q34:I have deleted photographs and/or videos from my DDCL.=False,"
        elif Q34 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q34:I have deleted photographs and/or videos from my DDCL.=Seldom True,"
        elif Q34 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q34:I have deleted photographs and/or videos from my DDCL.=At Times True,"
        elif Q34 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q34:I have deleted photographs and/or videos from my DDCL.=Frequently True,"
        elif Q34 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q34:I have deleted photographs and/or videos from my DDCL.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q34:I have deleted photographs and/or videos from my DDCL.=No Answer,"

        if Q35 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q35:I'd rather purchase items in a store than online.=False,"
        elif Q35 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q35:I'd rather purchase items in a store than online.=Seldom True,"
        elif Q35 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q35:I'd rather purchase items in a store than online.=At Times True,"
        elif Q35 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q35:I'd rather purchase items in a store than online.=Frequently True,"
        elif Q35 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q35:I'd rather purchase items in a store than online.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q35:I'd rather purchase items in a store than online.=No Answer,"

        if Q36 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q36:I enjoy fooling others online by pretending to be a different person.=False,"
        elif Q36 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q36:I enjoy fooling others online by pretending to be a different person.=Seldom True,"
        elif Q36 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q36:I enjoy fooling others online by pretending to be a different person.=At Times True,"
        elif Q36 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q36:I enjoy fooling others online by pretending to be a different person.=Frequently True,"
        elif Q36 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q36:I enjoy fooling others online by pretending to be a different person.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q36:I enjoy fooling others online by pretending to be a different person.=No Answer,"

        if Q37 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q37:I use apps to help me find new places to eat or drink.=False,"
        elif Q37 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q37:I use apps to help me find new places to eat or drink.=Seldom True,"
        elif Q37 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q37:I use apps to help me find new places to eat or drink.=At Times True,"
        elif Q37 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q37:I use apps to help me find new places to eat or drink.=Frequently True,"
        elif Q37 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q37:I use apps to help me find new places to eat or drink.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q37:I use apps to help me find new places to eat or drink.=No Answer,"

        if Q38 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q38:I have another phone or device that no one knows about to keep aspects of my life private.=False,"
        elif Q38 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q38:I have another phone or device that no one knows about to keep aspects of my life private.=Seldom True,"
        elif Q38 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q38:I have another phone or device that no one knows about to keep aspects of my life private.=At Times True,"
        elif Q38 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q38:I have another phone or device that no one knows about to keep aspects of my life private.=Frequently True,"
        elif Q38 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q38:I have another phone or device that no one knows about to keep aspects of my life private.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q38:I have another phone or device that no one knows about to keep aspects of my life private.=No Answer,"

        if Q39 == "False": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q39:I look at more items online than I actually purchase.=False,"
        elif Q39 == "Seldom True":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q39:I look at more items online than I actually purchase.=Seldom True,"
        elif Q39 == "At Times True":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q39:I look at more items online than I actually purchase.=At Times True,"
        elif Q39 == "Frequently True":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q39:I look at more items online than I actually purchase.=Frequently True,"
        elif Q39 == "Extremely True":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q39:I look at more items online than I actually purchase.=Extremely True,"
        else:
            Q_rawdata = Q_rawdata + "Q39:I look at more items online than I actually purchase.=No Answer,"

        st.markdown("For additional information and resources, please visit: [US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")

    #-------------------------------------------------------------------
    # TOOL SCORING
    # TOOL: Future Inferred Narration of Events, FINE
    #-------------------------------------------------------------------

    if submit4 and language == "English":
        Q_response = ""
        Q_rawdata = name + "," + str(age) + ","

        Q_rawdata = Q_rawdata + "Q1: Something you always wanted happens.=" + Q1 + ","
        Q_rawdata = Q_rawdata + "Q2: A valued possession is damaged.=" + Q2 + ","
        Q_rawdata = Q_rawdata + "Q3: You have an argument/disagreement with someone.=" + Q3 + ","
        Q_rawdata = Q_rawdata + "Q4: You go on vacation.=" + Q4 + ","
        Q_rawdata = Q_rawdata + "Q5: You break something.=" + Q5 + ","
        Q_rawdata = Q_rawdata + "Q6: You are successful.=" + Q6 + ","
        Q_rawdata = Q_rawdata + "Q7: An important relationship changes.=" + Q7 + ","
        Q_rawdata = Q_rawdata + "Q8: You move.=" + Q8 + ","
        Q_rawdata = Q_rawdata + "Q9: You forgive.=" + Q9 + ","
        Q_rawdata = Q_rawdata + "Q10: You go to court.=" + Q10 + ","
        Q_rawdata = Q_rawdata + "Q11: You go to the doctor.=" + Q11 + ","
        Q_rawdata = Q_rawdata + "Q12: You find something you have been looking for.=" + Q12 + ","
        Q_rawdata = Q_rawdata + "Q13: You are forgiven and feel understood.=" + Q13 + ","
        Q_rawdata = Q_rawdata + "Q14: You believe life is on track to accomplish what?=" + Q14
    
        st.markdown("For additional information and resources, please visit: [US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")

    #-------------------------------------------------------------------
    # TOOL SCORING
    # TOOL: Competency to Stand Trial
    #-------------------------------------------------------------------

    if submit6 and language == "English":
        Q_total = 0
        Q_rawdata = name + "," + str(age) + ","

        # Question 11 scored in reverse.
        if Q1 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q1:Does the defendant remember officers of the court?=Cannot Answer,"
        elif Q1 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q1:Does the defendant remember officers of the court?=Affirmative of Ability,"
        elif Q1 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q1:Does the defendant remember officers of the court?=Compromised,"
        elif Q1 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q1:Does the defendant remember officers of the court?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q1:Does the defendant remember officers of the court?=No Answer,"
        
        if Q2 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q2:Does the defendant remember their own counsel and team members?=Cannot Answer,"
        elif Q2 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q2:Does the defendant remember their own counsel and team members?=Affirmative of Ability,"
        elif Q2 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q2:Does the defendant remember their own counsel and team members?=Compromised,"
        elif Q2 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q2:Does the defendant remember their own counsel and team members?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q2:Does the defendant remember their own counsel and team members?=No Answer,"

        if Q3 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q3:Does the defendant follow advisement, such as not discussing their case with anyone not involved while it is being adjudicated?=Cannot Answer,"
        elif Q3 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q3:Does the defendant follow advisement, such as not discussing their case with anyone not involved while it is being adjudicated?=Affirmative of Ability,"
        elif Q3 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q3:Does the defendant follow advisement, such as not discussing their case with anyone not involved while it is being adjudicated?=Compromised,"
        elif Q3 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q3:Does the defendant follow advisement, such as not discussing their case with anyone not involved while it is being adjudicated?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q3:Does the defendant follow advisement, such as not discussing their case with anyone not involved while it is being adjudicated?=No Answer,"

        if Q4 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q4:Does the defendant recall prior conversations and can explain why their perceptions have changed?=Cannot Answer,"
        elif Q4 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q4:Does the defendant recall prior conversations and can explain why their perceptions have changed?=Affirmative of Ability,"
        elif Q4 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q4:Does the defendant recall prior conversations and can explain why their perceptions have changed?=Compromised,"
        elif Q4 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q4:Does the defendant recall prior conversations and can explain why their perceptions have changed?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q4:Does the defendant recall prior conversations and can explain why their perceptions have changed?=No Answer,"

        if Q5 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q5:In the investigation, was the defendant able to answer the questions asked?=Cannot Answer,"
        elif Q5 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q5:In the investigation, was the defendant able to answer the questions asked?=Affirmative of Ability,"
        elif Q5 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q5:In the investigation, was the defendant able to answer the questions asked?=Compromised,"
        elif Q5 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q5:In the investigation, was the defendant able to answer the questions asked?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q5:In the investigation, was the defendant able to answer the questions asked?=No Answer,"

        if Q6 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q6:Did the defendant appear to understand the seriousness of the accusations or allegations?=Cannot Answer,"
        elif Q6 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q6:Did the defendant appear to understand the seriousness of the accusations or allegations?=Affirmative of Ability,"
        elif Q6 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q6:Did the defendant appear to understand the seriousness of the accusations or allegations?=Compromised,"
        elif Q6 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q6:Did the defendant appear to understand the seriousness of the accusations or allegations?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q6:Did the defendant appear to understand the seriousness of the accusations or allegations?=No Answer,"
        
        if Q7 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q7:Do you believe the defendant can assist counsel or provide information addressing the circumstances of the current charges being considered?=Cannot Answer,"
        elif Q7 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q7:Do you believe the defendant can assist counsel or provide information addressing the circumstances of the current charges being considered?=Affirmative of Ability,"
        elif Q7 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q7:Do you believe the defendant can assist counsel or provide information addressing the circumstances of the current charges being considered?=Compromised,"
        elif Q7 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q7:Do you believe the defendant can assist counsel or provide information addressing the circumstances of the current charges being considered?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q7:Do you believe the defendant can assist counsel or provide information addressing the circumstances of the current charges being considered?=No Answer,"

        if Q8 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q8:Does the defendant have better interactions with others that you work with?=Cannot Answer,"
        elif Q8 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q8:Does the defendant have better interactions with others that you work with?=Affirmative of Ability,"
        elif Q8 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q8:Does the defendant have better interactions with others that you work with?=Compromised,"
        elif Q8 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q8:Does the defendant have better interactions with others that you work with?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q8:Does the defendant have better interactions with others that you work with?=No Answer,"

        if Q9 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q9:Is the defendant able to calm down if needed?=Cannot Answer,"
        elif Q9 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q9:Is the defendant able to calm down if needed?=Affirmative of Ability,"
        elif Q9 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q9:Is the defendant able to calm down if needed?=Compromised,"
        elif Q9 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q9:Is the defendant able to calm down if needed?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q9:Is the defendant able to calm down if needed?=No Answer,"

        if Q10 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q10:If the defendant is acting inappropriately, is counsel, the bailiff, sheriff, marshal, or judge able to address the conduct of the defendant in a manner that facilitates due process?=Cannot Answer,"
        elif Q10 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q10:If the defendant is acting inappropriately, is counsel, the bailiff, sheriff, marshal, or judge able to address the conduct of the defendant in a manner that facilitates due process?=Affirmative of Ability,"
        elif Q10 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q10:If the defendant is acting inappropriately, is counsel, the bailiff, sheriff, marshal, or judge able to address the conduct of the defendant in a manner that facilitates due process?=Compromised,"
        elif Q10 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q10:If the defendant is acting inappropriately, is counsel, the bailiff, sheriff, marshal, or judge able to address the conduct of the defendant in a manner that facilitates due process?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q10:If the defendant is acting inappropriately, is counsel, the bailiff, sheriff, marshal, or judge able to address the conduct of the defendant in a manner that facilitates due process?=No Answer,"

        # Reverse scored.
        if Q11 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q11:Do you believe court outbursts by the defendant are intentional?=Cannot Answer,"
        elif Q11 == "Affirmative of Ability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q11:Do you believe court outbursts by the defendant are intentional?=Affirmative of Ability,"
        elif Q11 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q11:Do you believe court outbursts by the defendant are intentional?=Compromised,"
        elif Q11 == "Inability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q11:Do you believe court outbursts by the defendant are intentional?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q11:Do you believe court outbursts by the defendant are intentional?=No Answer,"

        if Q12 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q12:Does the defendant respond appropriately to those present in the courthouse?=Cannot Answer,"
        elif Q12 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q12:Does the defendant respond appropriately to those present in the courthouse?=Affirmative of Ability,"
        elif Q12 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q12:Does the defendant respond appropriately to those present in the courthouse?=Compromised,"
        elif Q12 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q12:Does the defendant respond appropriately to those present in the courthouse?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q12:Does the defendant respond appropriately to those present in the courthouse?=No Answer,"

        if Q13 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q13:Does the defendant appear to comprehend what is taking place?=Cannot Answer,"
        elif Q13 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q13:Does the defendant appear to comprehend what is taking place?=Affirmative of Ability,"
        elif Q13 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q13:Does the defendant appear to comprehend what is taking place?=Compromised,"
        elif Q13 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q13:Does the defendant appear to comprehend what is taking place?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q13:Does the defendant appear to comprehend what is taking place?=No Answer,"

        if Q14 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q14:Does the defendant appear as if in their own world, responding to internal stimuli inappropriately, such as laughing, talking to themselves, or uttering unrestrained words or statements?=Cannot Answer,"
        elif Q14 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q14:Does the defendant appear as if in their own world, responding to internal stimuli inappropriately, such as laughing, talking to themselves, or uttering unrestrained words or statements?=Affirmative of Ability,"
        elif Q14 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q14:Does the defendant appear as if in their own world, responding to internal stimuli inappropriately, such as laughing, talking to themselves, or uttering unrestrained words or statements?=Compromised,"
        elif Q14 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q14:Does the defendant appear as if in their own world, responding to internal stimuli inappropriately, such as laughing, talking to themselves, or uttering unrestrained words or statements?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q14:Does the defendant appear as if in their own world, responding to internal stimuli inappropriately, such as laughing, talking to themselves, or uttering unrestrained words or statements?=No Answer,"

        if Q15 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q15:Are others uneasy in the presence of the defendant as if they may suddenly act inappropriately, whether verbally or physically?=Cannot Answer,"
        elif Q15 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q15:Are others uneasy in the presence of the defendant as if they may suddenly act inappropriately, whether verbally or physically?=Affirmative of Ability,"
        elif Q15 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q15:Are others uneasy in the presence of the defendant as if they may suddenly act inappropriately, whether verbally or physically?=Compromised,"
        elif Q15 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q15:Are others uneasy in the presence of the defendant as if they may suddenly act inappropriately, whether verbally or physically?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q15:Are others uneasy in the presence of the defendant as if they may suddenly act inappropriately, whether verbally or physically?=No Answer,"

        if Q16 == "Cannot Answer": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q16:Does the defendant remember the charges with breaks in contact?=Cannot Answer,"
        elif Q16 == "Affirmative of Ability":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q16:Does the defendant remember the charges with breaks in contact?=Affirmative of Ability,"
        elif Q16 == "Compromised":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q16:Does the defendant remember the charges with breaks in contact?=Compromised,"
        elif Q16 == "Inability":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q16:Does the defendant remember the charges with breaks in contact?=Inability,"
        else:
            Q_rawdata = Q_rawdata + "Q16:Does the defendant remember the charges with breaks in contact?=No Answer,"
        
        # st.markdown("For additional information and resources, please visit: [US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")
        Q_rawdata = Q_rawdata + "Score=" + str(Q_total)

    #-------------------------------------------------------------------
    # TOOL SCORING
    # TOOL: Perceptions of Concern, POC
    #-------------------------------------------------------------------

    if submit7 and language == "English":
        Q_response = ""
        Q_rawdata = name + "," + str(age) + ","

        Q_rawdata = Q_rawdata + "Q1: Is there an individual or group causing you to fear for your safety or the safety of others?=" + Q1 + ","
        Q_rawdata = Q_rawdata + "Q2: Have you observed any behaviors or incidents of concern? Please describe them briefly (as if writing a text message).=" + Q2 + ","
        Q_rawdata = Q_rawdata + "Q3: Have you heard or read anything (in person, online, or in writing) suggestive of potential harm or violence? Please share what was said and where it was found.=" + Q3 + ","
        Q_rawdata = Q_rawdata + "Q4: Are you aware of this person/group possessing or mentioning weapons (firearms, etc.), or have you heard reports of gunfire or explosions?=" + Q4 + ","
        Q_rawdata = Q_rawdata + "Q5: Has the individual shown signs of instability, such as extreme mood swings, sudden isolation, or reactions to a major personal loss (job, relationship, etc.)?=" + Q5 + ","
        Q_rawdata = Q_rawdata + "Q6: Does this person/group target specific individuals or communities with blame, insults, or expressions of hatred?=" + Q6 + ","
        Q_rawdata = Q_rawdata + "Q7: Has this situation impacted your daily routine, physical health (sleep/stress), or caused you to change your habits to avoid contact?=" + Q7 + ","
        Q_rawdata = Q_rawdata + "Q8: Based on what you know, what is the \"story\" of what might happen? Who is involved and what is the specific concern?=" + Q8 + ","
        Q_rawdata = Q_rawdata + "Q9: What intervention or solution do you believe would best resolve this conflict in your neighborhood or workplace?=" + Q9 + ","
    
        # st.markdown("For additional information and resources, please visit: [US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")

    #-------------------------------------------------------------------
    # TOOL SCORING
    # TOOL: Perceptions of Concern, POC, in Spanish
    #-------------------------------------------------------------------

    if submit7 and language == "Spanish":
        Q_response = ""
        Q_rawdata = name + "," + str(age) + ","

        Q_rawdata = Q_rawdata + "Q1: ¿Existe alguna persona o grupo que le haga temer por su seguridad o la de los demás?=" + Q1 + ","
        Q_rawdata = Q_rawdata + "Q2: ¿Ha observado algún comportamiento o incidente preocupante? Por favor, descríbalos brevemente (como si escribiera un mensaje de texto).=" + Q2 + ","
        Q_rawdata = Q_rawdata + "Q3: ¿Ha escuchado o leído algo (en persona, en línea o por escrito) que sugiera un posible daño o violencia? Por favor, comparta lo que se dijo y dónde se encontró.=" + Q3 + ","
        Q_rawdata = Q_rawdata + "Q4: ¿Tiene conocimiento de que esta persona o grupo posea o mencione armas (armas de fuego, etc.), o ha escuchado informes de disparos o explosiones?=" + Q4 + ","
        Q_rawdata = Q_rawdata + "Q5: ¿Ha mostrado el individuo signos de inestabilidad, como cambios extremos de humor, aislamiento repentino o reacciones ante una pérdida personal importante (trabajo, relación, etc.)?=" + Q5 + ","
        Q_rawdata = Q_rawdata + "Q6: ¿Esta persona o grupo ataca a individuos o comunidades específicas con culpas, insultos o expresiones de odio?=" + Q6 + ","
        Q_rawdata = Q_rawdata + "Q7: ¿Ha afectado esta situación su rutina diaria, su salud física (sueño/estrés) o le ha obligado a cambiar sus hábitos para evitar el contacto?=" + Q7 + ","
        Q_rawdata = Q_rawdata + "Q8: Según lo que sabe, ¿cuál es la \"historia\" de lo que podría suceder? ¿Quién está involucrado y cuál es la preocupación específica?=" + Q8 + ","
        Q_rawdata = Q_rawdata + "Q9: ¿Qué intervención o solución cree que resolvería mejor este conflicto en su vecindario o lugar de trabajo?=" + Q9 + ","

    #===================================================================

    #-------------------------------------------------------------------
    # TOOL ASSESSMENT
    # TOOL: Questions About Yourself and Others
    #-------------------------------------------------------------------

    # If submit button is clicked, query the aitam library.            
    if submit1:
        # If form is submitted without a query, stop.
        # QUERY_ENCRYPTED = b'gAAAAABpblkpLk8QZU-YUoN7fenjaVQ9i8ZBwuYIFMeWp_zl4TnSVInqQxIIkDg6TXnBUTqpNZgqSwFomnhoqADofSljkwXoKbvDJBpqkQdKmbiWaE4zKTTlEJXDYiglOZSeW_U2YeouZTcj425PuOs-7TOjAay4k6d_vKbit26hG_tbKcBBEdx9Xtj6HYZWGDgEtQ_WvsAhiCeWauiK0MrGIFx83xoFljciU9I4cRkgIeXYcqYTQ6Ns3cNbyod_vgqwHUH9P4yNUg9BTO6b1k7_0Vrz8aXP9w-GnhJdncheqUXmAUoNlgcI4HfFch8_OPXx3CqoXQe3m_FOjERsm6ctqC5UJQXZ1QiFG08IhlDm8_SoYdMTmo6011uh7m8h0uonXr0YJMzXJuu4q6ffHWQ461jXhSiZZDxx5nsm9Gtxbv0O-oy1O0KNpb8Rs7iS_PFqvLhwzmqPEFIXEiXa2Ls_WMtpOA5ONTXRjxs-KxW0NVZc92AFNFEtPT4-NfZkB_h3Xema1l5vI6cRGp139Iqw3E_wvRn1YguZaF5Y-6uYOR9L8tgiAQFRGLJjlGMa00p4ivZ6rIeGseXKEt97wyELUo0TaigPNPLVJFnC2-hD-RnZTuZKc4YkEJBcLQxmuvW_HuC3u_hnf6hsiongosYPQ2L1fpFPm2317Sf6qmJdf-aMNcR3J5CdTNpVsqoLE2hs1H6yMybeP00F2Y7nvo4gUNCdmyrsU0r6WWpzIdWxsHkznapDPHfaTdDoTvDIQsoBq5mR5X0YYE0Mk8eGATL77AqGjBYEPqSzUjVHL84AuVb3SGZb4mJV-mcZx31q5tiow51Pkjwm5YOqGE4JomNyNBkP2p1JcEjImJ9Wt5lG4MPhCQMrQ6pimf_ah2O_tMV6kJ9I9Ea3fhQazeuuegFFojmVDrbdhMF4GvnxyZ8LdU25BgzRcM9iaELupnyc7tLvur8qTu74dIHIqcJLCWS11CaRqlK4YrAbn0qNCkZd-XgtFh_Z-3pRkQeJFmZ3NAInm3RShzrIBm5FbRWNVNlaR4qhtw9XTKCMlIVxkXSvOXfPiKK7BFevtRpuTQzv5umim22gIPrD3GJlaoBwpceVo22OyNHOe0nM29XrUHumDEUoYIVrTHWmRyRlg6MjULXPes82e9NITzp8RZIwEqS64jey64wmqOUP4wb8G3U9fKfKdhkd7MK5wW8AnN5avJwHD7bCY6bQO3JJBXQaelDnYR0TbWjXFzd2UdWafuLcH6kGqXNY6YgVibp0Lu1EZ-OalsimA_OKFnjfoHkVG0djixQv5xzQsS-Y9MTPTPJ_BnZVjC3wuW1hn-RmqCQFSiqA5u8KIvC9M1u1suoxqZSUZRjhnBbgv1qxES7f50qWttqGJuNrULwrxGQHtiybppR0OTKFEIQsSAk7uv_bTHESHj2KW0SB2uQsn21li_4f4Mn0whPC_ZZcc7pDhhDdMl1Vn7eK6dfwNTZ-ruGAxTvEOxdeMqKAXB2kjCyg9na6DgxEUU1pNXGzyyFiVzwtFS1sCQAdzK1P5U7KXXnq1bYrrmV_bXyDI9c8tjtJ7-THqj_gvZsU73PQYY4ugrIoA-AMQj3io4KwEqtzfs675DxD_GRNpOKh8sJ-GSG1Ap7ziLL-JfGOOTQoPbGxmlUOMDjJRI-VYmMcvTeSOfawDBraOnHvji-Ybp5XmI_XIMPr6H5BFqSQigbGSBxMMs2BzzFl18-NotKJ'
        # key = st.secrets['INSTRUCTION_KEY'].encode()
        # f = Fernet(key)
        # QUERY = f.decrypt(QUERY_ENCRYPTED).decode()
        QUERY = f"""User context:
            - Assessment: Social Connection & Isolation Questionnaire
            - Raw responses: {Q_rawdata} 
            - Total score: {Q_total}
            - Interpretation label from the assessment system (if any): {Q_response}
            - Preferred language: {language}
            
            Task:
            Using only the retrieved content from the vector store—prioritizing:
            1) "US Surgeon General - Our Epidemic of Loneliness and Isolation 2023"
            2) "Cacioppo - Easing Your Way Out of Loneliness.pdf"—
            provide a supportive, concise response in {language} following the “Answer Structure” rules defined in the system instructions. Tailor the response based on the above interpretation label, total score, and raw responses.
            
            Requirements:
            - Include at least one **direct quote** with proper citation (quotation marks + source + year + page/section if available).
            - Do not speculate or use outside knowledge.
            - Be emotionally sensitive and avoid clinical or diagnostic language.
            
            Edge cases:
            - If the retrieved content is insufficient for a safe, useful answer, say so briefly and offer a compassionate general pointer drawn from what *is* available (with citations).
            - If the user language is right-to-left, ensure readability and correct punctuation direction.
            
            Now produce the response."""

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
            st.write("*This instrument is a screening tool, not a diagnostic measure. Scores should never be used in isolation to make clinical, educational, or disciplinary or other life decisions. Every one has both strengths and weaknesses. Use this information to connect with others who might provide useful suggestions and good conversations. Elevated isolation scores may be followed up with  a conversation with clergy, self-help groups, therapists, and health care professionals. This may lead to others interviewing you. Collateral information (family, school, context), and consideration of developmental stage, cultural norms, and access to in-person peers are areas of inquiry. High online engagement does not inherently indicate pathology; interpretation should distinguish between: adaptive online connection vs. avoidant or impairing social withdrawal. If responses suggest significant distress, withdrawal, or difficulties in learning, working and loving consider seeking a comprehensive psychosocial assessment and screening for depression, anxiety, trauma exposure, or bullying.*")
            # st.write("*The guidance and responses provided by this application are AI-generated and informed by the US Surgeon General's report Our Epidemic of Loneliness and Isolation and related professional resources. They are intended for informational and educational purposes only and do not constitute legal advice, official policy interpretation, or a substitute for professional judgment. Users should consult their professional policies, state regulations, or legal counsel for authoritative guidance on loneliness and isolation matters. This tool is designed to assist, not replace, professional decision-making or formal review processes.*")
        elif language == "Spanish":
            st.markdown("#### Qué Sopa AI Información")
            st.write("*Este instrumento es una herramienta de detección, no una medida diagnóstica. Los puntajes nunca deben utilizarse de manera aislada para tomar decisiones clínicas, educativas, disciplinarias u otras decisiones de vida. Todas las personas tienen fortalezas y debilidades. Use esta información para conectarse con otros que puedan ofrecer sugerencias útiles y buenas conversaciones. Los puntajes elevados de aislamiento pueden ser seguidos por una conversación con líderes religiosos, grupos de autoayuda, terapeutas y profesionales de la salud. Esto puede llevar a que otras personas le realicen entrevistas. La información colateral (familia, escuela, contexto) y la consideración de la etapa de desarrollo, las normas culturales y el acceso a compañeros en persona son áreas de indagación. Un alto nivel de participación en línea no indica inherentemente una patología; la interpretación debe distinguir entre conexión en línea adaptativa versus retraimiento social evitativo o perjudicial. Si las respuestas sugieren angustia significativa, retraimiento o dificultades para aprender, trabajar o amar, considere buscar una evaluación psicosocial integral y una detección de depresión, ansiedad, exposición a trauma o acoso escolar.*")
            # st.write("*La información y las respuestas proporcionadas por esta aplicación son generadas por IA y se basan en el informe del Cirujano General de EE. UU., Nuestro Epidemia de Soledad y Aislamiento, y en recursos profesionales relacionados. Están destinadas únicamente a fines informativos y educativos y no constituyen asesoramiento legal, interpretación oficial de políticas ni un sustituto del juicio profesional. Los usuarios deben consultar sus políticas profesionales, regulaciones estatales o asesoría legal para obtener orientación autorizada sobre asuntos de soledad y aislamiento. Esta herramienta está diseñada para asistir, no para reemplazar, la toma de decisiones profesional o los procesos de revisión formal.*")
            
        st.markdown(cleaned_response)

    #-------------------------------------------------------------------
    # TOOL ASSESSMENT
    # TOOL: My Feelings and Needs, NEIL Child Version
    #-------------------------------------------------------------------

    elif submit2:
        QUERY = f"""User context:
            - Assessment: My Feelings and Needs (NEIL Child Version)
            - Raw responses: {Q_rawdata} 
            - Total score: {Q_total}
            - Interpretation label from the assessment system (if any): {Q_response}
            - Preferred language: {language}
            
            Task:
            Using only the retrieved content from the vector store—prioritizing:
            1) "US Surgeon General - Our Epidemic of Loneliness and Isolation 2023"
            2) "Cacioppo - Easing Your Way Out of Loneliness.pdf"—
            provide a supportive, concise response in {language} following the “Answer Structure” rules defined in the system instructions. Tailor the response based on the above interpretation label, total score, and raw responses.
            
            Requirements:
            - Include at least one **direct quote** with proper citation (quotation marks + source + year + page/section if available).
            - Do not speculate or use outside knowledge.
            - Be emotionally sensitive and avoid clinical or diagnostic language.
            
            Edge cases:
            - If the retrieved content is insufficient for a safe, useful answer, say so briefly and offer a compassionate general pointer drawn from what *is* available (with citations).
            - If the user language is right-to-left, ensure readability and correct punctuation direction.
            
            Now produce the response."""

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
            st.write("*This instrument is a screening tool, not a diagnostic measure. Scores should never be used in isolation to make clinical, educational, or disciplinary or other life decisions. Every one has both strengths and weaknesses. Use this information to connect with others who might provide useful suggestions and good conversations. Elevated isolation scores may be followed up with  a conversation with clergy, self-help groups, therapists, and health care professionals. This may lead to others interviewing you. Collateral information (family, school, context), and consideration of developmental stage, cultural norms, and access to in-person peers are areas of inquiry. High online engagement does not inherently indicate pathology; interpretation should distinguish between: adaptive online connection vs. avoidant or impairing social withdrawal. If responses suggest significant distress, withdrawal, or difficulties in learning, working and loving consider seeking a comprehensive psychosocial assessment and screening for depression, anxiety, trauma exposure, or bullying.*")
            # st.write("*The guidance and responses provided by this application are AI-generated and informed by the US Surgeon General's report Our Epidemic of Loneliness and Isolation and related professional resources. They are intended for informational and educational purposes only and do not constitute legal advice, official policy interpretation, or a substitute for professional judgment. Users should consult their professional policies, state regulations, or legal counsel for authoritative guidance on loneliness and isolation matters. This tool is designed to assist, not replace, professional decision-making or formal review processes.*")
        elif language == "Spanish":
            st.markdown("#### Qué Sopa AI Información")
            st.write("*Este instrumento es una herramienta de detección, no una medida diagnóstica. Los puntajes nunca deben utilizarse de manera aislada para tomar decisiones clínicas, educativas, disciplinarias u otras decisiones de vida. Todas las personas tienen fortalezas y debilidades. Use esta información para conectarse con otros que puedan ofrecer sugerencias útiles y buenas conversaciones. Los puntajes elevados de aislamiento pueden ser seguidos por una conversación con líderes religiosos, grupos de autoayuda, terapeutas y profesionales de la salud. Esto puede llevar a que otras personas le realicen entrevistas. La información colateral (familia, escuela, contexto) y la consideración de la etapa de desarrollo, las normas culturales y el acceso a compañeros en persona son áreas de indagación. Un alto nivel de participación en línea no indica inherentemente una patología; la interpretación debe distinguir entre conexión en línea adaptativa versus retraimiento social evitativo o perjudicial. Si las respuestas sugieren angustia significativa, retraimiento o dificultades para aprender, trabajar o amar, considere buscar una evaluación psicosocial integral y una detección de depresión, ansiedad, exposición a trauma o acoso escolar.*")
            # st.write("*La información y las respuestas proporcionadas por esta aplicación son generadas por IA y se basan en el informe del Cirujano General de EE. UU., Nuestro Epidemia de Soledad y Aislamiento, y en recursos profesionales relacionados. Están destinadas únicamente a fines informativos y educativos y no constituyen asesoramiento legal, interpretación oficial de políticas ni un sustituto del juicio profesional. Los usuarios deben consultar sus políticas profesionales, regulaciones estatales o asesoría legal para obtener orientación autorizada sobre asuntos de soledad y aislamiento. Esta herramienta está diseñada para asistir, no para reemplazar, la toma de decisiones profesional o los procesos de revisión formal.*")
            
        st.markdown(cleaned_response)

    #-------------------------------------------------------------------
    # TOOL ASSESSMENT
    # TOOL: My Feelings and Needs, NEIL Adult Version
    #-------------------------------------------------------------------

    elif submit3:
        QUERY = f"""User context:
            - Assessment: My Feelings and Needs (NEIL Adult Version)
            - Raw responses: {Q_rawdata} 
            - Total score: {Q_total}
            - Interpretation label from the assessment system (if any): {Q_response}
            - Preferred language: {language}
            
            Task:
            Using only the retrieved content from the vector store—prioritizing:
            1) "US Surgeon General - Our Epidemic of Loneliness and Isolation 2023"
            2) "Cacioppo - Easing Your Way Out of Loneliness.pdf"—
            provide a supportive, concise response in {language} following the “Answer Structure” rules defined in the system instructions. Tailor the response based on the above interpretation label, total score, and raw responses.
            
            Requirements:
            - Include at least one **direct quote** with proper citation (quotation marks + source + year + page/section if available).
            - Do not speculate or use outside knowledge.
            - Be emotionally sensitive and avoid clinical or diagnostic language.
            
            Edge cases:
            - If the retrieved content is insufficient for a safe, useful answer, say so briefly and offer a compassionate general pointer drawn from what *is* available (with citations).
            - If the user language is right-to-left, ensure readability and correct punctuation direction.
            
            Now produce the response."""

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
            st.write("*This instrument is a screening tool, not a diagnostic measure. Scores should never be used in isolation to make clinical, educational, or disciplinary or other life decisions. Every one has both strengths and weaknesses. Use this information to connect with others who might provide useful suggestions and good conversations. Elevated isolation scores may be followed up with  a conversation with clergy, self-help groups, therapists, and health care professionals. This may lead to others interviewing you. Collateral information (family, school, context), and consideration of developmental stage, cultural norms, and access to in-person peers are areas of inquiry. High online engagement does not inherently indicate pathology; interpretation should distinguish between: adaptive online connection vs. avoidant or impairing social withdrawal. If responses suggest significant distress, withdrawal, or difficulties in learning, working and loving consider seeking a comprehensive psychosocial assessment and screening for depression, anxiety, trauma exposure, or bullying.*")
            # st.write("*The guidance and responses provided by this application are AI-generated and informed by the US Surgeon General's report Our Epidemic of Loneliness and Isolation and related professional resources. They are intended for informational and educational purposes only and do not constitute legal advice, official policy interpretation, or a substitute for professional judgment. Users should consult their professional policies, state regulations, or legal counsel for authoritative guidance on loneliness and isolation matters. This tool is designed to assist, not replace, professional decision-making or formal review processes.*")
        elif language == "Spanish":
            st.markdown("#### Qué Sopa AI Información")
            st.write("*Este instrumento es una herramienta de detección, no una medida diagnóstica. Los puntajes nunca deben utilizarse de manera aislada para tomar decisiones clínicas, educativas, disciplinarias u otras decisiones de vida. Todas las personas tienen fortalezas y debilidades. Use esta información para conectarse con otros que puedan ofrecer sugerencias útiles y buenas conversaciones. Los puntajes elevados de aislamiento pueden ser seguidos por una conversación con líderes religiosos, grupos de autoayuda, terapeutas y profesionales de la salud. Esto puede llevar a que otras personas le realicen entrevistas. La información colateral (familia, escuela, contexto) y la consideración de la etapa de desarrollo, las normas culturales y el acceso a compañeros en persona son áreas de indagación. Un alto nivel de participación en línea no indica inherentemente una patología; la interpretación debe distinguir entre conexión en línea adaptativa versus retraimiento social evitativo o perjudicial. Si las respuestas sugieren angustia significativa, retraimiento o dificultades para aprender, trabajar o amar, considere buscar una evaluación psicosocial integral y una detección de depresión, ansiedad, exposición a trauma o acoso escolar.*")
            # st.write("*La información y las respuestas proporcionadas por esta aplicación son generadas por IA y se basan en el informe del Cirujano General de EE. UU., Nuestro Epidemia de Soledad y Aislamiento, y en recursos profesionales relacionados. Están destinadas únicamente a fines informativos y educativos y no constituyen asesoramiento legal, interpretación oficial de políticas ni un sustituto del juicio profesional. Los usuarios deben consultar sus políticas profesionales, regulaciones estatales o asesoría legal para obtener orientación autorizada sobre asuntos de soledad y aislamiento. Esta herramienta está diseñada para asistir, no para reemplazar, la toma de decisiones profesional o los procesos de revisión formal.*")
            
        st.markdown(cleaned_response)

    #-------------------------------------------------------------------
    # TOOL ASSESSMENT
    # TOOL: Daily Digital Connected Life, DDCL
    #-------------------------------------------------------------------

    elif submit5 and language == "English":
        QUERY = f"""
            # User context:
                - Assessment: Daily Digital Connected Life (DDCL)
                - Raw responses: {Q_rawdata}
                - Preferred language: {language}
            
            Task:
            Using only the retrieved content from the vector store—prioritizing:
            1) "US Surgeon General - Our Epidemic of Loneliness and Isolation 2023"
            2) "Cacioppo - Easing Your Way Out of Loneliness.pdf"—
            provide a supportive, concise response in {language} following the “Answer Structure” rules defined in the system instructions. Tailor the response based on the raw responses.
            
            Requirements:
            - Include at least one **direct quote** with proper citation (quotation marks + source + year + page/section if available).
            - Do not speculate or use outside knowledge.
            - Be emotionally sensitive and avoid clinical or diagnostic language.
            
            Edge cases:
            - If the retrieved content is insufficient for a safe, useful answer, say so briefly and offer a compassionate general pointer drawn from what *is* available (with citations).
            - If the user language is right-to-left, ensure readability and correct punctuation direction.
            
            Now produce the response."""

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

        st.markdown("#### Qué Sopa AI Guidance")
        st.write("*This instrument is a screening tool, not a diagnostic measure. Scores should never be used in isolation to make clinical, educational, or disciplinary or other life decisions. Every one has both strengths and weaknesses. Use this information to connect with others who might provide useful suggestions and good conversations. Elevated isolation scores may be followed up with  a conversation with clergy, self-help groups, therapists, and health care professionals. This may lead to others interviewing you. Collateral information (family, school, context), and consideration of developmental stage, cultural norms, and access to in-person peers are areas of inquiry. High online engagement does not inherently indicate pathology; interpretation should distinguish between: adaptive online connection vs. avoidant or impairing social withdrawal. If responses suggest significant distress, withdrawal, or difficulties in learning, working and loving consider seeking a comprehensive psychosocial assessment and screening for depression, anxiety, trauma exposure, or bullying.*")            
        st.markdown(cleaned_response)

    #-------------------------------------------------------------------
    # TOOL ASSESSMENT
    # TOOL: Future Inferred Narration of Events, FINE
    #-------------------------------------------------------------------

    elif submit4 and language == "English":
        QUERY = f"""
            # User context:
                - Assessment: Future Inferred Narration of Events (FINE)
                - Raw scenario-writing responses: {Q_rawdata}
                - Preferred language: {language}
            
            # Task
            Analyze the user’s scenario‑writing responses to identify narrative patterns that may reflect how they currently imagine their future. Focus on descriptive, neutral interpretation of what appears in the text—not on inferring clinical meaning.
            Your analysis should examine content, structure, and tone, specifically including:

            # Narrative Content & Roles
            + The user’s perceived role (e.g., hero, victim, helper, observer).
            + Any indication of revenge motivation or desire for payback.
            + Whether the narrative presents the user as having control, lacking control, or alternating between the two.
            + The balance of positive vs. negative anticipated outcomes.
            + Expressions of hope, fear, uncertainty, despair, or optimism.
            + Whether the narrative emphasizes threat, safety, challenge, opportunity, or avoidance.

            # Emotional & Thematic Tone
            + Overall emotional atmosphere (e.g., dark, bleak, neutral, hopeful, mixed).
            + The relative balance of “dark versus hopeful” elements.
            + Depictions of interpersonal dynamics such as conflict, cooperation, disconnection, or alliance.

            Linguistic & Structural Features
            + Grammar clarity, complexity, and approximate written grade‑level.
            + Indications of coherence, organization, or fragmentation in the narrative.
            + Dominant metaphors, symbols, or imagery that may reflect worldview or mindset.
            + Any unusual narrative elements, phrasing, or structure—described neutrally and without implying pathology.
            + Indications of perceived rapid change, stagnation, uncertainty, or unexpected shifts in the future.

            # Requirements
            + Base all interpretations only on the text provided by the user.
            + Do not diagnose, imply mental health conditions, or make clinical judgments.
            + Use observational, non‑directive language (e.g., “The narrative describes…”, “This may suggest…”).
            + Avoid speculation beyond what is explicitly present.
            + Use the user’s preferred language for the entire output.

            # Output Structure
            1. Summary of Key Themes: A concise overview of the major narrative, emotional, and structural patterns observed.
            2. Interpretive Insights: A neutral explanation of what these patterns may suggest about how the user is imagining their future—without implying certainty, evaluation, or clinical interpretation.
            3. Linguistic Observations: Brief notes on grammar, grade‑level, clarity, and any unusual or striking structural features.
            4. Reflective Prompt (Optional): Provide one gentle, non‑directive question the user may consider (e.g., “What part of this imagined future feels most meaningful for you right now?”).
            
            # Edge Cases
            If the responses are too brief, vague, contradictory, or minimal to derive patterns, state this clearly and summarize whatever can be safely observed.            

            Now produce the thematic analysis.
            """
        
        # Setup output columns to display results.
        # answer_col, sources_col = st.columns(2)
        # Create new client for this submission.
        client2 = OpenAI(api_key=openai_api_key)
        # Query the aitam library vector store and include internet
        # serach results.
        with st.spinner('Searching...'):
            response2 = client2.responses.create(
                instructions = "Follow query instructions",
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

        st.markdown("#### Qué Sopa AI Guidance")
        st.write("*This instrument is a screening tool, not a diagnostic measure. Guidance should never be used in isolation to make clinical, educational, or disciplinary or other life decisions. Every one has both strengths and weaknesses. Use this information to connect with others who might provide useful suggestions and good conversations, such as clergy, self-help groups, therapists, and health care professionals. This may lead to others interviewing you. Collateral information (family, school, context), and consideration of developmental stage, cultural norms, and access to in-person peers are areas of inquiry. If responses suggest significant distress, withdrawal, or difficulties in learning, working and loving consider seeking a comprehensive psychosocial assessment and screening for depression, anxiety, trauma exposure, or bullying.*")            
        st.markdown(cleaned_response)

    #-------------------------------------------------------------------
    # TOOL ASSESSMENT
    # TOOL: Competency to Stand Trial
    #-------------------------------------------------------------------

    elif submit6 and language == "English":
        QUERY = f"""
            # User context:
                - Assessment: Competency to Stand Trial
                - Raw scenario-writing responses: {Q_rawdata}
                - Preferred language: {language}
            
            # Purpose:
            Review responses to assess whether the defendant can understand legal proceedings and communicate rationally with counsel to assist in their defense.

            # What to Evaluate
            Assess responses for evidence of:
            + Understanding of the Legal Process - Basic awareness of court roles, charges, and consequences
            + Communication with Counsel - Ability to express information, understand explanations, and collaborate with an attorney
            + Rational Thinking - Logical, coherent responses without disorganization or fixed false beliefs that interfere with legal decision‑making
            + Functional Emotional Regulation - Emotional or behavioral factors that may impede working with counsel

            # How to Rate
            Based on overall response patterns (not single answers), classify functioning as:
            + Adequate
            + Questionable
            + Impaired
            Do not assign diagnoses or make legal determinations.

            # Output
            Provide:
            + A brief summary of strengths and concerns
            + An overall impression of ability to assist counsel
            + Notation of any responses requiring clinical follow‑up

            # Requirements
            + Do not diagnose, imply mental health conditions, or make clinical judgments.
            + Use observational, non‑directive language (e.g., “This may suggest…”).
            + Avoid speculation beyond what is explicitly present.
            + Use the user’s preferred language for the entire output.

            Now produce the competency analysis.
            """
        
        # Setup output columns to display results.
        # answer_col, sources_col = st.columns(2)
        # Create new client for this submission.
        client2 = OpenAI(api_key=openai_api_key)
        # Query the aitam library vector store and include internet
        # serach results.
        with st.spinner('Searching...'):
            response2 = client2.responses.create(
                instructions = "Follow query instructions",
                input = QUERY,
                model = model,
                temperature = 0.6,
                # text={
                #     "verbosity": "low"
                # },
                tools = [{
                            "type": "file_search",
                            "vector_store_ids": [VECTOR_STORE_ID2],
                }],
                include=["output[*].file_search_call.search_results"]
            )
        # Write response to the answer column.    
        # with answer_col:
        try:
            cleaned_response = re.sub(r'【.*?†.*?】', '', response2.output_text) #output[1].content[0].text)
        except:
            cleaned_response = re.sub(r'【.*?†.*?】', '', response2.output[1].content[0].text)

        st.markdown("#### Qué Sopa AI Guidance")
        st.write("*This analysis supports, but does not replace, a qualified forensic evaluator’s opinion or the court’s determination of competency.*")            
        st.markdown(cleaned_response)

    #-------------------------------------------------------------------
    # TOOL ASSESSMENT
    # TOOL: Perceptions of Concern, POC
    #-------------------------------------------------------------------

    elif submit7:
        QUERY = f"""
            # User context:
                - Assessment: Perceptions of Concern (POC)
                - Raw scenario-writing responses: {Q_rawdata}
                - Preferred language: {language}
            
            # Purpose
            Analyze user responses from the Perceptions of Concern Questionnaire to identify observable narrative, emotional, and thematic patterns that reflect how the individual understands or describes safety concerns within their environment.
            This analysis supports early awareness and prevention, not judgment or blame, and should remain grounded strictly in the provided text.
            
            # Analysis Scope
            1. Narrative Content & Roles
            Evaluate how the respondent frames people, situations, and outcomes:
            + The respondent’s perceived role (e.g., observer, witness, helper, target, or uncertain role).
            + Descriptions of others (e.g., “person of concern,” peer group, authority figures).
            + Any references to conflict, grievance, or interpersonal tension.
            + Presence of language suggesting retaliation, escalation, or “payback.”
            + Indicators of perceived control, lack of control, or unpredictability in situations.
            + Emphasis on risk vs. safety, including awareness of potential harm or prevention.
            
            2. Safety-Relevant Indicators (Contextual, Not Diagnostic)
            Identify observable elements aligned with prevention and risk awareness:
            + Mentions of specific threats, weapons, or planned actions.
            + References to targets (individuals or groups) or assignment of blame.
            + Indications of behavioral changes, distress, or conflict escalation.
            + Evidence of“leakage” (sharing of concerning intent, stories, or warnings).
            + Descriptions of impact on the respondent (e.g., fear, avoidance, heightened awareness).
            
            These observations should remain descriptive and may align with structured risk signals used in prevention models, such as imminence, capability, and intent, but should not assign scores or risk levels unless explicitly instructed.
            
            3. Emotional & Thematic Tone
            Assess the overall tone and emotional qualities of the response:
            + General atmosphere (e.g., concerned, neutral, tense, uncertain, reassured).
            + Presence of fear, unease, vigilance, confidence, or trust/distrust.
            + Balance between concern vs. reassurance.
            + Depictions of social dynamics (e.g., conflict, isolation, cooperation, support).
            
            4. Linguistic & Structural Features
            Review how the response is expressed:
            + Clarity, grammar, and approximate communication complexity.
            + Organization and coherence (structured vs. fragmented responses).
            + Repetition, emphasis patterns, or notable phrasing.
            + Use of imagery, metaphors, or narrative framing (if present).
            + Indicators of perceived change over time (e.g., escalation, stability, uncertainty).
            
            # Operational Requirements
            + Base all observations only on the provided text.
            + Use neutral, descriptive, and non-directive language:
            ++ Examples:“The response describes…”,“This may suggest…”,“The respondent notes…”
            + Do not:
            ++ Diagnose or imply mental health conditions
            ++ Assign intent beyond what is explicitly stated
            ++ Make judgments about credibility or truth
            + Avoid speculation; clearly distinguish between explicit statements and cautious interpretation.
            + Maintain language consistency with the user’s input.
            
            # Output Structure
            1. Summary of Key Themes
            Provide a concise overview of:
            + Primary concerns raised
            + Notable narrative patterns
            + Overall tone and focus (safety, conflict, uncertainty, etc.)
            
            2. Observational Insights
            Offer a neutral interpretation of what the patterns may indicate about:
            + How the respondent perceives safety or risk
            + Their awareness of potential threats or prevention needs
            + Interpersonal or environmental dynamics described
            
            3. Safety-Relevant Observations
            Summarize any clearly identifiable prevention signals, such as:
            + Mentioned threats, targets, or concerning behaviors
            + Descriptions of escalation, distress, or warning signs
            + Reported personal impact (e.g., avoidance, fear, behavioral changes)
            
            4. Linguistic Observations
            Briefly note:
            + Clarity and organization
            + Language complexity
            + Any unusual or notable structural features
            
            5. Reflective Prompt (Optional)
            Provide one gentle, non-directive question to support reflection:
            + Example:“What part of this situation feels most important to address right now?”
            
            # Edge Case Handling
            If responses are:
            + Very brief
            + Vague or unclear
            + Contradictory
            
            Then:
            + State that pattern identification is limited
            + Describe only what is explicitly observable
            + Avoid extending interpretation beyond available information
            
            # Alignment with Prevention Framework
            This analysis supports a broader threat assessment and prevention workflow, where AI serves as an initial pattern-recognition layer, not a final decision-maker. [Facilitator Guide | Word]
            Any significant safety indicators identified here may be reviewed by a designated team for further context and appropriate action.
            
            # Final Instruction
            Produce a clear, structured, and neutral thematic analysis that prioritizes early awareness, clarity, and responsible interpretation of the respondent’s concerns.
            """
        
        # Setup output columns to display results.
        # answer_col, sources_col = st.columns(2)
        # Create new client for this submission.
        client2 = OpenAI(api_key=openai_api_key)
        # Query the aitam library vector store and include internet
        # serach results.
        with st.spinner('Searching...'):
            response2 = client2.responses.create(
                instructions = "Follow query instructions",
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

        st.markdown("#### Qué Sopa AI Guidance")
        st.write("*This instrument is a screening tool, not a diagnostic measure. Guidance should never be used in isolation to make clinical, educational, or disciplinary or other life decisions. Every one has both strengths and weaknesses. Use this information to connect with others who might provide useful suggestions and good conversations, such as clergy, self-help groups, therapists, and health care professionals. This may lead to others interviewing you. Collateral information (family, school, context), and consideration of developmental stage, cultural norms, and access to in-person peers are areas of inquiry. If responses suggest significant distress, withdrawal, or difficulties in learning, working and loving consider seeking a comprehensive psychosocial assessment and screening for depression, anxiety, trauma exposure, or bullying.*")            
        st.markdown(cleaned_response)

    #===================================================================

elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
