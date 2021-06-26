from scipy.optimize import minimize_scalar
from scipy.linalg import norm
from utils.kalman_filter import KF
from numpy import diff

## Funcion objetivo con regularizacion de Tikhonov
def fun_obj(sigma_model, sigma_meas, window_cma, df_train, delta, order):

    # Obtenemos los vectores kf y cma
    cma = df_train['close'].rolling(window=window_cma, center=True).mean()
    kf = KF(zs=df_train['close'], sigma_meas=sigma_meas, sigma_model=sigma_model)
    # Obtenemos la diferencia entre ambos vectores reemplazando los extremos que son nan por cero
    diff1 = (cma - kf).fillna(0)
    # Obtenemos la diferencia entre posiciones consecutivas del vector kf
    diff2 = diff(kf)

    return norm(diff1, ord=order) + delta * norm(diff2, ord=order)

## Funcion para calcular el sigma_model optimo
def optimize(df_train, window_cma, sigma_meas, delta=0, order=2):

    # Calculamos el sigma_model optimo en el intervalo (1e-5, sigma_meas)
    sigma_model = minimize_scalar(fun_obj, args=(sigma_meas, window_cma, df_train, delta, order), bounds=(1e-5, sigma_meas), method='bounded').x

    return sigma_model