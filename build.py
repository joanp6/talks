"""Genera la web estática de charlas en la carpeta dist/.

Uso:
    python build.py

Pasos:
    1. Lee cada .md de content/talks/ y valida su frontmatter (clase Talk).
    2. Descarta los drafts y ordena las charlas por fecha (más reciente primero).
    3. Renderiza las plantillas de templates/ y las escribe en dist/.
    4. Copia public/ (CSS, favicon, PDFs) tal cual a dist/.
"""

import datetime
import re
import shutil
import sys
from dataclasses import dataclass
from email.utils import format_datetime
from pathlib import Path
from typing import Literal

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, ValidationError

# --- Configuración del sitio -------------------------------------------------
# Cambia SITE_URL cuando tengas el dominio definitivo (sin "/" al final).
# Se usa en el sitemap, el RSS y las URLs canónicas / Open Graph.
SITE_URL = "https://iatalks.pages.dev"
SITE_TITLE = "Charlas de Joan Pérez"
SITE_DESCRIPTION = "Charlas que he dado en eventos: temas, diapositivas y recursos."
AUTHOR = "Joan Pérez"

ROOT = Path(__file__).parent
TALKS_DIR = ROOT / "content" / "talks"
TEMPLATES_DIR = ROOT / "templates"
PUBLIC_DIR = ROOT / "public"
DIST_DIR = ROOT / "dist"

LANGUAGES = {"es": "Español", "ca": "Català", "en": "English", "it": "Italiano"}
MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
          "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


# --- Esquema del frontmatter -------------------------------------------------
class Resource(BaseModel):
    label: str
    url: HttpUrl


class Talk(BaseModel):
    """Campos permitidos en la cabecera (---) de cada charla."""

    # extra="forbid": un campo mal escrito (p. ej. "titel") da error en vez
    # de ignorarse en silencio.
    model_config = ConfigDict(extra="forbid")

    title: str
    event: str
    eventUrl: HttpUrl | None = None
    date: datetime.date
    city: str | None = None
    language: Literal["es", "ca", "en", "it"]
    tags: list[str]
    summary: str = Field(max_length=200)
    slidesPdf: str | None = Field(default=None, pattern=r"^/slides/[a-z0-9-]+\.pdf$")
    slidesEmbed: HttpUrl | None = None
    video: HttpUrl | None = None
    resources: list[Resource] = []
    draft: bool = False


@dataclass
class TalkPage:
    slug: str          # nombre del archivo sin .md -> /charlas/<slug>/
    data: Talk         # frontmatter ya validado
    body_html: str     # cuerpo Markdown convertido a HTML


# --- Lectura de charlas ------------------------------------------------------
def read_talk(path: Path) -> TalkPage:
    """Lee un .md, separa frontmatter y cuerpo, y valida el frontmatter."""
    slug = path.stem
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        raise ValueError("el nombre del archivo solo puede tener minúsculas, números y guiones")

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("el archivo debe empezar con '---' (frontmatter)")
    # "---\n<frontmatter>\n---\n<cuerpo>" -> ["", frontmatter, cuerpo]
    _, frontmatter, body = text.split("---", 2)

    data = Talk.model_validate(yaml.safe_load(frontmatter))

    if data.slidesPdf and not data.draft:
        pdf = PUBLIC_DIR / data.slidesPdf.lstrip("/")
        if not pdf.is_file():
            raise ValueError(f"slidesPdf apunta a {data.slidesPdf}, pero no existe public{data.slidesPdf}")

    body_html = markdown.markdown(body, extensions=["extra"])
    return TalkPage(slug=slug, data=data, body_html=body_html)


def load_published_talks() -> list[TalkPage]:
    """Devuelve las charlas no-draft, de la más reciente a la más antigua.

    Si algún archivo tiene errores, los muestra todos y termina el build.
    """
    talks, errors = [], []
    for path in sorted(TALKS_DIR.glob("*.md")):
        try:
            talks.append(read_talk(path))
        except (ValueError, ValidationError, yaml.YAMLError) as error:
            errors.append(f"ERROR en {path.relative_to(ROOT)}:\n{error}\n")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(f"Build cancelado: {len(errors)} charla(s) con errores.")

    published = [talk for talk in talks if not talk.data.draft]
    published.sort(key=lambda talk: talk.data.date, reverse=True)
    return published


# --- Filtros para las plantillas ---------------------------------------------
def fecha(value: datetime.date) -> str:
    """2026-03-12 -> '12 de marzo de 2026'."""
    return f"{value.day} de {MONTHS[value.month - 1]} de {value.year}"


def rfc822(value: datetime.date) -> str:
    """Formato de fecha que exige RSS: 'Thu, 12 Mar 2026 00:00:00 +0000'."""
    moment = datetime.datetime.combine(value, datetime.time(), tzinfo=datetime.timezone.utc)
    return format_datetime(moment)


# --- Escritura de la web -----------------------------------------------------
def write(relative_path: str, content: str) -> None:
    target = DIST_DIR / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build() -> None:
    talks = load_published_talks()

    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["fecha"] = fecha
    env.filters["rfc822"] = rfc822
    env.globals["site"] = {
        "url": SITE_URL,
        "title": SITE_TITLE,
        "description": SITE_DESCRIPTION,
        "author": AUTHOR,
        "year": datetime.date.today().year,
    }
    env.globals["languages"] = LANGUAGES

    # Empezamos de cero y copiamos los archivos estáticos.
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    shutil.copytree(PUBLIC_DIR, DIST_DIR, ignore=shutil.ignore_patterns(".gitkeep"))

    # Cada página va en <ruta>/index.html para que la URL quede sin ".html".
    write("index.html", env.get_template("index.html").render(talks=talks, path="/"))
    write("about/index.html", env.get_template("about.html").render(path="/about/"))
    for talk in talks:
        path = f"/charlas/{talk.slug}/"
        write(f"charlas/{talk.slug}/index.html",
              env.get_template("talk.html").render(talk=talk, path=path))

    pages = ["/", "/about/"] + [f"/charlas/{talk.slug}/" for talk in talks]
    write("sitemap.xml", env.get_template("sitemap.xml").render(pages=pages))
    write("rss.xml", env.get_template("rss.xml").render(talks=talks))

    print(f"OK: web generada en dist/ con {len(talks)} charla(s) publicada(s).")


if __name__ == "__main__":
    build()
