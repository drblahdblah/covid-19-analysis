"""
Module to create datasets from the raw JHU data for interactive plotting
of the coronavirus-related data. These datasets will then flow into the
dashboard(s) create to illustrate the data in a better manner than simple
plots in my Jupyter notebooks.
"""
import os
from datetime import datetime

import pandas as pd
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2
from src.corona_analysis.corona_transformations import CoronaTransformations

pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 1000)
pd.set_option("display.width", 1000)


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
        CoronaAnalysis.write_to_csv(df_to_write=melted_data, path_to_write_to=melted_data_dir)

        cts = CoronaTransformations()

        total_cases_df = cts.create_cases_per_day(df_to_transform=melted_data, groupby_list=['Date', 'Country/Region'])

        period = 1
        groupby_list = ['Country/Region']
        cases_per_period = cts.create_cases_per_period(df_to_transform=total_cases_df,
                                                       groupby_list=groupby_list,
                                                       case_column='total_cases')

        rolling_avg = cts.create_rolling_average(df_to_transform=cases_per_period,
                                                 groupby_list=groupby_list,
                                                 period=7)

        power_law = cts.calculate_power_law_columns(df_to_transform=rolling_avg,
                                                    cols_to_logify=['total_cases', 'new_cases_per_week'])

        pl_slope = cts.calculate_power_law_slope(df_to_transform=power_law,
                                                 period=10,
                                                 groupby_list=groupby_list,
                                                 rise='log_new_cases_per_week',
                                                 run='log_total_cases')

        pl_acceleration = cts.calculate_power_law_acceleration(df_to_transform=pl_slope,
                                                               period=period,
                                                               groupby_list=groupby_list,
                                                               rise='slope_log_new_cases_per_week',
                                                               run='log_total_cases')

        df_gr = cts.calculate_growth_rate(df_to_transform=pl_acceleration,
                                          period=5,
                                          groupby_list=groupby_list,
                                          new_cases='new_cases',
                                          total_cases='total_cases')

        df_dbl_time = cts.calculate_doubling_time(df_to_transform=df_gr,
                                                  period=5,
                                                  groupby_list=groupby_list)
        result_df_path = f'../data/output/complete_df/{date_today}'
        CoronaAnalysis.write_to_csv(df_to_write=df_dbl_time, path_to_write_to=result_df_path)
        print(f"Wrote out DF to {result_df_path}.")

        # Add continent to the data
        df_dbl_time = CoronaAnalysis.assign_continent_to_df(df_dbl_time)

        # Stack the DF to get data into format for the dashboard
        stacked = CoronaAnalysis.stack_data_for_dashboard(df_dbl_time)
        stacked_df_path = f'../data/output/complete_df/stacked/{date_today}'
        CoronaAnalysis.write_to_csv(df_to_write=stacked, path_to_write_to=stacked_df_path)
        print(f"Wrote out stacked DF to {stacked_df_path}.")

    @staticmethod
    def stack_data_for_dashboard(df_dbl_time):
        """
        Method to arrange data in a dataframe in a way that allows for representation in the dashboard
        :param df_dbl_time:
        :return:
        """
        stacked = df_dbl_time.set_index(['Date', 'Country/Region', 'Continent']).stack(dropna=False).reset_index()
        stacked = stacked.rename(columns={"level_3": "indicator", 0: "value"})
        stacked['Days'] = (stacked
                           .groupby(['Country/Region'])['Date']
                           .transform(lambda x: (x - x.min()).dt.days)
                           )
        return stacked

    @staticmethod
    def assign_continent_to_df(df_dbl_time: pd.DataFrame) -> pd.DataFrame:
        """
        Method to assign a continent to a country in the given dataframe. Some
        alterations have had to be made due to the absence of them in the ISO codes.
        This in NO way is a political statement from the author.
        :param df_dbl_time:
        :return:
        """
        continents = {
            'NA': 'North America',
            'SA': 'South America',
            'AS': 'Asia',
            'OC': 'Australia',
            'AF': 'Africa',
            'EU': 'Europe'
        }
        df_dbl_time.loc[df_dbl_time['Country/Region'] == 'US', 'Country/Region'] = 'USA'
        df_dbl_time.loc[df_dbl_time['Country/Region'] == 'Burma', 'Country/Region'] = 'Myanmar'
        df_dbl_time.loc[df_dbl_time['Country/Region'] == 'Congo (Brazzaville)', 'Country/Region'] = 'Congo'
        df_dbl_time.loc[df_dbl_time['Country/Region'] == 'Congo (Kinshasa)', 'Country/Region'] = 'Congo'
        df_dbl_time.loc[df_dbl_time['Country/Region'] == 'Cote d\'Ivoire', 'Country/Region'] = 'Ivory Coast'
        df_dbl_time.loc[df_dbl_time['Country/Region'] == 'Diamond Princess', 'Country/Region'] = 'Japan'
        df_dbl_time.loc[df_dbl_time['Country/Region'] == 'Holy See', 'Country/Region'] = 'Italy'
        df_dbl_time.loc[df_dbl_time['Country/Region'] == 'Korea, South', 'Country/Region'] = 'South Korea'
        df_dbl_time.loc[df_dbl_time['Country/Region'] == 'Kosovo', 'Country/Region'] = 'Serbia'
        df_dbl_time.loc[df_dbl_time['Country/Region'] == 'MS Zaandam', 'Country/Region'] = 'Netherlands'
        df_dbl_time.loc[df_dbl_time['Country/Region'] == 'Taiwan*', 'Country/Region'] = 'Taiwan'
        df_dbl_time.loc[df_dbl_time['Country/Region'] == 'Timor-Leste', 'Country/Region'] = 'Indonesia'
        df_dbl_time.loc[df_dbl_time['Country/Region'] == 'West Bank and Gaza', 'Country/Region'] = 'Israel'
        df_dbl_time.loc[df_dbl_time['Country/Region'] == 'Western Sahara', 'Country/Region'] = 'Mali'
        df_dbl_time['Continent'] = (df_dbl_time.apply(
            lambda x: continents[country_alpha2_to_continent_code(country_name_to_country_alpha2(x['Country/Region']))],
            axis=1)
        )
        return df_dbl_time

    @staticmethod
    def write_to_csv(df_to_write: pd.DataFrame, path_to_write_to: str):
        if not os.path.exists(path_to_write_to):
            os.makedirs(path_to_write_to)
        df_to_write.to_csv(f'{path_to_write_to}/result.csv')
