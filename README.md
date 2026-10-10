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
| `public/` | Archivos que se copian sin cambios: `style.css`, `favicon.svg`, `slides/*.pdf`. |
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
