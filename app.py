import streamlit as st
from models import DataManager
import os

# Set page config
st.set_page_config(
    page_title="ポケモンユナイト大会分析ツール",
    page_icon="🎮",
    layout="wide",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': 'ポケモンユナイト大会の分析ツール'
    }
)

# Initialize session state
DataManager.initialize_session_state()

# CSS for custom styling with Pokemon background
st.markdown("""
<style>
    body {
        background-color: #FFFFFF;
    }
    
    .stApp {
        background-color: rgba(255, 255, 255, 0.85);
    }
    
    .main-header {
        font-family: 'Arial Black', sans-serif;
        color: #FF0000;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .pokemon-card {
        background-color: #FFF2F2;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 3px solid #FF0000;
    }
    
    .unite-badge {
        background-color: #FF0000;
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        margin-right: 10px;
    }
    
    /* ポケボールスタイルのボタン */
    .stButton>button {
        background: linear-gradient(to bottom, white 50%, #FF0000 50%);
        border: 2px solid black;
        border-radius: 50%;
        position: relative;
    }
    
    /* シンプルなスタイル */
    .stApp {
        background-color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# Main app header with Pokemon image
st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 20px;">
    <img src="https://www.freepnglogos.com/uploads/pokemon-symbol-logo-png-31.png" style="height: 60px; margin-right: 15px;">
    <h1 class="main-header">ポケモンユナイト大会分析ツール</h1>
</div>
""", unsafe_allow_html=True)

# App description with Pokemon-themed styling
st.markdown("""
<div class="pokemon-card">
    <h3>ようこそ！</h3>
    <p>このアプリケーションは大会主催者やチームがポケモンユナイトの試合を追跡・分析するのに役立ちます。</p>
    <p>左側のナビゲーションメニューから各機能にアクセスしてください。</p>
    <p>
        <span class="unite-badge">チーム登録</span>
        <span class="unite-badge">ポケモン登録</span>
        <span class="unite-badge">試合登録</span>
        <span class="unite-badge">統計・勝率</span>
    </p>
</div>
""", unsafe_allow_html=True)

