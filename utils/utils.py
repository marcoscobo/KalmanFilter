from pandas import DataFrame, to_datetime
from datetime import datetime
import MetaTrader5 as mt5

## Funcion para establecer conexion con MetaTrader5
def conexion(server='ICMarketsSC-Demo', login=50391826, password='wsAsSPzk'):

	# Establecemos la conexión y en caso de error avisamos de este
	if not mt5.initialize(server=server, login=login, password=password):
		print('Error en el inicio de sesion.')
		mt5.shutdown()
		exit()

## Funcion para descargar historicos en un rango o dado un numero de fechas
def preprocesado(symbol, timeframe, date_from=datetime.now(), date_to=datetime.now(), method='range', start_pos=0, count=0):

	# Descargamos los historicos del servidor
	if method == 'range':
		rates_frame = DataFrame(mt5.copy_rates_range(symbol, timeframe, date_from, date_to))
	elif method == 'pos':
		rates_frame = DataFrame(mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count))
	else:
		raise Exception('Metodo no compatible. Metodos disponibles: range , pos.')

	# Damos formato a las fechas
	rates_frame['time'] = to_datetime(rates_frame['time'], unit='s',utc=True)

	return rates_frame