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

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Cinzel:wght@400;500;600&display=swap');

/* Base */
html, body, [class*="css"] { font-family: 'Cormorant Garamond', serif; }
.stApp { background: #080603; color: #EDE3D0; }
section[data-testid="stSidebar"] { display: none; }

/* Header */
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

/* Search box */
div[data-testid="stTextInput"] input {
    background: rgba(0,0,0,.5) !important;
    border: 1px solid rgba(201,160,102,.22) !important;
    border-radius: 4px !important;
    color: #EDE3D0 !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 17px !important;
    padding: 14px 16px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(201,160,102,.5) !important;
    box-shadow: none !important;
}
div[data-testid="stTextInput"] label { color: rgba(237,227,208,.4) !important; font-family: 'Cinzel', serif !important; font-size: 10px !important; letter-spacing: .2em !important; }

/* File uploader */
div[data-testid="stFileUploader"] {
    background: rgba(201,160,102,.05);
    border: 1px dashed rgba(201,160,102,.25);
    border-radius: 4px;
    padding: 6px;
}
div[data-testid="stFileUploader"] label { color: rgba(201,160,102,.6) !important; font-family: 'Cinzel', serif !important; font-size: 10px !important; letter-spacing: .2em !important; }

/* Buttons */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #C9A066, #8B6530) !important;
    color: #0A0603 !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Cinzel', serif !important;
    font-size: 10px !important;
    letter-spacing: .18em !important;
    font-weight: 600 !important;
    padding: 12px 28px !important;
    width: 100%;
}
div[data-testid="stButton"] button:hover { opacity: .88 !important; }

