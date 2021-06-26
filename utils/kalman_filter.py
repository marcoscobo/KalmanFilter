from numpy import dot, eye, zeros, arange, array, outer
from scipy.linalg import inv
from math import factorial

## Clase del filtro de Kalman
class KalmanFilter():

	# Etapa de prediccion
	def predict(self):
		self.x = dot(self.F, self.x)
		self.P = dot(self.F,self.P).dot(self.F.T) + self.Q

	# Etapa de actualizacion
	def update(self, Z, n):
		y = Z - dot(self.H, self.x)
		S = dot(self.H, self.P).dot(self.H.T) + self.R
		K = dot(self.P, self.H.T).dot(inv(S))
		self.x = self.x + dot(K, y)
		I_KH = eye(n) - dot (K, self.H)
		self.P = dot(I_KH,self.P)

## Funcion para crear el filtro de Kalman
def KF(zs, sigma_meas, sigma_model, dt=0.1, n=2, Id=False):

	# Creamos la matriz F
	F = eye(n)
	for i in range(1,n):
		r = arange(n-i)
		F[r, r+i] = dt ** i / factorial(i)

	# Creamos la matriz H
	H = zeros((1,n)) ; H[0,0] = 1

	# Creamos la matriz Q
	if Id:
		Q = eye(n) * sigma_model ** 2
	else:
		w_k = []
		for n_i in range(n):
			w_k.append(dt ** (n - n_i) / factorial(n - n_i))
		Q = outer(array(w_k), array(w_k).T) * sigma_model ** 2

	# Creamos la matriz R
	R = sigma_meas ** 2

	# Creamos el punto inicial
	x_ini = zeros((n, 1)) ; x_ini[0, 0] = zs[0]

	# Creamos la matriz P
	P = eye(n) * 0.001

	# Creamos el filtro de Kalman con las matrices dadas
	Kalman_filter = KalmanFilter()
	Kalman_filter.x = x_ini
	Kalman_filter.P = P
	Kalman_filter.Q = Q
	Kalman_filter.R = R
	Kalman_filter.F = F
	Kalman_filter.H = H

	# Recorremos el vector de mediciones y calculamos el estado del sistema
	us = []
	for t in range(len(zs)):
		# Etapa de prediccion
		Kalman_filter.predict()
		# Etapa de actualizacion
		Kalman_filter.update(zs[t],n)

		# Agregamos el valor filtrado al vector output
		us.append(Kalman_filter.x[0,0])
		
	return us