"""Genera appconfy.com (GitHub Pages) con el diseño de Design.

Uso:  python build.py
Fuente del texto legal: fuentes/politica.md (copia de POLITICA_DE_PRIVACIDAD.md del repo de
la app; si cambia allá, copiarla aquí y volver a correr esto).

Genera:
  privacidad/  eliminar-cuenta/  correo-confirmado/        (español)
  en/privacy/  en/delete-account/  en/email-confirmed/     (inglés)
  404.html  sitemap.xml  robots.txt
  y REESCRIBE solo el <head> de index.html y en/index.html (SEO + JSON-LD); el cuerpo de las
  dos home se edita a mano.
NO toca: styles.css, theme.js, assets/, fonts/, CNAME ni google39877097484fefaa.html.
Las imágenes para compartir (assets/og-confy-*.png) las genera og_images.py.
"""
import html
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTACT = "soporte@appconfy.com"  # único lugar del correo de contacto
SITE = "https://appconfy.com"
LASTMOD = "2026-10-20"

MONTHS = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7,
    "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7,
    "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}

L = {
    "es": dict(
        lang="es-CO", og_locale="es_CO", skip="Saltar al contenido", nav_label="Principal",
        n1="Cómo funciona", n2="Privacidad", n3="Preguntas",
        toggle_label="Cambiar entre modo claro y oscuro", dark="Oscuro", light="Claro",
        toc_label="En esta página", toc_title="En esta página",
        doubts="¿Dudas sobre este documento?", write_us="Escríbenos a", back="Volver al inicio",
        tagline="Verificación de comprobantes para negocios en Colombia.", contact="Contacto",
        not_aff="Confy no está afiliada a Bancolombia ni a Nequi.",
        policy="Política de privacidad", delete="Eliminar cuenta",
        other_lang_name="English", other_lang="en", updated="Última actualización:",
    ),
    "en": dict(
        lang="en", og_locale="en_US", skip="Skip to content", nav_label="Main",
        n1="How it works", n2="Privacy", n3="FAQ",
        toggle_label="Switch between light and dark mode", dark="Dark", light="Light",
        toc_label="On this page", toc_title="On this page",
        doubts="Questions about this document?", write_us="Write to us at", back="Back to home",
        tagline="Receipt verification for businesses in Colombia.", contact="Contact",
        not_aff="Confy is not affiliated with Bancolombia or Nequi.",
        policy="Privacy policy", delete="Delete account",
        other_lang_name="Español", other_lang="es", updated="Last updated:",
    ),
}

# clave -> (ruta es, ruta en), sin barra final; la home es "" y "en"
PAGES = {
    "home": ("", "en"),
    "privacy": ("privacidad", "en/privacy"),
    "delete": ("eliminar-cuenta", "en/delete-account"),
    "email": ("correo-confirmado", "en/email-confirmed"),
}

# Título y descripción ÚNICOS por página e idioma (título ≤ 60, descripción 70–160).
SEO = {
    ("home", "es"): ("Confy · Verifica comprobantes de Bancolombia",
                     "Confy cruza cada comprobante de transferencia con el aviso real de Bancolombia y te muestra si coincide."),
    ("home", "en"): ("Confy · Verify Bancolombia receipts",
                     "Confy checks every transfer receipt against Bancolombia’s real notification and shows you whether it matches."),
    ("privacy", "es"): ("Política de privacidad · Confy",
                        "Política de privacidad de Confy: qué datos recoge, para qué los usa, cuánto tiempo los conserva y cómo borrarlos."),
    ("privacy", "en"): ("Privacy policy · Confy",
                        "Confy’s privacy policy: what data it collects, why it uses it, how long it keeps it and how to delete it."),
    ("delete", "es"): ("Eliminar cuenta · Confy",
                       "Cómo borrar tu cuenta de Confy y qué pasa con tus datos: qué se borra si eres dueño y qué queda si eres trabajador."),
    ("delete", "en"): ("Delete account · Confy",
                       "How to delete your Confy account and what happens to your data: what is deleted if you are an owner and what stays if you are an employee."),
    ("email", "es"): ("Correo confirmado · Confy",
                      "Tu correo quedó confirmado. Vuelve a la app de Confy e inicia sesión con tu correo y contraseña."),
    ("email", "en"): ("Email confirmed · Confy",
                      "Your email is confirmed. Go back to the Confy app and sign in with your email and password."),
}
SEO_404 = ("Página no encontrada · Page not found · Confy",
           "La página que buscas no existe. / The page you are looking for does not exist.")

