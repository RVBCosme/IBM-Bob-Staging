"""Turn the run ledger into a release-readiness verdict via watsonx.ai. Stdlib only.
Env: WATSONX_APIKEY, WATSONX_PROJECT_ID. Never commit either."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

from rx import ledger

URL = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
MODEL = "ibm/granite-4-h-small"


def iam_token(apikey):
    data = urllib.parse.urlencode({"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": apikey}).encode()
    req = urllib.request.Request("https://iam.cloud.ibm.com/identity/token", data=data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    return json.load(urllib.request.urlopen(req))["access_token"]


def main(ledger_file):
    rows = ledger.read(ledger_file)
    summary = {
        "gates": [f"{r['from']}->{r['to']}" for r in rows if r["event"] == "gate"],
        "blocked_calls": [f"{r['phase']}:{r['tool']}:{r['path']}" for r in rows if r["event"] == "deny"],
        "recorded_writes": len([r for r in rows if r["event"] == "write"]),
        "security_exit": next((r.get("security_exit") for r in rows if r["event"] == "gate" and r["to"] == "review"), None),
    }
    body = {
        "model_id": MODEL,
        "project_id": os.environ["WATSONX_PROJECT_ID"],
        "max_completion_tokens": 300,
        "messages": [{"role": "user", "content": [{"type": "text", "text":
            "You are a release manager. Given this RATCHET run receipt, answer in 3 lines: "
            "READY or NOT READY, the residual risk, and the one thing to check by hand.\n" + json.dumps(summary)}]}],
    }
    req = urllib.request.Request(f"{URL}/ml/v1/text/chat?version=2024-03-14", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + iam_token(os.environ["WATSONX_APIKEY"])})
    try:
        out = json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:                      # watsonx explains 4xx in the body; show it, never the key
        sys.exit(f"watsonx {e.code}: {e.read().decode()[:600]}")
    print(out["choices"][0]["message"]["content"])


if __name__ == "__main__":
    main(sys.argv[1])
