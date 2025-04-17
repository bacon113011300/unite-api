import streamlit as st
from models import DataManager

# Page config
st.set_page_config(
    page_title="チーム登録 - ポケモンユナイト大会分析ツール",
    page_icon="👥",
    layout="wide"
)

# Initialize session state
DataManager.initialize_session_state()

st.title("チーム登録")
st.markdown("大会に参加する5人制チームとメンバーを登録します。")

# Form for team registration
with st.form("team_registration_form"):
    st.subheader("新規チーム追加")
    
    team_name = st.text_input("チーム名")
    
    # Input fields for 5 members
    st.subheader("チームメンバー")
    member_names = []
    
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            member_name = st.text_input(f"メンバー {i+1}", key=f"member_{i}")
            member_names.append(member_name)
    
    # Submit button
    submit_button = st.form_submit_button("チームを登録")
    
    # Process form submission
    if submit_button:
        if not team_name:
            st.error("チーム名を入力してください。")
        elif any(not name for name in member_names):
            st.error("全てのメンバー名を入力してください。")
        else:
            # Add team to session state
            success = DataManager.add_team(team_name, member_names)
            
            if success:
                st.success(f"チーム「{team_name}」が正常に登録されました！")
                st.rerun()
            else:
                st.error(f"チーム名「{team_name}」は既に存在します。")

# Display registered teams
if st.session_state.teams:
    st.header("登録済みチーム")
    
    # Create tabs for each team
    team_tabs = st.tabs([team.name for team in st.session_state.teams])
    
    for i, tab in enumerate(team_tabs):
        with tab:
            team = st.session_state.teams[i]
            st.subheader(f"{team.name}のメンバー")
            
            # Display members in a table format
            cols = st.columns(5)
            for j, member in enumerate(team.members):
                with cols[j % 5]:
                    st.write(f"**{j+1}. {member.name}**")
else:
    st.info("まだチームが登録されていません。上記のフォームからチームを登録してください。")
