# UdacityCapstone
Udacity Data Scientist program capstone project


# Table of contents
1. [Instructions](#Instructions)
2. [Installation](#Installation)
3. [Motivation](#Motivation)
4. [Repository Structure](#Structure)
5. [WebApp User Guide](#Webapp)
6. [Results](#Results)
7. [Licensing, Authors, Acknowledgements](#Licensing)



## Instructions <a name="instructions"></a>
The project is seperated into two parts; a web app, and a experimental ipyb file. Findings and Anlaysis form the ipyb file is posted on a medium article.

1. WebApp
  - To run WebApp: from command window go to fanyuanapp directory, then in comman window type python run.py
  - From your broswer: http://localhost:5000
2. Ipyb File
  - Medium Link: https://medium.com/@ansin0517/machine-learning-screeners-for-stock-trading-ab698bc3df02
  
  
## Installation <a name="installation"></a>
The required libraries and installations are:

1. Anaconda (python3)
2. pip install yfinance --upgrade --no-cahe-dir
3. pip install flask
4. pip install flask-wtf
5. pip install flask-sqlalchemy
6. pip install scipy
7. pip install seaborn
8. sklearn
9. matplotlib
10. tensorflow



## Motivation <a name="Motivation"></a>
As the capstone project of the Udacity Data Scientist program, I have chosen to do a pilot project for FanYuan Investment Management; they have graciously provided data and experimental data neccessary.
In the first part(webapp) of the project, it was requested that a webapp was created to achieve the following goals:
1. Allow for accurate backtesting of stocktrades.
2. Allow for custom upload of Buys and Sells.
3. Allow for generation of Sells according to inputed variables through the webapp.
4. Allow for an abundant of results statistics generation.
5. Allow for storage of results for later access.
6. Usable for new strategy backtesting and analyzation, and old strategy statistics generation.

In the second part(ipyb file) project, it was requested to achieve the following goals:
1. expirment with creating a potential screener for stock universe
2. evaluation of screener
3. analysis of potential inclusion of screener in trading strategy.


## Repository Structure <a name="Structure"></a>
- The ipyinb file is the code notebook file containing all the codes written to clean and wrangle data, to analyzing data and producing model and graphs.
- The csv file is contained in the zip folder, it is the raw file supplied by Pan-Origins LLC, containing raw data over the last three years, of their indicators. including the features and targets used in this project.
- The assets folder contains graphs and pictures generated and produced that is used in the deployment of this projet on the blog site.


## WebApp User Guide <a name="Webapp"></a>
A step by step user guideline, with test data ready for use to test the webapp:
1. Under Indicator click create indicator.
2. Input a name for indicator name (e.g testdata)
3. Click choose file, under fayuanproj directory, to to user_inputs folder and select HKClose
4. Click on checkmark for Hong Kong Stock, because the input csv file is hong kong stocks, otherwise if it's U.S traded stocks, checkmark would be left blank.
5. In sequence, input these variable values starting from Max Stocks In Holding: 20 , 20, 6, 6, -8, 5, 500000, 0.0001, 0.0001.
6. Trading variables are needed to generate sell points, different variables can be inputed; for example, if the stock traded was shorted then the profit target and cut loss would be reversed(eg: -6,-6,8). For testing purposes, stick with the above given variable values. Can be experiemented with later.
7. Click create at the bottom
8. Once indicator is created, click on the created indicator name. Click on Buy Info to double check buy points are uploaded correctly. Upload of custom sell points is availble through clicking the top right upload button. However, for testing purposes, we'll stick with the inputed variables generated sell points.
9. Next, under backtest click Make a backtest.
10. Input any test name (eg. Test123)
11. The current data and test data supports backtesting between 2008-01-01 to 2019-12-31. Select testing range(eg. Start Date 2018-01-12 , End Date 1029-12-15)
12. Check the Use For Test box for the indicator previously created(testdata). Leave Use Sell Indicator box blank, since we're not using custom uploaded sell data.
13. Click Run & Save
14. After a few moments, a result report is generated. Different metrics are calculated and can be seen under different tabs, such as return against benchmark graph and more. Ohter tabs such as Daiy Summeries shows a EOD PL extra.
15. Under Backtest, on the top navigation bar, click test summaries to see all past backtest reports.
16. Under backtest of navigation bar, click global variables to change inputs such as leverage and starting cash etc.




## Results <a name="Results"></a>

1. WebApp

   The WebApp successfully fullfills requirements of FanYuan Investment Managment, however further improvements can be made such as hosting the webapp, and having all local database live, so users wouldn't have to download large files. A live trading management section can be added, and optimization features such as ML screeners, and parameters tuning can be potentially added in the future.

2. Experiemental screener(ipyb file)

   Detailed results can be seen at : https://medium.com/@ansin0517/machine-learning-screeners-for-stock-trading-ab698bc3df02


## Licensing, Authors, Acknowledgements <a name="Licensing"></a>
Must give special thanks to Pan-Origins LLC and FanYuan Investment Management for providing the csv data, which is availble for public use. Feel free to use the code provided that you give credits / cite this repo, as well as to contribute.
