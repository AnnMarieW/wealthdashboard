# -*- coding: utf-8 -*-
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import pathlib

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB, dbc.icons.FONT_AWESOME])

# set relative path
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("./data").resolve()

#  make dataframe from  spreadsheet:
df = pd.read_excel(DATA_PATH.joinpath("historic.xlsx"))

MAX_YR = df.Year.max()
MIN_YR = df.Year.min()
START_YR = 2007

COLORS = {
    "cash": "#3cb521",
    "bonds": "#fd7e14",
    "stocks": "#446e9b",
    "inflation": "#cd0200",
    "background": "whitesmoke",
}

# since data is as of year end, need to add start year
df = (
    df.append({"Year": MIN_YR - 1}, ignore_index=True)
    .sort_values("Year", ignore_index=True)
    .fillna(0)
)

"""
==========================================================================
Tables
"""

total_returns_table = dash_table.DataTable(
    id="total_returns",
    columns=[{"id": "Year", "name": "Year", "type": "text"}]
    + [
        {"id": col, "name": col, "type": "numeric", "format": {"specifier": "$,.0f"}}
        for col in ["Cash", "Bonds", "Stocks", "Total"]
    ],
    page_size=15,
)

annual_returns_pct_table = dash_table.DataTable(
    id="annual_returns_pct",
    columns=(
        [{"id": "Year", "name": "Year", "type": "text"}]
        + [
            {"id": col, "name": col, "type": "numeric", "format": {"specifier": ".1%"}}
            for col in df.columns[1:]
        ]
    ),
    data=df.to_dict("records"),
    style_table={"overflowX": "scroll"},
    page_size=15,
)


def make_summary_table(dff):
    """Make html table to show cagr and  best and worst periods"""

    cash = html.Span(
        [html.I(className="fa fa-money-bill-alt"), " Cash"], className="h5 text-body"
    )
    bonds = html.Span(
        [html.I(className="fa fa-handshake"), " Bonds"], className="h5 text-body"
    )
    stocks = html.Span(
        [html.I(className="fa fa-industry"), " Stocks"], className="h5 text-body"
    )
    inflation = html.Span(
        [html.I(className="fa fa-ambulance"), " Inflation"], className="h5 text-body"
    )

    start_yr = dff["Year"].iat[0]
    end_yr = dff["Year"].iat[-1]

    df_table = pd.DataFrame(
        {
            "": [cash, bonds, stocks, inflation],
            f"Annual returns (CAGR) from {start_yr} to {end_yr}": [
                cagr(dff["all_cash"]),
                cagr(dff["all_bonds"]),
                cagr(dff["all_stocks"]),
                cagr(dff["inflation_only"]),
            ],
            f"Worst Year from {start_yr} to {end_yr}": [
                worst(dff, "3-mon T.Bill"),
                worst(dff, "10yr T.Bond"),
                worst(dff, "S&P 500"),
                "",
            ],
        }
    )
    return dbc.Table.from_dataframe(df_table, bordered=True, hover=True)


"""
==========================================================================
Figures
"""


def make_pie(slider_input, title):
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Cash", "Bonds", "Stocks"],
                values=slider_input,
                textinfo="label+percent",
                textposition="inside",
                marker={"colors": [COLORS["cash"], COLORS["bonds"], COLORS["stocks"]]},
                sort=False,
                hoverinfo="none",
            )
        ]
    )
    fig.update_layout(
        title_text=title,
        title_x=0.5,
        margin=dict(b=25, t=75, l=35, r=25),
        height=325,
        paper_bgcolor=COLORS["background"],
    )
    return fig


