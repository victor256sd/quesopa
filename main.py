# Copyright (c) 2025 victor256sd
# All rights reserved.

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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpbIl5RQD2kYztw7Cr9lzVrYBxyMobRQbeVCy6UWkxfSOjfRd1NTSgn67TFtwGX6tKVIEYb8igx3SZEI-VNHg5lnRWLgnfkzrC40JsQIiHlw0Z_mVqd0BAl6iw3s5F0_qF2sR8ORVZDMKoS_S5reX_R8rKbQPmSyndWvHktLYzgTi0HHzcA9lHR5Je6spP_O4jzhRMxDxT9OgBsCASD2zy2CaNj7Aeh56Al0n1VwvZivKJVKraCzINywuH6-VQWPiYXlh_heJkpt6Ptj9bdrjMYdapVMlvRyDOOypChgARNW1QIDYawYjNTwgejDcjqfKbZv0MqANxvH6QPbniclcwUHC853h2nq5-xmEfw9zE-HqURbbTbRP5RjDJ4RIRMTQww2i8paGw2h0hEbWVdY4Fv3GtpPiuqsz4bXtRTcC4F5hTX_AzkZDfO7ihapnOnjwycdCHQb9T2UFvTA2fONlJ87WZ0nXkWx1GV9_ogoNt5aMSSwc2g8q_aDb0drGM3hGrI9DDD2jF_73A3VmeCkeowrJ4r1QxyRkeZpi-LEvcMcnmGfCN11c8FVGxI7cVPLuhkVenImgGmZmFg4udjrfED1Dfev0gTLKdrXrwuPmc32KaXT0vDV5teYOSocqbW7xMRrwdx_v98D_Hh2qu7V7-N18i22zPA8Plgwtn6z2J--MjKnXUJNabTPBRM0PkjyUdOXiaaGHt7ief1y0m4WbcCnaGJptxbJ0hhPABZ8PcKP1YSezYJaP1z5ZKas3mh2BibbuAY2yMk-9V5PaHszdJRLS05eYq_hkmfgBxm9XHpt0CffG4A_1_LH33IOPUavIAM5S46zmQALbpiS_GdJglgkwpLWzEWnE2eSK1DqpCBeex54ML49jPhOjkjfUeFbO3MSbPrhlSYR05eya577W0j2zuxhnqr4GFzOZeiqPtF9jbFclWIOqRratHsBtZlV2KzFAqzE1F6krj7LDZsWbhcxfp1kpBMI9EPZtTB5sZzxi2kYf48E_K2lfiYM2c93YHJ8k0HQsGX2oIY2M5EpXMctkOw8HJi20RJmawt1UsuEqxrE1YcGCplWwNjUD3yCupTJambz7bpTE94avdcobPvP-oJy0fQfmdFW3lyPhDEIF92AMAILxGeo5mGqiLCVU9rIqAYPd1U4bgnAMIkmEjTi8k_PEcEX8M4J3MxI5_IWgXHQC93aDwAkX_wdU7qcmKRiQS8IdJ1JILlxf20_QhHAYhW5KEveYpCSKJmrHv-oJEYVYo5dESkmqJ3ZHSUTGr38P9nJxP20O0AdzPhw0tqx7bBrwFPVf6KMWrlJhEGZI6CnRMgfuFlvibMYpwu41u0SrUGu1qvVtk0VzVP_Y9fkCrBdPiIMS1fO9tOas0VP4046stgJZ7tmZavSF6wBKdQZfIul1X5lWggN7dWhP9Rz502d1IYTs8QGvpsCN8JbW0Nmq2R68hqXu-pGcxXih896HVBhl0_k_GgP-EG1oe0JJ9A7mXv3HemVXADLkI7IaDgBbACfqPRQye19RCCqpoVJR0UNh_5ELJlSpbD-sspOc--R7xIFIL4QMpdkfmHjzzidjXW58dKUX38PJMD187YNQ-0EiPxnxc3R1VbKy4_Z7c6Q=='

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()

    # Set page layout and title.
    st.set_page_config(page_title="Qué Sopa AI", page_icon=":hibiscus:", layout="wide")
    st.header(":hibiscus: Qué Sopa AI")
    st.markdown("###### An assessment of loneliness.")
    # st.markdown("###### Your starting point for educator ethics")
    st.markdown("*The below assessment is the UCLA Loneliness Scale (Version 3), which is used to assess an individual's subjective feelings of loneliness and social isolation. The below questions were taken from [psytests.org](https://psytests.org/ipl/uclav3en-bl.html).*")
    
    # Field for OpenAI API key.
    openai_api_key = os.environ.get("OPENAI_API_KEY", None)

    # Retrieve user-selected openai model.
    # model: str = st.selectbox("Model", options=MODEL_LIST)
    model = "gpt-4o-mini"
        
    # If there's no openai api key, stop.
    if not openai_api_key:
        st.error("Please enter your OpenAI API key!")
        st.stop()

    # Create loneliness survey form.
    with st.form("ucla3_form"):
        st.write("Please fill out the form below:")
        name = st.text_input("Name")
        age = st.slider("Age", 18, 99)
        Q1 = st.selectbox("1. How often do you feel that you are *in tune* with the people around you?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q2 = st.selectbox("2. How often do you feel that you lack companionship?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q3 = st.selectbox("3. How often do you feel that there is no one you can turn to?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q4 = st.selectbox("4. How often do you feel alone?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q5 = st.selectbox("5. How often do you feel part of a group of friends?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q6 = st.selectbox("6. How often do you feel that you have a lot in common with the people around you?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q7 = st.selectbox("7. How often do you feel that you are no longer close to anyone?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q8 = st.selectbox("8. How often do you feel that your interests and ideas are not shared by those around you?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q9 = st.selectbox("9. How often do you feel outgoing and friendly?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q10 = st.selectbox("10. How often do you feel close to people?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q11 = st.selectbox("11. How often do you feel left out?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q12 = st.selectbox("12. How often do you feel that your relationships with others are not meaningful?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q13 = st.selectbox("13. How often do you feel that no one really knows you well?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q14 = st.selectbox("14. How often do you feel isolated from others?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q15 = st.selectbox("15. How often do you feel you can find companionship when you want it?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q16 = st.selectbox("16. How often do you feel that there are people who really understand you?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q17 = st.selectbox("17. How often do you feel shy?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q18 = st.selectbox("18. How often do you feel that people are around you but not with you?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q19 = st.selectbox("19. How often do you feel that there are people you can talk to?", ["","Never", "Rarely", "Sometimes", "Often"])
        Q20 = st.selectbox("20. How often do you feel that there are people you can turn to?", ["","Never", "Rarely", "Sometimes", "Often"])
        
        submit = st.form_submit_button("Submit")

    if submit:
        Q_total = 0
        Q_response = ""

        # Questions 1, 5, 6, 9, 10, 15, 16, 19, 20 are scored in reverse.
        if Q1 == "Never": 
            Q_total = Q_total + 4
        elif Q1 == "Rarely":
            Q_total = Q_total + 3
        elif Q1 == "Sometimes":
            Q_total = Q_total + 2
        elif Q1 == "Often":
            Q_total = Q_total + 1

        if Q5 == "Never": 
            Q_total = Q_total + 4
        elif Q5 == "Rarely":
            Q_total = Q_total + 3
        elif Q5 == "Sometimes":
            Q_total = Q_total + 2
        elif Q5 == "Often":
            Q_total = Q_total + 1
        
        if Q6 == "Never": 
            Q_total = Q_total + 4
        elif Q6 == "Rarely":
            Q_total = Q_total + 3
        elif Q6 == "Sometimes":
            Q_total = Q_total + 2
        elif Q6 == "Often":
            Q_total = Q_total + 1
    
        if Q9 == "Never": 
            Q_total = Q_total + 4
        elif Q9 == "Rarely":
            Q_total = Q_total + 3
        elif Q9 == "Sometimes":
            Q_total = Q_total + 2
        elif Q9 == "Often":
            Q_total = Q_total + 1

        if Q10 == "Never": 
            Q_total = Q_total + 4
        elif Q10 == "Rarely":
            Q_total = Q_total + 3
        elif Q10 == "Sometimes":
            Q_total = Q_total + 2
        elif Q10 == "Often":
            Q_total = Q_total + 1

        if Q15 == "Never": 
            Q_total = Q_total + 4
        elif Q15 == "Rarely":
            Q_total = Q_total + 3
        elif Q15 == "Sometimes":
            Q_total = Q_total + 2
        elif Q15 == "Often":
            Q_total = Q_total + 1

        if Q16 == "Never": 
            Q_total = Q_total + 4
        elif Q16 == "Rarely":
            Q_total = Q_total + 3
        elif Q16 == "Sometimes":
            Q_total = Q_total + 2
        elif Q16 == "Often":
            Q_total = Q_total + 1
    
        if Q19 == "Never": 
            Q_total = Q_total + 4
        elif Q19 == "Rarely":
            Q_total = Q_total + 3
        elif Q19 == "Sometimes":
            Q_total = Q_total + 2
        elif Q19 == "Often":
            Q_total = Q_total + 1
    
        if Q20 == "Never": 
            Q_total = Q_total + 4
        elif Q20 == "Rarely":
            Q_total = Q_total + 3
        elif Q20 == "Sometimes":
            Q_total = Q_total + 2
        elif Q20 == "Often":
            Q_total = Q_total + 1

        # Questions 2, 3, 4, 7, 8, 11, 12, 13, 14, 17, 18 scored normally.
        if Q2 == "Never": 
            Q_total = Q_total + 1
        elif Q2 == "Rarely":
            Q_total = Q_total + 2
        elif Q2 == "Sometimes":
            Q_total = Q_total + 3
        elif Q2 == "Often":
            Q_total = Q_total + 4

        if Q3 == "Never": 
            Q_total = Q_total + 1
        elif Q3 == "Rarely":
            Q_total = Q_total + 2
        elif Q3 == "Sometimes":
            Q_total = Q_total + 3
        elif Q3 == "Often":
            Q_total = Q_total + 4

        if Q4 == "Never": 
            Q_total = Q_total + 1
        elif Q4 == "Rarely":
            Q_total = Q_total + 2
        elif Q4 == "Sometimes":
            Q_total = Q_total + 3
        elif Q4 == "Often":
            Q_total = Q_total + 4

        if Q7 == "Never": 
            Q_total = Q_total + 1
        elif Q7 == "Rarely":
            Q_total = Q_total + 2
        elif Q7 == "Sometimes":
            Q_total = Q_total + 3
        elif Q7 == "Often":
            Q_total = Q_total + 4

        if Q8 == "Never": 
            Q_total = Q_total + 1
        elif Q8 == "Rarely":
            Q_total = Q_total + 2
        elif Q8 == "Sometimes":
            Q_total = Q_total + 3
        elif Q8 == "Often":
            Q_total = Q_total + 4

        if Q11 == "Never": 
            Q_total = Q_total + 1
        elif Q11 == "Rarely":
            Q_total = Q_total + 2
        elif Q11 == "Sometimes":
            Q_total = Q_total + 3
        elif Q11 == "Often":
            Q_total = Q_total + 4
    
        if Q12 == "Never": 
            Q_total = Q_total + 1
        elif Q12 == "Rarely":
            Q_total = Q_total + 2
        elif Q12 == "Sometimes":
            Q_total = Q_total + 3
        elif Q12 == "Often":
            Q_total = Q_total + 4

        if Q13 == "Never": 
            Q_total = Q_total + 1
        elif Q13 == "Rarely":
            Q_total = Q_total + 2
        elif Q13 == "Sometimes":
            Q_total = Q_total + 3
        elif Q13 == "Often":
            Q_total = Q_total + 4

        if Q14 == "Never": 
            Q_total = Q_total + 1
        elif Q14 == "Rarely":
            Q_total = Q_total + 2
        elif Q14 == "Sometimes":
            Q_total = Q_total + 3
        elif Q14 == "Often":
            Q_total = Q_total + 4

        if Q17 == "Never": 
            Q_total = Q_total + 1
        elif Q17 == "Rarely":
            Q_total = Q_total + 2
        elif Q17 == "Sometimes":
            Q_total = Q_total + 3
        elif Q17 == "Often":
            Q_total = Q_total + 4

        if Q18 == "Never": 
            Q_total = Q_total + 1
        elif Q18 == "Rarely":
            Q_total = Q_total + 2
        elif Q18 == "Sometimes":
            Q_total = Q_total + 3
        elif Q18 == "Often":
            Q_total = Q_total + 4

        if Q_total < 20:
            st.markdown("Please answer all questions.")
        elif Q_total < 28:
            st.write(f"#### Total Score: {Q_total}")
            st.markdown("No, or low, loneliness.")
            Q_response = "No, or low, loneliness."
        elif Q_total >= 28 and Q_total <= 43:
            st.write(f"#### Total Score: {Q_total}")
            st.markdown("Moderate loneliness.")
            Q_response = "Moderate loneliness."
        elif Q_total > 43:
            st.write(f"#### Total Score: {Q_total}")
            st.markdown("High degree of loneliness.")
            Q_response = "High degree of loneliness."

        if Q_total >= 20:
            st.markdown("For additional information and resources, please visit:")
            st.markdown("[US Surgeon General Report](https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf), [The Trevor Project](https://www.thetrevorproject.org/), [211](https://www.211.org/), [988](https://988lifeline.org/get-help/), [Virtual Hope Box](https://mobile.health.mil/Apps/Native-Apps/Virtual-Hope-Box)")
    
    # Create new form to search aitam library vector store.    
    # with st.form(key="qa_form", clear_on_submit=False, height=300):
    #     query = st.text_area("**What would you like to discuss?**", height="stretch")
    #     submit = st.form_submit_button("Send")
        
    # If submit button is clicked, query the aitam library.            
    if submit and Q_total >= 20:
        # If form is submitted without a query, stop.
        query = f"Please provide insights and recommendations to me regarding loneliness. I scored a {Q_total} on the UCLA Version 3 Loneliness Scale, which indicated the following: {Q_response}"
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
        st.markdown("#### Qué Sopa AI Guidance")
        st.write("*The guidance and responses provided by this application are AI-generated and informed by the US Surgeon General's report Our Epidemic of Loneliness and Isolation and related professional resources. They are intended for informational and educational purposes only and do not constitute legal advice, official policy interpretation, or a substitute for professional judgment. Users should consult their professional policies, state regulations, or legal counsel for authoritative guidance on loneliness and isolation matters. This tool is designed to assist, not replace, professional decision-making or formal review processes.*")
        st.markdown(cleaned_response)

        st.markdown("#### Sources")
        # Extract annotations from the response, and print source files.
        try:
            annotations = response2.output[1].content[0].annotations
            retrieved_files = set([response2.filename for response2 in annotations])
            file_list_str = ", ".join(retrieved_files)
            st.markdown(f"**File(s):** {file_list_str}")
        except (AttributeError, IndexError):
            st.markdown("**File(s): n/a**")

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
