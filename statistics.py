import streamlit as st
import pandas as pd
import plotly.express as px
from models import DataManager

# Page config
st.set_page_config(
    page_title="統計・勝率 - ポケモンユナイト大会分析ツール",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
DataManager.initialize_session_state()

st.title("統計・勝率")
st.markdown("チーム、プレイヤー、ポケモンのパフォーマンス分析を表示します。")

# Check if there's enough data to show statistics
if not st.session_state.matches:
    st.warning("まだ試合が登録されていません。まず試合登録ページから試合を記録してください。")
    st.stop()

# Sidebar for filtering options
with st.sidebar:
    st.header("フィルターオプション")
    
    # Add min matches filter
    min_matches = st.slider("最小試合数", 1, 10, 1)

# Create tabs for different types of statistics
tab1, tab2, tab3, tab4 = st.tabs(["チーム統計", "チーム別ポケモン統計", "プレイヤー統計", "ポケモン統計"])

# Team Statistics Tab
with tab1:
    st.header("チームパフォーマンス")
    
    team_stats = DataManager.calculate_team_stats()
    
    if team_stats.empty:
        st.info("チーム統計はありません。")
    else:
        # Filter by minimum matches
        filtered_team_stats = team_stats[team_stats['matches_played'] >= min_matches]
        
        if filtered_team_stats.empty:
            st.info(f"{min_matches}試合以上のチームはありません。")
        else:
            # Sort by win rate
            filtered_team_stats = filtered_team_stats.sort_values('win_rate', ascending=False)
            
            # Format win rate as percentage
            filtered_team_stats['win_rate_pct'] = (filtered_team_stats['win_rate'] * 100).round(1).astype(str) + '%'
            
            # Display as table
            st.dataframe(
                filtered_team_stats[['team_name', 'matches_played', 'matches_won', 'win_rate_pct']].rename(
                    columns={
                        'team_name': 'チーム名',
                        'matches_played': '試合数',
                        'matches_won': '勝利数',
                        'win_rate_pct': '勝率'
                    }
                ),
                use_container_width=True,
                hide_index=True
            )
            
            # Create win rate chart
            fig = px.bar(
                filtered_team_stats,
                x='team_name',
                y='win_rate',
                title='チーム勝率',
                labels={'team_name': 'チーム名', 'win_rate': '勝率'},
                color='win_rate',
                color_continuous_scale='RdYlGn',
                text_auto='.1%'
            )
            fig.update_layout(
                xaxis_title="チーム名", 
                yaxis_title="勝率",
                yaxis=dict(tickformat='.0%')
            )
            st.plotly_chart(fig, use_container_width=True)

# Team-Pokémon Statistics Tab
with tab2:
    st.header("チーム別ポケモンパフォーマンス")
    
    # Team selection
    team_options = {team.name: team.id for team in st.session_state.teams}
    selected_team_name = st.selectbox(
        "チームを選択",
        options=list(team_options.keys())
    )
    selected_team_id = team_options[selected_team_name]
    
    # Calculate team-specific Pokémon stats
    team_pokemon_stats = DataManager.calculate_team_pokemon_stats(selected_team_id)
    
    if team_pokemon_stats.empty:
        st.info(f"{selected_team_name}の試合データはありません。")
    else:
        # Filter by minimum matches
        filtered_stats = team_pokemon_stats[team_pokemon_stats['matches_played'] >= min_matches]
        
        if filtered_stats.empty:
            st.info(f"{selected_team_name}で{min_matches}試合以上使用したポケモンはありません。")
        else:
            # Sort by win rate
            filtered_stats = filtered_stats.sort_values('win_rate', ascending=False)
            
            # Format win rate as percentage
            filtered_stats['win_rate_pct'] = (filtered_stats['win_rate'] * 100).round(1).astype(str) + '%'
            
            # Display as table
            st.dataframe(
                filtered_stats[['pokemon_name', 'matches_played', 'matches_won', 'win_rate_pct']].rename(
                    columns={
                        'pokemon_name': 'ポケモン名',
                        'matches_played': '使用回数',
                        'matches_won': '勝利数',
                        'win_rate_pct': '勝率'
                    }
                ),
                use_container_width=True,
                hide_index=True
            )
            
            # Create win rate chart
            fig = px.bar(
                filtered_stats,
                x='pokemon_name',
                y='win_rate',
                title=f'{selected_team_name} - ポケモン別勝率',
                labels={'pokemon_name': 'ポケモン名', 'win_rate': '勝率'},
                color='win_rate',
                color_continuous_scale='RdYlGn',
                text_auto='.1%'
            )
            fig.update_layout(
                xaxis_title="ポケモン名", 
                yaxis_title="勝率",
                yaxis=dict(tickformat='.0%')
            )
            st.plotly_chart(fig, use_container_width=True)

# Player Statistics Tab
with tab3:
    st.header("プレイヤーパフォーマンス")
    
    player_stats = DataManager.calculate_member_stats()
    
    if player_stats.empty:
        st.info("プレイヤー統計はありません。")
    else:
        # Filter by minimum matches
        filtered_player_stats = player_stats[player_stats['matches_played'] >= min_matches]
        
        if filtered_player_stats.empty:
            st.info(f"{min_matches}試合以上のプレイヤーはいません。")
        else:
            # Sort by win rate
            filtered_player_stats = filtered_player_stats.sort_values('win_rate', ascending=False)
            
            # Format win rate as percentage
            filtered_player_stats['win_rate_pct'] = (filtered_player_stats['win_rate'] * 100).round(1).astype(str) + '%'
            
            # Display as table
            st.dataframe(
                filtered_player_stats[['member_name', 'team_name', 'matches_played', 'matches_won', 'win_rate_pct']].rename(
                    columns={
                        'member_name': 'プレイヤー名',
                        'team_name': 'チーム名',
                        'matches_played': '試合数',
                        'matches_won': '勝利数',
                        'win_rate_pct': '勝率'
                    }
                ),
                use_container_width=True,
                hide_index=True
            )
            
            # Create win rate chart for top players
            top_players = filtered_player_stats.head(15)  # Show top 15 players
            fig = px.bar(
                top_players,
                x='member_name',
                y='win_rate',
                title='トッププレイヤー勝率',
                labels={'member_name': 'プレイヤー名', 'win_rate': '勝率'},
                color='team_name',
                text_auto='.1%'
            )
            fig.update_layout(
                xaxis_title="プレイヤー名", 
                yaxis_title="勝率",
                yaxis=dict(tickformat='.0%')
            )
            st.plotly_chart(fig, use_container_width=True)

# Pokémon Statistics Tab
with tab4:
    st.header("ポケモンパフォーマンス")
    
    pokemon_stats = DataManager.calculate_pokemon_stats()
    
    if pokemon_stats.empty:
        st.info("ポケモン統計はありません。")
    else:
        # Filter by minimum matches
        filtered_pokemon_stats = pokemon_stats[pokemon_stats['matches_played'] >= min_matches]
        
        if filtered_pokemon_stats.empty:
            st.info(f"{min_matches}試合以上使用されたポケモンはありません。")
        else:
            # Sort by win rate
            filtered_pokemon_stats = filtered_pokemon_stats.sort_values('win_rate', ascending=False)
            
            # Format win rate as percentage
            filtered_pokemon_stats['win_rate_pct'] = (filtered_pokemon_stats['win_rate'] * 100).round(1).astype(str) + '%'
            
            # Display as table
            st.dataframe(
                filtered_pokemon_stats[['pokemon_name', 'matches_played', 'matches_won', 'win_rate_pct']].rename(
                    columns={
                        'pokemon_name': 'ポケモン名',
                        'matches_played': '使用回数',
                        'matches_won': '勝利数',
                        'win_rate_pct': '勝率'
                    }
                ),
                use_container_width=True,
                hide_index=True
            )
            
            # Create win rate chart
            fig = px.bar(
                filtered_pokemon_stats,
                x='pokemon_name',
                y='win_rate',
                title='ポケモン勝率',
                labels={'pokemon_name': 'ポケモン名', 'win_rate': '勝率'},
                color='win_rate',
                color_continuous_scale='RdYlGn',
                text_auto='.1%'
            )
            fig.update_layout(
                xaxis_title="ポケモン名", 
                yaxis_title="勝率",
                xaxis={'categoryorder':'total descending'},
                yaxis=dict(tickformat='.0%')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Usage statistics
            st.subheader("ポケモン使用率")
            
            fig2 = px.bar(
                filtered_pokemon_stats,
                x='pokemon_name',
                y='matches_played',
                title='ポケモン使用回数',
                labels={'pokemon_name': 'ポケモン名', 'matches_played': '使用回数'},
                color='matches_played',
                color_continuous_scale='Blues',
                text_auto=True
            )
            fig2.update_layout(
                xaxis_title="ポケモン名", 
                yaxis_title="使用回数",
                xaxis={'categoryorder':'total descending'}
            )
            st.plotly_chart(fig2, use_container_width=True)
