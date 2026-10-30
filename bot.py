
import os
import time
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

TOKEN = os.environ["BOT_TOKEN"]
CHANNEL = "@YouGold750"

URLS = {
    "طلای ۱۸ عیار": "https://www.tgju.org/profile/geram18",
    "مثقال طلا": "https://www.tgju.org/profile/mesghal"
}

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

last_prices = {}

def get_price(url):
    response = session.get(url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) < 2:
            continue

        if "نرخ فعلی" in cells[0].get_text(" ", strip=True):
            value = cells[1].get_text(" ", strip=True)
            value = re.sub(r"[^0-9۰-۹٠-٩]", "", value)
            value = value.translate(str.maketrans(
                "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
                "01234567890123456789"
            ))
            if value:
                return int(value)

    raise ValueError("Price not found")

def send_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    response = requests.post(
        url,
        data={
            "chat_id": CHANNEL,
            "text": message
        },
        timeout=20
    )
    response.raise_for_status()

def main():
    global last_prices

    while True:
        for name, url in URLS.items():
            try:
                price = get_price(url)

                if name not in last_prices:
                    last_prices[name] = price
                    continue

                old_price = last_prices[name]

                if price != old_price:
                    difference = price - old_price
                    direction = "🔺 افزایش" if difference > 0 else "🔻 کاهش"

                    message = (
                        f"🟡 تغییر قیمت {name}\n\n"
                        f"قیمت قبلی: {old_price:,} ریال\n"
                        f"قیمت جدید: {price:,} ریال\n"
                        f"{direction}: {abs(difference):,} ریال\n"
                        f"زمان: {datetime.now().strftime('%H:%M:%S')}\n\n"
                        f"منبع: TGJU"
                    )

                    send_message(message)
                    last_prices[name] = price

            except Exception as error:
                print(f"Error ({name}): {error}")

        time.sleep(30)

if __name__ == "__main__":
    main()

