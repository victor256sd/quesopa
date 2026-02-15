#-------------------------------------------------------------------
# Copyright (c) 2026 victor256sd
# All rights reserved.
#
# Changelog:
#
# 2/15/2026: Started programming Future Inferred Narration of 
# Events (FINE) tool based on meeting with Glenn and materials 
# provided on 2/13/2026.
#
# 2/13/2026, 2/14/2026: Modified NEIL child version description, 
# added two questions at the end, and adjusted language on multiple 
# question numbers (Glenn email, 2/12/2026). Added NEIL adult 
# version (Glenn email, 2/12/2026).
#
# 1/26/2026: Modified page to accommodate the loneliness and NEIL
# child version surveys.
#
# 1/21/2026: Modifications to survey, question wording and adding
# two questions, verbiage for prompts changed, interpretation of
# scores changed (Glenn email, 1/21/2026).
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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpeDtGCB8EbbnDDzlWIzayPCcwJoxujN9dg-_2QxxlCfu5oeBrXaGoUHOCfOb_OL_U57vHhtHtjsPIoYPjn2TN5WQ0v_NRbF8r4UbsyMMoG_Hl-xaFzjLsT00SAxCA0KL1KMPOpxevnRoUGnHlZ48n0lrDf-1Wccfc7zXPVga_2bOS2J3BefcXM8u7mwbNUbdXJ69eIRAfTybBA57D0mGxodGp_uSR1EYHRVB8K3HjV1BD3FY0F6NKdbgOAd2zhpXD8BwCQBnz4ZQQMIkYgqdlvWwDgh0wNwKSUTMs-7A8I-vurKLvF12AwpBN6KRDZcBBGf49kwKExQa8N7Dnt6xR0XUUJ5Wq_vR0vZaf5jbEI1_E0-At4vrraqbIYHDhQP7xAnjUruhwmRwWN52cY-c8u7Rp8a8XXjciOEngxK2dhrd9KiU89dfShPko8qXVu2Url9UARuWz85YgLH6WChOIFo7DRtfabhiYv7_K36RykMbXITgqLV4AQvfOub1DiBE8lEVp83WqiqKrBVm2_DdDzzQXpuvJ0PizEAH5QAPYOWXqawZBLAqRG90s9PeCqR4ll9rWESPuRb66jWDmTzrzBZy1lWxL78TnW3KlPhOxxtCikc_suUy5DnSdiT_mR7WaQLqlgbwtfub5gMnfO3Ox7HlRF5WCDkJueCx0pj9UrwymGWpucmJk5-_hbCY_ZN0PSPp0lestHyjleSoVgfY23zbZe-VSrENrOcwmBl2no85OPVBshO_7TzfKQ0VUaQqNZyObHjuF_u_ShpVHMX8qF8PiebQBRzxNDkXfXPOoC-eagdSzuyOmLurzSj8C2RibnVPelA9K0hkggohzrgWTgNhA9BDf55P-VPMkT3vnGj6umP0udeWyi_VzcFXHhI7_tgMJtOvycPQv61Hy7GcYu0KWikirerfX9utS1CqonZEn8fqZYfTLTrCm8-5JJPZ1vbp19CpzNi4kNWMuq7ukc4b-L-f_W9yPOV5zY3fU78WWLrxJFN4kaJf1NOk-NFLNWpj8Ia7fvX54lt94oU5DnyzUKXORukwMmKf8SkirawLIzYwepi5mZEFP17IB4iUZdz8nhTbIpgETIoMMga_zGKFdd74541UkUxJ3APgA6AwoJ7rm5RM52lo-7_Hnx656J1rEAQYxmc4OtiTX90hno2gWz3lNO7zXommSf4J2zIJuCEorYI6X2xkF-Pj52fdepz8ExHQEh6CMCyq08cWNQy7Il_5MDsTJSUhxCgukJ0twNN5tW39rry25a5w7Ky2uVJsb1xxF20d4S6BDFT9fL38hudlg9OOWhmJx6ukFGLGywLXdRgsCSNxILuIAyTO8wlNNnh_-AWX-niApUcZ7b8mZQCgHt7vf1k0DZ_ZkgxcqjxjBXLUabKzIB2zadsa_geyEB84M9kFig-j5d_4pCcMWYO-l5rI1d0ydNBNt-PqSNUPX85v2oLb8wvOEqPMfL2Z_H0mmEDp_aQ3AftfE0O-4S9F5ZsjDlJON2lTee2_Oj6sQQHrSqXmb_I-lm7TC1Kr0oEv4dDT8jjrnv8BApjkUVjsPBTpQbONHAPeqF4CA_9h7K79PKoCqXXtAtenHh2Sf0yyfoTkNfWiKdBojTNBdulUlTzEDrI7Tz7Dox3fyBmXX82NZekov1hgMLHgSYTIx2iejdo3r3pHNVI94L0PUcArWoq8oWEWr4HRkhip4jcXVygNDY_7Jen9zB0xa47F0K80VLpbJKTLwF-xvSaSe3bes_aKK-DdY0UvqFxZunXeRfiNJ16_wbTYk2S1edl_8ciJ26AgAO6t-AP8aBBNj7R97f5gztiJG21b-C7z6K4-RoB8wZ0cWH4tCvR8W1VYob1NSsogjqPBvGuLYMtcLaID2UOY4au5dqCSuxSKPXQbKXhJCvtCJNy_Am6L4dRHllyEnzAbcON7-JiQjB63OnrwmWeFldvnN0fidrT0u5JDiAgSRHMWJC65n3CDd7D3OXRMaTxrrNLZ2cVSNXlF_6CjKpJbDnx--a4JxikD_qfOI-cOL2p4NnVLehA6GRQ8T890FH4CfCVZpK49IQSbxJ9dhkkyNKOlPRG5-QZ0vNf_MI4ARd2nGWju8bwYcK0rDIX6ZNKmHZNulxdy6yJqYvmOn_c7C3cl6K5345fG7EX77ucZ_d9_HqfnRxnMIRS_wqJQ3uv6uA9-ILkEPE4jlUnoXg8bFcdfmHJsmJa92PbhHXJsg53n_q_lmG17hnyF-y-xjYXwj6BOdRofxGbUruUimO6V8QQGwl4T8wA5AsVqj9IAlJNHLEfH2Xs-hb58XMfiAd7JT6pJJYCCerwnMfCbBnYilmUvkwPFkmIIBjQVYkWgKOmPTCYMRyDSpI1cp7WoTen-FcHO81fwUbPK00eRSf_jSB2qCk9fZ5J_UD8ArMTQDRhNyQOw-4V7FslhIZ9i4ThoGJ4vYkmcwrn_beKvKSttZej37J0AsIHos52NVYtw7mtiQVOCoNX99oGNmpFDxLSN57AxB1apD9XKbmbtrgBaqgQoZJ3ChNmWFC57xqG7YN0UmvUzOZs5PJifxPqs7KMOgqmW7xFBImRT5aAXgucwDmAbtOm09d3PnhT4V8kQ5v1Vaj04NwqHOWMBU_YWbN6yAHDwP0X__A7IPp-vbpeaqcFKwf7MVk0abCuyFdZInTL5rZ29F-ivWVxa6tJCdVxPVAELB5-_ilq9L9SsLfKKQsCMT8NURuWlo0isH4_KqTDMO_S82OYW1NAj__H_GxhsKxmveR3EI3pU9WMK-nwzjGRJVrk_ry8dU6nTwyJjv5ctEbUR3BR_n4LMDWLnAfzTVEZZUCsWhjxcilgN9sHJ7TCFr27-oXhCkzFz9R1aNNHgCbq_0I-w4doYJVpGI_9LWAOj-A7wEAGTBetii1oxbsgBMTxj7cYOd2oGRL7trBnaGllL15q84IX_yd7_2hKKd_DlUnbdg18WEMfdl_LVJ8WFalaRuQij2utdULVAP8CBHBINKcx4BQMlJE3I4pq2DJDSCbcjrgZedYP_-I3rvscWSUQWqvyv5Wjf1ZjFkF5YGjWqQ-9f378xPTrB5wzd4ef2D5QG9VfcNkv1dSVJdOqd-UN3Fvny-oF2mfMnnFrOMWAxXcHhURhj5FmuX49_AW6lyQdBWiWo9aJWV4c2juHAdg88hYHTNXNfLgdTxcIOixG-u0ONiBEbHWJES_zMFkffOG3VOeP9IXr4LHaFOMWq8g1S8zcPBGHAZb-Oi1stw0Gm1PaE7xQxdwsqkTCsj-N0Ie5DvgfzIFyWaPA6plIIb5xzrGvIbiVvbJOeuORLO9RNLMHW1JVVJarBkGUytIWFj1OlOFFOFBDvyU3M-N3WU1_svYlEr5ZdWzOQkL6PATCL7fceEOeZVYxd5SkE93CHnRxQdf9R1y7CT_jLA0gvy_k9jOYp095RB65iOLzc_DYTPMUX0hvyJbCfd7EMS_BnmqN9aFf6dMmcd5LAyu6KXzswyai8YzXYI-9W4RyKHjMq7zqAEpqIuwIlHuUFBPiyssScLk2MITeQuV9P55I6jjpFXrW5LgaB4zFeSWB3GpDAuSUBfM4M18QtSkQVY9T-pNF2iZqLabpXwNw-DPVuNUsq6wfTcfPqK1YE-O27COMOP-6S57bQI-6hxXXLVMOqa9fzJ2vtL_br-s_SsN0thEZttyhurDqSdgsT7Zod39xEJ8QONyR9Ji-tkgaESIcGzwMy8E8AdlsRnN9BczGDriO5WwCJVdcCLbjGzzSArCFDPb-8rjwbw_Bv0ziZ8dqM68csdrLiOzmgJQn5c--Y3ufaTWE1qfwA6mEvezzmiYO0kDZZN9a5DpdZj6q3mf-Lohf2OnP5apU-7Dy6hQFaz18U2c2iGK8dxHEcRzRcyFCkHr99Gqp8UWQq69oxOb4RvvWg7XwN48UjpC_DuHKIhfJCvUzgvU2yJ9zVNCIkzvL-q0sqGt-SxHNPzX0ZoHeAQdh77StCU-s1Z-xkyUBESTlHQ-qbN64u7CpJRBcAIt7qoCkKm3n5xSh7K7KaYtDK5suhYs1PD2zvGQt3JKW97wi8q42uGqwDVxkOZBDZer-SEOphJ1QAYI-Tmo0yzIpDdEn03H3ooPz_0fTEthJS5EI-tfIy_d5DzlMO_nbf8nuy-a5-dTpkcIz6DPuz8SBV2W5VII5axWIGZGCEJe4CqC0cIF_XUiL4YHvF5J-GMn_DQr0xMj6dai3LFX2YowifWEmkCzLSrBd-ktefyNXkLvBoFrOSNNDvRm3dPS-Uh-DbW7BbHKMeUImCfzDTcCaeRMTq6pSED96JQil3hijkbyqnHtuK7kpsg5O71y04RwxVCHlTopxIloHc-B4fN568fCqvi0eTt0ZfHzWDgshxOnGNaBNMPEcVAkRYAj-8IeztPTc34jEaUuTFbRvcmcwdAV9Rp5GVsaGQOfUkeavsTQU-2cNZORE2okU4P4CYOIQ8eTOhS02pByuvE41n5lcQSr49Z-80CpqyGme22qZMRkB5qbuy9pv5vf3QwtVHlvJu1OKZgAxcX-WrK5ECHG5XoIxo-IUHsUglC2RSiCNSdYeDqDkNIWcCgMriIVtKH-qAY31v-_XUkeBP7jvFQBr74vgBnNk4xEdLk2QuHV-USb6kWqX_G6N1ED3kbsN45Pzl_ziJ9j0PL_sJQGr1ZkadydnPvOJH5aA=='

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()

    # Set page layout and title.
    st.set_page_config(page_title="Qué Sopa AI", page_icon=":hibiscus:", layout="wide")
    st.header(":hibiscus: Qué Sopa AI")
    st.markdown("###### A Starting Point for Understanding Loneliness and Belonging")
    # st.markdown("###### Your starting point for educator ethics")
    st.markdown("*Explore two simple tools that measure how people connect, feel included, or experience loneliness online or in daily life. A child‑friendly version is also available to capture younger children’s emotions and social experiences.*")
    
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

    tool = st.radio("Make a selection:",
        ["Social Connection & Isolation Questionnaire", "My Feelings and Needs (NEIL Child Version)", "My Feelings and Needs (NEIL Adult Version)", "Future Inferred Narration of Events (FINE)"], index=None,
        captions=[
            "A brief, non-diagnostic self-report measure designed to assess perceived social connection, loneliness, and online social engagement. Items are written at a 5th–6th grade reading level and are suitable for minimal-risk survey research.\n",
            "A questionnaire that helps measure how a child has been feeling and connecting with others over the past week.\n",
            "A questionnaire that helps measure how an adult has been feeling and connecting with others over the past month.\n",
            "A scenario writing questionnaire that guides users to imagine detailed narratives of possible future events in order to clarify their current mindset.\n",        ],
    )
    
    # Create loneliness survey form.
    if tool == "Social Connection & Isolation Questionnaire" and language == "English":
        with st.form("yvform"):
            st.write("Please answer each question based on how you usually feel. Choose one response.")
            Q1 = st.selectbox("#1. How often do people respond kindly when you share your feelings or worries?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q2 = st.selectbox("#2. Do you feel that people understand you, encourage you, and know you well?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q3 = st.selectbox("#3. When you want to talk with someone or do something together, is it easy to connect?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q4 = st.selectbox("#4. How often do you feel separate from others, even when you are with them?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q5 = st.selectbox("#5. I have someone to eat with when I want to share a meal.", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q6 = st.selectbox("#6. It is not easy for me to make friends?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q7 = st.selectbox("#7. How often do you wait a long time for others to contact you or reply to your messages?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q8 = st.selectbox("#8. Is it easier for you to play games or watch events by yourself?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q9 = st.selectbox("#9. How often do you feel left out when others get together without inviting you?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q10 = st.selectbox("#10. How often do you feel hurt because you don’t have someone to laugh with or talk to about your thoughts and feelings?", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q11 = st.selectbox("#11. Most of my friends are online and not people I see in person.", ["","Never", "Rarely", "Sometimes", "Often", "Always"])
            Q12 = st.selectbox("#12. I spend most of my time online.", ["","Never", "Rarely", "Sometimes", "Often", "Always"])

            submit1 = st.form_submit_button("Submit")
            submit2 = False
            submit3 = False
            submit4 = False
        
    elif tool == "Social Connection & Isolation Questionnaire" and language == "Spanish":
        with st.form("yvform"):
            st.write("Por favor, responde cada pregunta según cómo te sientes normalmente. Elige una respuesta.")
            Q1 = st.selectbox("#1. ¿Con qué frecuencia las personas responden con amabilidad cuando compartes tus sentimientos o preocupaciones?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q2 = st.selectbox("#2. ¿Sientes que las personas te entienden, te apoyan y te conocen bien?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q3 = st.selectbox("#3. Cuando quieres hablar con alguien o hacer algo juntos, ¿te resulta fácil conectar con esa persona?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q4 = st.selectbox("#4. ¿Con qué frecuencia te sientes separado(a) de los demás, incluso cuando estás con ellos?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q5 = st.selectbox("#5. Tengo a alguien con quien comer cuando quiero compartir una comida.", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q6 = st.selectbox("#6. ¿Te resulta difícil hacer amigos?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q7 = st.selectbox("#7. ¿Con qué frecuencia esperas mucho tiempo a que otras personas se comuniquen contigo o respondan a tus mensajes?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q8 = st.selectbox("#8. ¿Te resulta más fácil jugar o ver eventos tú solo(a)?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q9 = st.selectbox("#9. ¿Con qué frecuencia te sientes excluido(a) cuando otras personas se reúnen sin invitarte?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q10 = st.selectbox("#10. ¿Con qué frecuencia te sientes herido(a) porque no tienes a alguien con quien reír o hablar sobre tus pensamientos y sentimientos?", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q11 = st.selectbox("#11. La mayoría de mis amigos están en línea y no son personas que veo en persona.", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])
            Q12 = st.selectbox("#12. Paso la mayor parte de mi tiempo en línea.", ["", "Nunca", "Rara vez", "A veces", "A menudo", "Siempre"])

            submit1 = st.form_submit_button("Enviar")
            submit2 = False
            submit3 = False
            submit4 = False

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
            Q11 = st.selectbox("#11. Glad.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q12 = st.selectbox("#12. Happy with how things are.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q13 = st.selectbox("#13. Very excited.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q14 = st.selectbox("#14. I believe many people do not like me.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q15 = st.selectbox("#15. Uncomfortable or nervous.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q16 = st.selectbox("#16. Really disliking other people.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q17 = st.selectbox("#17. Friendly.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q18 = st.selectbox("#18. Rested and full of energy.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q19 = st.selectbox("#19. Relaxed.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q20 = st.selectbox("#20. Crying a lot.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q21 = st.selectbox("#21. Tired.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q22 = st.selectbox("#22. Lonely.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q23 = st.selectbox("#23. Laughing with others.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q24 = st.selectbox("#24. Like I wanted to cry.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q25 = st.selectbox("#25. Hopeful.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q26 = st.selectbox("#26. Liked.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q27 = st.selectbox("#27. Sad.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q28 = st.selectbox("#28. Jealous (wanting what others have).", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q29 = st.selectbox("#29. In a bad mood.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q30 = st.selectbox("#30. Others are better than you.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q31 = st.selectbox("#31. Part of a group.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q32 = st.selectbox("#32. Like I like myself.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q33 = st.selectbox("#33. Like I have good choices.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q34 = st.selectbox("#34. Interested in learning new things.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q35 = st.selectbox("#35. Hurt by other people.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q36 = st.selectbox("#36. Picked on or made fun of.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q37 = st.selectbox("#37. Understood.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q38 = st.selectbox("#38. Loved.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q39 = st.selectbox("#39. Happy.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q40 = st.selectbox("#40. Left out.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q41 = st.selectbox("#41. Proud of myself.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q42 = st.selectbox("#42. Wishing I was someone else.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])
            Q43 = st.selectbox("#43. Wishing I wasn’t here anymore.", ["","Not at all", "Only a little", "Sometimes", "Often", "A lot of the time (almost always)"])

            submit2 = st.form_submit_button("Submit")
            submit1 = False
            submit3 = False
            submit4 = False
    
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
            Q11 = st.selectbox("#11. Contento(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q12 = st.selectbox("#12. Muy emocionado(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q13 = st.selectbox("#13. Súper emocionado(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q14 = st.selectbox("#14. Sentí que no le caía bien a la gente.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q15 = st.selectbox("#15. Incómodo(a) o nervioso(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q16 = st.selectbox("#16. Siento que me caen mal los demás.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q17 = st.selectbox("#17. Amigable.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q18 = st.selectbox("#18. Descansado(a) y con mucha energía.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q19 = st.selectbox("#19. Relajado(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q20 = st.selectbox("#20. Llorando mucho.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q21 = st.selectbox("#21. Cansado(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q22 = st.selectbox("#22. Solo(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q23 = st.selectbox("#23. Riendo con otros.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q24 = st.selectbox("#24. Con ganas de llorar.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q25 = st.selectbox("#25. Con esperanza.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q26 = st.selectbox("#26. Le agrado a los demás.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q27 = st.selectbox("#27. Triste.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q28 = st.selectbox("#28. Celoso(a) (queriendo lo que otros tienen).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q29 = st.selectbox("#29. De mal humor.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q30 = st.selectbox("#30. Siento que otros son mejores que yo.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q31 = st.selectbox("#31. Parte de un grupo.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q32 = st.selectbox("#32. Siento que me quiero a mí mismo(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q33 = st.selectbox("#33. Siento que tengo buenas opciones.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q34 = st.selectbox("#34. Con ganas de aprender cosas nuevas.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q35 = st.selectbox("#35. Lastimado(a) por otras personas.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q36 = st.selectbox("#36. Molestado(a) o que se burlan de mí.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q37 = st.selectbox("#37. Comprendido(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q38 = st.selectbox("#38. Amado(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q39 = st.selectbox("#39. Feliz.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q40 = st.selectbox("#40. Dejado(a) fuera.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q41 = st.selectbox("#41. Orgulloso(a) de mí mismo(a).", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q42 = st.selectbox("#42. Deseando ser otra persona.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])
            Q43 = st.selectbox("#43. Deseando ya no estar aquí.", ["", "Para nada", "Solo un poco", "A veces", "Seguido", "Mucho del tiempo (casi siempre)"])

            submit2 = st.form_submit_button("Submit")
            submit1 = False
            submit3 = False
            submit4 = False

    # Create NEIL Adult Version survey form.
    elif tool == "My Feelings and Needs (NEIL Adult Version)" and language == "English":
        with st.form("neilform"):
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
            Q14 = st.text_area("#14. How do you see the future?", placeholder="Write your thoughts here...", height=150)

            submit4 = st.form_submit_button("Submit")
            submit1 = False
            submit2 = False
            submit3 = False    

    else:
        submit1 = False
        submit2 = False
        submit3 = False
        submit4 = False
    
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
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people understand you, encourage you, and know you well?=Never,"
        elif Q2 == "Rarely":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people understand you, encourage you, and know you well?=Rarely,"
        elif Q2 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people understand you, encourage you, and know you well?=Sometimes,"
        elif Q2 == "Often":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people understand you, encourage you, and know you well?=Often,"
        elif Q2 == "Always":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people understand you, encourage you, and know you well?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q2:Do you feel that people understand you, encourage you, and know you well?=No Answer,"

        if Q3 == "Never": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q3:When you want to talk with someone or do something together, is it easy to connect?=Never,"
        elif Q3 == "Rarely":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q3:When you want to talk with someone or do something together, is it easy to connect?=Rarely,"
        elif Q3 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q3:When you want to talk with someone or do something together, is it easy to connect?=Sometimes,"
        elif Q3 == "Often":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q3:When you want to talk with someone or do something together, is it easy to connect?=Often,"
        elif Q3 == "Always":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q3:When you want to talk with someone or do something together, is it easy to connect?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q3:When you want to talk with someone or do something together, is it easy to connect?=No Answer,"

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
            Q_rawdata = Q_rawdata + "Q6:It is not easy for me to make friends?=Never,"
        elif Q6 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q6:It is not easy for me to make friends?=Rarely,"
        elif Q6 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q6:It is not easy for me to make friends?=Sometimes,"
        elif Q6 == "Often":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q6:It is not easy for me to make friends?=Often,"
        elif Q6 == "Always":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q6:It is not easy for me to make friends?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q6:It is not easy for me to make friends?=No Answer,"
    
        # Scored in reverse.
        if Q7 == "Never": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q7:How often do you wait a long time for others to contact you or reply to your messages?=Never,"
        elif Q7 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q7:How often do you wait a long time for others to contact you or reply to your messages?=Rarely,"
        elif Q7 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q7:How often do you wait a long time for others to contact you or reply to your messages?=Sometimes,"
        elif Q7 == "Often":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q7:How often do you wait a long time for others to contact you or reply to your messages?=Often,"
        elif Q7 == "Always":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q7:How often do you wait a long time for others to contact you or reply to your messages?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q7:How often do you wait a long time for others to contact you or reply to your messages?=No Answer,"

        # Scored in reverse.
        if Q8 == "Never": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or watch events by yourself?=Never,"
        elif Q8 == "Rarely":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or watch events by yourself?=Rarely,"
        elif Q8 == "Sometimes":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or watch events by yourself?=Sometimes,"
        elif Q8 == "Often":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or watch events by yourself?=Often,"
        elif Q8 == "Always":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or watch events by yourself?=Always,"
        else:
            Q_rawdata = Q_rawdata + "Q8:Is it easier for you to play games or watch events by yourself?=No Answer,"

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
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te entienden, te apoyan y te conocen bien?=Nunca,"
        elif Q2 == "Rara vez":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te entienden, te apoyan y te conocen bien?=Rara vez,"
        elif Q2 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te entienden, te apoyan y te conocen bien?=A veces,"
        elif Q2 == "A menudo":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te entienden, te apoyan y te conocen bien?=A menudo,"
        elif Q2 == "Siempre":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te entienden, te apoyan y te conocen bien?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q2:¿Sientes que las personas te entienden, te apoyan y te conocen bien?=No Contesta,"

        if Q3 == "Nunca": 
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q3:Cuando quieres hablar con alguien o hacer algo juntos, ¿te resulta fácil conectar con esa persona?=Nunca,"
        elif Q3 == "Rara vez":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q3:Cuando quieres hablar con alguien o hacer algo juntos, ¿te resulta fácil conectar con esa persona?=Rara vez,"
        elif Q3 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q3:Cuando quieres hablar con alguien o hacer algo juntos, ¿te resulta fácil conectar con esa persona?=A veces,"
        elif Q3 == "A menudo":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q3:Cuando quieres hablar con alguien o hacer algo juntos, ¿te resulta fácil conectar con esa persona?=A menudo,"
        elif Q3 == "Siempre":
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q3:Cuando quieres hablar con alguien o hacer algo juntos, ¿te resulta fácil conectar con esa persona?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q3:Cuando quieres hablar con alguien o hacer algo juntos, ¿te resulta fácil conectar con esa persona?=No Contesta,"

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
            Q_rawdata = Q_rawdata + "Q6:¿Te resulta difícil hacer amigos?=Nunca,"
        elif Q6 == "Rara vez":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q6:¿Te resulta difícil hacer amigos?=Rara vez,"
        elif Q6 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q6:¿Te resulta difícil hacer amigos?=A veces,"
        elif Q6 == "A menudo":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q6:¿Te resulta difícil hacer amigos?=A menudo,"
        elif Q6 == "Siempre":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q6:¿Te resulta difícil hacer amigos?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q6:¿Te resulta difícil hacer amigos?=No Contesta,"
    
        # Scored in reverse.
        if Q7 == "Nunca": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q7:¿Con qué frecuencia esperas mucho tiempo a que otras personas se comuniquen contigo o respondan a tus mensajes?=Nunca,"
        elif Q7 == "Rara vez":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q7:¿Con qué frecuencia esperas mucho tiempo a que otras personas se comuniquen contigo o respondan a tus mensajes?=Rara vez,"
        elif Q7 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q7:¿Con qué frecuencia esperas mucho tiempo a que otras personas se comuniquen contigo o respondan a tus mensajes?=A veces,"
        elif Q7 == "A menudo":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q7:¿Con qué frecuencia esperas mucho tiempo a que otras personas se comuniquen contigo o respondan a tus mensajes?=A menudo,"
        elif Q7 == "Siempre":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q7:¿Con qué frecuencia esperas mucho tiempo a que otras personas se comuniquen contigo o respondan a tus mensajes?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q7:¿Con qué frecuencia esperas mucho tiempo a que otras personas se comuniquen contigo o respondan a tus mensajes?=No Contesta,"

        # Scored in reverse.
        if Q8 == "Nunca": 
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q8:¿Te resulta más fácil jugar o ver eventos tú solo(a)?=Nunca,"
        elif Q8 == "Rara vez":
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q8:¿Te resulta más fácil jugar o ver eventos tú solo(a)?=Rara vez,"
        elif Q8 == "A veces":
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q8:¿Te resulta más fácil jugar o ver eventos tú solo(a)?=A veces,"
        elif Q8 == "A menudo":
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q8:¿Te resulta más fácil jugar o ver eventos tú solo(a)?=A menudo,"
        elif Q8 == "Siempre":
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q8:¿Te resulta más fácil jugar o ver eventos tú solo(a)?=Siempre,"
        else:
            Q_rawdata = Q_rawdata + "Q8:¿Te resulta más fácil jugar o ver eventos tú solo(a)?=No Contesta,"

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

    if submit2 and language == "English":
        Q_connection = 0
        Q_inclusion = 0
        Q_isolation = 0
        Q_happy_feelings = 0
        Q_bad_feelings = 0
        Q_total = 0
        Q_response = ""
        Q_rawdata = name + "," + str(age) + ","

        # Connection Score is total from questions 1, 2, 23, 26, 31, 37, 38.
        # Inclusion Score is total from questions 1, 2, 17, 23, 26, 31, 37, 38.
        # Isolation Score is total from questions 14, 22, 35, 36, 40.
        # Happy Feelings Score is total from questions 3, 4, 6, 8, 9, 11, 12, 13, 18, 19, 25, 32, 33, 34, 39, 41.
        # Scores for bad feelings (questions 5, 7, 10, 15, 16, 20, 21, 24, 27, 28, 29, 30, 36) and 
        # isoluation (questions 14, 22, 35, 36, 40) will be subtracted from other question totals.
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
            Q_rawdata = Q_rawdata + "Q11:Glad.=Not at all,"
        elif Q11 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q11:Glad.=Only a little,"
        elif Q11 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q11:Glad.=Sometimes,"
        elif Q11 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q11:Glad.=Often,"
        elif Q11 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q11:Glad.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q11:Glad.=No Answer,"

        if Q12 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q12:Happy with how things are.=Not at all,"
        elif Q12 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q12:Happy with how things are.=Only a little,"
        elif Q12 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q12:Happy with how things are.=Sometimes,"
        elif Q12 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q12:Happy with how things are.=Often,"
        elif Q12 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q12:Happy with how things are.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q12:Happy with how things are.=No Answer,"

        if Q13 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q13:Very excited.=Not at all,"
        elif Q13 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q13:Very excited.=Only a little,"
        elif Q13 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q13:Very excited.=Sometimes,"
        elif Q13 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q13:Very excited.=Often,"
        elif Q13 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q13:Very excited.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q13:Very excited.=No Answer,"

        if Q14 == "Not at all": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q14:I believe many people do not like me.=Not at all,"
        elif Q14 == "Only a little":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q14:I believe many people do not like me.=Only a little,"
        elif Q14 == "Sometimes":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q14:I believe many people do not like me.=Sometimes,"
        elif Q14 == "Often":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q14:I believe many people do not like me.=Often,"
        elif Q14 == "A lot of the time (almost always)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q14:I believe many people do not like me.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q14:I believe many people do not like me.=No Answer,"

        if Q15 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q15:Uncomfortable or nervous.=Not at all,"
        elif Q15 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q15:Uncomfortable or nervous.=Only a little,"
        elif Q15 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q15:Uncomfortable or nervous.=Sometimes,"
        elif Q15 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q15:Uncomfortable or nervous.=Often,"
        elif Q15 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q15:Uncomfortable or nervous.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q15:Uncomfortable or nervous.=No Answer,"

        if Q16 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q16:Really disliking other people.=Not at all,"
        elif Q16 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q16:Really disliking other people.=Only a little,"
        elif Q16 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q16:Really disliking other people.=Sometimes,"
        elif Q16 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q16:Really disliking other people.=Often,"
        elif Q16 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q16:Really disliking other people.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q16:Really disliking other people.=No Answer,"

        if Q17 == "Not at all": 
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q17:Friendly.=Not at all,"
        elif Q17 == "Only a little":
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q17:Friendly.=Only a little,"
        elif Q17 == "Sometimes":
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q17:Friendly.=Sometimes,"
        elif Q17 == "Often":
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q17:Friendly.=Often,"
        elif Q17 == "A lot of the time (almost always)":
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q17:Friendly.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q17:Friendly.=No Answer,"

        if Q18 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q18:Rested and full of energy.=Not at all,"
        elif Q18 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q18:Rested and full of energy.=Only a little,"
        elif Q18 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q18:Rested and full of energy.=Sometimes,"
        elif Q18 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q18:Rested and full of energy.=Often,"
        elif Q18 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q18:Rested and full of energy.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q18:Rested and full of energy.=No Answer,"

        if Q19 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q19:Relaxed.=Not at all,"
        elif Q19 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q19:Relaxed.=Only a little,"
        elif Q19 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q19:Relaxed.=Sometimes,"
        elif Q19 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q19:Relaxed.=Often,"
        elif Q19 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q19:Relaxed.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q19:Relaxed.=No Answer,"

        if Q20 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q20:Crying a lot.=Not at all,"
        elif Q20 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q20:Crying a lot.=Only a little,"
        elif Q20 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q20:Crying a lot.=Sometimes,"
        elif Q20 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q20:Crying a lot.=Often,"
        elif Q20 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q20:Crying a lot.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q20:Crying a lot.=No Answer,"

        if Q21 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q21:Tired.=Not at all,"
        elif Q21 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q21:Tired.=Only a little,"
        elif Q21 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q21:Tired.=Sometimes,"
        elif Q21 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q21:Tired.=Often,"
        elif Q21 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q21:Tired.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q21:Tired.=No Answer,"

        if Q22 == "Not at all": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q22:Lonely.=Not at all,"
        elif Q22 == "Only a little":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q22:Lonely.=Only a little,"
        elif Q22 == "Sometimes":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q22:Lonely.=Sometimes,"
        elif Q22 == "Often":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q22:Lonely.=Often,"
        elif Q22 == "A lot of the time (almost always)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q22:Lonely.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q22:Lonely.=No Answer,"

        if Q23 == "Not at all": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q23:Laughing with others.=Not at all,"
        elif Q23 == "Only a little":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q23:Laughing with others.=Only a little,"
        elif Q23 == "Sometimes":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q23:Laughing with others.=Sometimes,"
        elif Q23 == "Often":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q23:Laughing with others.=Often,"
        elif Q23 == "A lot of the time (almost always)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q23:Laughing with others.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q23:Laughing with others.=No Answer,"

        if Q24 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q24:Like I wanted to cry.=Not at all,"
        elif Q24 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q24:Like I wanted to cry.=Only a little,"
        elif Q24 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q24:Like I wanted to cry.=Sometimes,"
        elif Q24 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q24:Like I wanted to cry.=Often,"
        elif Q24 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q24:Like I wanted to cry.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q24:Like I wanted to cry.=No Answer,"

        if Q25 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q25:Hopeful.=Not at all,"
        elif Q25 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q25:Hopeful.=Only a little,"
        elif Q25 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q25:Hopeful.=Sometimes,"
        elif Q25 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q25:Hopeful.=Often,"
        elif Q25 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q25:Hopeful.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q25:Hopeful.=No Answer,"

        if Q26 == "Not at all": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q26:Liked.=Not at all,"
        elif Q26 == "Only a little":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q26:Liked.=Only a little,"
        elif Q26 == "Sometimes":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q26:Liked.=Sometimes,"
        elif Q26 == "Often":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q26:Liked.=Often,"
        elif Q26 == "A lot of the time (almost always)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q26:Liked.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q26:Liked.=No Answer,"

        if Q27 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q27:Sad.=Not at all,"
        elif Q27 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q27:Sad.=Only a little,"
        elif Q27 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q27:Sad.=Sometimes,"
        elif Q27 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q27:Sad.=Often,"
        elif Q27 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q27:Sad.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q27:Sad.=No Answer,"

        if Q28 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q28:Jealous (wanting what others have).=Not at all,"
        elif Q28 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q28:Jealous (wanting what others have).=Only a little,"
        elif Q28 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q28:Jealous (wanting what others have).=Sometimes,"
        elif Q28 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q28:Jealous (wanting what others have).=Often,"
        elif Q28 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q28:Jealous (wanting what others have).=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q28:Jealous (wanting what others have).=No Answer,"

        if Q29 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q29:In a bad mood.=Not at all,"
        elif Q29 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q29:In a bad mood.=Only a little,"
        elif Q29 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q29:In a bad mood.=Sometimes,"
        elif Q29 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q29:In a bad mood.=Often,"
        elif Q29 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q29:In a bad mood.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q29:In a bad mood.=No Answer,"

        if Q30 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q30:Others are better than you.=Not at all,"
        elif Q30 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q30:Others are better than you.=Only a little,"
        elif Q30 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q30:Others are better than you.=Sometimes,"
        elif Q30 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q30:Others are better than you.=Often,"
        elif Q30 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q30:Others are better than you.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q30:Others are better than you.=No Answer,"

        if Q31 == "Not at all": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q31:Part of a group.=Not at all,"
        elif Q31 == "Only a little":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q31:Part of a group.=Only a little,"
        elif Q31 == "Sometimes":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q31:Part of a group.=Sometimes,"
        elif Q31 == "Often":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q31:Part of a group.=Often,"
        elif Q31 == "A lot of the time (almost always)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q31:Part of a group.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q31:Part of a group.=No Answer,"

        if Q32 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q32:Like I like myself.=Not at all,"
        elif Q32 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q32:Like I like myself.=Only a little,"
        elif Q32 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q32:Like I like myself.=Sometimes,"
        elif Q32 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q32:Like I like myself.=Often,"
        elif Q32 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q32:Like I like myself.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q32:Like I like myself.=No Answer,"

        if Q33 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q33:Like I have good choices.=Not at all,"
        elif Q33 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q33:Like I have good choices.=Only a little,"
        elif Q33 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q33:Like I have good choices.=Sometimes,"
        elif Q33 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q33:Like I have good choices.=Often,"
        elif Q33 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q33:Like I have good choices.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q33:Like I have good choices.=No Answer,"

        if Q34 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q34:Interested in learning new things.=Not at all,"
        elif Q34 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q34:Interested in learning new things.=Only a little,"
        elif Q34 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q34:Interested in learning new things.=Sometimes,"
        elif Q34 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q34:Interested in learning new things.=Often,"
        elif Q34 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q34:Interested in learning new things.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q34:Interested in learning new things.=No Answer,"

        if Q35 == "Not at all": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q35:Hurt by other people.=Not at all,"
        elif Q35 == "Only a little":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q35:Hurt by other people.=Only a little,"
        elif Q35 == "Sometimes":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q35:Hurt by other people.=Sometimes,"
        elif Q35 == "Often":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q35:Hurt by other people.=Often,"
        elif Q35 == "A lot of the time (almost always)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q35:Hurt by other people.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q35:Hurt by other people.=No Answer,"

        if Q36 == "Not at all": 
            Q_isolation = Q_isolation + 0
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q36:Picked on or made fun of.=Not at all,"
        elif Q36 == "Only a little":
            Q_isolation = Q_isolation + 1
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q36:Picked on or made fun of.=Only a little,"
        elif Q36 == "Sometimes":
            Q_isolation = Q_isolation + 2
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q36:Picked on or made fun of.=Sometimes,"
        elif Q36 == "Often":
            Q_isolation = Q_isolation + 3
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q36:Picked on or made fun of.=Often,"
        elif Q36 == "A lot of the time (almost always)":
            Q_isolation = Q_isolation + 4
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q36:Picked on or made fun of.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q36:Picked on or made fun of.=No Answer,"

        if Q37 == "Not at all": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q37:Understood.=Not at all,"
        elif Q37 == "Only a little":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q37:Understood.=Only a little,"
        elif Q37 == "Sometimes":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q37:Understood.=Sometimes,"
        elif Q37 == "Often":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q37:Understood.=Often,"
        elif Q37 == "A lot of the time (almost always)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q37:Understood.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q37:Understood.=No Answer,"

        if Q38 == "Not at all": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q38:Loved.=Not at all,"
        elif Q38 == "Only a little":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q38:Loved.=Only a little,"
        elif Q38 == "Sometimes":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q38:Loved.=Sometimes,"
        elif Q38 == "Often":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q38:Loved.=Often,"
        elif Q38 == "A lot of the time (almost always)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q38:Loved.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q38:Loved.=No Answer,"

        if Q39 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q39:Happy.=Not at all,"
        elif Q39 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q39:Happy.=Only a little,"
        elif Q39 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q39:Happy.=Sometimes,"
        elif Q39 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q39:Happy.=Often,"
        elif Q39 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q39:Happy.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q39:Happy.=No Answer,"

        if Q40 == "Not at all": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q40:Left out.=Not at all,"
        elif Q40 == "Only a little":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q40:Left out.=Only a little,"
        elif Q40 == "Sometimes":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q40:Left out.=Sometimes,"
        elif Q40 == "Often":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q40:Left out.=Often,"
        elif Q40 == "A lot of the time (almost always)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q40:Left out.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q40:Left out.=No Answer,"

        if Q41 == "Not at all": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q41:Proud of myself.=Not at all,"
        elif Q41 == "Only a little":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q41:Proud of myself.=Only a little,"
        elif Q41 == "Sometimes":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q41:Proud of myself.=Sometimes,"
        elif Q41 == "Often":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q41:Proud of myself.=Often,"
        elif Q41 == "A lot of the time (almost always)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q41:Proud of myself.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q41:Proud of myself.=No Answer,"    

        if Q42 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q42:Wishing I was someone else.=Not at all,"
        elif Q42 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q42:Wishing I was someone else.=Only a little,"
        elif Q42 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q42:Wishing I was someone else.=Sometimes,"
        elif Q42 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q42:Wishing I was someone else.=Often,"
        elif Q42 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q42:Wishing I was someone else.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q42:Wishing I was someone else.=No Answer,"

        if Q43 == "Not at all": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q43:Wishing I wasn’t here anymore.=Not at all,"
        elif Q43 == "Only a little":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q43:Wishing I wasn’t here anymore.=Only a little,"
        elif Q43 == "Sometimes":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q43:Wishing I wasn’t here anymore.=Sometimes,"
        elif Q43 == "Often":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q43:Wishing I wasn’t here anymore.=Often,"
        elif Q43 == "A lot of the time (almost always)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q43:Wishing I wasn’t here anymore.=A lot of the time (almost always),"
        else:
            Q_rawdata = Q_rawdata + "Q43:Wishing I wasn’t here anymore.=No Answer,"

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

        if (Q36 == "Often" or Q36 == "A lot of the time (almost always)") and Q_connection >= 14:
            st.write(f"The Victimization Gap - Question 36 is high ({Q36}) and the Connection Score ({Q_connection}) is also high. *Recommendation*: Investigate \"toxic\" friendships or bullying within a close group.")
        if (Q21 == "Often" or Q21 == "A lot of the time (almost always)") and Q18 == "Not at all":
            st.write(f"The Exhaustion Marker - Question 21 (Tired) is high ({Q21}), but Question 18 (Rested) is \"Not at all\". *Recommendation*: Consider screening for sleep issues or high-level environmental stress.")
        if (Q_connection + Q_inclusion + Q_happy_feelings + Q_isolation + Q_bad_feelings) == 0:
            st.write(f"Skewed Responding - the test taker answered \"Not at all\" for every single item. The results may be invalid due to \"all-or-nothing\" thinking or a lack of engagement with the questions.")
        elif (Q_connection + Q_inclusion + Q_happy_feelings + Q_isolation + Q_bad_feelings) == 196:
            st.write(f"Skewed Responding - the test taker answered \"A lot of the time (almost always)\" for every single item. The results may be invalid due to \"all-or-nothing\" thinking or a lack of engagement with the questions.")
        
        st.markdown("For additional information and resources, please visit: [US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")
        Q_rawdata = Q_rawdata + "Score=" + str(Q_total)
    
    if submit2 and language == "Spanish":
        Q_connection = 0
        Q_inclusion = 0
        Q_isolation = 0
        Q_happy_feelings = 0
        Q_bad_feelings = 0
        Q_total = 0
        Q_response = ""
        Q_rawdata = name + "," + str(age) + ","

        # Connection Score is total from questions 1, 2, 23, 26, 31, 37, 38.
        # Inclusion Score is total from questions 1, 2, 17, 23, 26, 31, 37, 38.
        # Isolation Score is total from questions 14, 22, 35, 36, 40.
        # Happy Feelings Score is total from questions 3, 4, 6, 8, 9, 11, 12, 13, 18, 19, 25, 32, 33, 34, 39, 41.
        # Scores for bad feelings (questions 5, 7, 10, 15, 16, 20, 21, 24, 27, 28, 29, 30, 36) and 
        # isoluation (questions 14, 22, 35, 36, 40) will be subtracted from other question totals.
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
            Q_rawdata = Q_rawdata + "Q11:Contento(a).=Para nada,"
        elif Q11 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q11:Contento(a).=Solo un poco,"
        elif Q11 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q11:Contento(a).=A veces,"
        elif Q11 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q11:Contento(a).=Seguido,"
        elif Q11 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q11:Contento(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q11:Contento(a).=No Contesta,"

        if Q12 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q12:Muy emocionado(a).=Para nada,"
        elif Q12 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q12:Muy emocionado(a).=Solo un poco,"
        elif Q12 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q12:Muy emocionado(a).=A veces,"
        elif Q12 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q12:Muy emocionado(a).=Seguido,"
        elif Q12 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q12:Muy emocionado(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q12:Muy emocionado(a).=No Contesta,"

        if Q13 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q13:Súper emocionado(a).=Para nada,"
        elif Q13 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q13:Súper emocionado(a).=Solo un poco,"
        elif Q13 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q13:Súper emocionado(a).=A veces,"
        elif Q13 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q13:Súper emocionado(a).=Seguido,"
        elif Q13 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q13:Súper emocionado(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q13:Súper emocionado(a).=No Contesta,"

        if Q14 == "Para nada": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q14:Sentí que no le caía bien a la gente.=Para nada,"
        elif Q14 == "Solo un poco":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q14:Sentí que no le caía bien a la gente.=Solo un poco,"
        elif Q14 == "A veces":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q14:Sentí que no le caía bien a la gente.=A veces,"
        elif Q14 == "Seguido":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q14:Sentí que no le caía bien a la gente.=Seguido,"
        elif Q14 == "Mucho del tiempo (casi siempre)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q14:Sentí que no le caía bien a la gente.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q14:Sentí que no le caía bien a la gente.=No Contesta,"

        if Q15 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q15:Incómodo(a) o nervioso(a).=Para nada,"
        elif Q15 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q15:Incómodo(a) o nervioso(a).=Solo un poco,"
        elif Q15 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q15:Incómodo(a) o nervioso(a).=A veces,"
        elif Q15 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q15:Incómodo(a) o nervioso(a).=Seguido,"
        elif Q15 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q15:Incómodo(a) o nervioso(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q15:Incómodo(a) o nervioso(a).=No Contesta,"

        if Q16 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q16:Siento que me caen mal los demás.=Para nada,"
        elif Q16 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q16:Siento que me caen mal los demás.=Solo un poco,"
        elif Q16 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q16:Siento que me caen mal los demás.=A veces,"
        elif Q16 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q16:Siento que me caen mal los demás.=Seguido,"
        elif Q16 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q16:Siento que me caen mal los demás.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q16:Siento que me caen mal los demás.=No Contesta,"

        if Q17 == "Para nada": 
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q17:Amigable.=Para nada,"
        elif Q17 == "Solo un poco":
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q17:Amigable.=Solo un poco,"
        elif Q17 == "A veces":
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q17:Amigable.=A veces,"
        elif Q17 == "Seguido":
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q17:Amigable.=Seguido,"
        elif Q17 == "Mucho del tiempo (casi siempre)":
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q17:Amigable.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q17:Amigable.=No Contesta,"

        if Q18 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q18:Descansado(a) y con mucha energía.=Para nada,"
        elif Q18 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q18:Descansado(a) y con mucha energía.=Solo un poco,"
        elif Q18 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q18:Descansado(a) y con mucha energía.=A veces,"
        elif Q18 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q18:Descansado(a) y con mucha energía.=Seguido,"
        elif Q18 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q18:Descansado(a) y con mucha energía.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q18:Descansado(a) y con mucha energía.=No Contesta,"

        if Q19 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q19:Relajado(a).=Para nada,"
        elif Q19 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q19:Relajado(a).=Solo un poco,"
        elif Q19 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q19:Relajado(a).=A veces,"
        elif Q19 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q19:Relajado(a).=Seguido,"
        elif Q19 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q19:Relajado(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q19:Relajado(a).=No Contesta,"

        if Q20 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q20:Llorando mucho.=Para nada,"
        elif Q20 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q20:Llorando mucho.=Solo un poco,"
        elif Q20 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q20:Llorando mucho.=A veces,"
        elif Q20 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q20:Llorando mucho.=Seguido,"
        elif Q20 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q20:Llorando mucho.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q20:Llorando mucho.=No Contesta,"

        if Q21 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q21:Cansado(a).=Para nada,"
        elif Q21 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q21:Cansado(a).=Solo un poco,"
        elif Q21 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q21:Cansado(a).=A veces,"
        elif Q21 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q21:Cansado(a).=Seguido,"
        elif Q21 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q21:Cansado(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q21:Cansado(a).=No Contesta,"

        if Q22 == "Para nada": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q22:Solo(a).=Para nada,"
        elif Q22 == "Solo un poco":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q22:Solo(a).=Solo un poco,"
        elif Q22 == "A veces":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q22:Solo(a).=A veces,"
        elif Q22 == "Seguido":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q22:Solo(a).=Seguido,"
        elif Q22 == "Mucho del tiempo (casi siempre)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q22:Solo(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q22:Solo(a).=No Contesta,"

        if Q23 == "Para nada": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q23:Riendo con otros.=Para nada,"
        elif Q23 == "Solo un poco":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q23:Riendo con otros.=Solo un poco,"
        elif Q23 == "A veces":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q23:Riendo con otros.=A veces,"
        elif Q23 == "Seguido":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q23:Riendo con otros.=Seguido,"
        elif Q23 == "Mucho del tiempo (casi siempre)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q23:Riendo con otros.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q23:Riendo con otros.=No Contesta,"

        if Q24 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q24:Con ganas de llorar.=Para nada,"
        elif Q24 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q24:Con ganas de llorar.=Solo un poco,"
        elif Q24 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q24:Con ganas de llorar.=A veces,"
        elif Q24 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q24:Con ganas de llorar.=Seguido,"
        elif Q24 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q24:Con ganas de llorar.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q24:Con ganas de llorar.=No Contesta,"

        if Q25 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q25:Con esperanza.=Para nada,"
        elif Q25 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q25:Con esperanza.=Solo un poco,"
        elif Q25 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q25:Con esperanza.=A veces,"
        elif Q25 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q25:Con esperanza.=Seguido,"
        elif Q25 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q25:Con esperanza.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q25:Con esperanza.=No Contesta,"

        if Q26 == "Para nada": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q26:Le agrado a los demás.=Para nada,"
        elif Q26 == "Solo un poco":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q26:Le agrado a los demás.=Solo un poco,"
        elif Q26 == "A veces":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q26:Le agrado a los demás.=A veces,"
        elif Q26 == "Seguido":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q26:Le agrado a los demás.=Seguido,"
        elif Q26 == "Mucho del tiempo (casi siempre)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q26:Le agrado a los demás.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q26:Le agrado a los demás.=No Contesta,"

        if Q27 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q27:Triste.=Para nada,"
        elif Q27 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q27:Triste.=Solo un poco,"
        elif Q27 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q27:Triste.=A veces,"
        elif Q27 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q27:Triste.=Seguido,"
        elif Q27 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q27:Triste.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q27:Triste.=No Contesta,"

        if Q28 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q28:Celoso(a) (queriendo lo que otros tienen).=Para nada,"
        elif Q28 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q28:Celoso(a) (queriendo lo que otros tienen).=Solo un poco,"
        elif Q28 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q28:Celoso(a) (queriendo lo que otros tienen).=A veces,"
        elif Q28 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q28:Celoso(a) (queriendo lo que otros tienen).=Seguido,"
        elif Q28 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q28:Celoso(a) (queriendo lo que otros tienen).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q28:Celoso(a) (queriendo lo que otros tienen).=No Contesta,"

        if Q29 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q29:De mal humor.=Para nada,"
        elif Q29 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q29:De mal humor.=Solo un poco,"
        elif Q29 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q29:De mal humor.=A veces,"
        elif Q29 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q29:De mal humor.=Seguido,"
        elif Q29 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q29:De mal humor.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q29:De mal humor.=No Contesta,"

        if Q30 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q30:Siento que otros son mejores que yo.=Para nada,"
        elif Q30 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q30:Siento que otros son mejores que yo.=Solo un poco,"
        elif Q30 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q30:Siento que otros son mejores que yo.=A veces,"
        elif Q30 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q30:Siento que otros son mejores que yo.=Seguido,"
        elif Q30 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q30:Siento que otros son mejores que yo.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q30:Siento que otros son mejores que yo.=No Contesta,"

        if Q31 == "Para nada": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q31:Parte de un grupo.=Para nada,"
        elif Q31 == "Solo un poco":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q31:Parte de un grupo.=Solo un poco,"
        elif Q31 == "A veces":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q31:Parte de un grupo.=A veces,"
        elif Q31 == "Seguido":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q31:Parte de un grupo.=Seguido,"
        elif Q31 == "Mucho del tiempo (casi siempre)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q31:Parte de un grupo.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q31:Parte de un grupo.=No Contesta,"

        if Q32 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q32:Siento que me quiero a mí mismo(a).=Para nada,"
        elif Q32 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q32:Siento que me quiero a mí mismo(a).=Solo un poco,"
        elif Q32 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q32:Siento que me quiero a mí mismo(a).=A veces,"
        elif Q32 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q32:Siento que me quiero a mí mismo(a).=Seguido,"
        elif Q32 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q32:Siento que me quiero a mí mismo(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q32:Siento que me quiero a mí mismo(a).=No Contesta,"

        if Q33 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q33:Siento que tengo buenas opciones.=Para nada,"
        elif Q33 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q33:Siento que tengo buenas opciones.=Solo un poco,"
        elif Q33 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q33:Siento que tengo buenas opciones.=A veces,"
        elif Q33 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q33:Siento que tengo buenas opciones.=Seguido,"
        elif Q33 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q33:Siento que tengo buenas opciones.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q33:Siento que tengo buenas opciones.=No Contesta,"

        if Q34 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q34:Con ganas de aprender cosas nuevas.=Para nada,"
        elif Q34 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q34:Con ganas de aprender cosas nuevas.=Solo un poco,"
        elif Q34 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q34:Con ganas de aprender cosas nuevas.=A veces,"
        elif Q34 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q34:Con ganas de aprender cosas nuevas.=Seguido,"
        elif Q34 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q34:Con ganas de aprender cosas nuevas.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q34:Con ganas de aprender cosas nuevas.=No Contesta,"

        if Q35 == "Para nada": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q35:Lastimado(a) por otras personas.=Para nada,"
        elif Q35 == "Solo un poco":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q35:Lastimado(a) por otras personas.=Solo un poco,"
        elif Q35 == "A veces":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q35:Lastimado(a) por otras personas.=A veces,"
        elif Q35 == "Seguido":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q35:Lastimado(a) por otras personas.=Seguido,"
        elif Q35 == "Mucho del tiempo (casi siempre)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q35:Lastimado(a) por otras personas.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q35:Lastimado(a) por otras personas.=No Contesta,"

        if Q36 == "Para nada": 
            Q_isolation = Q_isolation + 0
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q36:Molestado(a) o que se burlan de mí.=Para nada,"
        elif Q36 == "Solo un poco":
            Q_isolation = Q_isolation + 1
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q36:Molestado(a) o que se burlan de mí.=Solo un poco,"
        elif Q36 == "A veces":
            Q_isolation = Q_isolation + 2
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q36:Molestado(a) o que se burlan de mí.=A veces,"
        elif Q36 == "Seguido":
            Q_isolation = Q_isolation + 3
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q36:Molestado(a) o que se burlan de mí.=Seguido,"
        elif Q36 == "Mucho del tiempo (casi siempre)":
            Q_isolation = Q_isolation + 4
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q36:Molestado(a) o que se burlan de mí.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q36:Molestado(a) o que se burlan de mí.=No Contesta,"

        if Q37 == "Para nada": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q37:Comprendido(a).=Para nada,"
        elif Q37 == "Solo un poco":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q37:Comprendido(a).=Solo un poco,"
        elif Q37 == "A veces":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q37:Comprendido(a).=A veces,"
        elif Q37 == "Seguido":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q37:Comprendido(a).=Seguido,"
        elif Q37 == "Mucho del tiempo (casi siempre)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q37:Comprendido(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q37:Comprendido(a).=No Contesta,"

        if Q38 == "Para nada": 
            Q_connection = Q_connection + 0
            Q_inclusion = Q_inclusion + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q38:Amado(a).=Para nada,"
        elif Q38 == "Solo un poco":
            Q_connection = Q_connection + 1
            Q_inclusion = Q_inclusion + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q38:Amado(a).=Solo un poco,"
        elif Q38 == "A veces":
            Q_connection = Q_connection + 2
            Q_inclusion = Q_inclusion + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q38:Amado(a).=A veces,"
        elif Q38 == "Seguido":
            Q_connection = Q_connection + 3
            Q_inclusion = Q_inclusion + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q38:Amado(a).=Seguido,"
        elif Q38 == "Mucho del tiempo (casi siempre)":
            Q_connection = Q_connection + 4
            Q_inclusion = Q_inclusion + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q38:Amado(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q38:Amado(a).=No Contesta,"

        if Q39 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q39:Feliz.=Para nada,"
        elif Q39 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q39:Feliz.=Solo un poco,"
        elif Q39 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q39:Feliz.=A veces,"
        elif Q39 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q39:Feliz.=Seguido,"
        elif Q39 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q39:Feliz.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q39:Feliz.=No Contesta,"

        if Q40 == "Para nada": 
            Q_isolation = Q_isolation + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q40:Dejado(a) fuera.=Para nada,"
        elif Q40 == "Solo un poco":
            Q_isolation = Q_isolation + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q40:Dejado(a) fuera.=Solo un poco,"
        elif Q40 == "A veces":
            Q_isolation = Q_isolation + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q40:Dejado(a) fuera.=A veces,"
        elif Q40 == "Seguido":
            Q_isolation = Q_isolation + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q40:Dejado(a) fuera.=Seguido,"
        elif Q40 == "Mucho del tiempo (casi siempre)":
            Q_isolation = Q_isolation + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q40:Dejado(a) fuera.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q40:Dejado(a) fuera.=No Contesta,"

        if Q41 == "Para nada": 
            Q_happy_feelings = Q_happy_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q41:Orgulloso(a) de mí mismo(a).=Para nada,"
        elif Q41 == "Solo un poco":
            Q_happy_feelings = Q_happy_feelings + 1
            Q_total = Q_total + 1
            Q_rawdata = Q_rawdata + "Q41:Orgulloso(a) de mí mismo(a).=Solo un poco,"
        elif Q41 == "A veces":
            Q_happy_feelings = Q_happy_feelings + 2
            Q_total = Q_total + 2
            Q_rawdata = Q_rawdata + "Q41:Orgulloso(a) de mí mismo(a).=A veces,"
        elif Q41 == "Seguido":
            Q_happy_feelings = Q_happy_feelings + 3
            Q_total = Q_total + 3
            Q_rawdata = Q_rawdata + "Q41:Orgulloso(a) de mí mismo(a).=Seguido,"
        elif Q41 == "Mucho del tiempo (casi siempre)":
            Q_happy_feelings = Q_happy_feelings + 4
            Q_total = Q_total + 4
            Q_rawdata = Q_rawdata + "Q41:Orgulloso(a) de mí mismo(a).=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q41:Orgulloso(a) de mí mismo(a).=No Contesta,"    

        if Q42 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q42:Deseando ser otra persona.=Para nada,"
        elif Q42 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q42:Deseando ser otra persona.=Solo un poco,"
        elif Q42 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q42:Deseando ser otra persona.=A veces,"
        elif Q42 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q42:Deseando ser otra persona.=Seguido,"
        elif Q42 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q42:Deseando ser otra persona.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q42:Deseando ser otra persona.=No Contesta,"

        if Q43 == "Para nada": 
            Q_bad_feelings = Q_bad_feelings + 0
            Q_total = Q_total + 0
            Q_rawdata = Q_rawdata + "Q43:Deseando ya no estar aquí.=Para nada,"
        elif Q43 == "Solo un poco":
            Q_bad_feelings = Q_bad_feelings + 1
            Q_total = Q_total - 1
            Q_rawdata = Q_rawdata + "Q43:Deseando ya no estar aquí.=Solo un poco,"
        elif Q43 == "A veces":
            Q_bad_feelings = Q_bad_feelings + 2
            Q_total = Q_total - 2
            Q_rawdata = Q_rawdata + "Q43:Deseando ya no estar aquí.=A veces,"
        elif Q43 == "Seguido":
            Q_bad_feelings = Q_bad_feelings + 3
            Q_total = Q_total - 3
            Q_rawdata = Q_rawdata + "Q43:Deseando ya no estar aquí.=Seguido,"
        elif Q43 == "Mucho del tiempo (casi siempre)":
            Q_bad_feelings = Q_bad_feelings + 4
            Q_total = Q_total - 4
            Q_rawdata = Q_rawdata + "Q43:Deseando ya no estar aquí.=Mucho del tiempo (casi siempre),"
        else:
            Q_rawdata = Q_rawdata + "Q43:Deseando ya no estar aquí.=No Contesta,"

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

        if (Q36 == "Seguido" or Q36 == "Mucho del tiempo (casi siempre)") and Q_connection >= 14:
            st.write(f"La brecha de victimización - La pregunta 36 es alta ({Q36}) y la Puntuación de Conexión ({Q_connection}) también es alta. *Recomendación*: Investigar las amistades \"tóxicas\" o el acoso dentro de un grupo cercano.")
        if (Q21 == "Seguido" or Q21 == "Mucho del tiempo (casi siempre)") and Q18 == "Para nada":
            st.write(f"El marcador de agotamiento - Pregunta 21 (Cansado) es alto ({Q21}), pero la Pregunta 18 (Descansado) es \"Para nada\". *Recomendación*: Considerar la evaluación de problemas de sueño o estrés ambiental elevado.")
        if (Q_connection + Q_inclusion + Q_happy_feelings + Q_isolation + Q_bad_feelings) == 0:
            st.write(f"Respuesta Sesgada - el evaluado respondió \"Para nada\" en cada ítem. Los resultados pueden ser inválidos debido a un pensamiento de \"todo o nada\" o a la falta de compromiso con las preguntas.")
        elif (Q_connection + Q_inclusion + Q_happy_feelings + Q_isolation + Q_bad_feelings) == 196:
            st.write(f"Respuesta Sesgada - el evaluado respondió \"Mucho del tiempo (casi siempre)\" en cada ítem. Los resultados pueden ser inválidos debido a un pensamiento de \"todo o nada\" o a la falta de compromiso con las preguntas.")
        
        st.markdown("Para más información y recursos, favor de visitar: [US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")
        Q_rawdata = Q_rawdata + "Score=" + str(Q_total)
        
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
        Q_rawdata = Q_rawdata + "Q14: How do you see the future?=" + Q14
    
        st.markdown("For additional information and resources, please visit: [US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")

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

    elif submit4:
        QUERY = f"""
            User context:
                - Assessment: Future Inferred Narration of Events (FINE)
                - Raw scenario-writing responses: {Q_rawdata}
                - Preferred language: {language}
            
            Task:
            Analyze the user’s scenario-writing responses to identify narrative themes that may reflect how they currently imagine their future. Focus specifically on detecting recurring or salient patterns such as:
            - perceived role (e.g., hero, victim, protector, observer)
            - anticipated interpersonal dynamics (e.g., conflict, cooperation, avoidance)
            - emotional tone toward the future (e.g., hope, fear, despair, optimism)
            - expectations of threat, safety, challenge, or opportunity
            - agency level (e.g., empowered, passive, uncertain)
            - temporal orientation (e.g., rapid change, stagnation, unexpected shifts)
            - dominant metaphors, symbols, or imagery indicating mindset or worldview
            
            Requirements:
            - Base all interpretations **only** on the user’s provided responses.
            - Do **not** infer clinical meaning, diagnose, or make psychological claims.
            - Describe patterns neutrally and observationally (e.g., “The narrative emphasizes personal responsibility and resilience,” NOT “You show high resilience.”).
            - Write clearly, concisely, and in the user’s preferred language.
            - Frame interpretations as possibilities, not facts (e.g., “This may suggest…”, “This could reflect…”).
            - Avoid speculation beyond what is explicitly present in the text.
            
            Output Structure:
            1. **Summary of Key Themes**  
               Provide a short overview of the major narrative patterns you observed.
            
            2. **Interpretive Insights**  
               Explain what these patterns *may* indicate about how the user currently imagines or anticipates their future, using careful and non‑clinical language.
            
            3. **Reflective Prompt (Optional)**  
               Offer one gentle, non‑directive question the user could consider if they choose (e.g., “What part of this future feels most important for you to understand more deeply?”).
            
            Edge Cases:
            - If the responses are too short, vague, contradictory, or incomplete to extract patterns, say so clearly and briefly.
            
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
        
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
