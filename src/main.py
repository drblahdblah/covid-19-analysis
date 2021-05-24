"""
Corona Analysis
"""

from datetime import datetime

from src.corona_analysis.create_corona_dfs import CoronaAnalysis

if __name__ == '__main__':

    date_today = datetime.strftime(datetime.today(), '%d-%m-%Y')

    for country in ['world', 'usa', 'aus']:
        for analysis_type in ['case', 'death']:

            print(f"Processing data for {country} {analysis_type}s for {date_today}.")

            ca_object = CoronaAnalysis(data_type=country,
                                       case_type=analysis_type,
                                       processing_date=date_today)
            ca_object.run_corona_analysis()
