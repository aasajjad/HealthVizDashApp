# Importing libraries
import pandas as pd
import requests
from io import StringIO
import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
from datetime import datetime

# Direct download URL for data
url = "https://drive.google.com/uc?id=1cjpxMPK8ldsbGaRLkH9q6ZWD0e7LkZVE"

# Use requests to get the data from the URL
response = requests.get(url)

# Check if the request was successful, or print error message
if response.status_code == 200:
    # Use StringIO to convert the text content into a file-like object
    csv_raw = StringIO(response.text)
    
    # Read the CSV file into a DataFrame
    MED = pd.read_csv(csv_raw)

    # Examine DataFrame 
    # print(MED.head())
else:
    print("Failed to retrieve the data. HTTP Status Code:", response.status_code)

# Convert 'Date of Admission' to datetime
MED['Date of Admission'] = pd.to_datetime(MED['Date of Admission'])
MED['Year of Admission'] = MED['Date of Admission'].dt.year

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Healthcare Data Visualization"),
    
    html.Label("Select Admission Type:"),
    dcc.Dropdown(
        id='admission-type-dropdown',
        options=[{'label': i, 'value': i} for i in MED['Admission Type'].unique()],
        value=MED['Admission Type'].unique()[0]
    ),
    
    html.Br(),
    
    html.Label("Select Year:"),
    dcc.Slider(
        id='year-slider',
        min=MED['Year of Admission'].min(),
        max=MED['Year of Admission'].max(),
        value=MED['Year of Admission'].min(),
        marks={str(year): str(year) for year in MED['Year of Admission'].unique()},
        step=None
    ),
    
    html.Br(),
    
    dcc.Graph(id='age-vs-billing-amount-scatter'),
    dcc.Graph(id='medical-condition-bar-chart')
])

# Callback for updating graphs
@callback(
    Output('age-vs-billing-amount-scatter', 'figure'),
    Output('medical-condition-bar-chart', 'figure'),
    Input('admission-type-dropdown', 'value'),
    Input('year-slider', 'value')
)
def update_graphs(selected_admission_type, selected_year):
    # Filter data based on inputs
    filtered_df = MED[(MED['Admission Type'] == selected_admission_type) & 
                      (MED['Year of Admission'] == selected_year)]
    
    # Scatter plot for Age vs Billing Amount
    scatter_fig = px.scatter(filtered_df, x='Age', y='Billing Amount', 
                             title='Age vs Billing Amount', 
                             labels={'Age': 'Age', 'Billing Amount': 'Billing Amount'})

    # Bar chart for Medical Condition
    condition_counts = filtered_df['Medical Condition'].value_counts().reset_index()
    condition_counts.columns = ['Medical Condition', 'Count']  # Renaming columns for clarity

    bar_fig = px.bar(condition_counts, 
                    x='Medical Condition', 
                    y='Count', 
                    title='Count of Medical Conditions',
                    labels={'Medical Condition': 'Medical Condition', 'Count': 'Count'})

    return scatter_fig, bar_fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

