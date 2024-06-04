import streamlit as st
import pandas as pd
import requests

# Function to get access token
def get_access_token(tenant_id, client_id, client_secret):
    auth_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }

    response = requests.post(auth_url, data=auth_data)
    if response.status_code != 200:
        st.error("Authentication failed")
        st.text(response.text)
        return None
    
    return response.json().get('access_token')

# Function to get all lists from the SharePoint site
def get_all_lists(tenant_id, client_id, client_secret, site_id):
    access_token = get_access_token(tenant_id, client_id, client_secret)
    if not access_token:
        return None
    
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
def get_list_items(tenant_id, client_id, client_secret, site_id, list_id):
    access_token = get_access_token(tenant_id, client_id, client_secret)
    if not access_token:
        return None
    
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
tenant_id = 'bf4642cb-37d5-4b01-b220-381b7aa5dbbd'
client_id = 'a3aab3ad-8b7e-4940-b3c8-0773fba9a26b'
client_secret = 'UCQ8Q~zvL.2l2lViFjPFCftXCCpiZ_M8RAYTecOk'
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

# Get all lists from the SharePoint site
lists = get_all_lists(tenant_id, client_id, client_secret, site_id)
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
        df = get_list_items(tenant_id, client_id, client_secret, site_id, list_id)
        if df is not None and not df.empty:
            st.dataframe(df)
        else:
            st.write("No data available in this list")