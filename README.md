# terrain-releases

Public companion to the Terrain field GIS app. Two jobs, and nothing else
belongs here:

1. **Releases.** Every push to `main` in the private source repo builds a signed
   APK and publishes it here as a release. The app checks this repo on startup
   and offers the update in a banner.
2. **Field files.** Everything under [`files/`](files) is browsable inside the
   app — folders as folders, files as files, in whatever structure you put them.

This repo is public on purpose: a surveyor downloading an update in the field
should not need credentials, and neither should the file browser. **Nothing
private goes in here.** No project data, no customer drawings, no credentials.

## Adding files

Drop them anywhere under `files/`, in any folder structure you like. Create
folders freely — the app mirrors whatever is here. You can do it from the GitHub
web UI: open `files/`, then **Add file → Upload files**.

`index.json` at the root is regenerated automatically whenever `files/` changes.
The app reads that one file instead of walking the GitHub API, which would run
into the 60-requests-per-hour limit that applies to unauthenticated callers —
and a surveyor who has just opened four folders is exactly the caller who would
hit it. **Do not edit `index.json` by hand.**

## What the app does with each type

| kind | in the app |
|---|---|
| images (`.jpg`, `.png`, `.webp`) | shown inline |
| PDF | opens in the device's PDF viewer |
| CAD and engineering (`.dxf`, `.xml`, `.kml`, `.kmz`) | downloaded, then handed to the server for conversion |
| anything else | downloaded and passed to whichever app handles it |

## Releases

Each release carries the APK plus its `sha256`. `latest.json` at the root
mirrors the newest release so the app can check for updates with a single
request and no API rate limit.
