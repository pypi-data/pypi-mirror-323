import os
import streamlit as st

from cognite.client import CogniteClient, ClientConfig
from cognite.client.credentials import OAuthInteractive, OAuthClientCredentials
from streamlit_slb_gallery import streamlit_slb_gallery

def assign_auth(project_name):
        
    if project_name == "slb-test":        
        tenant_id = os.environ.get("CDF_SLBTEST_TENANT_ID") 
        client_id = os.environ.get("CDF_SLBTEST_CLIENT_ID") 
        client_secret = os.environ.get("CDF_SLBTEST_CLIENT_SECRET")
        cluster = os.environ.get("CDF_SLBTEST_CLUSTER")     
    elif project_name == "petronas-pma-dev" or project_name == "petronas-pma-playground":
        tenant_id = os.environ.get("CDF_PETRONASPMA_TENANT_ID") 
        cluster = os.environ.get("CDF_PETRONASPMA_CLUSTER") 
        client_id = os.environ.get("CDF_PETRONASPMA_CLIENT_ID") 
        client_secret = ""
    elif project_name == "hess-malaysia-dev":
        tenant_id = os.environ.get("CDF_HESSDEV_TENANT_ID") 
        client_id = os.environ.get("CDF_HESSDEV_CLIENT_ID") 
        client_secret = os.environ.get("CDF_HESSDEV_CLIENT_SECRET") 
        cluster = os.environ.get("CDF_HESSDEV_CLUSTER") 
    elif project_name == "hess-malaysia-prod":
        tenant_id = os.environ.get("CDF_HESSPROD_TENANT_ID") 
        client_id = os.environ.get("CDF_HESSPROD_CLIENT_ID") 
        client_secret = os.environ.get("CDF_HESSPROD_CLIENT_SECRET") 
        cluster = os.environ.get("CDF_HESSPROD_CLUSTER")     
    elif project_name == "mubadala-dev":
        tenant_id = os.environ.get("CDF_MUBADALADEV_TENANT_ID") 
        cluster = os.environ.get("CDF_MUBADALADEV_CLUSTER")
        client_id = os.environ.get("CDF_MUBADALADEV_CLIENT_ID") 
        client_secret = os.environ.get("CDF_MUBADALADEV_CLIENT_SECRET") 
           
    base_url = f"https://{cluster}.cognitedata.com"
    scopes = [f"{base_url}/.default"]
    
    return {
        "tenant_id": tenant_id, 
        "client_id": client_id, 
        "client_secret": client_secret, 
        "cluster": cluster,
        "base_url": base_url,
        "project_name": project_name,
        "scopes": scopes
    }

def interactive_client(project_name):
    
    auth_data: any = assign_auth(project_name)
    
    """Function to instantiate the CogniteClient, using the interactive auth flow"""
    return CogniteClient(
        ClientConfig(
            client_name=auth_data['project_name'],
            project=auth_data['project_name'],
            base_url=auth_data['base_url'],
            credentials=OAuthInteractive(
                authority_url=f"https://login.microsoftonline.com/{auth_data['tenant_id']}",
                client_id=auth_data['client_id'],
                scopes=auth_data['scopes'],
            ),
        )
    )

def client_credentials(project_name):
    
    auth_data = assign_auth(project_name)

    credentials = OAuthClientCredentials(
        token_url=f"https://login.microsoftonline.com/{auth_data['tenant_id']}/oauth2/v2.0/token", 
        client_id=auth_data['client_id'], 
        client_secret= auth_data['client_secret'],
        scopes=auth_data['scopes']
    )

    config = ClientConfig(
        client_name=auth_data['project_name'],
        project=auth_data['project_name'],
        base_url=auth_data['base_url'],
        credentials=credentials,
    )
    client = CogniteClient(config)

    return client

def connect(project_name):
    auth = assign_auth(project_name=project_name)  
    if auth["client_secret"] == "":
        return interactive_client(project_name)
    else:
        return client_credentials(project_name)

st.set_page_config(page_title="Streamlit Slb Gallery", layout='wide')
st.subheader("Streamlit Slb Gallery")

client: CogniteClient = connect("mubadala-dev")

cognite_token = client.iam.token

