from flask import Flask, request, jsonify, send_file
from tasks import translate_task
import os, json

app = Flask(__name__)
UPLOAD = 'uploads'
os.makedirs(UPLOAD, exist_ok=True)

@app.route('/frontend/<path:filename>')
def frontend_static(filename):
    return send_from_directory('frontend', filename)

@app.route('/api/translate', methods=['POST'])
def api_translate():
    f = request.files.get('file')
    params = request.form.to_dict()
    if not f or 'api_key' not in params:
        return jsonify(error='file and api_key required'), 400
    path = os.path.join(UPLOAD, f.filename)
    f.save(path)
    for k in ['rpm','chunk','max_retry','backoff_base']:
        if k in params: params[k] = int(params[k])
    for k in ['verbose_prompt','verbose_resp','verbose_write']:
        params[k] = params.get(k,'false').lower()=='true'
    params['api_key'] = params['api_key']
    job = translate_task.delay(path, params)
    return jsonify(job_id=job.id), 202

@app.route('/api/status/<job_id>')
def api_status(job_id):
    res = translate_task.AsyncResult(job_id)
    return jsonify(status=res.status)

@app.route('/api/result/<job_id>')
def api_result(job_id):
    res = translate_task.AsyncResult(job_id)
    if res.status == 'SUCCESS':
        return send_file(res.get(), as_attachment=True)
    return jsonify(error='processing'), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

