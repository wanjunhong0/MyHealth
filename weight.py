import pandas as pd
from xml.etree import ElementTree
import zipfile


path = 'data/export.zip'
# read zip file
print('Reading zip file in {0} ...'.format(path))
file = zipfile.ZipFile(path, 'r')
# read xml file
tree = ElementTree.parse(file.open('apple_health_export/export.xml'))
root = tree.getroot()
# get tag
tags = []
for i in root:
    tags.append(i.tag)
tags = set(tags)
# get data for each tag
data = {i: [] for i in tags}
for tag in tags:
    for i in root.findall(tag):
        data[tag].append(i.attrib)
    print('Found {0} {1} data!'.format(len(data[tag]), tag))
print('Read xml file completed!')


# processing weight data
weight = []
for i in data['Record']:
    if i['type'] == 'HKQuantityTypeIdentifierBodyMass':
        weight.append(i)
weight = pd.DataFrame(weight)
weight = weight.round({'value': 1})
assert weight.unit.unique() == 'kg'
weight['time'] = pd.to_datetime(weight.startDate.map(lambda x: x[: -6]))
weight['date'] = pd.to_datetime(weight.time.dt.date)
weight['week'] = weight.date.map(lambda x: 100 * x.year + x.week)
weight = weight[['week', 'date', 'value']]

# read workout data
workout = []
for i in data['ActivitySummary']:
    workout.append(i)
workout = pd.DataFrame(workout)
workout.activeEnergyBurned = workout.activeEnergyBurned.astype('float').astype('int')
workout.appleExerciseTime = workout.appleExerciseTime.astype('int')
workout = workout[workout.activeEnergyBurned > 0]
workout['week'] = pd.to_datetime(workout.dateComponents).map(lambda x: 100 * x.year + x.week)
workout = workout.groupby(by=['week'], as_index=False)[['appleExerciseTime', 'activeEnergyBurned']].sum()

# merge dateset by week
df = pd.merge(weight, workout, how='left', left_on='week', right_on='week')
df = df.dropna()
del df['week']
df = df.rename({'date': 'Date', 'value': 'Weight', 'appleExerciseTime': 'ExerciseTime',
                'activeEnergyBurned': 'Calories'}, axis=1)
df['ExerciseTime'] = df.ExerciseTime.astype('int')
df['ExerciseTimeLevel'] = pd.cut(df.ExerciseTime, bins=[0, 250, 500, 750, 1000, 1250, 1500, 1750, 2000], right=False,
                                 labels=['0 ~ 250', '250 ~ 500', '500 ~ 750', '750 ~ 1000',
                                         '1000 ~ 1250', '1250 ~ 1500', '1500 ~ 1750', '1750 ~ 2000'])
df.to_csv('myweight.csv', index=False)
print('Output csv file completed!')



