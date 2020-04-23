# -*- coding: utf-8 -*-

from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html

from src.corona_analysis.create_corona_dfs import CoronaAnalysis

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

date_today = datetime.strftime(datetime.today(), '%d-%m-%Y')
ca = CoronaAnalysis(case_type='case', data_type='world')
df, complete_data = ca.run_corona_analysis()

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Corona-virus Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children=f'A dashboard for visualising my analyses of the Johns Hopkins Univerisity\'s (JHUs)'
                      f'corona-virus dataset.',
             style={
                 'textAlign': 'center',
                 'color': colors['text']
             }),

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
                yaxis={'title': 'Total Cases / Country'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                hovermode='closest',
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
                font={
                    'color': colors['text']
                }
            )
        }
    ),

    html.Div(children=f'(C) Dr. David I. Jones, 2020. MIT License. See https://github.com/drblahdblah/covid-19-analysis'
                      f' xfor the code.',
             style={
                 'textAlign': 'right',
                 'color': colors['text']
             }),
])

if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=8088)
