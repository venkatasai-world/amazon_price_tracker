# main.py
from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import smtplib
import os
from dotenv import load_dotenv
import time
import uuid
import json
from pathlib import Path
import logging
import datetime

load_dotenv()

SMTP = os.getenv("SMTP_ADDRESS", "smtp.gmail.com")
SENDER_EMAIL = os.getenv("EMAIL_ADDRESS")
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

if not SENDER_EMAIL or not SENDER_PASSWORD:
    logging.warning("EMAIL_ADDRESS or EMAIL_PASSWORD not set in .env — emails will fail until configured.")


def get_price(url, wait_seconds=3):
    """Return product price as float, or None if not found. Uses Selenium (headless Chrome)."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        time.sleep(wait_seconds)

        selectors = [
            (By.CSS_SELECTOR, ".a-price .a-offscreen"),
            (By.ID, "priceblock_ourprice"),
            (By.ID, "priceblock_dealprice"),
            (By.ID, "price_inside_buybox"),
            (By.CLASS_NAME, "a-price-whole"),
        ]

        price_text = None
        for by, sel in selectors:
            try:
                el = driver.find_element(by, sel)
                txt = el.get_attribute("textContent") or el.text
                txt = txt.strip()
                if txt:
                    price_text = txt
                    break
            except Exception:
                continue

        if not price_text:
            try:
                el = driver.find_element(By.CSS_SELECTOR, "[data-a-size='l'] .a-offscreen")
                price_text = (el.get_attribute("textContent") or el.text).strip()
            except Exception:
                pass

        if not price_text:
            return None

        cleaned = price_text.replace("₹", "").replace("Rs.", "").replace("INR", "")
        cleaned = cleaned.replace(",", "").replace(" ", "").strip()

        try:
            price_value = float(cleaned)
            return price_value
        except Exception:
            import re
            m = re.findall(r"[\d\.]+", cleaned)
            if m:
                try:
                    return float(m[0])
                except:
                    return None
            return None
    finally:
        driver.quit()


def send_email(recipient_email, url, current_price, target_price):
    """Send email using SMTP creds from .env. Returns True on success."""
    subject = "PRICE ALERT — Product price dropped!"
    body = f"""Hello,

Good news — the product you're tracking has dropped below your target price.

Current Price: ₹{current_price}
Target Price:  ₹{target_price}

Product link:
{url}

Regards,
Price Tracker Bot
"""

    message = f"Subject: {subject}\n\n{body}"

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        logging.error("SMTP credentials not configured; cannot send email.")
        return False

    try:
        with smtplib.SMTP(SMTP, 587) as connection:
            connection.starttls()
            connection.login(SENDER_EMAIL, SENDER_PASSWORD)
            connection.sendmail(from_addr=SENDER_EMAIL, to_addrs=recipient_email, msg=message.encode("utf-8"))
        return True
    except Exception as e:
        logging.exception("Failed to send email:")
        return False


def save_tracker(data: dict) -> str:
    """Save tracker dict to a JSON file, return id."""
    tid = str(uuid.uuid4())
    path = DATA_DIR / f"{tid}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return tid


def load_all_trackers():
    for p in DATA_DIR.glob("*.json"):
        try:
            with p.open("r", encoding="utf-8") as f:
                d = json.load(f)
            yield p, d
        except Exception:
            logging.exception("Failed to read tracker file %s", p)


def delete_tracker_file(path: Path):
    try:
        path.unlink()
    except Exception:
        logging.exception("Failed to delete tracker file %s", path)


def check_all_trackers():
    logging.info("Running scheduled check for %s trackers", len(list(DATA_DIR.glob("*.json"))))
    for path, tracker in load_all_trackers():
        url = tracker.get("url")
        target = tracker.get("target_price")
        email = tracker.get("email")
        if not url or target is None or not email:
            logging.warning("Skipping invalid tracker %s", path)
            continue

        try:
            current = get_price(url)
        except Exception:
            logging.exception("Price fetch failed for %s", url)
            continue

        if current is None:
            logging.info("Price not found for %s (tracker %s)", url, path.name)
            continue

        logging.info("Tracker %s: current=%.2f target=%.2f", path.name, current, float(target))

        try:
            if float(current) <= float(target):
                ok = send_email(email, url, current, target)
                if ok:
                    logging.info("Email sent for tracker %s, deleting file.", path.name)
                    delete_tracker_file(path)
                else:
                    logging.warning("Failed to send email for tracker %s; will retry later.", path.name)
        except Exception:
            logging.exception("Error handling tracker %s", path.name)


app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/track", methods=["POST"])
def track():
    data = request.get_json() or request.form.to_dict()
    url = data.get("url")
    target = data.get("target_price") or data.get("target")
    email = data.get("email")

    if not url or not target or not email:
        return jsonify({"ok": False, "error": "Missing url, target_price or email"}), 400

    try:
        target_price = float(target)
    except ValueError:
        return jsonify({"ok": False, "error": "target_price must be numeric"}), 400

    tracker = {"url": url, "target_price": target_price, "email": email, "created_at": time.time()}
    tid = save_tracker(tracker)
    try:
        current = get_price(url)
    except Exception:
        current = None

    emailed = False
    if current is not None:
        try:
            if float(current) <= float(target_price):
                ok = send_email(email, url, current, target_price)
                if ok:
                    delete_tracker_file(Path(DATA_DIR / f"{tid}.json"))
                    emailed = True
        except Exception:
            logging.exception("Immediate check failed for tracker %s", tid)

    return jsonify({"ok": True, "id": tid, "emailed": emailed, "current_price": current})


@app.route("/status", methods=["GET"])
def status():
    items = []
    for p, d in load_all_trackers():
        items.append({"id": p.stem, "url": d.get("url"), "target_price": d.get("target_price"), "email": d.get("email")})
    return jsonify({"ok": True, "trackers": items})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scheduler = BackgroundScheduler()
    try:
        interval_min = int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))
    except Exception:
        interval_min = 15

    # APScheduler expects a datetime for `next_run_time`, not a float timestamp.
    scheduler.add_job(check_all_trackers, "interval", minutes=interval_min, next_run_time=datetime.datetime.now())
    scheduler.start()

    try:
        app.run(host="0.0.0.0", port=5000)
    finally:
        scheduler.shutdown()
