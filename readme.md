# Employee Management System - Refactorización y Mejora

## 🏢 Proyecto para Acme Workforce Solutions

Este proyecto tiene como objetivo refactorizar y mejorar un sistema de gestión de empleados desarrollado en Python para la empresa ficticia **Acme Workforce Solutions**, una organización que ofrece soluciones tecnológicas para la administración de talento humano en pequeñas y medianas empresas.

El sistema original fue concebido como un prototipo funcional y, aunque actualmente permite operaciones básicas como registrar empleados, otorgar vacaciones y calcular pagos, su diseño rígido y acoplado impide su evolución hacia nuevas políticas y requerimientos.

---

## 🎯 Objetivo del proyecto

Refactorizar el sistema actual para que sea más **robusto, escalable y mantenible**, aplicando buenas prácticas de **ingeniería de software**, principios **SOLID**, y al menos tres **patrones de diseño**. Esto permitirá que el sistema evolucione con facilidad ante nuevas reglas y necesidades del negocio.

---

## 🔍 Funcionalidades actuales del sistema

- Registro de empleados por nombre, tipo (asalariado o por hora) y rol (interno, gerente o vicepresidente).
- Visualización de empleados por tipo de rol.
- Gestión de vacaciones, con opción de tomarlas o recibir un **payout** equivalente a 5 días.
- Cálculo de pago mensual o por horas trabajadas.

---

## 🛠️ Funcionalidades a implementar

Estas funcionalidades han sido diseñadas para forzar una mejora estructural del sistema y asegurar que esté preparado para cambios futuros:

### 1. Bonificación por desempeño
- Asalariados reciben un 10% adicional sobre su salario.
- Empleados por hora reciben $100 extra si trabajan más de 160 horas.
- Internos no reciben bonificación.
- La lógica debe integrarse al cálculo de pago sin modificar la UI.

### 2. Políticas de vacaciones por rol
- Interns: no pueden tomar vacaciones ni recibir payout.
- Managers: pueden solicitar hasta 10 días como payout.
- Vice Presidents: vacaciones ilimitadas, máximo 5 días por solicitud.
- La lógica debe ser extensible por tipo de rol.

### 3. Tipo de empleado: Freelancer
- Se permite registrar freelancers que trabajan por proyecto.
- Cada freelancer puede registrar uno o más proyectos con monto asociado.
- El pago se calcula como la suma total de los proyectos entregados.

### 4. Historial de transacciones
- Se debe registrar cada pago y solicitud de vacaciones por empleado.
- El historial debe incluir fecha, tipo de operación y monto.
- Accesible desde la vista de detalle del empleado.

### 5. Configuración dinámica de políticas de pago
- Las reglas de pago (como porcentaje de bonificación o umbral de horas) deben cargarse desde una fuente externa (JSON, DB, etc.).

---

## 📦 Entregables esperados

- Informe de análisis de problemas del sistema legacy.
- Documento técnico con propuesta de arquitectura y patrones aplicados.
- Código fuente refactorizado con las nuevas funcionalidades.

---

## ✅ Criterios de aceptación

- Cumplimiento con los principios SOLID.
- Aplicación de al menos tres patrones de diseño.
- Implementación modular, escalable y extensible de las nuevas funcionalidades.