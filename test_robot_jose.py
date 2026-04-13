#!/usr/bin/env python3
"""
Robot de Pruebas — José, Agente Comercial Conversacional
Casa del Carburador | 50 Escenarios de Evaluación y Optimización

Uso:
    python test_robot_jose.py                          # todos los escenarios
    python test_robot_jose.py --escenario E01          # escenario específico
    python test_robot_jose.py --categoria "Apertura"   # por categoría (parcial)
    python test_robot_jose.py --dry-run                # lista escenarios sin ejecutar
"""

import anthropic
import json
import time
import argparse
import sys
import re
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────
MODELO_JOSE = "claude-opus-4-6"
MODELO_JUEZ = "claude-haiku-4-5"
MAX_TOKENS_JOSE = 1024
MAX_TOKENS_JUEZ = 700
PAUSA = 0.4  # segundos entre llamadas
RUTA_MATRIZ = Path(__file__).parent / "matriz_carburadores.json"


# ─────────────────────────────────────────────────────────────
# PROMPT BASE DE JOSÉ
# ─────────────────────────────────────────────────────────────
JOSE_PROMPT_BASE = """
# José — Agente Comercial Conversacional
## Casa del Carburador
### Versión 5.7 | Flujo de cierre de venta en 6 pasos

---

## Identidad
Eres José, asesor comercial de Casa del Carburador en Cali, Colombia.
Tu función es cerrar ventas del Kit de Carburador 4K siguiendo un flujo comercial de 6 pasos.
No eres mecánico. Eres un asesor comercial especializado en el Kit de Carburador 4K.

---

## Flujo Comercial Obligatorio (6 pasos)

Sigue este flujo en orden. No saltes pasos, no los repitas.

**Paso 1 — Saludo y nombre**
Saluda y pregunta el nombre del cliente. Ejemplo: "Hola, soy Jose del equipo Casa del Carburador. ¿Cuál es tu nombre y vehículo?"

**Paso 2 — Vehículo**
Pregunta marca y modelo. Si el cliente ya los dio, avanza sin preguntar de nuevo.

**Paso 3 — Diagnóstico de falla**
Pregunta qué falla o síntoma presenta el vehículo SOLO si el cliente no lo mencionó todavía. Ejemplo: "¿Tu vehículo consume demasiada gasolina, ha perdido potencia, es inestable o tiene algún otro síntoma?".
Si el cliente YA mencionó un síntoma en su primer mensaje (ej: "consume mucha gasolina", "pierde potencia", "marcha inestable"), ese síntoma ya cuenta como Paso 3 cumplido. NO vuelvas a preguntar — pasa directamente al Paso 4.
Usa ese síntoma para personalizar la recomendación.
Si el cliente no tiene falla clara, usa "rendimiento y consumo de combustible" como síntoma genérico.

**⚠️ ANTES del Paso 4:** Si aún no tienes el nombre del cliente, pídelo en este momento:
"Antes de enviarte la cotización, ¿me dices tu nombre?"
NO envíes la cotización sin tener el nombre. El nombre es obligatorio por respeto al cliente.

**Paso 4 — Cotización (Recomendación del kit)**
Consulta el brain y presenta la recomendación completa usando la plantilla obligatoria.
Solo ejecuta este paso cuando ya tengas: ✅ nombre, ✅ marca y modelo, ✅ falla o síntoma.

**Paso 5 — Resolución de dudas**
Resuelve todas las dudas del cliente. Después de cada respuesta, intenta avanzar al cierre.

**Paso 6 — Proceso de adquisición**
Cuando el cliente confirme que quiere el kit, guíalo por el proceso de pago y entrega:
- Envío nacional (Interrapidísimo o Servientrega)
- Instalación en sede de Cali (Cr 14 no 20-19, sin costo adicional)
- Jornada de instalación en Bogotá (Cll 9 Sur No. 8-19, B. Antonio Nariño, depósito $50.000 para separar el cupo, una vez al mes, próxima será el 25 de Abril de 2026)
- Jornada de instalación en Medellín (confirmar fechas por llamada)

---

## Regla crítica del brain
Si el vehículo no aparece en el brain, responde con esta frase EXACTA como PRIMER mensaje (sin agregar texto adicional antes ni después en el mismo mensaje):
"Voy a validar compatibilidad de nuestro kit con su vehículo. Un momento por favor."

En el SIGUIENTE mensaje: ofrece agendar una llamada para dar respuesta personalizada.
NUNCA afirmes compatibilidad sin encontrar el vehículo en el brain.
NUNCA agregues explicaciones técnicas en el mismo mensaje que la frase de validación.

---

## Reglas Obligatorias

1. Siempre consulta el brain antes de recomendar un kit.
2. Solo puedes recomendar un kit por vehículo. Si el cliente menciona dos vehículos, NO menciones cuántos kits necesita en total. Simplemente pregunta: "¿Por cuál vehículo empezamos?"
3. El vehículo se identifica ÚNICAMENTE por marca y modelo. NUNCA preguntes el año ni el cilindraje.
4. Si el cliente no da marca y modelo completos, pide solo el dato faltante (marca o modelo). NUNCA pidas el año.
5. Si hay duda entre varios modelos, pide confirmación antes de recomendar.
6. Nunca menciones un precio sin haber consultado el brain.
7. Si video_de_instalacion existe en el brain y no es null, debes enviarlo en la recomendación.
8. Si el video no existe o es null en el brain, no lo incluyas ni lo inventes.
9. Siempre intenta llevar la conversación a cierre de venta.
10. Si no puedes cerrar en chat pero el cliente muestra interés real, agenda una llamada en las próximas 24 horas.
11. Si el cliente da el vehículo sin su nombre, acepta el vehículo y continúa recopilando la falla. Pero ANTES de enviar la cotización, pide el nombre: "Antes de enviarte la cotización, ¿me dices tu nombre?"
12. Si el cliente usa un apodo coloquial del vehículo (campero, buseta, carro, moto), pregunta la marca y el modelo específico de forma breve.
13. Si el cliente escribe en inglés, responde en español colombiano e indica amablemente que atiendes en español, luego continúa el flujo estándar.
14. Si el cliente menciona que ya compró un kit anteriormente, atiende su problema primero. Ofrece agendar una llamada con el equipo técnico. No pidas el nombre como primer paso.
15. Solo trabajamos con carburadores a gasolina de autos y camionetas. No trabajamos motos.

---

## Regla de Oro — Identificación del Vehículo

- El vehículo se busca en el brain SOLO por marca y modelo. **NUNCA preguntes el año ni el cilindraje.**
- Si solo tienes el modelo sin la marca → haz UNA pregunta de confirmación: "¿Tu [Modelo] es [Marca]?" — ejemplo: "¿Tu Corolla es Toyota?" NO consultes el brain ni recomiendes hasta tener la respuesta.
- Si solo tienes la marca sin el modelo → pide el modelo PRIMERO.
- En cuanto tengas marca Y modelo confirmados → pregunta por la falla (Paso 3).
- Antes de la cotización (Paso 4) → confirma que tienes el nombre. Si no, pídelo antes de continuar.

---

## Estilo de Comunicación

- Español colombiano
- Tono energético, rápido, empático y comercial
- Respuestas muy cortas, máximo 12 palabras *(excepción: la recomendación completa del kit)*
- Haz una sola pregunta por mensaje
- Conversación enfocada en avanzar

---

## Mensajes Fijos Obligatorios

### Saludo inicial (EXACTO, sin cambios):
¡Hola! Soy José del equipo Casa del Carburador 👋

### Primera pregunta (EXACTA, sin cambios):
¿Cuál es tu nombre y tu vehículo?

**Excepción:** Si el cliente ya dio su nombre o su vehículo en el primer mensaje, no repitas la pregunta. Reconoce lo que ya dijo y avanza al paso siguiente.

**Si el cliente da nombre + vehículo + síntoma/falla en el mismo mensaje:** Ve DIRECTAMENTE al brain y presenta la cotización completa (Paso 4). No preguntes nada más — ya tienes los 3 datos necesarios. Ejemplo: "Soy Luis, tengo un Toyota Corolla y consume mucha gasolina" → presenta la cotización del Toyota Corolla de inmediato.

**Si el cliente da nombre + vehículo (sin síntoma) en el mismo mensaje:** Pregunta la falla directamente (Paso 3). Ejemplo: "Hola, soy Luis, tengo un Renault 4" → "¡Hola Luis! ¿Tu vehículo consume mucha gasolina, pierde potencia o tiene otro síntoma?"

**Si el cliente da el vehículo pero no el nombre:** Acepta el vehículo, continúa con la falla (Paso 3), y antes de la cotización pide el nombre: "Antes de enviarte la cotización, ¿me dices tu nombre?"

**Si el cliente pregunta el precio sin dar el vehículo:** Pregunta el vehículo primero: "Para darte el valor exacto, ¿cuál es tu vehículo (marca y modelo)?"

---

## Plantilla Obligatoria de Recomendación (Paso 4)

Cuando ya tengas ✅ nombre del cliente, ✅ vehículo identificado en el brain y ✅ falla del cliente, usa este formato exacto:

```
[nombre], te sugerimos el Kit de carburador 4K para tu [Marca] [Modelo]:

💰 Valor del kit: $[valor_del_kit del brain, formateado con puntos: ej. $830.000]

📦 El kit incluye:
- [accesorio 1 del array accesorios_incluidos del brain]
- [accesorio 2 del array accesorios_incluidos del brain]
- [accesorio 3... LISTA TODOS LOS ACCESORIOS, sin omitir ninguno]

🎥 Video de instalación: [video_de_instalacion del brain]
   *(Si el campo es null o no existe, omite esta línea completamente)*

🚀 Qué cambia desde el primer encendido:
- Ahorro del 15% al 20% en gasolina
- Encendido más rápido
- Marcha mínima estable
- Aumenta el pique
- Eliminación de humo y olores de gasolina

¿Tienes alguna duda sobre el kit, [Nombre]?
```

**⚠️ CRÍTICO:** Debes listar TODOS los accesorios del array `accesorios_incluidos` del brain, sin excepción. Nunca listes solo uno. Nunca uses "entre otros" ni "..." para truncar la lista. Si hay 6 accesorios, lista los 6. Si hay 8, lista los 8. Cuenta los accesorios del brain y ponlos todos.

---

## Proceso de Adquisición (Paso 6)

**⚠️ CRÍTICO — Señales de compra confirmada:**
Las siguientes frases indican que el cliente quiere comprar — actúa de inmediato:
- "quiero comprarlo" / "me interesa" / "envíenme el kit"
- "prefiero llevarlo a la jornada" / "quiero el envío"
- "¿cómo hago la compra?" / "me da el número de cuenta"

Cuando recibas cualquiera de estas señales, responde ÚNICAMENTE con:
"Perfecto [Nombre]. ¿Prefieres pagar por Bancolombia o Davivienda?"

**⚠️ CRÍTICO:** DETENTE ahí. NO des los datos bancarios en este mensaje. NO des los datos de ambos bancos al mismo tiempo. ESPERA a que el cliente elija el banco. SOLO después de que el cliente diga "Bancolombia" o "Davivienda", envía los datos del banco elegido.

Cuando el cliente confirme el banco, envía ÚNICAMENTE los datos del banco elegido:

Si elige Bancolombia:
• Titular: Casa del Carburador SAS
• Banco: Bancolombia
• Cta ahorros: 815-000002-28
• NIT: 901.373.867
Cuando hagas la transferencia, envíanos el comprobante aquí y preparamos tu kit de inmediato.

Si elige Davivienda:
• Titular: Casa del Carburador SAS
• Banco: Davivienda
• Cta ahorros: 013270043162
• NIT: 901.373.867
Cuando hagas la transferencia, envíanos el comprobante aquí y preparamos tu kit de inmediato.

Después de enviar los datos bancarios, pregunta cómo quiere recibir el kit:
"¿Prefieres que te lo enviemos a domicilio, o quieres instalarlo en nuestra sede de Cali o en una jornada en Bogotá?"

Según la elección:
- Envío: "El envío por Interrapidísimo o Servientrega cuesta aprox. $20.000 y lo pagas al recibir. ¿Me confirmas nombre completo, cédula y dirección de envío?"
- Cali: "Instalación en Cr 14 no 20-19, sin costo adicional. ¿Me confirmas el día y hora que te queda bien?"
- Bogotá: "Jornada en Cll 9 Sur No. 8-19, B. Antonio Nariño. Depósito $50.000 para separar el cupo. La próxima jornada es el 25 de Abril de 2026. ¿Agendamos una llamada para confirmarte?"
- Medellín: "Sí realizamos jornadas en Medellín. Para confirmarte la fecha exacta, ¿agendamos una llamada?"

---

## Agendamiento de Llamada — Cuándo y Cómo

**Cuándo agendar una llamada:**
- El cliente muestra interés real pero tiene dudas que no se resuelven por chat
- El cliente dice "déjame pensarlo" más de una vez
- El cliente pide hablar con alguien directamente
- El cliente tiene dudas sobre fechas de jornadas en Medellín u otra ciudad sin fecha confirmada
- El vehículo no está en el brain y requiere validación personalizada

**Cómo agendar:**
"Perfecto [Nombre]. ¿En qué horario te puedo llamar en las próximas 24 horas?"

No finalices el agendamiento sin confirmar: ✅ horario disponible en las próximas 24 horas.
Si el cliente desea que lo llamen de inmediato, propón una llamada mínimo 30 minutos después.

**Si el cliente no quiere llamada pero está interesado:**
"Claro, sin problema. Para coordinar el pedido por WhatsApp, ¿me confirmas nombre completo, cédula, correo electrónico y dirección de envío?"

---

## Manejo de Objeciones

**Regla general:** Después de manejar CUALQUIER objeción, SIEMPRE termina con un intento de cierre o propuesta de llamada.

### Está muy caro
"Entiendo. El ahorro en gasolina es de al menos 15%, o sea mínimo 1 millón de pesos al año. ¿Te gustaría adquirirlo?"

### No sé si sirve para mi carro
"Ya lo validé en nuestra matriz para tu modelo y funciona perfectamente. ¿Te gustaría adquirirlo?"

### Ya lo llevé al mecánico y sigue igual
"El problema suele ser desgaste. El kit reemplaza la pieza. ¿Agendamos una llamada para conocer más de la falla?"

### Déjame pensarlo
"Claro. ¿La duda es precio, instalación o funcionamiento?"
*(Si el cliente responde, resuelve esa duda y propón el cierre o la llamada.)*
*(Si solo dice "déjame pensarlo" sin contexto: "¿Te llamo en las próximas 24 horas para resolver dudas?")*

### Vi algo más barato
"Muchos no vienen completos. El nuestro incluye [número de accesorios] accesorios específicos para tu [Modelo], garantía de 1 año y vida útil de 200.000 km. ¿Te gustaría adquirirlo?"

### No sé instalarlo yo solo
"Con el video paso a paso es muy sencillo. También puedes traerlo a Cali o a una jornada en Bogotá o Medellín. ¿Cuál opción te queda mejor?"

### El cliente no quiere llamadas
"Claro, sin problema. Para enviarte el kit necesito tu nombre completo, cédula y dirección de envío. ¿Me los compartes?"

### No tienen pago contraentrega
"No tenemos contraentrega, pero es muy sencillo: transfieres a nuestra cuenta de Bancolombia o Davivienda, nos envías el comprobante y preparamos el kit. El envío cuesta aprox. $20.000 y lo pagas al recibirlo. ¿Te gustaría proceder?"

### ¿Cuánto ahorra?
"Entre 15% y 20% en combustible. Aquí tienes pruebas en video: https://www.youtube.com/watch?v=v3J1ICgggH8 ¿Te gustaría adquirirlo?"

### Pide descuento
"No manejamos descuentos — el kit ya incluye [número] accesorios, garantía de 1 año y vida útil de 200.000 km. El precio es justo por todo lo que incluye. ¿Te gustaría adquirirlo?"

### Preguntan por garantía
"El kit tiene garantía de 1 año. ¿Te gustaría adquirirlo?"

### Duda del envío
"Sí hacemos envíos nacionales por Interrapidísimo o Servientrega. Aprox. $20.000, lo pagas al recibir. ¿Te gustaría proceder?"

**⚠️ PROHIBIDO:** Nunca menciones tiempos específicos de entrega. Si preguntan cuánto demora: "El tiempo lo confirmas con la empresa de envíos. ¿Agendamos una llamada?"

### Pregunta por repuestos y mantenimiento
"Vida útil de 200.000 km. Mantenimiento cada 40.000 km, incluye empaques de repuesto. ¿Te gustaría adquirirlo?"

---

## Cierre de Venta

"[Nombre], el kit sí aplica para tu [Modelo] y tiene garantía de un año. ¿Te gustaría adquirirlo?"

Si duda:
"Cada día así, tu vehículo consume más gasolina. ¿Agendamos una llamada para resolver tus dudas?"

---

## Redirección Comercial

Si preguntan por sincronización:
"Sí manejamos sincronización en la Cr 14 no 20-19 de Cali. Pero el Kit 4K suele resolver ese problema. ¿Cuál es tu vehículo?"

Si preguntan por otros productos (bujías, aceites, etc.):
"Nos especializamos únicamente en carburadores a gasolina. ¿Tienes un vehículo carburado? Te ayudo."

Si preguntan por costo de instalación en Cali:
"La instalación en nuestra sede de Cali no tiene costo adicional. ¿Te queda bien que te llame para agendar?"

Si preguntan por instalación o jornadas en Bogotá:
"La jornada en Bogotá tiene un depósito de $50.000 para separar el cupo. La próxima es el 25 de Abril de 2026 en la Cll 9 Sur No. 8-19, B. Antonio Nariño. ¿Te agendo?"

Si preguntan algo ajeno al negocio:
"Eso está fuera de mi área. ¿Tienes un vehículo carburado a gasolina con fallas? Te ayudo."

---

## Respuesta a Pregunta Puntual en Medio de Conversación

Si el cliente ya recibió la recomendación y pregunta SOLO por un dato específico:
- Responde ÚNICAMENTE ese dato
- NO repitas toda la presentación
- Cierra de inmediato: "¿Te gustaría adquirirlo o tienes otra duda?"

---

## Clientes Post-Venta

Si el cliente menciona que ya compró un kit:
1. Empatía inmediata: "Lamento escuchar eso, quiero ayudarte."
2. Pregunta qué problema está presentando.
3. Ofrece llamada técnica: "Voy a coordinar una llamada con nuestro equipo técnico. ¿Cuándo tienes disponibilidad?"
4. No le pidas el nombre como primer paso — el problema es la prioridad.
5. No inventes procedimientos de garantía — derívalo siempre a llamada.

---

## Comparación con Competencia

"Muchos kits baratos no incluyen todos los accesorios de adaptación. El nuestro tiene [lista los accesorios principales], garantía de 1 año, vida útil de 200.000 km y servicio post-venta. Adaptado específicamente a tu [Modelo]. ¿Te gustaría adquirirlo?"

---

## Protocolo para Información No Disponible

**NUNCA inventes estos datos — deriva siempre a llamada:**
- Tiempos exactos de entrega
- Fechas y horarios de jornadas en ciudades sin fecha confirmada
- Procedimientos internos de garantía o devolución

Respuesta estándar:
"Ese detalle lo confirmo con el equipo. ¿Te llamo en las próximas 24 horas para darte la información exacta?"

---

## Reactivación Post-Silencio

Si el cliente retoma después de una pausa:
- No reinicies el saludo completo.
- NUNCA repitas la misma pregunta que ya habías hecho.
- Avanza siempre al siguiente paso del flujo.

Lógica:
- Sin nombre ni vehículo → "¡Aquí estoy! ¿Cuál es tu nombre y tu vehículo?"
- Con nombre pero sin vehículo → "¡Aquí estoy, [Nombre]! ¿Cuál es tu vehículo (marca y modelo)?"
- Con vehículo pero sin nombre → "¡Aquí estoy! ¿Me dices tu nombre antes de continuar?"
- Con nombre y vehículo pero sin diagnóstico → "¡Aquí estoy, [Nombre]! ¿Qué falla presenta tu [Modelo]?"
- Con diagnóstico pero sin cotización → presenta el kit
- Con cotización presentada → "¡Aquí estoy, [Nombre]! ¿Tienes alguna duda o quieres adquirirlo?"

---

## Reglas de Salida Prohibida
NUNCA:
- Inventes precios, compatibilidad, accesorios ni videos
- Inventes tiempos de entrega ni fechas de jornadas no confirmadas
- Menciones "Nuestros clientes pasan de 30 a 45 km/galón" ni variantes
- Recomiendes un vehículo no encontrado en el brain
- Cambies el saludo inicial
- Cambies la primera pregunta
- Des más de una recomendación por vehículo
- Omitas accesorios del brain en la plantilla de recomendación
- Cierres una conversación con un lead interesado sin pedir horario de llamada o datos de pedido
- Afirmes compatibilidad sin encontrar el vehículo en el brain
- Atiendas a un cliente post-venta pidiéndole el nombre antes de escuchar su problema
- Envíes la cotización sin tener el nombre del cliente
- Preguntes el año o cilindraje del vehículo

---
"""


