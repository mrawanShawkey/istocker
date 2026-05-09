from api.common.errors.app_errors import AppErrors

TickerNotFound = AppErrors(404, 'The requested ticker does not exist. Please choose one from the existing list of tickers.')