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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpMvkal8urQj7mtgsfES99PlOv3xabWfCAiELqXYhpANUCvAW2CoaIT4I-vtWOQfh-zik8Dn-bDNPLGgKTvQTwBHbjb5MtrGZyIYWS9xTKd2TfuDFlWpsYfJLg82uYFcv3hRySGn3xUhcQo2YTZKe2BwQD38FVgxKjrFE9tV8Vcf3m1pw3Ir4RGdaczYpp-FoOlz7LLVmAbs7ridYHLWGM_lii7Av7G-bd-3o8Q98pO2aIkce9CSUuoUZIkTZTVq3YN8eY46G_1UkXlRpEaMVe8L8MWZaygmjwYl4Sub8enecTomnVtDDvHM1pbzx3V9l_S13oxCMunkpu4tpEPXWzB35RBD1QvAJDEUCPc6lzCacu3Jax_lNH781q1E7FJ5RunXN7znvDbwK9Th3r1dLTKbIMh6aqhUUo5Ev0rZNJMcEaYA2sdXyeaHhGlCr1PtZC7M88whcFX2F9Vx_WftiOEkNqU0iEAtX5_zjiFBZ8roNtzLAfU1b2zVuqG4-pcYsUwjuxXNXXNhw772X74X2DOFVOjrO4Eh8h36CzpieN75Cx6zpFOnG3_oNtsnT8MNJlD_4sYeJpYIxzsoDkgkvrqAQzIvFhN6QyesUZEzxqd91hyw7z6sqcUV506Ts878itGIi_TTEKTR2qwJkbL63AAMJ5fmUPGy0iYGp8BXE0Z9V0j7sKkto7Ow99r1Cqp23eX4jUHom24Efu9lUtDyjkWDrElyRANBpsTzSTIjX-WqkMVPeEc5a_xSzK4HKAeFekyoUHMUYSPAl6-SvvS_8gNYpNaVo5pJ9diupNEC_iwQ-seIOUensGv2p-ekfIAc0flvqdXX0aaWpgZUYkkssbSWy2xaLkM4ymkCWJr7-DvUfgiU6hUirOxNvMO6JwgnGHX-PM58wLQqfFHLYVs_cGw-_9ogl-w0ruCb8wHy9wUVs1r6fednnPjHnEFDERUh1JS1rJ7AfNxKuFBtW6ZOn0yPb0hyrAlGXDgPDlULwVTzpdjwjwzFOoFcStuZZXzesIs2kSMX6RrItQV1MH9S5HfFTLE9hioCqI7V_Kn64aRKsbzqVdJ4_m5Un7D7XWLklhvVZJ7a3KiSpSZ1355jcnMbAMIePSBEkrFQylxKQY3HjV7oWOAWpRlHsGO_xT4Zox_QYC1pDj-BnXFtOFaaQ8zgwOwDmRUfXjgoppToztc3Nxk5fAtxVP9LJx1e9aEOsekmN-eJlcw-C5BlqpmbvY11xWJib4-A_5dzOlnYI1HUyt8iaRxlZphhWkqlTmyF4dY-TVo2xfvfNkDzz_xaSHqHSNaZyhbQFdL4emY1IwaGN2-usVhCsPTgNx-NCVfjckKjR1iFfBucvczKxJRMSRu3IuyFnwkJ3NAdG0PMa9f4qwQxrSKEzBreS9SMe_nsAFWm5ZeXTGCmXpx-Gq_074kth73724F-uHY_Dggy9oWTdKOLIPtpnBjOCP75XH9hJj36nPLmYQ8adVPjjso7AuYgWSrnjYjdnYlSmXI9ytjrP3gZuEo3Fe6eqCUDzw9XahtA7zsAFXAL7cdYjgu2Vx95Gj8vg2RjsimWKIZHXHgbsFQW2P0yTDA0iG9f-NSPvFJTdvUq-TMCnfFzQbmS5mrQnAz3vntioPlX4UQrPZW53ICB8eOY4Yj8kS6bcXYwUo0LMP1MhMn6x8tgGy2NG-73wpq7nEFLqCFIWASRVZ75-Xk8gLBsqk2kWEBTpwicwFnYCyXhq04RzpLiKUHqN_RpuaqUg8GqwkiwsK0BoplCu0_xhfIKKJlbQm-5_Q1OaySoMV5q-5DlBqnGZ_4O4GwnlTz2AywrKkVktlMAs03EYvTPwSiensIlsfcbL5Lb94jLw--HQZKranwAcVEGZk8Jg8i0-klXbyNk4qaia_ngOFsfGOaJ84vn8h0ie3P9b98hro_XAq-9l6MB88PHtt5o4ew4lKHOcD91CxPUIfMVtHze_V9pmM8wTKbwKKyLKkblPwNH4SACBqcknz515smYfmbceplzJ286c3_3Kw9u2emekkDSgbIU7cMsCW9sEJsG8KpJH0weFFHQTVWD1mLL2ruryqymzDPqGXPHD_xVQM867dzwPMHX1yqiuN0Um_Oyi3_elUkwBVqgvbfMRYkmZ5exD4hRSyY435cC-dMT3Wc4mmwD6CfUKxjJ_bSZ8rdGe2zIjWFMveR7yZaUKsfmiIXw2YxfGmYtpeZ0zAAdUManX3Z9s7MaIMdBjNV5cRQCYI3ubJpf4QnECWR0VR_QsPWYWHptiiSTCfIq0ws2avyBaKbcvZJqIzEK1oLjRG21VtYxgCKgLUalm2P47q-MRMLxPcbzEK5ZYRGdFbF5bilfTWV8Q5hIKsbq6dEWHYpIyqJfa-X_FMpPTWfY3C9E81UsNDIuZzqNNdQW0p3Brd1NxnMEZoqyJwaFhbHvsA2cT5Ms-tgCWMs0FVEqrhlr3fTVZ0TiK56Jt0uWUbnCu9rBEGJ9HUttyj3Ua4muk9LVWm4HUSrGGWgg64T8pWasDxEjhU-lE-q2dBb3EiQZ6W3D0mrf57wulh1Mizx-JmdWei7krs3RoE_pP3AQIB1YsPAn2_mB4lBYNRu2A-Z-MilAdKcriIqG5fG0-1dFIK6AlJjfcK-SVQFh60ywRYueoNZYOUSKJhcBc8xtLMvgo0rEa2nzUS1V1objCbjoxvFvOk_yOPk2LuOoTRSYIV25u5hjtikvr9j3SMkMcUTeyoRRj8XkyPEOB7oo_No4tUBZcM_7qEv-u50g2ZRJ9VztgAxASnzcEouQku7lpw0pbx2ftMx-0P2r8r0KYKdg3MfgxBYC4G4dzLsoL-u7wYQUQiaJKtHvKmfg7ZiWKYca6AVzN1m-LEDzxh0TcRgO1lC4Em6mBji5RxdoBvyI6TqNfw6EK0U6eUQ9fasrimd4ETVQTU0FkL-Y5HxAMfMHxUunmMXr8b3JiyDzqgqgl9rr7ihJMl8ayf3SIaV2SraWRN88TMDpF328D5Hin0uNGENZusIWEwOXCbWh4VVRrR7CY3EECt0o87Mp0Z_ZbhgRwflOWSFuvPDocCgyZ_8D9ThkeagBll8AyvqP74cRfLwGUlTY6Ba-qzfE8dtrDknEft6_HeCAsQPtVJxYCvwgFjCqveiCStJoXcDhZbIv-Dr-DY3byo7OPOVrwD25-l6asXys7oZLLK-y6Yd9fJ-A7RMfxX2pAA5fB1waIutGmcsQfH9EaHDMFxPvOv0vQUaevaEN9ylsEoJJUoAY3dYZa7clkcZi066A5hS1hpkMeO_4TehIz3GIp76FTkZ7S8KTad8u6OKn5FIuwRCG5FKQUYP2K5Sl4_ym5WvQC96PQVFyw8e8MHkgeesjEezH98uF36Iza4WuEbekqeLw4kUOp5AxaM4SfFTBTmzzTTNsSf7qDZrQ2tWVwGINJZ9xfTjGeXaOYy4Y7ZNHzfZNF3wEaCOJd4fvViCxgH8XLjHD9pknXGneZIdsf7q80yuHz0vaJSsV9x6wcBYQxthW5QMP1OmhCNvGC9ShQFN2J7bibbnQtUP2Ulqo_-sdQmtwHa2VXLWgkwVEdocN2d6gUEvZRssI69gDbjxBpT-lF_6uLUqfbyZxYIUaVxv-f-L9k1_LR1QYhFnVFQO95019UOaCiai0tyuaLjUeW8CeAaWMyCGT7rKTt9LoBILBz6rp7OX7w_7_7U__wjDZosA4xZ8iA1Tkz6p51WXn7PZJ0GUbnuB9IVB_DGV-NJodDyQvecb1NByyPu0uR0WRDuU_X62OtSp2G3IpGeOwjsFv3arVradZEk3drlvHUKYXdRhjHeZnmfF9pNEd6uRSS5W14BbXE_Gjp6ZCAjKT0p4FMg1sWekQVtEBNMGAYC-HMlKyiRZSj82zWQx-NdOu0Q8tDtg88xgCi7X3tmGWnEDBO70Ajls0mVGBEYhQWVhPGZJzS8PKMRk7fRouUqyOEL_sbaExLgxFm_fjXosNE5rP1YEd3NdBFX9UoW8YyJMSQEzTlMa5OHhclEYkopsWWbf27FoPbs68BxnoEOtEh0g8leUs94EXSVym-1DLtI-tPLNs6ADkIMU-UXl-b3Yujf2uejriY4nTeT_wDrqPyBWSZUH7GGGYyASqrGPtgF4p-S7f0-OCp1k9_zXsME4DB3w9cL1CiLR-PHEOSgcMHSvPsaYpCXB0sqXKl8E5oBjLYJdwpivfn5yjO8CMs46NRNhTcV36kisOJirz8gMwqrACXDe8WnTpXbyjxLGSGaRsnv7SWQaoSt6doKNwDWjkKa5wnSv4FatjX6a7rdEihg3yPrSUMmPIe80OsMEt9-Q4M_NnDJxKM4HhFZg0V8wgZpQJht3g5cS9kYluUKVQf2Qn2O_RVWfqchlkqxWw8ZFOtZsfDOElI2aUiUroRcot8gQlocOvKxLFnrAOaWhLnndJpySquFZ3fG1281mUtpz-weahfCf63GyeaBjWXUDHxUdpH0TOv1hqg_71uyeOY2zrxFMpsFbB7hmIxXPOT5pvQVKmuvhbe7eUXvx2OgWBLW5m3ltXZ5rB0MlEMVTFiKNKyjRIiPxkfWfs_IY0A25YB5W0F6drAqKHN3k-FKIq1w_8wjMOYcojBWqEomgdtxce371JjDNQi9bNqosHi3hsZAnIHR-N-aLUDuKttnqb5I4zudZ-3vwoRqfnr6yEz2FcEZlF4nnbV8lwfKNc9c9gEBLfMERT0sOPeGs_pV-Ufg2uWIVQS-EwcypUhnRNtQHp3FCE0aYYv2rMbXwsu5HXGr3K9arIU1F5_ozOyYUbKOtCaAisSFbpGvBYmMfIBNdnby9ySqcn42hpEP7YMoRdTwLIKcoQ2iiJcDh6J4xJ9kBc-o3jm2jrawPvHkIQWPFkCMQm0OhMtwaYoc-U5VXdp5nov6sa4FTYf96KiJdgxuqgChbBXEVijrrlv-oEml1SIsxBMGjPQDhOxYEGhejMr3RTyswDt67N-uAzQIxtVhL6MgadD924s9xT5qDqJ2bVkKutgvlRHVgrZL9N9ltC8PzUweT6OfcMgcQNYmUyS1Yd1KeImKGTe_sHb1muXQVsqenKks1OJRf3Y4mIAcpiqm5JhkQUKb-1KRwmAuXqzKdp6Sekm2HA6ZlPsfKuniTp55HmvMEj643AD5fr9LBJleJKqP3VcBqUgVXXpFv4hPbTdpQB3HtAmU2Q8axgCYgYIDW-8xu5vgHcR1lS_xYKGpZBNIZ6tM-zb81VChBadR1yxiPhcQkxR4baryB7VxzRtRvY86RdThCvN0Q3IzLSeXYO9aAJSFduq9vvpNuhzDj7rm8IjKeCvMPewe7Bpt08-zYdsocn1jhtso8WSSskv741UqQizpszsdb4cbjFNE45kZwJ3Y33kqMc3zrcm0HN7ba89x9QW0IjlPJ1ubAWRmEOV7K_qxlIjCJEultzNnuFR7bRRv6KwMtHL1RWc2q_Wn7B3KT1-D8yeTwbxubmc_6oqEuLAcHpsxNZ9-MvhgTD_dX9yH_0EMTHBM_3-zDivAsTIQZq3mWO72vgmOprpvqPIqATUp6DCJSx5Z5IFGkW6JLmUwOHo0KhYWi8hHxM_YGwiY0tQpwzo1RaYc3hzXLm35M9ROhU2ngyeNOfazQUJcpE5tEYyHyOWNvWBdrXSqrDu_OudH8x0TVUxmPjnfoWQ-AKeRDcMe-WrtY8sA1zCPxVfaaqdng_Dgo3Y66h15YatvR3NjQvEtBK11DjjySVsfDRW_02Wpe6CoXUnv5qKpnPoOydkGnEYeh_WfS7jZYpfAwWPTYQqnugO7A1d2SsStLWukUemj3kNs0zJOtPrhDoM2SsmCRKOewVhbM07ox2BCx4Da_EsPdOPr4V-X-s7bHMrPMOzxSYFhX_a8WbSZ2u2YzRQJtL_DzO7VwKUU_sHcuCHj9vrBkemj1pI6gcD1Qw5MFj8g--JfWloORd4HHBheA3zsQKWOWbMXs_sAEFiYnhGudGwaREzHgr9d-R_ZT4dA2ipTPPH33hcg9PYHzPQAk-pBnUlIfz3uPF0GFfw6nr_j0J8O8ugfknc_ucf8mZMwn8bTa6agOC-HdDppL0V8rHcX00YWt4Ney8EzHC2v5uoDGJiIkY3e5OCtBJH2qLIgZShQdbXW0AuH9Jkp_H_9alLRgmiqClE6QQlYrFeIwIzU7E3hN0He8oLpcAoUJyOxNbg7eKzJ0049WP0GYBKaTVQCBzDCGZ2MBviyIZ9w-mMNqqqpQEzE4Ju5CaR7UxKgYsz--V1tV-hYs-Txah1KfMtbTdkmryBZUK0gPMQdZzgr0XWppPrbD208fKPmbULIOJNX7WJ6GuDCGtTOAthJBilg'

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()

    # Set page layout and title.
    st.set_page_config(page_title="Integrity AI", page_icon=":butterfly:", layout="wide")
    st.header(":butterfly: Integrity AI")
    
    # Field for OpenAI API key.
    openai_api_key = os.environ.get("OPENAI_API_KEY", None)

    # Retrieve user-selected openai model.
    model: str = st.selectbox("Model", options=MODEL_LIST)
        
    # If there's no openai api key, stop.
    if not openai_api_key:
        st.error("Please enter your OpenAI API key!")
        st.stop()
    
    # Create new form to search aitam library vector store.    
    with st.form(key="qa_form", clear_on_submit=False, height=300):
        query = st.text_area("**Ask for guidance on the Model Code of Ethics for Educators:**", height="stretch")
        submit = st.form_submit_button("Send")
        
    # If submit button is clicked, query the aitam library.            
    if submit:
        # If form is submitted without a query, stop.
        if not query:
            st.error("Enter a question for MCEE guidance!")
            st.stop()            
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
        st.write("*The guidance and responses provided by this application are AI-generated and informed by the Model Code of Ethics for Educators and related professional standards. They are intended for informational and educational purposes only and do not constitute legal advice, official policy interpretation, or a substitute for professional judgment. Users should consult their school district policies, state regulations, or legal counsel for authoritative guidance on ethical or compliance matters. This tool is designed to assist, not replace, professional decision-making or formal review processes.*")
        st.markdown("#### Response")
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
