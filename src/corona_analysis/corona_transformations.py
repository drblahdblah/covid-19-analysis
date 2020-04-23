"""
Class describing the transformations that are made to the Corona-virus data
that allows the Dash dashboard(s) to be made.
"""
import pandas as pd
import numpy as np


class CoronaTransformations:

    @staticmethod
    def create_cases_per_day(df_to_transform, groupby_list) -> pd.DataFrame:
        """
        Method to create cases/day from a dataframe.
        :return: A Pandas DataFrame containing the columns from the group by list
        as well as the `total_cases` column summed over any remaining columns.
        """
        return (df_to_transform
                .groupby(groupby_list, as_index=False)
                .agg({"total_cases": "sum"})
                )

    @staticmethod
    def create_cases_per_period(df_to_transform, groupby_list, case_column: str) -> pd.DataFrame:
        """
        Method to create a cases/time-period column in a Pandas DataFrame.
        :param groupby_list:
        :param df_to_transform:
        :param case_column: A string denoting which column to aggregate over the period `period`.
        :return: A Pandas DataFrame containing a column caled `new_cases` that contains an aggregate over
        period `period` of column `case_column`.
        """

        df_to_transform['new_cases'] = (df_to_transform
                                        .groupby(groupby_list)[case_column]
                                        .transform(lambda x: x.diff())
                                        )
        df_to_transform.new_cases = df_to_transform.new_cases.fillna(0)
        return df_to_transform

    @staticmethod
    def create_rolling_average(df_to_transform, groupby_list, period: int):
        df_to_transform['new_cases_per_week'] = (df_to_transform
                                                 .groupby(groupby_list)['new_cases']
                                                 .transform(lambda x: x.rolling(period).sum())
                                                 )
        df_to_transform.new_cases_per_week = df_to_transform.new_cases_per_week.fillna(0)
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
            df_to_transform['log_'+column] = np.where(df_to_transform[column] != 0,
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

        df_to_transform['slope_'+rise] = ((df_to_transform
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
        df_to_transform['growth_rate'] = ((df_to_transform
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
        df_to_transform['days_since_first_event'] = (df_to_transform
                                                     .groupby(groupby_list)['Date']
                                                     .transform(lambda x: (x - x.min()).dt.days)
                                                     )
        df_to_transform['avg_growth_rate'] = (df_to_transform
                                              .groupby(groupby_list)['growth_rate']
                                              .transform(lambda x: np.log(2) / (np.log(1) +
                                                                                x.rolling(period).mean()))
                                              )
        df_to_transform['doubling_time'] = (df_to_transform.avg_growth_rate *
                                            df_to_transform.days_since_first_event)

        return df_to_transform
