"""
Corona Analysis
"""

from datetime import datetime

from src.corona_analysis.create_corona_dfs import CoronaAnalysis

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

    ca_aus_cases = CoronaAnalysis(data_type='aus', case_type='case', processing_date=date_today)
    ca_aus_cases.run_corona_analysis()
