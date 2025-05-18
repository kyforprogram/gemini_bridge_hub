import os, time, json, logging
import pandas as pd
from google import genai
from google.genai.errors import ServerError
from httpx import HTTPError

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
    logging.basicConfig(level=logging.INFO)
    df = pd.read_excel(input_path)
    src_col = next(c for c in df.columns if '英語' in str(c))
    eng_col, kid_col = 'Gemini(エンジニア1年目)', 'Gemini(小学生)'
    df[eng_col] = ''
    df[kid_col] = ''

    client = genai.Client(api_key=api_key)
    chat_eng = client.chats.create(model=model)
    chat_kid = client.chats.create(model=model)

    def make_prompt(batch, audience):
        joined = "\n---\n".join(batch)
        if audience == 'eng':
            return f"1年目エンジニア向けに要約してください。```{joined}```"
        return f"小学生向けに60字以内でわかりやすく要約してください。```{joined}```"

    def query_gemini(chat, prompt):
        for attempt in range(1, max_retry+1):
            try:
                resp = chat.send_message(prompt)
                return resp.text
            except (ServerError, HTTPError):
                if attempt < max_retry:
                    time.sleep(backoff_base * 2**(attempt-1))
                else:
                    return '[]'

    texts = df[src_col].astype(str).tolist()
    batches = [texts[i:i+chunk] for i in range(0, len(texts), chunk)]
    interval = 60.0 / rpm
    row = 0
    for batch in batches:
        prompt_eng = make_prompt(batch, 'eng')
        prompt_kid = make_prompt(batch, 'kid')
        if verbose_prompt: logging.info(prompt_eng[:200])
        res_eng = json.loads(query_gemini(chat_eng, prompt_eng))
        res_kid = json.loads(query_gemini(chat_kid, prompt_kid))
        for i in range(len(batch)):
            df.at[row+i, eng_col] = res_eng[i].get('eng','')
            df.at[row+i, kid_col] = res_kid[i].get('kid','')
            if verbose_write: logging.info(f"row {row+i}")
        row += len(batch)
        time.sleep(interval)

    out_path = input_path.replace('.xlsx','_translated.xlsx')
    df.to_excel(out_path, index=False)
    return out_path

