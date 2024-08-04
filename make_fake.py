import datetime
import json
import random
from datetime import timedelta

data = [
    {
        "exec_id": "23cf188a-daed-4e99-966b-3c55b242f49a",
        "exec_dt": datetime.datetime(2024, 7, 28, 16, 27, 41, 254362),
        "question_id": "check_species",
        "question_desc": "Check the number of species",
        "subject": [
            {"variety": "Setosa"},
            {"variety": "Versicolor"},
            {"variety": "Virginica"},
        ],
        "result": True,
    },
    {
        "exec_id": "6e177eef-2163-4b20-be96-1bb105af3a8a",
        "exec_dt": datetime.datetime(2024, 7, 28, 16, 27, 41, 254362),
        "question_id": "check_max_sepal",
        "question_desc": "Check the maximum sepal is not above 8",
        "subject": None,
        "result": True,
    },
    {
        "exec_id": "077eb658-a0a8-46d3-bc48-d7989895c4e7",
        "exec_dt": datetime.datetime(2024, 7, 28, 16, 27, 41, 254362),
        "question_id": "check_species_spark",
        "question_desc": "Check the number of species in spark",
        "subject": [
            {"variety": "Virginica"},
            {"variety": "Setosa"},
            {"variety": "Versicolor"},
        ],
        "result": True,
    },
    {
        "exec_id": "8e38ba7c-4836-45eb-8b7d-4221f79a7462",
        "exec_dt": datetime.datetime(2024, 7, 28, 16, 27, 41, 254362),
        "question_id": "check_count_spark",
        "question_desc": "Check the count in spark",
        "subject": {"count": 150},
        "result": False,
    },
]


# Fill with temp data
synth_data = []

for x in range(20):
    buffer = []
    for y in data:
        w = dict(y)
        w["exec_dt"] = y["exec_dt"] + timedelta(days=x)
        w["result"] = bool(random.getrandbits(1))
        buffer.append(w)
    synth_data += buffer


with open("data/data.json", "w", encoding="utf-8") as f:
    json.dump(synth_data, f, default=str)
