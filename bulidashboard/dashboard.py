import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from datetime import datetime


def get_results(year, team_id):
    request_url = f'https://www.openligadb.de/api/getmatchdata/bl1/{year}'
    results = requests.get(request_url).json()

    saison = []
    for match in results:
        spieltag_dict = {}
        if match['MatchIsFinished']:
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
        df_spieltag = pd.DataFrame(spieltag_dict)
        saison.append(df_spieltag)

    return pd.concat(saison)


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
    seasons = list(range(2010, current_season + 1))

    team_list = compile_team_list(seasons)

    selected_team = st.selectbox('Team', team_list['TeamName'])
    team_logo = team_list.loc[team_list['TeamName'] == selected_team, 'TeamIconUrl'].to_list()[0]

    components.html(f'<img src="{team_logo}" height="30">')


if __name__ == "__main__":
    main()
