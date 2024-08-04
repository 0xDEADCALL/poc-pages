import datetime

import numpy as np
import pandas as pd
import panel as pn
import plotly.graph_objs as go


def plot_exec_pass_rate(overview_pd):
    # Make plot
    fig_overview = go.Figure(
        [
            go.Scatter(
                x=overview_pd.exec_dt,
                y=overview_pd.passed_pct,
                mode="lines+markers",
                marker=dict(size=10, color=overview_pd.color),
                hovertemplate="<br><b>Date</b>: %{x}<br>"
                + "<b>Successful Checks</b>: %{y}"
                + "<extra></extra>",
            )
        ]
    )

    # Update layout and other params
    fig_overview.update_layout(
        yaxis_tickformat=".1%",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        margin=dict(l=10, r=10, t=20, b=10),
    )

    fig_overview.update_traces(line_color="#4099da")

    return fig_overview


def plot_groups_pass_rate(data_pd):
    # Create groups data
    groups_pd = (
        data_pd.filter(items=["question_id", "result"])
        .groupby("question_id")
        .value_counts()
        .to_frame()
        .reset_index()
        .pivot(index="question_id", columns="result", values="count")
        .reset_index()
        .rename(columns={False: "Failed", True: "Passed"})
        .sort_values(by="Failed", ascending=False)
    )

    # Make plot
    fig_groups = go.Figure(
        [
            go.Bar(
                name="Passed",
                y=groups_pd["question_id"],
                x=groups_pd["Passed"],
                orientation="h",
                marker=dict(color="#00A170"),
                hovertemplate="<b>Checks Passed </b>: %{x}<extra></extra>",
            ),
            go.Bar(
                name="Failed",
                y=groups_pd["question_id"],
                x=groups_pd["Failed"],
                orientation="h",
                marker=dict(color="#F08080"),
                hovertemplate="<b>Checks Failed </b>: %{x}<extra></extra>",
            ),
        ]
    )

    fig_groups.update_traces(width=0.2)

    # Update layout
    fig_groups.update_layout(
        margin_pad=10,
        showlegend=False,
        barmode="stack",
        bargap=0.2,
        bargroupgap=0.1,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )

    # Update axes
    fig_groups.update_yaxes(tickfont=dict(size=20))

    return fig_groups


# Center widget
def center_wd(x):
    return pn.Column(
        pn.layout.VSpacer(),
        pn.Row(pn.layout.HSpacer(), x, pn.layout.HSpacer()),
        pn.layout.VSpacer(),
    )


def metric_wd(title: str, text: str):
    return pn.widgets.StaticText(
        name="",
        value=f"""
            <p style="text-align:center">
            <font color="black" size="5pt">{title}</font>
            <br>
            <font size="20pt">{text}</font>
            </p>
        """,
    )


def metric_avg_pass_rate(overview_pd):
    value = 100.0 * (overview_pd.passed / overview_pd.total).mean()

    # Make metric card
    avg_pass_rate_wd = pn.indicators.Number(
        name='<font color="black">Avg. Pass Rate</font>',
        value=round(value, 2),
        format="{value}%",
        colors=[(50, "#F08080"), (70, "#DAA520"), (100, "#00A170")],
        font_size="40pt",
        title_size="19pt",
        align=("center"),
    )

    return center_wd(avg_pass_rate_wd)


def metric_last_exec(overview_pd):
    delta = (datetime.date.today() - overview_pd.exec_dt.max()).days

    if delta > 14:
        last_exec_color = "#F08080"
    elif delta > 7:
        last_exec_color = "#DAA520"
    else:
        last_exec_color = "#00A170"

    last_exec_wd = pn.widgets.StaticText(
        name="",
        value=f"""
            <p style="text-align:center">
            <font color="black" size="5pt">Last Execution</font>
            <br>
            <font size="20pt" color={last_exec_color}>{overview_pd.exec_dt.max()}</font>
            </p>
        """,
    )

    return center_wd(last_exec_wd)


def metric_total_apps(data_pd):
    value = data_pd.query("exec_dt == exec_dt.max()").exec_id.nunique()

    return center_wd(metric_wd("# Applications", value))


def metric_total_quest(data_pd):
    value = data_pd.query("exec_dt == exec_dt.max()").question_id.nunique()

    return center_wd(metric_wd("# Questions", value))


# Instantiate the template with widgets displayed in the sidebar
def get_page(data_pd):
    # Prepare data for overview
    overview_pd = (
        data_pd.assign(exec_dt=lambda x: pd.to_datetime(x.exec_dt).dt.date)
        .groupby("exec_dt")
        .agg(passed=("result", "sum"), total=("result", "count"))
        .assign(passed_pct=lambda x: round(x.passed / x.total, 2))
        .assign(failed=lambda x: x.total - x.passed)
        .assign(color=lambda x: np.where(x.passed_pct > 0.5, "#00A170", "#F08080"))
        .reset_index()
    )

    overview_wd = pn.widgets.Button(name='Overview', button_type='primary', disabled=True, sizing_mode="stretch_width")
    details_wd = pn.widgets.Button(name='Details', button_type='light', sizing_mode="stretch_width")

    details_wd.js_on_click({}, code="""window.location = "/details.html" """)

    # Build temaplte
    template = pn.template.FastGridTemplate(
        title="LiteDQ Overview",
        sidebar=[overview_wd, details_wd]
    )

    template.main[:4, 0:12] = pn.Column(
        pn.pane.Markdown("# Checks Status Time"),
        pn.panel(plot_exec_pass_rate(overview_pd), sizing_mode="stretch_both"),
        sizing_mode="stretch_both",
    )

    template.main[4:6, 0:6] = pn.Column(
        pn.pane.Markdown("# Check Status per Question ID"),
        pn.panel(plot_groups_pass_rate(data_pd), sizing_mode="stretch_width"),
        sizing_mode="stretch_both",
    )

    template.main[4:5, 6:9] = metric_avg_pass_rate(overview_pd)
    template.main[4:5, 9:12] = metric_last_exec(overview_pd)
    template.main[5:6, 6:9] = metric_total_apps(data_pd)
    template.main[5:6, 9:12] = metric_total_quest(data_pd)

    return template
