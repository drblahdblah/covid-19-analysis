"""
Corona Analysis
"""

from src.corona_analysis.create_corona_dfs import CoronaAnalysis
import pandas as pd
pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 1000)
pd.set_option("display.width", 1000)

if __name__ == '__main__':

    CoronaAnalysis.run_corona_analysis()
