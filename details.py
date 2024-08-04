import json

import pandas as pd
import panel as pn
import plotly.graph_objs as go
from panel.theme import Bootstrap

pn.config.design = Bootstrap
pn.widgets.Tabulator.theme = "semantic-ui"


def bootstrapHTML(html):
    return f"""
        <!doctype html>
        <html lang="en">
          <head>
            <!-- Required meta tags -->
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        
            <!-- Bootstrap CSS -->
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        
            <title>Hello, world!</title>
          </head>
          <body>
            {html}
            <!-- Optional JavaScript -->
            <!-- jQuery first, then Popper.js, then Bootstrap JS -->
            <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
            <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
          </body>
        </html>    
    """


def plot_qid_pass_rate(qid, qid_rate_pd):
    rate_pd = qid_rate_pd.query(f"question_id == '{qid}'")

    fig = go.Figure(
        [
            go.Scatter(
                x=rate_pd.exec_dt,
                y=rate_pd.passed_pct,
                mode="lines+markers",
                marker=dict(size=10, color=rate_pd.color),
                hovertemplate="<br><b>Date</b>: %{x}<br>"
                + "<b>Successful Checks</b>: %{y}"
                + "<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        yaxis_tickformat=".1%",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        margin=dict(l=10, r=10, t=20, b=10),
        height=200,
    )
    fig.update_traces(line_color="#4099da")

    return fig


def card_wd(qid, data_pd, qid_rate_pd):
    # Get latest entry
    exec_pd = data_pd.query(f"question_id == '{qid}' and exec_dt == exec_dt.max()")

    # Get attributes
    desc = exec_pd.question_desc.iloc[0]
    print(exec_pd.subject.iloc[0].replace("'", "\""))

    print(type(exec_pd.subject.iloc[0].replace("'", "\"")))
    subject = json.loads(exec_pd.subject.iloc[0].replace("'", "\"") or "{}")
    subject_pd = pd.DataFrame.from_records(
        [subject] if isinstance(subject, dict) else subject
    )
    result_color = "#00A170" if exec_pd.result.iloc[0] else "#F08080"

    # Fill column
    col = pn.Column()

    # Add description
    col.append(
        pn.pane.HTML(
            f"""
            <h5>Description</h5>
            <p class="lead"><font size="3">{desc}</font></p>
        """
        )
    )
    col.append(pn.layout.Divider())

    # Add subject iv available
    if not subject_pd.empty:
        # Make table and download button
        table_wd = pn.widgets.Tabulator(
            subject_pd,
            show_index=False,
            disabled=True,
            sizing_mode="stretch_width",
            layout="fit_data_fill",
            header_align="right",
        )

        button_wd = pn.widgets.Button(name="Download", button_type="primary")
        button_wd.js_on_click(
            {"table": table_wd, "filename": f"{qid}_subject.csv"},
            code="""
                table.filename = filename
                table.download = !table.download
                """,
        )

        col.append(
            pn.Column(
                pn.pane.HTML(""" <h5>Subject</h5> """), pn.Row(button_wd), table_wd
            )
        )
        col.append(pn.layout.Divider())

    # Add overall pass rate for the question
    col += [
        pn.pane.HTML(""" <h5>Daily Pass Rate</h5> """),
        pn.panel(
            plot_qid_pass_rate(qid, qid_rate_pd),
            sizing_mode="stretch_width",
            height=300,
        ),
    ]

    return pn.Card(
        col,
        title=f""" <h5><b>{qid.upper()}</b></h5> """,
        header_background="#edf2fb",
        collapsed=True,
    )

    return col


def get_page(data_pd, qid_rate_pd):
    # Prepare data
    passed_qids = data_pd.query(
        f"result == True and exec_dt == exec_dt.max()"
    ).question_id.unique()
    failed_qids = data_pd.query(
        f"result == False and exec_dt == exec_dt.max()"
    ).question_id.unique()

    passed_card_wd = pn.Card(
        *[card_wd(x, data_pd, qid_rate_pd) for x in passed_qids],
        title=bootstrapHTML(
            f""" <h4><font color="#ffffff"><b>Successful Questions</b></font> <span class="badge badge-light">{passed_qids.shape[0]}</span></h4> """
        ),
        header_background="#00A170",
        sizing_mode="stretch_width"
    )

    failed_card_wd = pn.Card(
        *[card_wd(x, data_pd, qid_rate_pd) for x in failed_qids],
        title=bootstrapHTML(
            f""" <h4><font color="#ffffff"><b>Failed Questions</b></font> <span class="badge badge-light">{failed_qids.shape[0]}</span></h4> """
        ),
        header_background="#F08080",
        sizing_mode="stretch_width"
    )

    overview_wd = pn.widgets.Button(name='Overview', button_type='light', sizing_mode="stretch_width")
    details_wd = pn.widgets.Button(name='Details', button_type='primary', sizing_mode="stretch_width", disabled=True)

    overview_wd.js_on_click({}, code="""window.location = "/overview.html" """)

    template = pn.template.BootstrapTemplate(
        title="LiteDQ Details",
        sidebar=[overview_wd, details_wd]
    )

    template.main.append(pn.Column(passed_card_wd, failed_card_wd))

    return template
