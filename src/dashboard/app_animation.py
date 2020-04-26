import plotly.graph_objects as go
from datetime import datetime

import pandas as pd

pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 1000)
pd.set_option("display.width", 1000)

url = "https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv"
dataset = pd.read_csv(url)
print(dataset.head())

date_today = datetime.strftime(datetime.today(), '%d-%m-%Y')
stacked_df_path = f'../../data/output/complete_df/stacked/{date_today}/result.csv'
df = pd.read_csv(stacked_df_path, header=0)

days = df.Days.unique()
# print(f"Days: {df.Days.unique()}")

continents = df.Continent.unique()
# print(f"continents: {continents}")

# make figure
fig_dict = {
    "data": [],
    "layout": {},
    "frames": []
}

df_total_new_cases = df.loc[(df.indicator == 'total_cases') | (df.indicator == 'new_cases')]
df_total_new_cases = df_total_new_cases.drop(labels=['Unnamed: 0'], axis=1)
# print(df_total_new_cases.head())

# blerg = df_total_new_cases[['Date', 'indicator', 'value']]
pivoted = (df_total_new_cases
           .set_index(['Date', 'Country/Region', 'Continent', 'Days'])
           .pivot_table(values='value',
                        index=['Date', 'Country/Region', 'Continent', 'Days'],
                        columns='indicator',
                        aggfunc='mean',
                        fill_value=0)
           .reset_index()
           )
print(pivoted.loc[pivoted.Continent == 'Australia'].head())

# fill in most of layout
fig_dict["layout"]["xaxis"] = {"range": [0, 6],
                               "title": "Total Cases",
                               'type': 'log'}
fig_dict["layout"]["yaxis"] = {"range": [0, 5],
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
                                               "easing": "quadratic-in-out"}}
                         ],
                "label": "Play",
                "method": "animate"
            },
            {
                "args": [[None], {"frame": {"duration": 0,
                                            "redraw": False},
                                  "mode": "immediate",
                                  "transition": {"duration": 0}}
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
                "sizeref": 100,
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

fig = go.Figure(fig_dict)

fig.show()
