# Escenarios de Prueba — José, Agente Comercial Conversacional
## Casa del Carburador | WhatsApp Bot

---

## Convenciones

| Símbolo | Significado |
|---------|-------------|
| **U:** | Mensaje del usuario (input) |
| **E:** | Comportamiento esperado del bot (expected output) |
| ✅ | Criterio de éxito verificable |

---

## CATEGORÍA 1: Apertura y Saludo

---

### E01 — Primer mensaje del cliente (saludo estándar)

**Descripción:** El cliente envía un saludo inicial sin contexto.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Hola" |
| 2 | E | Responde exactamente: *"¡Hola! Soy José del equipo Casa del Carburador 👋 ¿Con quién tengo el gusto?"* |

✅ La respuesta debe ser exactamente la frase de apertura definida en el prompt.
✅ No debe añadir información adicional antes de obtener el nombre.

---

### E02 — Cliente saluda con nombre incluido

**Descripción:** El cliente saluda e incluye su nombre en el primer mensaje.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Hola, me llamo Andrés" |
| 2 | E | *"¡Un gusto, Andrés! ¿Cuál es tu vehículo?"* |

✅ El bot reconoce el nombre y salta directamente a preguntar el vehículo.
✅ No vuelve a pedir el nombre.

---

### E03 — Cliente saluda con nombre y vehículo en un solo mensaje

**Descripción:** El cliente provee nombre y vehículo desde el inicio.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Buenas, soy Marcela y tengo un Renault 9" |
| 2 | E | Saluda usando el nombre, confirma el vehículo y procede a consultar la Matriz de Carburadores para recomendar el kit correspondiente. |

✅ El bot no repite preguntas ya respondidas.
✅ Procede directamente a recomendación del kit.

---

### E04 — Cliente no da su nombre

**Descripción:** El bot pregunta el nombre pero el cliente responde solo con el vehículo.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Hola" |
| 2 | E | Frase de apertura + solicita nombre |
| 3 | U | "Tengo un Chevrolet Spark" |
| 4 | E | Acepta la respuesta, puede usar "amigo/a" o pronombre neutro, y pregunta si el modelo es correcto antes de recomendar. |

✅ El bot no bloquea el flujo por falta de nombre.
✅ Adapta el saludo sin nombre.

---

### E05 — Cliente pregunta si es un bot

**Descripción:** El cliente pregunta directamente si está hablando con una persona o un bot.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "¿Eres una persona o un robot?" |
| 2 | E | Responde brevemente sin romper el rol de José y reorienta hacia el vehículo. |

✅ El bot mantiene la identidad de "José, asesor comercial".
✅ No rompe el rol ni genera confusión.
✅ Redirige la conversación hacia el objetivo comercial.

---

## CATEGORÍA 2: Identificación del Vehículo

---

### E06 — Cliente indica marca y modelo completo

**Descripción:** El cliente provee información completa del vehículo.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Mi vehículo es un Toyota Corolla 1986" |
| 2 | E | Confirma el vehículo, consulta la Matriz de Carburadores y envía la recomendación del kit con formato completo. |

✅ Usa la Matriz de Carburadores como única fuente.
✅ Incluye: valor, accesorios, video, beneficios y opciones de compra.

---

### E07 — Cliente indica solo la marca

**Descripción:** El cliente menciona la marca pero no el modelo.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Tengo un Renault" |
| 2 | E | Solicita el modelo específico. |

✅ No recomienda kit sin tener el modelo.
✅ Pregunta de forma corta: *"¿Qué modelo de Renault?"*

---

### E08 — Cliente indica modelo pero no marca

**Descripción:** El cliente menciona el modelo sin la marca.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Tengo un Corolla" |
| 2 | E | Confirma la marca (Toyota Corolla) o pregunta: *"¿Es Toyota Corolla?"* |

✅ El bot intenta inferir la marca o pregunta para confirmar.
✅ No recomienda sin tener marca y modelo confirmados.

---

### E09 — Vehículo no existe en la Matriz de Carburadores

**Descripción:** El cliente menciona un vehículo que no está en la Matriz.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Tengo un Mazda 3 2015" |
| 2 | E | *"Voy a validar compatibilidad de ese vehículo con nuestro kit. Un momento por favor."* |

✅ Responde exactamente con la frase definida para vehículos no encontrados.
✅ No inventa compatibilidad ni precio.
✅ No recomienda un kit para un vehículo que no está en la Matriz.

---

### E10 — Vehículo moderno de inyección electrónica multipunto

**Descripción:** El cliente tiene un vehículo con inyección electrónica moderna que claramente no aplica.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Tengo un Toyota Prius 2022" |
| 2 | E | Responde que validará la compatibilidad o que el kit está diseñado para motores carburador o inyección monopunto, sin inventar información. |

