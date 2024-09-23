import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import requests
import os
import random
import subprocess
from datetime import datetime

app = dash.Dash(__name__)

GOTIFY_URL = os.environ.get('GOTIFY_URL')
GOTIFY_TOKEN = os.environ.get('GOTIFY_TOKEN')
DOMAIN = os.environ.get('DOMAIN')

# List of Iranian IP ranges (this is a small sample, you might want to expand this)
IRAN_IP_RANGES = [
    "2.144.0.0/14",
    "2.176.0.0/12",
    "5.22.0.0/17",
    "5.22.192.0/19",
    "5.23.112.0/21",
    "5.52.0.0/16",
    "5.53.32.0/19",
    "5.56.128.0/22",
    "5.57.32.0/21",
    "5.61.24.0/22",
    "5.62.160.0/19",
    "5.72.0.0/14",
    "5.102.16.0/20",
    "5.106.0.0/16",
    "5.134.128.0/18",
    "5.144.128.0/18",
    "5.160.0.0/15",
    "5.190.0.0/16",
    "5.198.160.0/19",
    "5.200.0.0/19",
    "5.201.128.0/17",
    "5.202.0.0/16",
    "5.208.0.0/12",
    "5.226.0.0/16",
    "5.232.0.0/13",
]

def send_gotify_alert(title, message):
    requests.post(
        f"{GOTIFY_URL}/message",
        json={"title": title, "message": message, "priority": 5},
        headers={"X-Gotify-Key": GOTIFY_TOKEN}
    )

def check_iran_accessibility():
    ip = random.choice(IRAN_IP_RANGES).split('/')[0]  # Get a random IP from the ranges
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '5', ip], capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking accessibility: {e}")
        return False

app.layout = html.Div([
    html.H1('DNS Metrics Dashboard'),
    dcc.Graph(id='dns-queries-graph'),
    dcc.Graph(id='traefik-requests-graph'),
    html.Div(id='traefik-logs'),
    html.Div(id='iran-accessibility'),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # in milliseconds
        n_intervals=0
    )
])

@app.callback(
    [Output('dns-queries-graph', 'figure'),
     Output('traefik-requests-graph', 'figure'),
     Output('traefik-logs', 'children'),
     Output('iran-accessibility', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_graphs(n):
    # DNS Queries Graph
    dns_response = requests.get('http://prometheus:9090/api/v1/query', params={
        'query': 'rate(dnsmasq_queries_total[5m])'
    })
    dns_data = dns_response.json()['data']['result']
    dns_df = pd.DataFrame(dns_data)
    dns_df['value'] = dns_df['value'].apply(lambda x: x[1])
    dns_fig = px.line(dns_df, x='timestamp', y='value', title='DNS Queries per Second')

    # Traefik Requests Graph
    traefik_response = requests.get('http://prometheus:9090/api/v1/query', params={
        'query': 'sum(rate(traefik_entrypoint_requests_total[5m])) by (entrypoint)'
    })
    traefik_data = traefik_response.json()['data']['result']
    traefik_df = pd.DataFrame(traefik_data)
    traefik_df['value'] = traefik_df['value'].apply(lambda x: x[1])
    traefik_fig = px.line(traefik_df, x='timestamp', y='value', color='entrypoint', title='Traefik Requests per Second')

    # Traefik Logs
    with open('/app/traefik_logs/access.log', 'r') as f:
        logs = f.readlines()[-10:]  # Get last 10 lines
    log_output = html.Ul([html.Li(log) for log in logs])

    # Iran Accessibility
    iran_accessible = check_iran_accessibility()
    accessibility_status = html.P(f"Server is {'accessible' if iran_accessible else 'not accessible'} from Iran")

    # Send alert if not accessible
    if not iran_accessible:
        send_gotify_alert("Server Inaccessible", f"Server {DOMAIN} is not accessible from Iran")

    return dns_fig, traefik_fig, log_output, accessibility_status

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')