import os
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import datetime as dt
import glob

import fanyuanapp.core.constants as constants

INPUT_DATE_FORMAT = '%d-%m-%Y'

datapath = os.path.join(constants.MARKETDATA_FOLDER, "*.csv")
print(datapath)

names = glob.glob(datapath)
# print(names[0])

for name in names:
    marketData = pd.read_csv(name)
    for row_index, row in marketData.iterrows():
        try:
            originDateStr = row[constants.DATE_COLUMN]
            originDate = dt.datetime.strptime(originDateStr, INPUT_DATE_FORMAT)
            newDateStr = originDate.strftime(constants.DATE_FORMAT)
            marketData.at[row_index, constants.DATE_COLUMN] = newDateStr
        except ValueError as error:
            print(name, error)
    marketData.to_csv(name, index=False)