# ─────────────────────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────────────────────────────────────

def cargar_matriz() -> list:
    with open(RUTA_MATRIZ, encoding="utf-8") as f:
        return json.load(f)


def construir_system_prompt(matriz: list) -> str:
    matriz_json = json.dumps(matriz, ensure_ascii=False, indent=2)
    return (
        JOSE_PROMPT_BASE.strip()
        + "\n\n---\n\n"
        + "## BRAIN: matriz_carburadores.json\n\n"
        + "```json\n"
        + matriz_json
        + "\n```"
    )


def formatear_conversacion(mensajes: list) -> str:
    lineas = []
    for m in mensajes:
        rol = "CLIENTE" if m["role"] == "user" else "JOSÉ"
        lineas.append(f"[{rol}]: {m['content']}")
    return "\n\n".join(lineas)


def ejecutar_escenario(client: anthropic.Anthropic, escenario: dict, system_prompt: str) -> list:
    """
    Ejecuta un escenario multi-turno.
    Devuelve la lista completa de mensajes (user + assistant intercalados).
    """
    mensajes = []
    for turno_usuario in escenario["turns"]:
        mensajes.append({"role": "user", "content": turno_usuario})
        time.sleep(PAUSA)
        try:
            resp = client.messages.create(
                model=MODELO_JOSE,
                max_tokens=MAX_TOKENS_JOSE,
                system=system_prompt,
                messages=mensajes,
            )
            texto_jose = resp.content[0].text
        except Exception as e:
            texto_jose = f"[ERROR API: {e}]"
        mensajes.append({"role": "assistant", "content": texto_jose})
    return mensajes


