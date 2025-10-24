from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import random
import os

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://no_1_hub_user:p1DMNa1Qij5e0uw4yDUpzNDFUJ2OcUbb@dpg-d3tj9l6uk2gs73d6pd4g-a.oregon-postgres.render.com/no_1_hub")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    job_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
""")
conn.commit()

@app.route("/", methods=["GET"])
def home():
    cur.execute("SELECT job_id FROM jobs ORDER BY id ASC;")
    rows = cur.fetchall()
    data = [r[0] for r in rows]
    return jsonify({"all": data if data else ["nil"]})

@app.route("/job", methods=["POST"])
def add_job():
    data = request.get_json()
    job_id = data.get("jobId")
    if not job_id:
        return jsonify({"error": "Missing jobId"}), 400
    try:
        cur.execute("INSERT INTO jobs (job_id) VALUES (%s) ON CONFLICT (job_id) DO NOTHING;", (job_id,))
        conn.commit()
        cur.execute("SELECT job_id FROM jobs ORDER BY id ASC;")
        rows = cur.fetchall()
        all_jobs = [r[0] for r in rows]
        return jsonify({"success": True, "jobId": job_id, "all": all_jobs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/jobs", methods=["GET"])
def get_jobs():
    cur.execute("SELECT job_id FROM jobs ORDER BY id ASC;")
    rows = cur.fetchall()
    return jsonify({"all": [r[0] for r in rows] if rows else ["nil"]})

@app.route("/latest", methods=["GET"])
def get_latest():
    cur.execute("SELECT job_id FROM jobs ORDER BY id DESC LIMIT 1;")
    row = cur.fetchone()
    return jsonify({"latest": row[0] if row else "nil"})

@app.route("/jobid", methods=["GET"])
def get_random_job():
    cur.execute("SELECT id, job_id FROM jobs;")
    rows = cur.fetchall()
    if not rows:
        return jsonify({"jobId": "nil"})
    job = random.choice(rows)
    cur.execute("DELETE FROM jobs WHERE id = %s;", (job[0],))
    conn.commit()
    return jsonify({"jobId": job[1]})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
