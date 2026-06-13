import streamlit as st
import google.generativeai as genai
import pandas as pd
import re
import urllib.parse # 追加：日本語のシート名をURLで使えるように変換するライブラリ

# ページの基本設定
st.set_page_config(page_title="AIシフト作成アプリ", page_icon="📅")

st.title("AIシフト作成アプリ (複数シート対応版) 📅")
st.write("プルダウンでシートを選んで、シフトのたたき台を作成します。")

# サイドバーの設定項目
st.sidebar.header("設定")
api_key = st.sidebar.text_input("Gemini APIキー", type="password", help="Google AI Studioで取得したAPIキーを入力してください。")

# ==========================================
# ⚙️ スプレッドシートの事前設定エリア
# ==========================================
# 1. あなたのスプレッドシートURLをここに埋め込みます（xxxxxxの部分を書き換えてください）
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-2ExAUt0jaYIIuYSuLTfwfFCZk7M8YdJ8JfswcDKTB0/edit?usp=sharing"

# 2. スプレッドシートの下のタブにある「シート名」を正確にリストアップします
sheet_names = ["11月シフト希望", "12月シフト希望", "1月シフト希望"]

# 3. Streamlitの機能でプルダウン（セレクトボックス）を作成します
selected_sheet = st.sidebar.selectbox("読み込むシートを選択", sheet_names)
# ==========================================

# URLとシート名から、CSVダウンロード用URLを生成する関数
def get_csv_url(url, sheet_name):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        sheet_id = match.group(1)
        # 日本語のシート名をURLに含められる形に変換（URLエンコード）
        encoded_sheet = urllib.parse.quote(sheet_name)
        # 末尾に &sheet=シート名 を追加して特定のシートを狙い撃ちする
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet}"
    return None

# 従業員の希望データを格納する変数
staff_info_text = ""

# アプリ起動時、またはプルダウンが変更された時に自動で読み込み
csv_url = get_csv_url(SHEET_URL, selected_sheet)

if csv_url:
    try:
        # スプレッドシートをインターネット経由で読み込む
        df = pd.read_csv(csv_url)
        
        st.subheader(f"1. インポートされたデータ（シート: {selected_sheet}）")
        st.dataframe(df)
        
        # 表のデータをテキスト形式に変換
        lines = []
        for index, row in df.iterrows():
            row_text = ", ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
            lines.append(row_text)
        
        staff_info_text = "\n".join(lines)
            
    except Exception as e:
        st.error(f"「{selected_sheet}」シートの読み込みに失敗しました。シート名が完全に一致しているか確認してください。エラー: {e}")
else:
    st.error("スプレッドシートのURL形式が正しくありません。")

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
