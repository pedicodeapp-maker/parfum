from flask import Flask, request, Response, send_from_directory
from urllib.request import urlopen, Request
from urllib.parse import unquote
import os, random, time

app = Flask(__name__, static_folder="static")

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

ALLOWED_DOMAINS = [
    "www.fragrantica.com",
    "www.parfumo.net",
    "www.parfumo.com",
    "www.basenotes.net",
    "www.notinothek.de",
]

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/proxy")
def proxy():
    raw_url = request.args.get("url", "")
    url = unquote(raw_url)

    # Security: only allow perfume sites
    allowed = any(domain in url for domain in ALLOWED_DOMAINS)
    if not allowed:
        return Response("URL no permitida", status=400)

    ua = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "identity",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
        "DNT": "1",
    }

    # Add referer if searching (not home)
    if "/search" in url or "/perfume/" in url or "/Perfumes/" in url:
        domain = next((d for d in ALLOWED_DOMAINS if d in url), "")
        if domain:
            headers["Referer"] = f"https://{domain}/"

    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=15) as resp:
            body = resp.read()

        return Response(body, status=200, headers={
            "Content-Type": "text/html; charset=utf-8",
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=3600",
        })

    except Exception as e:
        code = 502
        msg = str(e)
        if "403" in msg: code = 403
        if "404" in msg: code = 404
        return Response(msg, status=code, headers={"Access-Control-Allow-Origin": "*"})

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
