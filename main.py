import pandas as pd
import akshare as ak
import matplotlib.pyplot as plt
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def fetch_price(code):
    if code.startswith("6"):
        symbol = "sh" + code
    else:
        symbol = "sz" + code

    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="")
    df = df.rename(columns={"日期": "date", "收盘": "close"})
    df["date"] = pd.to_datetime(df["date"])
    df["ret"] = df["close"].pct_change()
    return df.tail(30)

def analyze(pool):
    result = []
    for code in pool["code"]:
        df = fetch_price(code)
        if df.empty:
            continue
        last_ret = df["ret"].iloc[-1]
        vol = df["ret"].std()
        result.append({
            "code": code,
            "latest_return": round(last_ret,4),
            "volatility_30d": round(vol,4)
        })
    return pd.DataFrame(result)

def send_email(html_content):
    sender = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASS"]
    receiver = os.environ["EMAIL_TO"]

    msg = MIMEMultipart()
    msg["Subject"] = "Daily Stock Agent Report"
    msg["From"] = sender
    msg["To"] = receiver

    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.126.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())

if __name__ == "__main__":
    pool = pd.read_csv("pool.csv")
    report = analyze(pool)

    html = "<h2>Daily Stock Report</h2>"
    html += f"<p>Date: {datetime.now()}</p>"
    html += report.to_html(index=False)

    send_email(html)

