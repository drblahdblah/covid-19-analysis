"""
Corona Analysis
"""

from src.corona_analysis.create_corona_dfs import CoronaAnalysis
from datetime import datetime
import os

if __name__ == '__main__':
    date_today = datetime.strftime(datetime.today(), '%d-%m-%Y')
    print(f"Preparing data for {date_today}")
    corona_analysis = CoronaAnalysis(case_type='case', data_type='world')
    raw_data = corona_analysis.load_raw_data()
    melted_data = corona_analysis.melt_df(raw_data=raw_data)
    melted_data_dir = f'../data/output/data_at_state_level/{date_today}'
    print(f"Placing data in directory {melted_data_dir}")
    if not os.path.exists(melted_data_dir):
        os.makedirs(melted_data_dir)
    melted_data.to_csv(f'{melted_data_dir}/data_state_and_cases.csv')
    print(melted_data.head())