def make_returns_chart(dff):
    start = dff.loc[1, "Year"]
    yrs = dff["Year"].size - 1
    dtick = 1 if yrs < 16 else 2 if yrs in range(16, 30) else 5

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["all_cash"],
            name="All Cash",
            marker_color=COLORS["cash"],
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["all_bonds"],
            name="All Bonds (10yr T.Bonds)",
            marker_color=COLORS["bonds"],
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["all_stocks"],
            name="All Stocks (S&P500)",
            marker_color=COLORS["stocks"],
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["Total"],
            name="My Portfolio",
            marker_color="black",
            line=dict(width=6, dash="dot"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["inflation_only"],
            name="Inflation",
            visible=True,
            marker_color=COLORS["inflation"],
        )
    )
    fig.update_layout(
        title=f"Returns for {yrs} years starting {start}",
        template="none",
        showlegend=True,
        legend=dict(x=0.01, y=0.99),
        height=400,
        margin=dict(l=40, r=10, t=60, b=55),
        yaxis=dict(tickprefix="$", fixedrange=True),
        xaxis=dict(title="Year Ended", fixedrange=True, dtick=dtick),
    )
    return fig


"""
==========================================================================
Markdown Text
"""

datasource_text = dcc.Markdown(
    """
    [Data source:](http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html)
    Historical Returns on Stocks, Bonds and Bills from NYU Stern School of
    Business
    """
)

asset_allocation_text = dcc.Markdown(
    """

> **Asset allocation** is one of the main drivers of investment results.  Balance the risk (volatility) and rewards 
  by changing how much you invest in   different asset classes.   Play with the app and see for yourself!

> Change the allocation to cash, bonds and stocks on the sliders and see your portfolio results in the graph.
  Try entering different time periods and dollar amounts too.
"""
)

learn_text = dcc.Markdown(
    """
    Past performance certainly does not determine future results, but you can still
    learn a lot by reviewing how various asset classes have performed over time.

    Use the sliders to change the asset allocation (how much you invest in cash vs
    bonds vs stock) and see how this affects your returns.

    Note that the results shown in "My Portfolio" assumes rebalancing was done at
    the beginning of every year.  Also, this information is based on the S&P 500 index
    as a proxy for "stocks", the 10 year US Treasury Bond for "bonds" and the 3 month
    US Treasury Bill for "cash."  Your results of course,  would be different based
    on your actual holdings.

    This is intended to help you determine your investment philosophy and understand
    what sort of risks and returns you might see for each asset category.

    The  data is from [Aswath Damodaran](http://people.stern.nyu.edu/adamodar/New_Home_Page/home.htm)
    who teaches  corporate finance and valuation at the Stern School of Business
    at New York University.

    Check out his excellent on-line course in
    [Investment Philosophies.](http://people.stern.nyu.edu/adamodar/New_Home_Page/webcastinvphil.htm)
    """
)

footer = html.Div(
    dcc.Markdown(
        """
         This information is intended solely as general information for educational
        and entertainment purposes only and is not a substitute for professional advice and
        services from qualified financial services providers familiar with your financial
        situation.    Questions?  Suggestions? Please don't hesitate to get in touch:
          [Email](mailto:awardapps@fastmail.com?subject=cool)
        """
    ),
    className="p-2 mt-5 bg-primary text-white small",
)

"""
==========================================================================
Make Tabs
"""

# =======Play tab components

asset_allocation_card = dbc.Card(asset_allocation_text, className="mt-2")

slider_card = dbc.Card(
    dbc.CardBody(
        [
            html.H4("First set cash allocation %:", className="card-title"),
            dcc.Slider(
                id="cash",
                marks={i: f"{i}%" for i in range(0, 101, 10)},
                min=0,
                max=100,
                step=5,
                value=10,
                included=False,
            ),
            html.H4(
                "Then set stock allocation % ",
                className="card-title mt-3",
            ),
            html.Div("(The rest will be bonds)", className="card-title"),
            dcc.Slider(
                id="stock_bond",
                marks={i: f"{i}%" for i in range(0, 91, 10)},
                min=0,
                max=90,
                step=5,
                value=50,
                included=False,
            ),
        ],
    ),
    className="mt-4",
)


inflation_checkbox = dbc.Checkbox(
    id="inflation", label="Include inflation on graph", value=True
)


