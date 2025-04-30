from flask import Flask, request, render_template, jsonify
import requests
import datetime

app = Flask(__name__)

# Supabase Configurations
SUPABASE_URL = "https://stvavzacncijxinqbzhv.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN0dmF2emFjbmNpanhpbnFiemh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI0Njg2NTMsImV4cCI6MjA1ODA0NDY1M30.RIqxh5HHfIbeXe4sZLTOc6AfPHq_6EPTGnpMzNXxUdQ"
SUPABASE_TABLE = "data"

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

@app.route('/')
def dashboard():
    try:
        res = requests.get(
            f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?order=time_stamp.desc&limit=20",
            headers=HEADERS
        )
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                data.reverse()
            else:
                print("Unexpected data format from Supabase")
                data = []
            return render_template("dashboard.html", records=data)
        else:
            return jsonify({"error": "Failed to fetch data from Supabase"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/submit', methods=["GET", "POST"])
def submit():
    try:
        incoming = request.json
        # Validate required fields
        if "temperature" not in incoming or "moisture" not in incoming or "pump_status" not in incoming:
            return jsonify({"error": "Missing required data"}), 400
        
        # Add timestamp
        from datetime import datetime, timezone

        incoming["time_stamp"] = datetime.now(timezone.utc).isoformat()

        
        # Post the data to Supabase
        res = requests.post(
            f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
            headers=HEADERS,
            json=[incoming]
        )

        if res.status_code in [200, 201]:
            return jsonify({"status": "ok"})
        else:
            return jsonify({"error": "Failed to insert data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


