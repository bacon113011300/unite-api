from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import pandas as pd
import streamlit as st
import uuid
import json
import os

@dataclass
class Member:
    id: str
    name: str
    
@dataclass
class Team:
    id: str
    name: str
    members: List[Member]
    
@dataclass
class Pokemon:
    id: str
    name: str

@dataclass
class PlayerSelection:
    member_id: str
    pokemon_id: str
    
@dataclass
class TeamMatchData:
    team_id: str
    player_selections: List[PlayerSelection]
    
@dataclass
class Match:
    id: str
    team_a_data: TeamMatchData
    team_b_data: TeamMatchData
    winner_team_id: str
    date: str

class DataManager:
    # データファイルのパス
    DATA_DIR = "data"
    TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")
    POKEMONS_FILE = os.path.join(DATA_DIR, "pokemons.json")
    MATCHES_FILE = os.path.join(DATA_DIR, "matches.json")
    
    @staticmethod
    def _ensure_data_dir():
        """データディレクトリが存在することを確認"""
        if not os.path.exists(DataManager.DATA_DIR):
            os.makedirs(DataManager.DATA_DIR)
    
    @staticmethod
    def save_data():
        """セッションからデータを永続化"""
        DataManager._ensure_data_dir()
        
        # チームの保存
        with open(DataManager.TEAMS_FILE, 'w', encoding='utf-8') as f:
            teams_data = []
            for team in st.session_state.teams:
                team_data = {
                    "id": team.id,
                    "name": team.name,
                    "members": [{"id": m.id, "name": m.name} for m in team.members]
                }
                teams_data.append(team_data)
            json.dump(teams_data, f, ensure_ascii=False, indent=2)
        
        # ポケモンの保存
        with open(DataManager.POKEMONS_FILE, 'w', encoding='utf-8') as f:
            pokemons_data = [{"id": p.id, "name": p.name} for p in st.session_state.pokemons]
            json.dump(pokemons_data, f, ensure_ascii=False, indent=2)
        
        # 試合の保存
        with open(DataManager.MATCHES_FILE, 'w', encoding='utf-8') as f:
            matches_data = []
            for match in st.session_state.matches:
                match_data = {
                    "id": match.id,
                    "team_a_data": {
                        "team_id": match.team_a_data.team_id,
                        "player_selections": [
                            {"member_id": ps.member_id, "pokemon_id": ps.pokemon_id}
                            for ps in match.team_a_data.player_selections
                        ]
                    },
                    "team_b_data": {
                        "team_id": match.team_b_data.team_id,
                        "player_selections": [
                            {"member_id": ps.member_id, "pokemon_id": ps.pokemon_id}
                            for ps in match.team_b_data.player_selections
                        ]
                    },
                    "winner_team_id": match.winner_team_id,
                    "date": match.date
                }
                matches_data.append(match_data)
            json.dump(matches_data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_data():
        """保存されたデータをセッションに読み込む"""
        DataManager._ensure_data_dir()
        
        # チームの読み込み
        if os.path.exists(DataManager.TEAMS_FILE):
            try:
                with open(DataManager.TEAMS_FILE, 'r', encoding='utf-8') as f:
                    teams_data = json.load(f)
                    teams = []
                    for team_data in teams_data:
                        members = [Member(id=m["id"], name=m["name"]) for m in team_data["members"]]
                        teams.append(Team(id=team_data["id"], name=team_data["name"], members=members))
                    st.session_state.teams = teams
            except (json.JSONDecodeError, FileNotFoundError):
                if 'teams' not in st.session_state:
                    st.session_state.teams = []
        
        # ポケモンの読み込み
        if os.path.exists(DataManager.POKEMONS_FILE):
            try:
                with open(DataManager.POKEMONS_FILE, 'r', encoding='utf-8') as f:
                    pokemons_data = json.load(f)
                    st.session_state.pokemons = [Pokemon(id=p["id"], name=p["name"]) for p in pokemons_data]
            except (json.JSONDecodeError, FileNotFoundError):
                if 'pokemons' not in st.session_state:
                    st.session_state.pokemons = []
        
        # 試合の読み込み
        if os.path.exists(DataManager.MATCHES_FILE):
            try:
                with open(DataManager.MATCHES_FILE, 'r', encoding='utf-8') as f:
                    matches_data = json.load(f)
                    matches = []
                    for match_data in matches_data:
                        # Team A data
                        team_a_selections = [
                            PlayerSelection(member_id=ps["member_id"], pokemon_id=ps["pokemon_id"]) 
                            for ps in match_data["team_a_data"]["player_selections"]
                        ]
                        team_a_data = TeamMatchData(
                            team_id=match_data["team_a_data"]["team_id"], 
                            player_selections=team_a_selections
                        )
                        
                        # Team B data
                        team_b_selections = [
                            PlayerSelection(member_id=ps["member_id"], pokemon_id=ps["pokemon_id"]) 
                            for ps in match_data["team_b_data"]["player_selections"]
                        ]
                        team_b_data = TeamMatchData(
                            team_id=match_data["team_b_data"]["team_id"], 
                            player_selections=team_b_selections
                        )
                        
                        # Create match
                        match = Match(
                            id=match_data["id"],
                            team_a_data=team_a_data,
                            team_b_data=team_b_data,
                            winner_team_id=match_data["winner_team_id"],
                            date=match_data["date"]
                        )
                        matches.append(match)
                    
                    st.session_state.matches = matches
            except (json.JSONDecodeError, FileNotFoundError):
                if 'matches' not in st.session_state:
                    st.session_state.matches = []
    
    @staticmethod
    def initialize_session_state():
        """Initialize session state variables if they don't exist"""
        if 'teams' not in st.session_state:
            st.session_state.teams = []
        if 'pokemons' not in st.session_state:
            st.session_state.pokemons = []
        if 'matches' not in st.session_state:
            st.session_state.matches = []
            
        # 以前に保存されたデータがあれば読み込む
        DataManager.load_data()
            
    @staticmethod
    def add_team(team_name: str, member_names: List[str]) -> bool:
        """Add a new team with members"""
        DataManager.initialize_session_state()
        
        # Check if team name already exists
        if any(team.name == team_name for team in st.session_state.teams):
            return False
        
        # Create members
        members = [Member(id=str(uuid.uuid4()), name=name) for name in member_names]
        
        # Create and add team
        new_team = Team(
            id=str(uuid.uuid4()),
            name=team_name,
            members=members
        )
        
        st.session_state.teams.append(new_team)
        # データを保存
        DataManager.save_data()
        return True
    
    @staticmethod
    def add_pokemon(pokemon_name: str) -> bool:
        """Add a new pokemon"""
        DataManager.initialize_session_state()
        
        # Check if pokemon name already exists
        if any(pokemon.name == pokemon_name for pokemon in st.session_state.pokemons):
            return False
        
        # Create and add pokemon
        new_pokemon = Pokemon(
            id=str(uuid.uuid4()),
            name=pokemon_name
        )
        
        st.session_state.pokemons.append(new_pokemon)
        # データを保存
        DataManager.save_data()
        return True
    
    @staticmethod
    def add_match(
            team_a_id: str, 
            team_a_player_selections: List[Tuple[str, str]],
            team_b_id: str, 
            team_b_player_selections: List[Tuple[str, str]],
            winner_team_id: str,
            date: str
        ) -> bool:
        """Add a new match"""
        DataManager.initialize_session_state()
        
        # Create player selections for team A
        team_a_selections = [
            PlayerSelection(member_id=member_id, pokemon_id=pokemon_id)
            for member_id, pokemon_id in team_a_player_selections
        ]
        
        # Create player selections for team B
        team_b_selections = [
            PlayerSelection(member_id=member_id, pokemon_id=pokemon_id)
            for member_id, pokemon_id in team_b_player_selections
        ]
        
        # Create team match data
        team_a_data = TeamMatchData(team_id=team_a_id, player_selections=team_a_selections)
        team_b_data = TeamMatchData(team_id=team_b_id, player_selections=team_b_selections)
        
        # Create and add match
        new_match = Match(
            id=str(uuid.uuid4()),
            team_a_data=team_a_data,
            team_b_data=team_b_data,
            winner_team_id=winner_team_id,
            date=date
        )
        
        st.session_state.matches.append(new_match)
        # データを保存
        DataManager.save_data()
        return True
    
    @staticmethod
    def get_team_by_id(team_id: str) -> Optional[Team]:
        """Get team by ID"""
        DataManager.initialize_session_state()
        
        for team in st.session_state.teams:
            if team.id == team_id:
                return team
        return None
    
    @staticmethod
    def get_member_by_id(member_id: str) -> Optional[Tuple[Team, Member]]:
        """Get member and their team by member ID"""
        DataManager.initialize_session_state()
        
        for team in st.session_state.teams:
            for member in team.members:
                if member.id == member_id:
                    return (team, member)
        return None
    
    @staticmethod
    def get_pokemon_by_id(pokemon_id: str) -> Optional[Pokemon]:
        """Get pokemon by ID"""
        DataManager.initialize_session_state()
        
        for pokemon in st.session_state.pokemons:
            if pokemon.id == pokemon_id:
                return pokemon
        return None
    
    @staticmethod
    def calculate_team_stats():
        """Calculate team statistics"""
        DataManager.initialize_session_state()
        
        team_stats = []
        
        for team in st.session_state.teams:
            # Total matches played by team
            matches_played = 0
            matches_won = 0
            
            for match in st.session_state.matches:
                if match.team_a_data.team_id == team.id or match.team_b_data.team_id == team.id:
                    matches_played += 1
                    if match.winner_team_id == team.id:
                        matches_won += 1
            
            win_rate = matches_won / matches_played if matches_played > 0 else 0
            
            team_stats.append({
                'team_id': team.id,
                'team_name': team.name,
                'matches_played': matches_played,
                'matches_won': matches_won,
                'win_rate': win_rate
            })
            
        return pd.DataFrame(team_stats)
    
    @staticmethod
    def calculate_pokemon_stats():
        """Calculate pokemon statistics"""
        DataManager.initialize_session_state()
        
        pokemon_stats = {}
        
        for pokemon in st.session_state.pokemons:
            pokemon_stats[pokemon.id] = {
                'pokemon_id': pokemon.id,
                'pokemon_name': pokemon.name,
                'matches_played': 0,
                'matches_won': 0
            }
        
        for match in st.session_state.matches:
            # Process team A
            for selection in match.team_a_data.player_selections:
                pokemon_id = selection.pokemon_id
                if pokemon_id in pokemon_stats:
                    pokemon_stats[pokemon_id]['matches_played'] += 1
                    if match.winner_team_id == match.team_a_data.team_id:
                        pokemon_stats[pokemon_id]['matches_won'] += 1
            
            # Process team B
            for selection in match.team_b_data.player_selections:
                pokemon_id = selection.pokemon_id
                if pokemon_id in pokemon_stats:
                    pokemon_stats[pokemon_id]['matches_played'] += 1
                    if match.winner_team_id == match.team_b_data.team_id:
                        pokemon_stats[pokemon_id]['matches_won'] += 1
        
        # Calculate win rates
        for pokemon_id in pokemon_stats:
            stats = pokemon_stats[pokemon_id]
            stats['win_rate'] = stats['matches_won'] / stats['matches_played'] if stats['matches_played'] > 0 else 0
        
        return pd.DataFrame(list(pokemon_stats.values()))
    
    @staticmethod
    def calculate_member_stats():
        """Calculate member statistics"""
        DataManager.initialize_session_state()
        
        member_stats = {}
        
        # Initialize stats for all members
        for team in st.session_state.teams:
            for member in team.members:
                member_stats[member.id] = {
                    'member_id': member.id,
                    'member_name': member.name,
                    'team_name': team.name,
                    'matches_played': 0,
                    'matches_won': 0
                }
        
        for match in st.session_state.matches:
            # Process team A members
            for selection in match.team_a_data.player_selections:
                member_id = selection.member_id
                if member_id in member_stats:
                    member_stats[member_id]['matches_played'] += 1
                    if match.winner_team_id == match.team_a_data.team_id:
                        member_stats[member_id]['matches_won'] += 1
            
            # Process team B members
            for selection in match.team_b_data.player_selections:
                member_id = selection.member_id
                if member_id in member_stats:
                    member_stats[member_id]['matches_played'] += 1
                    if match.winner_team_id == match.team_b_data.team_id:
                        member_stats[member_id]['matches_won'] += 1
        
        # Calculate win rates
        for member_id in member_stats:
            stats = member_stats[member_id]
            stats['win_rate'] = stats['matches_won'] / stats['matches_played'] if stats['matches_played'] > 0 else 0
        
        return pd.DataFrame(list(member_stats.values()))
    
    @staticmethod
    def calculate_team_pokemon_stats(team_id: str):
        """Calculate pokemon statistics for a specific team"""
        DataManager.initialize_session_state()
        
        team = DataManager.get_team_by_id(team_id)
        if not team:
            return pd.DataFrame()
            
        pokemon_stats = {}
        
        for pokemon in st.session_state.pokemons:
            pokemon_stats[pokemon.id] = {
                'pokemon_id': pokemon.id,
                'pokemon_name': pokemon.name,
                'matches_played': 0,
                'matches_won': 0
            }
        
        for match in st.session_state.matches:
            # Check if team is in the match
            if match.team_a_data.team_id == team_id:
                # Process team A
                for selection in match.team_a_data.player_selections:
                    pokemon_id = selection.pokemon_id
                    if pokemon_id in pokemon_stats:
                        pokemon_stats[pokemon_id]['matches_played'] += 1
                        if match.winner_team_id == team_id:
                            pokemon_stats[pokemon_id]['matches_won'] += 1
            
            elif match.team_b_data.team_id == team_id:
                # Process team B
                for selection in match.team_b_data.player_selections:
                    pokemon_id = selection.pokemon_id
                    if pokemon_id in pokemon_stats:
                        pokemon_stats[pokemon_id]['matches_played'] += 1
                        if match.winner_team_id == team_id:
                            pokemon_stats[pokemon_id]['matches_won'] += 1
        
        # Calculate win rates and filter out unused pokemon
        filtered_stats = []
        for pokemon_id, stats in pokemon_stats.items():
            if stats['matches_played'] > 0:
                stats['win_rate'] = stats['matches_won'] / stats['matches_played']
                filtered_stats.append(stats)
        
        return pd.DataFrame(filtered_stats)