time_period_card = dbc.Card(
    [
        html.H4(
            "Or check out one of these time periods:",
            className="card-title",
        ),
        dbc.RadioItems(
            id="select_timeframe",
            options=[
                {
                    "label": f"2007-2008: Great Financial Crisis to {MAX_YR}",
                    "value": "2007",
                },
                {
                    "label": "1999-2010: The decade including 2000 Dotcom Bubble peak",
                    "value": "1999",
                },
                {
                    "label": "1969-1979:  The 1970s Energy Crisis",
                    "value": "1970",
                },
                {
                    "label": "1929-1948:  The 20 years following the start of the Great Depression",
                    "value": "1929",
                },
                {"label": f"{MIN_YR}-{MAX_YR}", "value": "1928"},
            ],
            labelClassName="mb-2",
            value="2007",
        ),
    ],
    body=True,
    className="mt-4",
)


amount_input_card = html.Div(
    [
        dbc.InputGroup(
            [
                dbc.InputGroupText("Start Amount $ :"),
                dbc.Input(
                    id="starting_amount",
                    placeholder="Min $10",
                    type="number",
                    min=10,
                    value=10000,
                ),
            ],
            className="mb-3",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Number of Years:"),
                dbc.Input(
                    id="planning_time",
                    placeholder="# yrs",
                    type="number",
                    min=1,
                    value=MAX_YR - START_YR + 1,
                ),
            ],
            className="mb-3",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Start Year:"),
                dbc.Input(
                    id="start_yr",
                    placeholder=f"min {MIN_YR}   max {MAX_YR}",
                    type="number",
                    min=MIN_YR,
                    max=MAX_YR,
                    value=START_YR,
                ),
            ],
            className="mb-3",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("My Portfolio Results: ", className="h1 text-body"),
                dbc.Input(id="results", disabled=True, className="h1 text-body"),
            ],
            className="mb-3",
        ),
    ],
    className="mt-4",
    style={"maxWidth": 400},
)

# =====  Results Tab components

results_card = dbc.Card(
    [
        dbc.CardHeader("My Portfolio Returns - Rebalanced Annually"),
        dbc.CardBody(total_returns_table),
    ],
    className="mt-4",
)


data_source_card = dbc.Card(
    [
        dbc.CardHeader("Source Data: Annual Total Returns"),
        dbc.CardBody(annual_returns_pct_table),
    ],
    className="mt-4",
)


# ========= Learn Tab  Components
learn_card = dbc.Card(
    [
        dbc.CardHeader("An Introduction to Asset Allocation"),
        dbc.CardBody(learn_text),
    ],
    className="mt-4",
)


# ========= Build tabs
tabs = dbc.Tabs(
    [
        dbc.Tab(learn_card, tab_id="tab1", label="Learn"),
        dbc.Tab(
            [
                asset_allocation_text,
                slider_card,
                amount_input_card,
                inflation_checkbox,
                time_period_card,
                dbc.Button("Print", id="print", className="mt-4"),
            ],
            tab_id="tab-2",
            label="Play",
        ),
        dbc.Tab([results_card, data_source_card], tab_id="tab-3", label="Results"),
    ],
    id="tabs",
    active_tab="tab-2",
)


"""
===========================================================================
Main Layout
"""

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H2(
                    "Asset Allocation Visualizer",
                    className="text-center bg-primary text-white p-2",
                ),
            )
        ),
        dbc.Row(
            [
                dbc.Col(tabs, width=12, lg=5, className="mt-4 border"),
                dbc.Col(
                    [
                        dcc.Graph(id="allocation_pie_chart", className="mb-2"),
                        dcc.Graph(id="returns_chart", className="pb-4"),
                        html.Hr(),
                        html.Div(id="summary_table"),
                        html.H6(datasource_text, className="my-2"),
                        html.Div(id="dummy_div"),
                    ],
                    width=12,
                    lg=7,
                    className="pt-4 ",
                ),
            ],
            className="ms-1",
        ),
        dbc.Row(dbc.Col(footer)),
    ],
    fluid=True,
)

