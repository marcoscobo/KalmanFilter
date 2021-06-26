from datetime import datetime, timedelta
from utils.utils import conexion, preprocesado
from utils.optimization import optimize
from utils.kalman_filter import KF
import matplotlib.pyplot as plt
import numpy as np
import MetaTrader5 as mt5

## Establecemos la conexion con el servidor
conexion()

""" SENSIBILIDAD DIMENSION """

## Definimos la divisa y el timeframe
symbol = 'EURGBP'
timeframe = mt5.TIMEFRAME_H1

## Descargamos los historicos
date_from = datetime.now() - timedelta(days=5)
date_to = datetime.now()
df = preprocesado(symbol=symbol, timeframe=timeframe, date_to=date_to, date_from=date_from)

## Establecemos los parametros de los modelos (sin)
sigma_meas = 0.0005
sigma_model = 0.0002

## Calculamos los vectores de filtrado (sin)
n = 1
kf1 = KF(zs=df['close'], n=n, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)
n = 2
kf2 = KF(zs=df['close'], n=n, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)
n = 3
kf3 = KF(zs=df['close'], n=n, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)
n = 4
kf4 = KF(zs=df['close'], n=n, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)

## Representamos los vectores calculados (sin)
plt.figure()
plt.plot(kf1, 'b', label='Kalman Filter 1D')
plt.plot(kf2, 'g', label='Kalman Filter 2D')
plt.plot(kf3, 'r', label='Kalman Filter 3D')
plt.plot(kf4, 'cyan', label='Kalman Filter 4D')
plt.plot(df['close'], 'm--', label='Measure')
plt.legend() ; plt.axis('off') ; plt.show()

""" SENSIBILIDAD S_MODEL """

## Creamos el dataset
muestra = 100
dt = 0.1
noise = 0.03
t1 = (np.arange(muestra) - muestra / 2) * dt
z1 = np.sin(t1)
sin = []
for i in range(muestra):
    sin.append(z1[i] + np.random.normal(0, noise))
muestra = 200
dt = 0.1
noise = 0.01
t2= (np.arange(muestra)-muestra/2) * dt
z2 = 1/(1+np.exp(-3*t2))
sigm = []
for i in range(muestra):
    sigm.append(z2[i] + np.random.normal(0, noise))


## Establecemos los parametros de los modelos (sin)
n = 2
sigma_meas = 0.03

## Calculamos los vectores de filtrado (sin)
sigma_model = 0.01
kf1 = KF(zs=sin, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)
sigma_model = 0.02
kf2 = KF(zs=sin, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)
sigma_model = 0.05
kf3 = KF(zs=sin, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)

## Representamos los vectores calculados (sin)
plt.figure()
plt.plot(t1, kf1, 'b', label='Kalman Filter 2D, s = 0.01')
plt.plot(t1, kf2, 'g', label='Kalman Filter 2D, s = 0.02')
plt.plot(t1, kf3, 'r', label='Kalman Filter 2D, s = 0.05')
plt.plot(t1, sin, 'm--', label='Measure')
plt.legend() ; plt.axis('off') ; plt.show()

## Establecemos los parametros de los modelos (sigm)
n = 2
sigma_meas = 0.03

## Calculamos los vectores de filtrado (sigm)
sigma_model = 0.01
kf1 = KF(zs=sigm, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)
sigma_model = 0.02
kf2 = KF(zs=sigm, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)
sigma_model = 0.05
kf3 = KF(zs=sigm, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)

## Representamos los vectores calculados (sigm)
plt.figure()
plt.plot(t2, kf1, 'b', label='Kalman Filter 2D, s = 0.01')
plt.plot(t2, kf2, 'g', label='Kalman Filter 2D, s = 0.02')
plt.plot(t2, kf3, 'r', label='Kalman Filter 2D, s = 0.05')
plt.plot(t2, sigm, 'm--', label='Measure')
plt.legend() ; plt.axis('off') ; plt.show()

""" SENSIBILIDAD S_MEASURE """

## Establecemos los parametros de los modelos (sin)
n = 2
sigma_model = 0.03

## Calculamos los vectores de filtrado (sin)
sigma_meas = 0.01
kf1 = KF(zs=sin, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)
sigma_meas = 0.02
kf2 = KF(zs=sin, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)
sigma_meas = 0.05
kf3 = KF(zs=sin, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)

## Representamos los vectores calculados (sin)
plt.figure()
plt.plot(t1, kf1, 'b', label='Kalman Filter 2D, s = 0.01')
plt.plot(t1, kf2, 'g', label='Kalman Filter 2D, s = 0.02')
plt.plot(t1, kf3, 'r', label='Kalman Filter 2D, s = 0.05')
plt.plot(t1, sin, 'm--', label='Measure')
plt.legend() ; plt.axis('off') ; plt.show()

## Establecemos los parametros de los modelos (sigm)
n = 2
sigma_model = 0.03

## Calculamos los vectores de filtrado (sigm)
sigma_meas = 0.01
kf1 = KF(zs=sigm, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)
sigma_meas = 0.02
kf2 = KF(zs=sigm, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)
sigma_meas = 0.05
kf3 = KF(zs=sigm, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)

