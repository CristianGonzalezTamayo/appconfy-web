"""Genera las páginas legales de appconfy.com (GitHub Pages) con el diseño de Design.

Uso:  python build.py
Fuente del texto: fuentes/politica.md (copia de POLITICA_DE_PRIVACIDAD.md del repo de
la app; si cambia allá, copiarla aquí y volver a correr esto).

Salida (marcado igual que las plantillas de Design, solo con el texto legal):
  privacidad/  eliminar-cuenta/  correo-confirmado/        (español)
  en/privacy/  en/delete-account/  en/email-confirmed/     (inglés)
  404.html
NO genera ni toca: index.html y en/index.html (la home, a mano), styles.css, theme.js,
assets/, fonts/, CNAME ni google39877097484fefaa.html (verificación de Search Console).
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTACT = "soporte@appconfy.com"  # único lugar del correo de contacto
SITE = "https://appconfy.com"

MONTHS = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7,
    "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7,
    "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}

L = {
    "es": dict(
        lang="es", og_locale="es_CO", skip="Saltar al contenido", nav_label="Principal",
        n1="Cómo funciona", n2="Privacidad", n3="Preguntas",
        toggle_label="Cambiar entre modo claro y oscuro", dark="Oscuro", light="Claro",
        toc_label="En esta página", toc_title="En esta página",
        doubts="¿Dudas sobre este documento?", write_us="Escríbenos a", back="Volver al inicio",
        tagline="Verificación de comprobantes para negocios en Colombia.", contact="Contacto",
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
        policy="Privacy policy", delete="Delete account",
        other_lang_name="Español", other_lang="es", updated="Last updated:",
    ),
}

# slug -> (ruta es, ruta en) sin barras
PAGES = {
    "privacy": ("privacidad", "en/privacy"),
    "delete": ("eliminar-cuenta", "en/delete-account"),
    "email": ("correo-confirmado", "en/email-confirmed"),
}


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return re.sub(r"([\w.+-]+@[\w-]+(?:\.[\w-]+)+)", r'<a href="mailto:\1">\1</a>', t)


def slug(t):
    s = re.sub(r"[^a-z0-9]+", "-", re.sub(r"[̀-ͯ]", "", __import__("unicodedata").normalize("NFD", t.lower()))).strip("-")
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


def ruta(page, lang):
    return PAGES[page][0 if lang == "es" else 1]


def depth(path):
    return path.count("/") + 1


def shell(page, lang, title, desc, h1, meta_html, body_html, toc, short=False, contact_block=True, back_link=False):
    t = L[lang]
    es_path, en_path = ruta(page, "es"), ruta(page, "en")
    mine = es_path if lang == "es" else en_path
    other = en_path if lang == "es" else es_path
    up = "../" * depth(mine)
    home = up if lang == "es" else f"{up}en/"
    other_url = f"{up}{other}/"
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
    d, e = html.escape(desc), html.escape(title)
    alt_es = f"{SITE}/{es_path}/"
    alt_en = f"{SITE}/{en_path}/"
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e} · Confy</title>
  <meta name="description" content="{d}">
  <link rel="canonical" href="{SITE}/{mine}/">
  <link rel="alternate" hreflang="es" href="{alt_es}">
  <link rel="alternate" hreflang="en" href="{alt_en}">
  <link rel="alternate" hreflang="x-default" href="{alt_es}">
  <meta property="og:title" content="{e} · Confy">
  <meta property="og:description" content="{d}">
  <meta property="og:url" content="{SITE}/{mine}/">
  <meta property="og:locale" content="{t['og_locale']}">
  <meta name="theme-color" content="#1B4332">
  <link rel="icon" type="image/png" sizes="32x32" href="{up}assets/favicon-32.png">
  <link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png">
  <link rel="stylesheet" href="{up}styles.css">
  <script src="{up}theme.js"></script>
</head>
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
        <p class="eyebrow">/{mine}</p>
        <h1>{html.escape(h1, quote=False)}</h1>{meta}
      </div>
    </section>
    <div class="{body_cls}">
{toc_html}      <article class="prose">
        {body_html}{contact}
      </article>
    </div>
  </main>
{footer(lang, up, other_url)}
</body>
</html>
"""


