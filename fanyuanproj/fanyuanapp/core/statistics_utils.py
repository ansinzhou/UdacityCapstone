import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
from scipy import stats
import seaborn as sns
import numpy as np

import fanyuanapp.core.constants as constants

from fanyuanapp import marketdataManager

def get_beta_alpha_sharpe(history_record, start, end, ishongkongstock):
    # print(f'get_beta_alpha_sharpe:\n {history_record}')
    history_record[constants.RETURNS] = history_record[constants.RETURNS].astype(float)

    port_ret = history_record[constants.RETURNS]

    if ishongkongstock:
        ticker = 'HKHSI'
    else:
        ticker = '^GSPC'
    prev_start = marketdataManager.get_previous_trade_date(ticker, start)
    if prev_start == None:
        prev_start = start
        port_ret = port_ret[1:]

    benchmark_ret = marketdataManager.get_benchmark_pct_change(ticker, prev_start, end)

    sns.regplot(benchmark_ret.values, port_ret.values)

    (beta, alpha) = stats.linregress(benchmark_ret.values, port_ret.values)[0:2]

    # print("The portfolio beta is", round(beta, 4))
    #
    # print("The portfolio alpha is", round(alpha,5))

    totaldays = len(history_record.index)
    sharpe_ratio = port_ret.mean()/port_ret.std()
    sharpe_ratio = (totaldays**0.5)*sharpe_ratio

    return (round(beta, 4), round(alpha,5), round(sharpe_ratio, 5))


def calculate_fortfolio_volatility(history_record):
    history_record[constants.RETURNS] = history_record[constants.RETURNS].astype(float)

    d_returns = history_record[constants.RETURNS]

    trading_days = len(d_returns.index)

    cov_matrix_d = d_returns.cov()

    cov_matrix_a = cov_matrix_d * trading_days

    weights = np.array([1])  # assign equal weights

    # calculate the variance and risk of the portfolo
    port_variance = np.dot(weights.T, np.dot(cov_matrix_a, weights))
    port_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix_a, weights)))

    percent_var = str(round(port_variance, 4) * 100)
    percent_vols = str(round(port_volatility, 4) * 100)

    return (percent_var, percent_vols)
