"""
Module to create datasets from the raw JHU data for interactive plotting
of the coronavirus-related data. These datasets will then flow into the
dashboard(s) create to illustrate the data in a better manner than simple
plots in my Jupyter notebooks.
"""
import pandas as pd


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
