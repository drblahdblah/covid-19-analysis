# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from datetime import datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

date_today = datetime.strftime(datetime.today(), '%d-%m-%Y')
df = pd.read_csv(f'~/PyCharmProjects/covid-19-analysis/data/output/data_at_state_level/'
                 f'{date_today}/data_state_and_cases.csv')

app.layout = html.Div([
    dcc.Graph(
        id='total-cases-by-country-and-state',
        figure={
            'data': [
                dict(
                    x=df[df['Country/Region'] == i]['Date'],
                    y=df[df['Country/Region'] == i]['total_cases'],
                    text=df[df['Country/Region'] == i]['Province/State'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {"width": 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in df['Country/Region'].unique()
            ],
            'layout': dict(
                xaxis={'title': 'Date'},
                yaxis={'title': 'Total Cases / Country / State / Day'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                hovermode='closest'
            )
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=8088)
