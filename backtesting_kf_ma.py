from utils.backtesting import BackTesting
from utils.utils import conexion, preprocesado
from utils.optimization import optimize
from utils.bollinger_bands import bollinger
from warnings import filterwarnings
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import matplotlib.pyplot as plt

## Ignoramos los avisos y establecemos conexion con el servidor
filterwarnings('ignore')
conexion()

## Definimos la divisa y el timeframe
symbol = 'EURUSD'
timeframe = mt5.TIMEFRAME_H1

## Definimos los parametros de la estrategia de las bandas de Bollinger con KF
sigma_meas = 1e-3
window_std = 48
factor = 2
contradir = False

## Definimos los parametros que ajustan sigma_model
window_cma = 48
order = 2
delta = 20

## Definimos las variables del backtest
TP = 50
SL = 50
pip = mt5.symbol_info(symbol).point * 10
spread = 5

## Definimos la duracion del periodo de entrenamiento
hours_train = 14 * 24

## Definimos el periodo de backtest
date_to = datetime(2021,6,14,23,0,0)
date_from = datetime(2019,6,14,23,0,0)

## Descargamos el dataset
date_from_total = date_from - timedelta(hours=hours_train)
df = preprocesado(symbol, timeframe, date_from=date_from_total, date_to=date_to, method='range')

## Comenzamos las iteraciones
df['action_kf'] = 0 ; df['action_ma'] = 0 ; iter = 0
for date in df['time'].loc[df['time'] > format(date_from)]:

    iter += 1
    print('ITER: {}, DATE: {}'.format(iter, date))

    # Obtenemos los historicos de entrenamiento
    date_from_train = date - timedelta(hours=hours_train)
    df_train_kf = df.loc[(df['time'] > date_from_train) & (df['time'] < date)].copy().reset_index(drop=True)

    # Actualizamos sigma_model cada 24 horas (al cierre del mercado, el cual es tras el cierre de la vela de las 23:00)
    if df_train_kf['time'][len(df_train_kf) - 1].hour % 23 == 0 or iter == 1:
        sigma_model = optimize(df_train=df_train_kf, window_cma=window_cma, sigma_meas=sigma_meas, delta=delta, order=order)

    # Representamos cada 24 horas (al cierre del mercado, el cual es tras el cierre de la vela de las 23:00)
    plot = False ; signal = True
    if df_train_kf['time'][len(df_train_kf) - 1].hour % 23 == 0:
        plot = True

    # Obtenemos la posicion de la estrategia de las bandas de bollinger en la iteracion actual y las almacenamos
    act_kf, act_ma = bollinger(df=df_train_kf.copy(), sigma_meas=sigma_meas, sigma_model=sigma_model, window_ma=window_cma, factor=factor, window_std=window_std, contradir=contradir, plot_kf=plot, plot_ma=plot, signal=signal)
    df.loc[df['time'] == date, 'action_kf'] = act_kf
    df.loc[df['time'] == date, 'action_ma'] = act_ma

## Creamos el dataframe para el backtest de la estrategia
df_backtest = df.loc[df['time'] > format(date_from)].copy().reset_index(drop=True)

## Realizamos el backtest a la estrategia basada en kf
backtest_kf = BackTesting(df_market=df_backtest, SL=SL, TP=TP, pip_value=pip, points_spread=spread, action_column='action_kf', result_column='Trade_Result', just_one=False, save_df=df_backtest)
print('-'*10,'BACKTEST KF','-'*10)
result_kf = backtest_kf.execute(metrics=True, verbose=True)

## Representamos las decisiones tomadas durante el proceso
plt.plot(result_kf['close'], c='b', label='market')
plt.plot(result_kf.loc[result_kf['action_kf'] == 1, 'close'], '^g')
plt.plot(result_kf.loc[result_kf['action_kf'] == -1, 'close'], 'vr')
plt.title('Strategy KF') ; plt.legend() ; plt.show()

## Representamos la evolucion del profit factor durante el proceso
plt.plot(result_kf['Profit_Factor'][400:], c='b', label='Profit Factor')
plt.axhline(y=1)
plt.title('Profit Factor KF') ; plt.legend() ; plt.show()

## Realizamos el backtest a la estrategia basada en ma
backtest_ma = BackTesting(df_market=df_backtest, SL=SL, TP=TP, pip_value=pip, points_spread=spread, action_column='action_ma', result_column='Trade_Result', just_one=False, save_df=df_backtest)
print('-'*10,'BACKTEST MA','-'*10)
result_ma = backtest_ma.execute(metrics=True, verbose=True)

## Representamos las decisiones tomadas durante el proceso
plt.plot(result_ma['close'][400:], c='b', label='market')
plt.plot(result_ma.loc[result_ma['action_ma'] == 1, 'close'], '^g')
plt.plot(result_ma.loc[result_ma['action_ma'] == -1, 'close'], 'vr')
plt.title('Strategy MA') ; plt.legend() ; plt.show()

## Representamos la evolucion del profit factor durante el proceso
plt.plot(result_ma['Profit_Factor'], c='b', label='Profit Factor')
plt.axhline(y=1)
plt.title('Profit Factor MA') ; plt.legend() ; plt.show()