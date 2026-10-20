# appconfy.com

Sitio de Confy publicado con GitHub Pages (dominio propio, ver `CNAME`). Diseño de Design, sin compilación.

## Qué hay

- `index.html`, `en/index.html` — home (ES/EN), **a mano**.
- `privacidad/`, `eliminar-cuenta/`, `correo-confirmado/` y `en/privacy/`, `en/delete-account/`, `en/email-confirmed/` —
  páginas legales, **generadas** por `build.py` con la plantilla de Design y el texto de `fuentes/politica.md`
  (copia de `POLITICA_DE_PRIVACIDAD.md` del repo de la app). Si cambia la política: copiarla aquí y correr `python build.py`.
- `404.html` — también la genera `build.py`.
- `styles.css`, `theme.js` (modo claro/oscuro), `assets/`, `fonts/` (Inter, JetBrains Mono, Instrument Serif con su licencia OFL) —
  todo alojado aquí: la página no carga nada de servidores externos.
- `google39877097484fefaa.html` — verificación de Search Console de `https://appconfy.com/`. **No borrar.**
- `CNAME` — el dominio. **No tocar.**

## Probar en local

```bash
python -m http.server 4173 --bind 127.0.0.1
```

y abrir http://127.0.0.1:4173/ (no con doble clic: las rutas son de carpeta).

## Pendientes conocidos

- Botón de Google Play: está en "Próximamente" (`aria-disabled`). Cuando exista la ficha, buscar el comentario `<!-- PLAY:` en
  `index.html` y `en/index.html` y seguir la instrucción.
- La página de "Uso limitado de datos de Google" del diseño **no se incluyó**: su texto legal no está aprobado.
- El correo de contacto (`soporte@appconfy.com`) está en `build.py` (`CONTACT`) y en el pie de las dos home.
