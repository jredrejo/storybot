# 🤖📚 Plan Técnico: Robot Cuentacuentos Local — Jetson Orin Nano Super

> **Versión:** 1.0 | **Hardware base:** NVIDIA Jetson Orin Nano Super Developer Kit (8 GB)  
> **Restricción crítica:** 100% offline — sin conexión a Internet en producción  
> **Audiencia:** Niños de 3 a 6 años, uso en aula por docentes

---

## Índice

1. [Resumen ejecutivo y restricciones del hardware](#1-resumen-ejecutivo-y-restricciones-del-hardware)
2. [Hardware completo recomendado](#2-hardware-completo-recomendado)
3. [Arquitectura web y red](#3-arquitectura-web-y-red)
4. [Arquitectura de software](#4-arquitectura-de-software)
5. [Modelos de IA locales](#5-modelos-de-ia-locales)
6. [Gestión de memoria y tiempos de carga](#6-gestión-de-memoria-y-tiempos-de-carga)
7. [Flujos de cada modalidad](#7-flujos-de-cada-modalidad)
8. [Adaptación del proyecto gemini_picturebook_generator](#8-adaptación-del-proyecto-gemini_picturebook_generator)
9. [Almacenamiento y gestión de contenidos](#9-almacenamiento-y-gestión-de-contenidos)
10. [Riesgos y decisiones críticas antes de comprar](#10-riesgos-y-decisiones-críticas-antes-de-comprar)
11. [Plan de desarrollo por fases](#11-plan-de-desarrollo-por-fases)
12. [Presupuesto completo — Compras en España](#12-presupuesto-completo--compras-en-españa)

---

## 1. Resumen ejecutivo y restricciones del hardware

### El Jetson Orin Nano Super en modo Super (MAXN, 25W)

| Característica | Valor |
|---|---|
| GPU | 1024 CUDA cores + 32 Tensor Cores (Ampere) |
| CPU | 6× Arm Cortex-A78AE @ hasta 1.7 GHz |
| RAM total | 8 GB LPDDR5 compartida CPU+GPU |
| Ancho de banda RAM | 102 GB/s (modo Super) |
| Rendimiento IA | 67 TOPS (INT8) |
| Almacenamiento base | MicroSD o SSD NVMe (recomendado) |
| SO | Ubuntu 20.04 / JetPack 6.2 |

### ⚠️ La restricción más importante del proyecto

**Los 8 GB de RAM son compartidos entre el SO, la aplicación y todos los modelos de IA.** Esto significa:

- El SO + aplicación Python consumen ~1,5–2 GB
- Solo quedan ~6 GB para modelos
- **Es imposible tener cargados simultáneamente el LLM + el modelo de imagen + el TTS**
- Los modelos deben cargarse y descargarse según la tarea activa

Este punto define completamente la arquitectura del sistema: **secuencial y basada en un gestor de modelos**.

---

## 2. Hardware completo recomendado

### Hardware base (ya disponible)

| Componente | Descripción |
|---|---|
| **Jetson Orin Nano Super 8GB** | Unidad central de procesamiento |

### Hardware adicional a comprar en España

| Componente | Modelo recomendado | Precio aprox. | Dónde comprar |
|---|---|---|---|
| **SSD NVMe M.2** | Samsung 870 EVO 500GB o Kingston NV3 500GB | 50–70€ | amazon.es |
| **Lector/escritor NFC USB** | ACR122U (ACS) | 35–55€ | shopnfc.com |
| **Tarjetas NFC en blanco** | NTAG213/215 PVC, pack de 50 | ~50€ | nfcstock.com |
| **Pantalla táctil 7"** | HAMTYSAN 7" 1024×600 IPS con altavoces duales | ~50€ | amazon.es |
| **Impresora pegatinas B&N** | Brother QL-800 | ~65€ | amazon.es |
| **Rollos adhesivos Brother** | DK-22205 (62mm×30m) | ~15€ | amazon.es |
| **Tira LED RGB** | Govee o similar 5V USB controlable, 1m | ~15–20€ | amazon.es |
| **Hub USB 3.0 alimentado** | Anker o similar (4 puertos, con fuente) | ~25–30€ | amazon.es |
| **Tarjeta MicroSD backup** | SanDisk 64GB Ultra A1 | ~12€ | amazon.es |

> **¿Por qué un SSD NVMe en vez de MicroSD?**  
> Los modelos de IA son archivos grandes (2–8 GB cada uno). Cargarlos desde una MicroSD puede tardar 30–60 segundos. Desde un SSD NVMe M.2 se reduce a 5–15 segundos. **Es la mejora de experiencia más importante que puedes hacer por ~60€.**

> **¿Por qué un hub USB alimentado?**  
> El lector NFC, la impresora Brother y otros periféricos juntos pueden superar la corriente que el Jetson puede dar por sus puertos USB. Un hub con fuente propia evita cortes y fallos misteriosos.

> **¿Por qué la tira LED?**  
> El proyecto menciona "luces de colores según la emoción del cuento". Con una tira LED 5V USB controlable por software (mediante scripts Python + librería como `rpi-ws281x` o directamente UART/USB), el LLM puede generar el color de ambiente de cada escena.

---

## 3. Arquitectura web y red

### 3.1 Punto de acceso WiFi externo — TP-Link TL-WR802N

#### ✅ Decisión: router mini externo en lugar de hotspot en el Jetson

La alternativa de crear el hotspot desde el propio Jetson (modo AP con tarjeta WiFi interna) tiene varios inconvenientes en la práctica:

- Requiere instalar y configurar una tarjeta WiFi M.2 adicional en el Jetson (~20–25€)
- El modo simultáneo cliente+AP (STA+AP) es inestable en Linux con la mayoría de tarjetas
- La configuración via `nmcli` puede romperse tras actualizaciones del sistema
- El Jetson tiene mejor uso para sus recursos de CPU que gestionar tráfico WiFi

**La solución más robusta, simple y económica es un mini router dedicado**: el **TP-Link TL-WR802N** (~18–20€ en Amazon.es), conectado al puerto Ethernet del Jetson por cable. El router crea la red WiFi `RobotCuentos`; el Jetson nunca necesita tarjeta WiFi.

#### TP-Link TL-WR802N — características relevantes para el proyecto

| Parámetro | Valor |
|---|---|
| **Precio** | ~18–20 € (Amazon.es) |
| **Tamaño** | 57×57×18 mm — cabe en cualquier sitio |
| **Alimentación** | MicroUSB 5V — se alimenta directamente del hub USB del robot |
| **Velocidad** | 300 Mbps (802.11n) — más que suficiente para tráfico local |
| **Modos** | Router, AP, Repetidor, Cliente, WISP |
| **Modo requerido** | **AP (Access Point)** — convierte Ethernet en WiFi |
| **Configuración** | Panel web sencillo — una sola vez, sin línea de comandos |

#### Modo de operación: Access Point (AP)

En modo AP, el TL-WR802N actúa como un switch inalámbrico: todo dispositivo WiFi conectado a la red `RobotCuentos` puede hablar directamente con el Jetson (que está conectado por cable al router). El Jetson actúa como servidor, sin gestionar nada de WiFi.

```
Configuración en panel web del TL-WR802N:
  Modo:        Access Point
  SSID:        RobotCuentos
  Contraseña:  cuentos2025 (WPA2)
  IP del AP:   192.168.0.254 (panel de admin del router)
  DHCP:        Activado (el router asigna IPs a los clientes WiFi)
```

#### Diagrama de red

```
┌─────────────────────────────────────────────────┐
│             RED WiFi "RobotCuentos"              │
│          (TP-Link TL-WR802N en modo AP)          │
│                                                  │
│  📱 Móvil docente    💻 Portátil docente         │
│       └──────────────────────┘                   │
│                    │ WiFi 2.4GHz                  │
│          ┌─────────▼──────────┐                  │
│          │  TP-Link TL-WR802N │ ← alimentado USB │
│          └─────────┬──────────┘                  │
│                    │ Cable Ethernet (RJ45)        │
│          ┌─────────▼──────────┐                  │
│          │      JETSON        │  192.168.0.1*    │
│          │      FastAPI       │  :8000           │
│          │      + Chromium    │  :80 (kiosk)     │
│          └────────────────────┘                  │
└─────────────────────────────────────────────────┘

* IP fija configurada en el Jetson via netplan o nmcli (Ethernet)
  Sin acceso a Internet — red completamente local
```

#### Configurar IP fija en el Jetson (Ethernet)

Para que la URL del panel de docentes sea siempre la misma, el Jetson necesita IP fija en su interfaz Ethernet:

```bash
# /etc/netplan/01-network-manager-all.yaml
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    eth0:
      dhcp4: no
      addresses: [192.168.0.1/24]
      gateway4: 192.168.0.254      # IP del TP-Link
      nameservers:
        addresses: [192.168.0.254]
```

```bash
sudo netplan apply
```

Con esto, la docente accede siempre a `http://192.168.0.1:8000/admin` desde su móvil o portátil conectados a la red WiFi `RobotCuentos`.

#### Tabla de acceso por dispositivo

| Dispositivo | Conexión | URL de acceso |
|---|---|---|
| Pantalla del robot (kiosk) | HDMI / localhost | `http://localhost/` |
| Móvil/portátil docente | WiFi `RobotCuentos` | `http://192.168.0.1:8000/admin` |
| Panel del router | WiFi `RobotCuentos` | `http://192.168.0.254` |

#### Ventajas del diseño con router externo

| Aspecto | Hotspot interno (Jetson) | Router externo (TP-Link) |
|---|---|---|
| Coste | +20–25€ tarjeta WiFi | +18–20€ router |
| Complejidad setup | Alta (nmcli, drivers, modo AP) | Muy baja (panel web, 5 min) |
| Estabilidad | Media (puede romperse con updates) | Muy alta (firmware dedicado) |
| Recursos Jetson | Consume CPU/RAM en gestión WiFi | Cero impacto en el Jetson |
| Mantenimiento | Requiere acceso SSH para reparar | Nada que mantener |
| M.2 Key E libre | No (ocupado por tarjeta WiFi) | **Sí (libre para otras expansiones)** |

> **Bonus:** Con el router externo, el slot M.2 Key E del Jetson queda libre para futuras expansiones (Bluetooth, LTE, etc.), y se puede actualizar el Jetson por Ethernet sin cambiar ninguna configuración de red.

#### Alimentación del TP-Link

El TL-WR802N se alimenta por MicroUSB a 5V/1A. Se puede conectar directamente al hub USB alimentado del proyecto, sin necesidad de enchufe adicional. Arranque automático al encender el robot.

---

### 3.2 FastAPI — servidor central de la aplicación

FastAPI sirve como backend único para **dos audiencias distintas**:

| Audiencia | Interfaz | URL | Propósito |
|---|---|---|---|
| **Niños** | Web en kiosk (Chromium pantalla completa) | `http://localhost/` | Interacción con los cuentos |
| **Docentes** | Web admin desde móvil/portátil | `http://192.168.0.1:8000/admin` | Gestión de contenidos |

#### Estructura de la API FastAPI

```
/api/
├── stories/
│   ├── GET  /                    # Listado de cuentos
│   ├── POST /upload              # Subir audio + metadatos
│   ├── GET  /{id}                # Obtener cuento por ID
│   └── DELETE /{id}             # Eliminar cuento
├── interactive/
│   ├── GET  /                    # Listado cuentos interactivos
│   └── POST /upload              # Subir árbol de decisión (JSON)
├── generate/
│   ├── POST /story               # Generar cuento con IA
│   └── GET  /status/{task_id}   # Progreso de generación (SSE)
├── nfc/
│   ├── GET  /read                # Leer tarjeta NFC activa (SSE)
│   └── POST /write               # Escribir UID en tarjeta
├── printer/
│   └── POST /print               # Enviar imagen a impresora
└── system/
    ├── GET  /status              # Estado del sistema (RAM, modelos)
    └── POST /led                 # Control de LEDs
```

#### Comunicación en tiempo real con Server-Sent Events (SSE)

Para que la interfaz del niño se actualice en tiempo real (progreso del cuento, narración, luces) sin polling constante, se usa **SSE** (Server-Sent Events), que es más sencillo que WebSockets y suficiente para flujos unidireccionales servidor→cliente:

```python
# Ejemplo: stream de generación de cuento
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

@app.post("/api/generate/story")
async def generate_story(data: StoryRequest):
    async def event_stream():
        async for token in ollama_stream(data.prompt):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

---

### 3.3 Interfaz del niño — Web en modo kiosk

La pantalla del dispositivo muestra Chromium en modo kiosk apuntando a `http://localhost/`. Esta es la interfaz principal con la que interactúan los niños.

#### Tecnología

- **Frontend:** HTML + CSS + JavaScript vanilla (o Vue.js ligero si se prefiere reactividad)
- **Servido por:** FastAPI con archivos estáticos (`StaticFiles`) o Nginx como proxy inverso
- **Sin instalación adicional:** El navegador es Chromium (preinstalado en JetPack/Ubuntu), se lanza en modo kiosk con:

```bash
# /etc/xdg/autostart/kiosk.desktop  (arranque automático)
[Desktop Entry]
Type=Application
Name=Robot Cuentacuentos
Exec=chromium-browser \
  --kiosk \
  --noerrdialogs \
  --disable-infobars \
  --no-first-run \
  --autoplay-policy=no-user-gesture-required \
  --app=http://localhost/
  --disable-session-crashed-bubble
```

#### Características de la UI del niño

```
┌─────────────────────────────────────────────┐
│   🎭  El Robot Cuentacuentos                │
│                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │  📻       │ │  🎮       │ │  ✨       │   │
│  │ Escuchar │ │Interactiv│ │ Inventar │   │
│  │ un cuento│ │          │ │ un cuento│   │
│  └──────────┘ └──────────┘ └──────────┘   │
│                                             │
│   [o acerca tu tarjeta mágica 🃏]          │
└─────────────────────────────────────────────┘
```

- Botones muy grandes (touch-friendly, mínimo 120×120px)
- Sin texto si los niños no leen aún — iconos + voz guía
- Animaciones CSS simples para feedback visual
- Audio del sistema narrado por el robot para cada interacción
- Bloqueo total: sin URL bar, sin gestos de salida, sin menú del sistema

#### Características del panel de docentes (`/admin`)

Accesible desde el móvil o portátil conectados al hotspot en `http://192.168.0.1:8000/admin`:

```
Panel de administración — Vista en móvil
┌─────────────────────────────┐
│ 🎙️ Añadir cuento narrado    │
│ ┌─────────────────────────┐ │
│ │ Título del cuento       │ │
│ └─────────────────────────┘ │
│ [📁 Seleccionar audio .mp3] │
│ Emoji portada: 🦁 🐉 🧚    │
│ Color LED: 🔴 🟡 🟢 🔵     │
│                             │
│   [✅ Guardar cuento]       │
│                             │
│ ─────────────────────────── │
│ 📚 Cuentos guardados (5)    │
│  • El León Valiente    [🗑️] │
│  • La Bruja Buena      [🗑️] │
│  • El Dragón Dormilón  [🗑️] │
│                             │
│ [🏷️ Escribir tarjeta NFC]   │
└─────────────────────────────┘
```

**Flujo de subida de cuento para docentes:**
1. Docente se conecta al WiFi `RobotCuentos` desde su móvil
2. Abre el navegador en `http://192.168.0.1:8000/admin`
3. Rellena el formulario: título, sube el audio, elige emoji y color de LED
4. Pulsa "Guardar" → el servidor guarda el audio en el SSD y actualiza `stories.json`
5. Acerca una tarjeta NFC en blanco al lector del robot
6. Pulsa "Escribir tarjeta NFC" → el sistema escribe el UID en la tarjeta
7. Listo — el cuento ya está disponible sin reiniciar nada

---

### 3.4 Consideraciones de seguridad del hotspot

Dado que es una red local en un aula:
- Contraseña WPA2 en el hotspot (no dejar abierta)
- El panel `/admin` protegido con contraseña básica HTTP (FastAPI `HTTPBasic`)
- La interfaz `/` (niños) es de solo lectura — no puede modificar contenidos
- No hay acceso a Internet, reduciendo el vector de ataque a cero

---

## 4. Arquitectura de software

### Visión general (arquitectura 100% web)

```
┌──────────────────────────────────────────────────────────────────┐
│  DISPOSITIVOS EXTERNOS (vía hotspot WiFi "RobotCuentos")         │
│  📱 Móvil docente  💻 Portátil docente                           │
│  → http://192.168.0.1:8000/admin                                   │
└──────────────────────────────┬───────────────────────────────────┘
                               │ HTTP / SSE
┌──────────────────────────────▼───────────────────────────────────┐
│                    JETSON ORIN NANO SUPER                        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              FASTAPI  (puerto 8000)                     │    │
│  │   /           → Interfaz niños (HTML estático)          │    │
│  │   /admin      → Panel docentes                          │    │
│  │   /api/*      → REST endpoints + SSE streams            │    │
│  └──────────────────────────┬────────────────────────────── ┘    │
│                             │                                    │
│  ┌──────────────────────────▼────────────────────────────────┐  │
│  │              GESTOR DE MODELOS (model_manager.py)         │  │
│  │   Cola de tareas asyncio — Carga/descarga modelos         │  │
│  └──────┬───────────────────┬──────────────────┬─────────────┘  │
│         │                   │                  │                 │
│    ┌────▼────┐         ┌─────▼──────┐    ┌─────▼──────┐        │
│    │  LLM    │         │  Piper TTS │    │  SD Image  │        │
│    │  Ollama │         │  (siempre) │    │  (demanda) │        │
│    └────┬────┘         └─────┬──────┘    └─────┬──────┘        │
│         │                   │                  │                │
│  ┌──────▼───────────────────▼──────────────────▼─────────────┐  │
│  │                   CAPA DE HARDWARE                         │  │
│  │   NFC (nfcpy)  │  Brother QL (brother_ql)  │  LEDs  │ 🔊  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │   CHROMIUM KIOSK → http://localhost/  (pantalla 7")       │   │
│  └───────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### Módulos principales

| Módulo | Tecnología | Responsabilidad |
|---|---|---|
| `main.py` | FastAPI | Servidor central, routing, SSE streams |
| `routers/stories.py` | FastAPI Router | CRUD de cuentos narrados |
| `routers/admin.py` | FastAPI Router | Panel de administración docentes |
| `routers/generate.py` | FastAPI Router + asyncio | Generación IA con streaming |
| `routers/nfc.py` | FastAPI Router | Lectura/escritura NFC via API |
| `model_manager.py` | Python asyncio | Carga/descarga modelos, gestión RAM |
| `nfc_handler.py` | Python + `nfcpy` | Lectura/escritura hardware NFC |
| `story_generator.py` | Ollama Python API | Generación de cuentos con LLM local |
| `tts_engine.py` | Piper TTS subprocess | Texto a voz en español |
| `image_generator.py` | Diffusers / ONNX | Generación de imágenes lineales |
| `printer_handler.py` | `python-brother-ql` | Envío a impresora Brother |
| `led_controller.py` | pyserial / USB HID | Control de luces RGB |
| `audio_player.py` | pygame / simpleaudio | Reproducción de audio pregrabado |
| `content_manager.py` | JSON + filesystem | Gestión de cuentos y assets locales |
| `static/` | HTML + CSS + JS | UI niños y panel admin (servidos por FastAPI) |

### Stack tecnológico

```
Sistema operativo:    Ubuntu 20.04 + JetPack 6.2
WiFi hotspot:         Intel AX210NGW + nmcli (NetworkManager)
Servidor web/API:     FastAPI + Uvicorn (Python 3.10)
UI niños:             HTML5 + CSS3 + JavaScript (Chromium kiosk)
UI docentes:          HTML5 responsive (acceso móvil vía hotspot)
Runtime modelos:      Ollama (LLM) + Piper TTS + Diffusers ONNX
Audio:                pygame / pydub + simpleaudio
NFC:                  nfcpy (compatible con ACR122U)
Impresora:            brother_ql Python library
LEDs:                 USB HID o pyserial
Gestión procesos:     systemd (autoarranque FastAPI + Chromium kiosk)
Tiempo real:          Server-Sent Events (SSE) para streaming IA
```

---

## 5. Modelos de IA locales

### 5.1 LLM — Generación de cuentos en español

#### ✅ Opción recomendada: Qwen 2.5 3B Instruct (Q4_K_M)

| Parámetro | Valor |
|---|---|
| **Origen** | Alibaba Cloud / Qwen Team (open-source, Apache 2.0 para 7B; Qwen Research License para 3B) |
| **Tamaño en disco** | ~1,9 GB (Q4_K_M) |
| **RAM consumida** | ~2,0 GB |
| **Velocidad en Jetson Orin Nano Super** | ~35–45 tok/s (modo MAXN) |
| **Tiempo para un cuento de 300 palabras** | **30–45 segundos** |
| **Calidad en español** | Muy buena — entrenado en 18T tokens multilingüe |
| **Disponible en Ollama** | `ollama pull qwen2.5:3b-instruct-q4_K_M` |

**¿Por qué Qwen 2.5 3B en lugar de Mistral 7B?**

Tres razones concretas para esta tarea:

1. **Velocidad**: 30–45 seg por cuento frente a 90–120 seg de Mistral 7B. Para un niño de 3 años, esa diferencia es decisiva.

2. **Huella de RAM**: ~2 GB frente a ~4,5 GB. Libera 2,5 GB adicionales que cambian la arquitectura del sistema (ver sección 6): SD 1.5 + LLM pueden mantenerse en RAM simultáneamente.

3. **Suficiencia para la tarea**: los cuentos son cortos (~300 palabras), vocabulario simple, estructura predecible. Qwen 2.5 3B es más que suficiente, con mejor seguimiento de instrucciones que Mistral 7B en benchmarks actuales del tamaño 3B.

**Ruta de escalado clara**: Si las pruebas con docentes revelan que la calidad narrativa es insuficiente, una sola línea en Ollama — `qwen2.5:7b-instruct-q4_K_M` — escala sin tocar ningún otro módulo.

**Prompt de generación de cuentos:**
```
Eres un narrador de cuentos infantiles. Crea un cuento corto
(máximo 300 palabras) en español, apropiado para niños de 3 a 6 años,
con protagonista: [X], antagonista: [Y], escenario: [Z].

El cuento debe:
- Usar vocabulario simple y frases muy cortas
- Tener final feliz y positivo
- Transmitir un valor (amistad, valentía o bondad)
- No incluir violencia ni elementos de miedo
- Dividirse en tres párrafos: introducción, nudo, desenlace

Solo devuelve el texto del cuento. Sin títulos, sin comentarios.
```

#### Alternativa validada: Llama 3.2 3B Instruct

Con soporte oficial de español (entre 8 idiomas soportados), benchmarks similares al Qwen 2.5 3B y licencia más permisiva. Opción equivalente si se prefiere el ecosistema Meta.
`ollama pull llama3.2:3b-instruct`

---

### 5.2 TTS — Texto a voz en español

#### ✅ Opción recomendada: Piper TTS con voces es_ES

| Parámetro | Valor |
|---|---|
| **Tamaño del modelo** | 60–120 MB por voz |
| **RAM consumida** | < 400 MB |
| **Velocidad** | **Tiempo real — menos de 500 ms por párrafo** |
| **Calidad** | Muy buena con `es_ES-sharvard-medium` |
| **Coexistencia con LLM** | ✅ Siempre cargado — insignificante en RAM |

Voces disponibles: `es_ES-sharvard-medium`, `es_ES-carlfm-x_low`, `es_ES-davefx-medium`

Las modalidades 1 y 2 usan audio pregrabado por las docentes. Piper solo actúa en la modalidad 3.

---

### 5.3 Generación de imágenes — Dibujos lineales para colorear

#### ✅ Opción recomendada: SD 1.5 + LCM LoRA + Lineart LoRA (stack de dos LoRAs)

**La distinción fundamental**: un LoRA de estilo (storybook, lineart) NO mejora la velocidad. Solo cambia el aspecto visual. La aceleración viene de reducir los pasos de difusión, lo que hace el **LCM LoRA** (Latent Consistency Model LoRA). Ambos pueden apilarse simultáneamente sobre el mismo checkpoint sin coste adicional de RAM relevante.

```
Checkpoint base: Lykon/dreamshaper-7
  ├─ LoRA A: Coloring Book Lineart  (~100 MB)  → estilo visual
  └─ LoRA B: LCM LoRA sdv1-5       (135 MB)   → aceleración (4–8 steps)
```

**Benchmarks y estimación en Jetson:**

| Configuración | Steps | RTX 3070 (referencia) | **Jetson Orin Nano (estimado)** |
|---|---|---|---|
| SD 1.5 vanilla (20 steps) | 20 | ~8–12 s | 3–8 min |
| SD 1.5 + LCM LoRA (4 steps) | 4 | ~2–4 s | **40–90 seg** ✓ |
| SD 1.5 + Lineart LoRA + LCM LoRA | 4–6 | ~3–5 s | **50–110 seg** ✓ |

**Componentes:**

| Componente | Fuente | Peso | Licencia |
|---|---|---|---|
| Checkpoint base | `Lykon/dreamshaper-7` (HuggingFace) | ~2 GB | Open |
| LCM LoRA (velocidad) | `latent-consistency/lcm-lora-sdv1-5` (HF) | 135 MB | MIT |
| Lineart LoRA (estilo) | Civitai / HuggingFace "coloring book lineart SD 1.5" | ~80–150 MB | Variable |

**Configuración de inferencia:**
```python
from diffusers import DiffusionPipeline, LCMScheduler
import torch

pipe = DiffusionPipeline.from_pretrained(
    "Lykon/dreamshaper-7", torch_dtype=torch.float16
).to("cuda")

pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
pipe.load_lora_weights("latent-consistency/lcm-lora-sdv1-5", adapter_name="lcm")
pipe.load_lora_weights("ruta/coloring_book_lora.safetensors", adapter_name="style")
pipe.set_adapters(["lcm", "style"], adapter_weights=[1.0, 0.8])

# IMPORTANTE: con LCM, guidance_scale debe ser 1.0–2.0
image = pipe(
    prompt="coloring book page, black and white line art, simple outlines, "
           "[personaje y escena], thick bold lines, no shading, "
           "white background, children illustration, printable",
    negative_prompt="color, shading, realistic, photograph, gray",
    num_inference_steps=6,
    guidance_scale=1.5,
    width=512, height=512
).images[0]
```

**Banco de imágenes pre-generadas (v1.0)**: incluso con LCM LoRA, 50–110 segundos puede ser demasiado para aula. La estrategia de v1.0 sigue siendo pre-generar en PC un banco de ~200 imágenes y seleccionar en tiempo real. La generación en vivo → v1.5 una vez validada la estabilidad del pipeline.

---

### 5.4 Resumen de modelos y huella de memoria

| Modelo | RAM | Disco | Estado |
|---|---|---|---|
| Piper TTS (es_ES) | ~400 MB | ~100 MB | **Siempre cargado** |
| Qwen 2.5 3B Q4_K_M | ~2,0 GB | ~1,9 GB | Carga bajo demanda (modalidad 3) |
| SD 1.5 + LoRAs | ~2,8 GB | ~2,3 GB | Carga bajo demanda (generación imagen) |

**Conclusión de memoria con la nueva arquitectura:**
```
RAM disponible total:     8,0 GB
SO + FastAPI + app:       1,5 GB
Piper TTS (siempre):      0,4 GB
Buffer + sistema:         0,8 GB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Disponible para modelos:  5,3 GB

→ Qwen 2.5 3B (2,0 GB) + SD 1.5 + LoRAs (2,8 GB) = 4,8 GB ✓ CABEN JUNTOS
→ Mistral 7B (4,5 GB) + SD 1.5 (2,8 GB) = 7,3 GB ✗ NO CABEN

🔑 Cambiar de Mistral 7B a Qwen 2.5 3B desbloquea la posibilidad de mantener
   el LLM y el modelo de imagen cargados simultáneamente, eliminando los
   tiempos de carga/descarga entre la narración y la generación de imagen.
```

---

## 6. Gestión de memoria y tiempos de carga

**Con Qwen 2.5 3B, la arquitectura de memoria cambia radicalmente:**

```
                 ARQUITECTURA ANTERIOR (Mistral 7B)
                 ───────────────────────────────────
  [SO 1.5GB] [Piper 0.4GB] [          Mistral 7B 4.5GB          ] [buf]
                           → Solo el LLM ya ocupa casi todo
                           → LLM y SD 1.5 NO pueden coexistir

                 ARQUITECTURA NUEVA (Qwen 2.5 3B)
                 ─────────────────────────────────
  [SO 1.5GB] [Piper 0.4GB] [Qwen 3B 2.0GB] [SD+LoRAs 2.8GB] [1.3 libre]
                           → LLM y modelo de imagen COEXISTEN ✓
                           → Cero tiempo de carga entre narración e imagen
```

### Flujo de carga/descarga de modelos

```
INICIO
  └─ Piper TTS se carga al arrancar (permanece en RAM siempre)
  
MODALIDAD 1 — Cuento narrado:
  └─ No se necesita ningún modelo IA
     Solo: reproduce audio pregrabado + Piper TTS para posibles textos extra
     Tiempo total: instantáneo

MODALIDAD 2 — Cuento interactivo:
  └─ No se necesita LLM (historia predefinida)
     Piper TTS ya cargado
     Tiempo total: instantáneo

MODALIDAD 3 — Cuento inventado por IA:
  1. Cargar Mistral 7B ............... 15–25 segundos (desde SSD NVMe)
  2. Generar cuento (400 palabras) ... 90–120 segundos
  3. Narrar con Piper TTS ............ tiempo real, por fragmentos
  4. Descargar Mistral 7B ............ 2–3 segundos
  5. Cargar SD 1.5 ................... 20–30 segundos
  6. Generar imagen lineal ........... 3–8 minutos
  7. Procesar imagen (B&N) ........... 5 segundos
  8. Enviar a impresora .............. 15–30 segundos
  9. Descargar SD 1.5 ................ 2–3 segundos
  ─────────────────────────────────────────────────
  TIEMPO TOTAL ESTIMADO MODALIDAD 3: ~10–12 minutos
```

> **Importante para la UX:** Los pasos 3 y 6 pueden solaparse parcialmente. Mientras el cuento se narra (paso 3), se puede iniciar la carga y generación de imagen en background (pasos 5–6). Con este solapamiento, el tiempo percibido por el niño se reduce.

### Estrategia para minimizar la espera percibida

1. **Cuento primero, imagen después:** Narrar el cuento completo en voz alta mientras la imagen se genera en background. El niño no espera mirando una pantalla en negro.
2. **Animación de "el robot está pensando":** Mostrar una animación de espera divertida y con los LEDs en modo "pensando" (color azul pulsante).
3. **Mensaje de audio:** El robot puede decir con Piper TTS: *"¡Voy a dibujar la historia mientras te la cuento! Al final te daré tu dibujo para colorear."*
4. **Pre-generación offline del banco de imágenes** para la v1.0 (ver alternativa B anterior).

---

## 7. Flujos de cada modalidad

### Modalidad 1 — Cuento narrado

```
NFC card detectada (polling del backend vía /api/nfc/read SSE)
  └─ Frontend recibe evento SSE con el UID de la tarjeta
  └─ Frontend llama GET /api/stories/{uid}
  └─ Backend devuelve metadatos del cuento (título, portada, LED color)
  └─ Frontend muestra portada + animación de carga
  └─ Frontend llama POST /api/system/led con el color del cuento
  └─ Frontend hace GET /api/stories/{uid}/audio → stream de audio
  └─ Reproducción en el <audio> tag del HTML5
  └─ Fin: pantalla de agradecimiento con animación
```

**Interfaz docente para añadir nuevos cuentos:**
La docente accede desde su móvil a `http://192.168.0.1:8000/admin`, rellena un formulario web sencillo (título, audio, emoji, color LED) y pulsa guardar. Sin comandos, sin desmontar nada.

### Modalidad 2 — Cuento interactivo

```
Selección de cuento en pantalla (o tarjeta NFC)
  └─ Cargar árbol de decisiones del cuento (JSON)
  └─ Reproducir fragmento de audio
  └─ Mostrar opciones en pantalla (2 botones grandes)
  └─ Niño toca su opción
  └─ LEDs cambian de color según la emoción de la escena
  └─ Reproducir siguiente fragmento según elección
  └─ Repetir hasta el final
  └─ Mostrar pantalla de "FIN" con ilustración
```

**Estructura de datos para cuentos interactivos:**
```json
{
  "id": "cuento_leon",
  "titulo": "El León Valiente",
  "escenas": {
    "inicio": {
      "audio": "leon_inicio.mp3",
      "texto": "El pequeño León se encontró con un río...",
      "led_color": "#FF8C00",
      "opciones": [
        {"texto": "Cruzar el río", "siguiente": "escena_rio"},
        {"texto": "Buscar otro camino", "siguiente": "escena_bosque"}
      ]
    },
    "escena_rio": { ... },
    "escena_bosque": { ... }
  }
}
```

### Modalidad 3 — Cuento inventado por IA

```
Frontend niños: Pantalla de selección (botones grandes touch)
  ├─ Protagonista (iconos: dragón, niña, robot, hada)
  ├─ Antagonista (lobo, bruja, nube, dragón dormilón)
  └─ Escenario (bosque, castillo, espacio, ciudad)

  └─ Frontend POST /api/generate/story → recibe task_id
  └─ Frontend abre SSE en GET /api/generate/status/{task_id}
  └─ Animación "El robot inventa tu cuento..." + LEDs azul pulsante

  [BACKEND asyncio:]
  1. model_manager carga Mistral 7B (~15–25s)
  2. Genera cuento en streaming → emite tokens por SSE
  3. Frontend recibe tokens → los muestra en pantalla en tiempo real
  4. Cada párrafo completo → POST interno a Piper TTS → audio → SSE "audio_ready"
  5. Frontend reproduce audio párrafo a párrafo

  [BACKGROUND, en paralelo con paso 3–5:]
  6. model_manager descarga Mistral → carga SD 1.5 (~20–30s)
  7. Genera imagen lineal → emite progreso por SSE
  8. Cuando imagen lista → SSE "image_ready" con URL de la imagen
  9. Frontend muestra imagen + botón "Imprimir mi dibujo"
  10. POST /api/printer/print → impresora Brother
```

**Prompt de generación de cuentos para niños de 3-6 años:**
```
Eres un narrador de cuentos infantiles. Crea un cuento corto 
(máximo 300 palabras) en español, apropiado para niños de 3 a 6 años, 
con el siguiente protagonista: [PROTAGONISTA], que se enfrenta a: [ANTAGONISTA], 
en el escenario de: [ESCENARIO].

El cuento debe:
- Usar vocabulario simple y frases cortas
- Tener un final feliz y positivo
- Transmitir un valor como la amistad, el valor o la bondad
- No incluir violencia ni elementos que puedan asustar
- Estar estructurado en: introducción, nudo, desenlace

Solo devuelve el texto del cuento, sin títulos ni comentarios.
```

---

## 8. Adaptación del proyecto gemini_picturebook_generator

El proyecto original de referencia (`angrysky56/gemini_picturebook_generator`) usa:
- **Gemini API** (Google, cloud) para generación de texto
- **Gemini API** para generación de imágenes
- Flask para UI web
- Exportación a HTML/PDF

### Qué conservar del proyecto original

| Elemento del original | Adaptación local |
|---|---|
| Estructura de datos de la historia (escenas) | ✅ Reutilizar el esquema JSON de escenas |
| Lógica de construcción de prompts | ✅ Adaptar para Mistral/Ollama |
| Generación de HTML/PDF del cuento | ✅ Útil para el manual didáctico |
| Templates de historia | ✅ Adaptar al español y a niños 3-6 años |

### Qué reemplazar completamente

| Elemento del original | Reemplazo |
|---|---|
| `GOOGLE_API_KEY` + Gemini API | Ollama local (Mistral) |
| Generación de imágenes Gemini | Stable Diffusion local (ONNX) |
| Flask web UI | PyQt5 / Tkinter (interfaz táctil local) |
| MCP server | No necesario — pipeline local directo |
| `enhanced_story_generator.py` | `story_generator.py` con Ollama Python API |

### Esquema de migración recomendado

```python
# Original (Gemini API)
import google.generativeai as genai
response = model.generate_content(prompt)

# Adaptación local (Ollama)
import ollama
response = ollama.generate(
    model='mistral:7b-instruct-q4_K_M',
    prompt=prompt,
    stream=True  # para narración en tiempo real
)
```

---

## 9. Almacenamiento y gestión de contenidos

### Estructura de directorios en el SSD

```
/home/robot/
├── models/
│   ├── ollama/          # Modelos LLM gestionados por Ollama
│   ├── piper/           # Modelos de voz Piper
│   └── stable_diffusion/ # Modelos SD en ONNX
├── content/
│   ├── stories/         # Cuentos narrados (JSON + audio)
│   ├── interactive/     # Cuentos interactivos (árboles JSON)
│   ├── images/          # Banco de imágenes pre-generadas
│   └── characters/      # Imágenes de personajes para UI
├── generated/
│   ├── ai_stories/      # Cuentos generados por IA (guardados)
│   └── print_queue/     # Cola de impresión
├── app/
│   └── [código fuente del proyecto]
└── logs/
```

### Gestión de tarjetas NFC

Cada tarjeta NFC almacena únicamente un **UID** (identificador único de 4–7 bytes). El sistema mantiene una base de datos local (`stories.json`) que mapea UID → cuento. Esto permite:
- Añadir nuevos cuentos sin reprogramar tarjetas existentes
- Reutilizar tarjetas con solo actualizar el JSON
- La docente puede gestionar el catálogo sin conocimientos técnicos

---

## 10. Riesgos y decisiones críticas antes de comprar

### ⚠️ Riesgo 1 — Tiempo de generación de imagen inaceptable para el aula
**Problema:** 3–8 minutos para una imagen puede frustrar a niños de 3 años.  
**Decisión:** Para la v1.0, usar banco de imágenes pre-generadas. La generación en tiempo real se implementa como mejora en v2.0.  
**Impacto en compras:** Ninguno — no cambia el hardware necesario.

### ⚠️ Riesgo 2 — Calidad del español en Mistral 7B
**Problema:** El modelo puede generar texto con galicismos o estructuras poco naturales en español.  
**Decisión:** Probar antes de desplegar con 20–30 cuentos generados y evaluados por las docentes.  
**Mitigación:** El prompt incluye instrucciones muy específicas de estilo y vocabulario.

### ⚠️ Riesgo 3 — Estabilidad del sistema en uso continuo por niños
**Problema:** Los niños no cuidan el hardware. Pantalla táctil, tarjetas NFC, cables.  
**Decisión:**  
- Pantalla dentro de carcasa robusta (impresión 3D o caja de madera)
- Tarjetas NFC laminadas
- Sistema en modo kiosko (no se puede salir de la aplicación)
- Arranque automático con systemd al encender

### ⚠️ Riesgo 4 — Brother QL-800 y drivers Linux
**Problema:** La librería `brother_ql` para Python funciona bien, pero imprimir imágenes (no solo texto) requiere configuración específica.  
**Decisión:** Probar el pipeline completo (Python → imagen PNG → conversión → impresora) antes de integrar en el sistema principal.

### ⚠️ Riesgo 5 — Temperatura y consumo eléctrico del Jetson
**Problema:** En modo MAXN (25W), el Jetson genera calor. En una caja cerrada puede sobrecalentarse.  
**Decisión:** Asegurarse de que la carcasa tiene ventilación pasiva o activa (pequeño ventilador USB). El Jetson tiene gestión térmica automática, pero si se estrangula el rendimiento cae drásticamente.

### ✅ Decisión sobre SSD vs MicroSD
**Decisión firme: SSD NVMe M.2.** La reducción en tiempo de carga de modelos (de 45s a 12s) es crítica para la experiencia de aula. El Jetson Orin Nano Super Developer Kit tiene ranura M.2 Key-M 2280 — instalar un SSD antes de cualquier desarrollo.

---

### ⚠️ Riesgo 6 — La tarjeta WiFi M.2 Key E no viene en el kit oficial
**Problema:** El Developer Kit oficial NVIDIA no incluye tarjeta WiFi — el slot M.2 Key E está vacío.  
**Decisión:** Comprar tarjeta Intel AX210NGW (~22€) y antenas IPEX MHF4 por separado antes de empezar.  
**Verificación:** Comprobar que el kit adquirido incluye o no la tarjeta antes de hacer el pedido.

### ⚠️ Riesgo 7 — NFC leído en polling vs. interrupción hardware
**Problema:** `nfcpy` puede necesitar polling activo (bucle Python cada 100–200ms). En un servidor FastAPI asyncio, esto debe ejecutarse en un hilo separado para no bloquear el event loop.  
**Decisión:** El `nfc_handler.py` se ejecuta en un `asyncio.to_thread()` o `ThreadPoolExecutor`, enviando eventos al frontend vía SSE cuando detecta una tarjeta.

## 11. Plan de desarrollo por fases

### Fase 0 — Setup (2–3 semanas)
- [ ] Instalar JetPack 6.2 + activar modo Super (MAXN)
- [ ] Instalar SSD NVMe M.2 y migrar el sistema
- [ ] Instalar tarjeta WiFi Intel AX210NGW + verificar reconocimiento
- [ ] Configurar hotspot con nmcli (`RobotCuentos`) + autoarranque
- [ ] Instalar Ollama y verificar inferencia de Mistral 7B
- [ ] Instalar Piper TTS + voz española + prueba de audio
- [ ] Probar lector NFC (ACR122U) + `nfcpy`
- [ ] Probar Brother QL-800 + `brother_ql` en Python
- [ ] Instalar Stable Diffusion ONNX + primer test de imagen
- [ ] Evaluar tiempos reales en hardware

### Fase 1 — MVP Modalidad 1: Cuento narrado (3–4 semanas)
- [ ] Estructura del proyecto FastAPI + Uvicorn
- [ ] Endpoints `/api/stories` (CRUD básico)
- [ ] Panel admin HTML para subir cuentos (accesible desde móvil vía hotspot)
- [ ] Frontend niños básico (HTML kiosk) con botones de selección
- [ ] Integración NFC → SSE → frontend
- [ ] Reproducción de audio HTML5 (`<audio>` tag)
- [ ] Autoarranque: systemd para FastAPI + Chromium kiosk
- [ ] Grabar y cargar 5 cuentos de prueba con las docentes
- [ ] Prueba en aula real con retroalimentación

### Fase 2 — Modalidad 2: Cuento interactivo (2–3 semanas)
- [ ] Endpoints `/api/interactive`
- [ ] Frontend de árbol de decisión (botones de elección touch)
- [ ] Control de LEDs por API (`/api/system/led`)
- [ ] Crear 2–3 cuentos interactivos piloto

### Fase 3 — Modalidad 3: Cuento inventado por IA (4–6 semanas)
- [ ] `model_manager.py` con asyncio + carga/descarga de modelos
- [ ] Endpoint `/api/generate/story` con SSE streaming
- [ ] Frontend de selección de personajes + progreso SSE en tiempo real
- [ ] Pipeline Piper TTS → audio párrafo a párrafo via SSE
- [ ] Banco de imágenes pre-generadas + selección automática
- [ ] Endpoint `/api/printer/print` + integración Brother
- [ ] Pruebas de estrés y estabilidad

### Fase 4 — Generación de imagen en tiempo real (opcional, v2.0)
- [ ] Optimización SD con TensorRT
- [ ] Solapamiento real narración + generación (paralelo asyncio)
- [ ] Evaluación de tiempos en producción con niños reales

### Fase 5 — Pulido y despliegue (2 semanas)
- [ ] Hardening del panel admin (autenticación HTTP Basic)
- [ ] UI del niño en modo kiosk completo (sin gestos de escape)
- [ ] Carcasa física para el robot (ventilación obligatoria)
- [ ] Manual de uso para docentes
- [ ] Formación a las profesoras

---

## 12. Presupuesto completo — Compras en España

Todos los precios incluyen IVA (21%). Los precios son orientativos y pueden variar.

### 12.1 Hardware principal

| # | Componente | Modelo recomendado | Precio (IVA inc.) | Tienda | Enlace / Referencia |
|---|---|---|---|---|---|
| 1 | **Jetson Orin Nano Super 8GB** | NVIDIA Developer Kit — ref. 945-13766-00 | **399,30 €** | bricogeek.com | [Ver producto](https://tienda.bricogeek.com/accesorios-robotica/2065-nvidia-jetson-orin-nano-super-developer-kit-8gb.html) *(envío gratis)* |
| 2 | **SSD NVMe M.2 2280** | Kingston NV3 500GB PCIe 4.0 (SNV3S/500G) | **~36 €** | amazon.es | Buscar "Kingston NV3 500GB M.2" |
| 3 | **Mini router WiFi** | TP-Link TL-WR802N (modo AP) | **~19 €** | amazon.es | Buscar "TP-Link TL-WR802N" |
| 4 | **Lector NFC USB** | ACS ACR122U | **~45 €** | shopnfc.com / amazon.es | Buscar "ACR122U lector NFC" |
| 5 | **Tarjetas NFC en blanco** | NTAG213 PVC × 50 unidades | **~45 €** | nfcstock.com / amazon.es | Buscar "tarjetas NFC NTAG213" |
| 6 | **Pantalla táctil 7"** | HAMTYSAN 7" IPS 1024×600 HDMI + táctil USB | **~50 €** | amazon.es | Buscar "HAMTYSAN 7 inch HDMI touch" |
| 7 | **Altavoces USB** | Cualquier altavoz estéreo USB/3.5mm compacto | **~15 €** | amazon.es | Buscar "altavoz USB compacto pequeño" |
| 8 | **Impresora pegatinas B&N** | Brother QL-800 (62mm, USB, sin tinta) | **~65 €** | amazon.es | Buscar "Brother QL-800" |
| 9 | **Rollos papel adhesivo** | Brother DK-22205 62mm continuo × 2 rollos | **~30 €** | amazon.es | Buscar "Brother DK-22205" |
| 10 | **Tira LED RGB** | Govee LED USB 1m controlable | **~18 €** | amazon.es | Buscar "Govee LED USB 1m" |
| 11 | **Hub USB alimentado** | Hub 4 puertos USB 3.0 con alimentación externa | **~22 €** | amazon.es | Buscar "hub USB alimentado 4 puertos" |
| 12 | **Cable Ethernet** | Cable RJ45 Cat6 1m (Jetson ↔ TP-Link) | **~5 €** | amazon.es / cualquier tienda | |
| 13 | **MicroSD de backup** | SanDisk Ultra A1 64GB (para imagen de emergencia) | **~12 €** | amazon.es | Buscar "SanDisk Ultra microSD 64GB A1" |

---

### 12.2 Resumen por categoría

| Categoría | Subtotal |
|---|---|
| Computación principal (Jetson + SSD) | **435,30 €** |
| Red WiFi (TP-Link + cable Ethernet) | **24 €** |
| Interacción (NFC lector + 50 tarjetas) | **90 €** |
| Pantalla + audio (pantalla 7" + altavoces) | **65 €** |
| Impresión pegatinas (impresora + 2 rollos) | **95 €** |
| Iluminación + conectividad (LEDs + hub USB) | **40 €** |
| Almacenamiento secundario (microSD) | **12 €** |
| **TOTAL ESTIMADO** | **~761 € (IVA inc.)** |

---

### 12.3 Notas importantes sobre el presupuesto

**¿Qué está incluido en el kit de la Jetson (399,30 €)?**
El Developer Kit de Bricogeek incluye: módulo Jetson Orin Nano Super, placa base portadora, disipador con ventilador, fuente de alimentación DC. **No incluye:** tarjeta microSD, SSD, tarjeta WiFi, ni pantalla. Con el diseño de este proyecto, tampoco necesitas tarjeta WiFi (la reemplaza el TP-Link).

**El TP-Link TL-WR802N sustituye a la tarjeta WiFi interna.** En el diseño anterior se contemplaba una tarjeta Intel AX210NGW (~22€) para crear el hotspot desde el Jetson. El TL-WR802N es más barato (~19€), más simple de configurar y más robusto. Ahorramos la complejidad y el slot M.2 Key E queda libre.

**Componentes opcionales / prescindibles para el MVP:**
- Tira LED: mejora la experiencia visual pero no es funcional para v1.0
- Impresora + rollos: solo necesaria si se implementa la funcionalidad de pegatinas desde el inicio
- Altavoces USB: algunos monitores 7" incluyen altavoces — verificar antes de comprar

**Presupuesto MVP mínimo funcional (sin impresora ni LEDs):**

| Componente | Precio |
|---|---|
| Jetson Orin Nano Super 8GB (Bricogeek) | 399,30 € |
| SSD NVMe Kingston NV3 500GB | 36 € |
| TP-Link TL-WR802N | 19 € |
| Lector NFC ACR122U | 45 € |
| Tarjetas NFC NTAG213 × 50 | 45 € |
| Pantalla táctil 7" + altavoces | 65 € |
| Hub USB + cable Ethernet + microSD | 39 € |
| **TOTAL MVP** | **~648 € (IVA inc.)** |

---

## Notas finales para el desarrollador

1. **No se usa PyQt5 ni ninguna librería de escritorio.** La UI es 100% web: FastAPI sirve HTML estático para los niños y el panel de docentes. Chromium en modo kiosk sustituye completamente a cualquier framework de escritorio, con la ventaja de que el mismo código HTML puede verse desde la pantalla del robot y desde el móvil de la docente.

2. **FastAPI + SSE es la clave de la experiencia fluida.** El streaming de tokens del LLM directamente al navegador del niño (letras apareciendo en tiempo real mientras el robot las narra) es la función más impresionante del proyecto. SSE lo implementa con menos de 20 líneas de Python.

3. **Empieza con la Fase 0 y mide los tiempos reales.** Los valores de esta guía son estimaciones basadas en benchmarks públicos. Tu hardware y configuración específica pueden variar ±30%.

4. **Prioriza la experiencia del niño sobre la sofisticación técnica.** Un cuento bien narrado con una imagen pre-dibujada y LEDs de colores va a deleitar a los niños igualmente que una imagen generada en tiempo real tras 8 minutos de espera.

5. **Las docentes son las expertas en contenido.** El audio pregrabado por ellas mismas es un activo enorme — aprovéchalo desde el primer día. El panel de administración web (simple, desde el móvil) es lo que hace que el proyecto sea sostenible en el tiempo sin depender de soporte técnico.

6. **Qwen 2.5 3B es tu LLM.** Más rápido (30–45 seg por cuento vs 90–120), huella de memoria dos veces menor que Mistral 7B, y calidad más que suficiente para cuentos infantiles simples. La ruta de escalado a 7B está a un comando de distancia si fuera necesario.

7. **LCM LoRA es el verdadero acelerador de imagen.** Un LoRA de estilo cambia la estética; el LCM LoRA reduce los pasos de 20 a 4–8, convirtiendo 3–8 minutos en 50–110 segundos. Pueden apilarse ambos en el mismo pipeline SD 1.5.

8. **El router TP-Link y el SSD son obligatorios antes de empezar.** Sin SSD, los tiempos de carga de modelos hacen las pruebas imposibles. Sin el TP-Link, el panel de docentes no existe. Ambos juntos cuestan menos de 60€.

---

*Documento generado para el proyecto Robot Cuentacuentos — uso educativo, Infantil 3-6 años*
