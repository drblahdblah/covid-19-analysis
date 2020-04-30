# -*- coding: utf-8 -*-
# import os
from datetime import datetime
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

# from create_corona_dfs import CoronaAnalysis

pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 1000)
pd.set_option("display.width", 1000)

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [f'https://github.com/plotly/dash-app-stylesheets/blob/master/dash-oil-and-gas.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

date_today = datetime.strftime(datetime.today(), '%d-%m-%Y')

# path_of_main_analysis = f"/data/output/complete_df/stacked/{date_today}/"
# if not os.path.exists(path_of_main_analysis):
#     CoronaAnalysis.run_corona_analysis()
stacked_df_path = f'./data/output/complete_df/stacked/{date_today}/result.csv'
df = pd.read_csv(stacked_df_path, header=0)
available_indicators = df['indicator'].unique()

days = df.Days.unique()
continents = df.Continent.unique()

df_total_new_cases = df.loc[(df.indicator == 'total_cases') |
                            (df.indicator == 'new_cases')]
df_total_new_cases = df_total_new_cases.drop(labels=['Unnamed: 0'], axis=1)

pivoted = (df_total_new_cases
           .set_index(['Date', 'Country/Region', 'Continent', 'Days'])
           .pivot_table(values='value',
                        index=['Date', 'Country/Region', 'Continent', 'Days'],
                        columns='indicator',
                        aggfunc='mean',
                        fill_value=0)
           .reset_index()
           )

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


def create_animation_scatter_plot() -> go.Figure:

    # make figure
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }

    # fill in most of layout
    fig_dict["layout"]["xaxis"] = {"range": [0, 6.5],
                                   "title": "Total Cases",
                                   'type': 'log'}
    fig_dict["layout"]["yaxis"] = {"range": [0, 5.5],
                                   "title": "New Cases",
                                   "type": "log"}
    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["sliders"] = {
        "args": [
            "transition", {
                "duration": 400,
                "easing": "cubic-in-out"
            }
        ],
        "initialValue": "0",
        "plotlycommand": "animate",
        "values": days,
        "visible": True
    }
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500,
                                              "redraw": False},
                                    "fromcurrent": True,
                                    "transition": {"duration": 300,
                                                   "easing": "quadratic-in-out"
                                                   }
                                    }
                             ],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0,
                                                "redraw": False
                                                },
                                      "mode": "immediate",
                                      "transition": {"duration": 0}
                                      }
                             ],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Day:",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 300, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    # make data
    day = 0
    for Continent in continents:
        dataset_by_day = pivoted[pivoted["Days"] == day]
        dataset_by_year_and_cont = dataset_by_day[
            dataset_by_day["Continent"] == Continent]

        data_dict = {
            "x": list(dataset_by_year_and_cont["total_cases"]),
            "y": list(dataset_by_year_and_cont["new_cases"]),
            "mode": "markers",
            "text": list(dataset_by_year_and_cont["Country/Region"]),
            "marker": {
                "sizemode": "area",
                "sizeref": 100,
                "size": list(dataset_by_year_and_cont["total_cases"])
            },
            "name": Continent
        }
        fig_dict["data"].append(data_dict)

    # make frames
    for day in days:
        frame = {"data": [], "name": str(day)}
        for continent in continents:
            dataset_by_year = pivoted[pivoted["Days"] == int(day)]
            dataset_by_year_and_cont = dataset_by_year[
                dataset_by_year["Continent"] == continent]

            data_dict = {
                "x": list(dataset_by_year_and_cont["total_cases"]),
                "y": list(dataset_by_year_and_cont["new_cases"]),
                "mode": "markers",
                "text": list(dataset_by_year_and_cont["Country/Region"]),
                "marker": {
                    "sizemode": "area",
                    "sizeref": 50,
                    "size": list(dataset_by_year_and_cont["total_cases"])
                },
                "name": continent
            }
            frame["data"].append(data_dict)

        fig_dict["frames"].append(frame)
        slider_step = {"args": [
            [str(day)],
            {"frame": {"duration": 300, "redraw": False},
             "mode": "immediate",
             "transition": {"duration": 300}}
        ],
            "label": str(day),
            "method": "animate"}
        sliders_dict["steps"].append(slider_step)

    fig_dict["layout"]["sliders"] = [sliders_dict]

    return go.Figure(fig_dict)


