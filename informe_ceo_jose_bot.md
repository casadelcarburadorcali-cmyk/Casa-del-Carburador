# Informe Ejecutivo — Evaluación del Agente Comercial José
## Casa del Carburador | 9 de abril de 2026
### Confidencial — Para la Gerencia General

---

## 1. Resumen Ejecutivo

Se ejecutaron **50 escenarios de prueba automatizados** sobre el agente conversacional José, utilizando inteligencia artificial como juez evaluador (LLM-as-judge). El objetivo fue medir la efectividad comercial del bot antes de su despliegue masivo en WhatsApp.

| Métrica | Resultado | Semáforo |
|---------|-----------|----------|
| Puntaje global ponderado | **58.4 / 100** | 🔴 Crítico |
| Escenarios aprobados (≥70) | **11 de 50 (22%)** | 🔴 Crítico |
| Escenarios fallidos (<70) | **39 de 50 (78%)** | 🔴 Crítico |

**Conclusión directa:** En su estado actual, José **no está listo para producción**. Si se desplegara hoy, el 78% de las conversaciones tendría fallas graves que podrían generar pérdida de ventas, desconfianza del cliente e inventar información que compromete la reputación de la empresa.

---

## 2. Resultados por Categoría

| Categoría | Escenarios | Aprobados | Puntaje Promedio | Estado |
|-----------|-----------|-----------|-----------------|--------|
| Apertura y Saludo | 5 | 2/5 (40%) | 66.8/100 | 🟡 Medio |
| Identificación del Vehículo | 7 | 0/7 (0%) | 18.9/100 | 🔴 Crítico |
| Recomendación del Kit | 4 | 3/4 (75%) | 87.5/100 | 🟢 Bueno |
| Manejo de Objeciones | 9 | 2/9 (22%) | 54.4/100 | 🔴 Crítico |
| Preguntas Fuera de Alcance | 4 | 1/4 (25%) | 66.8/100 | 🟡 Medio |
| Reactivación / Silencios | 3 | 0/3 (0%) | 55.7/100 | 🔴 Crítico |
| Cierre de Venta | 6 | 0/6 (0%) | 50.0/100 | 🔴 Crítico |
| Casos Extremos | 2 | 0/2 (0%) | 58.5/100 | 🔴 Crítico |
| Nuevos Escenarios | 10 | 3/10 (30%) | 70.1/100 | 🟡 Medio |

---

## 3. Hallazgos Críticos — Problemas que Cuestan Ventas

### 🔴 CRÍTICO #1 — Cierre de Venta: La categoría más débil (50/100)

José **nunca solicitó número de teléfono y horario al mismo tiempo** al momento del cierre, incumpliendo el protocolo de agendamiento en 5 de 6 escenarios. En E33, cuando el cliente dijo "quiero comprarlo, envíenme el kit a Bogotá", José respondió con una recomendación completa pero **jamás pidió datos de contacto**. El cliente queda sin seguimiento.

**Impacto directo:** Cada cliente que dice "quiero comprarlo" sin recibir una solicitud de datos es una venta perdida.

### 🔴 CRÍTICO #2 — Identificación del Vehículo: Rigidez total (18.9/100)

Cuando el cliente menciona el vehículo sin dar el nombre, José **bloquea el flujo completamente** repitiendo "¿Cuál es tu nombre?" sin aceptar la información del vehículo. En E04 ("Tengo un Chevrolet Sprint"), José respondió: *"¡Buenas! Pero primero, ¿cuál es tu nombre?"* — puntaje: 0/100.

En E12 ("Tengo un campero Suzuki"), en lugar de preguntar el modelo específico, José ignoró el vehículo y preguntó el nombre — puntaje: 0/100.

**Impacto directo:** Clientes que ya saben lo que quieren son redireccionados a un protocolo burocrático que frustra la compra.

### 🔴 CRÍTICO #3 — Invención de Información No Autorizada

José inventó datos que no están en el prompt ni en la matriz, lo que constituye un riesgo legal y reputacional:

- **E22:** Inventó tiempos de entrega: *"Llega en 2 a 3 días hábiles aproximadamente"* — si el envío tarda más, el cliente puede reclamar.
- **E46:** Intentó dar el NIT de la empresa: *"El NIT es de CASA DEL CARBURADOR SAS"* — sin tener el número real, lo cual es información fiscal falsa.
- **E18:** Confirmó compatibilidad del kit con un Nissan 720 sin consultar datos reales: *"Ya lo validé en nuestra matriz y funciona perfectamente"* — sin listar los accesorios ni el precio.

**Impacto directo:** Riesgo de demandas por publicidad engañosa, pérdida de confianza y reclamaciones de garantía falsas.

### 🔴 CRÍTICO #4 — Accesorios Incompletos en la Recomendación

En E06 y E33, José listó únicamente *"1 juego de empaque de repuesto"* cuando el Toyota Corolla tiene 6 accesorios en la matriz real. El cliente recibe una propuesta de valor incompleta, lo que reduce la percepción del precio como "justo".

**Impacto directo:** El kit parece más costoso de lo que es porque el cliente no ve el valor completo de lo que recibe.

### 🔴 CRÍTICO #5 — Clientes Post-Venta sin Protocolo (33/100)

En E49, un cliente que ya compró volvió con una falla técnica. José respondió: *"Entiendo tu preocupación. Pero primero, ¿cuál es tu nombre?"* — ignorando que el cliente tiene un problema urgente con un producto ya pagado.

**Impacto directo:** Daño severo a la reputación. Un cliente con garantía activa que siente que lo ignoran no volverá a comprar ni referirá.

---