# Imagen para compartir 1200×630 (la genera og_images.py).
OG = {
    "es": ("assets/og-confy-es.png", "Confy: que ningún comprobante falso te engañe otra vez"),
    "en": ("assets/og-confy-en.png", "Confy: never get fooled by a fake receipt again"),
}

# Párrafo "Qué es Confy" de la home (2 frases, mismos datos que la política) y su JSON-LD.
ABOUT = {
    "es": "Confy es una app que ayuda a negocios en Colombia a verificar comprobantes de transferencias bancarias. "
          "Compara el monto, la fecha y la hora de cada comprobante con el aviso que Bancolombia envía a tu correo y te muestra si coincide.",
    "en": "Confy is an app that helps businesses in Colombia verify bank transfer receipts. "
          "It compares the amount, date and time on each receipt with the notification Bancolombia sends to your email and shows you whether it matches.",
}


def url(key, lang):
    r = PAGES[key][0 if lang == "es" else 1]
    return f"{SITE}/{r}/" if r else f"{SITE}/"


def ruta(key, lang):
    return PAGES[key][0 if lang == "es" else 1]


def depth(path):
    return path.count("/") + 1 if path else 0


# ── Texto legal ──────────────────────────────────────────────────────────────
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    # Enlaces markdown [texto](https://…): solo http(s).
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" rel="noopener">\1</a>', t)
    return re.sub(r"([\w.+-]+@[\w-]+(?:\.[\w-]+)+)", r'<a href="mailto:\1">\1</a>', t)


def slug(t):
    s = re.sub(r"[^a-z0-9]+", "-", re.sub(r"[̀-ͯ]", "", unicodedata.normalize("NFD", t.lower()))).strip("-")
    return s or "seccion"


def prose(md):
    """Markdown mínimo de la política: ##, listas con '-', párrafos. Devuelve (html, [(id, título)])."""
    out, toc, in_list, used = [], [], False, set()
    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(line[2:])}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if not line:
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            sid, n = slug(title), 2
            while sid in used:
                sid, n = f"{slug(title)}-{n}", n + 1
            used.add(sid)
            toc.append((sid, title))
            out.append(f'<h2 id="{sid}">{inline(title)}</h2>')
        else:
            out.append(f"<p>{inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n        ".join(out), toc


# ── <head>: SEO, Open Graph, JSON-LD ─────────────────────────────────────────
def jsonld_home(lang):
    """Organization + WebSite + SoftwareApplication. Sin precio ni calificaciones.
    La descripción es EXACTAMENTE el párrafo visible "Qué es Confy"."""
    about = ABOUT[lang]
    page = url("home", lang)
    org = f"{SITE}/#organization"
    graph = [
        {
            "@type": "Organization",
            "@id": org,
            "name": "Confy",
            "url": f"{SITE}/",
            "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/apple-touch-icon.png", "width": 180, "height": 180},
            "email": CONTACT,
            "contactPoint": {"@type": "ContactPoint", "contactType": "customer support", "email": CONTACT},
        },
        {
            "@type": "WebSite",
            "@id": f"{SITE}/#website",
            "name": "Confy",
            "url": f"{SITE}/",
            "inLanguage": ["es-CO", "en"],
            "publisher": {"@id": org},
        },
        {
            "@type": "SoftwareApplication",
            "@id": f"{SITE}/#app",
            "name": "Confy",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Android",
            "description": about,
            "url": page,
            "inLanguage": L[lang]["lang"],
            "publisher": {"@id": org},
        },
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)


