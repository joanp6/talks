---

title: "Cómo trabajo con MCP en QA"
event: "Sesión interna de formación"
date: 2026-05-25
language: es
tags: ["MCP", "IA", "QA"]
summary: "Diez minutos sobre cómo conectar un asistente de IA a Jira, Confluence y Figma con MCP, y qué cambia en el día a día de QA cuando el modelo tiene contexto real."

resources:
  - label: "Presentación a pantalla completa"
    url: "https://iatalks.pages.dev/slides/mcp-en-qa"
  - label: "Model Context Protocol: documentación oficial"
    url: "https://modelcontextprotocol.io"

draft: false
---

## El problema: una IA sin contexto

Un asistente de IA genérico no sabe nada de tu proyecto. Si le preguntas
cómo funciona una regla de negocio concreta, lo único que puede hacer es
pedirte más información. Así acabas copiando y pegando tickets, buscando
páginas de documentación a mano y perdiendo tiempo en tareas que no añaden
valor.

En la charla lo mostré con una "anti-demo": la misma pregunta, al mismo
modelo, primero sin contexto y después con acceso a la documentación a
través de MCP. La diferencia entre "necesito más detalles" y una respuesta
concreta con su fuente es todo el argumento.

## Qué es MCP

**Model Context Protocol** es un estándar abierto para conectar modelos de
IA con herramientas y datos. La analogía que usé: es el **USB-C de los
modelos**, un único conector para enchufar cualquier herramienta.

Tiene tres piezas:

- **Host**: la aplicación donde trabajas (por ejemplo, VS Code).
- **Cliente MCP**: vive dentro del host y habla el protocolo.
- **Servidor MCP**: lo publica cada herramienta (Atlassian, Figma…).

Cada servidor expone **tools** (acciones), **resources** (datos) y
**prompts** (plantillas).

## Lo que se puede y lo que no

El alcance real importa más que la teoría. Con los servidores MCP de
Atlassian y Figma:

- **Jira**: lectura completa (issues, JQL, metadatos) y escritura habitual
  (crear y editar issues, comentar, cambiar estado). No cubre la gestión de
  tests de Xray, los adjuntos ni la administración.
- **Confluence**: leer y buscar páginas, crear y actualizar páginas y
  comentarios. Sin adjuntos ni gestión de permisos.
- **Figma**: leer componentes, capturas, variables y tableros de FigJam.
  No edita diseños existentes.

La autenticación es OAuth: el modelo solo ve lo que tu cuenta ya puede ver.

## Conclusión

MCP no hace al modelo más listo: le da el contexto que le faltaba. Para QA
eso significa menos tiempo buscando información y más tiempo probando.