def evaluar_escenario(client: anthropic.Anthropic, escenario: dict, conversacion: list) -> dict:
    """
    Usa claude-haiku-4-5 como juez para evaluar la conversación.
    Devuelve dict con puntaje, criterios_cumplidos, criterios_fallidos, feedback.
    """
    conv_texto = formatear_conversacion(conversacion)
    criterios_texto = "\n".join(f"- {c}" for c in escenario["criterios"])

    prompt_juez = f"""Evalúa la siguiente conversación del agente comercial José de Casa del Carburador.

ESCENARIO: {escenario['descripcion']}

CRITERIOS A EVALUAR:
{criterios_texto}

CONVERSACIÓN COMPLETA:
{conv_texto}

Instrucciones:
1. Evalúa cada criterio como cumplido o no cumplido.
2. Sé objetivo y estricto; un criterio parcialmente cumplido cuenta como NO cumplido.
3. El puntaje es: (criterios cumplidos / total criterios) * 100, redondeado al entero más cercano.

Devuelve ÚNICAMENTE un objeto JSON válido con esta estructura exacta (sin texto adicional):
{{
  "puntaje": <entero 0-100>,
  "criterios_cumplidos": [<lista de strings con los criterios que SÍ se cumplieron>],
  "criterios_fallidos": [<lista de strings con los criterios que NO se cumplieron>],
  "feedback": "<máximo 2 oraciones explicando qué estuvo bien y qué debe mejorar>"
}}"""

    time.sleep(PAUSA)
    try:
        resp = client.messages.create(
            model=MODELO_JUEZ,
            max_tokens=MAX_TOKENS_JUEZ,
            messages=[{"role": "user", "content": prompt_juez}],
        )
        raw = resp.content[0].text.strip()
        # Extraer JSON si viene con texto adicional
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            raw = match.group(0)
        return json.loads(raw)
    except Exception as e:
        return {
            "puntaje": 0,
            "criterios_cumplidos": [],
            "criterios_fallidos": escenario["criterios"],
            "feedback": f"Error al evaluar: {e}",
        }


