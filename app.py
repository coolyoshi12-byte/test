import streamlit as st
import google.generativeai as genai
import pandas as pd
import re

# ページの基本設定
st.set_page_config(page_title="AIシフト作成アプリ", page_icon="📅")

st.title("AIシフト作成アプリ (シート自動取得版) 📅")
st.write("スプレッドシート内のシート一覧を自動で読み込みます。")

# サイドバーの設定項目
st.sidebar.header("設定")
api_key = st.sidebar.text_input("Gemini APIキー", type="password", help="Google AI Studioで取得したAPIキーを入力してください。")

# ==========================================
# ⚙️ スプレッドシートのURL（ここにあなたのURLを貼ります）
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-2ExAUt0jaYIIuYSuLTfwfFCZk7M8YdJ8JfswcDKTB0/edit?usp=sharing"
# ==========================================

# スプレッドシート全体をExcel形式として一度に読み込む関数（高速化のためキャッシュを利用）
@st.cache_data(ttl=600) # 10分間は再ダウンロードせずに保存したデータを使う
def load_all_sheets(url):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        sheet_id = match.group(1)
        # Excel形式でダウンロードするURLを生成
        excel_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
        try:
            # sheet_name=None を指定することで、全シートを辞書形式（シート名: データ）で一括読み込み
            return pd.read_excel(excel_url, sheet_name=None)
        except Exception as e:
            st.error(f"データの読み込みに失敗しました: {e}")
            return None
    return None

# データ読み込みの実行
all_sheets_data = load_all_sheets(SHEET_URL)
staff_info_text = ""

if all_sheets_data:
    # 読み込んだデータからシート名のリスト（辞書のキー）を自動で取り出す
    sheet_names = list(all_sheets_data.keys())
    
    # 自動取得したシート名でプルダウンを作成
    selected_sheet = st.sidebar.selectbox("読み込むシートを選択", sheet_names)
    
    # 選択されたシートのデータを取り出す
    df = all_sheets_data[selected_sheet]
    
    st.subheader(f"1. インポートされたデータ（シート: {selected_sheet}）")
    st.dataframe(df)
    
    # 表のデータをテキスト形式に変換
    lines = []
    for index, row in df.iterrows():
        row_text = ", ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
        lines.append(row_text)
    
    staff_info_text = "\n".join(lines)
        
else:
    st.error("スプレッドシートの読み込みに失敗しました。URLを確認してください。")

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
        st.warning("従業員データがありません。")
    elif not requirements:
        st.warning("シフトの要件を入力してください。")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.5-flash')
            
            prompt = f"""
            あなたは優秀なシフト管理者です。以下のスプレッドシートから抽出された従業員の希望データと、シフト要件に基づいて、最適なシフト表を作成してください。
            出力はマークダウンのテーブル形式で見やすくし、なぜそのシフトにしたのかの簡単な解説も添えてください。

            【従業員の希望データ（シート名: {selected_sheet}）】
            {staff_info_text}

            【シフト要件】
            {requirements}
            """
            
            with st.spinner(f"Geminiが「{selected_sheet}」のデータをもとにシフトを考え中..."):
                response = model.generate_content(prompt)
                
            st.success("シフトの作成が完了しました！")
            st.markdown("### 作成されたシフト表")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
