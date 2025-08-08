import os, time, random, requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- tiny TTL cache to avoid hammering APIs ---
class TTLCache:
    def __init__(self, ttl_seconds=30):
        self.ttl = ttl_seconds
        self._store = {}
    def get(self, key):
        v = self._store.get(key)
        if not v: return None
        val, ts = v
        if time.time() - ts > self.ttl:
            self._store.pop(key, None)
            return None
        return val
    def set(self, key, val):
        self._store[key] = (val, time.time())

_http_timeout = 8
_cache = TTLCache(ttl_seconds=30)

def _get_json(url, params=None, headers=None):
    r = requests.get(url, params=params, headers=headers, timeout=_http_timeout)
    r.raise_for_status()
    # Some throttled pages aren't JSON—defend against that:
    ct = r.headers.get("content-type","").lower()
    if "json" not in ct and not r.text.strip().startswith("{") and not r.text.strip().startswith("["):
        raise RuntimeError(f"Non-JSON response from {url[:80]}...")
    return r.json()

# --------- Providers ----------
class PriceProvider:
    def get_equity_price(self, symbol: str) -> float:
        raise NotImplementedError
    def get_crypto_price(self, symbol: str) -> float:
        raise NotImplementedError

class FMPProvider(PriceProvider):
    BASE = "https://financialmodelingprep.com/api/v3"
    def __init__(self, key: str):
        self.key = key
    def get_equity_price(self, symbol: str) -> float:
        cache_key = ("fmp_quote", symbol)
        if (v := _cache.get(cache_key)) is not None:
            return v
        data = _get_json(f"{self.BASE}/quote/{symbol}", params={"apikey": self.key})
        if not data or "price" not in data[0]:
            raise RuntimeError("FMP empty/invalid quote")
        price = float(data[0]["price"])
        _cache.set(cache_key, price)
        return price

class AlphaVantageProvider(PriceProvider):
    BASE = "https://www.alphavantage.co/query"
    def __init__(self, key: str):
        self.key = key
    def get_equity_price(self, symbol: str) -> float:
        cache_key = ("av_quote", symbol)
        if (v := _cache.get(cache_key)) is not None:
            return v
        data = _get_json(self.BASE, params={
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.key
        })
        q = data.get("Global Quote") or {}
        price_str = q.get("05. price") or q.get("05. Price")
        if not price_str:
            raise RuntimeError(f"Alpha Vantage empty quote for {symbol}")
        price = float(price_str)
        _cache.set(cache_key, price)
        return price

class YahooLastResortProvider(PriceProvider):
    # Only used if the others fail. Long backoff + headers to look human.
    BASE = "https://query2.finance.yahoo.com/v10/finance/quoteSummary"
    def __init__(self):
        pass
    def get_equity_price(self, symbol: str) -> float:
        cache_key = ("yahoo_quote", symbol)
        if (v := _cache.get(cache_key)) is not None:
            return v
        params = {
            "modules": "financialData,quoteType,defaultKeyStatistics,assetProfile,summaryDetail",
            "corsDomain": "finance.yahoo.com",
            "formatted": "false",
            "symbol": symbol,
            "crumb": "Edge: Too Many Requests"
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/*;q=0.9,*/*;q=0.8",
            "Referer": "https://finance.yahoo.com/"
        }
        try:
            data = _get_json(f"{self.BASE}/{symbol}", params=params, headers=headers)
            result = data["quoteSummary"]["result"][0]
            # prefer financialData.currentPrice, fallback to summaryDetail
            price = (result.get("financialData", {}) or {}).get("currentPrice", {}).get("raw")
            if price is None:
                price = (result.get("summaryDetail", {}) or {}).get("previousClose", {}).get("raw")
            if price is None:
                raise RuntimeError("Yahoo missing price")
            price = float(price)
            _cache.set(cache_key, price)
            return price
        except requests.HTTPError as e:
            # If throttled, sleep longer so we don't loop 429s
            if e.response is not None and e.response.status_code == 429:
                # long-ish backoff with jitter
                sleep_s = 120 + random.uniform(0, 60)
                time.sleep(sleep_s)
            raise

class CoinbaseSpotProvider(PriceProvider):
    BASE = "https://api.coinbase.com/v2/prices"
    def get_crypto_price(self, symbol: str) -> float:
        # symbol expected like "BTC-USD"
        cache_key = ("cb_spot", symbol)
        if (v := _cache.get(cache_key)) is not None:
            return v
        data = _get_json(f"{self.BASE}/{symbol}/spot")
        amt = float(data["data"]["amount"])
        _cache.set(cache_key, amt)
        return amt

# --------- Coordinator / Facade ----------
class PriceRouter:
    """Tries FMP -> Alpha Vantage -> Yahoo (equities). Uses Coinbase for BTC."""
    def __init__(self):
        fmp_key = os.getenv("FMP_API_KEY", "")
        av_key  = os.getenv("ALPHAVANTAGE_API_KEY", "")
        self.providers_equity = []
        if fmp_key:
            self.providers_equity.append(FMPProvider(fmp_key))
        if av_key:
            self.providers_equity.append(AlphaVantageProvider(av_key))
        self.providers_equity.append(YahooLastResortProvider())  # last
        self.crypto = CoinbaseSpotProvider()

    def get_equity_price(self, symbol: str) -> float:
        last_err = None
        for p in self.providers_equity:
            try:
                return p.get_equity_price(symbol)
            except Exception as e:
                last_err = e
                continue
        raise RuntimeError(f"All equity providers failed for {symbol}: {last_err}")

    def get_crypto_price(self, base="BTC", quote="USD") -> float:
        pair = f"{base}-{quote}"
        return self.crypto.get_crypto_price(pair)
