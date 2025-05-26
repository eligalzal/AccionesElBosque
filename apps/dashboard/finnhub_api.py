import requests
import time
import yfinance as yf
from django.conf import settings

FINNHUB_API_KEY =  settings.FINNHUB_API_KEY
 
def obtener_precio_actual(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"

    try:
        ticker = yf.Ticker(symbol)
        precio_actual = ticker.history(period='1d')['Close'].iloc[-1]
        return round(precio_actual, 2)
    except Exception as e:
        print(f"Error al obtener precio actual de {symbol}: {e}")
        return None

def obtener_datos_finnhub(ticker):
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "current_price": data["c"],
            "change": data["d"],
            "percent_change": data["dp"],
            "high": data["h"],
            "low": data["l"],
            "open": data["o"],
            "prev_close": data["pc"]            
        }
    else:
        return None        
    
def obtener_market_news(categoria):
    url = f'https://finnhub.io/api/v1/news?category={categoria}&token={FINNHUB_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  
    else:
        return []
    

def obtener_precios_historicos_yahoo(ticker):
    try:
        datos = yf.download(ticker, period='7d', interval='1d', auto_adjust=False)
        if datos.empty:
            print("No se encontraron datos históricos.")
            return [], []

        fechas = [fecha.strftime('%Y-%m-%d') for fecha in datos.index]

        if 'Close' in datos.columns:
            precios = [float(p) for p in datos['Close'].values]

        else:
            print("La columna 'Close' no está disponible.")
            return [], []

        return fechas, precios

    except Exception as e:
        print(f"Error obteniendo datos históricos: {e}")
        return [], []



def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="7d", interval="1d")

    labels = [t.strftime('%Y-%m-%d') for t in hist.index]
    data = list(hist["Close"])

    info = stock.info
    return {
        "ticker": ticker,
        "name": info.get("shortName", ticker),
        "price": round(info.get("regularMarketPrice", 0), 2),
        "change": f"{round(info.get('regularMarketChangePercent', 0), 2)}%",
        "labels": labels,
        "data": data
    }

