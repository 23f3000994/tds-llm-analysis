import os
import time
import json
import re
import base64
import tempfile
from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import requests
from urllib.parse import urljoin

from pdf_helpers import extract_tables_sum_from_pdf, pdf_to_images_and_ocr

app = Flask(__name__)

EXPECTED_SECRET = os.environ.get("QUIZ_SECRET")
NAV_TIMEOUT = 50000
OVERALL_TIMEOUT = 160


STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
window.chrome = { runtime: {} };
"""


# ---------------- HELPERS ----------------

def fail(code, msg):
    return jsonify({"error": msg}), code


def extract_base64(html):
    """Look for atob(`base64...`)"""
    m = re.search(r"atob\\(\\s*`([^`]+)`\\s*\\)", html)
    if not m:
        return None
    try:
        return base64.b64decode(m.group(1)).decode("utf-8", errors="replace")
    except:
        return None


def find_submit_url(text):
    m = re.search(r"https?://[^\\s\"'<]+/submit[^\\s\"'<]*", text)
    return m.group(0) if m else None


# --------------- SOLVER FUNCTION ----------------

def solve_single(email, secret, quiz_url, page, deadline):

    if time.time() > deadline:
        raise Exception("Timeout exceeded")

    page.goto(quiz_url)
    page.wait_for_load_state("domcontentloaded")

    # Wait for JS result if available
    try:
        page.wait_for_function(
            "document.querySelector('#result') && document.querySelector('#result').innerHTML.length > 5",
            timeout=5000
        )
    except:
        pass

    time.sleep(1.0)

    html = page.content()

    # Try TYPE-A (base64 quiz)
    decoded = extract_base64(html)

    if decoded:
        # ---- BASE64 QUIZ ----
        decoded_json = None
        m = re.search(r"\\{[\\s\\S]*?\\}", decoded)
        if m:
            try:
                decoded_json = json.loads(m.group(0))
            except:
                decoded_json = None

        submit_url = None

        if decoded_json and "submit" in decoded_json:
            submit_url = decoded_json["submit"]

        if not submit_url:
            submit_url = find_submit_url(decoded)

        if not submit_url:
            submit_url = find_submit_url(html)

        if not submit_url:
            raise Exception("Submit URL not found in base64 mode")

        # Answer
        if decoded_json and "answer" in decoded_json:
            answer = decoded_json["answer"]
        else:
            answer = decoded[:1500]

        payload = {
            "email": email,
            "secret": secret,
            "url": quiz_url,
            "answer": answer
        }

        r = requests.post(submit_url, json=payload, timeout=20)
        try:
            resp = r.json()
        except:
            resp = {"text": r.text}
        return resp.get("url")

    # -------- TYPE-B: SIMPLE SCRAPE QUIZ --------
    # No base64 found → scrape mode
    m = re.search(r'href="([^"]+)"', html)
    if not m:
        raise Exception("Unknown page: neither base64 nor scrape link")

    next_url = m.group(1)
    next_url = urljoin(quiz_url, next_url)

    # Fetch the secret code to send back
    code_page = requests.get(next_url, timeout=20).text
    secret_code = code_page.strip()

    payload = {
        "email": email,
        "secret": secret,
        "url": quiz_url,
        "answer": secret_code
    }

    # Submit to the SAME page (scrape mode always submits back here)
    r = requests.post(quiz_url, json=payload, timeout=20)
    try:
        resp = r.json()
    except:
        resp = {"text": r.text}

    return resp.get("url")


# ----------------- WEBHOOK ROUTE -----------------

@app.route("/quiz-webhook", methods=["POST"])
def quiz_webhook():

    try:
        data = request.get_json(force=True)
    except:
        return fail(400, "Invalid JSON")

    email = data.get("email")
    secret = data.get("secret")
    start_url = data.get("url")

    if secret != EXPECTED_SECRET:
        return fail(403, "Invalid secret")

    if not email or not secret or not start_url:
        return fail(400, "Missing fields")

    deadline = time.time() + OVERALL_TIMEOUT
    steps = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = browser.new_page()
            page.set_default_navigation_timeout(NAV_TIMEOUT)
            page.add_init_script(STEALTH_JS)

            current = start_url
            stepnum = 1

            while current:
                nxt = solve_single(email, secret, current, page, deadline)
                steps.append({"step": stepnum, "url": current, "next": nxt})
                current = nxt
                stepnum += 1

            browser.close()

        return jsonify({"status": "chain_complete", "steps": steps}), 200

    except Exception as e:
        return fail(500, f"ERROR: {str(e)}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
