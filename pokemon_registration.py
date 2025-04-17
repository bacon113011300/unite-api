import streamlit as st
from models import DataManager

# Page config
st.set_page_config(
    page_title="ポケモン登録 - ポケモンユナイト大会分析ツール",
    page_icon="🐾",
    layout="wide"
)

# Initialize session state
DataManager.initialize_session_state()

st.title("ポケモン登録")
st.markdown("試合で使用するポケモンを登録します。")

# Form for Pokémon registration
col1, col2 = st.columns([1, 2])

with col1:
    with st.form("pokemon_registration_form"):
        st.subheader("新規ポケモン追加")
        
        pokemon_name = st.text_input("ポケモン名")
        
        # Submit button
        submit_button = st.form_submit_button("ポケモンを登録")
        
        # Process form submission
        if submit_button:
            if not pokemon_name:
                st.error("ポケモン名を入力してください。")
            else:
                # Add pokemon to session state
                success = DataManager.add_pokemon(pokemon_name)
                
                if success:
                    st.success(f"ポケモン「{pokemon_name}」が正常に登録されました！")
                    st.rerun()
                else:
                    st.error(f"ポケモン「{pokemon_name}」は既に存在します。")

# Display registered Pokémon
with col2:
    st.subheader("登録済みポケモン")
    
    if st.session_state.pokemons:
        # Display in a grid layout
        num_cols = 3
        cols = st.columns(num_cols)
        
        for i, pokemon in enumerate(sorted(st.session_state.pokemons, key=lambda x: x.name)):
            with cols[i % num_cols]:
                st.write(f"• {pokemon.name}")
    else:
        st.info("まだポケモンが登録されていません。フォームからポケモンを登録してください。")

# Batch import section for convenience
st.header("一括インポート")
st.markdown("複数のポケモンを一度に登録することができます。")

default_pokemon = """ピカチュウ
リザードン
カメックス
フシギバナ
カビゴン
ルカリオ
ゼラオラ
ゲッコウガ
エースバーン
ウッウ
ガブリアス
アブソル
ゲンガー
ファイアロー
ワタシラガ
ヤドラン
プクリン
アローラキュウコン
ツボツボ
カイリキー
サーナイト
ハピナス
ニンフィア
マンムー
カイリュー
アマージョ
フーパ
オーロット
ギルガルド
ジュラルドン
マフォクシー
エーフィ
グレイシア
ベベノム
バンギラス
ドードリオ
ハッサム
ミュウ
ピクシー
コンパン
ザシアン
リーフィア
ゾロアーク
ドラパルト
ブラッキー
ミュウツーX
ミュウツーY
ニャオハ
ラウドボーン
ウーラオス
インテレオン
"""

with st.expander("一括インポート"):
    batch_text = st.text_area("1行に1つずつポケモン名を入力", value=default_pokemon, height=300)
    
    if st.button("ポケモンをインポート"):
        pokemon_names = [name.strip() for name in batch_text.split('\n') if name.strip()]
        
        added_count = 0
        for name in pokemon_names:
            if name and DataManager.add_pokemon(name):
                added_count += 1
        
        if added_count > 0:
            st.success(f"{added_count}体のポケモンが正常にインポートされました！")
            st.rerun()
        else:
            st.info("新しいポケモンは追加されませんでした。既に登録されている可能性があります。")