"""
==========================================================================
Helper functions to calculate investment results, cagr and worst periods
"""


def backtest(stocks, cash, start_bal, nper, start_yr):
    """calculates the investment returns for user selected asset allocation,
    rebalanced annually
    """

    end_yr = start_yr + nper - 1
    cash_allocation = cash / 100
    stocks_allocation = stocks / 100
    bonds_allocation = (100 - stocks - cash) / 100

    # Select time period - since data is for year end, include year prior
    # for start ie year[0]
    dff = df[(df.Year >= start_yr - 1) & (df.Year <= end_yr)].set_index(
        "Year", drop=False
    )
    dff["Year"] = dff["Year"].astype(int)

    # add columns for My Portfolio returns
    dff["Cash"] = cash_allocation * start_bal
    dff["Bonds"] = bonds_allocation * start_bal
    dff["Stocks"] = stocks_allocation * start_bal
    dff["Total"] = start_bal
    dff["Rebalance"] = True

    # calculate My Portfolio returns
    for yr in dff.Year + 1:
        if yr <= end_yr:
            # Rebalance at the beginning of the period by reallocating
            # last period's total ending balance
            if dff.loc[yr, "Rebalance"]:
                dff.loc[yr, "Cash"] = dff.loc[yr - 1, "Total"] * cash_allocation
                dff.loc[yr, "Stocks"] = dff.loc[yr - 1, "Total"] * stocks_allocation
                dff.loc[yr, "Bonds"] = dff.loc[yr - 1, "Total"] * bonds_allocation

            # calculate this period's  returns
            dff.loc[yr, "Cash"] = dff.loc[yr, "Cash"] * (
                1 + dff.loc[yr, "3-mon T.Bill"]
            )
            dff.loc[yr, "Stocks"] = dff.loc[yr, "Stocks"] * (1 + dff.loc[yr, "S&P 500"])
            dff.loc[yr, "Bonds"] = dff.loc[yr, "Bonds"] * (
                1 + dff.loc[yr, "10yr T.Bond"]
            )
            dff.loc[yr, "Total"] = dff.loc[yr, ["Cash", "Bonds", "Stocks"]].sum()

    dff = dff.reset_index(drop=True)
    columns = ["Cash", "Stocks", "Bonds", "Total"]
    dff[columns] = dff[columns].round(0)

    # create columns for when portfolio is all cash, all bonds or  all stocks,
    #   include inflation too
    #
    # create new df that starts in yr 1 rather than yr 0
    dff1 = (dff[(dff.Year >= start_yr) & (dff.Year <= end_yr)]).copy()
    #
    # calculate the returns in new df:
    columns = ["all_cash", "all_bonds", "all_stocks", "inflation_only"]
    annual_returns = ["3-mon T.Bill", "10yr T.Bond", "S&P 500", "Inflation"]
    for col, return_pct in zip(columns, annual_returns):
        dff1[col] = round(start_bal * (1 + (1 + dff1[return_pct]).cumprod() - 1), 0)
    #
    # select columns in the new df to merge with original
    dff1 = dff1[["Year"] + columns]
    dff = dff.merge(dff1, how="left")
    # fill in the starting balance for year[0]
    dff.loc[0, columns] = start_bal
    return dff


def cagr(dff):
    """calculate Compound Annual Growth Rate for a series:"""

    start_bal = dff.iat[0]
    end_bal = dff.iat[-1]
    planning_time = len(dff) - 1
    cagr_result = ((end_bal / start_bal) ** (1 / planning_time)) - 1
    return f"{cagr_result:.1%}"


def worst(dff, asset):
    """calculate worst returns for asset in selected period
    and format for display panel"""

    worst_yr_loss = min(dff[asset])
    worst_yr = dff.loc[dff[asset] == worst_yr_loss, "Year"].iloc[0]
    return f"{worst_yr_loss:.1%} in {worst_yr}"


"""
==========================================================================
Callbacks
"""


