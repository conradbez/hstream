import pandas as pd
from hstream import hs

hs.markdown("## HStream also supports displaying dataframes")

df = pd.DataFrame(data={'col1': [1, 2], 'col2': [4, 3]})

hs.write_dataframe(df, key='test')

hs.markdown("## HStream also supports displaying wide dataframes")
with hs.tag("figcaption"):
    hs.text("Using pico.css awesome styling")


df = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')
hs.write_dataframe(df, key='test2')