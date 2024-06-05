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

# Function to get data from Microsoft List
def get_data_from_sharepoint(tenant_id, client_id, client_secret, site_id, list_id):
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
        st.error("API request failed")
        st.text(response.text)
        return None
    
    data_json = response.json()
    items = data_json.get('value', [])
    data = [item.get('fields', {}) for item in items]
    df = pd.DataFrame(data)
    return df

# Function to submit data to Microsoft List
def submit_data_to_sharepoint(tenant_id, client_id, client_secret, site_id, list_id, data):
    access_token = get_access_token(tenant_id, client_id, client_secret)
    if not access_token:
        return False
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    api_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/items"
    response = requests.post(api_url, headers=headers, json={"fields": data})
    
    if response.status_code == 201:
        return True
    else:
        st.error("Submission failed")
        st.text(response.text)
        return False

# Configuration
tenant_id = 'bf4642cb-37d5-4b01-b220-381b7aa5dbbd'
client_id = 'a3aab3ad-8b7e-4940-b3c8-0773fba9a26b'
client_secret = 'UCQ8Q~zvL.2l2lViFjPFCftXCCpiZ_M8RAYTecOk'
site_id = 'evaphotoandfilms-my.sharepoint.com,3f2bcdfa-bb50-4dc5-b133-4034dbbe6b5f,3e1b4fd4-5c24-4cfa-bb97-562216222cb9'
list_id = '7e416445-d7ec-4e15-9b78-b3da1b218987'

# Streamlit App with custom styles
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #f4f1e5;
    }
    .sidebar .sidebar-content input, .sidebar .sidebar-content select, .sidebar .sidebar-content textarea {
        color: #6b4423;
    }
    .sidebar .sidebar-content .stButton button {
        background-color: #b6ad90;
        color: white;
    }
    .reportview-container .main .block-container {
        background-color: #f4f1e5;
    }
    .reportview-container .main .block-container h1, .reportview-container .main .block-container h2, .reportview-container .main .block-container h3, .reportview-container .main .block-container h4, .reportview-container .main .block-container h5, .reportview-container .main .block-container h6, .reportview-container .main .block-container p, .reportview-container .main .block-container pre {
        color: #6b4423;
    }
    .reportview-container .main .block-container .stDataFrame, .reportview-container .main .block-container .stTable {
        color: #6b4423;
    }
    .reportview-container .main .block-container .stButton button {
        background-color: #b6ad90;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('EVA Weekly Review Scale')

st.sidebar.header('Submit Review')

# Form inputs
week_start_date = st.sidebar.date_input('Week Start Date')
member = st.sidebar.selectbox('Member', ['Jaysuriya Nagaraj', 'Sarvesh SD', 'Rahul S', 'Emil Danty', 'Madan Raj M'])
review_type = st.sidebar.selectbox('Review Type', ['Self', 'Manager'])
discipline_punctuality = st.sidebar.selectbox('DisciplinePunctuality', ['Yes', 'No'])
quality_of_work = st.sidebar.selectbox('QualityofWork', ['Yes', 'No'])
team_work = st.sidebar.selectbox('TeamWork', ['Yes', 'No'])
creativity = st.sidebar.selectbox('Creativity', ['Yes', 'No'])
rating_scale = st.sidebar.selectbox('RatingScale', ['Does not meet expectations', 'Partially meets expectations', 'Meets all expectations', 'Exceeds expectations'])
accept_manager_review = st.sidebar.selectbox('AccepttheManagerReview', ['Yes', 'No'])
comments = st.sidebar.text_area('Comments')

# Submit button
if st.sidebar.button('Submit'):
    st.sidebar.write('Submitting...')
    data = {
        "WeekStartDate": week_start_date.strftime('%Y-%m-%d'),  # Format the date correctly
        "Member": member,
        "ReviewType": review_type,
        "Discipline_x002f_Punctuality": discipline_punctuality,
        "QualityofWork": quality_of_work,
        "TeamWork": team_work,
        "Creativity": creativity,
        "RatingScale": rating_scale,
        "AccepttheManagerReview": accept_manager_review,
        "Comments": comments
    }
    
    if submit_data_to_sharepoint(tenant_id, client_id, client_secret, site_id, list_id, data):
        st.sidebar.success("Review submitted successfully!")
    else:
        st.sidebar.error("Failed to submit review.")

# Display the data
st.header('Current Ratings')

df = get_data_from_sharepoint(tenant_id, client_id, client_secret, site_id, list_id)
if df is not None:
    st.write(df)
else:
    st.write("No data available")

# Allow downloading the data as a CSV
if df is not None:
    st.download_button(
        label="Download data as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='EVA_Weekly_Review_Scale.csv',
        mime='text/csv'
    )
