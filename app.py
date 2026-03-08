import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Parfum — Monitor de Fragancias",
    page_icon="🫙",
    layout="centered",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Cinzel:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Cormorant Garamond', serif; }
.stApp { background: #080603; color: #EDE3D0; }
section[data-testid="stSidebar"] { display: none; }
.parfum-header { text-align: center; padding: 40px 0 28px; }
.parfum-eyebrow { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: .5em; color: rgba(201,160,102,.45); margin-bottom: 12px; }
.parfum-title {
    font-size: clamp(46px, 10vw, 72px); font-weight: 300; font-style: italic;
    background: linear-gradient(135deg, #EDE3D0 0%, #C9A066 45%, #EDE3D0 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    letter-spacing: .06em; line-height: 1; margin-bottom: 12px;
}
.parfum-rule { width: 60px; height: 1px; background: linear-gradient(90deg,transparent,#C9A066,transparent); margin: 0 auto 12px; }
.parfum-sub { font-family: 'Cinzel', serif; font-size: 9px; letter-spacing: .35em; color: rgba(237,227,208,.25); }
div[data-testid="stTextInput"] input {
    background: rgba(0,0,0,.5) !important; border: 1px solid rgba(201,160,102,.22) !important;
    border-radius: 4px !important; color: #EDE3D0 !important;
    font-family: 'Cormorant Garamond', serif !important; font-size: 17px !important; padding: 14px 16px !important;
}
div[data-testid="stTextInput"] input:focus { border-color: rgba(201,160,102,.5) !important; box-shadow: none !important; }
div[data-testid="stTextInput"] label { color: rgba(237,227,208,.4) !important; font-family: 'Cinzel', serif !important; font-size: 10px !important; letter-spacing: .2em !important; }
div[data-testid="stFileUploader"] { background: rgba(201,160,102,.05); border: 1px dashed rgba(201,160,102,.25); border-radius: 4px; padding: 6px; }
div[data-testid="stFileUploader"] label { color: rgba(201,160,102,.6) !important; font-family: 'Cinzel', serif !important; font-size: 10px !important; letter-spacing: .2em !important; }
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #C9A066, #8B6530) !important; color: #0A0603 !important;
    border: none !important; border-radius: 4px !important; font-family: 'Cinzel', serif !important;
    font-size: 10px !important; letter-spacing: .18em !important; font-weight: 600 !important;
    padding: 12px 28px !important; width: 100%;
}
div[data-testid="stTabs"] button { font-family: 'Cinzel', serif !important; font-size: 9px !important; letter-spacing: .2em !important; color: rgba(237,227,208,.35) !important; background: transparent !important; border: none !important; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #C9A066 !important; border-bottom: 2px solid #C9A066 !important; }
div[data-testid="stTabs"] [data-baseweb="tab-list"] { border-bottom: 1px solid rgba(201,160,102,.15) !important; background: transparent !important; }
div[data-testid="stTabs"] [data-baseweb="tab-panel"] { padding-top: 20px !important; }
div[data-testid="stMetric"] { background: rgba(255,255,255,.025); border: 1px solid rgba(201,160,102,.12); border-radius: 4px; padding: 16px 12px; text-align: center; }
div[data-testid="stMetric"] label { font-family: 'Cinzel', serif !important; font-size: 8px !important; letter-spacing: .22em !important; color: rgba(201,160,102,.42) !important; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] { font-family: 'Cormorant Garamond', serif !important; font-size: 20px !important; color: #C9A066 !important; }
p, li { color: rgba(237,227,208,.65); font-size: 14px; line-height: 1.7; }
a { color: #C9A066 !important; }
hr { border-color: rgba(201,160,102,.15) !important; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="parfum-header">
  <div class="parfum-eyebrow">COLECCIÓN PERSONAL</div>
  <div class="parfum-title">Parfum</div>
  <div class="parfum-rule"></div>
  <div class="parfum-sub">MONITOR DE FRAGANCIAS · PARFUMO</div>
</div>
""", unsafe_allow_html=True)

# ── HTTP ───────────────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

def get(url: str, **kwargs) -> requests.Response:
    r = requests.get(url, headers=HEADERS, timeout=15, **kwargs)
    r.raise_for_status()
    return r

# ── PARFUMO SCRAPER ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def search_perfume(query: str) -> dict:
    """
    Fuente principal: parfumo.net
    Fallback:         basenotes.net  (solo notas)
    """
    try:
        return _parfumo(query)
    except Exception as e1:
        try:
            return _basenotes(query)
        except Exception as e2:
            raise RuntimeError(
                f"Parfumo: {e1} | Basenotes: {e2}"
            )


# ── PARFUMO ────────────────────────────────────────────────────────────────────
def _parfumo(query: str) -> dict:
    # 1. Search
    r = get("https://www.parfumo.net/search", params={"q": query})
    soup = BeautifulSoup(r.text, "html.parser")

    # Find first perfume result link  /Perfumes/Brand/Name
    perf_url = ""
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if re.match(r"^/Perfumes/[^/]+/[^/]+$", href):
            perf_url = "https://www.parfumo.net" + href
            break
    # Also try absolute URLs in page
    if not perf_url:
        m = re.search(r'https?://www\.parfumo\.net/Perfumes/[^"\'<>\s]+', r.text)
        if m:
            perf_url = m.group(0)

    if not perf_url:
        raise ValueError(f'Sin resultados en Parfumo para "{query}"')

    # 2. Fetch perfume page
    r2 = get(perf_url)
    soup2 = BeautifulSoup(r2.text, "html.parser")
    html = r2.text

    # Name
    name = (soup2.find("h1") or soup2.new_tag("x")).get_text(strip=True)
    name = re.sub(r'\s+', ' ', name).strip()

    # Brand — usually before "/" in h1 or in breadcrumb
    brand = ""
    bc = soup2.find("ol", class_=re.compile(r"breadcrumb"))
    if bc:
        items = bc.find_all("li")
        if len(items) >= 2:
            brand = items[-2].get_text(strip=True)
    if not brand:
        m = re.search(r'/Perfumes/([^/]+)/', perf_url)
        if m:
            brand = m.group(1).replace("-", " ").replace("_", " ")

    # Year
    year = (re.search(r'\b(19[5-9]\d|20[0-2]\d)\b', html) or [None])[0]
    if year:
        year = re.search(r'\b(19[5-9]\d|20[0-2]\d)\b', html).group(1)
    else:
        year = ""

    # Image
    img_url = ""
    og = soup2.find("meta", property="og:image")
    if og:
        img_url = og.get("content", "")
    if not img_url:
        for img in soup2.find_all("img"):
            src = img.get("src", "")
            if "perfume" in src.lower() or "bottle" in src.lower() or "/perfumes/" in src.lower():
                img_url = src
                break
    if img_url.startswith("/"):
        img_url = "https://www.parfumo.net" + img_url

    # Description
    desc = ""
    for sel in ["div.description", "div.fragrance-description", "p.description", "meta[name=description]"]:
        tag = soup2.select_one(sel)
        if tag:
            desc = tag.get("content", "") or tag.get_text(strip=True)
            if desc:
                desc = desc[:300]
                break

    # Notes — Parfumo uses sections with class "notes" or similar
    top_notes, heart_notes, base_notes = _parfumo_notes(soup2, html)

    # Ratings — Parfumo shows community votes as numbers or bars
    longevity = _parfumo_rating(html, r'longevity|Haltbarkeit|duración') or 3
    sillage   = _parfumo_rating(html, r'sillage|Sillage|estela')          or 3
    intensity = _parfumo_rating(html, r'intensity|Intensität|intensidad') or 3

    # Gender
    gender = "Unisex"
    if re.search(r"pour femme|for women|femenin|damen|women", html, re.I):
        gender = "Femenino"
    elif re.search(r"pour homme|for men|masculin|herren|\bmen\b", html, re.I):
        gender = "Masculino"
    if re.search(r"unisex|for women and men|mixte", html, re.I):
        gender = "Unisex"

    # Season
    season = []
    for label, pat in [("🌸 Primavera","spring|Frühling"), ("☀️ Verano","summer|Sommer"),
                       ("🍂 Otoño","fall|autumn|Herbst"), ("❄️ Invierno","winter|Winter")]:
        if re.search(pat, html, re.I):
            season.append(label)
    if not season:
        season = ["🌍 Todo el año"]

    # Time of day
    time_day = []
    for label, pat in [("🌤 Diurno","day|Tag|diurno"), ("🌙 Nocturno","night|Nacht|nocturno|evening")]:
        if re.search(pat, html, re.I):
            time_day.append(label)
    if not time_day:
        time_day = ["🌤 Diurno", "🌙 Nocturno"]

    return dict(name=name, brand=brand, year=year, img_url=img_url, desc=desc,
                gender=gender, season=season, time_day=time_day,
                longevity=longevity, sillage=sillage, intensity=intensity,
                top_notes=top_notes, heart_notes=heart_notes, base_notes=base_notes,
                url=perf_url, source="Parfumo")


def _parfumo_notes(soup, html):
    """Extract notes from Parfumo page."""
    result = {"top": [], "heart": [], "base": []}
    keywords = {
        "top":    re.compile(r"top|head|kopf|salida", re.I),
        "heart":  re.compile(r"heart|middle|herz|corazón|coeur", re.I),
        "base":   re.compile(r"base|fond|basis|fondo", re.I),
    }

    # Strategy 1: structured note sections
    for section in soup.find_all(["div", "section", "ul"], class_=True):
        cls = " ".join(section.get("class", []))
        for key, pat in keywords.items():
            if pat.search(cls) and not result[key]:
                items = []
                for el in section.find_all(["li", "span", "a"]):
                    t = el.get_text(strip=True)
                    if 1 < len(t) < 40 and re.match(r"^[A-Za-zÀ-ÿ\s\-&']+$", t):
                        items.append(t)
                if items:
                    result[key] = items[:8]

    # Strategy 2: heading + following list
    if not any(result.values()):
        for heading in soup.find_all(["h2","h3","h4","strong","b"]):
            txt = heading.get_text(strip=True)
            for key, pat in keywords.items():
                if pat.search(txt) and len(txt) < 40 and not result[key]:
                    nxt = heading.find_next(["ul","div","p"])
                    if nxt:
                        items = []
                        for el in nxt.find_all(["li","span","a"]):
                            t = el.get_text(strip=True)
                            if 1 < len(t) < 40 and re.match(r"^[A-Za-zÀ-ÿ\s\-&']+$", t):
                                items.append(t)
                        if items:
                            result[key] = items[:8]

    # Strategy 3: img alts near note headings
    if not any(result.values()):
        for key, pat in keywords.items():
            chunk_m = re.search(
                {
                    "top":   r"(?:top|head|kopf)[^<]{0,60}(?:note|Note)[\s\S]{0,1000}?(?=heart|middle|base|$)",
                    "heart": r"(?:heart|middle|herz)[^<]{0,60}(?:note|Note)[\s\S]{0,1000}?(?=base|$)",
                    "base":  r"(?:base|fond|basis)[^<]{0,60}(?:note|Note)[\s\S]{0,1000}",
                }[key], html, re.I
            )
            if chunk_m:
                alts = re.findall(r'alt="([^"]{2,40})"', chunk_m.group())
                items = [a.strip() for a in alts if not re.search(r"logo|icon|parfumo", a, re.I)]
                if items:
                    result[key] = items[:8]

    def to_tuples(names):
        unique = list(dict.fromkeys(n[0].upper()+n[1:].lower() for n in names if n))[:8]
        return [(n, round(90 - i*(55/max(len(unique)-1,1)))) for i, n in enumerate(unique)]

    return to_tuples(result["top"]), to_tuples(result["heart"]), to_tuples(result["base"])


def _parfumo_rating(html, pattern):
    """Extract 1-5 rating near a keyword."""
    m = re.search(rf'(?:{pattern})[^<]{{0,80}}?(\d+(?:[.,]\d+)?)\s*(?:/\s*(?:5|10))?', html, re.I)
    if m:
        v = float(m.group(1).replace(",", "."))
        if 1 <= v <= 5:  return round(v)
        if 5 < v <= 10:  return round(v / 2)
    return 0


# ── BASENOTES FALLBACK ─────────────────────────────────────────────────────────
def _basenotes(query: str) -> dict:
    r = get("https://www.basenotes.net/search/", params={"query": query})
    soup = BeautifulSoup(r.text, "html.parser")

    perf_url = ""
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/fragrances/" in href or "/perfume/" in href:
            perf_url = href if href.startswith("http") else "https://www.basenotes.net" + href
            break
    if not perf_url:
        raise ValueError(f'Sin resultados en Basenotes para "{query}"')

    r2 = get(perf_url)
    soup2 = BeautifulSoup(r2.text, "html.parser")
    html = r2.text

    name  = (soup2.find("h1") or soup2.new_tag("x")).get_text(strip=True)
    brand = ""
    m = re.search(r'by\s+([A-Za-z\s&]+)', name)
    if m:
        brand = m.group(1).strip()
        name  = name[:name.lower().index(" by ")].strip() if " by " in name.lower() else name

    img_url = (soup2.find("meta", property="og:image") or {}).get("content", "")

    # Notes: basenotes labels them Top, Middle, Base
    top_notes, heart_notes, base_notes = _basenotes_notes(soup2)

    return dict(name=name, brand=brand, year="", img_url=img_url, desc="",
                gender="Unisex", season=["🌍 Todo el año"], time_day=["🌤 Diurno","🌙 Nocturno"],
                longevity=3, sillage=3, intensity=3,
                top_notes=top_notes, heart_notes=heart_notes, base_notes=base_notes,
                url=perf_url, source="Basenotes")


def _basenotes_notes(soup):
    result = {"top": [], "heart": [], "base": []}
    keywords = {"top": re.compile(r"top", re.I), "heart": re.compile(r"middle|heart", re.I), "base": re.compile(r"base", re.I)}
    for row in soup.find_all(["tr","div","li"]):
        txt = row.get_text(" ", strip=True)
        for key, pat in keywords.items():
            if pat.search(txt[:20]):
                notes = [n.strip() for n in re.split(r"[,;|·]", txt) if len(n.strip()) > 1]
                if len(notes) > 1:
                    result[key] = notes[1:9]
    def to_tuples(names):
        unique = list(dict.fromkeys(names))[:8]
        return [(n, round(90 - i*(55/max(len(unique)-1,1)))) for i, n in enumerate(unique)]
    return to_tuples(result["top"]), to_tuples(result["heart"]), to_tuples(result["base"])


# ── HELPERS ────────────────────────────────────────────────────────────────────
def dots(val, max_val=5):
    return "🟡" * int(val) + "⬛" * (max_val - int(val))

def price_links(name, brand):
    q = requests.utils.quote(f"{brand} {name}".strip())
    return [
        ("🌸 Douglas",          f"https://www.douglas.es/es/search?q={q}"),
        ("🏬 El Corte Inglés",  f"https://www.elcorteingles.es/search/?s={q}"),
        ("🖤 Sephora",          f"https://www.sephora.es/search?q={q}"),
        ("💼 Druni",            f"https://www.druni.es/catalogsearch/result/?q={q}"),
        ("📦 Amazon.es",        f"https://www.amazon.es/s?k={q}&i=beauty"),
        ("🧴 Arenal",           f"https://www.perfumeriasarenal.com/busqueda?q={q}"),
        ("✨ Primor",           f"https://www.primor.eu/es/search?q="{q}"),
    ]

# ── UI ─────────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input("q", placeholder="Nombre del perfume… (ej: Sauvage Dior)",
                          label_visibility="collapsed")
with col2:
    search_btn = st.button("BUSCAR", use_container_width=True)

st.markdown("<div style='text-align:center;color:rgba(201,160,102,.3);font-family:Cinzel,serif;font-size:9px;letter-spacing:.35em;padding:6px 0'>— O —</div>",
            unsafe_allow_html=True)

uploaded = st.file_uploader("📷  FOTOGRAFIAR BOTELLA", type=["jpg","jpeg","png","webp"],
                             label_visibility="visible")
if uploaded:
    st.image(uploaded, width=120)
    st.caption("🔍 Escribe el nombre del perfume manualmente en el campo de arriba")

st.markdown("<hr style='margin:20px 0'>", unsafe_allow_html=True)

# ── RESULTS ────────────────────────────────────────────────────────────────────
if search_btn and query:
    with st.spinner("Buscando en Parfumo…"):
        try:
            p = search_perfume(query)
        except Exception as e:
            st.error(f"❌ No encontrado en ninguna fuente.\n\nPrueba: marca + nombre (ej: *Dior Sauvage*, *YSL Black Opium*)\n\n`{e}`")
            st.stop()

    source_badge = f"<span style='font-family:Cinzel,serif;font-size:8px;letter-spacing:.2em;padding:3px 9px;background:rgba(201,160,102,.12);border:1px solid rgba(201,160,102,.3);border-radius:2px;color:rgba(201,160,102,.7)'>✦ {p.get('source','Parfumo').upper()}</span>"

    # Hero
    hero1, hero2 = st.columns([1, 2.8])
    with hero1:
        if p["img_url"]:
            st.image(p["img_url"], use_container_width=True)
        else:
            st.markdown("<div style='font-size:60px;text-align:center;opacity:.15;padding:20px 0'>🫙</div>",
                        unsafe_allow_html=True)
    with hero2:
        st.markdown(f"""
        <div style='margin-bottom:6px'>{source_badge}</div>
        <div style='font-family:Cinzel,serif;font-size:9px;letter-spacing:.35em;color:rgba(201,160,102,.55);margin-bottom:4px;margin-top:8px'>
            {p['brand'].upper()}{" · " + p['year'] if p['year'] else ""}
        </div>
        <div style='font-family:Cormorant Garamond,serif;font-size:clamp(22px,4vw,34px);font-weight:300;font-style:italic;color:#EDE3D0;line-height:1.1;margin-bottom:10px'>
            {p['name']}
        </div>
        """, unsafe_allow_html=True)

        tags_html = "".join(
            f"<span style='font-family:Cinzel,serif;font-size:7.5px;letter-spacing:.18em;padding:4px 10px;"
            f"border:1px solid rgba(201,160,102,.28);border-radius:2px;color:#C9A066;"
            f"margin-right:5px;margin-bottom:5px;display:inline-block'>{t}</span>"
            for t in [p["gender"]] + p["season"] + p["time_day"]
        )
        st.markdown(f"<div style='margin-bottom:12px'>{tags_html}</div>", unsafe_allow_html=True)
        if p["desc"]:
            st.markdown(f"<p style='font-size:13px;line-height:1.75;color:rgba(237,227,208,.6)'>{p['desc']}</p>",
                        unsafe_allow_html=True)
        st.markdown(f"[↗ Ver en {p.get('source','Parfumo')}]({p['url']})")

    st.markdown("<hr style='margin:18px 0'>", unsafe_allow_html=True)

    # Metrics
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("⧗  LONGEVIDAD", dots(p["longevity"]))
    with m2: st.metric("◈  ESTELA",      dots(p["sillage"]))
    with m3: st.metric("◉  INTENSIDAD",  dots(p["intensity"]))

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Tabs
    tab1, tab2 = st.tabs(["PIRÁMIDE OLFATIVA", "COMPARATIVA DE PRECIOS"])

    with tab1:
        nc1, nc2, nc3 = st.columns(3)
        for col, notes, icon, label in [
            (nc1, p["top_notes"],   "▲", "NOTAS DE SALIDA"),
            (nc2, p["heart_notes"], "◆", "NOTAS DE CORAZÓN"),
            (nc3, p["base_notes"],  "▼", "NOTAS DE FONDO"),
        ]:
            with col:
                st.markdown(f"""
                <div style='text-align:center;margin-bottom:14px'>
                  <div style='font-size:18px;color:#C9A066'>{icon}</div>
                  <div style='font-family:Cinzel,serif;font-size:7px;letter-spacing:.2em;color:rgba(201,160,102,.38)'>{label}</div>
                </div>
                """, unsafe_allow_html=True)
                if notes:
                    for note_name, pct in notes:
                        st.markdown(f"""
                        <div style='margin-bottom:9px'>
                          <div style='display:flex;justify-content:space-between;margin-bottom:4px'>
                            <span style='font-size:12.5px;color:#C9A066'>{note_name}</span>
                            <span style='font-size:10px;color:rgba(237,227,208,.3)'>{pct}%</span>
                          </div>
                          <div style='height:3px;background:rgba(201,160,102,.1);border-radius:2px'>
                            <div style='height:100%;width:{pct}%;background:linear-gradient(90deg,#C9A066,#F0D080);border-radius:2px'></div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No disponible")

    with tab2:
        for retailer, url in price_links(p["name"], p["brand"]):
            st.markdown(f"""
            <a href="{url}" target="_blank" style="text-decoration:none">
              <div style='background:rgba(255,255,255,.025);border:1px solid rgba(201,160,102,.12);
                   border-radius:4px;padding:14px 18px;margin-bottom:7px;
                   display:flex;justify-content:space-between;align-items:center'>
                <div>
                  <div style='font-size:15px;color:#EDE3D0'>{retailer}</div>
                  <div style='font-size:11px;color:rgba(237,227,208,.35)'>Buscar "{p['name']}"</div>
                </div>
                <span style='color:rgba(201,160,102,.5);font-size:16px'>↗</span>
              </div>
            </a>
            """, unsafe_allow_html=True)
        st.caption("Los enlaces abren la búsqueda en cada tienda para ver el precio actual")

elif search_btn and not query:
    st.warning("✦ Escribe el nombre de una fragancia primero.")