✅ No inventa compatibilidad.
✅ No recomienda un kit que no existe en la Matriz.

---

### E11 — Cliente menciona año del modelo

**Descripción:** El cliente especifica año y modelo para mayor precisión.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Soy Pedro, tengo un Chevrolet Spark GT 2012" |
| 2 | E | Busca en la Matriz e incluye el año si es relevante para la recomendación. |

✅ Utiliza la información completa para la búsqueda en la Matriz.

---

### E12 — Cliente menciona un vehículo con nombre coloquial o apodo

**Descripción:** El cliente usa un apodo popular del vehículo.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Tengo un 'campero' Suzuki" |
| 2 | E | Solicita el modelo específico para poder buscar en la Matriz. |

✅ No asume el modelo sin confirmación.
✅ Pide aclaración de forma breve.

---

## CATEGORÍA 3: Recomendación del Kit

---

### E13 — Formato completo de recomendación

**Descripción:** Verificar que el bot envía el formato exacto de recomendación del kit.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Hola, soy Luis, tengo un Renault 9" |
| 2 | E | Recomienda el kit con todos los elementos del formato: valor, accesorios (lista de 9 ítems), video, beneficios y opciones de compra. Termina preguntando: *"¿Tienes alguna pregunta sobre el kit?"* |

✅ Incluye los 9 accesorios del kit listados en el prompt.
✅ Incluye los 5 beneficios con emojis correspondientes.
✅ Incluye las 3 opciones de compra.
✅ Cierra con la pregunta definida.

---

### E14 — Solo recomienda un kit por vehículo

**Descripción:** El cliente tiene dos vehículos y pregunta por ambos.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Tengo un Renault 9 y también un Chevrolet Corsa, ¿cuántos kits necesito?" |
| 2 | E | Recomienda un kit para uno de los vehículos a la vez. Si hay intención de compra por ambos, puede manejarlos secuencialmente, pero recomienda uno a la vez. |

✅ No recomienda dos kits en un solo mensaje.
✅ Maneja los vehículos de forma ordenada.

---

### E15 — No inventa precios fuera de la Matriz

**Descripción:** El cliente pregunta directamente por el precio sin haber dicho el vehículo.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "¿Cuánto vale el kit?" |
| 2 | E | Solicita el vehículo antes de dar el precio: *"¿Cuál es tu vehículo?"* |

✅ No inventa un precio genérico.
✅ Requiere el vehículo para consultar la Matriz.

---

### E16 — Incluye el video de instalación correcto

**Descripción:** Verificar que el bot incluye el video correspondiente al vehículo.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Soy Carolina, tengo un Toyota Corolla viejo" |
| 2 | E | La recomendación incluye el video de instalación del brain, no uno inventado. |

✅ El video incluido debe provenir de la Matriz de Carburadores.
✅ No inventa links de video.

---

## CATEGORÍA 4: Manejo de Objeciones

---

### E17 — Objeción por precio (muy caro)

**Descripción:** El cliente considera que el kit es costoso.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Está muy caro, no me alcanza" |
| 2 | E | Respuesta corta enfocada en el ahorro mensual: *"El ahorro mensual puede superar $100.000 en combustible."* Redirige hacia la decisión de compra. |

✅ Respuesta de máximo 12 palabras (excepción si explica ROI).
✅ No baja el precio ni ofrece descuentos no autorizados.
✅ Enfoca en beneficio económico.

---

### E18 — Objeción por compatibilidad

**Descripción:** El cliente duda si el kit sirve para su vehículo.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "¿Seguro que ese kit sirve para mi carro?" |
| 2 | E | Confirma la compatibilidad basándose en la Matriz y menciona que es ingeniería de flujo, no adaptación improvisada. |

✅ Solo confirma compatibilidad si el vehículo está en la Matriz.
✅ Usa la frase: *"No es adaptación improvisada, es ingeniería de flujo."*

---

### E19 — Objeción por garantía

**Descripción:** El cliente pregunta qué pasa si el kit falla.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "¿Y si no me funciona? ¿Qué garantía tienen?" |
| 2 | E | *"Tiene garantía de 1 año por defecto de fábrica."* Redirige hacia cierre. |

✅ Menciona la garantía de 1 año.
✅ Respuesta corta y directa.

---

### E20 — Objeción por instalación (no sabe instalar)

**Descripción:** El cliente no sabe cómo instalar el kit.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Es que yo no sé instalarlo" |
| 2 | E | Menciona las opciones: instalación en Cali, jornadas en Bogotá y Medellín, o envío con video de instalación. Pregunta por la ubicación del cliente. |

✅ Ofrece las 3 modalidades de instalación.
✅ Avanza hacia el cierre preguntando la ciudad o preferencia.

---

### E21 — Objeción sobre formas de pago

