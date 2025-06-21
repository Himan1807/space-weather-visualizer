import streamlit as st   # import Streamlit library for building web apps
import requests     # import the requests library for making HTTP requests
import pandas as pd    # import pandas for data manipulation and analysis
from datetime import datetime, timedelta    # import datetime and timedelta for handling dates and times
import plotly.express as px     # import Plotly Express for data visualization

# Define event descriptions for glossary and explanations
event_descriptions = {
    "CME": "Coronal Mass Ejection (CME): A massive burst of solar wind and magnetic fields rising above the solar corona.",
    "GST": "Geomagnetic Storm (GST): Disturbances in Earth's magnetosphere caused by solar wind shocks.",  # description for GST 
    "FLR": "Solar Flare (FLR): A sudden flash of increased brightness on the Sun, usually observed near its surface.",  # description for FLR 
    "SEP": "Solar Energetic Particle (SEP): High-energy particles emitted by the Sun, often associated with solar flares and CMEs.",  # description for SEP 
    "IPS": "Interplanetary Shock (IPS): Shock waves traveling through space, often caused by CMEs or solar wind variations.",  # description for IPS 
    "RBE": "Radiation Belt Enhancement (RBE): An increase in the density of charged particles in Earth's radiation belts.",  # description for RBE 
    "MPC": "Magnetopause Crossing (MPC): When solar wind plasma crosses Earth's magnetopause, the boundary of the magnetosphere.",  # description for MPC 
    "HSS": "High Speed Stream (HSS): Streams of fast-moving solar wind emanating from coronal holes on the Sun.",  # description for HSS 
    "notifications": "Notifications: General alerts and updates related to various space weather events."    # description for notifications
}

# Define the CSS for space-themed design
space_themed_css = """
<style>

/* background and text colors */
body{
    background-color: #0e1117;
    color: #FAFAFA;
    font-family: 'Arial', sans-serif;
}

.sidebar .sidebar-content{
    background-color: #262730    /* set sidebar background color */
    color: #FAFAFA;      /* set sidebard text color  */
}

/* remove the default streamlit header */
.css-1d391kg{
    background-color: #0e1117;     /* set background color of header  */
}

.css-1v3fcvr{
    color: #FAFAFA;    /* set text color  */
}

.css-1adrfps.edgvbvh3{     /* targeting nested CSS classes */
    background-color: #262730;
}

/* style for expander headers */
.streamlit-expanderHeader{    /*  styling expander headers  */
    color: #1f77b4;     /*  set color for expander headers  */
} 

</style>
"""    # end of CSS styles

st.markdown(space_themed_css, unsafe_allow_html=True)   # apply the CSS styles to the Streamlit app

# Title and Description
st.title("🌌 Space Weather Visualizer")  # set the main title of the app
st.markdown("""
This application visualizes space weather trends using NASA's DONKI API. 
Explore events like Coronal Mass Ejections (CME), Geomagnetic Storms (GST), Solar Flares (FLR), and more.
""")  # end of markdown description

# sidebar for user inputs
st.sidebar.header("Configuration")   # add a header to the sidebar

# 1) NASA API Key input at the top
api_key = st.sidebar.text_input("Enter your NASA API Key: ", value="DEMO_KEY")   # input field for NASA API Key

# 2) Event Type Selection
event_types = {    # dictionary mapping event display names to their codes
    "CME (Coronal Mass Ejection)": "CME",  # mapping for CME 
    "GST (Geomagnetic Storm)": "GST",  # mapping for GST 
    "FLR (Solar Flare)": "FLR",  # mapping for FLR 
    "SEP (Solar Energetic Particle)": "SEP",  # mapping for SEP 
    "IPS (Interplanetary Shock)": "IPS",  # mapping for IPS 
    "RBE (Radiation Belt Enhancement)": "RBE",  # mapping for RBE 
    "MPC (Magnetopause Crossing)": "MPC",  # mapping for MPC 
    "HSS (High Speed Stream)": "HSS",  # mapping for HSS 
    "Notifications": "notifications"  # mapping for Notifications 
}

