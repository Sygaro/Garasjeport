#!/bin/bash

echo "🔍 Standardiserer config_paths-importer..."

PROJECT_ROOT=$(pwd)

# Finn alle .py-filer unntatt venv
find "$PROJECT_ROOT" -type f -name "*.py" ! -path "*/venv/*" | while read -r file; do
  # Bytt importlinje
  if grep -q "from config import config_paths$" "$file"; then
    sed -i 's/from config import config_paths$/from config import config_paths as paths/' "$file"
    echo "✅ Oppdatert import i: $file"
  fi

  # Bytt bruk av config_paths. til paths.
  if grep -q "config_paths\." "$file"; then
    sed -i 's/config_paths\./paths./g' "$file"
    echo "✅ Oppdatert referanser i: $file"
  fi
done

echo "🚀 Ferdig! Importer og referanser er nå standardisert."
