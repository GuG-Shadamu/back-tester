# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2024-06-01 09:51:01
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2024-06-01 20:44:17

import zmq
import protos.zmq_message_pb2 as pb
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import threading
import datetime
import json

# Dictionary to store DataFrames for different intervals
dataframes = {}
df_lock = threading.Lock()

new_data_event = threading.Event()

def receive_data():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5555")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    while True:
        full_message = socket.recv()

        # Parse the wrapper message
        wrapper = pb.Wrapper()
        wrapper.ParseFromString(full_message)

        if wrapper.type == pb.MessageType.MESSAGE_OHLCData:
            ohlc = wrapper.data
            # Convert timestamp from seconds to datetime
            timestamp_datetime = datetime.datetime.fromtimestamp(ohlc.timestamp)

            # Append new data to the appropriate DataFrame based on the interval
            new_data = pd.DataFrame({
                'timestamp': [timestamp_datetime],
                'open': [ohlc.open],
                'high': [ohlc.high],
                'low': [ohlc.low],
                'close': [ohlc.close]
            })

            with df_lock:
                if ohlc.interval not in dataframes:
                    dataframes[ohlc.interval] = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close'])
                dataframes[ohlc.interval] = pd.concat([dataframes[ohlc.interval], new_data], ignore_index=True)
            # Signal that new data is available
            new_data_event.set()

# Initialize Dash app
app = dash.Dash(__name__)

# Layout with placeholders for graphs and intervals
app.layout = html.Div([
    html.H1('Live OHLC Data'),
    html.Div(id='graphs-container'),
    dcc.Store(id='store-data'),  # Store component to hold the dataframes
    dcc.Interval(id='interval-trigger', interval=1*1000)  # Interval to trigger store update
])

# Callback to update the store with new data
@app.callback(
    Output('store-data', 'data'),
    [Input('interval-trigger', 'n_intervals')]
)
def update_store(n_intervals):
    if new_data_event.is_set():
        with df_lock:
            serializable_data = {
                k: df.assign(timestamp=df['timestamp'].astype(str)).to_dict(orient='list')
                for k, df in dataframes.items()
            }
        new_data_event.clear()
        return json.dumps(serializable_data)
    raise dash.exceptions.PreventUpdate

# Callback to update the graphs when new data is received
@app.callback(
    Output('graphs-container', 'children'),
    [Input('store-data', 'data')]
)
def update_graphs(data):
    if data is None:
        raise dash.exceptions.PreventUpdate

    dataframes = {int(k): pd.DataFrame(v).assign(timestamp=lambda df: pd.to_datetime(df['timestamp'])) for k, v in json.loads(data).items()}

    graphs = []
    for interval, df in dataframes.items():
        if df.empty:
            fig = go.Figure()
        else:
            fig = go.Figure(data=[go.Candlestick(x=df['timestamp'],
                                                 open=df['open'],
                                                 high=df['high'],
                                                 low=df['low'],
                                                 close=df['close'],
                                                 increasing_line_width=1.0,  # Adjust line width for better visibility
                                                 decreasing_line_width=1.0,  # Adjust line width for better visibility
                                                 )])
            fig.update_layout(
                title=f'{interval}-Minute OHLC Data',
                xaxis_title='Timestamp',
                yaxis_title='Price',
                xaxis_rangeslider_visible=False,
                xaxis=dict(
                    type='date',
                    tickformat='%Y-%m-%d %H:%M:%S',
                    tickangle=-45,
                    tickwidth=1,
                    tickcolor='blue',
                    showticklabels=True,
                    ticks='outside',
                    tickmode='linear',   # Ensure linear ticks
                    nticks=len(df),  # Number of ticks to ensure bars are close together
                    showgrid=False,   # Hide grid lines to make bars appear adjacent
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='LightPink'
                ),
                plot_bgcolor='white',
                bargap=0  # This makes the bars adjacent to each other
            )
        graphs.append(html.Div([dcc.Graph(figure=fig)]))
    return graphs

if __name__ == '__main__':
    # Start the data receiving thread
    data_thread = threading.Thread(target=receive_data, daemon=True)
    data_thread.start()

    # Run the Dash app in the main thread
    app.run_server(debug=True)