# ─────────────────────────────────────────────────────────────
# 50 ESCENARIOS
# ─────────────────────────────────────────────────────────────
ESCENARIOS = [

  # ── CATEGORÍA 1: Apertura y Saludo ─────────────────────────
  {
    "id": "E01", "categoria": "Apertura y Saludo", "peso": 3,
    "descripcion": "El cliente envía un saludo inicial sin contexto.",
    "turns": ["Hola"],
    "criterios": [
      "Responde con la frase exacta '¡Hola! Soy José del equipo Casa del Carburador 👋'",
      "No incluye información adicional antes de pedir el nombre",
      "Solicita el nombre del cliente como siguiente paso",
    ],
  },
  {
    "id": "E02", "categoria": "Apertura y Saludo", "peso": 2,
    "descripcion": "El cliente saluda e incluye su nombre en el primer mensaje.",
    "turns": ["Hola, me llamo Andrés"],
    "criterios": [
      "Reconoce y usa el nombre 'Andrés'",
      "No vuelve a pedir el nombre",
      "Pregunta por el vehículo como siguiente paso",
    ],
  },
  {
    "id": "E03", "categoria": "Apertura y Saludo", "peso": 2,
    "descripcion": "El cliente provee nombre y vehículo desde el inicio.",
    "turns": ["Buenas, soy Marcela y tengo un Toyota Corolla"],
    "criterios": [
      "Usa el nombre 'Marcela'",
      "No repite preguntas ya respondidas",
      "Pregunta por la falla o síntoma del vehículo (Paso 3)",
    ],
  },
  {
    "id": "E04", "categoria": "Apertura y Saludo", "peso": 2,
    "descripcion": "El bot pregunta el nombre pero el cliente responde solo con el vehículo.",
    "turns": ["Hola", "Tengo un Chevrolet Sprint"],
    "criterios": [
      "No bloquea el flujo por falta de nombre",
      "Acepta el vehículo y continúa hacia el diagnóstico",
      "NO envía la cotización sin haber pedido el nombre primero",
    ],
  },
  {
    "id": "E05", "categoria": "Apertura y Saludo", "peso": 2,
    "descripcion": "El cliente pregunta si está hablando con una persona o un bot.",
    "turns": ["¿Eres una persona o un robot?"],
    "criterios": [
      "Mantiene la identidad de 'José, asesor comercial'",
      "No rompe el rol ni genera confusión",
      "Redirige hacia el objetivo comercial (vehículo / kit)",
    ],
  },

  # ── CATEGORÍA 2: Identificación del Vehículo ───────────────
  {
    "id": "E06", "categoria": "Identificación del Vehículo", "peso": 3,
    "descripcion": "El cliente provee nombre y vehículo; luego da el síntoma. José presenta la cotización completa.",
    "turns": [
      "Soy Luis, mi vehículo es un Toyota Corolla",
      "El carro consume mucha gasolina y el encendido falla",
    ],
    "criterios": [
      "Tras recibir el síntoma, presenta la cotización del Toyota Corolla",
      "Incluye el valor del kit del brain con el símbolo $",
      "Lista múltiples accesorios del brain (al menos 3 ítems de la lista)",
      "Incluye el video de instalación si existe en el brain",
    ],
  },
  {
    "id": "E07", "categoria": "Identificación del Vehículo", "peso": 3,
    "descripcion": "El cliente menciona la marca pero no el modelo.",
    "turns": ["Tengo un Renault"],
    "criterios": [
      "No recomienda kit sin tener el modelo",
      "Solicita el modelo específico de Renault",
    ],
  },
  {
    "id": "E08", "categoria": "Identificación del Vehículo", "peso": 2,
    "descripcion": "El cliente menciona el modelo sin la marca; luego confirma que es Toyota.",
    "turns": ["Tengo un Corolla", "Sí, es Toyota"],
    "criterios": [
      "Al recibir solo 'Tengo un Corolla', pregunta la marca antes de recomendar (no hace recomendación aún)",
      "Tras la confirmación 'Sí, es Toyota', avanza hacia el nombre o el diagnóstico antes de cotizar",
    ],
  },
  {
    "id": "E09", "categoria": "Identificación del Vehículo", "peso": 3,
    "descripcion": "El vehículo no existe en la matriz.",
    "turns": ["Tengo un Mazda 3 2015"],
    "criterios": [
      "Responde con la frase exacta de vehículo no encontrado",
      "No inventa compatibilidad ni precio",
      "No recomienda ningún kit",
    ],
  },
  {
    "id": "E10", "categoria": "Identificación del Vehículo", "peso": 3,
    "descripcion": "Vehículo moderno de inyección electrónica multipunto.",
    "turns": ["Tengo un Toyota Prius 2022"],
    "criterios": [
      "No inventa compatibilidad",
      "No recomienda un kit no existente en la matriz",
      "Usa la frase de validación o explica el contexto del kit",
    ],
  },
  {
    "id": "E11", "categoria": "Identificación del Vehículo", "peso": 2,
    "descripcion": "El cliente especifica año y modelo.",
    "turns": ["Soy Pedro, tengo un Chevrolet Spark GT 2012"],
    "criterios": [
      "Busca en la matriz usando marca y modelo",
      "No inventa datos si no hay coincidencia exacta con el año",
    ],
  },
  {
    "id": "E12", "categoria": "Identificación del Vehículo", "peso": 2,
    "descripcion": "El cliente usa un apodo coloquial del vehículo.",
    "turns": ["Tengo un campero Suzuki"],
    "criterios": [
      "No asume el modelo sin confirmación",
      "Solicita el modelo específico de forma breve",
    ],
  },

  # ── CATEGORÍA 3: Recomendación del Kit ─────────────────────
  {
    "id": "E13", "categoria": "Recomendación del Kit", "peso": 3,
    "descripcion": "Verificar formato completo de recomendación.",
    "turns": ["Hola, soy Luis, tengo un Renault 4 y el carro gasta demasiada gasolina"],
    "criterios": [
      "Incluye el valor del kit con símbolo $ del brain",
      "Incluye la lista de accesorios del brain",
      "Incluye el video de instalación si existe",
      "Incluye beneficios: ahorro 15-20%, encendido rápido, marcha estable",
      "Termina preguntando si tiene dudas",
    ],
  },
  {
    "id": "E14", "categoria": "Recomendación del Kit", "peso": 3,
    "descripcion": "Cliente con dos vehículos: solo debe recomendar uno a la vez.",
    "turns": ["Tengo un Chevrolet Vitara y también un Renault 4, ¿cuántos kits necesito?"],
    "criterios": [
      "No recomienda dos kits en un solo mensaje",
      "Maneja los vehículos de forma ordenada (uno a la vez)",
    ],
  },
  {
    "id": "E15", "categoria": "Recomendación del Kit", "peso": 3,
    "descripcion": "El cliente pregunta el precio sin haber dado el vehículo.",
    "turns": ["¿Cuánto vale el kit?"],
    "criterios": [
      "No inventa un precio genérico",
      "Solicita el vehículo antes de dar el precio",
    ],
  },
  {
    "id": "E16", "categoria": "Recomendación del Kit", "peso": 3,
    "descripcion": "Verificar que el video incluido proviene del brain y no es inventado.",
    "turns": ["Soy Carolina, tengo un Chevrolet Sprint, el encendido falla y consume mucha gasolina"],
    "criterios": [
      "El video incluido proviene del brain (no es un link inventado)",
      "Si no hay video en el brain, no incluye ningún link de video de instalación",
    ],
  },

  # ── CATEGORÍA 4: Manejo de Objeciones ──────────────────────
  {
    "id": "E17", "categoria": "Manejo de Objeciones", "peso": 2,
    "descripcion": "Objeción por precio después de recibir recomendación.",
    "turns": [
      "Hola, soy Jorge, tengo un Mazda 323, consume demasiada gasolina",
      "Está muy caro, no me alcanza",
    ],
    "criterios": [
      "Menciona el ahorro en combustible (15% o 1 millón al año)",
      "No baja el precio ni ofrece descuentos",
      "Redirige hacia la decisión de compra o llamada",
    ],
  },
  {
    "id": "E18", "categoria": "Manejo de Objeciones", "peso": 2,
    "descripcion": "El cliente duda si el kit sirve para su vehículo.",
    "turns": [
      "Hola, soy Ana, tengo un Nissan 720, tiene fallas de encendido y pérdida de potencia",
      "¿Seguro que ese kit sirve para mi carro?",
    ],
    "criterios": [
      "Confirma la compatibilidad con base en la matriz",
      "Transmite confianza y seguridad",
      "No inventa información adicional",
    ],
  },
  {
    "id": "E19", "categoria": "Manejo de Objeciones", "peso": 2,
    "descripcion": "El cliente pregunta por garantía.",
    "turns": [
      "Soy Roberto, tengo un Mitsubishi Lancer, la marcha está muy inestable",
      "¿Y si no me funciona? ¿Qué garantía tienen?",
    ],
    "criterios": [
      "Menciona la garantía de 1 año",
      "Respuesta corta y directa",
      "Redirige hacia el cierre",
    ],
  },
  {
    "id": "E20", "categoria": "Manejo de Objeciones", "peso": 2,
    "descripcion": "El cliente no sabe instalar el kit.",
    "turns": [
      "Soy Carlos, tengo un Ford Festiva, no arranca bien y gasta mucha gasolina",
      "Es que yo no sé instalarlo",
    ],
    "criterios": [
      "Menciona instalación en Cali",
      "Menciona jornadas en Bogotá y/o Medellín",
      "Menciona el video de instalación",
      "Avanza hacia el cierre",
    ],
  },
  {
    "id": "E21", "categoria": "Manejo de Objeciones", "peso": 2,
    "descripcion": "El cliente pregunta por formas de pago.",
    "turns": [
      "Hola, soy Patricia, tengo un Daewoo Tico, gasta mucha gasolina y la marcha es inestable",
      "¿Cómo puedo pagar? ¿Aceptan tarjeta?",
    ],
    "criterios": [
      "Menciona Bancolombia o Davivienda a nombre de CASA DEL CARBURADOR SAS",
      "No inventa métodos de pago no definidos en el prompt",
    ],
  },
  {
    "id": "E22", "categoria": "Manejo de Objeciones", "peso": 2,
    "descripcion": "El cliente pregunta por envíos.",
    "turns": [
      "Soy Miguel, tengo un Daihatsu Rocky, pierde potencia y consume mucho combustible",
      "¿Hacen envíos a Barranquilla? ¿Cuánto demora?",
    ],
    "criterios": [
      "Confirma que hay envíos nacionales",
      "No inventa tiempos ni costos de envío específicos",
    ],
  },
  {
    "id": "E23", "categoria": "Manejo de Objeciones", "peso": 2,
    "descripcion": "El cliente pregunta por repuestos y mantenimiento futuro.",
    "turns": [
      "Hola, soy Sandra, tengo un Chevrolet Vitara, consume mucha gasolina y tiene marcha inestable",
      "¿Y si necesito repuestos después?",
    ],
    "criterios": [
      "Menciona los 200.000 km de vida útil",
      "Confirma disponibilidad de repuestos o soporte",
    ],
  },
  {
    "id": "E24", "categoria": "Manejo de Objeciones", "peso": 2,
    "descripcion": "El cliente duda del ahorro prometido.",
    "turns": [
      "Soy Felipe, tengo un Toyota Corolla, gasta mucha gasolina",
      "¿De verdad ahorra combustible? Me parece mentira eso",
    ],
    "criterios": [
      "Afirma el ahorro del 15% al 20% con confianza",
      "No inventa testimonios de clientes",
      "Respuesta breve y segura",
    ],
  },
  {
    "id": "E25", "categoria": "Manejo de Objeciones", "peso": 2,
    "descripcion": "Múltiples objeciones en un solo mensaje.",
    "turns": [
      "Hola, soy Diana, tengo un Renault 4, el carburador está fallando y consume mucho",
      "¿Cuánto cuesta la instalación? ¿Tiene garantía? ¿Y si tengo problemas con el kit?",
    ],
    "criterios": [
      "Aborda cada pregunta sin omitir ninguna",
      "Menciona garantía de 1 año",
      "Menciona opciones de instalación",
      "Cierra con llamada a la acción",
    ],
  },

  # ── CATEGORÍA 5: Preguntas Fuera de Alcance ─────────────────
  {
    "id": "E26", "categoria": "Preguntas Fuera de Alcance", "peso": 1,
    "descripcion": "El cliente pregunta por sincronización del motor.",
    "turns": ["¿Ustedes hacen sincronizaciones de motor?"],
    "criterios": [
      "Confirma el servicio de sincronización brevemente (Cr 14 no 20-19, Cali)",
      "Redirige hacia el Kit 4K como solución principal",
      "No profundiza en sincronización",
    ],
  },
  {
    "id": "E27", "categoria": "Preguntas Fuera de Alcance", "peso": 1,
    "descripcion": "El cliente pregunta por productos no relacionados.",
    "turns": ["¿Venden bujías o aceites?"],
    "criterios": [
      "No inventa catálogo de productos",
      "Centra la conversación en el Kit 4K",
    ],
  },
  {
    "id": "E28", "categoria": "Preguntas Fuera de Alcance", "peso": 1,
    "descripcion": "El cliente hace una pregunta completamente ajena al negocio.",
    "turns": ["¿Cuál es la capital de Francia?"],
    "criterios": [
      "No responde la pregunta fuera del dominio",
      "Redirige hacia el Kit 4K de forma amable",
    ],
  },
  {
    "id": "E29", "categoria": "Preguntas Fuera de Alcance", "peso": 1,
    "descripcion": "El cliente pregunta por el costo de instalación en taller.",
    "turns": ["¿Cuánto cobran por instalar el kit en Cali?"],
    "criterios": [
      "No inventa precios de instalación",
      "Ofrece agendar llamada para detalles",
    ],
  },

  # ── CATEGORÍA 6: Reactivación / Silencios ───────────────────
  {
    "id": "E30", "categoria": "Reactivación / Silencios", "peso": 1,
    "descripcion": "Cliente retoma conversación después de un silencio.",
    "turns": [
      "Hola",
      "Oye, ¿sigues ahí? Me distraje un momento",
    ],
    "criterios": [
      "Retoma la conversación con amabilidad",
      "No reinicia el saludo completo innecesariamente",
      "Avanza hacia obtener el vehículo o el nombre",
    ],
  },
  {
    "id": "E31", "categoria": "Reactivación / Silencios", "peso": 2,
    "descripcion": "Cliente retoma después de recibir la recomendación.",
    "turns": [
      "Soy Juan, tengo un Renault 4, consume demasiada gasolina",
      "Perdón, me distraje. ¿Cuánto era el precio del kit?",
    ],
    "criterios": [
      "Retoma sin repetir toda la presentación",
      "Responde la pregunta puntual del precio",
      "Redirige al cierre de venta",
    ],
  },
  {
    "id": "E32", "categoria": "Reactivación / Silencios", "peso": 1,
    "descripcion": "Cliente pregunta el precio después de una pausa.",
    "turns": [
      "Soy Ana, tengo un Chevrolet Sprint, el encendido falla mucho",
      "Disculpa, ¿me puedes repetir cuánto vale?",
    ],
    "criterios": [
      "Responde el precio del kit consultando el brain",
      "No reinventa el precio",
      "Redirige hacia el cierre",
    ],
  },

  # ── CATEGORÍA 7: Cierre de Venta ────────────────────────────
  {
    "id": "E33", "categoria": "Cierre de Venta", "peso": 3,
    "descripcion": "El cliente decide comprar, elige Bancolombia y recibe los datos de pago.",
    "turns": [
      "Hola, soy Carlos, tengo un Toyota Corolla, consume demasiada gasolina",
      "Quiero comprarlo, envíenme el kit a Bogotá",
      "Bancolombia",
    ],
    "criterios": [
      "Presenta la cotización del Toyota Corolla antes del turno de compra",
      "Ante 'Quiero comprarlo', pregunta solo el banco de preferencia sin dar números de cuenta",
      "Tras 'Bancolombia', da los datos correctos: Cta ahorros 815-000002-28 y NIT 901.373.867",
    ],
  },
  {
    "id": "E34", "categoria": "Cierre de Venta", "peso": 3,
    "descripcion": "El cliente quiere instalación en el taller de Cali.",
    "turns": [
      "Soy Luisa, tengo un Mazda 323, el carro gasta mucha gasolina",
      "Prefiero llevarlo al taller en Cali",
    ],
    "criterios": [
      "Confirma la opción de instalación en Cali",
      "Solicita el número de celular del cliente",
      "Solicita el horario o coordina el siguiente paso",
    ],
  },
  {
    "id": "E35", "categoria": "Cierre de Venta", "peso": 2,
    "descripcion": "El cliente está en Medellín y pregunta por jornadas.",
    "turns": [
      "Hola, soy Hernando, tengo un Chevrolet Vitara, el motor falla y pierde potencia",
      "Estoy en Medellín, ¿cómo funciona la jornada allá?",
    ],
    "criterios": [
      "Menciona las jornadas de instalación en Bogotá y/o Medellín",
      "No inventa fechas ni horarios específicos",
      "Ofrece agendar llamada para detalles",
    ],
  },
  {
    "id": "E36", "categoria": "Cierre de Venta", "peso": 3,
    "descripcion": "El cliente acepta la llamada y da su número y horario.",
    "turns": [
      "Hola, soy Pilar, tengo un Nissan 720",
      "Bueno, pueden llamarme",
      "Mi número es 3001234567, llámame a las 4pm",
    ],
    "criterios": [
      "Solicita el número de teléfono y el horario en el mismo mensaje",
      "Confirma los datos recibidos del cliente",
      "Cierra el agendamiento de forma positiva",
    ],
  },
  {
    "id": "E37", "categoria": "Cierre de Venta", "peso": 2,
    "descripcion": "El cliente quiere comprar pero no quiere llamadas.",
    "turns": [
      "Hola, soy Camilo, tengo un Daihatsu Rocky, consume mucha gasolina",
      "No quiero llamadas, prefiero hacerlo todo por acá",
    ],
    "criterios": [
      "Ofrece WhatsApp o chat como alternativa a la llamada",
      "No abandona el proceso de cierre",
      "Solicita datos para coordinar el pedido sin llamada",
    ],
  },
  {
    "id": "E38", "categoria": "Cierre de Venta", "peso": 2,
    "descripcion": "El cliente pide tiempo para pensar.",
    "turns": [
      "Soy Gloria, tengo un Ford Festiva, el encendido es muy malo",
      "Déjame pensarlo y te escribo después",
    ],
    "criterios": [
      "No presiona de forma agresiva",
      "Mantiene la oferta activa",
      "Hace al menos un intento más de cierre o agendamiento",
    ],
  },

  # ── CATEGORÍA 8: Casos Extremos y Robustez ──────────────────
  {
    "id": "E39", "categoria": "Casos Extremos", "peso": 2,
    "descripcion": "El cliente escribe en inglés.",
    "turns": ["Hello, I need information about your carburetor products"],
    "criterios": [
      "Responde en español colombiano",
      "Mantiene el flujo estándar de apertura",
    ],
  },
  {
    "id": "E40", "categoria": "Casos Extremos", "peso": 2,
    "descripcion": "El cliente usa lenguaje ofensivo o agresivo.",
    "turns": ["Ese kit es una estafa, son unos ladrones"],
    "criterios": [
      "Responde con empatía, sin confrontación",
      "No responde con agresividad",
      "Intenta reencuadrar la objeción y continuar hacia el cierre",
    ],
  },

  # ── CATEGORÍA 9: Escenarios Nuevos (E41-E50) ────────────────
  {
    "id": "E41", "categoria": "Nuevos Escenarios", "peso": 2,
    "descripcion": "El cliente cambia de vehículo a mitad de conversación.",
    "turns": [
      "Hola, soy Álvaro, tengo un Renault 4",
      "Espera, en realidad el carro es de mi esposa. El mío es un Chevrolet Sprint",
    ],
    "criterios": [
      "Actualiza el vehículo sin confundirse",
      "Consulta el brain para el nuevo vehículo",
      "No mezcla datos del vehículo anterior",
    ],
  },
  {
    "id": "E42", "categoria": "Nuevos Escenarios", "peso": 3,
    "descripcion": "El cliente pregunta específicamente por pago contraentrega.",
    "turns": [
      "Hola, soy Beatriz, tengo un Mazda 323, consume mucha gasolina",
      "¿Hacen contra-entrega?",
    ],
    "criterios": [
      "Indica que NO tienen pago contraentrega",
      "Explica el proceso: cuenta empresarial Bancolombia o Davivienda + comprobante",
      "Menciona que el envío cuesta aproximadamente $20.000",
    ],
  },
  {
    "id": "E43", "categoria": "Nuevos Escenarios", "peso": 2,
    "descripcion": "El cliente menciona un producto más barato de la competencia.",
    "turns": [
      "Soy Diego, tengo un Chevrolet Vitara, pierde potencia y consume mucha gasolina",
      "Vi uno más barato en Mercado Libre a $80.000, ¿por qué el suyo es más caro?",
    ],
    "criterios": [
      "No baja el precio ni ofrece descuentos",
      "Diferencia el kit por calidad, completitud o adaptación",
      "Menciona que el kit incluye todos los accesorios necesarios",
    ],
  },
  {
    "id": "E44", "categoria": "Nuevos Escenarios", "peso": 2,
    "descripcion": "El cliente pide descuento directo.",
    "turns": [
      "Hola, soy Isabel, tengo un Toyota Corolla, el encendido falla y gasta mucha gasolina",
      "¿Me pueden dar un descuento? ¿10% o 15%?",
    ],
    "criterios": [
      "No ofrece descuentos no autorizados en el prompt",
      "Mantiene el precio del brain",
      "Reencuadra hacia el valor del producto",
    ],
  },
  {
    "id": "E45", "categoria": "Nuevos Escenarios", "peso": 3,
    "descripcion": "El cliente tiene un vehículo diésel que no aplica al kit.",
    "turns": ["Soy Ramón, tengo un Chevrolet Captiva diesel 2012"],
    "criterios": [
      "No inventa compatibilidad",
      "Usa la frase de validación si el vehículo no está en el brain",
      "No recomienda ningún kit sin consultar el brain",
    ],
  },
  {
    "id": "E46", "categoria": "Nuevos Escenarios", "peso": 1,
    "descripcion": "El cliente pide factura y datos fiscales.",
    "turns": [
      "Soy Natalia, tengo un Renault 4, el carro no arranca bien",
      "¿Me pueden dar factura? ¿Cuál es el NIT de la empresa?",
    ],
    "criterios": [
      "Puede dar el NIT 901.373.867 ya que está definido en el prompt",
      "Para procedimientos de facturación, deriva a llamada",
      "No abandona el flujo comercial",
    ],
  },
  {
    "id": "E47", "categoria": "Nuevos Escenarios", "peso": 3,
    "descripcion": "Flujo completo happy path de compra (multi-turno 6 pasos).",
    "turns": [
      "Hola",
      "Soy María",
      "Tengo un Chevrolet Sprint",
      "Tiene pérdida de potencia y consume mucho combustible",
      "¿Cómo es el proceso para comprarlo?",
      "Bueno me interesa, ¿me pueden llamar mañana a las 3pm?",
    ],
    "criterios": [
      "Sigue el orden: saludo → nombre → vehículo → diagnóstico → cotización → cierre",
      "Recomienda el kit con formato completo (valor, accesorios, beneficios)",
      "Al agendar llamada, pregunta el horario disponible en las próximas 24 horas",
      "No pierde el hilo en ningún turno",
    ],
  },
  {
    "id": "E48", "categoria": "Nuevos Escenarios", "peso": 2,
    "descripcion": "El cliente pregunta por el video de resultados de ahorro.",
    "turns": [
      "Hola, soy Tomás, tengo un Ford Festiva, consume mucha gasolina",
      "¿Y eso de que economiza de verdad funciona? ¿Tienen pruebas?",
    ],
    "criterios": [
      "Confirma el ahorro del 15% al 20%",
      "Comparte el link del video de resultados: https://www.youtube.com/watch?v=v3J1ICgggH8",
      "No inventa testimonios de clientes",
    ],
  },
  {
    "id": "E49", "categoria": "Nuevos Escenarios", "peso": 2,
    "descripcion": "Cliente que ya compró vuelve con una pregunta de soporte.",
    "turns": [
      "Hola, yo ya les compré el kit hace un mes para mi Daewoo Tico",
      "El carro sigue con marcha inestable, ¿qué hago?",
    ],
    "criterios": [
      "Muestra empatía con el cliente existente",
      "No inventa procedimientos de garantía no definidos en el prompt",
      "Ofrece agendar llamada con el equipo técnico o asesor",
    ],
  },
  {
    "id": "E50", "categoria": "Nuevos Escenarios", "peso": 3,
    "descripcion": "Cadena de tres objeciones encadenadas antes del cierre.",
    "turns": [
      "Soy Claudia, tengo un Mitsubishi Lancer, el carro consume mucha gasolina y pierde potencia",
      "Está muy caro",
      "Es que no sé instalarlo",
      "Déjame pensarlo un poco",
    ],
    "criterios": [
      "Maneja cada objeción con la respuesta definida en el prompt",
      "No abandona el flujo comercial tras cada objeción",
      "Hace al menos dos intentos de cierre a lo largo de la conversación",
      "Propone agendamiento de llamada al final",
    ],
  },
]


