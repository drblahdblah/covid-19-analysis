import world_bank_data as wbd
import pandas as pd

# wbd.get_indicators()

if __name__ == '__main__':
    countries = wbd.get_countries()

    population = wbd.get_series('SP.POP.TOTL', id_or_value='id', simplify_index=True, mrv=1)

    df = countries[['region', 'name']].rename(columns={'name': 'country'}).loc[countries.region != 'Aggregates']
    df['population'] = population
    df.reset_index(inplace=True)
    print(df.loc[df.country == 'Andorra']['population'])
