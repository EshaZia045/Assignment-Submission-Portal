import json, os
from urllib.parse import urlparse
from flask import Flask, request, render_template_string

PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Assignment Portal</title>
<style>
  :root { --brand:#2f4fd8; --brand-dark:#2540b3; --bg:#f4f6fb; --card:#fff;
          --text:#1f2937; --muted:#6b7280; --line:#e5e7eb; --err:#b42318; --errbg:#fef3f2; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
         background:var(--bg); color:var(--text); line-height:1.5; }
  header { background:var(--brand); color:#fff; padding:1.5rem 1rem; }
  header div { max-width:860px; margin:0 auto; }
  header h1 { margin:0; font-size:1.5rem; }
  header p { margin:.25rem 0 0; opacity:.85; font-size:.95rem; }
  main { max-width:860px; margin:1.5rem auto; padding:0 1rem; display:grid; gap:1.5rem; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:12px;
          padding:1.5rem; box-shadow:0 1px 3px rgba(0,0,0,.05); }
  .card h2 { margin:0 0 1rem; font-size:1.15rem; }
  .grid { display:grid; grid-template-columns:1fr 1fr; gap:1rem; }
  .full { grid-column:1 / -1; }
  label { display:block; font-size:.85rem; font-weight:600; margin-bottom:.3rem; }
  input { width:100%; padding:.65rem .75rem; border:1px solid #d1d5db; border-radius:8px;
          font-size:.95rem; font-family:inherit; }
  input:focus { outline:2px solid var(--brand); outline-offset:1px; border-color:var(--brand); }
  button { background:var(--brand); color:#fff; border:0; border-radius:8px;
           padding:.7rem 1.4rem; font-size:.95rem; font-weight:600; cursor:pointer; }
  button:hover { background:var(--brand-dark); }
  .errors { background:var(--errbg); border:1px solid #fecdca; color:var(--err);
            border-radius:8px; padding:.75rem 1rem; margin-bottom:1rem; }
  .errors p { margin:.15rem 0; }
  table { width:100%; border-collapse:collapse; font-size:.92rem; }
  th, td { text-align:left; padding:.65rem .5rem; border-bottom:1px solid var(--line); }
  th { color:var(--muted); font-size:.78rem; text-transform:uppercase; letter-spacing:.04em; }
  td a { color:var(--brand); word-break:break-all; }
  .empty { color:var(--muted); text-align:center; padding:1.5rem 0; }
  .count { color:var(--muted); font-weight:400; font-size:.9rem; }
  @media (max-width:600px) { .grid { grid-template-columns:1fr; } }
</style>
</head>
<body>
<header><div>
  <h1>Assignment Submission Portal</h1>
  <p>Submit your assignment link for review.</p>
</div></header>
<main>
  <section class="card">
    <h2>New submission</h2>
    {% if errors %}
    <div class="errors">{% for e in errors %}<p>{{ e }}</p>{% endfor %}</div>
    {% endif %}
    <form method="post" novalidate>
      <div class="grid">
        <div><label for="name">Name</label>
             <input id="name" name="name" placeholder="e.g. Ali Khan"></div>
        <div><label for="reg_no">Registration number</label>
             <input id="reg_no" name="reg_no" placeholder="e.g. 2023-CS-045"></div>
        <div class="full"><label for="title">Assignment title</label>
             <input id="title" name="title" placeholder="e.g. Database Design Report"></div>
        <div class="full"><label for="url">Submission URL</label>
             <input id="url" name="url" placeholder="https://github.com/username/repo"></div>
        <div class="full"><button type="submit">Submit assignment</button></div>
      </div>
    </form>
  </section>

  <section class="card">
    <h2>Saved submissions <span class="count">({{ submissions|length }})</span></h2>
    {% if submissions %}
    <div style="overflow-x:auto">
    <table>
      <thead><tr><th>Name</th><th>Reg. No.</th><th>Assignment</th><th>Link</th></tr></thead>
      <tbody>
      {% for s in submissions %}
        <tr><td>{{ s.name }}</td><td>{{ s.reg_no }}</td><td>{{ s.title }}</td>
            <td><a href="{{ s.url }}" target="_blank" rel="noopener">{{ s.url }}</a></td></tr>
      {% endfor %}
      </tbody>
    </table>
    </div>
    {% else %}
    <p class="empty">No submissions yet.</p>
    {% endif %}
  </section>
</main>
</body>
</html>
"""

LABELS = {"name": "Name", "reg_no": "Registration number",
          "title": "Assignment title", "url": "Submission URL"}

def is_valid_url(value):
    try:
        p = urlparse(value)
    except ValueError:
        return False
    return p.scheme in ("http", "https") and bool(p.netloc) and " " not in value

def create_app(data_file="submissions.json"):
    app = Flask(__name__)

    def load():
        if not os.path.exists(data_file):
            return []
        with open(data_file) as f:
            return json.load(f)

    def save(items):
        with open(data_file, "w") as f:
            json.dump(items, f, indent=2)

    @app.route("/", methods=["GET", "POST"])
    def index():
        errors, status = [], 200
        if request.method == "POST":
            form = {k: request.form.get(k, "").strip() for k in LABELS}
            for k, label in LABELS.items():
                if not form[k]:
                    errors.append(f"{label} is required")
            if form["url"] and not is_valid_url(form["url"]):
                errors.append("Submission URL is invalid")
            if errors:
                status = 400
            else:
                items = load()
                items.append(form)
                save(items)
        return render_template_string(PAGE, errors=errors, submissions=load()), status

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