selected_event_display = st.sidebar.selectbox(   # dropdown for selecting event type
    "Select Space Weather Event Type: ",    # label for the dropdown 
    list(event_types.keys()),   # list for event display names
    format_func = lambda x: x   # formatting function for display
)

api_endpoint = event_types[selected_event_display]   # get the selected event code

# 3) Date Range Selection
st.sidebar.markdown('### Date Range')   # add a markdown header for date range
default_end_date = datetime.utcnow().date()   # set default end date to today
default_start_date = default_end_date - timedelta(days = 30)   # set default start date to 30 days ago

start_date = st.sidebar.date_input("Start Date: ", default_start_date)    # input for start date
end_date = st.sidebar.date_input("End Date: ", default_end_date)   # input for end date

# Validate Date Range
if start_date > end_date:   # check if start date is after end date
    st.sidebar.error("Error: End date must fall after start date.")    # show error message if dates are invalid
    
# 4) Fetch Data Button
fetch_button = st.sidebar.button("Fetch Data")  # button for fetching data from API

# 5) Event Information expandable section
st.sidebar.markdown("### Event Information")    # add a markdown header for event info
with st.sidebar.expander("ℹ️ What is this event?"):   # expander for event info
    st.write(event_descriptions.get(api_endpoint, "No description available"))   # display selected event description
    
# 6) Glossary section
st.sidebar.markdown("### Glossary")  # add a markdown header for glossary
with st.sidebar.expander("📖 View Glossary"):   # expander for glossary terms
    for term, description in event_descriptions.items():   # iterate over glossary terms
        st.markdown(f"**{term}**: {description}")   # display each term and its corresponding description

# 7) Help section
st.sidebar.markdown("### Help")    # add a markdown header for help section
with st.sidebar.expander("❓ How to Use This App"):   # expander for help instructions
    st.write("""
    1. **Enter API Key**: Provide your NASA API Key.
    2. **Select Event Type**: Choose the space weather event you're interested in.
    3. **Set Date Range**: Specify the start and end dates for the data visualization.
    4. **Fetch Data**: Click the "Fetch Data" button to retrieve and visualize the data.
    5. **View Details**: Expand the raw JSON data or raw data sections to inspect the data.
    6. **Explore**: Interact with the plots to learn more about specific events.
    """)      # end of help instructions
    
# Function to fetch data from NASA's DONKI API
@st.cache_data(ttl = 3600)    # cache the function to avoid redundant API calls (stores info for some time)
def fetch_space_weather(event, start, end, key):  # define function to fetch space weather data
    base_url = f"https://api.nasa.gov/DONKI/{event}" 
    params = {    # initialize parameters for the API request
        "startDate": start.strftime("%Y-%m-%d"),   # format start date
        "endDate": end.strftime("%Y-%m-%d"),   # format end date
        "api_key": key   # include the API key
    }    
    
    # additional parameters for specific events
    if event == "CME":    # check if the event is 'CME'
        params.update({   # update parameters with CME-specific options
            "mostAccurateOnly": "true",   # include only the most accurate data
            "completeEntryOnly": "true",   # include only complete entries
            "speed": 500,   # set speed parameter
            "halfAngle": 30,   # set half-angle parameter
            "catalog": "ALL"   # include all catalogs
        })
    elif event == "notifications":   # check if the event is notificaitons
        params.update({    # update parameters for notifications
            "type": "all"   # include all types of notifications
        })
    
    response = requests.get(base_url, params = params)   # make the API request
    
    if response.status_code == 200:   # check if the request was successful
        return response.json()   # return the JSON response
    else:    # if the request failed
        st.error(f"Error fetching data: {response.status_code} - {response.text}")  # display error message
        return None
    
