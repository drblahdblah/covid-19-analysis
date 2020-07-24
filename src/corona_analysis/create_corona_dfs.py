"""
Module to create datasets from the raw JHU data for interactive plotting
of the coronavirus-related data. These datasets will then flow into the
dashboard(s) create to illustrate the data in a better manner than simple
plots in my Jupyter notebooks.
"""
import os

import pandas as pd
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2

from src.corona_analysis.corona_transformations import CoronaTransformations


class CoronaAnalysis:
    """
    Class containing methods to create datasets that allow for
    dashboarding of data pertaining to the Corona-virus pandemic of 2020.
    """
    def __init__(self, data_type: str, case_type: str, processing_date: str):
        self.data_type = data_type
        self.case_type = case_type
        self.processing_date = processing_date

    def load_raw_data(self) -> pd.DataFrame:
        """
        Method to load the raw data into a dataframe.
        or the USA-specific data.
        :return: A Pandas DataFrame containing the raw data.
        """

        if self.data_type == 'world' and self.case_type == 'case':
            raw_data = pd.read_csv(f'~/PyCharmProjects/covid-19-analysis/data/COVID-19/csse_covid_19_data/'
                                   f'csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
        elif self.data_type == 'world' and self.case_type == 'death':
            raw_data = pd.read_csv(f'~/PyCharmProjects/covid-19-analysis/data/COVID-19/csse_covid_19_data/'
                                   f'csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
        elif self.data_type == 'usa' and self.case_type == 'death':
            raw_data = pd.read_csv(f'~/PyCharmProjects/covid-19-analysis/data/COVID-19/csse_covid_19_data/'
                                   f'csse_covid_19_time_series/time_series_covid19_deaths_US.csv')
        elif self.data_type == 'usa' and self.case_type == 'case':
            raw_data = pd.read_csv('~/PyCharmProjects/covid-19-analysis/data/COVID-19/csse_covid_19_data/'
                                   'csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
        elif self.data_type == 'aus' and self.case_type == 'case':
            raw_data = pd.read_csv(f'~/PyCharmProjects/covid-19-analysis/data/COVID-19/csse_covid_19_data/'
                                   f'csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
            raw_data = raw_data.loc[raw_data['Country/Region'] == 'Australia']

        # Default to worldwide cases.
        else:
            raw_data = pd.read_csv(f'~/PyCharmProjects/covid-19-analysis/data/COVID-19/csse_covid_19_data/'
                                   f'csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

        raw_data_filtered = pd.DataFrame
        if self.data_type == 'world':
            useful_cols = [col for col in raw_data.columns if col not in ['Lat', 'Long']]
            raw_data_filtered = raw_data[useful_cols]
            countries_to_drop = ['Holy See', 'Congo (Brazzaville)', 'Congo (Kinshasa)', 'Diamond Princess',
                                 'MS Zaandam', 'Kosovo', 'Timor-Leste', 'West Bank and Gaza', 'Western Sahara']
            raw_data_filtered = raw_data_filtered.loc[~raw_data_filtered['Country/Region'].isin(countries_to_drop)]

        elif self.data_type == 'usa' and self.case_type == 'case':
            useful_cols = [col for col in raw_data.columns if col not in ['UID', 'iso2', 'iso3', 'code3',
                                                                          'FIPS', 'Admin2', 'Country_Region',
                                                                          'Long_', 'Lat', 'Combined_Key']]
            raw_data_filtered = raw_data[useful_cols]

        elif self.data_type == 'usa' and self.case_type == 'death':
            useful_cols = [col for col in raw_data.columns if col not in ['UID', 'iso2', 'iso3', 'code3',
                                                                          'FIPS', 'Admin2', 'Country_Region',
                                                                          'Long_', 'Lat', 'Combined_Key', 'Population']]
            raw_data_filtered = raw_data[useful_cols]

        elif self.data_type == 'aus' and self.case_type == 'case':
            useful_cols = [col for col in raw_data.columns if col not in ['Lat', 'Long', 'Country/Region']]
            raw_data_filtered = raw_data[useful_cols]

        return raw_data_filtered

    @staticmethod
    def melt_df(raw_data: pd.DataFrame, id_vars: list) -> pd.DataFrame:
        """
        Method to turn a raw dataframe (with state, country, date_1, ..., date_n)
        into a dataframe with a date column and the total number of cases/deaths/etc.
        :param raw_data: The Pandas DataFrame to melt.
        :param id_vars: The columns to group by to create melted DataFrame with.
        :return: A pivoted Pandas DataFrame with a date column.
        """
        world_data = (raw_data
                      .melt(id_vars=id_vars,
                            var_name="Date",
                            value_name='total_cases')
                      )
        world_data.Date = pd.to_datetime(world_data.Date)
        return world_data

    def run_corona_analysis(self):
        """
        Main function to run analyses of World, USA, and Australian corona virus data from the JHU database
        """
        cts = CoronaTransformations(case_type=self.case_type, data_type=self.data_type)
        print(f"Running analysis for {self.case_type} and {self.data_type} for date {self.processing_date}")

        raw_data = self.load_raw_data()

        if self.data_type == 'world':
            groupby_list = ['Country/Region']
            groupby_list_cases_per_day = ['Date', 'Country/Region']
            id_vars = ["Province/State", 'Country/Region']
        elif self.data_type == 'usa' and self.case_type == 'death':
            groupby_list_cases_per_day = ['Date', 'Province_State']
            groupby_list = ['Province_State']
            id_vars = ["Province_State"]
        elif self.data_type == 'aus' and self.case_type == 'case':
            groupby_list_cases_per_day = ['Date', 'Province/State']
            groupby_list = ['Province/State']
            id_vars = ["Province/State"]
        else:
            groupby_list_cases_per_day = ['Date', 'Province_State']
            groupby_list = ['Province_State']
            id_vars = ["Province_State"]

        melted_data = self.melt_df(raw_data=raw_data, id_vars=id_vars)

        print(f"Creating total number of {self.case_type}s for data type {self.data_type}...")
        total_cases_df = cts.create_cases_per_day(df_to_transform=melted_data,
                                                  groupby_list=groupby_list_cases_per_day)
        print("done.")

        print(f"Creating number of {self.case_type}s per period")
        period = 1
        cases_per_period = cts.create_cases_per_period(df_to_transform=total_cases_df,
                                                       groupby_list=groupby_list,
                                                       case_column='Total cases')
        print("done.")

        print(f"Creating rolling average of {self.case_type}s per period")
        rolling_avg = cts.create_rolling_average(df_to_transform=cases_per_period,
                                                 groupby_list=groupby_list,
                                                 period=7)
        print("done.")

        print(f"Creating power-law data products for {self.case_type}s")
        power_law = cts.calculate_power_law_columns(df_to_transform=rolling_avg,
                                                    cols_to_logify=['Total cases', 'New cases per week'])

        pl_slope = cts.calculate_power_law_slope(df_to_transform=power_law,
                                                 period=10,
                                                 groupby_list=groupby_list,
                                                 rise='log10(New cases per week)',
                                                 run='log10(Total cases)')

        pl_acceleration = cts.calculate_power_law_acceleration(df_to_transform=pl_slope,
                                                               period=period,
                                                               groupby_list=groupby_list,
                                                               rise='slope of log10(New cases per week)',
                                                               run='log10(Total cases)')
        pl_acceleration = (pl_acceleration
                           .rename(columns={"slope of slope of log10(New cases per week)": "Acceleration of power-law",
                                            "slope of log10(New cases per week)": "Slope of power-law"})
                           )
        print("done.")
        print(f"Creating growth rates and doubling times for {self.case_type}s.")
        df_gr = cts.calculate_growth_rate(df_to_transform=pl_acceleration,
                                          period=5,
                                          groupby_list=groupby_list,
                                          new_cases='New cases',
                                          total_cases='Total cases')

        df_dbl_time = cts.calculate_doubling_time(df_to_transform=df_gr,
                                                  period=5,
                                                  groupby_list=groupby_list)
        print("done.")

        result_df_path = f'processed_data/'
        self.write_to_csv(df_to_write=df_dbl_time,
                          path_to_write_to=result_df_path,
                          file_name='result.csv')

        # Add continent to the data
        print(f"Adding continents to the {self.case_type}s data")
        df_dbl_time_with_cont = self.assign_continent_to_df(df_add_continent=df_dbl_time)
        print("done.")

        # Stack the DF to get data into format for the dashboard
        print(f"Preparing data for {self.case_type}s for dashboard")
        stacked = self.stack_data_for_dashboard(df_dbl_time_with_cont)

        stacked_df_path = f'stacked/'
        self.write_to_csv(df_to_write=stacked,
                          path_to_write_to=stacked_df_path,
                          file_name='result.csv')

        # pivot data for dashboard
        df_total_new_cases = stacked.loc[(stacked.indicator == 'Total cases') |
                                         (stacked.indicator == 'New cases') |
                                         (stacked.indicator == 'Growth Rate')]

        if self.data_type == 'world':
            pivoted = (df_total_new_cases
                       .set_index(['Date', 'Country/Region', 'Continent', 'Days'])
                       .pivot_table(values='value',
                                    index=['Date', 'Country/Region', 'Continent', 'Days'],
                                    columns='indicator',
                                    aggfunc='mean',
                                    fill_value=0)
                       .reset_index()
                       )
        elif self.data_type == 'aus' and self.case_type == 'case':
            pivoted = (df_total_new_cases
                       .set_index(['Date', 'Province/State', 'Days'])
                       .pivot_table(values='value',
                                    index=['Date', 'Province/State', 'Days'],
                                    columns='indicator',
                                    aggfunc='mean',
                                    fill_value=0)
                       .reset_index()
                       )
        else:
            pivoted = (df_total_new_cases
                       .set_index(['Date', 'Province_State', 'Days'])
                       .pivot_table(values='value',
                                    index=['Date', 'Province_State', 'Days'],
                                    columns='indicator',
                                    aggfunc='mean',
                                    fill_value=0)
                       .reset_index()
                       )
        print("done.")
        pivoted_data_path = f'pivoted/'
        self.write_to_csv(df_to_write=pivoted,
                          path_to_write_to=pivoted_data_path,
                          file_name='result_pivoted.csv')

    def stack_data_for_dashboard(self, df_to_stack):
        """
        Method to arrange data in a dataframe in a way that allows for representation in the dashboard
        :param df_to_stack:
        :return:
        """
        if self.data_type == 'world':
            # Need to fillna to 0s
            df_to_stack = df_to_stack.fillna(0)
            stacked = (df_to_stack
                       .set_index(['Date', 'Country/Region', 'Continent'])
                       .stack()
                       .reset_index()
                       )
            stacked = stacked.rename(columns={"level_3": "indicator", 0: "value"})

            stacked['Days'] = (stacked
                               .groupby(['Country/Region', 'Continent'])['Date']
                               .transform(lambda x: (x - x.min()).dt.days)
                               )

        elif self.data_type == 'aus' and self.case_type == 'case':
            # Need to fillna to 0s
            df_to_stack.drop(columns={'Continent'}, inplace=True)
            df_to_stack = df_to_stack.fillna(0)
            stacked = (df_to_stack
                       .set_index(['Date', 'Province/State'])
                       .stack()
                       .reset_index()
                       )
            stacked = stacked.rename(columns={"level_2": "indicator", 0: "value"})

            stacked['Days'] = (stacked
                               .groupby(['Province/State'])['Date']
                               .transform(lambda x: (x - x.min()).dt.days)
                               )
        else:
            # Need to fillna to 0s
            df_to_stack.drop(columns={'Continent'}, inplace=True)
            df_to_stack = df_to_stack.fillna(0)
            stacked = (df_to_stack
                       .set_index(['Date', 'Province_State'])
                       .stack()
                       .reset_index()
                       )
            stacked = stacked.rename(columns={"level_2": "indicator", 0: "value"})

            stacked['Days'] = (stacked
                               .groupby(['Province_State'])['Date']
                               .transform(lambda x: (x - x.min()).dt.days)
                               )
        return stacked

    def assign_continent_to_df(self, df_add_continent: pd.DataFrame) -> pd.DataFrame:
        """
        Method to assign a continent to a country in the given dataframe. Some
        alterations have had to be made due to the absence of them in the ISO codes.
        This in NO way is a political statement from the author.
        :param df_add_continent:
        :return:
        """

        if self.data_type == 'world':
            df_add_continent.loc[df_add_continent['Country/Region'] == 'US', 'Country/Region'] = 'USA'
            df_add_continent.loc[df_add_continent['Country/Region'] == 'Burma', 'Country/Region'] = 'Myanmar'
            df_add_continent.loc[
                df_add_continent['Country/Region'] == 'Cote d\'Ivoire', 'Country/Region'] = 'Ivory Coast'
            df_add_continent.loc[df_add_continent['Country/Region'] == 'Korea, South', 'Country/Region'] = 'South Korea'
            df_add_continent.loc[df_add_continent['Country/Region'] == 'Taiwan*', 'Country/Region'] = 'Taiwan'

            df_add_continent['Continent'] = (df_add_continent
                                             .apply(lambda x: self.apply_continent_to_country(x['Country/Region']),
                                                    axis=1
                                                    )
                                             )
        elif self.data_type == 'aus':
            df_add_continent['Continent'] = 'Australasia'
        else:
            df_add_continent['Continent'] = 'North America'

        return df_add_continent

    @staticmethod
    def apply_continent_to_country(country):
        continents = {
            'NA': 'North America',
            'SA': 'South America',
            'AS': 'Asia',
            'OC': 'Australasia',
            'AF': 'Africa',
            'EU': 'Europe'
        }
        return continents[country_alpha2_to_continent_code(country_name_to_country_alpha2(country))]

    def write_to_csv(self, df_to_write: pd.DataFrame, path_to_write_to: str, file_name: str):

        if self.data_type == 'world':
            if self.case_type == 'case':
                write_path_cases = f"../data/output/world/{self.processing_date}/cases/{path_to_write_to}"
                if os.path.exists(write_path_cases):
                    print(f'Writing data out to path: {write_path_cases}')
                    df_to_write.to_csv(write_path_cases+f'/{file_name}')
                else:
                    print(f"Making directory to write out to...")
                    os.makedirs(write_path_cases)
                    print(f'Writing data out to path: {write_path_cases}')
                    df_to_write.to_csv(write_path_cases+f'/{file_name}')

            if self.case_type == 'death':
                write_path_deaths = f"../data/output/world/{self.processing_date}/deaths/{path_to_write_to}"
                if os.path.exists(write_path_deaths):
                    print(f'Writing data out to path: {write_path_deaths}')
                    df_to_write.to_csv(write_path_deaths+f'/{file_name}')
                else:
                    print(f"Making directory to write out to...")
                    os.makedirs(write_path_deaths)
                    print(f'Writing data out to path: {write_path_deaths}')
                    df_to_write.to_csv(write_path_deaths+f'/{file_name}')
        elif self.data_type == 'aus' and self.case_type == 'case':
            write_path_cases = f"../data/output/aus/{self.processing_date}/cases/{path_to_write_to}"
            if os.path.exists(write_path_cases):
                print(f'Writing data out to path: {write_path_cases}')
                df_to_write.to_csv(write_path_cases + f'/{file_name}')
            else:
                print(f"Making directory to write out to...")
                os.makedirs(write_path_cases)
                print(f'Writing data out to path: {write_path_cases}')
                df_to_write.to_csv(write_path_cases + f'/{file_name}')
        else:
            if self.case_type == 'case':
                write_path_cases = f"../data/output/usa/{self.processing_date}/cases/{path_to_write_to}"
                if os.path.exists(write_path_cases):
                    print(f'Writing data out to path: {write_path_cases}')
                    df_to_write.to_csv(write_path_cases + f'/{file_name}')
                else:
                    print(f"Making directory to write out to...")
                    os.makedirs(write_path_cases)
                    print(f'Writing data out to path: {write_path_cases}')
                    df_to_write.to_csv(write_path_cases + f'/{file_name}')

            if self.case_type == 'death':
                write_path_deaths = f"../data/output/usa/{self.processing_date}/deaths/{path_to_write_to}"
                if os.path.exists(write_path_deaths):
                    print(f'Writing data out to path: {write_path_deaths}')
                    df_to_write.to_csv(write_path_deaths + f'/{file_name}')
                else:
                    print(f"Making directory to write out to...")
                    os.makedirs(write_path_deaths)
                    print(f'Writing data out to path: {write_path_deaths}')
                    df_to_write.to_csv(write_path_deaths + f'/{file_name}')

        print("done.")
