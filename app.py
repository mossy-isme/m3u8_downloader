from flask import Flask, request, send_file
import subprocess
import os
import tempfile
import zipfile

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download_m3u8():
    links = request.json.get('links', [])
    if not links:
        return {'error': 'No links provided'}, 400

    temp_dir = tempfile.mkdtemp()
    output_files = []

    for i, link in enumerate(links):
        output_path = os.path.join(temp_dir, f'video_{i+1}.mp4')
        command = ['ffmpeg', '-i', link, '-c', 'copy', output_path]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        output_files.append(output_path)

    zip_path = os.path.join(temp_dir, 'videos.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in output_files:
            zipf.write(file, os.path.basename(file))

    return send_file(zip_path, as_attachment=True, download_name='videos.zip')

if __name__ == '__main__':
    app.run(debug=True)
