# Reproduce the import and verification

The ready-to-run app is in `dist/`; rebuilding is optional.

Data scripts require Python 3 and `lxml` (`python -m pip install lxml`).
The required original Bible/trivia baselines, SQLite module, USFX XML, source archives, dictionary JavaScript and appendix source pages are included in `sources/`.

From the project folder:

```sh
python scripts/verify_data.py
python scripts/import_strongs.py
python scripts/import_bullinger.py
```

The Bullinger importer can contact the cited source website to refresh image files. Existing complete imported images remain in `dist/bullinger/images/`. Source license and attribution details are in `sources/PROVENANCE.md`.

Browser verification requires Node.js, Playwright and its Chromium browser. Start a local server and set the test URL explicitly:

```sh
python -m http.server 8087 --bind 127.0.0.1 --directory dist
# In another terminal, after installing Playwright and Chromium:
BIBLE_TEST_URL=http://127.0.0.1:8087/ node scripts/verify_app.cjs
```

In PowerShell, set `$env:BIBLE_TEST_URL="http://127.0.0.1:8087/"` before running Node. The browser check replaces the saved reports/screenshots with the results of that run.
