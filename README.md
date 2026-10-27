# Assignment Submission Portal (CSC418 Lab Midterm)

A small Flask app where students submit their name, registration number, assignment
title and a submission URL. Every push runs automated tests in GitHub Actions, and the
test report (JSON) is sent to a local receiver that saves it as `test-report.json`.

## Setup

```bash
python -m venv venv
# Windows: venv\Scripts\activate      macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

## Run the application

```bash
python app.py
```
Open http://127.0.0.1:5000. Valid submissions are saved to `submissions.json`.

## Run the tests

```bash
pytest -v
```
Tests cover: valid submission saved and listed, missing registration number rejected,
invalid URL rejected and not saved.

## Start the local receiver

```bash
# macOS/Linux
REPORT_TOKEN=mysecret python receiver.py
# Windows PowerShell
$env:REPORT_TOKEN="mysecret"; python receiver.py
```
It listens on `http://127.0.0.1:5001/report` and writes each received report to
`test-report.json` in the current folder.

## Reach your computer from GitHub Actions

**Option A: tunnel** (GitHub-hosted runner)
1. Keep the receiver running.
2. In another terminal: `cloudflared tunnel --url http://localhost:5001` (or `ngrok http 5001`).
3. Repo -> Settings -> Secrets and variables -> Actions, add:
   - `RECEIVER_URL` = `https://<tunnel-host>/report`
   - `REPORT_TOKEN` = `mysecret`
4. Quick tunnels change URL on every restart; update the secret each time.

**Option B: self-hosted runner**
1. Repo -> Settings -> Actions -> Runners -> New self-hosted runner, follow the steps.
2. In `.github/workflows/ci.yml` set `runs-on: self-hosted` for the `test` job.
3. Set `RECEIVER_URL` = `http://localhost:5001/report` and `REPORT_TOKEN`.

## How the pipeline works

```
git push -> GitHub Actions -> pytest (JSON results) -> scripts/build_report.py
         -> POST to RECEIVER_URL -> receiver.py saves test-report.json
```
- A failing test fails the "Run tests" step and the job.
- The report step uses `if: always()`, so reports are sent for passing and failing runs.
- The `deploy` job (`needs: test`, main branch only) publishes `site/` to GitHub Pages
  only if all tests pass. Enable it under Settings -> Pages -> Source: GitHub Actions.
- Email bonus: add secrets `SMTP_USERNAME`, `SMTP_PASSWORD`, `REPORT_EMAIL_TO` and
  uncomment the "Email report" step in `ci.yml`.

## Demonstrating a failure

In `app.py`, change `if not form[k]:` to `if False:` (or make `is_valid_url` always
return `True`), commit and push. The pipeline fails and `test-report.json` shows
`"overall_status": "failed"` with failure messages. Revert the change and push again to
get a passing run.
