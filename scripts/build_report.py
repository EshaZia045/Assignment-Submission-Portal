import json, os, time, datetime, urllib.request

RAW = "raw-results.json"

def build():
    raw = json.load(open(RAW)) if os.path.exists(RAW) else {"tests": []}
    tests = []
    for t in raw["tests"]:
        msg = None
        if t["outcome"] != "passed":
            for phase in ("setup", "call", "teardown"):
                p = t.get(phase)
                if p and p.get("outcome") == "failed":
                    msg = (p.get("crash") or {}).get("message") or p.get("longrepr")
                    break
        tests.append({"name": t["nodeid"].split("::")[-1],
                      "result": t["outcome"],
                      "failure_message": msg})
    passed = sum(1 for t in tests if t["result"] == "passed")
    failed = len(tests) - passed
    return {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "tests": tests,
        "summary": {"total": len(tests), "passed": passed, "failed": failed},
        "overall_status": "passed" if tests and failed == 0 else "failed",
    }

def post(report):
    url = os.environ.get("RECEIVER_URL")
    if not url:
        print("RECEIVER_URL not set; skipping POST")
        return
    req = urllib.request.Request(
        url, data=json.dumps(report).encode(), method="POST",
        headers={"Content-Type": "application/json",
                 "X-Report-Token": os.environ.get("REPORT_TOKEN", "")})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                print("Receiver responded:", r.status)
                return
        except Exception as e:
            print(f"POST attempt {attempt+1} failed: {e}")
            time.sleep(3)
    print("WARNING: could not deliver report")

if __name__ == "__main__":
    report = build()
    with open("test-report.json", "w") as f:
        json.dump(report, f, indent=2)
    s = report["summary"]
    with open("summary.txt", "w") as f:
        f.write(f"Commit: {report['commit_sha']}\nResult: {report['overall_status']}\n"
                f"Total: {s['total']}  Passed: {s['passed']}  Failed: {s['failed']}\n\n")
        for t in report["tests"]:
            f.write(f"- {t['name']}: {t['result']}\n")
    post(report)