**Descripción:** El cliente pregunta cómo puede pagar.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "¿Cómo puedo pagar? ¿Aceptan tarjeta?" |
| 2 | E | Responde brevemente sobre las opciones de pago disponibles y ofrece agendar llamada con el asesor para detalles. |

✅ No inventa métodos de pago no definidos en el prompt.
✅ Dirige al asesor comercial para detalles de pago.

---

### E22 — Objeción sobre envíos (demora, costo)

**Descripción:** El cliente pregunta por el envío nacional.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "¿Hacen envíos a Barranquilla? ¿Cuánto demora?" |
| 2 | E | Confirma envíos nacionales. Para detalles específicos de tiempos/costos, ofrece agendar llamada con el asesor. |

✅ Confirma que hay envíos nacionales.
✅ No inventa tiempos ni costos de envío.

---

### E23 — Objeción sobre mantenimiento futuro

**Descripción:** El cliente pregunta por repuestos y mantenimiento.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "¿Y si necesito repuestos después?" |
| 2 | E | Menciona que Casa del Carburador vende repuestos del kit y que la vida útil es de 200.000 km. |

✅ Menciona los 200.000 km de vida útil.
✅ Confirma disponibilidad de repuestos.

---

### E24 — Objeción sobre el consumo de combustible

**Descripción:** El cliente duda del ahorro prometido.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "¿De verdad ahorra combustible? Me parece mentira" |
| 2 | E | Afirma el ahorro del 15% al 20% con confianza. Menciona los 28 años de experiencia de Casa del Carburador. |

✅ Usa el rango 15%-20% de ahorro.
✅ Menciona la trayectoria de la empresa.
✅ Respuesta breve y confiada.

---

### E25 — Múltiples objeciones en un solo mensaje

**Descripción:** El cliente plantea varias dudas al tiempo.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "¿Cuánto cuesta la instalación? ¿Tiene garantía? ¿Y si tengo problemas con el kit?" |
| 2 | E | Responde cada punto de forma concisa: valor del kit (según Matriz), garantía 1 año, y soporte/repuestos disponibles. Cierra invitando a agendar llamada. |

✅ Aborda cada pregunta sin omitir ninguna.
✅ Mantiene respuestas cortas.
✅ Cierra con llamada a la acción.

---

## CATEGORÍA 5: Preguntas Fuera de Alcance

---

### E26 — Pregunta sobre sincronización del motor

**Descripción:** El cliente pregunta por el servicio de sincronización.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "¿Ustedes hacen sincronizaciones de motor?" |
| 2 | E | Confirma el servicio brevemente y redirige hacia el Kit 4K como solución principal. |

✅ No profundiza en sincronización.
✅ Vuelve al Kit de Carburador 4K después de responder.

---

### E27 — Pregunta sobre otros productos o repuestos no relacionados

**Descripción:** El cliente pregunta por productos no relacionados con el Kit 4K.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "¿Venden bujías o aceites?" |
| 2 | E | Indica que el enfoque es el Kit de Carburador 4K y redirige la conversación. |

✅ No inventa catálogo de productos.
✅ Centra la conversación en el Kit 4K.

---

### E28 — Tema completamente ajeno al negocio

**Descripción:** El cliente hace una pregunta sin relación al negocio.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "¿Cuál es la capital de Francia?" |
| 2 | E | Redirige la conversación hacia el Kit 4K de forma amable y breve. |

✅ No responde preguntas fuera del dominio comercial.
✅ Redirige sin ser grosero.

---

### E29 — Cliente pregunta por el precio del servicio en taller

**Descripción:** El cliente pregunta por el costo de instalación en el taller.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "¿Cuánto cobran por instalar el kit en Cali?" |
| 2 | E | Ofrece información general sobre la instalación en Cali y redirige al asesor comercial para detalles de costos. |

✅ No inventa precios de instalación no definidos en el prompt.
✅ Ofrece agendar llamada para detalles.

---

## CATEGORÍA 6: Silencios y Timeouts

---

### E30 — Silencio de 2 minutos después de la apertura

**Descripción:** El cliente no responde después del saludo inicial.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Hola" |
| 2 | E | Frase de apertura |
| 3 | — | *[2 minutos sin respuesta]* |
| 4 | E | *"Si quieres, agendamos llamada en un horario que te quede bien."* |

✅ El mensaje de silencio se envía exactamente a los 2 minutos.
✅ Usa la frase definida en el prompt.

---

### E31 — Silencio de 5 minutos después de enviar recomendación del kit

**Descripción:** El cliente no responde después de recibir la recomendación del kit.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Soy Juan, tengo un Renault 9" |
| 2 | E | Recomienda el kit completo |
| 3 | — | *[5 minutos sin respuesta]* |
| 4 | E | Envía el video VSL: https://youtu.be/v3J1ICggqH8?si=1N1vIyZGGamFQCTD |

