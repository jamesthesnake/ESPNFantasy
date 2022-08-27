import requests
import pandas as pd
from collections import defaultdict

import plotly.graph_objects as go

s = requests.Session()
r = s.get('https://www.espn.com')

swid = s.cookies.get_dict()['SWID']
espn_cookie="AEC5Ghd182YQnnbEpK8h8KdThfJ8OXS1ibacrzl0UDVXWW3pBW%2F%2BXzKm4ovgFo7TpEINzgzH1B3SuelvDJ8K1yjvC4tdGHdDo3bJrbBBQDI%2B6%2B%2F9l7YRoIbRMrd%2F4cB9eDmLcJWWLLMcQdfltDcjWpxbU9%2Fg78IzCiD2PZLQxZ%2FBn7z35kVRxOTpanoOl4yk2ZSeCWIUBnyBBtqNRm8flFBEI0m%2BoVgNcmzXCzVmC31nMQTNZTvFzXsqJJ%2FI9NKoxQl0AA2Du9qsXWJBR22mUlYHV5yKIUvQzndaFOcFir0TE72oh%2FpuhNX5AKzPzabVArM%3D"
overallRecord = {}     

league_id = 1547664
teamId = {}
abbrv_dict={10:'jake',11:'shane',4:'lauren',7:'dps',3:'alex',1:'luke',2:'dylan',8:'taylor',12:'der',13:'rachel'}
rev_dict=defaultdict(list)
final_df=pd.DataFrame()
for x in range(0,7):
    number=2015+x
    url = 'https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/%s?seasonId=%s' %(league_id ,number)


    r = requests.get(url, cookies={"swid": swid, "espn_s2": espn_cookie}).json()[0]
    #Get Team IDs
    home_dict = {}

    for team in r['teams']:
        print(team)
        try:
          #  teamId[team['id']] = team['location'].strip() + ' ' + team['nickname'].strip()
          name=team['location'].strip() + ' ' + team['nickname'].strip()
          home_dict[team['id']] = name
          teamId[name]=team['id']
          rev_dict[team['id']].append(name)
        except:
            print(team)
            #teamId[team['id']]=team['displayName']
    #Get each team's weekly points and calculate their head-to-head records
    r = requests.get(url, cookies={"swid": swid, "espn_s2": espn_cookie}, params={"view": "mMatchup"}).json()[0]
    #weeklyPts = pd.DataFrame()
    weeklyPts = pd.DataFrame()

    for each in r['schedule']:
        #each = r['schedule'][0]

        week = each['matchupPeriodId']
        if week > 14:
            continue
    #    print(each['home']['teamId'])
      #  homeTm = teamId[each['home']['teamId']]
        homeTm=each['home']['teamId']
        homeTmPts = each['home']['totalPoints']

        try:
           # awayTm = teamId[each['away']['teamId']]
            awayTm=each['away']['teamId']

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

        weeklyPts = pd.concat([weeklyPts,temp_df], sort=True).reset_index(drop=True)

    weeklyPts['win'] = weeklyPts.groupby(['team'])['win'].cumsum()
    weeklyPts['loss'] = weeklyPts.groupby(['team'])['loss'].cumsum()
    weeklyPts['tie'] = weeklyPts.groupby(['team'])['tie'].cumsum()
    #print(weeklyPts)

    # Calculate each teams record compared to all other teams points week to week
    cumWeeklyRecord = {}   
    for week in weeklyPts[weeklyPts['pts'] > 0]['week'].unique():
        df = weeklyPts[weeklyPts['week'] == week]

        cumWeeklyRecord[week] = {}
        for idx, row in df.iterrows():
            team = row['team']
            team=home_dict[int(team)]
            pts = row['pts']
            win = len(df[df['pts'] < pts])
            loss = len(df[df['pts'] > pts])
            tie = len(df[df['pts'] == pts])

            cumWeeklyRecord[week][team] = {}
            cumWeeklyRecord[week][team]['win'] = win
            cumWeeklyRecord[week][team]['loss'] = loss
            cumWeeklyRecord[week][team]['tie'] = tie-1

    # Combine those cumluative records to get an overall season record      
   # overallRecord = {}     
   # print(overallRecord)
    index=0
   #    print(overallRecord.keys())
    for each in cumWeeklyRecord.items():
       # print(index)
        index+=1
        #print(each)
        for team in each[1].keys():
            abbv=abbrv_dict[teamId[team]]
            if number>2020 and abbv=='shane':
                abbv='david c'
            print(teamId[team],abbv)
            if abbv not in overallRecord.keys():
                overallRecord[abbv] = {} 
            teams=abbv

            win = each[1][team]['win']
            loss = each[1][team]['loss']
            tie = each[1][team]['tie']
            #print(win,loss,team,teams)
            if 'win' not in overallRecord[teams].keys():
                overallRecord[teams]['win'] = win
            else:
                overallRecord[teams]['win'] += win

            if 'loss' not in overallRecord[teams].keys():
                overallRecord[teams]['loss'] = loss
            else:
                overallRecord[teams]['loss'] += loss

            if 'tie' not in overallRecord[teams].keys():
                overallRecord[teams]['tie'] = tie
            else:
                overallRecord[teams]['tie'] += tie

  #  print(number)
 #   print(cumWeeklyRecord)
    print(overallRecord,number)

names=[]
wins=[]
loses=[]
ties=[]
for x,y in overallRecord.items():
    names.append(x)
    wins.append(y['win'])
    loses.append(y['loss'])
    ties.append(y['tie'])
headerColor = 'grey'
rowEvenColor = 'white'
rowOddColor = 'white'

fig = go.Figure(data=[go.Table(
  header=dict(
    values=['<b>Name</b>','<b>Wins</b>','<b>Loses</b>','<b>Ties</b>'],
    line_color='darkslategray',
    fill_color=headerColor,
    align=['left','center'],
    font=dict(color='white', size=12)
  ),
  cells=dict(
    values=[
    names,
    wins,
    loses,
    ties],
    line_color='darkslategray',
    # 2-D list of colors for alternating rows
    fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor]*5],
    align = ['left', 'center'],
    font = dict(color = 'darkslategray', size = 11)
    ))
])
fig.show()

"""
    overallRecord_df = pd.DataFrame(overallRecord).T
    overallRecord_df = overallRecord_df.rename_axis('team').reset_index()
    overallRecord_df = overallRecord_df.rename(columns={'win':'overall_win', 'loss':'overall_loss','tie':'overall_tie'})
    overallRecord_df['overall_win%'] = overallRecord_df['overall_win'] / (overallRecord_df['overall_win'] + overallRecord_df['overall_loss'] + overallRecord_df['overall_tie'])
    overallRecord_df['overall_rank'] = overallRecord_df['overall_win%'].rank(ascending=False, method='min')
   # print(weeklyPts)



    regularSeasRecord = weeklyPts[weeklyPts['week'] == 14][['team','win','loss', 'tie']]
    regularSeasRecord['win%'] = regularSeasRecord['win'] / (regularSeasRecord['win'] + regularSeasRecord['loss'] + regularSeasRecord['tie'])
    regularSeasRecord['rank'] = regularSeasRecord['win%'].rank(ascending=False, method='min')



    finals = overallRecord_df.merge(regularSeasRecord, how='left', on=['team'])
    if number==2015:
        final_df=finals
    else:

        final_df=pd.concat(finals,final_df)
    print(final_df)
    for index,x in enumerate(final_df['team']):
        print(abbrv_dict,index,x)
        namer=abbrv_dict[x]
        final_df['team'][index]=namer
    print(final_df)
    #print(x,number)
    """