def show_main_content():
    
    st.session_state["selected_datetime_from"] = st.selectbox(key="start_date", label="Start Date", options=["2024-07-01 06:00:00","2024-07-02 06:00:00","2024-07-03 06:00:00","2024-07-04 06:00:00","2024-07-05 06:00:00", "2024-01-22 06:00:00"], )	
    st.session_state["selected_datetime_to"] = st.selectbox(key="end_date", label="Start Date", options=["2024-07-01 06:00:00","2024-07-02 06:00:00","2024-07-03 06:00:00","2024-07-04 06:00:00","2024-07-05 06:00:00", "2025-01-22 06:00:00"])	
    
    st.session_state.selected_deck = st.selectbox(label="Deck", options=["Main Deck", "Upper Deck"])
    
    if "selected_data" in st.session_state:
        st.write(st.session_state.selected_data)
         
def show_streamlit_slb_gallery():      
    if "selected_datetime_from" in st.session_state and "selected_datetime_to" in st.session_state:
        st.session_state.selected_data = streamlit_slb_gallery(
            data={
                "height": 600, 
                "items_per_page": 10, 
                "event_start_time": st.session_state["selected_datetime_from"], 
                "event_end_time": st.session_state["selected_datetime_to"], 
                "event_type": "PPE_VIOLATION", 
                "load_delay": 2000,
                "limit": 500
                },
            token="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IllUY2VPNUlKeXlxUjZqekRTNWlBYnBlNDJKdyIsImtpZCI6IllUY2VPNUlKeXlxUjZqekRTNWlBYnBlNDJKdyJ9.eyJhdWQiOiJodHRwczovL2F6LXNpbi1zcC0wMDEuY29nbml0ZWRhdGEuY29tIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNmUzMDJmZTktMTE4Ni00MjgxLTlmYjMtOTQ0ZDdiYjgyOGNjLyIsImlhdCI6MTczNzY5MTQ2MywibmJmIjoxNzM3NjkxNDYzLCJleHAiOjE3Mzc2OTUzNjMsImFpbyI6ImsyUmdZTmovUE5IK2diR1U2WXhIWDhXUGZOM1pDd0E9IiwiYXBwaWQiOiIzM2ZiY2NjYS0xZjEzLTQzMzktOWQ0Ni02NDE4MjJiYWRiZmUiLCJhcHBpZGFjciI6IjEiLCJncm91cHMiOlsiNDc5YTM2M2QtZGQ5Ny00ZTNjLTk5MjktMWQyOTljODk0ZmIxIiwiNGZhYzhhNWMtNjQzNC00MzQwLTgzMTQtNWRiOWQ0ZjdjNzBiIl0sImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0LzZlMzAyZmU5LTExODYtNDI4MS05ZmIzLTk0NGQ3YmI4MjhjYy8iLCJvaWQiOiI1OGYzZjk5ZS1kZWUxLTQ4YmEtODYyMS00ZThkNzMzZmU4NzUiLCJyaCI6IjEuQWNZQTZTOHdib1lSZ1VLZnM1Uk5lN2dvekVMc1hQNlk0cWhPcWZkVmZLbTFVYTdHQUFER0FBLiIsInN1YiI6IjU4ZjNmOTllLWRlZTEtNDhiYS04NjIxLTRlOGQ3MzNmZTg3NSIsInRpZCI6IjZlMzAyZmU5LTExODYtNDI4MS05ZmIzLTk0NGQ3YmI4MjhjYyIsInV0aSI6IjhDc0J6SUU4SGthZDZaZ1V5OFdhQUEiLCJ2ZXIiOiIxLjAifQ.QpzZa81lwgmLt2uDrJltqiY22pFvbeCRclmkmMQdU_BZUohBvY_NQb8o6JcECjD-mn0gRq3dLHF4-eBe3E-YtL5RqjJkjL5MzBMYiiHD_-c-k8fylzkdcrbZO74BdcO5vffnVQA8ySgilG8i29psr87dMhdmOYqs7QbEmD5b6frq0VgkMRC-Xg9G4-HPq0sB36AvZHQJbIpKITdIWmAUepwvF1qGPTzOkB0E64VWi2rsY9-PMekJD02Bi0-UIHdPS5a3Wtgti_QBKTaSOhg-iyIN6Q6LcPFBFmk4yCGAfHrPa0VZvkxtOL07bJPqAqO5bld2rminq59_ji-Hy4AGRQ",
            key="streamlit_slb_gallery"
        )

main_content, gallery = st.columns([1,1])

with main_content:
    show_main_content()
    
with gallery:
    show_streamlit_slb_gallery()



