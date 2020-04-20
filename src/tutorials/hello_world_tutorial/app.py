# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
df = pd.read_csv(f'https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/'
                 f'raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

markdown_text = '''
### Dash and Markdown

Dash apps can be written in Markdown.
Dash uses the [CommonMark](http://commonmark.org/)
specification of Markdown.
Check out their [60 Second Markdown Tutorial](http://commonmark.org/help/)
if this is your first introduction to Markdown!
'''

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Life expectancy versus Gross Domestic Product (GDP)',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.H3(style={'textAlign': 'center', 'color': colors['text']},
            children=dcc.Markdown(children=markdown_text)
            ),
    dcc.Graph(
        id='life-exp-vs-gdp',
        figure={
            'data': [
                dict(
                    x=df.loc[df.continent == i]['gdp per capita'],
                    y=df.loc[df.continent == i]['life expectancy'],
                    text=df.loc[df.continent == i]['country'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in df.continent.unique()
            ],
            'layout': dict(
                xaxis={'type': 'log', 'title': 'GDP per Capita'},
                yaxis={'title': 'Life Expectancy'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
