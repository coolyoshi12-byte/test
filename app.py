import streamlit as st
import google.generativeai as genai

# ページの基本設定
st.set_page_config(page_title="AIシフト作成アプリ", page_icon="📅")

st.title("AIシフト作成アプリ 📅")
st.write("従業員の希望と条件を入力すると、Geminiがシフト表のたたき台を作成します。")

# サイドバーでAPIキーを取得
st.sidebar.header("設定")
api_key = st.sidebar.text_input("Gemini APIキー", type="password", help="Google AI Studioで取得したAPIキーを入力してください。")

# メイン画面の入力フォーム
st.subheader("1. 従業員の希望シフト")
staff_info = st.text_area(
    "スタッフの名前と希望を入力してください",
    value="Aさん: 月、水、金の午前のみ\nBさん: 火、木、金\nCさん: 平日いつでも可\nDさん: 月曜日以外いつでも可",
    height=150
)

st.subheader("2. シフトの要件")
requirements = st.text_area(
    "シフトのルールを入力してください",
    value="・来週の月曜日〜金曜日の5日間のシフトを作成してください。\n・各日、必ず2名配置してください。\n・午前と午後で分ける必要はありません。1日単位でアサインしてください。",
    height=150
)

# 実行ボタン
if st.button("✨ シフトを作成する", type="primary"):
    if not api_key:
        st.warning("左側のサイドバーからGemini APIキーを入力してください。")
    elif not staff_info or not requirements:
        st.warning("従業員の希望とシフトの要件を入力してください。")
    else:
        try:
            # Gemini APIの設定
            genai.configure(api_key=api_key)
            # コストと速度のバランスが良い 1.5 Flash を使用
            model = genai.GenerativeModel('gemini-3.1-flash-lite')
            
            # AIへの指示（プロンプト）
            prompt = f"""
            あなたは優秀なシフト管理者です。以下の条件に基づいて、最適なシフト表を作成してください。
            出力はマークダウンのテーブル形式で見やすくし、なぜそのシフトにしたのかの簡単な解説も添えてください。

            【従業員の希望】
            {staff_info}

            【シフト要件】
            {requirements}
            """
            
            with st.spinner("Geminiがシフトを考え中..."):
                response = model.generate_content(prompt)
                
            st.success("シフトの作成が完了しました！")
            st.markdown("### 作成されたシフト表")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
