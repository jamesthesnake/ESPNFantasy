from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import dataframe_image as dfi

xls = pd.ExcelFile('history.xlsx')
sheet_to_df_map = pd.read_excel("history.xlsx", sheet_name=None)
#print(sheet_to_df_map)
keys=sheet_to_df_map.keys()
point_dict=defaultdict(int)
wins_dict=defaultdict(int)
names_set=set()
looser=pd.DataFrame(sheet_to_df_map["2021"][["TEAM","Name","Wins","Lose","PF","PA"]])
loses_dict=defaultdict(int)
for x in keys:
    for name in sheet_to_df_map[x].Name:
        names_set.add(name)
    if x !='2021':
        print(sheet_to_df_map[x],"baker")
        looser=pd.concat([looser,sheet_to_df_map[x][["TEAM","Name","Wins","Lose","PF","PA"]]])
      #    looser.append()
      #  print(sheet_to_df_map[x].loc[sheet_to_df_map[x]['Name'] == y, 'Wins'])
        #wins_dict[] += y.Wins
        #loses_dict[y.Name] += y.Loses

pivot=pd.pivot_table(
    data=looser,
    index='Name',
    aggfunc=['mean','sum']

  #  values=['Wins',"Lose"]
)

print(pivot)
alone=pd.Series()
pivot['games']=pivot['sum']['Wins']+pivot['sum']['Lose']
pivot['average_points_user_scored_for_per_game']=pivot['sum']['PF']/pivot['games']
pivot['average_points_scored_against_user_per_game']=pivot['sum']['PA']/pivot['games']

edge=[]
luck=[]
name_r=[]
for x in names_set:
    print(x)
    name_r.append(x)
    luck.append((sum(pivot['sum']['PF'])-pivot['sum']['PF'][x])/(sum(pivot['games'])-pivot['games'][x])-pivot['sum']['PA'][x]/pivot['games'][x])
    print(x,(sum(pivot['sum']['PF'])-pivot['sum']['PF'][x])/(sum(pivot['games'])-pivot['games'][x]))
    edge.append((sum(pivot['sum']['PF'])-pivot['sum']['PF'][x])/(sum(pivot['games'])-pivot['games'][x]))

alone=pd.Series(edge)
alone.index=name_r
pivot['average_score_of_other_players_per_game']=alone
alone=pd.Series(luck)
alone.index=name_r
pivot['luck']=alone

print(pivot.keys())
print(type(pivot['sum']['Wins']))
print(pivot.index)
df_styled = pivot.style.background_gradient() #adding a gradient based on values in cell
dfi.export(df_styled,"mytable.png")

ax=pivot['sum'][['Wins','Lose']].plot(kind='barh',stacked='true').get_figure()
ra=pivot['sum'][['PF','PA']].plot(kind='barh',stacked='true').get_figure()

ax.savefig('test.pdf')
ra.savefig('test1.pdf')

#plt.figure(pivot,pivot['sum']['Wins'])

       # sheet_to_df_map[x][
        #print(sheet_to_df_map[x][["Name","Wins","Lose"]])
#reduced = [x for x in sheet_to_df_map.name]
#print(reduced)
#df.groupby(reduced, axis=1).sum()