## Representamos los vectores calculados (sigm)
plt.figure()
plt.plot(t2, kf1, 'b', label='Kalman Filter 2D, s = 0.01')
plt.plot(t2, kf2, 'g', label='Kalman Filter 2D, s = 0.02')
plt.plot(t2, kf3, 'r', label='Kalman Filter 2D, s = 0.05')
plt.plot(t2, sigm, 'm--', label='Measure')
plt.legend() ; plt.axis('off') ; plt.show()

""" SENSIBILIDAD MATRIZ Q """

## Establecemos los parametros de los modelos (sin)
n = 2
sigma_meas = 0.01
sigma_model = 0.05

## Calculamos los vectores de filtrado (sin)
kf1 = KF(zs=sin, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)
kf2 = KF(zs=sin, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=False)

## Representamos los vectores calculados (sin)
plt.figure()
plt.plot(t1, kf1, 'b', label='Kalman Filter 2D, Q = Id')
plt.plot(t1, kf2, 'g', label='Kalman Filter 2D, Q = Q_cap2')
plt.plot(t1, sin, 'm--', label='Measure')
plt.legend() ; plt.axis('off') ; plt.show()

## Calculamos los vectores de filtrado (sigm)
kf1 = KF(zs=sigm, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=True)
kf2 = KF(zs=sigm, sigma_meas=sigma_meas, sigma_model=sigma_model, Id=False)

## Representamos los vectores calculados (sigm)
plt.figure()
plt.plot(t2, kf1, 'b', label='Kalman Filter 2D, Q = Id')
plt.plot(t2, kf2, 'g', label='Kalman Filter 2D, Q = Q_cap2')
plt.plot(t2, sigm, 'm--', label='Measure')
plt.legend() ; plt.axis('off') ; plt.show()

""" BOLLINGER BANDS """

## Definimos la divisa y el timeframe
symbol = 'EURGBP'
timeframe = mt5.TIMEFRAME_H1

## Descargamos los historicos
date_from = datetime(2021,5,19,0,0,0)
date_to = datetime(2021,5,30,0,0,0)
df = preprocesado(symbol=symbol, timeframe=timeframe, date_to=date_to, date_from=date_from)

## Establecemos los parametros de los modelos
window = 24
sigma_meas = 1e-3
sigma_model = 1e-3

## Calculamos los vectores de filtrado
df['ma'] = df['close'].rolling(window=window).mean()
df['cma'] = df['close'].rolling(window=window, center=True).mean()
df['kf'] = KF(zs=df['close'], sigma_meas=sigma_meas, sigma_model=sigma_model)
df['std'] = df['close'].rolling(window=window).std()
df['up_ma'] = df['ma'] + 2 * df['std']
df['down_ma'] = df['ma'] - 2 * df['std']
df['up_cma'] = df['cma'] + 2 * df['std']
df['down_cma'] = df['cma'] - 2 * df['std']
df['up_kf'] = df['kf'] + 2 * df['std']
df['down_kf'] = df['kf'] - 2 * df['std']

## Representamos los vectores calculados
plt.plot(df['close'], c='grey', linestyle='--', label='market')
plt.plot(df['ma'], c='green', label='moving average')
plt.plot(df['up_ma'], c='purple')
plt.plot(df['down_ma'], c='purple')
plt.legend() ; plt.axis('off') ; plt.show()
plt.plot(df['close'], c='grey', linestyle='--', label='market')
plt.plot(df['cma'], c='red', label='centered moving average')
plt.plot(df['up_cma'], c='purple')
plt.plot(df['down_cma'], c='purple')
plt.legend() ; plt.axis('off') ; plt.show()
plt.plot(df['close'], c='grey', linestyle='--', label='market')
plt.plot(df['kf'], c='blue', label='kalman filter')
plt.plot(df['up_kf'], c='purple')
plt.plot(df['down_kf'], c='purple')
plt.legend() ; plt.axis('off') ; plt.show()

""" KF vs CMA """

## Definimos la divisa y el timeframe
symbol = 'EURUSD'
timeframe = mt5.TIMEFRAME_H1

## Descargamos los historicos
date_from = datetime(2021,3,30,18,0,0)
date_to = datetime(2021,4,15,18,0,0)
df = preprocesado(symbol=symbol, timeframe=timeframe, date_to=date_to, date_from=date_from)

## Establecemos los parametros de los modelos
window = 24
sigma_meas = 0.002
sigma_model = 0.001

## Calculamos los vectores de filtrado
sigma_model_1 = optimize(df_train=df, window_cma=window, sigma_meas=sigma_meas, order=2, delta=0)
sigma_model_2 = optimize(df_train=df, window_cma=window, sigma_meas=sigma_meas, order=2, delta=10)
df['kf_1'] = KF(zs=df['close'], sigma_meas=sigma_meas, sigma_model=sigma_model_1)
df['kf_2'] = KF(zs=df['close'], sigma_meas=sigma_meas, sigma_model=sigma_model_2)
df['cma'] = df['close'].rolling(window=window, center=True).mean()

## Representamos los vectores calculados
plt.plot(df['close'], c='grey', linestyle='--', label='market')
plt.plot(df['kf_1'], c='blue', label='kalman filter')
plt.plot(df['cma'], c='red', label='centered moving average')
plt.legend() ; plt.axis('off') ; plt.show()
plt.plot(df['close'], c='grey', linestyle='--', label='market')
plt.plot(df['kf_2'], c='blue', label='kalman filter')
plt.plot(df['cma'], c='red', label='centered moving average')
plt.legend() ; plt.axis('off') ; plt.show()