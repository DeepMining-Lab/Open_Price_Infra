# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH

#!/usr/bin/env bash

# Description: Met à jour les données Chainlink USDC/USD et USDT/USD et concatène aux données existantes
# Usage: bash update.sh
# Pour les droits d'exécution: chmod +x update.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "$PROJECT_DIR"

LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/update_$(date +"%Y%m%d_%H%M%S").log"

find "$LOG_DIR" -name "*.log" -mtime +30 -delete && echo "[INFO] Anciens logs (>30j) supprimés." || true

echo "=== Démarrage du script update.sh ($(date)) ===" | tee -a "$LOG_FILE"
exec > >(awk '{ print strftime("%Y-%m-%d %H:%M:%S"), "-", $0; fflush(); }' | tee -a "$LOG_FILE") 2>&1

DATA_FILE_USDC="$PROJECT_DIR/data/chainlink_usdc_usd.csv"
DATA_FILE_USDT="$PROJECT_DIR/data/chainlink_usdt_usd.csv"
LAST_FILE_USDC="$PROJECT_DIR/data/chainlink_usdc_usd_last.csv"
LAST_FILE_USDT="$PROJECT_DIR/data/chainlink_usdt_usd_last.csv"

if [[ -z "$RPC" ]]; then
  echo "WARNING: La variable RPC n'est pas définie." >&2
else
  echo "INFO: Utilisation de RPC=$RPC"
fi

# Vérifier l'existence des CSVs
if [[ ! -f "$DATA_FILE_USDC" ]]; then
  echo "[ERROR] Fichier $DATA_FILE_USDC introuvable." >&2
  exit 1
fi
echo "[INFO] Fichier de données: $DATA_FILE_USDC"

if [[ ! -f "$DATA_FILE_USDT" ]]; then
  echo "[ERROR] Fichier $DATA_FILE_USDT introuvable." >&2
  exit 1
fi
echo "[INFO] Fichier de données: $DATA_FILE_USDT"

# Extraire les timestamps de départ (+1s) depuis la dernière ligne de chaque CSV
last_iso_usdc=$(tail -n 1 "$DATA_FILE_USDC" | cut -d',' -f4)
if [[ "$last_iso_usdc" == "datetime_utc" ]] || [[ -z "$last_iso_usdc" ]]; then
  start_ts_usdc=1546300800
  echo "[INFO] CSV USDC vide, démarrage depuis la date par défaut."
else
  start_ts_usdc=$(( $(date -d "$last_iso_usdc" +"%s") + 1 ))
fi

last_iso_usdt=$(tail -n 1 "$DATA_FILE_USDT" | cut -d',' -f4)
if [[ "$last_iso_usdt" == "datetime_utc" ]] || [[ -z "$last_iso_usdt" ]]; then
  start_ts_usdt=1546300800
  echo "[INFO] CSV USDT vide, démarrage depuis la date par défaut."
else
  start_ts_usdt=$(( $(date -d "$last_iso_usdt" +"%s") + 1 ))
fi

echo "[INFO] Timestamp de démarrage USDC : $start_ts_usdc"
echo "[INFO] Timestamp de démarrage USDT : $start_ts_usdt"

# Extraction Chainlink USDC/USD
echo "[INFO] Lancement de chainlink_usdc_usd.py..."
if ! python3 "$PROJECT_DIR/scripts/chainlink_usdc_usd.py" --debut "$start_ts_usdc"; then
  echo "[ERROR] Échec de chainlink_usdc_usd.py." >&2
  [[ -f "$LAST_FILE_USDC" ]] && rm "$LAST_FILE_USDC"
  exit 1
fi
echo "[INFO] Traitement Chainlink USDC terminé"

# Extraction Chainlink USDT/USD
echo "[INFO] Lancement de chainlink_usdt_usd.py..."
if ! python3 "$PROJECT_DIR/scripts/chainlink_usdt_usd.py" --debut "$start_ts_usdt"; then
  echo "[ERROR] Échec de chainlink_usdt_usd.py." >&2
  [[ -f "$LAST_FILE_USDT" ]] && rm "$LAST_FILE_USDT"
  exit 1
fi
echo "[INFO] Traitement Chainlink USDT terminé"

# Concaténer les fichiers _last dans les CSVs principaux
if [[ -f "$LAST_FILE_USDC" ]]; then
  echo "[INFO] Concaténation de $LAST_FILE_USDC dans $DATA_FILE_USDC"
  tail -n +2 "$LAST_FILE_USDC" >> "$DATA_FILE_USDC"
  rm "$LAST_FILE_USDC"
else
  echo "[WARNING] $LAST_FILE_USDC non trouvé, aucune concaténation effectuée."
fi

if [[ -f "$LAST_FILE_USDT" ]]; then
  echo "[INFO] Concaténation de $LAST_FILE_USDT dans $DATA_FILE_USDT"
  tail -n +2 "$LAST_FILE_USDT" >> "$DATA_FILE_USDT"
  rm "$LAST_FILE_USDT"
else
  echo "[WARNING] $LAST_FILE_USDT non trouvé, aucune concaténation effectuée."
fi

# MAJ du README
echo "[INFO] Lancement de generate_readme.py..."
if ! python3 "$PROJECT_DIR/scripts/generate_readme.py"; then
  echo "[WARNING] Impossible de mettre à jour le README !" >&2
fi
echo "[INFO] Generate_readme terminé"

# SCP vers extract.lan.text-analytics.ch
MAX=5
SCP_OK=false
for i in $(seq 1 $MAX); do
  echo "[INFO] Tentative #$i..."
  if scp data/{chainlink_usdc_usd.csv,chainlink_usdt_usd.csv} debian@extract.lan.text-analytics.ch:/data/ethereum/prices; then
    SCP_OK=true
    break
  fi
  echo "[WARNING] Échec SCP (code : $?). Nouvelle tentative dans 3s." >&2
  sleep 3
done

if $SCP_OK; then
  echo "[INFO] Transfert réussi à la tentative #$i."
else
  echo "[ERROR] Impossible de transférer après $MAX tentatives." >&2
  exit 1
fi

# Commit & Push du README mis-à-jour sur Github
git add README.md
git commit -m "Update data" || echo "[WARNING] Rien à committer ou échec du commit."
git pull --rebase origin main || echo "[WARNING] git pull --rebase avant push a échoué."
git push origin main || echo "[WARNING] git push échoué (clé SSH ?). Données mises à jour localement."

sleep 3
echo "=== Fin du script ==="
