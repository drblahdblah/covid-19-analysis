"""
Module to create datasets from the raw JHU data for interactive plotting
of the coronavirus-related data. These datasets will then flow into the
dashboard(s) create to illustrate the data in a better manner than simple
plots in my Jupyter notebooks.
"""
import os
from datetime import datetime

import pandas as pd

from src.corona_analysis.corona_transformations import CoronaTransformations


class CoronaAnalysis:
    """
    Class containing methods to create datasets that allow for
    dashboarding of data pertaining to the Corona-virus pandemic of 2020.
    """
    def __init__(self, data_type: str, case_type: str):
        self.data_type = data_type
        self.case_type = case_type

    def load_raw_data(self) -> pd.DataFrame:
        """
        Method to load the raw data into a dataframe.
        or the USA-specific data.
        :return: A Pandas DataFrame containing the raw data.
        """
        # if self.data_type != 'world' or self.data_type != 'usa':
        #     print(f"Please check which data_type you want to load:\n"
        #           f"Possible values: 'world' or 'usa'")
        #     exit(1)
        #
        # if self.case_type != 'death' or self.case_type != 'case':
        #     print(f"Please check which case_type you want to load:\n"
        #           f"Possible values: 'case' or 'death'")
        #     exit(1)

        if self.data_type == 'world' and self.case_type == 'case':
            raw_data = pd.read_csv(f'~/PyCharmProjects/covid-19-analysis/data/COVID-19/csse_covid_19_data/'
                                   f'csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
        elif self.data_type == 'world' and self.case_type == 'death':
            raw_data = pd.read_csv(f'~/PyCharmProjects/covid-19-analysis/data/COVID-19/csse_covid_19_data/'
                                   f'csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
        elif self.data_type == 'usa' and self.case_type == 'death':
            raw_data = pd.read_csv(f'~/PyCharmProjects/covid-19-analysis/data/COVID-19/csse_covid_19_data/'
                                   f'csse_covid_19_time_series/time_series_covid19_deaths_US.csv')
        else:
            raw_data = pd.read_csv('~/PyCharmProjects/covid-19-analysis/data/COVID-19/csse_covid_19_data/'
                                   'csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
        useful_cols = [col for col in raw_data.columns if col not in ['Lat', 'Long']]
        return raw_data[useful_cols]

    @staticmethod
    def melt_df(raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Method to turn a raw dataframe (with state, country, date_1, ..., date_n)
        into a dataframe with a date column and the total number of cases/deaths/etc.
        :return: A pivoted Pandas DataFrame with a date column.
        """
        world_data = (raw_data
                      .melt(id_vars=["Province/State", 'Country/Region'],
                            var_name="Date",
                            value_name='total_cases')
                      )
        world_data.Date = pd.to_datetime(world_data.Date)
        return world_data

    @staticmethod
    def run_corona_analysis():

        date_today = datetime.strftime(datetime.today(), '%d-%m-%Y')

        corona_analysis = CoronaAnalysis(case_type='case', data_type='world')
        raw_data = corona_analysis.load_raw_data()
        melted_data = corona_analysis.melt_df(raw_data=raw_data)
        melted_data_dir = f'../data/output/data_at_state_level/{date_today}'
        if not os.path.exists(melted_data_dir):
            os.makedirs(melted_data_dir)
        melted_data.to_csv(f'{melted_data_dir}/data_state_and_cases.csv')

        cts = CoronaTransformations()

        total_cases_df = cts.create_cases_per_day(df_to_transform=melted_data, groupby_list=['Date', 'Country/Region'])

        period = 1
        groupby_list = ['Country/Region']
        cases_per_period = cts.create_cases_per_period(df_to_transform=total_cases_df,
                                                       groupby_list=groupby_list,
                                                       case_column='total_cases')
        print(f"cases_per_period:\n {cases_per_period.head()}")

        rolling_avg = cts.create_rolling_average(df_to_transform=cases_per_period,
                                                 groupby_list=groupby_list,
                                                 period=7)
        print(f"rolling_avg:\n {rolling_avg.head()}")

        # def calculate_power_law_columns(df_to_transform, cols_to_logify: list) -> pd.DataFrame:
        power_law = cts.calculate_power_law_columns(df_to_transform=rolling_avg,
                                                    cols_to_logify=['total_cases', 'new_cases_per_week'])
        print(f"power_law:\n {power_law.head()}")

        pl_slope = cts.calculate_power_law_slope(df_to_transform=power_law,
                                                 period=10,
                                                 groupby_list=groupby_list,
                                                 rise='log_new_cases_per_week',
                                                 run='log_total_cases')
        print(f"pl_slope:\n {pl_slope.loc[pl_slope['Country/Region'] == 'Australia'].head(20)}")

        pl_acceleration = cts.calculate_power_law_acceleration(df_to_transform=pl_slope,
                                                               period=period,
                                                               groupby_list=groupby_list,
                                                               rise='slope_log_new_cases_per_week',
                                                               run='log_total_cases')
        print(f"pl_acceleration:\n {pl_acceleration.loc[pl_acceleration['Country/Region'] == 'Australia'].head(20)}")

        # def calculate_growth_rate(df_to_transform: pd.DataFrame, period: int, groupby_list: list, new_cases: str,
        #                           total_cases: str) -> pd.DataFrame:
        df_gr = cts.calculate_growth_rate(df_to_transform=pl_acceleration,
                                          period=5,
                                          groupby_list=groupby_list,
                                          new_cases='new_cases',
                                          total_cases='total_cases')
        print(f"df_gr:\n {df_gr.loc[df_gr['Country/Region'] == 'Australia'].head(20)}")

        df_dbl_time = cts.calculate_doubling_time(df_to_transform=df_gr,
                                                  period=5,
                                                  groupby_list=groupby_list)
        print(f"df_dbl_time:\n {df_dbl_time.loc[df_dbl_time['Country/Region'] == 'Australia'].head(20)}")
