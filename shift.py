import streamlit as st
import google.generativeai as genai
import os

# APIキーの設定 (Streamlit Secrets または ローカル環境変数から取得)
# ※絶対にコード内に直接APIキーを書き込まないでください
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not api_key:
    st.error("APIキーが設定されていません。")
    st.stop()

genai.configure(api_key=api_key)

st.title("Gemini シフト自動生成アプリ")

# UIコンポーネント
staff_names = st.text_input("スタッフの名前（カンマ区切り）", "Aさん, Bさん, Cさん")
conditions = st.text_area("シフトの制約・条件", "・1日の必要人数は2名\n・Aさんは水曜休み希望\n・Bさんは土日出勤可能")

if st.button("シフトを生成"):
    with st.spinner('シフトを作成中です...'):
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Geminiへの指示（プロンプト）
        prompt = f"""
        あなたは優秀なシフト管理者です。以下の条件を満たす1週間のシフト表を作成してください。

        【スタッフ】{staff_names}
        【条件】{conditions}

        出力は、月曜日から日曜日までのスケジュールが分かるMarkdownの表形式のみで出力してください。
        """

        response = model.generate_content(prompt)
        st.markdown(response.text)
