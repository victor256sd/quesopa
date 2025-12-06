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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpM7PbxXx1LuOf26_f5_NZ1a2XQSm7OPVj483H0JLfLPsyD3S-JPZHkVzFeoHbt15T4ffwobGriNp3zyb-h9tjwr-n6O4LtebDYIUFa5y7NWywK-m2r2w7l5uSO0Ieq6wldyB7bBsddrAo3seMd-fLx3BEBcvIpn2Gi2F8DUdUl7rCERyI67bSVre40X7oZMGHqy52jP-_RZ-t_NfDbyV9RWfv_KQaNDnzWmB1d69Oxi7eIW6nOjiJ1WIlJq4QkQXr__eXLhQl66tA6NIOpvWNpk2GOg8i0PT_losFz0bGILfwJcIkbFVbyjJWMZfquJqIhVCVZDSV4EYJ50OqzRglvMfrxMMbb6tzficfl8uzBRTTWmTUdW6rdscqLn0VKUvYbGL7RI0q3cMOncL-82eh7PkgDF81IDoEogkaYFQoRd_tReQednRh-OF-8vcrrEk0vXMVjAqWjd45ghKREfE54vxwU-0X1myv6hM8JxiyW4H8vsadhKo_t5p6YckptO9VBHQNK9wX53jiI0JLY5SMTlo7_QdVVtE0YD1Zbn7EnhoFB89U1ZpI2QkEwyjr_3zJWLY7XXm1dBt6x6J3AESWjCAXmO-UGJ3tRosAVEj0k3boQTJpvExRUpoB0XnN5Fhau6tyXx4BXgBMNW1wsxhLAi0R7BY51c1aacQRvTFcDdRiEKrmlSP4eHIfklZj2Fnl7durbMTQ17neGzT5_ytnCqlllJPtgnv-bBq_Ub9AH72LDG1V_iMC6O7Ual2XmWKnLVKwnkFabg8il3swnUfzRYkXUneyj6U4raUC4-xRWUSuxMfQSD4wnjMw8BUtMFZiSOfTg4Kj9ZH7xKWqOR4GcXVop2INOZx_7J5DpEiFlg2zgqBPGj2wDpgbXQctyyfGdp2_Wioo6M9eQs5_9pBa3bzO0QBRSSimVWDNc7SaoKj6aMWXtX0WgMvRYPSLc-MF1C1RaR6qFo_ARdsVffO70L0m8LcM-T8Cu9JjSK81f-wu5SCZtsYXSrQa3lWIrnQHvbr8JZXoMgJQFb7Voldor4rNdtxt9FYifiLJmZEaPkSjblOw8OuhzNVkVOcgkoqsP8P-Ch48KDYhiGE6oGrGwVpdqDsc2jBUskMDGpzXGBDCAD7W76U9do5lvdGypC_pnGCXM0Z7l4RTdcXSjn3RWURk0UJecnFlqrY8Nar9DF4ykL4uPgRGvr29eo3JuMGxdupVbS7raFVuWzBiNn2bkZmYzP7GMC-vFlwc39-6MA3-JsLOznk-rqhXYW30gMtY06Woj7xWSrVIn0GvfEbiBAdbe5zdixgJoae79PUQpyizs4hvBlhDn8voOzdVkT0HCAz0-KdQphRDx9KYptgNGV3lxZNg-GpaA0cu5tc4FT8x24CbT0IYi66ziMlwjU2w_p5LPMiCrmOvfqdmqkhpyf2COlCWHe8tPs8g07EQ1ryiRurJxowBd7hw5Zt34X_G2OoH5k46gkk6GGPm3xPQIyx533tv_hYQZdxUrrK5fmH11lBTJ4gEGcnoOSjorLsRDkgcLuOD9IQARc9PC27cleC2NqmDf-ixQlNnQo4tLKTTy1PWWZdwkMa0cozACaIUJLAAURe0nPhPcJjnbjnl1e5EY2jcGBEfLCdA1ZBCLGGM9IGcq3gGiknRG6_2QhdhtWeHhgBlgXNBil4UFHkNi_27rYLP80QeObndqoZ8VJgq2Za_ccDnkdnjo0erW_zxmEt9kZZwk-i5ifFiRovjL8Z-CKNqhA01t0Mta-1JjHbPIBfOSCoRUzWVrKi7DTecQPEy4QtuDdsLCcKCX6Y-TyYqNl8yMCjh1gYQInpGfi9mKVCkJXtIQCACcDAkT9pKZVSCcCwFqcvtbfjuzkRrseZdMxNa0-e-sjt1BeIlsoyGueVd-_byfntCrpAXM4X26hzOls07uEpamB1meOdAc0FEsS-iPjA7ilb35doHFBlnnXD1xYWAdDPxjTsbUJa-2XI35dlI59GuhyT0baDvF89-3V1n2OUwpSrJyFCyYsIMPNlbp5Y-AV7kOZkk7uKr2AcGS2Gx-BANfxvZejVQz3hpa_kYjyCc9prx0KyjblVvBMigopSRRbUhJC3weqLEOLSVVvc7kSVpez1FeooboGPURag_4a4mW4WSJMvLsr3fJukvvR-fHHvP2qpC4uJz9yctRb9E_t5PO0oFT6yiNhSyzqsqzjGYwODmjjPziwF7F0SvQt_cjlngjVcxs-elhb7g28uOJoFHe9AHcCW0a1CWEr6ccerqTAqcc_yyHZksOFe8ND79jSkUacSINf0n4bTf8fAheQUunnMGJyDZSbhnM4GPpCi_0s3Iz6M1oxpIL5oRzSYdG8nsG7N8yxtAJGikcqO81qJiZ1IfJNTgCy7kIgFFJCb6JL46C6HNC0pTWN6-PWemK30Kc1Y0-yQwKvdgW6dhsfUtWr7TU2E-WosU-rO9kjJ64C2FFdDy18Bn1N38LjMFCv3HkmCum5s4E1Xu4s3LirXfbDt95i4FslUpvMM9vm2pmioZfXZIe1OHBokQ3uYW5WOZkOKNyGXs7Ri_u18Pfal53IbDDZE_X-6EDiI9oaeFqLwtss_FrWvtEm5RQyEdbAVbPzYQk5HIwKROBNJHBjPIIZXrKo2vhYhhDJptZEYO4A_JA58ZZCJa8P_raS3hOJhwb3vL7QKvc6s4-LIPzHKKR-hCqsWZaPycDeNF2cqiFV-R6RLA41zCJM--FnJcmtLARi5Fg_Wctfe7rx46To6ids_sxdSPUg8A0OAjCoxfCRwG0F6cgimy0cMoQaFo_n3JCxi0QJtiZ9SilsQPzWD6YyFI-5149w_b7qyfLJo0nAV60vrpTCZsrHueC_g7l2RV5rG-XT7H62lt3N1vvVBLahVvtM450nV23ZhK9_rCu3qmEeeVXYvLEAgInVeFfX_7CT1mjKKxtKzKCpeJ9ixvCZJUIbG5p-4iimKeZnwD7ftPp-OX9a_4fKDzgCXxXu2SpvFT7y6QmOVnS5WMYFKRIguStW11YOZYnRtg5TKv_DI1k17GNgGxCDpe5drVDJZiHJxrjB-PphD1pQXX6Zy8ck9SRRPENVR5taL5J3S6G-SAWWSWqKnibD5nbeDK37EsE26wL9vCXey6NKiAsby1g9poDZa-kgACncDk48SOpYdoKMqS7ouXypB-PlSVeJ8U49DBn74DLzh9_L-3Oynlp4c4FWHPQQafdOlhWVPfO-IkenPY6omgLG1hrrdNVqlt08iezoExwrJ4hpEFpZJDWub_DO4UH46rZ2o0Xb4023K-tQ5bwZrzprTuJYFdVnz5kxfS-pNs0zGDA8BCkLlGYNCKUtW5c6PUq-ykVM6Ydt0yV1IwGDr7kfrAlxrwoN_tJEaVAXvvm_m0NkusI3K_YJ8F0j4rCZS7Z0RQUSsr2caGeAetfvC_fXeI32BvKtJhXSvbwITCwsCoMh9QM_ZsELCA1rwrLtqiesjuHPry3aoAdFErKDBJBUYt78wIo4zmF3tgzJ4E4HH9HXaFT8cCMXHkT7uskjzL4e2lsQWI-tLLCDc4NNEVufjAu-dzL3fHexHY7indJaFPzH1i_J4hAjmNZdZLpDceJpR-bH4vuXEB3CVmMRVGWEjSLtrjQWv0NllScTOhHKI0TskDNYS5gAeM_XV7IKX-zzGcuojqDn0t8x8hpvIj9bUcL5LX-HPuzpPgaeyKnQp8vViu5fajN-Z3U7nbdiTd235R0zkVR7Iz8KA3gdqm9kQ4uVW2ZL_Xn5IiX_RPZoT42-DTLcQhIK-4CxkhAbQeZuSm-tZiJhgNWqyTHq3SVOV8UpfmWtYI6Dg_6z8tbBjWwPd-qiqrHPonZG2Qm6-0AtTu_40TgH5DrqBo-M7FIXogxIDMxHWEfX5q9yiJBwjUGspG8EgQCpdNImfNuTIdhIK1ielSsrd0UC_9JjEhBApKI9fwu92eVCFLurSIIvTB6DcWxRHclER1hOJM8KEOsDPd46Y-cvgzKjoY8H171uI8rLCx32t22s4b-uOaI7uYkJlAjyDz8K4EZPucyRn4z1C4G4W0M-HjqgVNWU6PbesCyviMVUBOsj8tB1NJeJf2qcF8-RH4MAHpA3tuxRei4EZPy3h78sqVP4L91nyFXgP71_DpAni5tF5WgbR95OIxA6bm_tJeUvOszCshlOFxeJ7ubhydUz3htpgw0EdLOUUxrjMPR-aMKCCBIIZABCJ2LWWQJBBemY7XM4JNRbountDu8YRQ3UG3qw8DD9kse3z22lGI8Fv9xt_pTKKdeCAL76siJu_aMX5YORZx5p4yS6rCR_3RU-d3dFp5J22Twu4j-uHZtw7NlE6IQ2dUvLGAb9GO_aSxZl0CsAkfgPasGdX7Jez9XMrqdxbDYEtFaAe-WmlmdrnAEtL5MfNYyLR1HNVgH-ulWfc4AW6_rxdsbf2qgCGytGk_a338gRxwdqNRWqr44Jd3wcGB5Rr8OFseFt7Dcc_xbsuFRg39WsEp4VNyWnfIS6TmS6kewJrnC7LLPHxZADbPThTb-vWB3rtRQSGAYMYq2ocKrF8w2wYXu09Pl1zQD67FlZSJDqGj-oYymlW4Id_q0djQBHx0TP1u2rFY5CMsRkmgL-zS9gyp1aP0tHAQ-SbhUsH3e9FSd6l3Fm1KvEJxpLcHyXX-kZCArPHGgxiqdNe5LtgM06KAP8SkRFnsWxA6GA4ieYOcU9LIf00UcAl54yA6VvlRIoB43anxdZxlKJw_P672Ue2UeS_Pxc4EN50y9BVRaizERPHOgte2nKcIPGmSPf5xSept0ZXemedJn0GffgueZPAa6Xl3QyazTd-VWZQLH-jJ6OVwEkGdVj2a1OaO5_4H7lRy6rOW51iAm4C-XlGEvgbbS6NiVcFsD1o6xp5CcBPGO5KzKK6d5dLnSbVF_oivXrG_DWqLNmqxedU6vhwGj1PvueviT-dtwjP4Bjkj1PPeDXs9x-MCjgu-z2Z92EVw-paVsntTsInnusFN9COwts2ooqEPx-ncwGFeIZJjwZ0mvM2LkVRnXQ6lbFlgK0eTk0J7ZsUir1vSdsaV8xxhKVKjJT3lRoMTQtsaCvx7y1V_qjN_8ryVs-66E2JI860DoEXwWaXo7FP2FV7irAmv54VfPuvsNQK8JTcQyRH9j5uVYpUUeKEi4n0_e97plqTaLplWWr_buo1niXQNd_sdklmSOQp-e-aakVgRd42V30pNdFciEAR7T9XdE8RhHeITHF0iywhrxVYHDoHMOBhcPzuYfxWp-AYCFDMUXdXFQBluE1h81-CU7g-A2-10-v1cvmK9GBiuTpjhr17h9qNAuFGymILOdWZXKqFNTUnY81uol9qNELpfFo4NazOVxLM56PoFYH08JLA5PpBSkqkKYWRim7M_8Yjgbl3mEIWTijKg2YuoKlz19ZfHlASmCQnKEyomOKF3t5cYUQGQc2fHIQY5s1dRH3iEa8Lq1RO_nldaPxrKuStHG8bRBUlXisUwrHBR8BUdc4c4GnaXIYBMs9vA7kxv3Z2VMtA_OCjbGQsQsE9UkFBZSoz4rN2WwNapziUoTVV5C65q-0-7I2E0GY2A4juAn571Jk9ANHIiDxYbdaP7WlobBUfYqR27ttrZWwmlTR4ez8kfsyK-yqEU3c4pMesGgR6IY8ODB05Wq5z0buKza9Vg7REsBS28RBvH9qAxUhG2_kFWZSIH5n1fucPzPhXMZDSwpodHRyWb5fHa37kiMO-FawJvVy-mt-qiUTu5p0rzRrPkgRPbj7vdePtI6mkzYtShiTWGcY1ygXvvAEt05Sxv5zL2wJ8UaW-DO9kzB-HSQOcm7zplt7iTqFVeEUnh9HLvKp6_J5vsfOLbbx9MabtvocHCwsEXtNOm23FOZ27oMmuKwZdzbzbT1KqKiErgric7ykM2qe006OLpeme1wJS23sbBhG0xgOdAncz12KVnAwJ_Dfd9BxltnJqq5OKM08-zBs_I7sZMVLl_UcAQOsZlDKJp5ZmM0RUndvzwDZAQk0CK89X2JGm4fuBivdbE73iFj_378u5HIYrzWTrNlZV9UF5vmns_6ErAOXLxpJ5Gqk5486j4k-hia9V_Z0BEvXJg8sFrVf-65RKFZNP8Yuke9CWVnnfceRRI8xQ-nY51levD6NgJ_6Q9eiVvw_69YvsX0Yud_49hS3-jYn__IDXfZcD-FsEF4DIfZtwb7eMRZgw-fAiaZjq7_pNRK0lUhWaOAHVLl64bTcDoLpTz1bi6D_jQ4xwd-0NkqW_K7XPTADAB8kt13fCZsDaeSV0z1AWf7pRg1fHXIHv4udojL8AjhyZgTZoIk8mwBo3n3cgdWi7Bns5x0lRoSzMmIU5Wo5YbdKsS4iT4ZmdV53xPQTEjsuZduqAsn-C7R2IpQ6E7-5cUCXRZPW0hkM3LiCgK56a1beFVOBOIXGI6fsMtbvEKFZHf9Oq6NfTwQ49zlSKBqnLpBHItWVwiyd6xsA=='

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
