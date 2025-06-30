"""
CMF Equation of State (EOS) and QLIMR Observable Plotting Utilities

This script provides a collection of plotting functions for visualizing
thermodynamic quantities and stellar observables using Plotly. It supports:

- 1D and 2D plots of CMF EOS data.
- Visualization of QLIMR observables (e.g., mass, radius, moment of inertia).
- 3D comparison plots between CMF EOS and Lepton-neutralized data.

Author: Nikolas Cruz Camacho
Email:  cnc6@illinois.edu
"""

import plotly.graph_objects as go

# Mapping from raw column names to display labels
label_map = {
    'T': 'Temperature [MeV]',
    'muB': 'Baryon Chemical Potential [MeV]',
    'muQ': 'Electric Charge Chemical Potential [MeV]',
    'muS': 'Strange Chemical Potential [MeV]',
    'nB': 'Baryon Density [fm^-3]',
    'nS': 'Strange Density [fm^-3]',
    'nQ': 'Electric Charge Density [fm^-3]',
    'E': 'Energy Density [MeV / fm^3]',
    'P': 'Pressure [MeV / fm^3]',
    's': 'Entropy Density [fm^-3]',
    'nB_noPol': 'Baryon Density (No Pol) [fm^-3]',
    'Quark_nB': 'Quark Baryon Density [fm^-3]',
    'Octet_nB': 'Octet Baryon Density [fm^-3]',
    'Decuplet_nB': 'Decuplet Baryon Density [fm^-3]',
}

qlimr_label_map = {
    'e_c': 'central energy density [MeV/fm^3]',
    'Q': 'cuadrupole moment',
    'L': 'Love number',
    'I': 'moment of inertia',
    'M': 'mass [sun mass]',
    'R': 'radius [km]',
}

def plot_QLIMR_observables(df, x_col, y_col, order='e_c', logy=False, logx=False):
    """
    Plot 1D line plot of QLIMR observables using Plotly.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing QLIMR observables.
    x_col : str
        Column name for the x-axis.
    y_col : str
        Column name for the y-axis.
    order : str, optional
        Column to sort the DataFrame by before plotting (default: 'e_c').
    logy : bool, optional
        Whether to apply a logarithmic scale to the y-axis.
    logx : bool, optional
        Whether to apply a logarithmic scale to the x-axis.

    Raises:
    -------
    ValueError
        If x_col or y_col is not found in the DataFrame.
    """
    print(f"Plotting 1D QLIMR observables for columns: {x_col} vs {y_col}")

    if x_col not in df.columns:
        raise ValueError(f"Column '{x_col}' not found in DataFrame.")
    if y_col not in df.columns:
        raise ValueError(f"Column '{y_col}' not found in DataFrame.")

    df = df.sort_values(by=order)

    x_label = qlimr_label_map.get(x_col, x_col)
    y_label = qlimr_label_map.get(y_col, y_col)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='lines',
        name=f'{y_col} vs {x_col}'
    ))

    fig.update_layout(
        title=f'QLIMR Plot for {y_col} vs {x_col}',
        xaxis_title=x_label,
        yaxis_title=y_label,
        template='plotly_white',
        hovermode='closest'
    )

    if logx:
        fig.update_xaxes(type='log')
    if logy:
        fig.update_yaxes(type='log')

    fig.show()

def plot_1D_CMF_EoS(df, x_col, y_col):
    """
    Plot a 1D CMF Equation of State curve using Plotly.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing EOS data.
    x_col : str
        Column name for the x-axis.
    y_col : str
        Column name for the y-axis.

    Raises:
    -------
    ValueError
        If x_col or y_col is not found in the DataFrame.
    """
    print(f"Plotting 1D CMF EOS for columns: {x_col} vs {y_col}")

    if x_col not in df.columns:
        raise ValueError(f"Column '{x_col}' not found in DataFrame.")
    if y_col not in df.columns:
        raise ValueError(f"Column '{y_col}' not found in DataFrame.")

    df = df.sort_values(by=x_col)

    x_label = label_map.get(x_col, x_col)
    y_label = label_map.get(y_col, y_col)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='lines',
        name='CMF EOS'
    ))

    fig.update_layout(
        title='1D CMF EOS Plot',
        xaxis_title=x_label,
        yaxis_title=y_label,
        template='plotly_white',
        hovermode='closest'
    )

    fig.show()

