#!/bin/sh
# Bootstrap wrapper for environments where the standard Gradle wrapper JAR is unavailable.
# GitHub Actions uses the official Gradle setup action defined in .github/workflows/build-apk.yml.
set -e
if command -v gradle >/dev/null 2>&1; then
  exec gradle "$@"
fi
echo "Gradle is not installed. On GitHub Actions, run the provided Build ComicCraft APK workflow." >&2
exit 1
