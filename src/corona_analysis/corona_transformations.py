"""
Class describing the transformations that are made to the Corona-virus data
that allows the Dash dashboard(s) to be made.
"""
import pandas as pd
import numpy as np
import world_bank_data as wbd

pd.set_option("display.max_columns", 500)
pd.set_option("display.max_rows", 1000)
pd.set_option("display.width", 1000)


class CoronaTransformations:

    @staticmethod
    def get_wbd_population() -> pd.DataFrame:
        """
        Method to obtain
        :return:
        """
        countries = wbd.get_countries()
        population = wbd.get_series('SP.POP.TOTL', id_or_value='id', simplify_index=True, mrv=1)
        pop_df = \
            countries[['region', 'name']].rename(columns={'name': 'country'}).loc[countries.region != 'Aggregates']
        pop_df['population'] = population
        pop_df.reset_index(inplace=True)
        return pop_df

    @staticmethod
    def get_ctry_pop(pop_df: pd.DataFrame, cntry: str) -> float:
        """
        Method that returns the population of a country.
        :return: the population of the country.
        """
        if cntry == 'Burma':
            population = pop_df.loc[pop_df.country.str.contains('Myanmar')].population.item()
        elif cntry == 'China':
            population = pop_df.loc[pop_df.country == 'China'].population.item()
        elif cntry == 'Czechia':
            population = pop_df.loc[pop_df.country == 'Czech Republic'].population.item()
        elif cntry == 'Dominican Republic':
            population = pop_df.loc[pop_df.country == 'Dominican Republic'].population.item()
        elif cntry == 'Dominica':
            population = pop_df.loc[pop_df.country == 'Dominica'].population.item()
        elif cntry == 'Guinea':
            population = pop_df.loc[pop_df.country == 'Guinea'].population.item()
        elif cntry == 'Guinea-Bissau':
            population = pop_df.loc[pop_df.country == 'Guinea-Bissau'].population.item()
        elif cntry == 'Equatorial Guinea':
            population = pop_df.loc[pop_df.country == 'Equatorial Guinea'].population.item()
        elif cntry == 'Papua New Guinea':
            population = pop_df.loc[pop_df.country == 'Papua New Guinea'].population.item()
        elif cntry == 'Korea, South':
            population = pop_df.loc[pop_df.country == 'Korea, Rep.'].population.item()
        elif cntry == 'Kyrgyzstan':
            population = pop_df.loc[pop_df.country == 'Kyrgyz Republic'].population.item()
        elif cntry == 'Laos':
            population = pop_df.loc[pop_df.country == 'Lao PDR'].population.item()
        elif cntry == 'Niger':
            population = pop_df.loc[pop_df.country == 'Niger'].population.item()
        elif cntry == 'Nigeria':
            population = pop_df.loc[pop_df.country == 'Nigeria'].population.item()
        elif cntry == 'Saint Kitts and Nevis':
            population = pop_df.loc[pop_df.country == 'St. Kitts and Nevis'].population.item()
        elif cntry == 'Saint Lucia':
            population = pop_df.loc[pop_df.country == 'St. Lucia'].population.item()
        elif cntry == 'Saint Vincent and the Grenadines':
            population = pop_df.loc[pop_df.country == 'St. Vincent and the Grenadines'].population.item()
        elif cntry == 'Slovakia':
            population = pop_df.loc[pop_df.country == 'Slovak Republic'].population.item()
        elif cntry == 'Sudan':
            population = pop_df.loc[pop_df.country == 'Sudan'].population.item()
        elif cntry == 'South Sudan':
            population = pop_df.loc[pop_df.country == 'South Sudan'].population.item()
        elif cntry == 'US':
            population = pop_df.loc[pop_df.country == 'United States'].population.item()
        else:
            population = pop_df.loc[pop_df.country.str.contains(cntry)].population.item()

        return population / 1000000.0

    def create_cases_per_day(self, df_to_transform, groupby_list) -> pd.DataFrame:
        """
        Method to create cases/day from a dataframe.
        :return: A Pandas DataFrame containing the columns from the group by list
        as well as the `total_cases` column summed over any remaining columns.
        """

        total_cases_df = (df_to_transform
                          .groupby(groupby_list, as_index=False)
                          .agg({"total_cases": "sum"})
                          )
        pop_df = self.get_wbd_population()

        total_cases_df['css_per_prsn'] = (total_cases_df
                                          .apply(lambda x: x.total_cases / self.get_ctry_pop(pop_df=pop_df,
                                                                                             cntry=x['Country/Region']),
                                                 axis=1)
                                          )
        total_cases_df = total_cases_df.rename(columns={"total_cases": "Total cases",
                                                        "css_per_prsn": "Total cases per million"})

        return total_cases_df

    def create_cases_per_period(self, df_to_transform, groupby_list, case_column: str) -> pd.DataFrame:
        """
        Method to create a cases/time-period column in a Pandas DataFrame.
        :param groupby_list:
        :param df_to_transform:
        :param case_column: A string denoting which column to aggregate over the period `period`.
        :return: A Pandas DataFrame containing a column caled `new_cases` that contains an aggregate over
        period `period` of column `case_column`.
        """

        df_to_transform['New cases'] = (df_to_transform
                                        .groupby(groupby_list)[case_column]
                                        .transform(lambda x: x.diff())
                                        )

        df_to_transform['New cases'] = df_to_transform['New cases'].fillna(0)
        pop_df = self.get_wbd_population()

        df_to_transform['new_css_per_prsn'] = (df_to_transform
                                               .apply(lambda x: x['New cases'] /
                                                                self.get_ctry_pop(pop_df=pop_df,
                                                                                  cntry=x['Country/Region']),
                                                      axis=1)
                                               )
        df_to_transform = df_to_transform.rename(columns={"new_css_per_prsn": "New cases per million"})
        return df_to_transform

    def create_rolling_average(self, df_to_transform, groupby_list, period: int):
        df_to_transform['New cases per week'] = (df_to_transform
                                                 .groupby(groupby_list)['New cases']
                                                 .transform(lambda x: x.rolling(period).sum())
                                                 )
        df_to_transform['New cases per week'] = df_to_transform['New cases per week'].fillna(0)

        pop_df = self.get_wbd_population()
        df_to_transform['new_css_per_wk_prsn'] = (df_to_transform
                                                  .apply(lambda x: x['New cases per week'] /
                                                                   self.get_ctry_pop(pop_df=pop_df,
                                                                                     cntry=x['Country/Region']),
                                                         axis=1)
                                                  )
        df_to_transform = df_to_transform.rename(columns={"new_css_per_wk_prsn": "New cases per week per million"})

        return df_to_transform

    @staticmethod
    def calculate_power_law_columns(df_to_transform, cols_to_logify: list) -> pd.DataFrame:
        """
        Method to convert columns to log-valued columns using Numpy's np.log10
        :param df_to_transform:
        :param cols_to_logify: A list of columns to calculate the log values of.
        :return: A Pandas DataFrame containing columns `cols_to_logify` values.
        """
        if not all(cols in df_to_transform.columns for cols in cols_to_logify):
            print(f"Columns chosen to `logify` are not present in `df_to_transform`.\n"
                  f"Please check which columns to take the log-value of.")
            exit(1)

        for column in cols_to_logify:
            df_to_transform['log10(' + column + ')'] = np.where(df_to_transform[column] != 0,
                                                                np.log10(df_to_transform[column]),
                                                                0)
        return df_to_transform

    @staticmethod
    def calculate_power_law_slope(df_to_transform, period: int,
                                  groupby_list: list, rise: str, run: str) -> pd.DataFrame:
        """
        Method which calculates the slope of two columns in a Pandas DataFrame
        :param df_to_transform:
        :param period: The period over which to average the slope.
        :param groupby_list: The columns in the DataFrame over which to group to take the slope.
        :param rise: The column which is the rise in the rise/run == slope.
        :param run: The column which is the run in the rise/run == slope.
        :return: A Pandas DataFrame containing the slope of two columns
        """

        if not all(cols in df_to_transform.columns for cols in [rise, run]):
            print(f"Columns chosen to `logify` are not present in `df_to_transform`.\n"
                  f"Please check which columns to take the log-value of.")
            exit(1)

        df_to_transform['slope of ' + rise] = ((df_to_transform
                                                .groupby(groupby_list)[rise].diff(periods=period)) /
                                               (df_to_transform
                                                .groupby(groupby_list)[run].diff(periods=period))
                                               )
        return df_to_transform

    def calculate_power_law_acceleration(self,
                                         df_to_transform: pd.DataFrame,
                                         period: int,
                                         groupby_list: list,
                                         rise: str,
                                         run: str) -> pd.DataFrame:
        """
        Method to calculate the `slope of the slope` of a line, which can be thought of as being analogous to
        the acceleration of the rate-of-change of the line in a power-law (in this sense is how I am implementing
        it).
        :param df_to_transform:
        :param period: The period over which to average the speed.
        :param groupby_list: The columns in the DataFrame over which to group to take the speed.
        :param rise: The column which is the rise in the rise/run == slope.
        :param run: The column which is the run in the rise/run == slope.
        :return: A Pandas DataFrame containing the slope of two columns
        """
        return self.calculate_power_law_slope(df_to_transform=df_to_transform,
                                              period=period, groupby_list=groupby_list, rise=rise, run=run)

    @staticmethod
    def calculate_growth_rate(df_to_transform: pd.DataFrame, period: int, groupby_list: list, new_cases: str,
                              total_cases: str) -> pd.DataFrame:
        """
        Method by which to calculate the growth rate of cases. This is essentially the percentage of `total_cases`
        that the `new_cases` represents.
        :param df_to_transform:
        :param period: The period over which to average the growth rate.
        :param groupby_list: The columns in the DataFrame over which to group to take the slope.
        :param new_cases: The column representing the new_cases for the time period.
        :param total_cases: The column representing the total_cases for the entire time period.
        :return: A Pandas DataFrame containing a column for the growth rate.
        """
        df_to_transform['Growth Rate'] = ((df_to_transform
                                           .groupby(groupby_list)[new_cases]
                                           .transform(lambda x: x.rolling(period).mean())
                                           ) /
                                          df_to_transform
                                          .groupby(['Country/Region'])[total_cases]
                                          .transform(lambda x: x.rolling(period).mean())
                                          ) * 100.0
        return df_to_transform

    @staticmethod
    def calculate_doubling_time(df_to_transform: pd.DataFrame, period: int, groupby_list: list) -> pd.DataFrame:
        """

        :param df_to_transform:
        :param period:
        :param groupby_list:
        :return:
        """
        df_to_transform['Days since first case'] = (df_to_transform
                                                    .groupby(groupby_list)['Date']
                                                    .transform(lambda x: (x - x.min()).dt.days)
                                                    )
        df_to_transform['Average Growth Rate'] = (df_to_transform
                                                  .groupby(groupby_list)['Growth Rate']
                                                  .transform(lambda x: np.log(2) / (np.log(1) +
                                                                                    x.rolling(period).mean())
                                                             )
                                                  )

        df_to_transform['Doubling time'] = (df_to_transform['Average Growth Rate'] *
                                            df_to_transform['Days since first case'])

        return df_to_transform
