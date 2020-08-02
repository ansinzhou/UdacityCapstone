# UdacityCapstone
Udacity Data Scientist program capstone project


# Table of contents
1. [Instructions](#Instructions)
2. [Installation](#Installation)
3. [Motivation](#Motivation)
4. [Repository Structure](#Structure)
5. [WebApp User Guide](#Webapp)
6. [Metrics](#Metrics)
7. [Analysis](#Analysis)
5. [Methodology](#Methodology)
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
3. Click choose file, under fayuanproj directory, to to user_inputs folder and select testinput
4. Click on checkmark for Hong Kong Stock, because the input csv file is hong kong stocks, otherwise if it's U.S traded stocks, checkmark would be left blank.
5. In sequence, input these variable values starting from Max Stocks In Holding: 20 , 20, 6, 6, -8, 1, 1000, 0.0001, 0.0001.
6. Trading variables are needed to generate sell points, different variables can be inputed; for example, if the stock traded was shorted then the profit target and cut loss would be reversed(eg: -6,-6,8). For testing purposes, stick with the above given variable values. Can be experiemented with later.
7. Click create at the bottom
8. Once indicator is created, click on the created indicator name. Click on Buy Info to double check buy points are uploaded correctly. Upload of custom sell points is availble through clicking the top right upload button. However, for testing purposes, we'll stick with the inputed variables generated sell points.
9. Next, under backtest click Make a backtest.
10. Input any test name (eg. Test123)
11. Select test date range: Start date 2016-01-01  End date 2016-02-01.
12. In normal circumstances all market data would be availble for all U.S and HongKong stocks for all dates from 2008 to 2020, however this test version only has marketdata for the testinput stocks.
13. Check the Use For Test box for the indicator previously created(testdata). Leave Use Sell Indicator box blank, since we're not using custom uploaded sell data.
14. Click Run & Save
15. After a few moments, a result report is generated. Different metrics are calculated and can be seen under different tabs, such as return against benchmark graph and more. Ohter tabs such as Daiy Summeries shows a EOD PL extra.
16. Under Backtest, on the top navigation bar, click test summaries to see all past backtest reports.
17. Under backtest of navigation bar, click global variables to change inputs such as leverage and starting cash etc.



## Metrics <a name="Metrics"></a>

- Metrics for the WebApp are the generated return , and daily P/L in the results page. It evaluates a strategies peformance and indicates whether a strategy is usable in real world scenarios. 

- Metrics used for  the screener are accruacy, confusion matrix, and standard deviation. Metrics are chosen because the main intrest is the prediction accuracy of the model, hence gaging if it would translate into the real world.


## Analysis <a name="Analysis"></a>

The features and calculated statistics relevant to the datset are calculated and reported through the WebApp, the webapp will return different numbers depending on the uploaded and tested dataset.

1. In the WebApp generated report under statistics tab, calculated reatures and statistics are the following:
    - Beta
    - Alpha
    - Sharpe
    - Win(%)
    - Loss(%)
    - Coverage(%)
    - Turnover
    - Cash used
    - Leverage
    - Average stock in holding
    - Average holding period per stock
    - Max drawdown(%)
    - Lowest return(%)
    - Actual number of trades
    - No trades due to volume restriction
    - No trades to to shortage of cash
    - Number of potential trades
 
2. In the WebApp generated report under statistics tab, derived features from original dataset are the following:
    - Transaction type
    - Unit price
    - Unit quantity
 
3.  In the WebApp generated report under daily positions tab, derived features from the original dataset are the following:
    - Current unit price
    - Unit quantity
    - Position
    - Holding period
    - Gain/Loss

4.  In the WebApp generated report under daily summeries tab, derived features from the original dataset are the following:
    - Daily returns
    - Daily cash
    - Daily stock holding value
    - Daily actual portfolio value
    - Daily leveraged portfolio value
    - Daily leverage
    - Daily drawdown
    
5.  In the WebApp generated report under Statistics tab, the following visualizations are generated to help users better understand their trading strategy: 
    - Plotted return line against benchmark.
    - Bar graph of number of daily bought stocks.



## Methodology <a name="Methodology"></a>
   
   - Preprocessing the dataset given for building the model includes 9 steps:
     1. Importing dataset
     2. Dropping all unneeded columns: Dropping all the 'Label' columns because they only contain nan values and isn't useful.
     3. Only interested in rows where Shortbuy happnened. Hence dropping all rows where shortbuy=0
     4. Dropping rows where ShortBuy and BuyWINLOSS are nans, ShortBuy is the data interested in, BuyWINLOSS is the y dependent variable.
     5. Shortbuy not needed for model training and calculations, after the first 4 steps, shorbuy becomes unuseful and dropped.
     6. Filling the rest of the missing values with mean
     7. Splitting dataset into independent variables(X) and the dependent variable(y)
     8. Performing features scaling on X
     9. Splitting the dataset into the training set and test set
    
   
   - One supervised model was chosen for the dataset and one unsupervised model was chosen, to compare accuracies of the two different type of models; in superviesd models it was previously found that in this situations, random forest classifier generates the highest accuracy. The article to previous findings can be found here: https://medium.com/@ansin0517/quantitative-hedgefunds-what-happens-when-your-5-day-moving-average-crosses-above-the-c357bd8e16b7

   - The unsupervised model was chosen to see if machine generated logic and weights would provide better results as model accuracy. Because generally, all stockmarket related trade data is easily collected or purchased, there is abundent data available, and unsupervised model tends to work better and improve with bigger data.
   
  
## Results <a name="Results"></a>

1. WebApp

   The WebApp successfully fullfills requirements of FanYuan Investment Managment, however further improvements can be made such as hosting the webapp, and having all local database live, so users wouldn't have to download large files. A live trading management section can be added, and optimization features such as ML screeners, and parameters tuning can be potentially added in the future.

2. Experiemental screener(ipyb file)

   Detailed results can be seen at : https://medium.com/@ansin0517/machine-learning-screeners-for-stock-trading-ab698bc3df02


## Licensing, Authors, Acknowledgements <a name="Licensing"></a>
Must give special thanks to Pan-Origins LLC and FanYuan Investment Management for providing the csv data, which is availble for public use. Feel free to use the code provided that you give credits / cite this repo, as well as to contribute.