/* Tabs */
div[data-testid="stTabs"] button {
    font-family: 'Cinzel', serif !important;
    font-size: 9px !important;
    letter-spacing: .2em !important;
    color: rgba(237,227,208,.35) !important;
    background: transparent !important;
    border: none !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #C9A066 !important;
    border-bottom: 2px solid #C9A066 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    border-bottom: 1px solid rgba(201,160,102,.15) !important;
    background: transparent !important;
    gap: 0 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-panel"] { padding-top: 20px !important; }

/* Metric cards */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,.025);
    border: 1px solid rgba(201,160,102,.12);
    border-radius: 4px;
    padding: 16px 12px;
    text-align: center;
}
div[data-testid="stMetric"] label { font-family: 'Cinzel', serif !important; font-size: 8px !important; letter-spacing: .22em !important; color: rgba(201,160,102,.42) !important; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] { font-family: 'Cormorant Garamond', serif !important; font-size: 22px !important; color: #C9A066 !important; }

/* General text */
p, li { color: rgba(237,227,208,.65); font-size: 14px; line-height: 1.7; }
h1, h2, h3 { color: #EDE3D0 !important; font-family: 'Cormorant Garamond', serif !important; font-weight: 300 !important; }
a { color: #C9A066 !important; }

/* Divider */
hr { border-color: rgba(201,160,102,.15) !important; }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="parfum-header">
  <div class="parfum-eyebrow">COLECCIÓN PERSONAL</div>
  <div class="parfum-title">Parfum</div>
  <div class="parfum-rule"></div>
  <div class="parfum-sub">MONITOR DE FRAGANCIAS · FRAGRANTICA</div>
</div>
""", unsafe_allow_html=True)

# ── SCRAPER FUNCTIONS ──────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

@st.cache_data(ttl=3600, show_spinner=False)
def search_fragrantica(query: str) -> dict:
    """Busca un perfume en Fragrantica y devuelve sus datos."""
    # 1. Search
    search_url = f"https://www.fragrantica.com/search/?query={requests.utils.quote(query)}"
    r = requests.get(search_url, headers=HEADERS, timeout=15)
    r.raise_for_status()

    # Find perfume page URL
    perf_url = ""
    matches = re.findall(r'https?://www\.fragrantica\.com/perfume/[^"\'<>\s]+\d+\.html', r.text)
    for m in dict.fromkeys(matches):  # deduplicate preserving order
        if "?" not in m:
            perf_url = m
            break
    if not perf_url:
        m2 = re.search(r'href="(/perfume/[^"]+\d+\.html)"', r.text)
        if m2:
            perf_url = "https://www.fragrantica.com" + m2.group(1)
    if not perf_url:
        raise ValueError(f'No se encontró "{query}" en Fragrantica')

    # 2. Fetch perfume page
    r2 = requests.get(perf_url, headers=HEADERS, timeout=15)
    r2.raise_for_status()
    return parse_page(r2.text, perf_url)


def parse_page(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # Name & brand
    name  = (soup.find("h1", itemprop="name") or soup.find("h1") or soup.new_tag("x")).get_text(strip=True)
    brand_tag = soup.find(itemprop="brand")
    brand = brand_tag.find("span").get_text(strip=True) if brand_tag and brand_tag.find("span") else ""

    # Year
    year_m = re.search(r'\b(19[5-9]\d|20[0-2]\d)\b', html)
    year = year_m.group(1) if year_m else ""

    # Image
    og_img = soup.find("meta", property="og:image")
    img_url = og_img["content"] if og_img else ""
    if not img_url:
        img_tag = soup.find("img", itemprop="image")
        img_url = img_tag.get("src", "") if img_tag else ""
    if img_url.startswith("/"):
        img_url = "https://www.fragrantica.com" + img_url

    # Description
    desc_tag = soup.find(itemprop="description") or soup.find("meta", {"name": "description"})
    desc = desc_tag.get_text(strip=True) if desc_tag else ""
    if not desc and desc_tag:
        desc = desc_tag.get("content", "")
    desc = desc[:300]

    # Notes
    top_notes    = extract_notes(soup, html, "top")
    heart_notes  = extract_notes(soup, html, "middle")
    base_notes   = extract_notes(soup, html, "base")

    # Ratings
    longevity = parse_rating(html, "longevity") or 3
    sillage   = parse_rating(html, "sillage")   or 3
    intensity = parse_rating(html, "intensity") or 3

    # Gender / Season / Time
    gender = ("Unisex"   if re.search(r"for women and men|unisex", html, re.I) else
              "Femenino" if re.search(r"for women|femme",           html, re.I) else
              "Masculino"if re.search(r"for men|homme",             html, re.I) else "Unisex")

    season = [s for s, p in [("🌸 Primavera","spring"),("☀️ Verano","summer"),("🍂 Otoño","fall|autumn"),("❄️ Invierno","winter")] if re.search(p, html, re.I)]
    if not season: season = ["🌍 Todo el año"]

    time_day = [t for t, p in [("🌤 Diurno","day\\s*time|daytime"),("🌙 Nocturno","night|evening")] if re.search(p, html, re.I)]
    if not time_day: time_day = ["🌤 Diurno", "🌙 Nocturno"]

    return dict(name=name, brand=brand, year=year, img_url=img_url, desc=desc,
                gender=gender, season=season, time_day=time_day,
                longevity=longevity, sillage=sillage, intensity=intensity,
                top_notes=top_notes, heart_notes=heart_notes, base_notes=base_notes,
                url=url)


def extract_notes(soup, html, note_type):
    names = []
    heads = {"top": re.compile(r"Top Notes?", re.I),
             "middle": re.compile(r"Middle Notes?|Heart Notes?", re.I),
             "base": re.compile(r"Base Notes?", re.I)}
    pat = heads[note_type]
    capture = False
    for el in soup.find_all(["h3","h4","div","section"]):
        text = el.get_text(strip=True)
        if pat.match(text) and len(text) < 40:
            capture = True; continue
        if capture:
            for img in el.find_all("img", alt=True):
                a = img["alt"].strip()
                if 1 < len(a) < 40 and not re.search(r"logo|icon|fragrantica", a, re.I):
                    names.append(a)
            for s in el.find_all(["a","span"]):
                v = s.get_text(strip=True)
                if 1 < len(v) < 35 and re.match(r"^[A-Za-zÀ-ÿ\s\-&']+$", v):
                    names.append(v)
            if names: break

    # Regex fallback
    if not names:
        chunk_re = {"top": r"Top Notes?[\s\S]{0,1200}?(?=Middle|Heart|Base)",
                    "middle": r"(?:Middle|Heart) Notes?[\s\S]{0,1200}?(?=Base)",
                    "base": r"Base Notes?[\s\S]{0,1200}"}
        chunk_m = re.search(chunk_re[note_type], html, re.I)
        if chunk_m:
            for a in re.findall(r'alt="([^"]{2,40})"', chunk_m.group()):
                if not re.search(r"fragrantica|logo|icon", a, re.I):
                    names.append(a.strip())

    unique = list(dict.fromkeys(
        n[0].upper() + n[1:].lower()
        for n in names if len(n) > 1
    ))[:8]
    return [(n, round(90 - i * (55 / max(len(unique)-1, 1)))) for i, n in enumerate(unique)]


def parse_rating(html, kw):
    m = re.search(rf'"{kw}"\s*:\s*\{{[^}}]*"value"\s*:\s*(\d+\.?\d*)', html, re.I)
    if m:
        v = float(m.group(1))
        if 1 <= v <= 5:
            return round(v)
    return 0


def dots(val, max_val=5):
    filled = "🟡" * val + "⬛" * (max_val - val)
    return filled


def price_links(name, brand):
    q = requests.utils.quote(f"{brand} {name}".strip())
    return [
        ("🌸 Douglas",          f"https://www.douglas.es/es/search?q={q}"),
        ("🏬 El Corte Inglés",  f"https://www.elcorteingles.es/search/?s={q}"),
        ("🖤 Sephora",          f"https://www.sephora.es/search?q={q}"),
        ("💼 Druni",            f"https://www.druni.es/catalogsearch/result/?q={q}"),
        ("📦 Amazon.es",        f"https://www.amazon.es/s?k={q}&i=beauty"),
        ("🧴 Arenal",           f"https://www.perfumeriasarenal.com/busqueda?q={q}"),
        ("✨ Primor",           f"https://www.primor.eu/es/search?q={q}"),
    ]


# ── SEARCH UI ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input("Fragancia", placeholder="Nombre del perfume… (ej: Sauvage Dior)", label_visibility="collapsed")
with col2:
    search_btn = st.button("BUSCAR", use_container_width=True)

st.markdown("<div style='text-align:center;color:rgba(201,160,102,.3);font-family:Cinzel,serif;font-size:9px;letter-spacing:.35em;padding:6px 0'>— O —</div>", unsafe_allow_html=True)

uploaded = st.file_uploader("📷  FOTOGRAFIAR BOTELLA", type=["jpg","jpeg","png","webp"], label_visibility="visible")

if uploaded:
    st.image(uploaded, width=120)
    st.caption("🔍 Introduce el nombre del perfume manualmente en el campo de arriba")

st.markdown("<hr style='margin:20px 0'>", unsafe_allow_html=True)

# ── RUN SEARCH ─────────────────────────────────────────────────────────────────
if search_btn and query:
    with st.spinner("Buscando en Fragrantica…"):
        try:
            p = search_fragrantica(query)
        except Exception as e:
            st.error(f"❌ No encontrado. Prueba con marca + nombre (ej: 'Dior Sauvage').\n\n`{e}`")
            st.stop()

    # ── HERO ──────────────────────────────────────────────────────────────────
    hero_col1, hero_col2 = st.columns([1, 2.8])
    with hero_col1:
        if p["img_url"]:
            st.image(p["img_url"], use_container_width=True)
        else:
            st.markdown("<div style='font-size:60px;text-align:center;opacity:.2;padding:20px 0'>🫙</div>", unsafe_allow_html=True)

    with hero_col2:
        st.markdown(f"""
        <div style='font-family:Cinzel,serif;font-size:9px;letter-spacing:.35em;color:rgba(201,160,102,.55);margin-bottom:4px'>
            {p['brand'].upper()}{" · " + p['year'] if p['year'] else ""}
        </div>
        <div style='font-family:Cormorant Garamond,serif;font-size:clamp(22px,4vw,34px);font-weight:300;font-style:italic;color:#EDE3D0;line-height:1.1;margin-bottom:10px'>
            {p['name']}
        </div>
        """, unsafe_allow_html=True)

        # Tags
        tags_html = "".join(
            f"<span style='font-family:Cinzel,serif;font-size:7.5px;letter-spacing:.18em;padding:4px 10px;border:1px solid rgba(201,160,102,.28);border-radius:2px;color:#C9A066;margin-right:5px;margin-bottom:5px;display:inline-block'>{t}</span>"
            for t in [p["gender"]] + p["season"] + p["time_day"]
        )
        st.markdown(f"<div style='margin-bottom:12px'>{tags_html}</div>", unsafe_allow_html=True)

        if p["desc"]:
            st.markdown(f"<p style='font-size:13.5px;line-height:1.75;color:rgba(237,227,208,.6)'>{p['desc']}</p>", unsafe_allow_html=True)

        st.markdown(f"[↗ Ver en Fragrantica]({p['url']})")

    st.markdown("<hr style='margin:18px 0'>", unsafe_allow_html=True)

    # ── METRICS ───────────────────────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("⧗  LONGEVIDAD", dots(p["longevity"]))
    with m2: st.metric("◈  ESTELA",      dots(p["sillage"]))
    with m3: st.metric("◉  INTENSIDAD",  dots(p["intensity"]))

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────────────────────
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
                          <div style='height:3px;background:rgba(201,160,102,.1);border-radius:2px;overflow:hidden'>
                            <div style='height:100%;width:{pct}%;background:linear-gradient(90deg,#C9A066,#F0D080);border-radius:2px'></div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No disponible")

    with tab2:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        for retailer, url in price_links(p["name"], p["brand"]):
            st.markdown(f"""
            <a href="{url}" target="_blank" style="text-decoration:none">
              <div style='background:rgba(255,255,255,.025);border:1px solid rgba(201,160,102,.12);border-radius:4px;padding:14px 18px;margin-bottom:7px;display:flex;justify-content:space-between;align-items:center;transition:all .2s'>
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
