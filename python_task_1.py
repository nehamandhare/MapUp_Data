import pandas as pd

def generate_car_matrix(df)->pd.DataFrame:
    """
    Creates a DataFrame  for id combinations.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Matrix generated with 'car' values, 
                          where 'id_1' and 'id_2' are used as indices and columns respectively.
    """
    df = pd.read_csv('dataset-1.csv')
    matrix = df.pivot_table(index="id_1", values="car", columns="id_2", aggfunc=pd.Series.nunique)
    
    return df
