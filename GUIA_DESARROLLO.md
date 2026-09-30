# Guía de desarrollo — Raíz y coordinación del repositorio

**Carpeta:** `.`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](AGENTS.md).
- [Reparto vigente y criterios de entrega](docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](docs/equipo/dependencias.md).
- [Alcance de la demo](docs/guia-inicio-desarrollo.md).
- [docs/base-para-desarrollo.md](docs/base-para-desarrollo.md).

## Punto de partida

**30-09-2026 · Paso 5: Telegram se configura desde Proveedores → Configuración Telegram por Administrador. Token cifrado en volumen telegram_secrets; JWT_SECRET estable (mínimo 32 caracteres). API escribe y worker lee. TELEGRAM_BOT_TOKEN de entorno es fallback opcional. Conservar secreto de instalación/volumen en respaldo privado; rotar JWT_SECRET requiere guardar token de nuevo. Sin aprobación/envío de pedidos en este corte.**

Archivos técnicos observados al preparar esta guía: `.env.example`, `.gitignore`, `compose.yaml`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](docs/equipo/avances/cueva.md) para el último estado.

Axel coordina la raíz; los seis responden por su propio bloque. La revisión documental no declara implementados los módulos.

**A03:** `compose.yaml` aplica Alembic mediante el servicio de una sola ejecución `migraciones` antes de iniciar API, worker y Beat. Beat es único en esta instalación local; revisa ejecuciones cada 30 segundos. Mantener PostgreSQL y Redis saludables antes de las pruebas del motor. Los adaptadores de negocio aún no están registrados.

**A04:** la imagen backend instala el extra `ml` de ejecución y prepara `/code/model_artifacts`; Compose monta allí un volumen persistente con lectura en API y escritura en worker. El bot usa `TELEGRAM_BOT_TOKEN` opcional; el destino se vinculará en el módulo de Aguirre. CI revisa migración en cabeza, volumen compartido, cola y motor. El modelo y el canal no se declaran integrados hasta recibir las entregas y pruebas de sus dueños.

`iniciar-foodsave.cmd` delega en `iniciar-foodsave.ps1`: evita dos arranques simultáneos del lanzador por instalación, comprueba Docker y espera hasta 120 segundos por API/web antes de abrir `/inicializacion/piloto`. Conserva los volúmenes y muestra el error real de Compose. Usa imágenes ya construidas; tras cambios de código, ejecutar `iniciar-foodsave.cmd -Build` una vez. `-NoBrowser` permite comprobar el arranque sin abrir una pestaña. El primer build sigue requiriendo Docker y descarga de dependencias. El asistente completo está en `/inicializacion`. No ejecutar otro `docker compose up` en paralelo; ante conflicto de nombres, esperar al arranque en curso y volver a intentar, sin borrar volúmenes.

## Trabajo en esta carpeta

1. Mantener README como entrada al alcance y reparto vigente; enlazar el mapa de carpetas.
2. Integrar manifiestos, Compose y variables de entorno con los requisitos aportados por cada bloque.
3. Mantener una revisión por cambio y evidencia de integración por cada frontera.
4. Preservar datos históricos, cambios locales y secretos fuera de Git.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

README, reparto, diccionario y guías atribuyen el mismo dueño; un compañero puede ubicar su tarea y reproducir el núcleo.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](docs/equipo/avances/cueva.md) siguiendo [la plantilla](docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
