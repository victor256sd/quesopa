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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpM7TAH5yIiG9SLFtucmIqbnxbUM5iDR6lGK99CJPjooYZAhhqkwSaVSDEZYr--eINtATM5BFGEOUqoOozcLsoKnTQLp7O6ZLbEfNYr8pda2z5Ytl7aS8nakk7VoowBMs2nOUZxViu70LFk-Fcx0mcK89Rx_bJuj-7GyV_ZknAkoPU8z7mjJjQMNKqqE33WbDSxaFWvtrewYwv9iGndwtyvAJWLsXIBDo0w78kc1XzynQp_HLKad5Yj64gQDC8PesLfYK3iNOmQzX4P9GQg9Oc3FjnL1IshZPiJEJqvWpHzZBLdu8sy4q-rZXevGZxdESARUwNJGmxGTkvF4Js5hlhDLkC0mH16I--HXL5VM5oZc8-C8TYrZTg67FdinGkeQxj0rSfxKP62Vys2fD7eMDL_1uw09W7IDB0EctwL0rbjwNSVGQkY4wMj-SREBD7vpIbeRLXNz2xU_pQRpEdgIpYl8VjB1T3xOjMfUNXOCeHLZInhoq1KOVYCQpUypV174g_RJwSG0aBr1PtqiQi1vWqXS5sOEMmLqX5I_bw8LTdMv8iUHgMKJ7WTvj2Z1_FB5lBHaB6wRtj56ZW-aW2sKw_qaGdEx0XB-7Wo65ZSPKoAM7Qc9PtXI1FkBlwCZsMFI8yvEt9B2R6YBRXK5OxOrO8xxvRXzWDOEEZCc8PPPxJGTEfetdLvmpeVbFFgSHb0NZrpSZz8aqVcTBuY8R1x5CJlrfDSYAKVmQdmnqDm7Trk7iiO9FgcIk6kec0si3P9cYEHewJ_JddRgWGb44DKzjyAxZNusSkNI636bBTd8g5mc3VxsMAFiVvPmaLn4aN9Qdzfz89A4D6_4lLgVtUE5kZMouvH0BDtEe5qqjyVq9qIGqbfP32XIE9RVwEEbSGtxHPyM0nebaUY2pR7Lfeu62TpZwQmCuaqNlevDE3cv6t9VQ69Ug2ydHnXphAU67tuSwakjRt3ZnQOv3_XTYlj7j32IE0nf272yTVe9mmSl9qxiI9ulYADqxm4bD_6ob2ClLUj6DO4FaBzEG632ysAyh6ij7PMyCQuBABIGKT6fgyPhU8-ku84A2AqR0TUSJEE0b0zjM2d-GKT0Hh6oGa5Q7Rtv-DEDqaZ9N2kHc47dgSfl9igjzCzliu6xWo1mocUZ5sGgRnX8ZMr-q2RsIVLhZYXiWp2GEl1dM6M786OXYbS6Gmfe0tbzYeEE3cEno4KgUjHB6hWByY5RxxVla_k8_j-TfWho1XtGwxw7gCfHf2-bXYU-IxhLOxqf3e-hLt-DvTeqBo8BKawvE1sDeDk4Bby75oMe-_hlFwLwdqiae2UxE9EYrodDNEOicDjzV3XIcCMhVJJFbXb19RX5ew8qnpifmzgaVmXRjY-iPGinllPjf_FjkQXvI5uDFHfHmU2LghZdkiFezouuHDKP29njpvDLWccm5hKtUJclyfrwBBOtv14PKazwLfiGfKJ42RkJsAcZplOlUM0P4zY6bJYBm4Qr-il0l48pjBryj20B6eXF49TOBTL6jkbxum9XfnymMfXBfNEhCk03HtLIlPTE3PQsGxt0X_phZ2vasCpyovlcR5FaB3pjK3dHjIloPDBxVVYV9TPMPAlTFzIcGgu4xcN_yZL5FMZK_Rwwot9BiTRXjFxo5uz5h5fMFOZkupKHh7s_ke2JR4GWnc8GojWz6ttUGK9B0uHjV_b9txXdyhik8nIEoCrwSDaHijkbTwLnlO3vmWdXLoEWDrq876k2ZxmF8AgofwYS028FU5zTsRiGbRpa4x6uTYn0eHKZNfMenFpvg_pVG9qOSjbjXt2tf_ThKMlJ3h1_YGY9RtnY-WgpdZzKdlrI_4eKgRyISm7LFB_UuL3027VzZwevf9v76gajAISuOSzdknPYtyFYn6lqhzymt_DpB-K--naEduKsdK2wrYyNnqChK7VUVIkqXXtHdHSpandVASPijG2YmSIo7u9TJwRkQE81szmcPgO91irkb68xZphKLisynSOgV4cUkjyckg0kOX8P8fMR0fBjwH0qm5U6GMFPBc1Rk7qFLlvvlNMKaVGfg0TmuQDsTUhwISJf0pJEPQeYt89jeegROwF42GUQPbgbU6GzIbKi6BRM-n504BykBYf6YcDB3X-7dulZu1k1vYUO85cJkFc7C73ZEEfXsSYK148GGfVsYXHg1_rkl4b2D04flnzu6FN_BQv2oZeasr7N2Rwg6zSks01NcVCbfg4r4BDaoA-WwQk-8MZ1eDFKncnpjkWZTvpJpwx_vYzNQIgWkydATqGftKH2jCkuGqX5XjfGOlGid0Mx8cPXUi3XzHJ85NakJWrdHW-5VAT1l8UQAO-CopnXXUIwlNQ9EYylRFo8HKOEY04XEy_9x43opC3QYrUf3bqzqEUw3WEPdviWRqkvw_t5EOjn4CAeWwrLOoQMYdE4FStXTpz7WH_xpKQXPzSlzXK-oE4M30VS6cbJAPhaBeYbS1D0a18KONbcsbDxT5arcBgkSSjdKOU0p7Oq4DRnlsWAGR1-1kENbrUOp5M3Nt6k6zRBhPQEorzbo-xcerg5hN1kp6Kfp5ivOjBrl4HlpjmLx8i_q68VOsnpUubHUlAM-_33a0lRx7iCCfvQssP66V8B8XgEp60sShhEYA3MQK5rK9QIs0ofMH4BK3ZfWCXrZGDJWtNUic2M7W6Yg_kvArcyjOflw9He76s8yYEcTvoPt3h9RxKfyQV-pKDZ26PcVkIn77pcAWwG0Lc4aBgT_SrjuQczDqfyr9fzLGFb3uCyELbRyczWSHM85-bfjEL6mTWrOmIKOpu3Gt751UHDS_AJ8Y5LzsbhNl2U8WTNobzO661XET0X3zWTspR3r9qvC8Jm3S-7mBto7vSzdGkG90pwu1ipnYwBQvB7nBPE-JiiQRLvbnyOADNrTaSi9Ny9baH41Kw_Ic3YX0TkpbxDJ-Z7FVNLDeMPTnIXStn5H_65lDzrr33okLTZgNdGXUeHExNNvrNfY-N6dGe7_X7Nr1-rff2gRFdwOo7OrWVI2JkwLPj__AeskdTVQqBUApb_LbHbQ47Tn7OqEU5mIGapJYIBhRQD1AvuSzHqiLWbFmSlD2bHm8MRJklqWI3lqavGwnCylH1L8JFr-2PsO8kXt_-MwPOyIWJfQuJKKlFeOpQmw052HAC-2SMysAzYbBuY8doYoVUsUcBrl8NEkhoOrWg0NThex5yuZzU5xMkYL0lz3aU4ET5Y77fP2Qhcdbc3igFRM1t2YAOhmAgYkavs1-Li61w2F3pQRcxaYc3XTnVRPZFajYrXhTTRs5RMZhoaB_RtPqGfL08HNOnw_L4LAOL1zC6c8jFusL7PfEnZuWG1VrckDwq7lUt6UmLkDg4vS9LdmuZSJWt--9H1k2XzUEdgBq44KMOk2JDznmvPncHJzf_40OxBKMKd6IKfUDEQmaCDExvS2POJU_wl0cGqR-d2NLNnmgACsI6qWeDLlAhmmDdZ55n9NPBRZt2-KZnN4Z6TdxD6Le5Cf8pyxedYNARlpFW49UpLk24NPaShGf92DS9HPOqjhpqAzao3LLPngwh0eSpqeIuftElVF3deiO7C7m6sGus7Qn33z-LtzuQAVAHsebq7mHNNuCKBpS0fnQ3Rytb7nAgY3PAMH6W_lyEaDN72Pil9ivnKdmSuAMgN_xAG7js5HZklzZy7LlftnGNlTQZgAIP2YsCxf5qs_0eThFFsnWgQm5BmxD8pKnUNdF9PCgM4l5KIsf8KOuCaQW-B_GpbMRfBSck_IkZ1QqUDf6aUFAcfIA4Nwq2bDSFOyDEG9HOqJPei4eHDmrci1S7q56943chwSICS_17czt4qGl76z_8iNFoJCEwcipdz4WfK6seqWiSdL4FMsQzFzmaPWlMpxgKGXed6xDgEasyKVd-YXhZeiCcouy8dO3eI5wnzB3HdvhBQJr0XjGnJgsezyJvXH3yxJteKkInU2ooiQ29oJRZRepF0Wh2Ivd2E11gONDOXfUhgoXlOfCH-KxozGZMHoYbEkaEOVxz3WIxIsrJpAzUA3lC3u82bTLUWoE2EEO2dUBsp435cQ4mSQQjNB72p0norXVOgbMZngbdkGw7-okJWAMhFtzgi8IwhH_eT-5VHCTCmwjCz3s4fSWtRsZ_JdIblZQl8iObcreu0iJTkT02WOUZK_bSiqMhxvqYmGFC18CONtUsZkAusur9ucLYOJRfO3gwd-NqKjow2SsZQhXsR6pjzIm4BuZAtB4DHqtLVVkbpf67jUEak9aSC3DKBIv44LUFkU4yXsQDCWqOB3sKi_vE20pO8IX3DKBXV1NuW39n-0zVFX8K-Mh-lUBQ_pp0U0YwkfxwZnJ-q_bIPuryVdUOFOFHs1boElNne4OzRIhjbVsWJt5-LdZ9TAzLcdJP9jynlzs5KeE0svPTIlr_3DOyuBG_kFtB6VQnquf1GjNfeHgKAf9DFhBpao_vwuUQ6Hr2-K63AR7RRC8kLP1PVO-KgIFIlmfW_H0HZhp8e8GjEkOk3Y84_psbi0uw1qhWn5pwu44REx23LK1N6K3W-bVxNyZS3548oK4W_HhD2FvRcrL_wQ-k6DtG-xxvmYt9i--gepGrofon8pLn_1crxKzVyWhpEuyTM7UChLPMXzDj2MgX6otnQ4C5nk0X5JMbckIMpKECsjzyKRt68Y0CQhoHn_KtVz-A5uRUZZsJSSI2zaqHc0tBW13zJu6qOaUWddS0lRXRNx3nZDdiY2CiJip1QXcdTqRL2uDCpkhNbgMEKbpA93919Z0peQHKGay-K8ZFvbu0cY-p8olJUqM9ZT7Ik0PS-jcC7CTM4Ak9l0hRffUva0emr7JYTg6oqKL5Frozo3SYoGmSvc7Jr4wsYBkQK2b9QKkxmkYoaQefl56qEEA3aoDmsUK3SqQ0ky6u5uxSKQkM-f6xHHkZnZ8kbSgOgT8xFcM1dCOopjkgmufEw6Db1qAliJeGof3dR08uIqjr40sZPRGIwuK-kM9MnJKpIlqA6ZnL9-QVmljPfY-w4YkVgJ5AW6BQTRZdolxzIiFDZNXsH2nb0PgPshGg6-KgGhV9f9MkikF5VE0hzSvG9D7jfrPg0ReUpSOc1Q7UFs6ocOCilNn06LbePEEsFk-txzMAlIO_Ycl0bcJ22WljfddjTrNneRaaxoJTUa6yXf0eHN0jcaNuDi7X1Zx1JXlvGWEruoZCcfCsii32aQhytRyQVsBDzmAck1-Q_uA02uvnqm_3IUwKTkNoNnZTyZV7O-T2U-2OA7zGbgtT9b8SPC5o8nJQS4E_GJmBzUua2TZdmZ3IYBDE36CNgMJW-k-YC2j78CqnMSJSfwpDYQTAn1Gq4YVuiUgVPK6Qub26oXEotfdEiIjo2LDTNT2XZDO_r_AMu8PENqOwfi0Umv87Ns7ZBYnl93L5Eskdo0Ot-OccAhjgJAbsgLb65yjesCZce9YWXnKr_ryy2FU-V0aTbKEb3gee6IF2JgOcRZgfwWhM0P8nazLeQIqFOJAnZBnNVudok11y7-z2KSkuY6fttjXaqnQPHmK4Vb82tE28aPk0WQY4N_taQdtnSIF6DRpTzn1CgcKA7JyQ7gHOhqnVYIudLrhB5PPbObhfmZt40059naEDHFRx_kW9WY8UCz03q04pB_1p9LXOuYUfVbYBPaLintUWMKzdRiHFYXRkP4R7ixrVBZhfzB5_hp1ADf0I20dNoaXEnvTq6ZEE84fAYnhkZicOOTuq78Cb6SOkdPljPm4G2gyg7pTjAI75Uln722KIGAsgZH1IK6tA9abPf90T9zE4zHR8Chr5axEdfatU4OvlqS3ECYmsvWYm34PM6h100cAf_GnefYghWoGdjAI19_AyXMfQunrOZlBieeq3e-RgDBQK6crjQpC2LSkrHSwSTkQOtQu6P0uqLUrdVShayekyztxrq6rv8pKn0wXLJD7RSAaYx1lgeJaP-oDY7CRP9Gw32E53oSrNkXp7cwAaExIAKSUZf-UaOHvF6Vj8dVY_aPL0xhZYf8c_bOryD-SACGYy2l-0F7s2fD_LRIkUMBkSUV2rWb9TvsTI9iU4EL73W2g3v2FK-Hgp6cKvnwTuIbFugXkb7rLPai15eXXB3_tko990r27ctR51rTsmSIkLrbgEs2NEWjZlIYdZ2U5k6NoilQWCGZRN3TkMmSKVJtrRTPs215PbY49ZEBRFU5EqJcBDt5AHXoRWgEs_SytPc-UF6s6J2NOyDZn6R-0uUYcZKNinVzkSReZCY0EtVuzfuc1hyLuhdXquSr-v3a4kDZoZE7p2BqQPHi9eX1BQ3BGy3BSxeO__I37ydaRLOtrVAPkglfFLIdeutRLfeuRQlci3VIKsH_iOcv0bbvtWhBpPlOz3wAk08n8GZeL_HK7IB5kpJwkZ_WX6awfPD8MhcDiAYWY23MZBh4qzm9LToWuVddxYsG54uOUeXVkS6XLGm_kPCwA75AHAxEfD747U9k-MwaI9g=='

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
