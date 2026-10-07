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

Archivos técnicos observados al preparar esta guía: `.env.example`, `.gitignore`, `compose.yaml`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](docs/equipo/avances/cueva.md) para el último estado.

Axel coordina la raíz; los seis responden por su propio bloque. La revisión documental no declara implementados los módulos.

**A03:** `compose.yaml` aplica Alembic mediante el servicio de una sola ejecución `migraciones` antes de iniciar API, worker y Beat. Beat es único en esta instalación local; revisa ejecuciones cada 30 segundos. Mantener PostgreSQL y Redis saludables antes de las pruebas del motor. Están registrados preparación, backtest y evaluación de pronóstico; plan y evaluación programados disponibles; compras y promoción siguen pendientes.

**A04:** la imagen backend instala el extra `ml` de ejecución y prepara `/code/model_artifacts`; Compose monta allí un volumen persistente con lectura en API y escritura en worker. El bot usa `TELEGRAM_BOT_TOKEN` opcional; el destino se vinculará en el módulo de Aguirre. CI revisa migración en cabeza, volumen compartido, cola y motor. El modelo y el canal no se declaran integrados hasta recibir las entregas y pruebas de sus dueños.

`iniciar-foodsave.cmd` arranca Compose con las imágenes ya construidas y abre `/inicializacion/piloto` al terminar el arranque; conserva los volúmenes y necesita `.env` configurado una vez. El primer build sigue requiriendo Docker y descarga de dependencias. El asistente completo está en `/inicializacion`.

**E03/K01:** primera carga completa conectada al modelo automático, progreso durable y reintento sin reimportar; revisión `0008_e03_modelo` al final de la cadena. Cinco CSV sintéticos y pruebas PostgreSQL/Redis de carga, entrenamiento, evaluación y recuperación. Ver [evidencia](docs/equipo/avances/cueva.md).

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

**M02–M04:** plan, faltantes y pantalla conectados; `GENERAR_PROPUESTA` hace inferencia real y reserva evaluación. Migración `0009_m02_planes`. No genera pedidos aún; política de recompra pendiente. Ver avance de coordinación y Rojas.
