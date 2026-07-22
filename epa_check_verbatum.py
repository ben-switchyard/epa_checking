import pip
import smtplib
import datetime
pip.main(['install', 'sinbad'])

from sinbad import *

ds = DataSource.connect("https://www.fueleconomy.gov/ws/rest/vehicle/menu/model", format="xml")
ds.set_param("year", "2024")
ds.set_param("make", "Ford")
ds.load()
makes = ds.fetch('text')

#Print all 2022 Fords
print(makes)

# is there a record for hybrid?
[x for x in makes if 'Maverick' in x and 'HEV' in x]
valid = [x for x in makes if 'Maverick' in x and 'HEV' in x]
if not valid:
  valid = [x for x in makes if 'Maverick' in x and 'FWD' in x]

# valid = 'Maverick AWD' if [x for x in makes if 'ybrid' in x]  else [x for x in makes if 'ybrid' in x]

print(valid)

available = 'Not checked'
if [x for x in makes if 'Maverick' in x and 'HEV' in x]:
  available = True
else:
  available = False

print(available)

makelist = '\n'.join(makes)

ds = DataSource.connect("http://www.fueleconomy.gov/ws/rest/vehicle/menu/options", format="xml")
ds.set_param("year", "2022")
ds.set_param("make", "Ford").set_param("model", valid[0])
ds.load()

num = ds.fetch('value')
print(num)
if isinstance(num, list):
  num=num[0]

ds = DataSource.connect_load("http://www.fueleconomy.gov/ws/rest/vehicle/"+num, format="xml")
mpgdata = (ds.fetch("make", "model", "trany", "year", "city08", "highway08","comb08") )
mpgdataprint = ('make: '+mpgdata['make'],'model: '+mpgdata['model']+'\nyear: '+mpgdata['year']+'\nCity MPG: '+mpgdata['city08']+'\nHighway MPG: '+mpgdata['highway08']+'\nCombo MPG: '+mpgdata['comb08'])

mpgdatalist = '\n'.join(mpgdataprint)
print(mpgdatalist)

personalemail = 'test@gmail.com'
passwordkey = 'ENTERPASS'
toAddress = [personalemail]

#import datetime
# record = []
#record.append(datetime.datetime.now().strftime("%a, %d %B %Y %H:%M:%S"))
#print('\n'.join(record))

from google.colab import drive
drive.mount('/content/drive')

with open('/content/drive/MyDrive/EPA.txt', 'a') as writefile:
    writefile.write(datetime.datetime.now().strftime("%a, %d %B %Y %H:%M:%S")+'\n')

with open('/content/drive/MyDrive/EPA.txt', 'r') as testwritefile:
    print(testwritefile.read())