def head(key, lang, up, *, noindex=False, jsonld=None, page404=False):
    t = L[lang]
    title, desc = SEO_404 if page404 else SEO[(key, lang)]
    img_rel, img_alt = OG[lang]
    img = f"{SITE}/{img_rel}"
    other = "en" if lang == "es" else "es"
    if page404:
        me = es_u = en_u = None
    else:
        me, es_u, en_u = url(key, lang), url(key, "es"), url(key, "en")
    e_title, e_desc, e_alt = html.escape(title), html.escape(desc), html.escape(img_alt)
    lines = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{e_title}</title>",
        f'<meta name="description" content="{e_desc}">',
    ]
    if noindex:
        lines.append('<meta name="robots" content="noindex">')
    if not page404:
        lines += [
            f'<link rel="canonical" href="{me}">',
            f'<link rel="alternate" hreflang="es-CO" href="{es_u}">',
            f'<link rel="alternate" hreflang="en" href="{en_u}">',
            f'<link rel="alternate" hreflang="x-default" href="{es_u}">',
        ]
    lines += [
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Confy">',
        f'<meta property="og:title" content="{e_title}">',
        f'<meta property="og:description" content="{e_desc}">',
    ]
    if not page404:
        lines.append(f'<meta property="og:url" content="{me}">')
    lines += [
        f'<meta property="og:locale" content="{t["og_locale"]}">',
        f'<meta property="og:locale:alternate" content="{L[other]["og_locale"]}">',
        f'<meta property="og:image" content="{img}">',
        '<meta property="og:image:type" content="image/png">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{e_alt}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{e_title}">',
        f'<meta name="twitter:description" content="{e_desc}">',
        f'<meta name="twitter:image" content="{img}">',
        f'<meta name="twitter:image:alt" content="{e_alt}">',
        '<meta name="theme-color" content="#1B4332">',
        f'<link rel="icon" type="image/png" sizes="32x32" href="{up}assets/favicon-32.png">',
        f'<link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png">',
        f'<link rel="stylesheet" href="{up}styles.css">',
        f'<script src="{up}theme.js"></script>',
    ]
    if jsonld:
        lines.append(f'<script type="application/ld+json">\n{jsonld}\n</script>')
    body = "\n".join("\n".join("  " + ln for ln in x.split("\n")) for x in lines)
    return "<head>\n" + body + "\n</head>"


# ── Páginas ──────────────────────────────────────────────────────────────────
def shell(key, lang, h1, meta_html, body_html, toc, short=False, contact_block=True, back_link=False,
          abs_root=False, page404=False, extra_not_aff=None):
    t = L[lang]
    mine = ruta(key, lang)
    other_path = ruta(key, "en" if lang == "es" else "es")
    if abs_root:
        up, home, other_url = "/", "/", "/en/"
    else:
        up = "../" * depth(mine)
        home = up if lang == "es" else f"{up}en/"
        other_url = f"{up}{other_path}/" if other_path else up
    toc_html = ""
    if not short:
        items = "\n".join(f'          <li><a href="#{i}">{html.escape(tt, quote=False)}</a></li>' for i, tt in toc)
        toc_html = f"""      <nav class="toc" aria-label="{t['toc_label']}">
        <p class="toc-title">{t['toc_title']}</p>
        <ol>
{items}
        </ol>
      </nav>
"""
    back = f'\n          <p><a href="{home}">{t["back"]}</a></p>' if back_link else ""
    contact = f"""
        <div class="legal-contact">
          <h2 class="legal-contact-title">{t['doubts']}</h2>
          <p>{t['write_us']} <a href="mailto:{CONTACT}">{CONTACT}</a></p>{back}
        </div>""" if contact_block else ""
    meta = f"\n        {meta_html}" if meta_html else ""
    body_cls = "wrap legal-body legal-short" if short else "wrap legal-body"
    eyebrow = "404" if page404 else f"/{mine}"
    return f"""<!doctype html>
<html lang="{t['lang']}">
{head(key, lang, up, noindex=(key == 'email' and not page404), page404=page404)}
<body>
  <a class="skip" href="#contenido">{t['skip']}</a>
  <header class="site-header">
    <div class="wrap header-row">
      <a class="brand" href="{home}"><img src="{up}assets/confy-icono.webp" alt="" width="32" height="32"><span>Confy</span></a>
      <nav class="main-nav" aria-label="{t['nav_label']}">
        <a href="{home}#como-funciona">{t['n1']}</a>
        <a href="{home}#confianza">{t['n2']}</a>
        <a href="{home}#preguntas">{t['n3']}</a>
      </nav>
      <div class="header-tools">
        <a class="lang-link" href="{other_url}" hreflang="{t['other_lang']}" lang="{t['other_lang']}">{t['other_lang_name']}</a>
        <button class="theme-toggle" type="button" aria-label="{t['toggle_label']}"><span class="solo-claro">{t['dark']}</span><span class="solo-oscuro">{t['light']}</span></button>
      </div>
    </div>
  </header>
  <main id="contenido">
    <section class="legal-head">
      <div class="wrap">
        <p class="eyebrow">{eyebrow}</p>
        <h1>{html.escape(h1, quote=False)}</h1>{meta}
      </div>
    </section>
    <div class="{body_cls}">
{toc_html}      <article class="prose">
        {body_html}{contact}
      </article>
    </div>
  </main>
{footer(key, lang, up, other_url, abs_root, extra_not_aff)}
</body>
</html>
"""


