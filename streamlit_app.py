pip install streamlit msal
import streamlit as st
import pandas as pd
import requests
import msal
import atexit
import os
import webbrowser

# Configuration
client_id = 'a3aab3ad-8b7e-4940-b3c8-0773fba9a26b'
client_secret = 'UCQ8Q~zvL.2l2lViFjPFCftXCCpiZ_M8RAYTecOk'
tenant_id = 'bf4642cb-37d5-4b01-b220-381b7aa5dbbd'
authority = f'https://login.microsoftonline.com/{tenant_id}'
redirect_uri = 'http://localhost:8501'
scopes = ["User.Read", "Sites.Read.All"]

# Function to get access token
def get_access_token():
    cache = msal.SerializableTokenCache()
    atexit.register(lambda: open("token_cache.bin", "w").write(cache.serialize()) if cache.has_state_changed else None)
    if os.path.exists("token_cache.bin"):
        cache.deserialize(open("token_cache.bin", "r").read())
    app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret, token_cache=cache)
    result = None

    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])

    if not result:
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise ValueError("Failed to create device flow")
        st.write(flow["message"])
        webbrowser.open(flow["verification_uri"])
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        return result["access_token"]
    else:
        st.error("Could not authenticate")
        st.stop()

# Function to get all lists from the SharePoint site
def get_all_lists(access_token, site_id):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    api_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists"
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        st.error("Failed to retrieve lists")
        st.text(response.text)
        return None
    
    return response.json().get('value', [])

# Function to get items from a specific list
def get_list_items(access_token, site_id, list_id):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    api_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/items?expand=fields"
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to retrieve items for list {list_id}")
        st.text(response.text)
        return None
    
    data_json = response.json()
    items = data_json.get('value', [])
    data = [item.get('fields', {}) for item in items]
    df = pd.DataFrame(data)
    return df

# Configuration
site_id = 'evaphotoandfilms-my.sharepoint.com,3f2bcdfa-bb50-4dc5-b133-4034dbbe6b5f,3e1b4fd4-5c24-4cfa-bb97-562216222cb9'

# Streamlit App
st.set_page_config(page_title="SharePoint Lists Viewer", page_icon="📋", layout="wide")

# Custom CSS for aesthetics
st.markdown("""
<style>
    /* Main title style */
    .main-title {
        color: #3E2723;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 20px;
    }

    /* Tab style */
    .stTabs [data-baseweb="tab-list"] {
        background: #A1887F;
        padding: 5px;
        border-radius: 10px;
    }

    /* Tab content style */
    .stTabs [data-baseweb="tab"] {
        background: #D7CCC8;
        color: #3E2723;
        border-radius: 5px;
        padding: 10px;
        margin: 5px;
        font-weight: bold;
    }
    
    /* Selected tab style */
    .stTabs [data-baseweb="tab"]:hover, .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #795548;
        color: white;
    }

    /* Sidebar style */
    .sidebar .sidebar-content {
        background: #EFEBE9;
        padding: 20px;
        border-radius: 10px;
    }

    /* Button style */
    .stButton button {
        background: #3E2723;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
    }

    /* Dataframe style */
    .stDataFrame {
        background: #FAFAFA;
        border: 1px solid #D7CCC8;
        border-radius: 10px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">SharePoint Lists Viewer</h1>', unsafe_allow_html=True)

# Get access token
access_token = get_access_token()

# Get all lists from the SharePoint site
lists = get_all_lists(access_token, site_id)
if lists is None:
    st.stop()

# List names for tabs
list_names = [lst['name'] for lst in lists]

# Create tabs for each list
tabs = st.tabs(list_names)

# Display each list in its own tab
for i, lst in enumerate(lists):
    with tabs[i]:
        st.header(lst['name'])
        list_id = lst['id']
        df = get_list_items(access_token, site_id, list_id)
        if df is not None and not df.empty:
            st.dataframe(df)
        else:
            st.write("No data available in this list")