import numpy as np

class BackTesting:

    ## Inicializamos el constructor
    def __init__(self, SL, TP, df_market, pip_value, points_spread, action_column='trade_action',result_column='Trade_Result', just_one=False, save_df=None):

        self.SL = SL
        self.TP = TP
        self.df_market = df_market
        self.pip_value = pip_value
        self.points_spread = points_spread
        self.action_column = action_column
        self.result_column = result_column
        self.just_one = just_one
        self.save_df = save_df

        self.buy_wins_returns = 0
        self.buy_loses_returns = 0
        self.sell_wins_returns = 0
        self.sell_loses_returns = 0
        self.count_buy_win = 0
        self.count_buy_lose = 0
        self.count_sell_win = 0
        self.count_sell_lose = 0

    ## Definimos los precios objetivo del SL y TP con spread
    def define_SL_and_TP(self):

        if self.SL is not None and self.TP is not None:
            if self.SL <= 0 or self.TP <= 0:
                raise Exception('TP y SL deben de ser mayores que 0')
            self.df_market['SL'] = self.SL
            self.df_market['TP'] = self.TP

        self.df_market['SL_value_buy'] = self.df_market['open'] - self.df_market['SL'] * self.pip_value + (self.points_spread * self.pip_value / 10)
        self.df_market['SL_value_sell'] = self.df_market['open'] + self.df_market['SL'] * self.pip_value - (self.points_spread * self.pip_value / 10)
        self.df_market['TP_value_buy'] = self.df_market['open'] + self.df_market['TP'] * self.pip_value + (self.points_spread * self.pip_value / 10)
        self.df_market['TP_value_sell'] = self.df_market['open'] - self.df_market['TP'] * self.pip_value - (self.points_spread * self.pip_value / 10)

    ## Calculamos las ganancias/perdidas en cada operacion
    def compute_return_trad(self, trade_row,future_df):

        index_win = 100000
        index_lost = 100000

        # Obtenemos posiciones cuando Buy toca SL o TP
        if trade_row[self.action_column] > 0:
            if len(np.where(future_df['high'] > trade_row['TP_value_buy'])[0]) > 0:
                index_win = np.where(future_df['high'] > trade_row['TP_value_buy'])[0][0]
            if len(np.where(future_df['low'] < trade_row['SL_value_buy'])[0]) > 0:
                index_lost = np.where(future_df['low'] < trade_row['SL_value_buy'])[0][0]

        # Obtenemos posiciones cuando Sell toca SL o TP
        elif trade_row[self.action_column] < 0:
            if len(np.where(future_df['low'] < trade_row['TP_value_sell'])[0]) > 0:
                index_win = np.where(future_df['low'] < trade_row['TP_value_sell'])[0][0]
            if len(np.where(future_df['high'] > trade_row['SL_value_sell'])[0]) > 0:
                index_lost = np.where(future_df['high'] > trade_row['SL_value_sell'])[0][0]

        # Vemos si toca antes TP o SL y calculamos ganancias/perdidas
        if index_win < index_lost:
            trade_result = self.TP
        elif index_win > index_lost:
            trade_result = -self.SL

        # Si tocan a la vez o no tocan perdemos spread
        else:
            trade_result = -self.points_spread

        # Si just_one=True no tenemos en cuenta las siguientes
        if self.just_one:
            index = np.min([index_win,index_lost])
            if index < 100000:
                if ~np.isnan(index):
                    self.df_market.loc[(self.df_market.time > trade_row.time) & (self.df_market.time <= future_df.iloc[np.min([index_win,index_lost])]['time']), 'action'] = 0
                else:
                    self.df_market.loc[(self.df_market.time == trade_row.time), 'action'] = 0
            elif index == 100000:
                self.df_market.loc[(self.df_market.time > trade_row.time), 'action'] = 0

        return trade_result

    ## Ejecutamos el BackTest
    def execute(self, metrics=False, verbose=False, profit_factor=True):

        self.df_market[self.result_column] = 0
        self.define_SL_and_TP()
        self.df_market.reset_index(inplace=True, drop=True)

        # Calculamos el resultado de la operacion
        df_trades = self.df_market[(self.df_market[self.action_column].abs() > 0)]
        for i, trade_row in df_trades.iterrows():
            future_df = self.df_market[self.df_market.time >= trade_row.time]
            future_df.reset_index(inplace=True, drop=True)
            if self.df_market.loc[self.df_market.time == trade_row.time,self.action_column].abs().iloc[0] == 1:
                trade_result = self.compute_return_trad(trade_row,future_df)
                self.df_market.loc[self.df_market['time'] == trade_row.time, self.result_column] = trade_result

        if self.just_one:
            self.df_market.loc[self.df_market[self.action_column] == 0, self.result_column] = 0

        # Calculamos las metricas del backtest
        if metrics:
            self.calculate_metrics(df_market_action=self.df_market, action_column=self.action_column, verbose=verbose)

        # Calculamos el profit factor acumulado
        if profit_factor:
            self.calculate_pf(self)

        return self.df_market

    ## Calculamos el beneficio neto y su std
    @staticmethod
    def net_std_pip(df_market_action,column):

        metric_pip_net_profit = df_market_action[column].sum()
        metric_pip_std_strategy = df_market_action[column].std()

        return metric_pip_net_profit , metric_pip_std_strategy

    ## Calculamos el ratio de Sharpe
    @staticmethod
    def sharpe_ratio(df_market_action, action_column, metric_pip_net_profit,metric_pip_std_strategy):

        sharpe_ratio = np.sqrt(len(df_market_action[df_market_action[action_column].abs() > 0])) * metric_pip_net_profit / metric_pip_std_strategy

        return sharpe_ratio

    ## Calculamos las operaciones positivas y negativas
    @staticmethod
    def trades_returns(df_market_action, action_column, direction, column='Trade_Result'):

        trades_wins_returns = df_market_action.loc[(df_market_action[action_column] == direction) & (df_market_action[column] > 0), column].sum()
        trades_loses_returns = df_market_action.loc[(df_market_action[action_column] == direction) & (df_market_action[column] < 0), column].sum()

        return trades_wins_returns, trades_loses_returns

    ## Obtenemos las metricas
    def calculate_metrics(self, df_market_action, action_column, verbose=False):

            # Generamos entradas aleatorias
            df_market_action['benchmark'] = 0
            df_market_action.loc[df_market_action[action_column].abs() > 0, 'benchmark'] = np.random.randint(1, 3, size=len(df_market_action.loc[df_market_action[action_column].abs() > 0, 'benchmark']))
            df_market_action.loc[df_market_action['benchmark'].abs() == 2, 'benchmark'] = -1
            df_market_action = BackTesting(pip_value=self.pip_value, points_spread=self.points_spread, action_column='benchmark', SL=self.SL, TP=self.TP, df_market=df_market_action, result_column='Trade_Result_benchmark', just_one=False).execute(metrics=False)

            # Calculamos el beneficio neto y su std
            metric_pip_net_profit , metric_pip_std_strategy = self.net_std_pip(df_market_action,'Trade_Result')
            metric_pip_net_profit_bench, metric_pip_std_strategy_bench = self.net_std_pip(df_market_action, 'Trade_Result_benchmark')
            sharpe_ratio = self.sharpe_ratio(df_market_action, action_column, metric_pip_net_profit,metric_pip_std_strategy )
            sharpe_ratio_benchmark = self.sharpe_ratio(df_market_action, action_column, metric_pip_net_profit_bench, metric_pip_std_strategy_bench )

            if verbose:
                print('NET PROFIT ALGO:', metric_pip_net_profit, 'NET PROFIT BENCH:', metric_pip_net_profit_bench)
                print('STD ALGO:', metric_pip_std_strategy, 'STD BENCH:', metric_pip_std_strategy_bench)
                print('SHARPE RATIO ALGO:', sharpe_ratio, 'SHARPE RATIO BENCH:', sharpe_ratio_benchmark)

            # Calculamos las operaciones positivas y negativas y profit factor
            buy_wins_returns , buy_loses_returns = self.trades_returns(df_market_action, action_column, direction=1, column='Trade_Result')
            sell_wins_returns, sell_loses_returns = self.trades_returns(df_market_action, action_column, direction=-1, column='Trade_Result')
            buy_wins_returns_bench, buy_loses_returns_bench = self.trades_returns(df_market_action, action_column, direction=1, column='Trade_Result_benchmark')
            sell_wins_returns_bench, sell_loses_returns_bench = self.trades_returns(df_market_action, action_column, direction=-1, column='Trade_Result_benchmark')

            count_buy_wins = len(df_market_action[(df_market_action[action_column] == 1) & (df_market_action['Trade_Result'] > 0)])
            count_sell_wins = len(df_market_action[(df_market_action[action_column] == -1) & (df_market_action['Trade_Result'] > 0)])
            count_buy_lose = len(df_market_action[(df_market_action[action_column] == 1) & (df_market_action['Trade_Result'] < 0)])
            count_sell_lose = len(df_market_action[(df_market_action[action_column] == -1) & (df_market_action['Trade_Result'] < 0)])

            profit_factor = (buy_wins_returns + sell_wins_returns) / -(buy_loses_returns + sell_loses_returns)
            profit_factor_benchmark = (buy_wins_returns_bench + sell_wins_returns_bench) / -(buy_loses_returns_bench + sell_loses_returns_bench)

            average_pip_win = (buy_wins_returns + sell_wins_returns) / (count_buy_wins + count_sell_wins)
            average_pip_lose = (buy_loses_returns + sell_loses_returns) / (count_buy_lose + count_sell_lose)

            if verbose:
                print('NUMBER OF OPS BUY:', count_buy_lose+count_buy_wins, 'NUMBER OF OPS BUY WIN:', count_buy_wins , 'NUMBER OF OPS SELL:', count_sell_lose+count_sell_wins,'NUMBER OF OPS SELL WIN:', count_sell_wins)
                print('NUMBER OF OPS:', (count_buy_wins + count_sell_wins)+(count_buy_lose + count_sell_lose))
                print('PROFIT FACTOR:', profit_factor, '\nPROFIT FACTOR BENCHMARK:', profit_factor_benchmark, '\nPIPS AVERAGE:', average_pip_win, '\nPIPS AVERAGE BENCHMARK:', average_pip_lose)

            self.buy_wins_returns = buy_wins_returns
            self.buy_loses_returns = buy_loses_returns
            self.sell_wins_returns = sell_wins_returns
            self.sell_loses_returns = sell_loses_returns
            self.count_buy_win = count_buy_wins
            self.count_buy_lose = count_buy_lose
            self.count_sell_win = count_sell_wins
            self.count_sell_lose = count_sell_lose

    ## Calculamos el profit factor acumulado
    @staticmethod
    def calculate_pf(self):

        self.df_market['Profit_Factor'] = 0
        wins_returns = 1e-4
        loses_returns = 1e-4
        for i, trade_row in self.df_market.iterrows():
            result = trade_row.Trade_Result
            if result < 0:
                loses_returns += -result
                pf = wins_returns / loses_returns
            elif result > 0:
                wins_returns += result
                pf = wins_returns / loses_returns
            else:
                pf = wins_returns / loses_returns

            self.df_market.loc[self.df_market['time'] == trade_row.time, 'Profit_Factor'] = pf