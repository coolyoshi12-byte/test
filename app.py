import streamlit as st
import google.generativeai as genai
import pandas as pd
import re

# ページの基本設定
st.set_page_config(page_title="AIシフト作成アプリ (Sheet連携版)", page_icon="📅")

st.title("AIシフト作成アプリ (Googleシーツ連携版) 📅")
st.write("Googleフォームの回答（スプレッドシート）を読み込んで、自動でシフトのたたき台を作成します。")

# サイドバーの設定項目
st.sidebar.header("設定")
api_key = st.sidebar.text_input("Gemini APIキー", type="password", help="Google AI Studioで取得したAPIキーを入力してください。")

# スプレッドシートのURL入力欄をサイドバーに追加
sheet_url = st.sidebar.text_input(
    "GoogleスプレッドシートのURL", 
    help="「リンクを知っている全員が閲覧可能」に設定したスプレッドシートのURLを貼り付けてください。"
)

# スプレッドシートのURLから、プログラムが読み込める「CSVダウンロード用URL」に変換する関数
def get_csv_url(url):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        sheet_id = match.group(1)
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    return None

# 従業員の希望データを格納する変数
staff_info_text = ""

# URLが入力されたら自動で読み込みを開始
if sheet_url:
    csv_url = get_csv_url(sheet_url)
    if csv_url:
        try:
            # スプレッドシートをインターネット経由で読み込む
            df = pd.read_csv(csv_url)
            
            st.subheader("1. インポートされた従業員データ")
            # アプリ画面に綺麗な表として表示
            st.dataframe(df)
            
            # 【重要】表のデータを、Geminiが理解しやすい「テキスト形式」に自動変換する
            # 例：「タイムスタンプ: 2026/06/06, 名前: Aさん, 希望曜日: 月水金」のような文字列を作ります
            lines = []
            for index, row in df.iterrows():
                # 空白のセルを除外して、列名と中身をペアにする
                row_text = ", ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                lines.append(row_text)
            
            staff_info_text = "\n".join(lines)
            
            # どんなテキストに変身したかを確認できる隠しメニュー（確認用）
            with st.expander("Geminiに送信されるテキストデータ（確認用）"):
                st.text_area("整形されたデータ", value=staff_info_text, height=150, disabled=True)
                
        except Exception as e:
            st.error(f"スプレッドシートの読み込みに失敗しました。URLや共有設定を確認してください。エラー: {e}")
    else:
        st.error("正しいGoogleスプレッドシートのURLを入力してください。")
else:
    st.info("👈 左側のサイドバーに「GoogleスプレッドシートのURL」を入力すると、ここにデータがインポートされます。")

# シフトの要件入力
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
    elif not staff_info_text:
        st.warning("スプレッドシートから従業員のデータが正常に読み込まれていません。")
    elif not requirements:
        st.warning("シフトの要件を入力してください。")
    else:
        try:
            # Gemini APIの設定とモデルの呼び出し
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.1-flash-lite')
            
            # プロンプト（AIへの指示文）の組み立て
            prompt = f"""
            あなたは優秀なシフト管理者です。以下のスプレッドシートから抽出された従業員の希望データと、シフト要件に基づいて、最適なシフト表を作成してください。
            出力はマークダウンのテーブル形式で見やすくし、なぜそのシフトにしたのかの簡単な解説も添えてください。

            【従業員の希望データ（スプレッドシートより自動インポート）】
            {staff_info_text}

            【シフト要件】
            {requirements}
            """
            
            with st.spinner("Geminiがインポートデータをもとにシフトを考え中..."):
                response = model.generate_content(prompt)
                
            st.success("シフトの作成が完了しました！")
            st.markdown("### 作成されたシフト表")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
