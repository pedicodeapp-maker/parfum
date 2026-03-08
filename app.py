from flask import Flask, request, Response, send_from_directory
import requests as req
import os, random

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
]

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/proxy")
def proxy():
    # Flask auto-decodes query params — use request.args directly
    url = request.args.get("url", "")
    if not url:
        return Response("Missing url param", status=400)

    # Security: only allow perfume sites
    if not any(d in url for d in ALLOWED_DOMAINS):
        return Response("URL no permitida", status=400)

    ua = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",
    }

    # Add Referer for non-home pages to look more natural
    domain = next((d for d in ALLOWED_DOMAINS if d in url), "")
    if domain and not url.rstrip("/").endswith(domain):
        headers["Referer"] = f"https://{domain}/"

    try:
        # requests handles URL encoding properly and follows redirects
        r = req.get(url, headers=headers, timeout=15, allow_redirects=True)
        r.raise_for_status()

        return Response(r.content, status=200, headers={
            "Content-Type": "text/html; charset=utf-8",
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=3600",
        })

    except req.exceptions.HTTPError as e:
        code = e.response.status_code if e.response else 502
        return Response(str(e), status=code, headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        return Response(str(e), status=502, headers={"Access-Control-Allow-Origin": "*"})

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
