from flask import Flask, request, jsonify, send_file, send_from_directory
from tasks import translate_task
import os, json

app = Flask(__name__)
UPLOAD = 'uploads'
os.makedirs(UPLOAD, exist_ok=True)

# 静的ファイル配信
@app.route('/frontend/<path:filename>')
def frontend_static(filename):
    return send_from_directory('frontend', filename)

# 翻訳ジョブ受付
@app.route('/api/translate', methods=['POST'])
def api_translate():
    f = request.files.get('file')
    params = request.form.to_dict()
    if not f or 'api_key' not in params:
        return jsonify(error='file and api_key required'), 400

    path = os.path.join(UPLOAD, f.filename)
    f.save(path)

    # 数値型・真偽値型への変換
    for k in ['rpm', 'chunk', 'max_retry', 'backoff_base']:
        if k in params:
            try:
                params[k] = int(params[k])
            except ValueError:
                return jsonify(error=f'invalid integer for {k}'), 400
    for k in ['verbose_prompt', 'verbose_resp', 'verbose_write']:
        params[k] = params.get(k, 'false').lower() == 'true'
    params['api_key'] = params['api_key']

    job = translate_task.delay(path, params)
    return jsonify(job_id=job.id), 202

# ジョブステータス取得
@app.route('/api/status/<job_id>')
def api_status(job_id):
    res = translate_task.AsyncResult(job_id)
    payload = {'status': res.status}
    if res.status == 'FAILURE':
        payload['error'] = str(res.result)
    return jsonify(payload)

# 結果ファイル取得
@app.route('/api/result/<job_id>')
def api_result(job_id):
    res = translate_task.AsyncResult(job_id)
    if res.status == 'SUCCESS':
        return send_file(res.get(), as_attachment=True)
    return jsonify(error='processing'), 202

if __name__ == '__main__':
    # 本番は Gunicorn 等で起動する想定ですが、開発用にこのままでもOK
    app.run(host='0.0.0.0', port=5000)

