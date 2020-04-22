# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

df = pd.read_csv(f'https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/'
                 f'raw/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv')


def generate_simple_table(dataframe: pd.DataFrame, max_rows=10) -> html.Table:
    """
    Simple function to return a simple HTML table for a Dash dashboard.
    :param dataframe: A Pandas DataFrame to plot.
    :param max_rows: The maximum number of rows to plot: defaults to 10
    :return: A HTML table object.
    """

    return html.Table([
        html.Thead(
            html.Tr([html.Tr(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col] for col in dataframe.columns)
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H4(children="US Agriculture Exports (2011)"),
    generate_simple_table(dataframe=df, max_rows=10)
])

if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=8088)
