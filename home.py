import datetime
import json
import random
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import panel as pn
import plotly.express as px
import plotly.graph_objs as go
from bokeh.resources import INLINE
from index import get_page as overview_page
from details import get_page as details_page

data_path = Path(__file__).parents[0] / "data" / "data.json"
f = open(data_path)

synth_data = json.load(f)

# Get main data
main_data = [
    {
        x: row[x]
        for x in ["exec_id", "exec_dt", "question_id", "question_desc", "subject", "result"]
    }
    for row in synth_data
]
data_pd = (pd.DataFrame.from_dict(main_data)
           .assign(subject=lambda x: x.subject.astype(str))
           .replace("None", "")
           )

# Make overview
overview_pd = (
    data_pd.assign(exec_dt=lambda x: pd.to_datetime(x.exec_dt).dt.date)
    .groupby("exec_dt")
    .agg(passed=("result", "sum"), total=("result", "count"))
    .assign(passed_pct=lambda x: round(x.passed / x.total, 2))
    .assign(failed=lambda x: x.total - x.passed)
    .assign(color=lambda x: np.where(x.passed_pct > 0.5, "#00A170", "#F08080"))
    .reset_index()
)

# Get distinct qids and their pass rate
qid_rate_pd = (data_pd
               .assign(exec_dt=lambda x: pd.to_datetime(x.exec_dt).dt.date)
               .groupby(["question_id", "exec_dt"])
               .agg(passed=("result", "sum"), total=("result", "count"))
               .assign(passed_pct=lambda x: round(x.passed / x.total, 3))
               .assign(failed=lambda x: x.total - x.passed)
               .assign(color=lambda x: np.where(x.passed_pct > 0.5, "#00A170", "#F08080"))
               .reset_index()
               )


details_page(data_pd, qid_rate_pd).save("details.html")

overview_page(data_pd).save("index.html")

ROUTES = {
    "overview": lambda: overview_page(data_pd),
    "details": lambda: details_page(data_pd, qid_rate_pd)
}
