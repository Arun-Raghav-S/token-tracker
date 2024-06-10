from flask import Flask, redirect
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from pymongo import MongoClient
import pandas as pd
import plotly.graph_objs as go
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MongoDB connection string from environment variable
MONGODB_URI = os.getenv('MONGODB_URI')

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['langchain_db']
collection = db['token_tracking']

# Create a Flask server
server = Flask(__name__)

# Create a Dash app
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

# Function to fetch and process data
def fetch_data():
    data = list(collection.find())
    df = pd.DataFrame(data)
    
    # Convert the 'time' field to datetime
    df['time'] = pd.to_datetime(df['time'])
    
    # Ensure numeric columns are properly converted
    df['total_tokens'] = pd.to_numeric(df['total_tokens'], errors='coerce')
    df['cost'] = pd.to_numeric(df['cost'], errors='coerce')
    
    # Handle NaN values (e.g., by filling them with 0 or using a different strategy)
    df.fillna({'total_tokens': 0, 'cost': 0}, inplace=True)
    # df['total_tokens'].fillna(0, inplace=True)
    # df['cost'].fillna(0, inplace=True)
    
    # Drop non-numeric columns to avoid issues during resampling and aggregation
    df = df.drop(columns=['_id', 'completion', 'model_name'])
    
    # Add a column for API requests (each document represents one request)
    df['api_requests'] = 1
    
    # Aggregate data by day and week
    daily_usage = df.resample('D', on='time').sum()
    weekly_usage = df.resample('W', on='time').sum()
    
    return daily_usage, weekly_usage

# Layout of the Dash app
app.layout = html.Div(style={'backgroundColor': '#f9f9f9', 'padding': '20px'}, children=[
    html.H1("API Usage Dashboard", style={'textAlign': 'center'}),
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'padding': '20px'}, children=[
        dcc.Graph(id='daily-cost', style={'flex': '1'}),
    ]),
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '20px'}, children=[
        dcc.Graph(id='daily-tokens', style={'flex': '1', 'margin-right': '10px'}),
        dcc.Graph(id='daily-requests', style={'flex': '1', 'margin-left': '10px'}),
    ]),
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'padding': '20px'}, children=[
        dcc.Graph(id='weekly-cost', style={'flex': '1'}),
    ]),
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '20px'}, children=[
        dcc.Graph(id='weekly-tokens', style={'flex': '1', 'margin-right': '10px'}),
        dcc.Graph(id='weekly-requests', style={'flex': '1', 'margin-left': '10px'}),
    ]),
    dcc.Interval(id='interval-component', interval=1*60000, n_intervals=0)  # Update every minute
])

# Callback to update the graphs
@app.callback(
    [Output('daily-cost', 'figure'),
     Output('daily-tokens', 'figure'), Output('daily-requests', 'figure'),
     Output('weekly-cost', 'figure'), Output('weekly-tokens', 'figure'), Output('weekly-requests', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    daily_usage, weekly_usage = fetch_data()
    
    daily_cost_fig = go.Figure()
    daily_cost_fig.add_trace(go.Scatter(x=daily_usage.index, y=daily_usage['cost'], mode='lines+markers', name='Cost', line=dict(color='firebrick'), marker=dict(color='firebrick', size=6)))
    daily_cost_fig.update_layout(title='Daily Cost', xaxis_title='Date', yaxis_title='Cost ($)', xaxis=dict(tickformat='%Y-%m-%d', tickangle=45), template='plotly_white', plot_bgcolor='rgba(0,0,0,0)')
    
    daily_tokens_fig = go.Figure()
    daily_tokens_fig.add_trace(go.Scatter(x=daily_usage.index, y=daily_usage['total_tokens'], mode='lines+markers', name='Total Tokens', line=dict(color='royalblue'), marker=dict(color='royalblue', size=6)))
    daily_tokens_fig.update_layout(title='Daily Total Tokens', xaxis_title='Date', yaxis_title='Total Tokens', xaxis=dict(tickformat='%Y-%m-%d', tickangle=45), template='plotly_white', plot_bgcolor='rgba(0,0,0,0)')
    
    daily_requests_fig = go.Figure()
    daily_requests_fig.add_trace(go.Scatter(x=daily_usage.index, y=daily_usage['api_requests'], mode='lines+markers', name='API Requests', line=dict(color='green'), marker=dict(color='green', size=6)))
    daily_requests_fig.update_layout(title='Daily API Requests', xaxis_title='Date', yaxis_title='Number of Requests', xaxis=dict(tickformat='%Y-%m-%d', tickangle=45), template='plotly_white', plot_bgcolor='rgba(0,0,0,0)')
    
    weekly_cost_fig = go.Figure()
    weekly_cost_fig.add_trace(go.Scatter(x=weekly_usage.index, y=weekly_usage['cost'], mode='lines+markers', name='Cost', line=dict(color='firebrick'), marker=dict(color='firebrick', size=6)))
    weekly_cost_fig.update_layout(title='Weekly Cost', xaxis_title='Date', yaxis_title='Cost ($)', xaxis=dict(tickformat='%Y-%m-%d', tickangle=45), template='plotly_white', plot_bgcolor='rgba(0,0,0,0)')
    
    weekly_tokens_fig = go.Figure()
    weekly_tokens_fig.add_trace(go.Scatter(x=weekly_usage.index, y=weekly_usage['total_tokens'], mode='lines+markers', name='Total Tokens', line=dict(color='royalblue'), marker=dict(color='royalblue', size=6)))
    weekly_tokens_fig.update_layout(title='Weekly Total Tokens', xaxis_title='Date', yaxis_title='Total Tokens', xaxis=dict(tickformat='%Y-%m-%d', tickangle=45), template='plotly_white', plot_bgcolor='rgba(0,0,0,0)')
    
    weekly_requests_fig = go.Figure()
    weekly_requests_fig.add_trace(go.Scatter(x=weekly_usage.index, y=weekly_usage['api_requests'], mode='lines+markers', name='API Requests', line=dict(color='green'), marker=dict(color='green', size=6)))
    weekly_requests_fig.update_layout(title='Weekly API Requests', xaxis_title='Date', yaxis_title='Number of Requests', xaxis=dict(tickformat='%Y-%m-%d', tickangle=45), template='plotly_white', plot_bgcolor='rgba(0,0,0,0)')
    
    return daily_cost_fig, daily_tokens_fig, daily_requests_fig, weekly_cost_fig, weekly_tokens_fig, weekly_requests_fig

# Route to redirect root URL to the dashboard
@server.route('/')
def index():
    return redirect('/dashboard/')

# Run the server
if __name__ == '__main__':
    server.run(debug=True)
