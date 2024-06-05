import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Helper function to get the nearest Monday
def get_nearest_monday(date):
    return date - timedelta(days=date.weekday())

# Initialize an empty DataFrame to store the data
if 'reviews' not in st.session_state:
    st.session_state['reviews'] = pd.DataFrame(columns=[
        "WeekStartDate", "Member", "ReviewType", "Discipline_x002f_Punctuality",
        "QualityofWork", "TeamWork", "Creativity", "RatingScale", "AccepttheManagerReview", "Comments"
    ])

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
today = datetime.today()
week_start_date = st.sidebar.date_input('Week Start Date', value=get_nearest_monday(today))
if week_start_date.weekday() != 0:
    st.sidebar.error("Please select a Monday for Week Start Date.")

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
    if week_start_date.weekday() == 0:  # Check if the date is Monday
        new_data = {
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
        
        st.session_state['reviews'] = st.session_state['reviews'].append(new_data, ignore_index=True)
        st.sidebar.success("Review submitted successfully!")
    else:
        st.sidebar.error("Week Start Date must be a Monday.")

# Display the data
st.header('Current Ratings')

df = st.session_state['reviews']

# Filter options
st.sidebar.header('Filter Reviews')
filter_week_start_date = st.sidebar.selectbox('Week Start Date', ['All'] + df['WeekStartDate'].unique().tolist())
filter_month = st.sidebar.selectbox('Month', ['All'] + sorted(df['WeekStartDate'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%B')).unique().tolist()))
filter_rating_scale = st.sidebar.selectbox('Rating Scale', ['All'] + df['RatingScale'].unique().tolist())

# Apply filters
if filter_week_start_date != 'All':
    df = df[df['WeekStartDate'] == filter_week_start_date]
if filter_month != 'All':
    df = df[df['WeekStartDate'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%B')) == filter_month]
if filter_rating_scale != 'All':
    df = df[df['RatingScale'] == filter_rating_scale]

if not df.empty:
    st.write(df)
else:
    st.write("No data available")
