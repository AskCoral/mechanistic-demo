import json
import os

_DIR = os.path.dirname(os.path.abspath(__file__))

import requests

BASE_URL = "https://dev.api.lkm.cleeai.com"
ENDPOINT = "/tasks/trace_prediction"
URL = f"{BASE_URL}{ENDPOINT}"
QUERY = "What are the various theories for the founding of London?"

def call_trace_prediction(query: str) -> None:
    """
    Call the /trace_prediction endpoint with the given query.
    """
    payload = {"query": query}

    try:
        response = requests.post(URL, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise


def get_test_output():
    with open(os.path.join(_DIR, "report2.json"), "r") as f:
        out = json.load(f)
    return out


def process_query(query):
    out = call_trace_prediction(query)
    print(out)
    routing = out.get("final_result", {})
    decision = routing.get("decision") or out.get("final_result", {}).get("final_decision")
    decision_conf = round(float(routing.get("decision_confidence") or out.get("final_result", {}).get("decision_confidence", 1.0)), 4)
    answer = out.get("answer", {}).get("answer_text") or out.get("final_result", {}).get("final_response_text")
    compute_saved = round(float(out.get("compute_saved", {}).get("llm_calls_saved_pct", 0)), 4)
    return {
        "decision": decision,
        "confidence": decision_conf,
        "query": query,
        "answer": answer,
        "savings": compute_saved
    }