import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

today_str = datetime.now().strftime("%Y-%m-%d")

# 你的專屬 Discord Webhook 網址
discord_webhook_url = "https://discord.com/api/webhooks/1533668810194817024/JtZwgbu0VxzyjBXUGRODN8IA433odo9oFoLF7-K4aEMFSLDNq4TQ-nYV"

print("📡 GitHub 雲端機器人甦醒，正在抓取全球市場數據...\n")

# 1. 抓取宏觀數據
fed_policy = "Rate Cut / Low Interest Rate"
try:
    vix_val = round(yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1], 2)
except:
    vix_val = 15.0

try:
    fx_rate = round(yf.Ticker("USDTWD=X").history(period="1d")["Close"].iloc[-1], 2)
except:
    fx_rate = 32.0

stock_list = ["NVDA", "AAPL", "TSLA", "MSFT", "AMD", "2330.TW"]
reports = []

for symbol in stock_list:
    try:
        df = yf.Ticker(symbol).history(period="6mo").dropna()

        price = round(df["Close"].iloc[-1], 2)
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA60"] = df["Close"].rolling(60).mean()
        ma20 = round(df["MA20"].iloc[-1], 2)
        ma60 = round(df["MA60"].iloc[-1], 2)

        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = round(100 - (100 / (1 + rs)).iloc[-1], 2)

        recent_peak = round(df["High"].tail(60).max(), 2)
        dynamic_stop = round(recent_peak * 0.92, 2)

        # 綜合評分
        score = 0
        if ma20 > ma60: score += 25
        if 40 <= rsi <= 68: score += 25
        elif 30 <= rsi < 40 or 68 < rsi <= 75: score += 15
        else: score += 5
        if price > dynamic_stop: score += 25
        if vix_val < 20: score += 25
        else: score += 10

        if score >= 85: rating = "🌟 85+ Strong Bull"
        elif score >= 65: rating = "🟢 65~84 Solid Hold"
        else: rating = "🟡 Watch / Defensive"

        reports.append({
            "symbol": symbol,
            "price": price,
            "score": score,
            "rsi": rsi,
            "stop_line": dynamic_stop,
            "rating": rating
        })
    except:
        pass

# 2. 組裝全英文 Discord 晨間戰報
msg = f"👑 **[GitHub Actions: Autonomous Daily Quant Brief]**\n"
msg += f"📅 **Date:** {today_str} | **Zero-Touch Cloud Scheduled Run**\n"
msg += "========================================\n"
msg += f"🏛️ **Fed Macro:** `{fed_policy}` | 🚨 **VIX:** `{vix_val}` | 💱 **USD/TWD:** `{fx_rate}`\n"
msg += "========================================\n"
msg += "🏆 **[Global AI Quant Health Scorecard]**\n"

for r in reports:
    msg += f"🔹 **`{r['symbol']}`** | Price: `${r['price']}` | Score: **`{r['score']}/100`**\n"
    msg += f"   • RSI: `{r['rsi']}` | 8% Stop: `${r['stop_line']}` | Rating: {r['rating']}\n"

msg += "========================================\n"
msg += "🤖 *24/7 Headless Cloud Runner Executed Successfully.*"

# 3. 發送至 Discord
response = requests.post(discord_webhook_url, json={"content": msg})
print(f"📡 Discord 回應狀態碼：{response.status_code}")
