import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px


def get_results(year, team_id):
    request_url = f'https://www.openligadb.de/api/getmatchdata/bl1/{year}'
    results = requests.get(request_url).json()

    saison = []
    for match in results:
        spieltag_dict = {}
        if match['MatchIsFinished']:
            match_day = match['Group']['GroupName']
            for match_results in match['MatchResults']:
                if match_results['ResultName'] == 'Endergebnis':
                    if match_results['PointsTeam1'] > match_results['PointsTeam2']:
                        spieltag_dict[match['Team1']['TeamId']] = [3]
                        spieltag_dict[match['Team2']['TeamId']] = [0]
                    elif match_results['PointsTeam1'] < match_results['PointsTeam2']:
                        spieltag_dict[match['Team1']['TeamId']] = [0]
                        spieltag_dict[match['Team2']['TeamId']] = [3]
                    else:
                        spieltag_dict[match['Team1']['TeamId']] = [1]
                        spieltag_dict[match['Team2']['TeamId']] = [1]
        df_spieltag = pd.DataFrame(spieltag_dict, index=[match_day])
        saison.append(df_spieltag)

    df = pd.concat(saison)

    if team_id in df.columns:
        return df[team_id].dropna().cumsum()
    else:
        return pd.DataFrame(columns=[team_id], index=df.index.unique())


def get_teams(year):
    request_url = f'https://www.openligadb.de/api/getavailableteams/bl1/{year}'
    results = requests.get(request_url).json()
    return results


def compile_team_list(seasons):
    team_list = []
    for season in seasons:
        teams = pd.DataFrame(get_teams(season))
        team_list.append(teams)

    df_teams = pd.concat(team_list)
    df_teams.drop_duplicates(inplace=True)
    df_teams.reset_index(drop=True, inplace=True)
    df_teams.set_index('TeamId', inplace=True)
    df_teams.sort_values(by='TeamName', inplace=True)

    return df_teams


def main():
    current_season = 2022
    seasons = list(range(2006, current_season + 1))

    team_list = compile_team_list(seasons)

    selected_team = st.selectbox('Team', team_list['TeamName'])
    team_logo = team_list.loc[team_list['TeamName'] == selected_team, 'TeamIconUrl'].to_list()[0]
    team_id = team_list.loc[team_list['TeamName'] == selected_team].index.to_list()[0]

    components.html(f'<img src="{team_logo}" height="40">')

    df_temp = [get_results(year, team_id) for year in seasons]
    df_temp = pd.concat(df_temp, axis=1)
    df_temp.columns = seasons
    df_temp.dropna(how='all', axis=1, inplace=True)

    fig = px.line(df_temp, x=df_temp.index, y=df_temp.columns, title='Punkte nach Spieltagen')

    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