@app.callback(
    Output("allocation_pie_chart", "figure"),
    Input("stock_bond", "value"),
    Input("cash", "value"),
)
def update_pie(stocks, cash):
    bonds = 100 - stocks - cash
    slider_input = [cash, bonds, stocks]

    if stocks >= 70:
        investment_style = "Aggressive"
    elif stocks <= 30:
        investment_style = "Conservative"
    else:
        investment_style = "Moderate"
    figure = make_pie(slider_input, investment_style + " Asset Allocation")
    return figure


@app.callback(
    Output("stock_bond", "max"),
    Output("stock_bond", "marks"),
    Output("stock_bond", "value"),
    Input("cash", "value"),
    State("stock_bond", "value"),
)
def update_stock_slider(cash, initial_stock_value):
    max_slider = 100 - int(cash)
    stocks = min(max_slider, initial_stock_value)

    # formats the slider scale
    if max_slider > 50:
        marks_slider = {i: f"{i}%" for i in range(0, max_slider + 1, 10)}
    elif max_slider <= 15:
        marks_slider = {i: f"{i}%" for i in range(0, max_slider + 1, 1)}
    else:
        marks_slider = {i: f"{i}%" for i in range(0, max_slider + 1, 5)}
    return max_slider, marks_slider, stocks


@app.callback(
    Output("planning_time", "value"),
    Output("start_yr", "value"),
    Output("select_timeframe", "value"),
    Input("planning_time", "value"),
    Input("start_yr", "value"),
    Input("select_timeframe", "value"),
)
def update_timeframe(planning_time, start_yr, timeframe_start):
    """syncs inputs and selected time periods"""
    ctx = callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    timeframe_years = {
        "2007": MAX_YR - START_YR + 1,
        "1999": 10,
        "1970": 10,
        "1929": 20,
        "1928": MAX_YR - MIN_YR + 1,
    }
    if trigger_id == "select_timeframe":
        planning_time = timeframe_years[timeframe_start]
        start_yr = timeframe_start

    if trigger_id in ["planning_time", "start_yr"]:
        timeframe_start = None

    return planning_time, start_yr, timeframe_start


@app.callback(
    Output("total_returns", "data"),
    Output("returns_chart", "figure"),
    Output("summary_table", "children"),
    Output("results", "value"),
    Input("stock_bond", "value"),
    Input("cash", "value"),
    Input("starting_amount", "value"),
    Input("planning_time", "value"),
    Input("start_yr", "value"),
    Input("inflation", "value"),
)
def update_totals(stocks, cash, start_bal, planning_time, start_yr, inflation):
    # set defaults for invalid inputs
    start_bal = 10 if start_bal is None else start_bal
    planning_time = 1 if planning_time is None else planning_time
    start_yr = MIN_YR if start_yr is None else int(start_yr)

    # calculate valid time frames and ranges
    max_time = MAX_YR + 1 - start_yr
    planning_time = max_time if planning_time > max_time else planning_time
    if start_yr + planning_time > MAX_YR:
        start_yr = min(df.iloc[-planning_time, 0], MAX_YR)  # 0 is Year column

    # create investment results dataframe
    dff = backtest(stocks, cash, start_bal, planning_time, start_yr)

    # create data for DataTable
    data = dff.to_dict("records")

    # create the line chart
    fig = make_returns_chart(dff)
    fig.update_traces(visible=False, selector=dict(name="Inflation"))
    if inflation:
        fig.update_traces(visible=True, selector=dict(name="Inflation"))

    # create portfolio results text
    dollars = dff["Total"].iloc[-1]
    percentage = cagr(dff["Total"])
    my_portfolio_results = f"${dollars:0,.0f}    {percentage}"

    return data, fig, make_summary_table(dff), my_portfolio_results


app.clientside_callback(
    """
    function(n) {
        if (n > 0) {
          window.print()
        }
        return ""
    }
    """,
    Output("dummy_div", "children"),
    Input("print", "n_clicks"),
)

if __name__ == "__main__":
    app.run_server(debug=True)
