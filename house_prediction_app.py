from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from urllib.parse import parse_qs, urlparse


HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", "8000"))

FEATURES = [
    "MedInc",
    "HouseAge",
    "AveRooms",
    "AveBedrms",
    "Population",
    "AveOccup",
    "Latitude",
    "Longitude",
]

FEATURE_LABELS = {
    "MedInc": "Median income",
    "HouseAge": "House age",
    "AveRooms": "Average rooms",
    "AveBedrms": "Average bedrooms",
    "Population": "Population",
    "AveOccup": "Average occupants",
    "Latitude": "Latitude",
    "Longitude": "Longitude",
}

FEATURE_HELP = {
    "MedInc": "Income in California Housing dataset units, e.g. 4.5.",
    "HouseAge": "Median age of houses in the block.",
    "AveRooms": "Average number of rooms per household.",
    "AveBedrms": "Average number of bedrooms per household.",
    "Population": "Block group population.",
    "AveOccup": "Average number of occupants per household.",
    "Latitude": "California latitude, usually 32.54 to 41.95.",
    "Longitude": "California longitude, usually -124.35 to -114.31.",
}

DEFAULTS = {
    "MedInc": 4.5,
    "HouseAge": 20,
    "AveRooms": 5.5,
    "AveBedrms": 1.0,
    "Population": 900,
    "AveOccup": 3.0,
    "Latitude": 34.05,
    "Longitude": -118.25,
}

SAMPLES = [
    {
        "name": "Los Angeles sample",
        "values": DEFAULTS,
    },
    {
        "name": "Bay Area sample",
        "values": {
            "MedInc": 8.0,
            "HouseAge": 10,
            "AveRooms": 7.0,
            "AveBedrms": 1.1,
            "Population": 650,
            "AveOccup": 2.5,
            "Latitude": 37.77,
            "Longitude": -122.42,
        },
    },
    {
        "name": "Central Valley sample",
        "values": {
            "MedInc": 2.0,
            "HouseAge": 35,
            "AveRooms": 4.0,
            "AveBedrms": 1.2,
            "Population": 1500,
            "AveOccup": 4.0,
            "Latitude": 36.75,
            "Longitude": -119.77,
        },
    },
]

# LinearRegression coefficients for the notebook's California Housing setup.
# The original target was converted from 100,000-dollar units to USD.
INTERCEPT = -3702322.35
COEFFICIENTS = {
    "MedInc": 44867.4334,
    "HouseAge": 972.9327,
    "AveRooms": -12332.1072,
    "AveBedrms": 78314.8454,
    "Population": -0.202528,
    "AveOccup": -353.4414,
    "Latitude": -41979.8572,
    "Longitude": -43370.1084,
}

MODEL_METRICS = {
    "MAE": 53320.01,
    "RMSE": 74558.14,
    "R2": 0.576,
}


def predict_price(values):
    prediction = INTERCEPT
    for feature in FEATURES:
        prediction += values[feature] * COEFFICIENTS[feature]
    return round(prediction, 2)


def parse_values(payload):
    values = {}
    errors = {}
    for feature in FEATURES:
        raw = payload.get(feature)
        if isinstance(raw, list):
            raw = raw[0] if raw else ""
        try:
            values[feature] = float(raw)
        except (TypeError, ValueError):
            errors[feature] = f"{FEATURE_LABELS[feature]} must be a number."
    return values, errors


def currency(amount):
    return f"${amount:,.2f}"


def render_form_fields():
    fields = []
    for feature in FEATURES:
        step = "0.01" if feature not in {"HouseAge", "Population"} else "1"
        fields.append(
            f"""
            <label class="field">
              <span>{FEATURE_LABELS[feature]}</span>
              <input name="{feature}" type="number" step="{step}" value="{DEFAULTS[feature]}" required>
              <small>{FEATURE_HELP[feature]}</small>
            </label>
            """
        )
    return "\n".join(fields)


def render_samples():
    buttons = []
    for sample in SAMPLES:
        data = json.dumps(sample["values"])
        buttons.append(
            f'<button type="button" class="sample-button" data-sample=\'{data}\'>{sample["name"]}</button>'
        )
    return "\n".join(buttons)


