# See: https://streamlit.io/
import streamlit as st
#import pandas as pd
#import numpy as np
import jwt
import uuid
import time
import requests
import json

# Creates a signed JWT
def make_jwt():
    apiKey = st.secrets["APIKEY"]
    epoch_time = int(time.time())
    st.session_state['auth_time'] = epoch_time
    expiry_time = epoch_time + 240
    key = st.secrets["KEY"]
    payload = {"iss": apiKey,
               "sub": apiKey,
               "aud": "https://int.api.service.nhs.uk/oauth2/token",
               "jti":  str(uuid.uuid4()),
               "exp": expiry_time}
    header = {"typ": "JWT",
              "kid": "1",
              "alg": "RS512"}
    encoded = jwt.encode(payload, key, algorithm="RS512", headers=header)
    return encoded

# Does token exchange to swap our locally signed JWT for an opaque APIM access token
def exchange_token(token):
    # The API endpoint to communicate with
    token_exchange_url = "https://int.api.service.nhs.uk/oauth2/token"

    the_data = {"grant_type": "client_credentials", "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer", "client_assertion": token}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    # Execute the post
    post_response = requests.post(token_exchange_url, data=the_data, headers=headers)
    post_response_json = post_response.json()
    print("Got access token")
    return post_response_json["access_token"]

# Calls PDS for this patient
def call_pds(nhs_number, access_token):
    pds_url = "https://int.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/"
    headers = { "accept": "application/fhir+json",
            "nhsd-end-user-organisation-ods": "X26",
            "Authorization": "Bearer " + access_token,
            "X-Request-ID": str(uuid.uuid4())}
    pds_response = requests.get(pds_url + nhs_number,
                     headers=headers)
    return pds_response.json()

# Calls NRL for this patient
def call_nrl(nhs_number, access_token):
    nrl_url = "https://int.api.service.nhs.uk/record-locator/consumer/FHIR/R4/DocumentReference?subject:identifier=https://fhir.nhs.uk/Id/nhs-number|" + nhs_number
    headers = { "accept": "application/fhir+json;version=1",
            "nhsd-end-user-organisation-ods": "X26",
            "Authorization": "Bearer " + access_token,
            "X-Request-ID": str(uuid.uuid4())}
    nrl_response = requests.get(nrl_url,
                     headers=headers)
    response = nrl_response.json()
    return response

# Construct a name given whatever we have
def build_name(pds_record):
    if "prefix" in pds_record["name"][0]:
        prefix = pds_record["name"][0]["prefix"][0] + " "
    else:
        prefix = ""

    if "given" in pds_record["name"][0]:
        given = pds_record["name"][0]["given"][0] + " "
    else:
        given = ""
    
    if "family" in pds_record["name"][0]:
        family = pds_record["name"][0]["family"]
    else:
        family = ""
    
    return prefix + given + family

# Here we start the App display
st.title('NRL Record Finder Application')

# We get the tokens early
if 'access_token' not in st.session_state:
    token = make_jwt()
    access_token = exchange_token(token)
    st.session_state['access_token'] = access_token

# We refresh the tokens every 8 minutes
if st.session_state["auth_time"] + 480 < int(time.time()):
    token = make_jwt()
    access_token = exchange_token(token)
    st.session_state['access_token'] = access_token

# Build the sidebar
selected_nhs_number = st.sidebar.selectbox(
    "NHS Number",
    ("Choose",
     "9900000285",
     "5900006212",
     "9691231506",
     "9730379378",
     "9730379386",
     "9730379394",
     "9730379408",
     "9730379416",
     "9730379424",
     "9730379432",
     "9730379440",
     "9730379459",
     "9730379467",
     "9730379475",
     "9730379483",
     "9730379491",
     "9730379505",
     "9730379513",
     "9730379521",
     "9730379548",
     "9730379556",
     "9730379564",
     "9730379572")
)

# If we haven't selected a patient, then we go no further
if selected_nhs_number == 'Choose':
    st.markdown("This app demonstrates getting test data from the INT environment for PDS and for NRL. All personal data is synthetic, and all links are purely to illustrate that the app works.")
    st.stop()

# But if we have we call PDS, then call NRL
pds_record = call_pds(selected_nhs_number, st.session_state['access_token'])

st.header('Patient details: ' + selected_nhs_number, divider='blue')
col1, col2 = st.columns([1,4])

# We put demographics into two columns
with col1:
    st.markdown("**Name:**")
    st.markdown("**DoB:**")
    st.markdown("**Gender:**")

with col2:
    st.markdown(build_name(pds_record))
    st.markdown(pds_record["birthDate"])
    st.markdown(pds_record["gender"])


# But we just list NRL docs as so
if selected_nhs_number == 'Choose':
    st.header('Documents listed in NRL', divider='blue')
else:
    nrl_data = call_nrl(selected_nhs_number, st.session_state['access_token'])
    st.header('Documents listed in NRL for: ' + selected_nhs_number, divider='blue')

if nrl_data["total"] == 0:
    st.write("None found")
else:
    for doc_ref in nrl_data["entry"]:
        st.write(doc_ref["resource"]["id"] + " [link](%s)" % doc_ref["resource"]["content"][0]["attachment"]["url"])
        if st.button("View Document Reference", key=doc_ref["resource"]["id"]):
            st.code(json.dumps(doc_ref, indent=2), language='json')
        st.divider()
