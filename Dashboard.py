from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import pandas_ta as ta
import requests

app = Dash(external_stylesheets = [dbc.themes.CYBORG])

def create_dropdown(option, id_value):

    return html.Div([html.H5(' '.join(id_value.replace('-',' ').split(' ')[:-1]),
                                style={'padding': '0px 5ßpx 0px 50px'}),
                    dcc.Dropdown(option, id=id_value, value=option[0], style={'width':'100px'})])


app.layout = html.Div([
    # html.H2('Interactive Real-Time Crypto Chart', style={'margin':'auto', 'textAlign':'center', 'padding-down':'20px'}),
    html.Div([
        create_dropdown(['btcusd', 'ethusd', 'xrpusd'], 'Coin-USD-select'),
        create_dropdown(['60', '3600', '86400'], 'Timeframe-[s]-select'),
        create_dropdown(['20', '50', '100'], 'Number-of-Bars-select'),
        ], style = {'display':'flex', 'margin':'auto', 'width':'800px', 'justify-content':'space-around'}),


    html.Div([
        dcc.RangeSlider(min=0, max=20, step=1, value=[0, 20], id='range-slider'),
         ], id = 'range-slider-container',
         style = {'width':'880px', 'margin':'auto', 'padding-top':'30px'}),


    dcc.Graph(id='candles'),
    dcc.Graph(id='indicator'),
    dcc.Interval(id='interval', interval=2000),

    ])

# update the rangeslider when the interval is selected
@app.callback(
        Output('range-slider-container', 'children'),
        Input('Number-of-Bars-select', 'value')
            )

def update_Rangeslider(num_bars):
    return dcc.RangeSlider(min=0, max=int(num_bars), step=int(int(num_bars) / 20),
                           value=[0, int(num_bars)], id='range-slider')
# main callbacks
@app.callback(
        Output('candles', 'figure'),
        Output('indicator', 'figure'),
        Input('interval', 'n_intervals'),
        Input('Coin-USD-select', 'value'),
        Input('Timeframe-[s]-select', 'value'),
        Input('Number-of-Bars-select', 'value'),
        Input('range-slider', 'value'),
            )

def update_figure(n_intervals, coin_pair, time_frame, num_bars, range_values):
    url = f'https://www.bitstamp.net/api/v2/ohlc/{coin_pair}/'

    params = {
            'step': time_frame,
            # adding 14 because the rsi need a 14 days runup to be displayed
            'limit':int(num_bars)+14,
             }
    # dictonary of values
    data = requests.get(url, params=params).json()['data']['ohlc']

    # Change it to a pd.Dataframe()
    data = pd.DataFrame(data)

    # Change time to datetime for plotly to be able to pick it up
    data.timestamp = pd.to_datetime(data.timestamp, unit='s')

    # calculating the rsi
    data['rsi'] = ta.rsi(data.close.astype(float))
    # cutting the non displaing warm up bars
    data = data.iloc[14:]
    # adjusting to the range slider
    data = data.iloc[range_values[0]:range_values[1]]

    # Create a object of candlecharts
    candles = go.Figure(
                    data = [
                        go.Candlestick(
                            x=data.timestamp,
                            open = data.open,
                            high = data.high,
                            low = data.low,
                            close = data.close
                            )
                        ]
                    )
        # updating the layout and design of the figure
    candles.update_layout(xaxis_rangeslider_visible=False, height=400, template='none'
                          , title_text='Coin to USD Chart', title_font_size=20, title_x=0.5, yaxis_title="$USD Value")

    # creating a indicator graph
    indicator = px.line(x=data.timestamp, y=data.rsi, height=300, title="Relative Strength Index (RSI) Chart"
                        , labels = {'x':'Date', 'y':'RSI'}, template='none')
    indicator.update_layout(title_font_size=20, title_x=0.5)

    return candles, indicator

if __name__ == '__main__':
    app.run_server(debug=False)
