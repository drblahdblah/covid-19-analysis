import plotly.express as px
import pandas as pd
import numpy as np
from datetime import date
import os

import plotly.io as pio
pio.renderers.default = "browser"



# load proc data
df = pd.read_csv(f'../data/output/complete_df/23-04-2020/result.csv')
df = df.groupby(['Country/Region', 'Date'], as_index=False).sum()

# Add color for some countries
col_countries = ['US', 'Spain', 'Italy', 
    # 'France', 
    'China', 'Netherlands', 'Australia', 
    # 'Japan', 
    'United Kingdom',
    'Diamond Princess', 'Korea, South']
df['Region'] = np.where(df['Country/Region'].isin(col_countries), 
    df['Country/Region'], 'Other countries')

df['growth_rate_clip'] = df['growth_rate'].clip(lower=1)
# df['New cases per week'] = 10**df['log_new_cases_per_week']

df['New cases per week'] = df['new_cases_per_week'].clip(lower=1)
df['Total cases'] = df['total_cases'].clip(lower=1)


# plotly

fig = px.scatter(df, x="Total cases", y="New cases per week", 
        animation_frame="Date", animation_group="Country/Region",
           size="growth_rate_clip", 
           size_max=100, 
           color="Region", 
           hover_name="Country/Region",
           log_x=False, 
           log_y=False, 
            range_x=[1, 1e6],
           range_y=[1, 1e6],
           title='Covid19 cases per region: Marker size is growth rate'
           )

fig.write_html("animation_non_log_scale.html")

fig
