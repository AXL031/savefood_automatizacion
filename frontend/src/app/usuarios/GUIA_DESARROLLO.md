# Guía de desarrollo — Gestión de usuarios

Responsable: Axel Cueva, ampliación A01 autorizada por el usuario. Leer [guía padre](../GUIA_DESARROLLO.md), [alcance](../../../../docs/guia-inicio-desarrollo.md), [responsabilidades](../../../../docs/equipo/responsabilidades.md) y [contrato](../../../../docs/api/contratos.md).

Página administrativa `/usuarios`: listado, creación, edición de nombre/correo/rol y activación. Usa servicios HTTP y componentes compartidos. Operadores ven acceso restringido; el backend también exige administrador. El último administrador activo no puede desactivarse ni degradarse. No hay eliminación física ni registro público.

Registrar cambios y pruebas reales en [avance de Axel](../../../../docs/equipo/avances/cueva.md). No mostrar ni conservar contraseñas en respuestas o tablas.
