# kwi-ui Quickstart

## Prerequisites

- **Rust** ≥ 1.75 with `cargo`
- **Node.js** ≥ 20 with `npm`
- **System libraries** (Linux): `libwebkit2gtk-4.1-dev`, `libgtk-3-dev`,
  `libayatana-appindicator3-dev`, `librsvg2-dev`
- **PostgreSQL** accessible at the URL in `~/.config/kwi/config.toml`
  or `KWI_DATABASE_URL` env var

### Install system dependencies (Ubuntu/Debian)

```bash
sudo apt install libwebkit2gtk-4.1-dev libgtk-3-dev \
  libayatana-appindicator3-dev librsvg2-dev
```

## Setup

```bash
# From repo root
cd kwi-ui

# Install frontend dependencies
npm install

# Verify Rust toolchain
rustup update stable
```

## Configuration

kwi-ui reads the same config as the CLI:

```toml
# ~/.config/kwi/config.toml
database_url = "postgresql://user:pass@host:5432/workitems"
```

Or via environment variable:

```bash
export KWI_DATABASE_URL="postgresql://user:pass@host:5432/workitems"
```

## Development

```bash
# Start in dev mode (hot-reload for frontend, auto-rebuild for Rust)
npm run tauri dev
```

This opens the app window. Frontend changes reload instantly;
Rust changes trigger a recompile on save.

## Build

```bash
# Build release binary
npm run tauri build
```

Output is in `kwi-ui/src-tauri/target/release/`.

## Testing

```bash
# Rust unit tests
cd src-tauri && cargo test

# Frontend checks
npm run check      # svelte-check
npm run test       # vitest
```

## Pre-commit Checks

From `kwi-ui/`:

```bash
# Rust
cd src-tauri && cargo fmt --check && cargo clippy -- -D warnings && cargo test

# Frontend
npm run format -- --check && npm run lint && npm run check && npm run test
```
