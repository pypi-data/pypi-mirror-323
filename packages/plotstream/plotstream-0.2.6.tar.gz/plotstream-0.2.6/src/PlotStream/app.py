import os

import dill
import numpy as np
import pandas as pd

import streamlit as st
import plotly.graph_objects as go

from data_proc import process_data
from funcs_def import (
    FunctionData,
    pkl_file_path,
)  # Assuming this file contains your function definitions
from typing import Dict, List, Any, cast

# Load the functions from the 'functions.pkl' file into the FUNCTIONS variable
try:
    with open(pkl_file_path, "rb") as f:
        FUNCTIONS = dill.load(f)
        # Print the loaded functions pretty printing
        print("Loaded functions:")
        print(FUNCTIONS)
        # Remove the file after loading the functions
        # os.remove(pkl_file_path)
except FileNotFoundError:
    st.error("No functions found. Please register functions!")
    st.stop()


# Helper function to group functions by graph names
def group_functions_by_graph(
    functions: Dict[str, FunctionData]
) -> Dict[str, List[FunctionData]]:
    print("FUNCTIONS:", functions)
    grouped_graphs: Dict[str, List[FunctionData]] = {}
    for function_name, function_data in functions.items():
        try:
            graph_name = cast(str, function_data["graph"])
            if graph_name not in grouped_graphs:
                grouped_graphs[graph_name] = []
            grouped_graphs[graph_name].append(function_data)
        except KeyError:
            st.error(f"Function '{function_name}' is missing the 'graph' key.")
            continue
    return grouped_graphs


def collect_user_inputs(
    function_data: FunctionData, series_index: int
) -> tuple[dict, dict]:
    """Collects user inputs for a specific function in the sidebar."""
    series_name = function_data.get("name", function_data["function"].__name__)
    st.sidebar.markdown(f"### {series_name}:")

    inputs: Dict[str, Any] = cast(Dict[str, Any], function_data["inputs"])
    chart_type: str = cast(str, function_data.get("type", "Line"))
    color: str = cast(str, function_data.get("color", "#000000"))

    # Add checkboxes for secondary Y-axis and secondary graph
    secondary_y_axis = st.sidebar.checkbox(
        f"Use Secondary Y-Axis (Series {series_index + 1})",
        value=function_data.get("secondary_y_axis", False),
        key=f"secondary_y_axis_series_{series_index}",
    )
    secondary_graph = st.sidebar.checkbox(
        f"Use Secondary Graph (Series {series_index + 1})",
        value=function_data.get("secondary_graph", False),
        key=f"secondary_graph_series_{series_index}",
    )

    # Collect user inputs for parameters
    user_inputs = {}
    for param_name, default_value in inputs.items():
        # Create a two-column layout for each parameter
        cols = st.sidebar.columns([1, 2])  # Adjust ratios for label vs input size
        with cols[0]:
            st.write(f"{param_name} ({type(default_value).__name__})")  # Parameter name
        with cols[1]:
            if isinstance(default_value, int):
                user_inputs[param_name] = st.number_input(
                    "int_input",  # Empty label since the name is on the left
                    value=default_value,
                    step=1,
                    key=f"{param_name}_series_{series_index}",
                    label_visibility="visible",  # Hide the label
                )
            elif isinstance(default_value, float):
                user_inputs[param_name] = st.number_input(
                    "float_input",
                    value=default_value,
                    step=0.1,
                    key=f"{param_name}_series_{series_index}",
                    label_visibility="visible",
                )
            elif isinstance(default_value, str):
                user_inputs[param_name] = st.text_input(
                    "string_input",
                    value=default_value,
                    key=f"{param_name}_series_{series_index}",
                    label_visibility="visible",
                )

    return user_inputs, {
        "chart_type": chart_type,
        "secondary_y_axis": secondary_y_axis,
        "secondary_graph": secondary_graph,
        "color": color,
    }


# Helper function to create and configure a Plotly figure
def create_figure(series_list: List[Dict[str, Any]], yaxis: str = "y") -> go.Figure:
    """Creates and configures a Plotly figure."""
    fig = go.Figure()
    add_traces_to_figure(fig, series_list, yaxis)
    return fig


# Helper function to add traces to a Plotly figure (with type hints)
def add_traces_to_figure(
    fig: go.Figure, series_list: List[Dict[str, Any]], yaxis: str = "y"
) -> None:
    """Adds traces to a Plotly figure."""
    for series in series_list:
        data = series["data"]
        chart_type = series["chart_type"]
        color = series["color"]
        name = series.get("name", f"{yaxis} Axis")

        if chart_type == "Line":
            fig.add_trace(
                go.Scatter(
                    x=data["x"],
                    y=data["y"],
                    mode="lines",
                    line=dict(color=color),
                    name=name,
                    yaxis=yaxis,
                )
            )
        elif chart_type == "Scatter":
            fig.add_trace(
                go.Scatter(
                    x=data["x"],
                    y=data["y"],
                    mode="markers",
                    marker=dict(color=color),
                    name=name,
                    yaxis=yaxis,
                )
            )


# Main function to render the visualization
def render_visualization(
    selected_graph_name: str, selected_functions: List[FunctionData]
) -> None:
    """Renders the visualization for the selected graph."""
    st.title(f"{selected_graph_name}")

    all_series_primary = []
    all_series_secondary_y = []
    all_series_secondary_graph = []

    # Collect user inputs and generate data
    for i, function_data in enumerate(selected_functions):
        # if the data is a series or an array of data, add proper x-axis values (incremental)
        user_inputs, config = collect_user_inputs(function_data, i)
        data = function_data["function"](**user_inputs)  # type: ignore

        data = process_data(
            data,
            function_data["x_col"],
            function_data["y_col"],
            reference_name=function_data["function"].__name__,
            row_major=function_data["row_major"],
        )

        series_data = {
            "data": data,
            **config,
            "name": function_data.get("name", function_data["function"].__name__),
        }

        if config["secondary_graph"]:
            all_series_secondary_graph.append(series_data)
        elif config["secondary_y_axis"]:
            all_series_secondary_y.append(series_data)
        else:
            all_series_primary.append(series_data)

    if all_series_primary or all_series_secondary_y:
        fig = create_figure(all_series_primary, yaxis="y")
        add_traces_to_figure(fig, all_series_secondary_y, yaxis="y2")

        # fig.update_layout(
        #     yaxis2=dict(title="Secondary Y Axis", overlaying="y", side="right"),
        #     title="Primary and Secondary Y-Axis",
        #     xaxis_title="X Axis",
        #     yaxis_title="Primary Y Axis",
        # )

        st.plotly_chart(fig, use_container_width=True)

    if all_series_secondary_graph:
        st.markdown("### Secondary Graph")
        for series in all_series_secondary_graph:
            fig = create_figure([series])  # Pass as a single-item list
            st.plotly_chart(fig, use_container_width=True)


# Main Streamlit App Workflow
def main():
    graphs = group_functions_by_graph(FUNCTIONS)

    st.sidebar.title("Graph Configurator")
    selected_graph_name = st.sidebar.selectbox("Select a Graph", list(graphs.keys()))

    selected_functions = graphs[selected_graph_name]

    render_visualization(selected_graph_name, selected_functions)


if __name__ == "__main__":
    main()