def footer(key, lang, up, other_url, abs_root=False, extra_not_aff=None):
    t = L[lang]
    pol, dele = ruta("privacy", lang), ruta("delete", lang)
    notes = f"<span>{t['not_aff']}</span>"
    if extra_not_aff:
        notes += f"\n        <span lang=\"{extra_not_aff[0]}\">{extra_not_aff[1]}</span>"
    return f"""  <footer class="site-footer">
    <div class="wrap footer-row">
      <div class="footer-brand">
        <span class="brand-sm"><img src="{up}assets/confy-icono.webp" alt="" width="22" height="22">Confy</span>
        <span>{t['tagline']}</span>
        {notes}
      </div>
      <nav class="footer-legal" aria-label="Legal">
          <a href="{up}{pol}/">{t['policy']}</a>
          <a href="{up}{dele}/">{t['delete']}</a>
      </nav>
      <div class="footer-contact">
        <span>{t['contact']}</span>
        <a href="mailto:{CONTACT}">{CONTACT}</a>
        <span>© 2026 Confy · appconfy.com</span>
        <a class="lang-link-foot" href="{other_url}" hreflang="{t['other_lang']}" lang="{t['other_lang']}">{t['other_lang_name']}</a>
      </div>
    </div>
  </footer>"""


def meta_date(lang, line):
    """'Última actualización: 11 de octubre de 2026' -> <p class="meta">… <time datetime="2026-10-11">…</time></p>"""
    label = L[lang]["updated"]
    txt = line.split(":", 1)[1].strip()
    nums = re.findall(r"\d{4}|\d{1,2}|[A-Za-zÁÉÍÓÚáéíóú]+", txt)
    day = next(int(n) for n in nums if n.isdigit() and len(n) <= 2)
    year = next(int(n) for n in nums if n.isdigit() and len(n) == 4)
    month = next(MONTHS[w.lower()] for w in nums if w.lower() in MONTHS)
    return f'<p class="meta">{label} <time datetime="{year:04d}-{month:02d}-{day:02d}">{html.escape(txt, quote=False)}</time></p>'


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8"))  # LF, sin conversión de saltos de línea


def rewrite_home_head(lang):
    """Sustituye SOLO el <head> de la home y comprueba que el párrafo 'Qué es Confy' coincide con el JSON-LD."""
    rel = "index.html" if lang == "es" else "en/index.html"
    p = ROOT / rel
    s = p.read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert html.escape(ABOUT[lang], quote=False) in s, f"{rel}: falta el párrafo 'Qué es Confy' visible (debe ser igual al JSON-LD)"
    up = "" if lang == "es" else "../"
    s = re.sub(r'<html lang="[^"]*">', f'<html lang="{L[lang]["lang"]}">', s, count=1)
    new = head("home", lang, up, jsonld=jsonld_home(lang))
    s2, n = re.subn(r"<head>.*?</head>", lambda m: new, s, count=1, flags=re.S)
    assert n == 1, rel
    p.write_bytes(s2.encode("utf-8"))