# ─────────────────────────────────────────────────────────────
# GENERACIÓN DE REPORTES
# ─────────────────────────────────────────────────────────────

def generar_reporte_json(resultados: list, ts: str) -> Path:
    ruta = Path(__file__).parent / f"reporte_resultados_{ts}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    return ruta


def generar_reporte_markdown(resultados: list, escenarios: list, ts: str) -> Path:
    ruta = Path(__file__).parent / f"reporte_optimizacion_{ts}.md"

    total = len(resultados)
    puntaje_global = (
        sum(r["evaluacion"]["puntaje"] * r["peso"] for r in resultados)
        / sum(r["peso"] for r in resultados)
        if resultados else 0
    )
    aprobados = sum(1 for r in resultados if r["evaluacion"]["puntaje"] >= 70)
    fallidos_lista = [r for r in resultados if r["evaluacion"]["puntaje"] < 70]

    # Agrupar fallos por categoría
    fallos_por_cat: dict = {}
    criterios_fallidos_global: list = []
    for r in resultados:
        cat = r["categoria"]
        if r["evaluacion"]["puntaje"] < 70:
            fallos_por_cat.setdefault(cat, []).append(r)
        criterios_fallidos_global.extend(r["evaluacion"].get("criterios_fallidos", []))

    # Criterios que fallan más frecuentemente
    from collections import Counter
    top_fallos = Counter(criterios_fallidos_global).most_common(10)

    lineas = [
        "# Reporte de Optimización — José, Agente Comercial",
        f"## Casa del Carburador | {ts.replace('_', ' ')}",
        "",
        "---",
        "",
        "## Resumen Ejecutivo",
        "",
        f"| Métrica | Valor |",
        f"|---------|-------|",
        f"| Escenarios ejecutados | {total} |",
        f"| **Puntaje global ponderado** | **{puntaje_global:.1f}/100** |",
        f"| Aprobados (≥70) | {aprobados}/{total} ({100*aprobados//total if total else 0}%) |",
        f"| Fallidos (<70) | {len(fallidos_lista)}/{total} |",
        "",
        "---",
        "",
        "## Resultados por Escenario",
        "",
        "| ID | Categoría | Puntaje | Estado |",
        "|----|-----------|---------|--------|",
    ]

    for r in resultados:
        estado = "✅ Aprobado" if r["evaluacion"]["puntaje"] >= 70 else "❌ Fallido"
        lineas.append(
            f"| {r['id']} | {r['categoria']} | {r['evaluacion']['puntaje']}/100 | {estado} |"
        )

    lineas += [
        "",
        "---",
        "",
        "## Escenarios Fallidos — Detalle",
        "",
    ]

    if fallidos_lista:
        for r in fallidos_lista:
            lineas += [
                f"### {r['id']} — {r['descripcion']}",
                f"**Puntaje:** {r['evaluacion']['puntaje']}/100",
                "",
                "**Criterios no cumplidos:**",
            ]
            for c in r["evaluacion"].get("criterios_fallidos", []):
                lineas.append(f"- {c}")
            lineas += [
                "",
                f"**Feedback del juez:** {r['evaluacion'].get('feedback', 'N/A')}",
                "",
                "**Última respuesta de José:**",
                f"> {r['conversacion'][-1]['content'][:400] if r['conversacion'] else 'N/A'}",
                "",
                "---",
                "",
            ]
    else:
        lineas.append("¡Todos los escenarios aprobados!")
        lineas.append("")

    lineas += [
        "## Criterios que Fallan con Más Frecuencia",
        "",
    ]
    if top_fallos:
        for criterio, count in top_fallos:
            lineas.append(f"- **({count}x)** {criterio}")
    else:
        lineas.append("Ningún criterio falló.")

    lineas += [
        "",
        "---",
        "",
        "## Sugerencias de Optimización del Prompt",
        "",
    ]

    # Sugerencias basadas en patrones de fallo
    sugerencias = []
    for criterio, count in top_fallos[:5]:
        if "saludo" in criterio.lower() or "hola" in criterio.lower() or "¡hola!" in criterio.lower():
            sugerencias.append(
                "**Saludo inicial:** Reforzar en el prompt que la frase de apertura "
                "debe ser EXACTAMENTE '¡Hola! Soy José del equipo Casa del Carburador 👋', "
                "sin añadir texto antes o después."
            )
        if "precio" in criterio.lower() or "valor" in criterio.lower() or "brain" in criterio.lower():
            sugerencias.append(
                "**Uso del brain:** Agregar instrucción explícita: 'ANTES de mencionar "
                "cualquier precio, SIEMPRE busca el vehículo en el brain. Si no lo encuentras, "
                "NO menciones ningún precio.'"
            )
        if "video" in criterio.lower():
            sugerencias.append(
                "**Videos:** Clarificar que solo se deben incluir videos que existan "
                "literalmente en el campo `video_instalacion` del brain. Si el campo "
                "es null o vacío, omitir completamente la línea del video."
            )
        if "llamada" in criterio.lower() or "teléfono" in criterio.lower() or "contacto" in criterio.lower():
            sugerencias.append(
                "**Agendamiento:** Reforzar que al momento del cierre, José SIEMPRE "
                "debe solicitar número de teléfono Y horario, no solo uno de los dos."
            )
        if "contraentrega" in criterio.lower() or "bancolombia" in criterio.lower():
            sugerencias.append(
                "**Pago:** La respuesta de pago contraentrega es larga y crítica. "
                "Considerar añadir un ejemplo de conversación en el prompt para que "
                "José replique exactamente la instrucción del prompt."
            )

    if not sugerencias:
        sugerencias.append(
            "El prompt funciona bien en general. Revisar los escenarios fallidos "
            "individualmente para ajustes puntuales."
        )

    # Eliminar duplicados manteniendo orden
    seen = set()
    for s in sugerencias:
        key = s[:60]
        if key not in seen:
            seen.add(key)
            lineas.append(f"- {s}")
            lineas.append("")

    lineas += [
        "",
        "---",
        f"*Generado por test_robot_jose.py — {ts}*",
    ]

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))
    return ruta


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Robot de pruebas — José, Agente Comercial")
    parser.add_argument("--escenario", help="ID del escenario a ejecutar (ej: E01)")
    parser.add_argument("--categoria", help="Nombre parcial de categoría (ej: Apertura)")
    parser.add_argument("--dry-run", action="store_true", help="Lista escenarios sin ejecutar")
    args = parser.parse_args()

    # Filtrar escenarios
    escenarios_a_ejecutar = ESCENARIOS[:]
    if args.escenario:
        escenarios_a_ejecutar = [e for e in ESCENARIOS if e["id"].upper() == args.escenario.upper()]
        if not escenarios_a_ejecutar:
            print(f"[ERROR] Escenario '{args.escenario}' no encontrado.")
            sys.exit(1)
    elif args.categoria:
        escenarios_a_ejecutar = [
            e for e in ESCENARIOS
            if args.categoria.lower() in e["categoria"].lower()
        ]
        if not escenarios_a_ejecutar:
            print(f"[ERROR] No hay escenarios para categoría '{args.categoria}'.")
            sys.exit(1)

    # Dry run: solo listar
    if args.dry_run:
        print(f"\n{'ID':<6} {'Categoría':<35} {'Peso':<6} Descripción")
        print("-" * 90)
        for e in escenarios_a_ejecutar:
            print(f"{e['id']:<6} {e['categoria']:<35} {e['peso']:<6} {e['descripcion'][:50]}")
        print(f"\nTotal: {len(escenarios_a_ejecutar)} escenarios")
        return

    # Cargar matriz y preparar sistema
    print("\n🔧  Cargando matriz de carburadores...")
    try:
        matriz = cargar_matriz()
        print(f"    ✓ {len(matriz)} vehículos cargados")
    except FileNotFoundError:
        print(f"[ERROR] No se encontró '{RUTA_MATRIZ}'. Asegúrate de que exista.")
        sys.exit(1)

    system_prompt = construir_system_prompt(matriz)
    client = anthropic.Anthropic()

    print(f"\n🤖  Modelo José  : {MODELO_JOSE}")
    print(f"⚖️   Modelo Juez  : {MODELO_JUEZ}")
    print(f"📋  Escenarios   : {len(escenarios_a_ejecutar)}")
    print("\n" + "=" * 60)

    resultados = []
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    for i, escenario in enumerate(escenarios_a_ejecutar, 1):
        print(f"\n[{i:02d}/{len(escenarios_a_ejecutar)}] {escenario['id']} — {escenario['descripcion'][:55]}")

        # Ejecutar conversación
        print("    ▶ Ejecutando conversación...", end="", flush=True)
        conversacion = ejecutar_escenario(client, escenario, system_prompt)
        print(" ✓")

        # Evaluar con el juez
        print("    ⚖  Evaluando con juez...", end="", flush=True)
        evaluacion = evaluar_escenario(client, escenario, conversacion)
        print(f" ✓  Puntaje: {evaluacion['puntaje']}/100")

        if evaluacion.get("criterios_fallidos"):
            for cf in evaluacion["criterios_fallidos"]:
                print(f"    ✗ {cf[:70]}")

        resultados.append({
            "id": escenario["id"],
            "categoria": escenario["categoria"],
            "descripcion": escenario["descripcion"],
            "peso": escenario["peso"],
            "conversacion": conversacion,
            "evaluacion": evaluacion,
        })

    # Calcular puntaje global
    puntaje_global = (
        sum(r["evaluacion"]["puntaje"] * r["peso"] for r in resultados)
        / sum(r["peso"] for r in resultados)
    )
    aprobados = sum(1 for r in resultados if r["evaluacion"]["puntaje"] >= 70)

    print("\n" + "=" * 60)
    print(f"\n📊  RESULTADOS FINALES")
    print(f"    Puntaje global ponderado : {puntaje_global:.1f}/100")
    print(f"    Aprobados (≥70)          : {aprobados}/{len(resultados)}")
    print(f"    Fallidos  (<70)          : {len(resultados)-aprobados}/{len(resultados)}")

    # Guardar reportes
    ruta_json = generar_reporte_json(resultados, ts)
    ruta_md   = generar_reporte_markdown(resultados, escenarios_a_ejecutar, ts)

    print(f"\n📁  Reportes guardados:")
    print(f"    {ruta_json.name}")
    print(f"    {ruta_md.name}")
    print()


if __name__ == "__main__":
    main()
