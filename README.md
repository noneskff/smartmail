# SmartMail — Render deployment starter

SmartMail is a Flask web app with a browser frontend, prediction API, and prediction history. It is configured for Render deployment using PostgreSQL. For local development without `DATABASE_URL`, it falls back to SQLite.

> **Important:** The current classifier is only a keyword-based demonstration. It is NOT a trained machine-learning model and must not be used for real email-security decisions. Step 2 will add a trained TF-IDF + Multinomial Naive Bayes model.

## Deploy to Render (no local running required)

1. Extract this ZIP.
2. Create a new **public GitHub repository** named `smartmail`.
3. Upload the contents of the `smartmail_project` folder to the repository root. Make sure `render.yaml`, `app.py`, `requirements.txt`, `templates/`, and `static/` are at the root level—not inside another nested folder.
4. Sign in to [Render](https://render.com/) and connect your GitHub account.
5. In Render, choose **New → Blueprint** and select the `smartmail` GitHub repository.
6. Render will read `render.yaml` and show the web service and PostgreSQL database. Review the plan and click **Apply**.
7. Wait for the deployment to finish. Open the `smartmail` web service and visit its `onrender.com` URL.
8. Test `/health`, the message checker, and prediction history.

The Blueprint links the app's `DATABASE_URL` to the managed PostgreSQL database. Do not paste database credentials into source code or commit a `.env` file.

## Files

- `app.py` — Flask routes, prediction demo, and database access.
- `templates/index.html` — frontend page.
- `static/style.css` — styles.
- `static/app.js` — browser-side API calls and history display.
- `render.yaml` — Render web service + PostgreSQL Blueprint configuration.
- `requirements.txt` — Python dependencies, including Gunicorn and psycopg.

## Local development (optional)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000.

## Troubleshooting

- If Render cannot find `app.py`, check that the repository root contains `app.py` and `render.yaml` directly.
- If deployment fails, open the Render service's **Logs** and inspect the first error.
- If `/health` does not return `{"status":"ok",...}`, check the deployment logs and database provisioning status.
- Render free services may spin down when idle. The first request after inactivity can take some time.
- Check Render's current pricing and free-database retention limits before relying on the service for long-term data storage.
