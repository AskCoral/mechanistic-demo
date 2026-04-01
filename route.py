import json
import os

_DIR = os.path.dirname(os.path.abspath(__file__))

import requests

BASE_URL = "https://dev.api.lkm.cleeai.com"
ENDPOINT = "/tasks/trace_prediction"
URL = f"{BASE_URL}{ENDPOINT}"
QUERY = "What are the various theories for the founding of London?"

def call_trace_prediction(queries: list[str]) -> None:
    """
    Call the /trace_prediction endpoint with the given query.
    """
    payload = {"queries": queries}

    try:
        response = requests.post(URL, json=payload, timeout=600)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def process_queries(queries):
    res = call_trace_prediction(queries)
    print(res)
    q_vals = res.get("query_routing", [])
    savings = round(float(res.get("compute", {}).get("avg_compute_saved_pct", 0)), 2)
    queries = []
    for q in q_vals:
        query = q.get("query")
        decision = q.get("routed_decision")
        conf = round(float(q.get("confidence", 1)), 2)
        answer = q.get("answer")
        queries.append(
            {
                "decision": decision,
                "confidence": conf,
                "query": query,
                "answer": answer,
                "savings": savings
            }
        )
    return queries

def get_test_output():
    with open(os.path.join(_DIR, "report2.json"), "r") as f:
        out = json.load(f)
    return out