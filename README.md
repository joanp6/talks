# talks

Charlas que he dado en eventos: temas, diapositivas y recursos.

Es una web estática generada con un script de Python propio (`build.py`) y
desplegada en Cloudflare Pages. No hay servidor: el script produce HTML, CSS y
XML en la carpeta `dist/`, y Cloudflare sirve esos archivos.

## Cómo funciona

```
content/talks/*.md  ──┐
templates/*.html    ──┼──>  build.py  ──>  dist/  ──>  Cloudflare Pages
public/ (CSS, PDFs) ──┘
```

1. `build.py` lee cada `.md` de `content/talks/` y valida su cabecera
   (frontmatter) con Pydantic. Si falta un campo o tiene un valor incorrecto,
   el build se para y te dice qué archivo y qué campo fallan.
2. Descarta las charlas con `draft: true` y ordena el resto por fecha.
3. Rellena las plantillas Jinja2 de `templates/` y escribe el HTML en `dist/`.
4. Copia `public/` tal cual a `dist/`.

| Archivo / carpeta | Qué contiene |
|---|---|
| `build.py` | El generador. Arriba del todo está `SITE_URL` y el título del sitio. |
| `check_size.py` | Comprueba que ningún archivo supera 25 MiB. |
| `content/talks/` | Una charla = un archivo `.md`. |
| `templates/` | HTML de cada página (`index`, `talk`, `about`, `404`) + `rss.xml` y `sitemap.xml`. |
| `public/` | Archivos que se copian sin cambios: `style.css`, `favicon.svg`, `slides/*.pdf` y `slides/*.html`. |
| `dist/` | La web generada. No se sube a Git: la genera Cloudflare en cada deploy. |

## Arrancar en local

Necesitas Python 3.13 o superior. En Windows el comando es `py`.

1. Crea el entorno virtual (solo la primera vez):

   ```bash
   py -m venv .venv
   ```

2. Actívalo (cada vez que abras una terminal nueva):

   ```bash
   .venv\Scripts\activate
   ```

3. Instala las dependencias (la primera vez o si cambia `requirements.txt`):

   ```bash
   pip install -r requirements.txt
   ```

4. Genera la web:

   ```bash
   python build.py
   ```

5. Sírvela en <http://localhost:8000>:

   ```bash
   python -m http.server -d dist 8000
   ```

No hay recarga automática. Si cambias algo, vuelve a ejecutar
`python build.py` y recarga el navegador.

## Añadir una charla nueva

1. **Copia la plantilla.** Duplica `content/talks/ejemplo.md` y cámbiale el
   nombre. El nombre del archivo es la URL: `mi-charla.md` →
   `/charlas/mi-charla/`. Usa solo minúsculas, números y guiones.
2. **Rellena la cabecera.** Cambia los valores entre los dos `---`, borra los
   campos opcionales que no uses y escribe el contenido debajo en Markdown.
   Pon `draft: false` cuando quieras publicarla.
3. **(Opcional) Sube el PDF.** Cópialo a `public/slides/mi-charla.pdf` y pon
   `slidesPdf: "/slides/mi-charla.pdf"`. Debe pesar **menos de 25 MiB**.
4. **Comprueba y publica.** Ejecuta `python build.py` y
   `python check_size.py`. Si los dos dicen `OK`, haz commit y push.
   Cloudflare la publicará en uno o dos minutos.

### Campos de la cabecera

| Campo | Obligatorio | Formato |
|---|---|---|
| `title` | sí | texto |
| `event` | sí | texto |
| `eventUrl` | no | URL |
| `date` | sí | `AAAA-MM-DD` |
| `city` | no | texto |
| `language` | sí | `es`, `ca`, `en` o `it` |
| `tags` | sí | lista, p. ej. `["QA", "IA"]` (puede ser `[]`) |
| `summary` | sí | texto, máximo 200 caracteres |
| `slidesPdf` | no | `/slides/<nombre>.pdf` (el archivo debe existir en `public/slides/`) |
| `slidesEmbed` | no | URL de embed de Google Slides, Speaker Deck o Canva |
| `video` | no | URL |
| `resources` | no | lista de `label` + `url` |
| `draft` | no | `true` / `false` (por defecto `false`). Con `true` no se publica. |