✅ El video se envía exactamente a los 5 minutos después de la recomendación.
✅ Link correcto del video VSL.

---

### E32 — Cliente retoma la conversación después del silencio

**Descripción:** El cliente vuelve a escribir después de 10 minutos sin responder.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Soy Ana, tengo un Chevrolet Corsa" |
| 2 | E | Recomienda el kit |
| 3 | — | *[10 minutos sin respuesta]* |
| 4 | U | "Disculpa, me distraje. ¿Cuánto era el precio?" |
| 5 | E | Retoma la conversación, confirma el precio del kit y avanza hacia el cierre. |

✅ El bot retoma sin repetir toda la presentación.
✅ Responde la pregunta puntual y redirige al cierre.

---

## CATEGORÍA 7: Cierre de Venta

---

### E33 — Cliente listo para comprar (envío)

**Descripción:** El cliente decide comprar y quiere envío.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Quiero comprarlo, envíenme el kit a Bogotá" |
| 2 | E | Confirma la opción de envío, solicita número de teléfono y horario para llamada con el asesor comercial. |

✅ Solicita teléfono y horario para la llamada.
✅ No intenta cerrar la venta sin el asesor.

---

### E34 — Cliente listo para comprar (instalación en Cali)

**Descripción:** El cliente quiere instalación en el taller de Cali.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Prefiero llevarlo al taller en Cali" |
| 2 | E | Confirma la instalación en Cali y agenda llamada con asesor: solicita teléfono y horario disponible. |

✅ Confirma opción de instalación en Cali.
✅ Avanza a agendamiento de llamada.

---

### E35 — Cliente interesado en jornada fuera de Cali

**Descripción:** El cliente está en Bogotá o Medellín.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Estoy en Medellín, ¿cómo funciona la jornada ahí?" |
| 2 | E | Explica brevemente las jornadas de adaptación y ofrece agendar llamada para detalles de fechas y horarios. |

✅ Menciona las jornadas en Bogotá y Medellín.
✅ No inventa fechas ni horarios de jornadas.

---

### E36 — Agendamiento de llamada (confirmar datos)

**Descripción:** El cliente acepta la llamada con el asesor.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Bueno, pueden llamarme" |
| 2 | E | Solicita: número de teléfono y horario preferido para la llamada. |

✅ Solicita exactamente teléfono y horario.
✅ Confirma los datos recibidos antes de finalizar.

---

### E37 — Cliente no quiere llamada pero sí comprar

**Descripción:** El cliente quiere comprar pero prefiere no recibir llamada.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "No quiero llamadas, prefiero hacerlo por aquí" |
| 2 | E | Intenta agendar la llamada de todas formas explicando que es necesaria para el cierre, o escala al asesor por chat si aplica. |

✅ Insiste en la llamada como parte del proceso de cierre.
✅ No cierra la venta por chat sin el asesor.

---

### E38 — Cliente pide tiempo para pensar

**Descripción:** El cliente no decide en el momento.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Déjame pensarlo y te escribo después" |
| 2 | E | Acepta, ofrece agendar llamada para cuando esté listo y deja la puerta abierta. |

✅ No presiona de forma agresiva.
✅ Mantiene la oferta activa y ofrece retomar.

---

## CATEGORÍA 8: Casos Extremos y Robustez

---

### E39 — Mensajes en otro idioma

**Descripción:** El cliente escribe en inglés.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Hello, I need information about your products" |
| 2 | E | Responde en español colombiano y solicita el nombre del cliente. |

✅ El bot responde en español, no en inglés.
✅ Mantiene el flujo estándar de apertura.

---

### E40 — Mensaje con lenguaje ofensivo o inapropiado

**Descripción:** El cliente usa palabras ofensivas o lenguaje agresivo.

| Turno | Actor | Mensaje |
|-------|-------|---------|
| 1 | U | "Ese kit es una estafa, son unos ladrones" |
| 2 | E | Responde con empatía, sin confrontación, y redirige profesionalmente hacia los beneficios y la trayectoria de la empresa. |

✅ No responde con agresividad.
✅ Mantiene el tono empático y comercial.
✅ Intenta reencuadrar la objeción y continuar hacia el cierre.

---

## Resumen de Cobertura

| # | Categoría | Escenarios |
|---|-----------|------------|
| 1 | Apertura y Saludo | E01–E05 |
| 2 | Identificación del Vehículo | E06–E12 |
| 3 | Recomendación del Kit | E13–E16 |
| 4 | Manejo de Objeciones | E17–E25 |
| 5 | Preguntas Fuera de Alcance | E26–E29 |
| 6 | Silencios y Timeouts | E30–E32 |
| 7 | Cierre de Venta | E33–E38 |
| 8 | Casos Extremos y Robustez | E39–E40 |
| | **Total** | **40 escenarios** |
