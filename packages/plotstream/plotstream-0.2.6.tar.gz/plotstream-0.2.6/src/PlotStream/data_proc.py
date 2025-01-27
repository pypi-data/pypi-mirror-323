from typing import Any, Union, List, Optional

import numpy as np
import pandas as pd


def validate_col_in_df(df: pd.DataFrame, col: str) -> bool:
    """
    Validate if a column exists in a DataFrame.
    :param df: The DataFrame.
    :param col: The column name.
    :return: True if the column exists, False otherwise.
    """
    return col in df.columns if col else False


def process_data_dataframe(
    df: pd.DataFrame,
    x_axis: Optional[Union[str, int]] = None,
    y_axis: Optional[Union[str, int]] = None,
    reference_name: Optional[str] = None,
) -> dict:
    """
    Handles DataFrame data extraction.

    Cases:
    1. One column: x_axis and y_axis are ignored.
    2. Two columns, one date-like: x_axis and y_axis are ignored.
    3. Two columns, no date-like: y_axis is required. x_axis defaults to index.
    4. More than two columns: y_axis is required. x_axis defaults to index if not provided.

    If x_axis or y_axis are provided (and not empty strings), they must be valid column names.

    :param df:
    :param x_axis:
    :param y_axis:
    :param reference_name:
    :return:
    """

    name_intro = f"{reference_name + ': ' if reference_name else ''}"

    # Validate the input and extract the x and y columns
    if (not isinstance(x_axis, str)) or (len(x_axis) == 0):
        x_axis = None
    if (not isinstance(y_axis, str)) or (len(y_axis) == 0):
        y_axis = None

    date_cols = [
        "date",
        "Date",
        "Datetime",
        "datetime",
        "Date/Time",
        "date_time",
    ]

    date_col = next((col for col in df.columns if col in date_cols), None)

    if len(df.columns) == 1:
        # Case 1: One column: x_axis and y_axis values are non-relevant
        return {"x": df.index, "y": df.iloc[:, 0]}

    elif len(df.columns) == 2:
        if date_col:
            # Case 2: Two columns. One is date-like: x_axis and y_axis values are non-relevant
            y_col = next(col for col in df.columns if col != date_col)
            return {"x": df[date_col], "y": df[y_col]}

    # Combined handling for cases 3, 4, and 5:
    if not validate_col_in_df(df, y_axis):
        raise ValueError(f"{name_intro}y_axis column '{y_axis}' not found or None.")
    y = df[y_axis]

    if x_axis is None:
        if date_col:
            x = df[date_col]
        else:
            x = df.index
    elif validate_col_in_df(df, x_axis):
        x = df[x_axis]
    else:
        raise ValueError(f"{name_intro}x_axis column '{x_axis}' not found.")

    return {"x": x, "y": y}


def process_data_array(
    array: Union[np.ndarray, List[Any]],
    x_axis: Optional[Union[str, int]] = None,
    y_axis: Optional[Union[str, int]] = None,
    reference_name: Optional[str] = None,
    row_major: bool = True,
) -> dict:
    """
    Processes the data for the selected array or list.


    :param array:
    :param x_axis:
    :param y_axis:
    :param reference_name:
    :param row_major:
    :return:
    """

    name_intro = f"{reference_name + ': ' if reference_name else ''}"

    if isinstance(array, list):
        try:
            array = np.array(array)
        except ValueError as e:
            raise ValueError(f"{name_intro}Array conversion failed: {e}")

    try:
        # Handle structured arrays
        if array.dtype.names:  # structured array
            if row_major is False:
                raise ValueError(
                    "row_major=False is not supported for structured arrays."
                )
            df = pd.DataFrame(array)

        else:  # Regular array
            columns = (
                range(array.shape[1]) if array.ndim > 1 else [0]
            )  # handle 1D array case
            # In case of 1 D array, convert it to 2D array
            if array.ndim == 1:
                array = array.reshape(-1, 1)
            df = pd.DataFrame(
                array if row_major else array.T,
                columns=[str(c) for c in columns],  # convert column indices to strings
            )

    except ValueError as e:
        raise ValueError(f"{name_intro}Array conversion to df failed: {e}.")

    # Validate and convert x_axis and y_axis to strings if necessary
    if x_axis is not None:
        x_axis = str(x_axis)  # Convert to string for consistent DataFrame access
    if y_axis is not None:
        y_axis = str(y_axis)  # Convert to string for consistent DataFrame access

    return process_data_dataframe(df, x_axis, y_axis, reference_name)


def process_data(
    series: Union[pd.Series, pd.DataFrame, np.ndarray, List[Any]],
    x_axis: Optional[Union[str, int]] = None,
    y_axis: Optional[Union[str, int]] = None,
    reference_name: Optional[str] = None,
    row_major: bool = True,
) -> dict:
    """
    Processes the data for the selected series.

    The logic is as follows:
    1. If series is of type pd.Series:
       The x_axis is the index and the y_axis is the values.
    2. If series is of type pd.DataFrame:
       The x_axis and y_axis are the columns.
       If x_axis is not in the columns or empty, one of the following is used ['date', 'Date', 'Datetime', 'datetime', 'Date/Time', 'date_time'], if non exists - the index is used.
       If y_axis is not in the columns or empty, a ValueError is raised.
       If the pd.DataFrame has only one column, the y_axis is the column and the x_axis is the index.
    3. If series is of type 2D List or 2D np.ndarray:
         The x_axis and y_axis are the indices of the 2D array. One of them must be provided.
         If non is given:
         The x_axis is 0.
         The y_axis 1d.
    4. If series is of type np.ndarray or List:
       The x-axis is the range of the length of the array and the y-axis is the array.

    :param series: type of data: pd.Series, pd.DataFrame, np.ndarray, List.
    :param x_axis:
    :param y_axis:
    :param reference_name: The name of the series.
    :param row_major: Whether to treat the array as row-major (default) or column-major. If not an array, this parameter is ignored.
    :return: {'x': Union[pd.Series, np.ndarray, List[Any]], 'y': Union[pd.Series, np.ndarray, List[Any]]}
    """

    name_intro = f"{reference_name + ': ' if reference_name else ''}"

    if isinstance(series, pd.Series):
        # Handle the case where the input is a pandas Series
        return {"x": series.index, "y": series.values}

    elif isinstance(series, pd.DataFrame):
        return process_data_dataframe(series, x_axis, y_axis, reference_name)

    elif isinstance(series, list) or isinstance(series, np.ndarray):
        # Handle the case where the input is a list or a NumPy array
        return process_data_array(series, x_axis, y_axis, reference_name, row_major)

    else:
        # Unsupported type
        raise TypeError(f"{name_intro}Unsupported series type: {type(series)}")