# proceed if Fetch Data button is clicked 
if fetch_button:   
    if not api_key:   # check if the API key is provided
        st.error("Please enter your NASA API Key to proceed.")    # prompt user to enter API key
    else:   # if API Key is provided
        with st.spinner("Fetching data..."):   # show a spinner while fetching data
            data = fetch_space_weather(api_endpoint, start_date, end_date, api_key)   # fetch the data
            
        if data:   # if data was fetched successfully
            st.success("Data fetched successfully!")   # display success message
            
            # show raw JSON data for debugging
            with st.expander("Show Raw JSON Data for Debugging"):   # expander to show raw JSON data
                st.json(data)   # display the raw JSON data
            
            # process data based on event type
            if isinstance(data, list):  # check if the data is a list
                df = pd.json_normalize(data)  # normalize JSON data into a DataFrame
                
                # define date field mapping
                date_field_mapping = {    # mapping of event types to their date fields
                    "CME": "startTime",  # Date field for CME 
                    "GST": "startTime",  # Date field for GST 
                    "FLR": "beginTime",  # Date field for FLR 
                    "SEP": "eventTime",  # Date field for SEP 
                    "IPS": "eventTime",  # Date field for IPS 
                    "RBE": "eventTime",  # Date field for RBE 
                    "MPC": "eventTime",  # Date field for MPC 
                    "HSS": "eventTime",  # Date field for HSS 
                    "notifications": "messageIssueTime" 
                }
                
                # define y_label mapping 
                y_label_mapping = {   # mapping of event types to their y-axis labels
                    "CME": "Number of CMEs",  # Y-label for CME 
                    "GST": "Average Kp Index",  # Y-label for GST 
                    "FLR": "Number of Solar Flares",  # Y-label for FLR 
                    "SEP": "Number of Solar Energetic Particles",  # Y-label for SEP 
                    "IPS": "Number of Interplanetary Shocks",  # Y-label for IPS 
                    "RBE": "Number of Radiation Belt Enhancements",  # Y-label for RBE 
                    "MPC": "Number of Magnetopause Crossings",  # Y-label for MPC 
                    "HSS": "Number of High Speed Streams",  # Y-label for HSS 
                    "notifications": "Number of Notifications" 
                }
                
                # define y_label
                y_label = y_label_mapping.get(api_endpoint, "Count")  # get the y-axis label based on the event type
                
                # get the correct date field
                date_field = date_field_mapping.get(api_endpoint, None)  # get the date field for the selected event
                
                if date_field and date_field in df.columns:    # check if the date field exists in the DataFrame
                    df['date'] = pd.to_datetime(df[date_field], errors = 'coerce').dt.date   # convert the date field to datetime and extract the date
                else:   # if the specific date field is not found
                    # attempt to find a date field dynamically
                    possible_keys = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]  # search for columns containing 'date' or 'time'
                    if possible_keys:  # if any possible date fields are found
                        date_field = possible_keys[0]  # use the first possible date field
                        st.warning(f"Using '{date_field}' as the date field")   # warn the user about the chosen date field
                        df['date'] = pd.to_datetime(df[date_field], errors = 'coerce').dt.date  # convert to datetime and extract the date
                    else:  # if no date fields are found
                        st.error("No suitable date field found in the data")  # display error message
                        df['date'] = pd.NaT   # assign Not-a-Time if no date field is found
                        
                # handle different event types
                if api_endpoint == "CME":   # if the event is CME
                    # for CME, plot the no. of CMEs per day
                    df_grouped = df.groupby('date').size().reset_index(name = 'count')  # group data by date and count CMEs
                    
                    # plotting with Plotly for interactivity
                    st.markdown("### Selected Event Information")   # add a markdown header
                    st.write(event_descriptions.get(api_endpoint, "No description available."))   # display event description
                    
                    st.subheader(f"{selected_event_display} from {start_date} to {end_date}")   # add a subheader with event and date range
                    fig = px.line(df_grouped, x = 'date', y = 'count', title = f"Trend of {selected_event_display} Over Time",  # create a line plot for CME trend
                                labels = {"date": "Date", "count": label},    # set axis labels
                                markers = True, template = "plotly_dark")  # add markers and set theme
                    st.plotly_chart(fig, use_container_width = True)   # display the plotly chart
                    
                elif api_endpoint == 'GST':   # if the event is GST
                    # for GST, plot the average Kp index per day
                    if 'allKpIndex' in df.columns:    # check if 'allKpIndex' column exists
                        kp_df = df.explode('allKpIndex')   # explore the 'allKpIndex' list into separate rows
                        kp_df = pd.json_normalize(kp_df['allKpIndex'])   # normalize the exploded JSON data
                        kp_df['date'] = pd.to_datetime(kp_df['observedTime'], errors = 'coerce').dt.date  # convert 'observedTime' to date
                        df_grouped = kp_df.groupby('date').agg({'kpIndex': 'mean'}).reset_index()    # calculate avg Kp Index per day
                        
                        # plotting with Plotly for interactivity
                        st.markdown("### Selected Event Information")   # add a markdown header
                        st.write(event_descriptions.get(api_endpoint, "No description available"))    # display event description
                        
                        st.subheader(f"{selected_event_display} Kp Index from {start_date} to {end_date}")   # add a subheader with event and date range
                        fig = px.line(df_grouped, x = 'date', y = 'kpIndex', title = f"Average Kp Index of {selected_event_display} Over Time",   # create a line plot for average kp Index
                                labels = {"date": "Date", "kpIndex": y_label},    # set axis labels
                                markers = True, template = "plotly_dark")   # add markers and set theme
                        st.plotly_chart(fig, use_container_width = True)   # display the plotly chart
                    else:  # if 'allKpIndex' data is not available
                        st.error("No 'allKpIndex' data available to plot.")   # show error message
                        
                elif api_endpoint == "notifications":    # if event is 'notifications'
                    # for notifications, plot the no. of notifications per day
                    df_grouped = df.groupby('date').size().reset_index(name = 'count')  # group data by date and count notifications
                    
                    # plotting with Plotly for interactivity
                    st.markdown("### Selected Event Information")  # add a markdown header
                    st.write(event_descriptions.get(api_endpoint, "No description available."))   # display event description
                    
                    st.subheader(f"{selected_event_display} from {start_date} to {end_date}")    # add a subheader with event and date range
                    fig = px.bar(df_grouped, x = 'date', y = 'count', title = f"Number of {selected_event_display} Over Time",   # create a bar chart for notifications
                                labels = {"date": "Date", "count": y_label},    # set axis labels
                                template = "plotly_dark")   # set the plot theme
                    st.plotly_chart(fig, use_container_width = True)    # display the plotly chart
                    
                else:   # for other event types
                    # plot the count per day
                    df_grouped = df.groupby('date').size().reset_index(name = 'count')   # group data by date and time
                    
                    # plotting with Plotly for interactivity
                    st.markdown("### Selected Event Information")   # add a markdown header
                    st.write(event_descriptions.get(api_endpoint, "No description available."))    # display event description
                    
                    st.subheader(f"{selected_event_display} from {start_date} to {end_date}")   # add a subheader with event and date range
                    fig = px.bar(df_grouped, x = 'date', y = 'count', title = f"Number of {selected_event_display} Over Time",    # create a bar chart for event counts 
                                labels = {"date": "Date", "count": y_label},    # set axis labels
                                template = "plotly_dark")    # set the plot theme
                    st.plotly_chart(fig, use_container_width = True)   # display the plotly chart
                    
                # show raw data
                with st.expander("Show Raw Data"):   # expander to show the raw DataFrame
                    st.write(df)   # display the raw DataFrame
            else:   # if no data is available
                st.write("No data available for the selected parameters.")    # inform the user that no data is available