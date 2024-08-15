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

import awswrangler as wr
import boto3


# Get data from AWS
session = boto3.Session()
data_pd = wr.athena.read_sql_query(
    "SELECT * FROM logs", 
    database="datalogger", 
    boto3_session=session
)

print(data_pd)

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
