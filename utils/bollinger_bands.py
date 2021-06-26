from numpy import where
import matplotlib.pyplot as plt
from utils.kalman_filter import KF

## Estrategia usando las bandas de Bollinger con kf y ma
def bollinger(df, column='close', sigma_meas=1e-3, sigma_model=1e-5, window_ma=21, window_std=21, factor=2, contradir=True, plot_kf=False, plot_ma=False, signal=False):

    # Obtenemos las bandas de Bollinger
    df['KF'] = KF(zs=df[column], sigma_meas=sigma_meas, sigma_model=sigma_model)
    df['MA'] = df[column].rolling(window=window_ma).mean()
    df['STD'] = df[column].rolling(window=window_std).std()
    df['BOLLINGER_UP_KF'] = df['KF'] + factor * df['STD']
    df['BOLLINGER_UP_MA'] = df['MA'] + factor * df['STD']
    df['BOLLINGER_DOWN_KF'] = df['KF'] - factor * df['STD']
    df['BOLLINGER_DOWN_MA'] = df['MA'] - factor * df['STD']

    # Obtenemos la decision de la estrategia (contradireccional)
    df['action_kf'] = where(df[column] > df['BOLLINGER_UP_KF'], -1, 0)
    df['action_kf'] = where(df[column] < df['BOLLINGER_DOWN_KF'], 1, df['action_kf'])
    df['action_ma'] = where(df[column] > df['BOLLINGER_UP_MA'], -1, 0)
    df['action_ma'] = where(df[column] < df['BOLLINGER_DOWN_MA'], 1, df['action_ma'])

    # Si la estrategia es direccional, cambiamos compras por ventas y viceversa
    if not contradir:
        df['action_kf'] = -1 * df['action_kf']
        df['action_ma'] = -1 * df['action_ma']

    # Representamos los datos
    if plot_kf:
        plt.plot(df[column], c='grey', label='Market')
        plt.plot(df['KF'], c='blue', label='Kalman filter')
        plt.plot(df['BOLLINGER_UP_KF'], c='red', label='Bollinger up')
        plt.plot(df['BOLLINGER_DOWN_KF'], c='red', label='Bollinger down')
        if signal:
            plt.plot(df.loc[df['action_kf'] == 1, 'close'], '^g')
            plt.plot(df.loc[df['action_kf'] == -1, 'close'], 'vr')
        plt.title('Bollinger Bands KF') ; plt.show()
    if plot_ma:
        plt.plot(df[column], c='grey', label='Market')
        plt.plot(df['KF'], c='blue', label='Moving average')
        plt.plot(df['BOLLINGER_UP_MA'], c='red', label='Bollinger up')
        plt.plot(df['BOLLINGER_DOWN_MA'], c='red', label='Bollinger down')
        if signal:
            plt.plot(df.loc[df['action_ma'] == 1, 'close'], '^g')
            plt.plot(df.loc[df['action_ma'] == -1, 'close'], 'vr')
        plt.title('Bollinger Bands MA') ; plt.show()

    # Devolvemos la ultima decision tomada disponible para las 3 estrategias
    return df['action_kf'][len(df) - 1], df['action_ma'][len(df) - 1]