Cómo se muestran las diapositivas:

- Con `slidesEmbed`: se ven en un iframe 16:9.
- Con `slidesPdf`: aparece un botón de descarga. Si además no hay
  `slidesEmbed`, el PDF también se muestra en un visor.
- Sin ninguno de los dos: no aparece la sección.

## Subir una presentación HTML

Las presentaciones en HTML (como las de `mcp-en-qa` y `statuslinebar`) son
**un único archivo** con el HTML, el CSS y el JavaScript dentro. No necesitan
nada más en el servidor.

1. **Revisa el contenido.** Todo lo que hay en `public/` se publica **aunque
   la charla tenga `draft: true`**, porque `build.py` copia la carpeta entera.
   Si la charla todavía no es pública, deja la presentación fuera del repo
   hasta publicarla. Comprueba también que no lleva datos internos del trabajo
   (nombres de clientes, tickets, URLs internas).
2. **Cópiala** a `public/slides/<slug>.html`, con el mismo nombre que el `.md`
   de la charla. Por ejemplo, `public/slides/mi-charla.html`.
3. **Enlázala** desde la cabecera de la charla, en `resources`:

   ```yaml
   resources:
     - label: "Presentación a pantalla completa"
       url: "https://iatalks.pages.dev/slides/mi-charla"
   ```

   Pon la URL **sin `.html`**. Cloudflare Pages quita la extensión y, si la
   pones, redirige (código 308) a la versión sin ella.
4. **(Opcional) Incrústala** en la página con
   `slidesEmbed: "https://iatalks.pages.dev/slides/mi-charla"`. Ojo: dentro
   del iframe las flechas del teclado solo funcionan después de hacer clic en
   la presentación. Por eso las charlas actuales solo la enlazan.
5. **Comprueba y publica** como cualquier otra charla: `python build.py`,
   `python check_size.py`, commit y push.

Para que la presentación tenga un botón de vuelta a la web, las actuales
llevan este enlace en la barra superior:

```html
<a id="backLink" href="/charlas/mi-charla/" target="_top">← Volver a la charla</a>
<script>
  // Dentro de un iframe ya estás en la charla: el enlace sobra.
  if (window.self !== window.top) document.getElementById("backLink").hidden = true;
</script>
```

`target="_top"` hace que, si se pulsa desde un iframe, se abra en la ventana
entera y no dentro del recuadro.

## Límite de 25 MiB por archivo

Cloudflare Pages **rechaza cualquier archivo de más de 25 MiB**. Si un PDF de
diapositivas pesa más, comprímelo (por ejemplo, exportándolo con menos calidad
de imagen) o usa `slidesEmbed` en su lugar.

`python check_size.py` revisa `public/` y `dist/` y falla si encuentra algún
archivo por encima del límite. También se ejecuta en cada deploy de Cloudflare
(ver el build command de abajo), así que un archivo demasiado grande cancela
el deploy en vez de romper la web.

## Desplegar en Cloudflare Pages

Solo hay que hacerlo una vez. Después, cada push a `main` se publica solo.

1. En el dashboard de Cloudflare: **Workers & Pages → Create application →
   pestaña Pages → Import an existing Git repository** y elige `joanp6/talks`.
2. En **Build settings**:

   | Campo | Valor |
   |---|---|
   | Framework preset | `None` |
   | Build command | `pip install -r requirements.txt && python build.py && python check_size.py` |
   | Build output directory | `dist` |

   La versión de Python la fija el archivo `.python-version` (3.13), así que no
   hace falta añadir variables de entorno.
3. Pulsa **Save and Deploy**. La web quedará en `https://<proyecto>.pages.dev` (la actual es <https://iatalks.pages.dev>).
4. Cuando sepas la URL definitiva, cámbiala en `SITE_URL`, arriba del todo de
   `build.py`. Se usa en el sitemap, el RSS y las etiquetas Open Graph.

Las ramas que no sean `main` generan una URL de preview propia, útil para
revisar una charla antes de publicarla.

## Licencias

- **Contenido** (charlas, textos, diapositivas): [CC BY 4.0](LICENSE-CONTENT).
  Puedes reutilizarlo citando la autoría.
- **Código** (`build.py`, plantillas, CSS): [MIT](LICENSE).
