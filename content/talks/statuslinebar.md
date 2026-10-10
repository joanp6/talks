---
title: "La status line de Claude Code: tu panel de control en la terminal"
event: "AI Lightning Talks with Claude · Quantiqus Meetup"
eventUrl: "https://www.meetup.com/es-es/quantiqus-meetup-group/events/316867953/"
date: 2026-10-15
city: "Sant Cugat del Vallès"
language: es
tags: ["Claude Code", "IA", "productividad", "terminal"]
summary: "Cómo convertir la barra inferior de Claude Code en un panel con contexto, límites de uso, coste y rama de git, con un script de pocas líneas que recibe JSON por stdin."

# slidesEmbed: "https://iatalks.pages.dev/slides/statuslinebar"
resources:
  - label: "Documentación oficial: Customize your status line"
    url: "https://code.claude.com/docs/en/statusline"
  - label: "ccstatusline (proyecto de la comunidad)"
    url: "https://github.com/sirmalloc/ccstatusline"

draft: false
---

## De qué va

Claude Code tiene una barra en la parte inferior de la terminal que puedes
programar tú. Le pasa a un script tuyo un JSON con el estado de la sesión
(modelo, contexto usado, coste, límites de uso…) y muestra lo que el script
imprima. En la charla construyo una paso a paso, desde un `echo` hasta la
que uso a diario en VS Code.

## Cómo funciona

1. En `~/.claude/settings.json` añades un bloque `statusLine` con el comando
   que quieres ejecutar.
2. Claude Code ejecuta ese comando y le envía el JSON por **stdin**.
3. Lo que el script escribe en **stdout** aparece en la barra. Admite varias
   líneas y colores ANSI.

Se actualiza cuando llega un mensaje nuevo, al cambiar de modo y, si quieres,
cada N segundos con `refreshInterval`. Se ejecuta en local y no consume tokens.

## Qué se puede mostrar

- Modelo y nivel de esfuerzo.
- Porcentaje de la ventana de contexto usado.
- Límites de uso de 5 horas y 7 días, con el tiempo hasta que se reinician.
- Coste estimado y duración de la sesión.
- Carpeta y rama de git.

## Trucos y errores típicos

- Prueba el script con un JSON de ejemplo antes de configurarlo.
- Algunos campos llegan vacíos al principio de la sesión: usa valores por
  defecto.
- En Windows, escribe las rutas del comando con `/` y no con `\`.
- Si el script falla o tarda, la barra se queda en blanco: mantenlo rápido.
