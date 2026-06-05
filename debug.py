import streamlit as st
import google.generativeai as genai
import os

api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
genai.configure(api_key=api_key)

st.title("利用可能なGeminiモデル一覧の確認")

try:
    # generateContent（テキスト生成）に対応しているモデルのみを取得
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    st.success("APIキーは正常に認証されました！")
    st.write("▼ このAPIキーで指定可能なモデル名一覧 ▼")
    for model_name in models:
        st.code(model_name.replace("models/", "")) # 'models/'の部分を省いて表示
        
except Exception as e:
    st.error(f"モデル一覧の取得中にエラーが発生しました: {e}")
