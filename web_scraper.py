import requests
import pandas as pd



s = requests.Session()
r = s.get('https://www.espn.com')

swid = s.cookies.get_dict()['SWID']
print(s.cookies.get_dict())
espn_cookie="AEC5Ghd182YQnnbEpK8h8KdThfJ8OXS1ibacrzl0UDVXWW3pBW%2F%2BXzKm4ovgFo7TpEINzgzH1B3SuelvDJ8K1yjvC4tdGHdDo3bJrbBBQDI%2B6%2B%2F9l7YRoIbRMrd%2F4cB9eDmLcJWWLLMcQdfltDcjWpxbU9%2Fg78IzCiD2PZLQxZ%2FBn7z35kVRxOTpanoOl4yk2ZSeCWIUBnyBBtqNRm8flFBEI0m%2BoVgNcmzXCzVmC31nMQTNZTvFzXsqJJ%2FI9NKoxQl0AA2Du9qsXWJBR22mUlYHV5yKIUvQzndaFOcFir0TE72oh%2FpuhNX5AKzPzabVArM%3D"

league_id = 1547664

for x in range(0,7):
    #number=2015+x
    number=2015
    url = 'https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/%s?seasonId=%s' %(league_id ,number)


    r = requests.get(url, cookies={"swid": swid, "espn_s2": espn_cookie}).json()[0]

    #Get Team IDs
    teamId = {}
    for team in r['teams']:
        print(team)
        try:
            teamId[team['id']] = team['location'].strip() + ' ' + team['nickname'].strip()
        except:
            print(team)
            #teamId[team['id']]=team['displayName']

    #Get each team's weekly points and calculate their head-to-head records
    weeklyPoints = {}
    r = requests.get(url, cookies={"swid": swid, "espn_s2": espn_cookie}, params={"view": "mMatchup"}).json()[0]

    weeklyPts = pd.DataFrame()
    for each in r['schedule']:
        #each = r['schedule'][0]

        week = each['matchupPeriodId']
        if week > 14:
            continue

        homeTm = teamId[each['home']['teamId']]
        homeTmPts = each['home']['totalPoints']

        try:
            awayTm = teamId[each['away']['teamId']]
            awayTmPts = each['away']['totalPoints']
        except:
            homeTmPts = 'BYE'
            continue

        temp_df = pd.DataFrame(list(zip([homeTm, awayTm], [homeTmPts, awayTmPts], [week, week])), columns=['team','pts','week'])

        if homeTmPts > awayTmPts:
            temp_df.loc[0,'win'] = 1
            temp_df.loc[0,'loss'] = 0
            temp_df.loc[0,'tie'] = 0

            temp_df.loc[1,'win'] = 0
            temp_df.loc[1,'loss'] = 1
            temp_df.loc[1,'tie'] = 0

        elif homeTmPts < awayTmPts:
            temp_df.loc[0,'win'] = 0
            temp_df.loc[0,'loss'] = 1
            temp_df.loc[0,'tie'] = 0

            temp_df.loc[1,'win'] = 1
            temp_df.loc[1,'loss'] = 0
            temp_df.loc[1,'tie'] = 0

        elif homeTmPts == awayTmPts:
            temp_df.loc[0,'win'] = 0
            temp_df.loc[0,'loss'] = 0
            temp_df.loc[0,'tie'] = 1

            temp_df.loc[1,'win'] = 0
            temp_df.loc[1,'loss'] = 0
            temp_df.loc[1,'tie'] = 1

        weeklyPts = weeklyPts.append(temp_df, sort=True).reset_index(drop=True)

    weeklyPts['win'] = weeklyPts.groupby(['team'])['win'].cumsum()
    weeklyPts['loss'] = weeklyPts.groupby(['team'])['loss'].cumsum()
    weeklyPts['tie'] = weeklyPts.groupby(['team'])['tie'].cumsum()



    # Calculate each teams record compared to all other teams points week to week
    cumWeeklyRecord = {}   
    for week in weeklyPts[weeklyPts['pts'] > 0]['week'].unique():
        df = weeklyPts[weeklyPts['week'] == week]

        cumWeeklyRecord[week] = {}
        for idx, row in df.iterrows():
            team = row['team']
            pts = row['pts']
            win = len(df[df['pts'] < pts])
            loss = len(df[df['pts'] > pts])
            tie = len(df[df['pts'] == pts])

            cumWeeklyRecord[week][team] = {}
            cumWeeklyRecord[week][team]['win'] = win
            cumWeeklyRecord[week][team]['loss'] = loss
            cumWeeklyRecord[week][team]['tie'] = tie-1

    # Combine those cumluative records to get an overall season record      
    overallRecord = {}     
    for each in cumWeeklyRecord.items():
        for team in each[1].keys():
            if team not in overallRecord.keys():
                overallRecord[team] = {} 

            win = each[1][team]['win']
            loss = each[1][team]['loss']
            tie = each[1][team]['tie']

            if 'win' not in overallRecord[team].keys():
                overallRecord[team]['win'] = win
            else:
                overallRecord[team]['win'] += win

            if 'loss' not in overallRecord[team].keys():
                overallRecord[team]['loss'] = loss
            else:
                overallRecord[team]['loss'] += loss

            if 'tie' not in overallRecord[team].keys():
                overallRecord[team]['tie'] = tie
            else:
                overallRecord[team]['tie'] += tie


    # Little cleaning up of the data nd calculating win %
    overallRecord_df = pd.DataFrame(overallRecord).T
    overallRecord_df = overallRecord_df.rename_axis('team').reset_index()
    overallRecord_df = overallRecord_df.rename(columns={'win':'overall_win', 'loss':'overall_loss','tie':'overall_tie'})
    overallRecord_df['overall_win%'] = overallRecord_df['overall_win'] / (overallRecord_df['overall_win'] + overallRecord_df['overall_loss'] + overallRecord_df['overall_tie'])
    overallRecord_df['overall_rank'] = overallRecord_df['overall_win%'].rank(ascending=False, method='min')




    regularSeasRecord = weeklyPts[weeklyPts['week'] == 14][['team','win','loss', 'tie']]
    regularSeasRecord['win%'] = regularSeasRecord['win'] / (regularSeasRecord['win'] + regularSeasRecord['loss'] + regularSeasRecord['tie'])
    regularSeasRecord['rank'] = regularSeasRecord['win%'].rank(ascending=False, method='min')



    final_df = overallRecord_df.merge(regularSeasRecord, how='left', on=['team'])
    print(final_df)