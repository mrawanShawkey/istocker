from api.common.errors.app_errors import AppErrors

TickerNotFound = AppErrors(404, 'TICKER_NOT_FOUND', 'The requested ticker does not exist. Please choose one from the existing list of tickers.')