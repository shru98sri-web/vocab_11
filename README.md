# voca_11

Vocabulary app with a Flutter frontend and a small Flask API.

## Run locally

From the project root, start the backend in one terminal:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
python backend/notifier.py
```

Python 3.11 or newer is required for the MCP SDK.

In a second terminal, start the Flutter web app:

```sh
flutter pub get
flutter run -d chrome --dart-define=VOCAB_URL=http://localhost:8000
```

`VOCAB_URL` is a compile-time setting. For a production build, pass the
deployed backend's HTTPS base URL without a trailing slash, for example:

```sh
flutter build web --release \
  --base-href "/vocab_11/" \
  --dart-define=VOCAB_URL=https://your-backend.example.com
```

The GitHub Pages workflow reads `VOCAB_API_URL` from the repository variable.
If unset, it builds with `http://127.0.0.1:8000` so the static site can deploy;
that fallback only works when the visitor is running the backend locally. For
the public site to access an API, set `VOCAB_API_URL` to a deployed HTTPS
backend URL under **Settings → Secrets and variables → Actions → Variables**.
Enable GitHub Pages with **GitHub Actions** as the build and deployment source.

The JSON file in `backend/vocab_250.json` is the API's server-side database,
and is also bundled as an offline startup fallback. If the API is unavailable,
the app loads its cached vocabulary or this bundled dataset. API-backed writes
and chat still require a reachable backend.

The GitHub Pages workflow builds with the bundled dataset when
`VOCAB_API_URL` is unset or points to the local development server. Set the
repository Actions variable to a public HTTPS backend URL to enable server-backed
features on the published site.

## Vocabulary agent and MCP

The Tutor uses the backend's local vocabulary tools for exact lookups, search,
and quizzes. `POST /chat` returns those results in the format expected by
Flutter; it does not require an external model key. The same read-only tools are
available to Copilot through the workspace-root `.mcp.json`.

1. Install the backend requirements in the project virtual environment.
2. Open this workspace in VS Code with the Copilot harness and approve the
   `vocabulary` MCP server when prompted.
3. Select **Vocabulary Orchestrator** in the agent picker to use the vocabulary
   tools while keeping code edits, tests, and review under manual control.

The MCP tools read the existing `backend/vocab_250.json`; the normal app API and
manual vocabulary editing continue to work if MCP is unavailable. No MongoDB
connection or external vocabulary server is configured.

## Android builds

Build a release APK and App Bundle with the backend URL reachable from the
device:

```sh
flutter build apk --release \
  --dart-define=VOCAB_URL=http://<computer-lan-ip>:8000
flutter build appbundle --release \
  --dart-define=VOCAB_URL=http://<computer-lan-ip>:8000
```

The outputs are `build/app/outputs/flutter-apk/app-release.apk` and
`build/app/outputs/bundle/release/app-release.aab`. Release builds currently use
the local debug signing key for device testing; configure a private release
keystore before distributing through Google Play.