def plot_2D_CMF_EoS(df, x_col, y_col, z_col):
    """
    Plot a 3D scatter plot of CMF EOS data using Plotly.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing EOS data.
    x_col : str
        Column name for the x-axis.
    y_col : str
        Column name for the y-axis.
    z_col : str
        Column name for the z-axis (used for both height and color).

    Raises:
    -------
    ValueError
        If any of the specified columns are not found in the DataFrame.
    """
    print(f"Plotting 2D CMF EOS for columns: {x_col} vs {y_col} vs {z_col}")

    for col in (x_col, y_col, z_col):
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame.")

    x_label = label_map.get(x_col, x_col)
    y_label = label_map.get(y_col, y_col)
    z_label = label_map.get(z_col, z_col)

    fig = go.Figure(data=[go.Scatter3d(
        x=df[x_col],
        y=df[y_col],
        z=df[z_col],
        mode='markers',
        marker=dict(
            size=3,
            color=df[z_col],
            colorscale='Viridis',
            colorbar=dict(title=z_label),
            opacity=0.8
        )
    )])

    fig.update_layout(
        title='2D CMF EOS Plot',
        scene=dict(
            xaxis_title=x_label,
            yaxis_title=y_label,
            zaxis_title=z_label
        ),
        margin=dict(l=0, r=0, b=0, t=40)
    )

    fig.show()

def plot_2D_CMF_EoS_with_Lepton(cmf_df, lepton_df, y_col):
    """
    Overlay a 3D CMF EOS scatter plot with a Lepton EOS line plot for comparison.

    Parameters:
    -----------
    cmf_df : pandas.DataFrame
        DataFrame containing CMF EOS data.
    lepton_df : pandas.DataFrame
        DataFrame containing lepton-neutralized EOS data.
    y_col : str
        Column name for the y-axis (typically a density).

    Raises:
    -------
    ValueError
        If any of the required columns are not found in the input DataFrames.
    """
    print(f"Plotting 2D CMF EOS with Lepton data")

    x_col = 'E'  # Energy Density
    z_col = 'P'  # Pressure

    for col in (x_col, y_col, z_col):
        if col not in cmf_df.columns:
            raise ValueError(f"Column '{col}' not found in CMF DataFrame.")
        if col not in lepton_df.columns:
            raise ValueError(f"Column '{col}' not found in Lepton DataFrame.")

    x_label = label_map.get(x_col, x_col)
    y_label = label_map.get(y_col, y_col)
    z_label = label_map.get(z_col, z_col)

    scatter_trace = go.Scatter3d(
        x=cmf_df[x_col],
        y=cmf_df[y_col],
        z=cmf_df[z_col],
        mode='markers',
        name='CMF EOS',
        marker=dict(
            size=3,
            color=cmf_df[z_col],
            colorscale='Viridis',
            colorbar=dict(title=z_label),
            opacity=0.8
        )
    )

    line_trace = go.Scatter3d(
        x=lepton_df[x_col],
        y=lepton_df[y_col],
        z=lepton_df[z_col],
        mode='lines',
        name='Lepton EOS',
        line=dict(color='red', width=6)
    )

    fig = go.Figure(data=[scatter_trace, line_trace])

    fig.update_layout(
        title='2D CMF EOS with Lepton neutralization',
        scene=dict(
            xaxis_title=x_label,
            yaxis_title=y_label,
            zaxis_title=z_label
        ),
        legend=dict(x=0, y=1),
        margin=dict(l=0, r=0, b=0, t=40)
    )

    fig.show()
