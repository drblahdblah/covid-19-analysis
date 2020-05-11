"""
Corona Analysis
"""

from src.corona_analysis.create_corona_dfs import CoronaAnalysis
import pandas as pd
from datetime import datetime

pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 1000)
pd.set_option("display.width", 1000)

if __name__ == '__main__':
    date_today = datetime.strftime(datetime.today(), '%d-%m-%Y')

    ca_cases = CoronaAnalysis(data_type='world', case_type='case', processing_date=date_today)
    ca_cases.run_corona_analysis()

    ca_deaths = CoronaAnalysis(data_type='world', case_type='death', processing_date=date_today)
    ca_deaths.run_corona_analysis()

    ca_us_cases = CoronaAnalysis(data_type='usa', case_type='case', processing_date=date_today)
    ca_us_cases.run_corona_analysis()

    ca_us_deaths = CoronaAnalysis(data_type='usa', case_type='death', processing_date=date_today)
    ca_us_deaths.run_corona_analysis()
