# backend/translation_app.py
from flask import (
    Flask, request, jsonify,
    send_file, send_from_directory, redirect
)
from werkzeug.utils import secure_filename
from tasks import translate_task
import os, json

app = Flask(__name__)
UPLOAD = 'uploads'
os.makedirs(UPLOAD, exist_ok=True)

# 静的 UI を配信
@app.route('/', methods=['GET'])
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/frontend/<path:filename>')
def frontend_static(filename):
    return send_from_directory('frontend', filename)

# POST のみ許可
@app.route('/api/translate', methods=['POST'])
def api_translate():
    f = request.files.get('file')
    params = request.form.to_dict()
    if not f or 'api_key' not in params:
        return jsonify(error='file and api_key required'), 400

    filename = secure_filename(f.filename)
    path = os.path.join(UPLOAD, filename)
    f.save(path)
    # 型変換
    for k in ['rpm','chunk','max_retry','backoff_base']:
        if k in params:
            try:
                params[k] = int(params[k])
            except ValueError:
                return jsonify(error=f'Invalid integer for {k}'), 400
    for k in ['verbose_prompt','verbose_resp','verbose_write']:
        params[k] = params.get(k,'false').lower()=='true'
    params['api_key'] = params['api_key']

    job = translate_task.delay(path, params)
    return jsonify(job_id=job.id), 202

# 万が一 GET でたたかれたらルートへリダイレクト
@app.route('/api/translate', methods=['GET'])
def api_translate_get():
    return redirect('/')

@app.route('/api/status/<job_id>', methods=['GET'])
def api_status(job_id):
    res = translate_task.AsyncResult(job_id)
    payload = {'status': res.status}
    if res.status == 'FAILURE':
        payload['error'] = str(res.result)
    return jsonify(payload)

@app.route('/api/result/<job_id>', methods=['GET'])
def api_result(job_id):
    res = translate_task.AsyncResult(job_id)
    if res.status == 'SUCCESS':
        return send_file(res.get(), as_attachment=True)
    return jsonify(error='processing'), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

