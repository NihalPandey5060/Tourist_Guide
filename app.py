import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
import json
import altair as alt
from folium.plugins import MarkerCluster

# Set page config
st.set_page_config(
    page_title="Indian Tourism Explorer",
    page_icon="🗺️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    footfall = pd.read_csv('data/tourist_footfall.csv')
    places = pd.read_csv('data/places.csv')
    services = pd.read_csv('data/services.csv')
    with open('data/scams.json', 'r') as f:
        scams = json.load(f)
    with open('data/tips.json', 'r') as f:
        tips = json.load(f)
    return footfall, places, services, scams, tips

footfall, places, services, scams, tips = load_data()

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Interactive Map", "Tourist Footfall", "Scam Reports", "Verified Services", "Local Tips"])

# Interactive Map
if page == "Interactive Map":
    st.title("Interactive Map of India")
    st.write("Explore popular tourist destinations across India")
    
    # Create map
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add places
    for _, place in places.iterrows():
        popup_html = f"""
            <b>{place['name']}</b><br>
            Type: {place['type']}<br>
            Description: {place['description']}<br>
            Entry Fee: ₹{place['entry_fee']}<br>
            Popularity: {'⭐' * int(place['popularity'])}
        """
        folium.Marker(
            [place['latitude'], place['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=place['name']
        ).add_to(marker_cluster)
    
    # Add scam warnings
    for scam in scams['scams']:
        folium.CircleMarker(
            location=scam['location'],
            radius=8,
            popup=f"⚠️ {scam['type']}<br>{scam['description']}<br>Prevention: {scam['prevention']}",
            color='red',
            fill=True
        ).add_to(m)
    
    folium_static(m, width=1200, height=600)

# Tourist Footfall
elif page == "Tourist Footfall":
    st.title("Tourist Footfall Analysis")
    
    # Year selector
    selected_year = st.selectbox("Select Year", sorted(footfall['year'].unique()))
    
    # Filter data
    year_data = footfall[footfall['year'] == selected_year]
    
    # Create bar chart
    fig = px.bar(
        year_data,
        x='state',
        y=['domestic_visitors', 'foreign_visitors'],
        title=f'Tourist Footfall by State ({selected_year})',
        barmode='group',
        labels={'value': 'Number of Visitors', 'state': 'State'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Create line chart for trend
    fig_trend = px.line(
        footfall,
        x='year',
        y=['domestic_visitors', 'foreign_visitors'],
        color='state',
        title='Tourist Footfall Trend (2012-2020)',
        labels={'value': 'Number of Visitors', 'year': 'Year'}
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# Scam Reports
elif page == "Scam Reports":
    st.title("Tourist Scam Reports")
    st.write("Stay informed about common tourist scams in different cities")
    
    # Create table
    scams_df = pd.DataFrame(scams['scams'])
    st.dataframe(
        scams_df[['city', 'type', 'description', 'severity', 'prevention']],
        use_container_width=True
    )
    
    # Severity distribution
    severity_counts = scams_df['severity'].value_counts()
    fig = px.pie(
        values=severity_counts.values,
        names=severity_counts.index,
        title='Scam Severity Distribution'
    )
    st.plotly_chart(fig, use_container_width=True)

# Verified Services
elif page == "Verified Services":
    st.title("Verified Tourist Services")
    st.write("Find trusted services across different regions")
    
    # Region filter
    selected_region = st.selectbox("Select Region", sorted(services['region'].unique()))
    region_services = services[services['region'] == selected_region]
    
    # Display services
    st.dataframe(
        region_services[['name', 'type', 'rating', 'contact']],
        use_container_width=True
    )
    
    # Rating distribution
    fig = px.histogram(
        region_services,
        x='rating',
        title='Service Rating Distribution',
        nbins=10
    )
    st.plotly_chart(fig, use_container_width=True)

# Local Tips
elif page == "Local Tips":
    st.title("Local Tips and Cultural Information")
    
    # State selector
    selected_state = st.selectbox("Select State", [state['name'] for state in tips['states']])
    state_info = next(state for state in tips['states'] if state['name'] == selected_state)
    
    # Display information in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cultural Tips")
        for tip in state_info['cultural_tips']:
            st.write(f"• {tip}")
        
        st.subheader("Local Phrases")
        for phrase in state_info['local_phrases']:
            st.write(f"• {phrase}")
    
    with col2:
        st.subheader("Do's")
        for do in state_info['dos']:
            st.write(f"✅ {do}")
        
        st.subheader("Don'ts")
        for dont in state_info['donts']:
            st.write(f"❌ {dont}")
    
    st.subheader("Famous Foods")
    for food in state_info['famous_foods']:
        st.write(f"🍽️ {food}")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ for Indian Tourism") 