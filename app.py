from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
import csv
from datetime import datetime
import os

import job_search_module as jobs

app = Flask(__name__)
CORS(app)  # allow all origins by default; tighten later if you want

@app.route("/")
def root():
    return jsonify({
        "name": "ToolHouzz Job Search API",
        "status": "running",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "search (POST)": "/search"
        }
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/search", methods=["POST"])
def search():
    """
    Body JSON:
    {
      "job_title": "Business Analyst",
      "city": "Toronto",
      "country": "Canada",
      "job_age": 15   # (days) optional
    }
    Returns: CSV file with results (at minimum: smart search links for major sites).
    """
    try:
        payload = request.get_json(force=True, silent=False) or {}
        job_title = (payload.get("job_title") or "").strip()
        city = (payload.get("city") or "").strip()
        country = (payload.get("country") or "").strip()
        job_age = int(payload.get("job_age") or 15)

        if not job_title:
            return jsonify({"error": "job_title is required"}), 400
        if not country and not city:
            return jsonify({"error": "Provide at least country or city"}), 400

        location = f"{city}, {country}".strip(", ").strip()

        # Run the aggregator (links + light scraping-safe metadata)
        results = jobs.search_all_portals(job_title=job_title,
                                          location=location,
                                          job_age=job_age)

        # Always return a CSV (even if only search links)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Date",
            "Source",
            "Type",
            "Company",
            "Job Title",
            "Location",
            "URL",
            "Notes"
        ])

        today = datetime.utcnow().strftime("%Y-%m-%d")
        for row in results:
            writer.writerow([
                row.get("date") or today,
                row.get("source") or "",
                row.get("type") or "link",
                row.get("company") or "",
                row.get("title") or job_title,
                row.get("location") or location,
                row.get("url") or "",
                row.get("notes") or ""
            ])

        mem = io.BytesIO(output.getvalue().encode("utf-8"))
        mem.seek(0)

        filename = f"jobs_{job_title.replace(' ', '_')}_{today}.csv"
        return send_file(mem,
                         mimetype="text/csv",
                         as_attachment=True,
                         download_name=filename)

    except Exception as e:
        # Print server-side for Render logs
        print("[/search] ERROR:", repr(e))
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
