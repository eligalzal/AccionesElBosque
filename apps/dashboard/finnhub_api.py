import requests

FINNHUB_API_KEY = 'd0lf25pr01qhb0284op0d0lf25pr01qhb0284opg'

def obtener_precio_accion(simbolo):
    url = f'https://finnhub.io/api/v1/quote?symbol={simbolo}&token={FINNHUB_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def obtener_market_news(categoria):
    url = f'https://finnhub.io/api/v1/news?category={categoria}&token={FINNHUB_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  
    else:
        return []
