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
    
    # Create a new DataFrame with values from car column
    car_matrix = df.pivot_table(index="id_1", columns="id_2", values="car", fill_value=0)
    
    # Set diagonal values to 0
    car_matrix.values[::len(car_matrix) + 1] = 0

    return car_matrix


def get_type_count(df)->dict:
    """
    Categorizes 'car' values into types and returns a dictionary of counts.

    Args:
        df (pandas.DataFrame)

    Returns:
        dict: A dictionary with car types as keys and their counts as values.
    """
    
    # Define car type categories
    car_type_categories = {
          "low": (lambda x: x <= 15),
          "medium": (lambda x: 15 < x <= 25),
          "high": (lambda x: x > 25),
    }

    # Add a new column 'car_type' based on car values
    df["car_type"] = df["car"].apply(
          lambda x: next(
              k for k, v in car_type_categories.items() if v(x)
        )
    )

    # Calculate the count of occurrences for each car type
    type_count = df["car_type"].value_counts().to_dict()

    # Sort the dictionary alphabetically based on keys
    type_count = dict(sorted(type_count.items()))

    return type_count


def get_bus_indexes(df)->list:
    """
    Returns the indexes where the 'bus' values are greater than twice the mean.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of indexes where 'bus' values exceed twice the mean.
    """
    # Calculate the mean of the bus column
    mean_bus = df["bus"].mean()

    # Filter the DataFrame to include only rows where bus is greater than twice the mean
    filtered_df = df[df["bus"] > 2 * mean_bus]

    # Get the indices of the filtered DataFrame
    bus_indexes = filtered_df.index.to_list()

    # Sort the bus indexes in ascending order
    bus_indexes.sort()

    return bus_indexes


def filter_routes(df)->list:
    """
    Filters and returns routes with average 'truck' values greater than 7.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of route names with average 'truck' values greater than 7.
    """
    # Create a new DataFrame grouped by route
    grouped_df = df.groupby("route").agg({"truck": "mean"})

    # Filter routes with average truck count greater than 7
    filtered_routes = grouped_df[grouped_df["truck"] > 7].index.to_list()

    # Sort the filtered routes in ascending order
    filtered_routes.sort()

    return filtered_routes


def multiply_matrix(matrix)->pd.DataFrame:
    """
    Multiplies matrix values with custom conditions.

    Args:
        matrix (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Modified matrix with values multiplied based on custom conditions.
    """
    def multiply_value(x):
        if x > 20:
            return x * 0.75
        else:
            return x * 1.25
  
    # Apply the function to each value in the DataFrame
    matrix = matrix.applymap(multiply_value)

    # Round all values to 1 decimal place
    matrix = matrix.round(1)
    
    return matrix


def time_check(df)->pd.Series:
    """
    Use shared dataset-2 to verify the completeness of the data by checking whether the timestamps for each unique (`id`, `id_2`) pair cover a full 24-hour and 7 days period

    Args:
        df (pandas.DataFrame)

    Returns:
        pd.Series: return a boolean series
    """
      """
      This function checks if timestamps for each (id, id_2) pair cover 24 hours and 7 days.
      """
    def check_timestamps(row):
    """
    Helper function to check timestamps for a single row.
    """
        start_day, start_time, end_day, end_time = row[["startDay", "startTime", "endDay", "endTime"]]

        # Convert timestamps to datetime objects
        start_dt = pd.to_datetime(f"{start_day} {start_time}")
        end_dt = pd.to_datetime(f"{end_day} {end_time}")

        # Calculate total duration
        duration = (end_dt - start_dt)

        # Check if duration covers 24 hours and 7 days
        is_valid = (
            duration.total_seconds() >= 24 * 3600
            and duration.days == 7
        )
        return not is_valid

    # Create a boolean series with multi-index checking if timestamps are valid
    is_invalid = df.apply(check_timestamps, axis=1)
    is_invalid.index = pd.MultiIndex.from_tuples(zip(df["id"], df["id_2"]))

    return is_invalid

    return pd.Series()
