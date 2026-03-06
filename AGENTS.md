# StoryBot Agent Configuration

## Project Overview

**StoryBot** is a storytelling robot for children ages 3-6, running 100% offline on NVIDIA Jetson Orin Nano Super 8GB. It uses FastAPI, local AI models (Ollama + Piper TTS + Stable Diffusion), NFC cards, and a thermal sticker printer.

## Environments

There are **two distinct environments**. Code is written and tested on the development machine, then deployed to the Jetson.

### Development Machine (where you are running)

- **Architecture**: x86_64
- **OS**: Ubuntu 24.04 LTS (kernel 6.14)
- **Python**: 3.10.18
- **GPU**: NVIDIA RTX 4000 Ada (12GB VRAM)
- **CUDA**: via pip packages (cuda-python, cupy, torch, etc.)
- **Package Manager**: uv

### Target Device (production)

- **Hardware**: NVIDIA Jetson Orin Nano Super 8GB
- **Architecture**: aarch64 (ARM)
- **OS**: Ubuntu 22.04 LTS (Linux 5.15 tegra, JetPack 6.2.1)
- **Python**: 3.10.12
- **CUDA**: 12.6.10 (pre-installed via `nvidia-jetpack` apt package)
- **TensorRT**: 10.3.0 (pre-installed via apt)
- **cuDNN**: 9.3.0 (pre-installed via apt)

### Key difference

On the **dev machine**, CUDA/AI libraries are installed as pip dependencies (see `[project.optional-dependencies] jetson` in pyproject.toml). On the **Jetson**, these same libraries come pre-installed as system packages via `sudo apt install nvidia-jetpack` — they should NOT be pip-installed there. The `jetson` optional dependencies exist to emulate the Jetson environment on x86 for development and testing.

## Project Setup

### Initialize project with uv

```bash
uv venv
uv sync
```

### Install development dependencies

```bash
uv sync --extra dev
```

## Code Standards

### Formatting

- **Black** for code formatting (line length: 88)
- Run formatter: `uv run black .`

### Type Checking

- **Ruff** for linting and import sorting
- Run linter: `uv run ruff check .`
- Run formatter: `uv run ruff format .`

### Testing

- **pytest** for unit and integration tests
- Run tests: `uv run pytest`
- Test coverage: `uv run pytest --cov`

## Project Structure

```
storybot/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── routers/                # API route modules
│   │   ├── __init__.py
│   │   ├── stories.py          # Story CRUD endpoints
│   │   ├── admin.py            # Admin panel endpoints
│   │   ├── generate.py         # AI generation endpoints
│   │   ├── nfc.py              # NFC handling endpoints
│   │   ├── printer.py          # Printer control endpoints
│   │   └── system.py           # System status & LED control
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── model_manager.py    # AI model loading/unloading
│   │   ├── story_generator.py  # LLM story generation
│   │   ├── tts_engine.py       # Piper TTS integration
│   │   ├── image_generator.py  # Stable Diffusion pipeline
│   │   ├── nfc_handler.py      # NFC reader/writer
│   │   ├── printer_handler.py  # Brother QL printer
│   │   ├── led_controller.py   # RGB LED control
│   │   ├── audio_player.py     # Audio playback
│   │   └── content_manager.py  # Content storage management
│   └── models/                 # Pydantic schemas
│       ├── __init__.py
│       └── ...
├── static/                     # Frontend assets
│   ├── children/               # Children's UI (kiosk)
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── script.js
│   └── admin/                  # Teacher admin panel
│       ├── index.html
│       ├── styles.css
│       └── script.js
├── content/                    # Story content storage
│   ├── stories/               # Narrated stories (JSON + audio)
│   ├── interactive/          # Interactive story trees (JSON)
│   └── images/                # Pre-generated images
├── models/                     # AI models (managed by Ollama)
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   └── test_integration/
├── pyproject.toml
├── uv.lock
├── README.md
├── AGENTS.md
└── .gitignore
```

## Key Technical Decisions

### AI Models

- **LLM**: Qwen 2.5 3B Instruct (Q4_K_M) via Ollama - ~2GB RAM, 35-45 tok/s
- **TTS**: Piper TTS with es_ES voices - always loaded, ~400MB RAM
- **Image Generation**: Stable Diffusion 1.5 + LCM LoRA + Lineart LoRA - ~2.8 Memory Management

TheGB RAM

### 8GB RAM is shared between OS, app, and AI models. Models are loaded/unloaded based on active task:
- Piper TTS: always loaded
- LLM and SD: can coexist with Qwen 2.5 3B (~4.8GB combined)

### Real-time Communication

- **Server-Sent Events (SSE)** for streaming AI generation to frontend
- **FastAPI** for REST API serving both children (kiosk) and teachers (mobile)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stories` | GET | List all stories |
| `/api/stories` | POST | Upload new story |
| `/api/stories/{id}` | GET | Get story by ID |
| `/api/stories/{id}` | DELETE | Delete story |
| `/api/generate/story` | POST | Generate AI story (SSE) |
| `/api/generate/status/{task_id}` | GET | Generation progress (SSE) |
| `/api/nfc/read` | GET | Read NFC card (SSE) |
| `/api/nfc/write` | POST | Write UID to NFC card |
| `/api/printer/print` | POST | Print sticker |
| `/api/system/status` | GET | System status (RAM, models) |
| `/api/system/led` | POST | Control RGB LEDs |

## Testing Strategy

1. **Unit tests**: Test individual service functions
2. **Integration tests**: Test API endpoints with mocked services
3. **Hardware tests**: Test NFC, printer, LED with actual hardware (optional, can be mocked)

## Common Tasks

### Run development server

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run tests with coverage

```bash
uv run pytest --cov=app --cov-report=html
```

### Format and lint code

```bash
uv run black .
uv run ruff check . --fix
uv run ruff format .
```

## Hardware Integration

- **NFC Reader**: ACS ACR122U (USB) - uses nfcpy library
- **Printer**: Brother QL-800 - uses brother_ql library
- **LED Strip**: USB-controlled RGB (Govee or similar)
- **Display**: 7" HDMI touchscreen running Chromium kiosk mode
- **Network**: TP-Link TL-WR802N as access point

## Important Notes

- All AI inference runs locally - NO internet required in production
- Teacher panel accessible at `/admin` with HTTP Basic auth
- Children interface runs in Chromium kiosk mode at `http://localhost/`
- Use SSE instead of WebSockets for server-to-client streaming
