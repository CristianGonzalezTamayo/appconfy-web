"""Genera las páginas legales de appconfy.com (GitHub Pages).

Uso:  python build.py
Fuente de la política: fuentes/politica.md (copia de POLITICA_DE_PRIVACIDAD.md del
repo de la app; si cambia allá, copiarla aquí y volver a correr esto).

Salida: index.html, privacidad/, eliminar-cuenta/, correo-confirmado/, 404.html.
Estilo sobrio a propósito: solo texto legal legible, sin diseño de marca.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTACT = "confy.cuenta.soporte@gmail.com"  # único lugar del correo de contacto

CSS = """
:root{--text:#111827;--muted:#6B7280;--line:#E5E7EB;--accent:#1B4332}
*{box-sizing:border-box}
body{margin:0;background:#fff;color:var(--text);font:17px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:720px;margin:0 auto;padding:40px 20px 64px}
header{max-width:720px;margin:0 auto;padding:20px 20px 0;display:flex;align-items:center;gap:10px}
header a{display:flex;align-items:center;gap:10px;color:var(--accent);font-weight:700;text-decoration:none}
header img{width:28px;height:28px}
h1{font-size:30px;line-height:1.2;margin:0 0 6px}
h2{font-size:20px;margin:32px 0 6px}
a{color:var(--accent)}
.meta{color:var(--muted);margin:0 0 24px}
.lang{color:var(--muted);font-size:15px}
hr{border:0;border-top:1px solid var(--line);margin:48px 0}
footer{max-width:720px;margin:0 auto;padding:24px 20px 40px;border-top:1px solid var(--line);color:var(--muted);font-size:14px}
footer a{color:var(--muted);margin-right:16px}
"""


def page(title, body, lang="es", depth=1):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="icon" href="{up}shield-64.png">
<style>{CSS}</style>
</head>
<body>
<header><a href="{up}"><img src="{up}shield-64.png" alt="">Confy</a></header>
<main>
{body}
</main>
<footer>
<a href="{up}privacidad/">Política de privacidad / Privacy</a>
<a href="{up}eliminar-cuenta/">Eliminar cuenta / Delete account</a>
<a href="mailto:{CONTACT}">{CONTACT}</a>
</footer>
</body>
</html>
"""


def inline(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return re.sub(r"([\w.+-]+@[\w-]+\.[\w.]+)", r'<a href="mailto:\1">\1</a>', t)


def md_to_html(md):
    """Markdown mínimo de la política: #, ##, listas con '-', párrafos."""
    out, in_list = [], False
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
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif re.match(r"^(Última actualización|Last updated):", line):
            out.append(f'<p class="meta">{inline(line)}</p>')
        else:
            out.append(f"<p>{inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def main():
    md = (ROOT / "fuentes/politica.md").read_text(encoding="utf-8")
    es, en = md.split("\n# Privacy Policy for Confy", 1)
    en = "# Privacy Policy for Confy" + en
    write("privacidad/index.html", page(
        "Política de privacidad — Confy",
        '<p class="lang"><a href="#en">English version below</a></p>\n'
        + md_to_html(es) + '\n<hr>\n<div id="en" lang="en">\n' + md_to_html(en) + "\n</div>"))

    sec_es = es[es.index("## Cómo eliminar tu cuenta"):es.index("## Seguridad")]
    sec_en = en[en.index("## How to delete your account"):en.index("## Security")]
    write("eliminar-cuenta/index.html", page(
        "Eliminar tu cuenta — Confy",
        "<h1>Eliminar tu cuenta de Confy</h1>\n"
        '<p class="lang"><a href="#en">English below</a></p>\n'
        + md_to_html(sec_es.replace("## Cómo eliminar tu cuenta", ""))
        + '\n<p>Más detalles en la <a href="../privacidad/">política de privacidad</a>.</p>'
        + '\n<hr>\n<div id="en" lang="en">\n<h1>Delete your Confy account</h1>\n'
        + md_to_html(sec_en.replace("## How to delete your account", ""))
        + '\n<p>More details in the <a href="../privacidad/#en">privacy policy</a>.</p>\n</div>'))

    write("correo-confirmado/index.html", page(
        "Correo confirmado — Confy",
        "<h1>Tu correo quedó confirmado</h1>\n"
        "<p>Vuelve a la app de Confy e inicia sesión con tu correo y contraseña.</p>\n"
        '<p lang="en" class="meta">Your email is confirmed. Go back to the Confy app and sign in.</p>'))

    write("index.html", page(
        "Confy",
        "<h1>Confy</h1>\n"
        "<p>Verificación de comprobantes de transferencia para negocios en Colombia.</p>\n"
        '<ul>\n<li><a href="privacidad/">Política de privacidad / Privacy policy</a></li>\n'
        '<li><a href="eliminar-cuenta/">Eliminar cuenta / Delete account</a></li>\n</ul>', depth=0))

    write("404.html", page(
        "Página no encontrada — Confy",
        '<h1>Página no encontrada</h1>\n<p><a href="/">Volver al inicio</a></p>', depth=0)
        .replace('href=""', 'href="/"').replace('src="shield', 'src="/shield'))
    write("CNAME", "appconfy.com\n")
    write(".nojekyll", "")
    print("listo")


if __name__ == "__main__":
    main()
