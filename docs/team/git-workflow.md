# Flujo de trabajo con Git

Ramas:
```text
main
develop
feature/*
fix/*
refactor/*
docs/*
```

Ejemplos:
```text
feature/inventory
feature/forecasting
feature/purchasing
feature/surplus
feature/dashboard
feature/automation-engine
```

Flujo:
```text
feature/*
↓
Pull Request
↓
develop
↓
testing
↓
main
```

Convención de commits:
```text
feat:
fix:
refactor:
docs:
test:
chore:
```

Ejemplos:
```text
feat(inventory): add stock movement endpoint
feat(planning): generate ingredient requirements
fix(purchasing): prevent duplicate orders
test(automation): add retry policy tests
```

Cada Pull Request debe incluir:
- descripción;
- módulo afectado;
- cambios;
- cómo probar;
- dependencias;
- capturas si aplica.

Antes de merge:
- tests passing;
- lint passing;
- review aprobado;
- sin conflictos.