def footer(lang, up, other_url):
    t = L[lang]
    pol, dele = ruta("privacy", lang), ruta("delete", lang)
    return f"""  <footer class="site-footer">
    <div class="wrap footer-row">
      <div class="footer-brand">
        <span class="brand-sm"><img src="{up}assets/confy-icono.webp" alt="" width="22" height="22">Confy</span>
        <span>{t['tagline']}</span>
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


def main():
    md = (ROOT / "fuentes/politica.md").read_text(encoding="utf-8")
    es, en = md.split("\n# Privacy Policy for Confy", 1)
    en = "# Privacy Policy for Confy" + en

    for lang, doc in (("es", es), ("en", en)):
        lines = doc.splitlines()
        date_line = next(x for x in lines if re.match(r"^(Última actualización|Last updated):", x))
        first_h2 = next(i for i, x in enumerate(lines) if x.startswith("## "))
        body, toc = prose("\n".join(lines[first_h2:]))
        # Intro (sin título ni fecha): lo que va entre la fecha y el primer ##
        intro_lines = [x for x in lines[:first_h2] if x.strip() and not x.startswith("# ") and x != date_line]
        intro = "\n        ".join(f"<p>{inline(x)}</p>" for x in intro_lines)
        full = (intro + "\n        " if intro else "") + body
        is_es = lang == "es"

        # Política: el texto ya trae su sección "Contacto", sin bloque extra.
        write(f"{ruta('privacy', lang)}/index.html", shell(
            "privacy", lang,
            "Política de privacidad" if is_es else "Privacy policy",
            "Qué datos recoge Confy, para qué y por cuánto tiempo." if is_es
            else "What data Confy collects, why, and for how long.",
            "Política de privacidad" if is_es else "Privacy policy",
            meta_date(lang, date_line), full, toc, contact_block=False))

        # Eliminar cuenta: la sección de la política, igual que antes.
        a, b = ("## Cómo eliminar tu cuenta", "## Seguridad") if is_es else ("## How to delete your account", "## Security")
        sec = doc[doc.index(a):doc.index(b)].replace(a, "", 1)
        del_body, _ = prose(sec)
        more = (f'<p>Más detalles en la <a href="../{ruta("privacy", "es")}/">política de privacidad</a>.</p>' if is_es
                else f'<p>More details in the <a href="../../{ruta("privacy", "en")}/">privacy policy</a>.</p>')
        write(f"{ruta('delete', lang)}/index.html", shell(
            "delete", lang,
            "Eliminar cuenta" if is_es else "Delete account",
            "Cómo borrar tu cuenta y qué pasa con tus datos." if is_es
            else "How to delete your account and what happens to your data.",
            "Eliminar cuenta" if is_es else "Delete account",
            "", del_body + "\n        " + more, []))

    # Correo confirmado: el texto de siempre. En español se conserva la línea en inglés.
    write(f"{ruta('email', 'es')}/index.html", shell(
        "email", "es", "Correo confirmado", "Correo confirmado", "Correo confirmado", "",
        "<p>Tu correo quedó confirmado.</p>\n        <p>Vuelve a la app de Confy e inicia sesión con tu correo y contraseña.</p>\n"
        '        <p lang="en" class="meta">Your email is confirmed. Go back to the Confy app and sign in.</p>',
        [], short=True, back_link=True))
    write(f"{ruta('email', 'en')}/index.html", shell(
        "email", "en", "Email confirmed", "Email confirmed", "Email confirmed", "",
        "<p>Your email is confirmed.</p>\n        <p>Go back to the Confy app and sign in.</p>",
        [], short=True, back_link=True))

    # 404: rutas absolutas (se sirve desde cualquier profundidad).
    page404 = shell("email", "es", "Página no encontrada", "Página no encontrada", "Página no encontrada", "",
                    '<p><a href="/">Volver al inicio</a></p>', [], short=True, contact_block=False)
    page404 = (page404.replace('href="../', 'href="/').replace('src="../', 'src="/')
               .replace('<link rel="canonical" href="https://appconfy.com/correo-confirmado/">\n', "")
               .replace('  <link rel="alternate" hreflang="es" href="https://appconfy.com/correo-confirmado/">\n', "")
               .replace('  <link rel="alternate" hreflang="en" href="https://appconfy.com/en/email-confirmed/">\n', "")
               .replace('  <link rel="alternate" hreflang="x-default" href="https://appconfy.com/correo-confirmado/">\n', "")
               .replace('  <meta property="og:url" content="https://appconfy.com/correo-confirmado/">\n', "")
               .replace('<p class="eyebrow">/correo-confirmado</p>', '<p class="eyebrow">404</p>')
               .replace('href="/correo-confirmado/"', 'href="/en/"').replace('href="/en/email-confirmed/"', 'href="/en/"')
               .replace('<meta name="theme-color"', '<meta name="robots" content="noindex">\n  <meta name="theme-color"'))
    write("404.html", page404)
    write(".nojekyll", "")
    print("listo")


if __name__ == "__main__":
    main()
