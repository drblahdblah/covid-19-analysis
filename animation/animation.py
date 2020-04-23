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
df['color_country'] = np.where(df['Country/Region'].isin(col_countries), 
    df['Country/Region'], 'other')

df['growth_rate_clip'] = df['growth_rate'].clip(lower=1)

# plotly

fig = px.scatter(df, x="log_total_cases", y="log_new_cases_per_week", 
        animation_frame="Date", animation_group="Country/Region",
           size="growth_rate_clip", 
           size_max=100, 
           color="color_country", 
           hover_name="Country/Region",
        #    log_x=True, 
           range_x=[0, int(df['log_total_cases'].max())+1], 
           range_y=[0, int(df['log_new_cases_per_week'].max())+1],
           title='Covid19: Size is growth rate'
           )

fig.write_html("animation.html")

fig

