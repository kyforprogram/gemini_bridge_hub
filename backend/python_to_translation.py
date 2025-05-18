import os, time, logging
import pandas as pd
from google import genai
from google.genai.errors import ServerError
from httpx import HTTPError

# ログ出力設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

def run_translation(
    input_path: str,
    api_key: str,
    rpm: int = 15,
    chunk: int = 50,
    model: str = "gemini-2.0-flash",
    max_retry: int = 7,
    backoff_base: int = 5,
    verbose_prompt: bool = False,
    verbose_resp: bool = False,
    verbose_write: bool = False
) -> str:
    # Excel読み込み
    df = pd.read_excel(input_path)
    # 「英語」を含むカラムを探す
    src_col = next(c for c in df.columns if '英語' in str(c))
    eng_col, kid_col = 'Gemini(エンジニア1年目)', 'Gemini(小学生)'
    df[eng_col] = ''
    df[kid_col] = ''

    client = genai.Client(api_key=api_key)
    chat_eng = client.chats.create(model=model)
    chat_kid = client.chats.create(model=model)

    def prompt_for(text: str, audience: str) -> str:
        if audience == 'eng':
            return f"1年目エンジニア向けに要約してください。```{text}```"
        return f"小学生向けに60字以内でわかりやすく要約してください。```{text}```"

    # レート制御
    interval = 60.0 / rpm

    for idx, text in enumerate(df[src_col].astype(str)):
        # プロンプト作成
        p_eng = prompt_for(text, 'eng')
        p_kid = prompt_for(text, 'kid')
        if verbose_prompt:
            logging.info(f"[{idx}] PROMPT ENG: {p_eng}")
            logging.info(f"[{idx}] PROMPT KID: {p_kid}")

        def safe_query(chat, prompt: str) -> str:
            for attempt in range(1, max_retry+1):
                try:
                    resp = chat.send_message(prompt)
                    return resp.text
                except (ServerError, HTTPError) as e:
                    logging.warning(f"Attempt {attempt} failed: {e}")
                    if attempt < max_retry:
                        time.sleep(backoff_base * 2**(attempt-1))
                    else:
                        return ''

        # API呼び出し
        res_eng = safe_query(chat_eng, p_eng)
        res_kid = safe_query(chat_kid, p_kid)
        if verbose_resp:
            logging.info(f"[{idx}] RESPONSE ENG: {res_eng}")
            logging.info(f"[{idx}] RESPONSE KID: {res_kid}")

        # DataFrameに書き込み
        df.at[idx, eng_col] = res_eng
        df.at[idx, kid_col] = res_kid
        if verbose_write:
            logging.info(f"[{idx}] WROTE ROW")
        time.sleep(interval)

    # 結果を別ファイルで出力
    out_path = input_path.replace('.xlsx', '_translated.xlsx')
    df.to_excel(out_path, index=False)
    return out_path

