import pandas as pd


def calculate_distance_matrix(df)->pd.DataFrame():
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """

      """
      This function calculates a distance matrix from a DataFrame containing route information.
      """
      # Create an empty DataFrame to store distances
      distance_matrix = pd.DataFrame(index=df["ID"].unique(), columns=df["ID"].unique())

      # Set all values to infinity initially
      distance_matrix.values[:] = float("inf")

      # Fill known distances
      for index, row in df.iterrows():
        start_id = row["ID"]
        end_id = row["NextID"]
        distance = row["Distance"]

        # Update distance in both directions (symmetric matrix)
        distance_matrix.loc[start_id, end_id] = distance
        distance_matrix.loc[end_id, start_id] = distance

      # Compute cumulative distances using Floyd-Warshall algorithm
      for k in distance_matrix.index:
        for i in distance_matrix.index:
            for j in distance_matrix.index:
                distance_matrix.loc[i, j] = min(
                distance_matrix.loc[i, j],
                distance_matrix.loc[i, k] + distance_matrix.loc[k, j]
            )

      # Set diagonal values to 0
      distance_matrix.values[::len(distance_matrix) + 1] = 0

    return distance_matrix
    



def unroll_distance_matrix(df)->pd.DataFrame():
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    
    """
    This function unrolls a distance matrix into a DataFrame with three columns.
    """
    # Extract IDs and distances from the matrix
    id_pairs = list(zip(distance_matrix.index, distance_matrix.columns))
    distances = distance_matrix.values.flatten()

    # Filter out redundant pairs
    filtered_pairs = [pair for pair in id_pairs if pair[0] != pair[1]]

    # Create a new DataFrame with three columns
    unrolled_df = pd.DataFrame(
        list(zip(*filtered_pairs, distances)),
        columns=["id_start", "id_end", "distance"],
    )

    return unrolled_df



def find_ids_within_ten_percentage_threshold(df, reference_id)->pd.DataFrame():
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.

    Args:
        df (pandas.DataFrame)
        reference_id (int)

    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                          of the reference ID's average distance.
    """
    """
    This function finds IDs within 10% of the reference ID's average distance.
    """
    # Calculate average distance for the reference ID
    reference_avg_distance = df[df["id_start"] == reference_id]["distance"].mean()

    # Calculate 10% threshold range
    lower_threshold = reference_avg_distance * 0.9
    upper_threshold = reference_avg_distance * 1.1

    # Filter IDs within the threshold range
    filtered_df = df[(df["id_start"] == reference_id) & (df["distance"].between(lower_threshold, upper_threshold))]

    # Extract and sort IDs
    id_list = filtered_df["id_end"].tolist()
    id_list.sort()

    return id_list



def calculate_toll_rate(df)->pd.DataFrame():
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    """
    This function calculates toll rates for different vehicle types.
    """
    # Define rate coefficients for each vehicle type
    rate_coefficients = {
        "moto": moto_rate,
        "car": car_rate,
        "rv": rv_rate,
        "bus": bus_rate,
        "truck": truck_rate,
    }

    # Calculate toll rates for each vehicle type
    for vehicle_type, rate_coefficient in rate_coefficients.items():
        df[vehicle_type] = df["distance"] * rate_coefficient

    return df



def calculate_time_based_toll_rates(df)->pd.DataFrame():
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    """
    This function calculates time-based toll rates for different time intervals within a day.
    """
    def get_time_range(start_time, end_time):
      """
      Helper function to create a time range for a specific interval.
      """
        start_datetime = datetime.strptime(f"{start_day} {start_time}", "%A %H:%M:%S")
        end_datetime = datetime.strptime(f"{end_day} {end_time}", "%A %H:%M:%S")
    
    return pd.to_timedelta([start_datetime, end_datetime])

      # Define time ranges for weekdays and weekends
        weekdays = [("Monday", "00:00:00", "10:00:00", 0.8),
                  ("Monday", "10:00:00", "18:00:00", 1.2),
                  ("Monday", "18:00:00", "23:59:59", 0.8)]
        weekends = [("Saturday", "00:00:00", "23:59:59", 0.7),
                  ("Sunday", "00:00:00", "23:59:59", 0.7)]

        # Create additional columns for time ranges
        df["start_day"] = df["id_start"].apply(lambda id_: "Monday")
        df["end_day"] = df["id_end"].apply(lambda id_: "Friday" if id_ <= 5 else "Sunday")

        # Initialize a dictionary to store time ranges for each (id_start, id_end) pair
        time_ranges = {}

        # Iterate through each unique (id_start, id_end) pair
        for start_id, end_id in df[["id_start", "id_end"]].drop_duplicates(ignore_index=True).values:
            start_day = df[df["id_start"] == start_id]["start_day"].iloc[0]
            end_day = df[df["id_end"] == end_id]["end_day"].iloc[0]

        # Determine if it's a weekday or weekend
        is_weekday = start_day not in ["Saturday", "Sunday"]

        # Get time ranges for the specific day type
        ranges = weekdays if is_weekday else weekends

        # Create a 24-hour time range covering all 7 days
        full_range = get_time_range("00:00:00", "23:59:59")
        time_ranges[(start_id, end_id)] = full_range

        # Add individual time ranges within the 24-hour period
        for start_time, end_time, factor in ranges:
            time_range = get_time_range(start_time, end_time)
            time_ranges[(start_id, end_id)] -= time_range
  
        # Apply discount factor to vehicle columns based on time range
        for vehicle_type in ["moto", "car", "rv", "bus", "truck"]:
            df.loc[(df["id_start"] == start_id) & (df["id_end"] == end_id), vehicle_type] *= factor

        # Create separate columns for start and end time of each time range
        df["start_time"] = df.apply(lambda row: time_ranges[(row["id_start"], row["id_end"])].iloc[0], axis=1)
        df["end_time"] = df.apply(lambda row: time_ranges[(row["id_start"], row["id_end"])].iloc[1], axis=1)

        # Convert timedelta objects to datetime.time() objects
        df["start_time"] = df["start_time"].apply(lambda td: datetime.time(td.seconds // 3600, (td.seconds // 60) % 60))
        df["end_time"] = df["end_time"].apply(lambda td: datetime.time(td.seconds // 3600

    return df
