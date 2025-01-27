# PlotStream

PlotStream allows you to register your Python functions with a simple decorator, `@plotstream_function`, and automatically create dynamic, interactive dashboards to visualize their outputs. It supports a variety of data formats like DataFrames, arrays, and lists, and generates customizable charts with minimal effort.

---

## Features

- **Simple Function Registration**: Use `@plotstream_function` to register functions effortlessly.
- **Dynamic Dashboards**: Automatically generate Streamlit dashboards with interactive controls for function inputs.
- **Customizable Charts**: Define chart types, axis mappings, colors, and more.
- **Multi-format Support**: Works seamlessly with Pandas DataFrames, Series, NumPy arrays, and Python lists.
- **Minimal Code Overhead**: Just decorate your functions and call `run_plotstream_app()`.

---

## Usage

1. Register your functions with the `@plotstream_function` decorator. Customize the parameters to control how the function is visualized.

    None of the parameters are required, but you can specify the following:

```python
from plotstream import plotstream_function, run_plotstream_app

import pandas as pd
import numpy as np

@plotstream_function(
    name="Sine Wave",
    graph="Trigonometry Graph",
    chart_type="Line",
    color="#FF5733",
    x_col="x",
    y_col="y",
)
def sine_wave(a: float = 1.0, b: float = 2.0, n: int = 100) -> pd.DataFrame:
    """
    Generate a sine wave with given parameters.

    Args:
        a (float): Amplitude of the sine wave.
        b (float): Frequency of the sine wave.
        n (int): Number of points.

    Returns:
        pd.DataFrame: A DataFrame containing the sine wave (x, y).
    """
    x = np.linspace(0, 10, n)
    y = a * np.sin(b * x)
    return pd.DataFrame({"x": x, "y": y})
```

2. Run the PlotStream app to generate the dashboard.
```python
run_plotstream_app()
```

The Streamlit dashboard will open in your browser, allowing you to:

- Select from registered functions.
- Adjust inputs using dynamically generated controls.
- View and interact with the resulting visualizations.

---

## How It Works

1. **Function Registration**:
    
    Use @plotstream_function to register your function along with metadata like chart type, axis mappings, and colors.
    Metadata is stored in a global dictionary (FUNCTIONS) and serialized for reuse. 


2. **Data Processing**:
    
    The process_data utility handles different data formats (DataFrames, arrays, lists) and extracts x/y data for visualization.


3. **Streamlit App**:

    The run_plotstream_app() function launches the Streamlit app, dynamically loading registered functions and their associated metadata.

---

## Key Decorator Parameters

When using `@plotstream_function`, you can customize the visualization with the following parameters:

| Parameter          | Type             | Default           | Description                                                                 |
|--------------------|------------------|-------------------|-----------------------------------------------------------------------------|
| `name`             | `str`           | `None`            | The name of the function (appears in the dashboard).                        |
| `graph`            | `str`           | `"Default Graph"` | The graph this function belongs to (groups functions visually).             |
| `chart_type`       | `str`           | `"Line"`          | The chart type (`"Line"`, `"Scatter"`, etc.).                               |
| `secondary_y_axis` | `bool`          | `False`           | Whether to use a secondary Y-axis.                                          |
| `secondary_graph`  | `bool`          | `False`           | Whether to plot this series on a secondary graph.                           |
| `color`            | `str` (hex)     | `Auto-assigned`   | The color of the series (default is auto-assigned).                         |
| `x_col`            | `str|int|None`  | `None`            | X-axis column name (for DataFrames) or index (for arrays).                  |
| `y_col`            | `str|int|None`  | `None`            | Y-axis column name (for DataFrames) or index (for arrays).                  |
| `row_major`        | `bool`          | `True`            | Whether arrays are row-major (`True`) or column-major (`False`).            |

---

## Future Improvements

- Add support for more chart types.
- Add support for more data formats (including multi graphs for multi columns DataFrames).
- Add support for more controls (e.g., sliders, dropdowns, etc.).
- Provide enhanced error handling and logging.
- Ignore unsupported input data types.
- Function naming in legend.

---

## License

This project is licensed under the MIT License.

