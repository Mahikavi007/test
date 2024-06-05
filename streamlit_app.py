import streamlit as st
import pandas as pd

# Load the CSV file
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

# Save new review to CSV
def save_data(file_path, data):
    df = pd.read_csv(file_path)
    new_data = pd.DataFrame([data])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(file_path, index=False)

# Configuration
file_path = 'EVA_Weekly_Review_Scale.csv'

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
    .reportview-container .main .block-container h1, .reportview-container .main .block-container h2, .reportview-container .main .block-container h3, .reportview-container .main .block-container h4, .reportview-container .main .block-container h5, .reportview-container .main .block-container p, .reportview-container .main .block-container pre {
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
    
    save_data(file_path, data)
    st.sidebar.success("Review submitted successfully!")

# Display the data
st.header('Current Ratings')

df = load_data(file_path)
if df is not None:
    st.write(df)
else:
    st.write("No data available")
