from flask_cors import CORS
from flask import Flask, request, jsonify, send_file
import os, tempfile, subprocess, zipfile, threading, uuid, time

app = Flask(__name__)
jobs = {}
CORS(app)
def download_job(job_id, links):
    temp_dir = tempfile.mkdtemp()
    output_files = []

    jobs[job_id] = {"status": "running", "progress": 0, "total": len(links), "zip_path": None}

    for i, link in enumerate(links):
        output_path = os.path.join(temp_dir, f'video_{i+1}.mp4')
        command = ['ffmpeg', '-i', link, '-c', 'copy', output_path]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        output_files.append(output_path)
        jobs[job_id]["progress"] = i + 1

    zip_path = os.path.join(temp_dir, 'videos.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in output_files:
            zipf.write(file, os.path.basename(file))

    jobs[job_id]["status"] = "complete"
    jobs[job_id]["zip_path"] = zip_path

@app.route('/start', methods=['POST'])
def start_download():
    links = request.json.get('links', [])
    if not links:
        return jsonify({"error": "No links provided"}), 400

    job_id = str(uuid.uuid4())
    threading.Thread(target=download_job, args=(job_id, links)).start()
    return jsonify({"job_id": job_id})

@app.route('/status/<job_id>')
def check_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Invalid job ID"}), 404
    return jsonify(job)

@app.route('/download/<job_id>')
def get_zip(job_id):
    job = jobs.get(job_id)
    if job and job["status"] == "complete":
        return send_file(job["zip_path"], as_attachment=True, download_name="videos.zip")
    return jsonify({"error": "Not ready"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, threaded=True)
