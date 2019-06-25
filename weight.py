import pandas as pd
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go

# read weight data
weight = pd.read_csv('data/BodyMass.csv')
weight = weight.round({'value': 1})
assert weight.unit.unique() == 'kg'
weight['time'] = pd.to_datetime(weight.creationDate.map(lambda x: x[: -6]))
weight['date'] = pd.to_datetime(weight.time.dt.date)
weight['week'] = weight.date.map(lambda x: 100 * x.year + x.week)
weight = weight[['week', 'date', 'value']]

# read workout data
workout = pd.read_csv('data/ActivitySummary.csv')
workout = workout[workout.activeEnergyBurnedGoal > 0]
workout['week'] = pd.to_datetime(workout.dateComponents).map(lambda x: 100 * x.year + x.week)
workout = workout.groupby(by=['week'], as_index=False)[['appleExerciseTime', 'activeEnergyBurned']].sum()

# merge dateset by week
df = pd.merge(weight, workout, how='left', left_on='week', right_on='week')
df = df.dropna()
del df['week']
df = df.rename({'date': 'Date', 'value': 'Weight', 'appleExerciseTime': 'ExerciseTime',
                'activeEnergyBurned': 'Calories'}, axis=1)
df['ExerciseTime'] = df.ExerciseTime.astype('int')
ExerciseTimeLevel = df.ExerciseTime.values
for i in range(len(ExerciseTimeLevel)):
    if ExerciseTimeLevel[i] <= 250:
        ExerciseTimeLevel[i] = 250
    elif  250 < ExerciseTimeLevel[i] <= 500:
        ExerciseTimeLevel[i] = 500
    elif 500 < ExerciseTimeLevel[i] <=750:
        ExerciseTimeLevel[i] = 750
    else:
        ExerciseTimeLevel[i] = 1000
df['ExerciseTimeLevel'] = ExerciseTimeLevel
df.to_csv('myweight.csv', index=False)
print('Output completed!')
# # plot
# plot = go.Scatter(x=df.Date, y=df.Weight,
#                   marker=dict(size=8, color=df.ExerciseTime, colorbar=dict(title='Colorbar'), colorscale='Viridis'),
#                   mode='lines+markers')
# py.iplot([plot], filename='basic', auto_open=True)


