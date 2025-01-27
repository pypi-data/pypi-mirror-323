import os

import dill

from typing import Dict, Union, Callable
from inspect import signature, Parameter

FunctionData = Dict[str, Union[str, Callable, Dict[str, Union[str, float, int]], bool]]

pkl_filename = "../functions.pkl"

current_directory = os.path.dirname(os.path.abspath(__file__))

pkl_file_path = os.path.join(current_directory, pkl_filename)

# FUNCTIONS dictionary to store function metadata
FUNCTIONS = {}

# Default values for name and color
DEFAULT_COLORS = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"]
color_index = 0  # To track the current color
series_counter = 1  # To track the current series number


def plotstream_function(
    name: str = None,
    graph: str = "Default Graph",
    chart_type: str = "Line",
    secondary_y_axis: bool = False,
    secondary_graph: bool = False,
    color: str = None,
    x_col: Union[str, None, int] = None,
    y_col: Union[str, None, int] = None,
    row_major: bool = True,
):
    """
    A decorator to register a function in the FUNCTIONS dictionary.

    Args:
        name (str): The name of the function.
        graph (str): The graph this function belongs to.
        chart_type (str): Default chart type ('Line' or 'Scatter').
        secondary_y_axis (bool): Whether this series uses a secondary Y-axis.
        secondary_graph (bool): Whether this series is in a separate graph.
        color (str): Default color of the series (hex code).
        x_col (str|None|int): Name of the column for the x-axis or the index of it in a 2D array.
        y_col (str|None|int): Name of the column for the y-axis or the index of it in a 2D array.
        row_major (bool): Whether to treat the array as row-major (default) or column-major. If not an array, this parameter is ignored.
    """

    def decorator(func: Callable) -> Callable:
        global color_index, series_counter

        # Automatically assign a name if not provided
        auto_name = name if name else func.__name__
        series_counter += 1  # Increment the series counter

        # Automatically assign a color if not provided
        auto_color = color if color else DEFAULT_COLORS[color_index]
        color_index = (color_index + 1) % len(DEFAULT_COLORS)  # Cycle through colors

        # Use the function signature to extract parameter names and default values
        sig = signature(func)
        inputs = {}
        for param_name, param in sig.parameters.items():
            if param.default != Parameter.empty:
                # If the parameter has a default value, use it
                inputs[param_name] = param.default
            elif param.annotation is int:
                # Assign a sensible default for `int` parameters
                inputs[param_name] = 1.0
            elif param.annotation is float:
                # Assign a sensible default for `float` parameters
                inputs[param_name] = 1.0
            elif param.annotation is str:
                # Assign a sensible default for `str` parameters
                inputs[param_name] = ""
            else:
                # If no type or default is provided, assign None
                inputs[param_name] = None

        # Add the function and its metadata to the FUNCTIONS dictionary
        FUNCTIONS[auto_name] = {
            "function": func,
            "inputs": inputs,
            "graph": graph,
            "type": chart_type,
            "secondary_y_axis": secondary_y_axis,
            "secondary_graph": secondary_graph,
            "color": auto_color,
            "x_col": x_col,
            "y_col": y_col,
            "row_major": row_major,
        }
        print(f"Registered function: {auto_name}")

        # Update the functions.json file
        # Pickle the FUNCTIONS dictionary to a file
        with open(pkl_file_path, "wb") as f:
            dill.dump(FUNCTIONS, f)

        return func

    return decorator


# # Define and register "Sine Wave 1"
# @register_function(
#     name="Sine Wave 1",
#     graph="Graph #1",
#     chart_type="Line",
#     color="#0000FF",  # Blue
# )
# def sine_wave_1(a: float = 1.0, b: float = 1.0, n: int = 50):
#     return pd.DataFrame(
#         {
#             "x": np.linspace(0, 10, n),
#             "y": a * np.sin(b * np.linspace(0, 10, n)),
#         }
#     )
#
#
# # Define and register "Sine Wave 2"
# @register_function(
#     name="Sine Wave 2",
#     graph="Graph #1",
#     chart_type="Scatter",
#     secondary_y_axis=True,
#     secondary_graph=False,
#     color="#FF0000",  # Red
# )
# def sine_wave_2(a: float = 2.0, b: float = 0.5, n: int = 100):
#     return pd.DataFrame(
#         {
#             "x": np.linspace(0, 10, n),
#             "y": a * np.sin(b * np.linspace(0, 10, n)),
#         }
#     )
#
#
# # Define and register "Quadratic Series"
# @register_function(
#     name="Quadratic Series",
#     graph="Graph #2",
#     chart_type="Line",
#     secondary_y_axis=False,
#     secondary_graph=True,
#     color="#00FF00",  # Green
# )
# def quadratic_series(start: int = 0, end: int = 100, step: int = 10):
#     x = np.arange(start, end, step)
#     return pd.DataFrame(
#         {
#             "x": x,
#             "y": x**2,
#         }
#     )