# Display dashboard with summary statistics if there's data
if st.session_state.teams and st.session_state.matches:
    st.markdown('<h2 class="main-header">ダッシュボード</h2>', unsafe_allow_html=True)
    
    # Dashboard stats
    stats_col1, stats_col2 = st.columns(2)
    
    with stats_col1:
        st.markdown("""
        <div class="pokemon-card" style="border-top: 4px solid #5470C6;">
            <h3 style="color: #5470C6;">登録済みチーム</h3>
            <p style="font-size: 20px; font-weight: bold;">総チーム数: {}</p>
            <hr style="margin: 10px 0; border-color: #eee;">
        """.format(len(st.session_state.teams)), unsafe_allow_html=True)
        
        # List all teams
        for team in st.session_state.teams:
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="background-color: #5470C6; color: white; width: 24px; height: 24px; border-radius: 50%; 
                            text-align: center; line-height: 24px; margin-right: 10px; font-size: 14px;">T</div>
                <div>{team.name} ({len(team.members)}名)</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with stats_col2:
        st.markdown(f"""
        <div class="pokemon-card" style="border-top: 4px solid #91CC75;">
            <h3 style="color: #91CC75;">大会統計</h3>
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                <div>
                    <p style="color: #666; margin-bottom: 0;">総試合数</p>
                    <p style="font-size: 24px; font-weight: bold; margin-top: 5px;">{len(st.session_state.matches)}</p>
                </div>
                <div>
                    <p style="color: #666; margin-bottom: 0;">登録済みポケモン</p>
                    <p style="font-size: 24px; font-weight: bold; margin-top: 5px;">{len(st.session_state.pokemons)}体</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Show recent matches if any
    if st.session_state.matches:
        st.markdown('<h3 style="margin-top: 30px; color: #FF0000;">最近の試合</h3>', unsafe_allow_html=True)
        
        # Get recent matches
        recent_matches = sorted(st.session_state.matches, key=lambda x: x.date, reverse=True)[:5]
        
        for match in recent_matches:
            team_a = DataManager.get_team_by_id(match.team_a_data.team_id)
            team_b = DataManager.get_team_by_id(match.team_b_data.team_id)
            winner = DataManager.get_team_by_id(match.winner_team_id)
            
            if team_a and team_b and winner:
                winner_style = 'style="color: #FF0000; font-weight: bold;"' if winner.id == team_a.id else ''
                loser_style = 'style="color: #FF0000; font-weight: bold;"' if winner.id == team_b.id else ''
                
                st.markdown(f"""
                <div class="pokemon-card" style="padding: 15px; margin-bottom: 10px; display: flex; align-items: center;">
                    <div style="flex: 2; text-align: right;"><span {winner_style}>{team_a.name}</span></div>
                    <div style="flex: 1; text-align: center; font-weight: bold;">vs</div>
                    <div style="flex: 2; text-align: left;"><span {loser_style}>{team_b.name}</span></div>
                    <div style="flex: 2; text-align: right; color: #666; font-size: 0.9em;">勝者: <span style="color: #FF0000; font-weight: bold;">{winner.name}</span></div>
                    <div style="flex: 1; text-align: right; color: #999; font-size: 0.8em;">{match.date}</div>
                </div>
                """, unsafe_allow_html=True)
else:
    # Instructions for new users with Pokemon styling
    st.markdown("""
    <div class="pokemon-card" style="border-left: 5px solid #4E67EB;">
        <h3>👈 サイドバーのナビゲーションからチームとポケモンの登録を始めましょう！</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="main-header">はじめに</h2>', unsafe_allow_html=True)
    
    # Step-by-step guide with Pokemon styling
    st.markdown("""
    <div class="pokemon-card" style="margin-top: 20px; position: relative; overflow: hidden;">
        <!-- ポケモンのシルエットを背景に -->
        <div style="position: absolute; right: -50px; bottom: -30px; opacity: 0.1; transform: rotate(10deg);">
            <img src="https://www.pngmart.com/files/2/Pokemon-Transparent-Background.png" width="200">
        </div>
        
        <div style="display: flex; align-items: center; margin-bottom: 15px; position: relative; z-index: 2;">
            <div style="background-color: #FF0000; color: white; width: 30px; height: 30px; border-radius: 50%; text-align: center; line-height: 30px; margin-right: 15px;">1</div>
            <div><strong>チーム登録</strong>ページでチームを登録します</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 15px; position: relative; z-index: 2;">
            <div style="background-color: #FF0000; color: white; width: 30px; height: 30px; border-radius: 50%; text-align: center; line-height: 30px; margin-right: 15px;">2</div>
            <div><strong>ポケモン登録</strong>ページで使用するポケモンを登録します</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 15px; position: relative; z-index: 2;">
            <div style="background-color: #FF0000; color: white; width: 30px; height: 30px; border-radius: 50%; text-align: center; line-height: 30px; margin-right: 15px;">3</div>
            <div><strong>試合登録</strong>ページで試合を記録します</div>
        </div>
        <div style="display: flex; align-items: center; position: relative; z-index: 2;">
            <div style="background-color: #FF0000; color: white; width: 30px; height: 30px; border-radius: 50%; text-align: center; line-height: 30px; margin-right: 15px;">4</div>
            <div><strong>統計・勝率</strong>ページで分析結果を確認します</div>
        </div>
        
        <!-- ポケボールのデコレーション -->
        <div style="position: absolute; left: 10px; top: 10px; width: 20px; height: 20px; border-radius: 50%; background: linear-gradient(to bottom, white 50%, #FF0000 50%); border: 1px solid black;"></div>
        <div style="position: absolute; right: 10px; top: 10px; width: 20px; height: 20px; border-radius: 50%; background: linear-gradient(to bottom, white 50%, #FF0000 50%); border: 1px solid black;"></div>
    </div>
    """, unsafe_allow_html=True)