fig = create_animation_scatter_plot()

app.layout = html.Div([

    html.Title('Corona-virus Dashboard'),
    # Dashboard heading
    html.H1(
        children='Corona-virus Dashboard',
        style={
            'textAlign': 'center',
        }
    ),

    # Dashboard sub-heading
    html.Div(children=f'A dashboard for visualising my analyses of the Johns Hopkins Univerisity\'s (JHUs)'
                      f' corona-virus dataset.',
             style={
                 'textAlign': 'center',
             }),

    html.Div([
        # Left-hand (X-axis) dropdown and log/linear radio buttons
        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Total Cases (cumulative cases / country)'
            ),
            dcc.RadioItems(
                id='crossfilter-xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '49%',
                  'float': 'left',
                  'display': 'inline-block'}
        ),

        # Right-hand (Y-axis) dropdown and log/linear radio buttons
        html.Div([
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='New cases / day / country'
            ),
            dcc.RadioItems(
                id='crossfilter-yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    html.Div([
        html.Div([
            # Main plot
            dcc.Graph(
                id='crossfilter-indicator-scatter',
                hoverData={'points': [{'customdata': 'Spain'}]},
            )
        ], style={'width': '49%',
                  'float': 'left',
                  'display': 'inline-block',
                  'padding': '10 10',
                  'borderRight': 'thin lightgrey solid',
                  }
        ),

        # Right-hand-side X and Y time series
        html.Div([
            dcc.Graph(id='x-time-series'),
            dcc.Graph(id='y-time-series'),
        ], style={'display': 'inline-block',
                  'width': '49%',
                  'borderLeft': 'thin lightgrey solid'
                  }
        ),

        # Slider for time movement
        html.Div(dcc.Slider(
            id='crossfilter-year--slider',
            min=df['Days'].min(),
            max=df['Days'].max(),
            value=df['Days'].max(),
            marks={str(year): str(year) for year in df['Days'].unique()[0::5]},
            step=2
        ), style={'width': '49%',
                  'float': 'left',
                  'padding': '0px 20px 20px 20px'}
        ),
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }
    ),

    html.Div([
        dcc.Graph(id='total-new-cases-slider',
                  figure=fig,
                  style={'height': '700px'}),
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px',
        'vertical-align': 'middle'
    }
    ),

    html.Div(children=f'Copyright Dr. David I. Jones, 2020. MIT License. '
                      f'See https://github.com/drblahdblah/covid-19-analysis for the code.',
             style={
                 'textAlign': 'right',
                 'width': '100%'
             }
             )
])


@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-year--slider', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 date_value):
    dff = df[df['Days'] == date_value]
    return {
        'data': [dict(
            x=dff[(dff['indicator'] == xaxis_column_name) & (dff['Continent'] == i)]['value'],
            y=dff[(dff['Continent'] == i) & (dff['indicator'] == yaxis_column_name)]['value'],
            text=dff[(dff['indicator'] == yaxis_column_name) & (dff['Continent'] == i)]['Country/Region'],
            customdata=dff[(dff['indicator'] == yaxis_column_name) & (dff['Continent'] == i)]['Country/Region'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ) for i in dff['Continent'].unique()
        ],
        'layout': dict(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest'
        )
    }


def create_time_series(dff, axis_type, title):
    return {
        'data': [dict(
            x=dff['Date'],
            y=dff['value'],
            mode='lines+markers'
        )],
        'layout': {
            'height': 225,
            'margin': {'l': 40, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
            'xaxis': {'showgrid': False}
        }
    }


@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value')])
def update_y_timeseries(hover_data, xaxis_column_name, axis_type):
    country_name = hover_data['points'][0]['customdata']
    dff = df[df['Country/Region'] == country_name]
    dff = dff[dff['indicator'] == xaxis_column_name]
    title = f'<b>{country_name}</b><br>{xaxis_column_name}'
    return create_time_series(dff, axis_type, title)


@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-type', 'value')]
)
def update_x_timeseries(hover_data, yaxis_column_name, axis_type):
    dff = df[df['Country/Region'] == hover_data['points'][0]['customdata']]
    dff = dff[dff['indicator'] == yaxis_column_name]
    return create_time_series(dff, axis_type, yaxis_column_name)


if __name__ == '__main__':
    app.run_server(debug=True, port=8188)
