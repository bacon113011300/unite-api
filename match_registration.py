import streamlit as st
from models import DataManager
from datetime import datetime

# Page config
st.set_page_config(
    page_title="試合登録 - ポケモンユナイト大会分析ツール",
    page_icon="🏆",
    layout="wide"
)

# Initialize session state
DataManager.initialize_session_state()

st.title("試合登録")
st.markdown("チーム間の試合を登録します。")

# Check if there are enough teams and Pokémon registered
if len(st.session_state.teams) < 2:
    st.warning("試合を記録するには少なくとも2つのチームが必要です。まずチーム登録ページからチームを登録してください。")
    st.stop()

if not st.session_state.pokemons:
    st.warning("試合を記録する前にポケモンを登録する必要があります。ポケモン登録ページからポケモンを登録してください。")
    st.stop()

# Helper function to create team selection form
def create_team_selection_form(team_key, other_team_id=None):
    team_label = "A" if team_key == "A" else "B"
    st.subheader(f"チーム{team_label}")
    
    # Filter out the other team if it's already selected
    available_teams = st.session_state.teams
    if other_team_id:
        available_teams = [team for team in st.session_state.teams if team.id != other_team_id]
    
    team_options = {team.name: team.id for team in available_teams}
    
    if not team_options:
        st.error("選択可能なチームがありません。")
        return None, []
    
    selected_team_name = st.selectbox(
        f"チーム{team_label}を選択", 
        options=list(team_options.keys()),
        key=f"team_{team_key}"
    )
    
    selected_team_id = team_options[selected_team_name]
    selected_team = DataManager.get_team_by_id(selected_team_id)
    
    # Pokemon selections for each team member
    st.write("各メンバーが使用するポケモンを選択してください：")
    
    pokemon_options = {pokemon.name: pokemon.id for pokemon in st.session_state.pokemons}
    player_selections = []
    
    cols = st.columns(5)
    for i, member in enumerate(selected_team.members):
        with cols[i]:
            st.write(f"**{member.name}**")
            selected_pokemon = st.selectbox(
                "ポケモン",
                options=list(pokemon_options.keys()),
                key=f"team_{team_key}_member_{i}"
            )
            player_selections.append((member.id, pokemon_options[selected_pokemon]))
    
    return selected_team_id, player_selections

# Match registration form
with st.form("match_registration_form"):
    st.header("試合を登録")
    
    match_date = st.date_input("試合日", value=datetime.now().date())
    
    # Team A selection
    st.markdown("---")
    team_a_id, team_a_selections = create_team_selection_form("A")
    
    # Team B selection
    st.markdown("---")
    team_b_id, team_b_selections = create_team_selection_form("B", team_a_id)
    
    # Winner selection
    st.markdown("---")
    
    # Get team names for winner selection
    team_a_name = "チームA"
    team_b_name = "チームB"
    
    if team_a_id:
        team_a = DataManager.get_team_by_id(team_a_id)
        if team_a:
            team_a_name = team_a.name
    
    if team_b_id:
        team_b = DataManager.get_team_by_id(team_b_id)
        if team_b:
            team_b_name = team_b.name
    
    winner_options = {
        team_a_name: team_a_id,
        team_b_name: team_b_id
    }
    
    selected_winner = st.radio("勝者チーム", options=list(winner_options.keys()))
    winner_id = winner_options[selected_winner]
    
    # Submit button
    submit_button = st.form_submit_button("試合を登録")
    
    # Process form submission
    if submit_button:
        if not team_a_id or not team_b_id:
            st.error("両方のチームを選択してください。")
        elif team_a_id == team_b_id:
            st.error("異なるチームを選択してください。")
        else:
            # Add match to session state
            date_str = match_date.strftime("%Y-%m-%d")
            success = DataManager.add_match(
                team_a_id=team_a_id,
                team_a_player_selections=team_a_selections,
                team_b_id=team_b_id,
                team_b_player_selections=team_b_selections,
                winner_team_id=winner_id,
                date=date_str
            )
            
            if success:
                st.success("試合が正常に登録されました！")
                st.rerun()
            else:
                st.error("試合の登録に失敗しました。")

# Display registered matches
if st.session_state.matches:
    st.header("登録済み試合")
    
    # Sort matches by date (recent first)
    sorted_matches = sorted(st.session_state.matches, key=lambda x: x.date, reverse=True)
    
    for i, match in enumerate(sorted_matches):
        # Get team names
        team_a = DataManager.get_team_by_id(match.team_a_data.team_id)
        team_b = DataManager.get_team_by_id(match.team_b_data.team_id)
        winner = DataManager.get_team_by_id(match.winner_team_id)
        
        if team_a and team_b and winner:
            with st.expander(f"試合 {i+1}: {team_a.name} vs {team_b.name} ({match.date})"):
                st.write(f"**勝者: {winner.name}**")
                
                col1, col2 = st.columns(2)
                
                # Display Team A details
                with col1:
                    st.subheader(f"{team_a.name}")
                    for selection in match.team_a_data.player_selections:
                        member_data = DataManager.get_member_by_id(selection.member_id)
                        pokemon = DataManager.get_pokemon_by_id(selection.pokemon_id)
                        
                        if member_data and pokemon:
                            team, member = member_data
                            st.write(f"• {member.name}: {pokemon.name}")
                
                # Display Team B details
                with col2:
                    st.subheader(f"{team_b.name}")
                    for selection in match.team_b_data.player_selections:
                        member_data = DataManager.get_member_by_id(selection.member_id)
                        pokemon = DataManager.get_pokemon_by_id(selection.pokemon_id)
                        
                        if member_data and pokemon:
                            team, member = member_data
                            st.write(f"• {member.name}: {pokemon.name}")
else:
    st.info("まだ試合が登録されていません。上記のフォームから試合を登録してください。")