def render_html(result=None, values=None, errors=None):
    values = values or DEFAULTS
    result_block = ""
    if errors:
        items = "".join(f"<li>{message}</li>" for message in errors.values())
        result_block = f'<div class="notice error"><strong>Check the inputs</strong><ul>{items}</ul></div>'
    elif result is not None:
        result_block = f"""
        <section class="result" aria-live="polite">
          <p>Predicted median house value</p>
          <strong>{currency(result)}</strong>
          <span>Linear regression estimate from the California Housing features.</span>
        </section>
        """

    fields = render_form_fields()
    samples = render_samples()
    metrics = "".join(
        f"<div><span>{name}</span><strong>{value:,.2f}</strong></div>"
        for name, value in MODEL_METRICS.items()
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>House Price Prediction</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #20252b;
      --muted: #667085;
      --line: #d7dde5;
      --panel: #f7f9fb;
      --accent: #1c6b5d;
      --accent-2: #b94e48;
      --focus: #c58b1f;
      --white: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: var(--white);
    }}
    header {{
      padding: 28px clamp(18px, 4vw, 56px) 18px;
      border-bottom: 1px solid var(--line);
      background: #f1f5f2;
    }}
    header h1 {{
      margin: 0 0 8px;
      font-size: clamp(28px, 4vw, 44px);
      line-height: 1.05;
      letter-spacing: 0;
    }}
    header p {{
      max-width: 760px;
      margin: 0;
      color: #46535f;
      line-height: 1.55;
    }}
    main {{
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.65fr);
      gap: 28px;
      padding: 28px clamp(18px, 4vw, 56px) 44px;
    }}
    form {{
      display: grid;
      gap: 20px;
      align-content: start;
    }}
    .inputs {{
      display: grid;
      grid-template-columns: repeat(2, minmax(220px, 1fr));
      gap: 16px;
    }}
    .field {{
      display: grid;
      gap: 7px;
      min-width: 0;
    }}
    .field span {{
      font-weight: 700;
      font-size: 14px;
    }}
    .field input {{
      width: 100%;
      min-height: 44px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 12px;
      font: inherit;
      color: var(--ink);
      background: var(--white);
    }}
    .field input:focus {{
      outline: 3px solid color-mix(in srgb, var(--focus) 32%, transparent);
      border-color: var(--focus);
    }}
    .field small {{
      color: var(--muted);
      line-height: 1.35;
    }}
    .actions {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      align-items: center;
    }}
    button {{
      border: 1px solid var(--accent);
      border-radius: 6px;
      cursor: pointer;
      font: inherit;
      font-weight: 700;
    }}
    .primary {{
      min-height: 46px;
      padding: 0 20px;
      color: var(--white);
      background: var(--accent);
    }}
    .sample-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .sample-button {{
      min-height: 38px;
      padding: 0 12px;
      color: var(--accent);
      background: var(--white);
    }}
    aside {{
      display: grid;
      gap: 18px;
      align-content: start;
    }}
    .result {{
      padding: 20px;
      border-radius: 8px;
      color: var(--white);
      background: var(--accent);
    }}
    .result p, .result span {{
      margin: 0;
      color: #e7f2ef;
    }}
    .result strong {{
      display: block;
      margin: 8px 0;
      font-size: clamp(30px, 5vw, 46px);
      line-height: 1.05;
      letter-spacing: 0;
      overflow-wrap: anywhere;
    }}
    .panel {{
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    .panel h2 {{
      margin: 0 0 12px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }}
    .metrics div {{
      min-width: 0;
      padding: 10px;
      border-left: 4px solid var(--accent-2);
      background: var(--white);
    }}
    .metrics span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }}
    .metrics strong {{
      display: block;
      margin-top: 4px;
      font-size: 15px;
      overflow-wrap: anywhere;
    }}
    canvas {{
      width: 100%;
      height: 180px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--white);
    }}
    .notice {{
      padding: 14px 16px;
      border-radius: 8px;
      line-height: 1.45;
    }}
    .error {{
      color: #7c241f;
      background: #fff0ee;
      border: 1px solid #efb1aa;
    }}
    .error ul {{
      margin: 8px 0 0;
      padding-left: 20px;
    }}
    footer {{
      padding: 16px clamp(18px, 4vw, 56px);
      color: var(--muted);
      border-top: 1px solid var(--line);
      font-size: 13px;
    }}
    @media (max-width: 840px) {{
      main {{
        grid-template-columns: 1fr;
      }}
      .inputs {{
        grid-template-columns: 1fr;
      }}
      .metrics {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>House Price Prediction</h1>
    <p>Enter the same eight California Housing features from the notebook and get an estimated median house value in US dollars.</p>
  </header>
  <main>
    <form method="post" action="/predict">
      <div class="inputs">
        {fields}
      </div>
      <div class="actions">
        <button class="primary" type="submit">Predict price</button>
        <div class="sample-row" aria-label="Sample inputs">
          {samples}
        </div>
      </div>
    </form>
    <aside>
      {result_block}
      <section class="panel">
        <h2>Model performance</h2>
        <div class="metrics">{metrics}</div>
      </section>
      <section class="panel">
        <h2>Location preview</h2>
        <canvas id="mapCanvas" width="560" height="280" aria-label="California coordinate preview"></canvas>
      </section>
    </aside>
  </main>
  <footer>
    Built from Oseagwina_COSC22404_Ass1.ipynb. Prediction endpoint: POST /api/predict with JSON feature values.
  </footer>
  <script>
    const samples = document.querySelectorAll(".sample-button");
    const form = document.querySelector("form");
    const canvas = document.getElementById("mapCanvas");
    const ctx = canvas.getContext("2d");

    function setValues(values) {{
      for (const [key, value] of Object.entries(values)) {{
        const input = form.elements[key];
        if (input) input.value = value;
      }}
      drawLocation();
    }}

    function drawLocation() {{
      const lat = Number(form.elements.Latitude.value || 34.05);
      const lon = Number(form.elements.Longitude.value || -118.25);
      const minLat = 32.54, maxLat = 41.95, minLon = -124.35, maxLon = -114.31;
      const x = ((lon - minLon) / (maxLon - minLon)) * canvas.width;
      const y = canvas.height - ((lat - minLat) / (maxLat - minLat)) * canvas.height;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#f7f9fb";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.strokeStyle = "#c8d0da";
      ctx.lineWidth = 1;
      for (let i = 1; i < 5; i++) {{
        ctx.beginPath();
        ctx.moveTo((canvas.width / 5) * i, 0);
        ctx.lineTo((canvas.width / 5) * i, canvas.height);
        ctx.moveTo(0, (canvas.height / 5) * i);
        ctx.lineTo(canvas.width, (canvas.height / 5) * i);
        ctx.stroke();
      }}
      ctx.fillStyle = "#1c6b5d";
      ctx.beginPath();
      ctx.arc(Math.max(8, Math.min(canvas.width - 8, x)), Math.max(8, Math.min(canvas.height - 8, y)), 8, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#20252b";
      ctx.font = "14px Arial";
      ctx.fillText(`Lat ${{lat.toFixed(2)}}, Lon ${{lon.toFixed(2)}}`, 14, 24);
    }}

    samples.forEach((button) => {{
      button.addEventListener("click", () => setValues(JSON.parse(button.dataset.sample)));
    }});
    form.querySelectorAll("input").forEach((input) => input.addEventListener("input", drawLocation));
    drawLocation();
  </script>
</body>
</html>"""


class HousePredictionHandler(BaseHTTPRequestHandler):
    def send_text(self, status, body, content_type="text/html; charset=utf-8"):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def send_json(self, status, payload):
        self.send_text(status, json.dumps(payload, indent=2), "application/json; charset=utf-8")

    def read_payload(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length).decode("utf-8")
        content_type = self.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return json.loads(raw or "{}")
        return parse_qs(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self.send_text(200, render_html())
        elif path == "/health":
            self.send_json(200, {"status": "ok"})
        else:
            self.send_text(404, "Not found", "text/plain; charset=utf-8")

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            payload = self.read_payload()
            values, errors = parse_values(payload)
        except json.JSONDecodeError:
            self.send_json(400, {"errors": {"body": "Invalid JSON body."}})
            return

        if errors:
            if path == "/api/predict":
                self.send_json(400, {"errors": errors})
            else:
                self.send_text(400, render_html(errors=errors))
            return

        prediction = predict_price(values)
        if path == "/api/predict":
            self.send_json(200, {"prediction_usd": prediction, "inputs": values})
        elif path == "/predict":
            self.send_text(200, render_html(result=prediction, values=values))
        else:
            self.send_text(404, "Not found", "text/plain; charset=utf-8")

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


def main():
    server = ThreadingHTTPServer((HOST, PORT), HousePredictionHandler)
    print(f"House Prediction app running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
