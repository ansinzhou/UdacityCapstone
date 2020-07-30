import matplotlib.pyplot as plt
import io
import base64

from fanyuanapp import marketdataManager

def generate_save_plot(summery):
    marketdataManager.load_benchmarks_from_stock_dfs()

    img = io.BytesIO()

    plt.switch_backend('Agg')

    plt.style.use('ggplot')

    returns = marketdataManager.query_backtest_returns(summery.id)
    # print("returns size:", len(returns))

    previousdate = marketdataManager.get_previous_trade_date('^GSPC', summery.start)
    if previousdate == None:
        previousdate = summery.start
        returns = returns[1:]

    if summery.hongkongmarket>0:
        hkhsi_returns = marketdataManager.get_index_return('HKHSI', previousdate, summery.end)
        plt.figure(figsize=(10.8, 4), dpi=100)

        plt.plot(hkhsi_returns, label=f"HKHSI ({round(hkhsi_returns[-1],4)})")
        plt.plot(hkhsi_returns.index, returns, color='g', label=f"BackTest ({round(returns[-1],4)})")
        days = len(hkhsi_returns.index)
        skipdays = int(days/12)
        plt.xticks(hkhsi_returns.index[::skipdays])
    else:
        spy_returns = marketdataManager.get_index_return('^GSPC', previousdate, summery.end)

        dow_returns = marketdataManager.get_index_return('^DJI', previousdate, summery.end)

        nasdaq_returns = marketdataManager.get_index_return('^IXIC', previousdate, summery.end)

        plt.figure(figsize=(10.8, 4), dpi=100)

        plt.plot(spy_returns, color='y', label=f"S&P ({round(spy_returns[-1],4)})")
        plt.plot(dow_returns, label=f"DOW ({round(dow_returns[-1],4)})")
        plt.plot(nasdaq_returns, label=f"Nasdaq ({round(nasdaq_returns[-1],4)})")
        days = len(spy_returns.index)

        plt.plot(spy_returns.index, returns, color='g', label=f"BackTest ({round(returns[-1],4)})")
        skipdays = int(days/12)
        plt.xticks(spy_returns.index[::skipdays])
    plt.gcf().autofmt_xdate()





    plt.title("Portfolio Returns")

    plt.ylabel("Return")

    plt.legend()

    plt.tight_layout()


    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return 'data:image/png;base64,{}'.format(graph_url)


def generate_save_buy_graph(summery):
    img = io.BytesIO()

    plt.switch_backend('Agg')
    # plt.style.use('ggplot')

    (days, boughtstocks) = marketdataManager.query_daily_buyinfo(summery.id)

    plt.figure(figsize=(10.8, 4), dpi=100)

    plt.bar(days, boughtstocks, color='b')

    plt.gcf().autofmt_xdate()

    num_days = len(days)
    skipdays = int(num_days/12)
    plt.xticks(days[::skipdays])


    plt.title("Number of Daily Bought Stocks")

    plt.ylabel("Stocks")

    plt.legend()

    plt.tight_layout()

    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return 'data:image/png;base64,{}'.format(graph_url)
