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

The GitHub Pages workflow reads that URL from the repository variable
`VOCAB_API_URL`. Set it under **Settings → Secrets and variables → Actions →
Variables** before deploying. Enable GitHub Pages with **GitHub Actions** as
the build and deployment source.

The JSON file in `backend/vocab_250.json` is the API's server-side database,
not a Flutter asset. The app currently loads its Flutter assets from the PNG
files declared in `pubspec.yaml`.