def sitemap():
    rows = []
    for key in ("home", "privacy", "delete"):  # correo-confirmado va con noindex: no se lista
        es_u, en_u = url(key, "es"), url(key, "en")
        for loc in (es_u, en_u):
            rows.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{LASTMOD}</lastmod>
    <xhtml:link rel="alternate" hreflang="es-CO" href="{es_u}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{en_u}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{es_u}"/>
  </url>""")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def main():
    md = (ROOT / "fuentes/politica.md").read_text(encoding="utf-8")
    es, en = md.split("\n# Privacy Policy for Confy", 1)
    en = "# Privacy Policy for Confy" + en

    for lang, doc in (("es", es), ("en", en)):
        lines = doc.splitlines()
        date_line = next(x for x in lines if re.match(r"^(Última actualización|Last updated):", x))
        first_h2 = next(i for i, x in enumerate(lines) if x.startswith("## "))
        body, toc = prose("\n".join(lines[first_h2:]))
        intro_lines = [x for x in lines[:first_h2] if x.strip() and not x.startswith("# ") and x != date_line]
        intro = "\n        ".join(f"<p>{inline(x)}</p>" for x in intro_lines)
        full = (intro + "\n        " if intro else "") + body
        is_es = lang == "es"

        # Política: el texto ya trae su sección "Contacto", sin bloque extra.
        write(f"{ruta('privacy', lang)}/index.html", shell(
            "privacy", lang, "Política de privacidad" if is_es else "Privacy policy",
            meta_date(lang, date_line), full, toc, contact_block=False))

        # Eliminar cuenta: la sección de la política.
        a, b = ("## Cómo eliminar tu cuenta", "## Seguridad") if is_es else ("## How to delete your account", "## Security")
        sec = doc[doc.index(a):doc.index(b)].replace(a, "", 1)
        del_body, _ = prose(sec)
        more = (f'<p>Más detalles en la <a href="../{ruta("privacy", "es")}/">política de privacidad</a>.</p>' if is_es
                else f'<p>More details in the <a href="../../{ruta("privacy", "en")}/">privacy policy</a>.</p>')
        write(f"{ruta('delete', lang)}/index.html", shell(
            "delete", lang, "Eliminar cuenta" if is_es else "Delete account",
            "", del_body + "\n        " + more, []))

    # Correo confirmado (noindex): el texto de siempre. En español se conserva la línea en inglés.
    write(f"{ruta('email', 'es')}/index.html", shell(
        "email", "es", "Correo confirmado", "",
        "<p>Tu correo quedó confirmado.</p>\n        <p>Vuelve a la app de Confy e inicia sesión con tu correo y contraseña.</p>\n"
        '        <p lang="en" class="meta">Your email is confirmed. Go back to the Confy app and sign in.</p>',
        [], short=True, back_link=True))
    write(f"{ruta('email', 'en')}/index.html", shell(
        "email", "en", "Email confirmed", "",
        "<p>Your email is confirmed.</p>\n        <p>Go back to the Confy app and sign in.</p>",
        [], short=True, back_link=True))

    # 404 bilingüe: rutas absolutas (se sirve desde cualquier profundidad).
    write("404.html", shell(
        "home", "es", "Página no encontrada", "",
        '<p lang="en">Page not found.</p>\n        <p><a href="/">Volver al inicio</a> · <a href="/en/" lang="en">Back to home</a></p>',
        [], short=True, contact_block=False, abs_root=True, page404=True,
        extra_not_aff=("en", L["en"]["not_aff"])))

    rewrite_home_head("es")
    rewrite_home_head("en")
    write("sitemap.xml", sitemap())
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    write(".nojekyll", "")
    print("listo")


if __name__ == "__main__":
    main()