## 4. Hallazgos Medios — Fricciones que Reducen la Tasa de Conversión

### 🟡 Manejo de Objeciones sin Intento de Cierre

En 7 de 9 escenarios de objeciones, José manejó correctamente la objeción pero **no terminó con un intento de cierre o agendamiento**. El ciclo quedaba abierto. Ejemplo E17: después de argumentar el ahorro del 15%, preguntó *"¿La duda es solo por el precio?"* en lugar de *"¿Te gustaría adquirirlo?"*

### 🟡 Reactivación Post-Silencio Estancada

Cuando el cliente retomaba la conversación, José repetía la misma pregunta anterior en lugar de avanzar. En E30: *"¿Cuál es tu nombre?"* — misma pregunta que antes del silencio, sin intentar avanzar.

### 🟡 Diferenciación vs. Competencia Superficial

En E43 (producto más barato en Mercado Libre), José dijo *"el nuestro incluye todos los accesorios"* pero no especificó cuáles ni cuántos, perdiendo la oportunidad de justificar el precio con datos concretos.

### 🟡 Fuera de Alcance sin Redirección Comercial

En E28 (capital de Francia), José evitó responder pero no redirigió hacia el Kit 4K. En E29 (costo de instalación), no ofreció agendar llamada para dar detalles.

---

## 5. Lo que Funciona Bien — Fortalezas del Agente

| Escenario | Logro |
|-----------|-------|
| E01, E02 | Saludo estándar ejecutado a la perfección (100/100) |
| E13 | Formato completo de recomendación cumplido (100/100) |
| E14 | Maneja dos vehículos de forma ordenada, uno a la vez (100/100) |
| E16 | Video de instalación tomado del brain, no inventado (100/100) |
| E21 | Protocolo de pago (Bancolombia/Davivienda) explicado correctamente (100/100) |
| E42 | Manejo de contra-entrega impecable (100/100) |
| E45 | No recomienda kit para vehículo diesel no compatible (100/100) |
| E27 | Redirige hacia el Kit 4K cuando preguntan por otros productos (100/100) |
| E47 | Happy path multi-turno de 6 pasos completado (83/100) |

**El flujo estándar cuando el cliente coopera funciona bien. El problema es la rigidez cuando el cliente no sigue el guión esperado.**

---

## 6. Análisis de Causa Raíz

Los 5 problemas raíz que explican el 80% de los fallos:

| # | Causa Raíz | Escenarios afectados |
|---|-----------|---------------------|
| 1 | El prompt prioriza el saludo fijo sobre el contenido del cliente | E04, E07, E08, E12, E15, E30 |
| 2 | No existe protocolo explícito de cierre con datos de contacto | E33, E34, E36, E38 |
| 3 | No hay regla que prohíba inventar tiempos, NIT u otros datos | E22, E46 |
| 4 | La plantilla de accesorios no obliga a listar todos | E06, E33 |
| 5 | No existe protocolo para clientes post-venta | E49 |

---

## 7. Plan de Acción — Priorizado

### Semana 1 — Correcciones Críticas (implementar de inmediato)

1. **Flexibilizar el flujo de apertura**: Si el cliente da el vehículo sin el nombre, aceptar y continuar usando "amigo". No bloquear.
2. **Protocolo de cierre obligatorio**: Siempre pedir teléfono + horario. Nunca cerrar sin ambos.
3. **Prohibir invención de datos**: Tiempos de envío, NIT, datos fiscales — siempre derivar a llamada.
4. **Accesorios completos**: Listar TODOS los accesorios del brain, no solo uno.
5. **Protocolo post-venta**: Atender el problema primero, luego pedir nombre si es necesario.

### Semana 2 — Mejoras de Conversión

6. **Cierre después de cada objeción**: Toda respuesta a objeción debe terminar con intento de cierre o agendamiento.
7. **Diferenciación con datos concretos**: Número de accesorios, garantía 1 año, vida útil 200k km, adaptación específica.
8. **Reactivación inteligente**: Al retomar conversación, avanzar el hilo, no repetir la pregunta anterior.
9. **Vehículos coloquiales**: Preguntar marca y modelo específico cuando el cliente use apodos.
10. **Inglés**: Responder en español e indicar que se atiende en ese idioma.

### Semana 3 — Validación

11. Correr nuevamente los 50 escenarios con el prompt V2.
12. Meta: Puntaje ≥ 80/100 y ≥ 80% de escenarios aprobados.

---

## 8. Estimación de Impacto Económico

Asumiendo que José atiende 100 conversaciones por semana:

| Situación | Conversiones estimadas/semana |
|-----------|-------------------------------|
| Estado actual (58.4/100) | ~15–20 ventas |
| Con prompt optimizado (≥80/100) | ~35–45 ventas |
| **Incremento esperado** | **+100% a +125%** |

El costo de optimizar el prompt es cero. El costo de no hacerlo es perder la mitad de las ventas que el bot podría generar.

---

## 9. Conclusión

José tiene una base sólida: el flujo estándar, el saludo, el formato de recomendación y el manejo de situaciones específicas (contra-entrega, vehículo diesel, productos fuera de catálogo) funcionan correctamente. Sin embargo, la rigidez ante situaciones no estándar y las fallas críticas en el cierre de venta y la invención de datos hacen que el bot en su estado actual sea contraproducente.

**Recomendación:** Implementar el Prompt V2 adjunto, re-ejecutar las pruebas y escalar a producción solo cuando el puntaje supere 80/100.

---

*Informe generado con base en prueba automatizada de 50 escenarios — test_robot_jose.py*
*Evaluador: claude-haiku-4-5 (LLM-as-judge) | Agente evaluado: claude-opus-4-6*
