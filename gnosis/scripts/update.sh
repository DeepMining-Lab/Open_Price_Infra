# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH

#!/usr/bin/env bash

# Description: Met à jour les données de Chainlink et concatène aux données existantes
# Usage: bash update.sh
# Pour les droits d'exécution: chmod +x update.sh

# Options de sécurité bash
set -euo pipefail

# Détecter le répertoire du script et définir le répertoire projet
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "$PROJECT_DIR"

# Créer le répertoire pour les logs
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
# Nom du fichier de log avec timestamp
LOG_FILE="$LOG_DIR/update_$(date +"%Y%m%d_%H%M%S").log"


find "$LOG_DIR" -name "*.log" -mtime +30 -delete && echo "[INFO] Anciens logs (>30j) supprimés." || true

echo "=== Démarrage du script update.sh ($(date)) ===" | tee -a "$LOG_FILE"
# Rediriger stdout et stderr vers le fichier de log (tout en conservant l'affichage)
exec > >(awk '{ print strftime("%Y-%m-%d %H:%M:%S"), "-", $0; fflush(); }' | tee -a "$LOG_FILE") 2>&1

concat_with_header_sync() {
  local last="$1" data="$2"
  if [[ ! -f "$last" ]]; then
    echo "[WARNING] $last non trouvé, aucune concaténation effectuée."
    return
  fi
  local last_hdr data_hdr
  last_hdr=$(head -1 "$last")
  data_hdr=$(head -1 "$data")
  if [[ "$last_hdr" != "$data_hdr" ]]; then
    echo "[WARNING] Schema mismatch détecté pour $(basename "$data") — mise à jour du header"
    sed -i "1s|.*|${last_hdr}|" "$data"
  fi
  echo "[INFO] Concaténation de $last dans $data"
  tail -n +2 "$last" >> "$data"
  rm "$last"
}

# Chemins absolus
DATA_FILE_CHAINLINK="$PROJECT_DIR/data/chainlink_gno_usd.csv"
OUTPUT_DIR="$PROJECT_DIR/data/output"
LAST_FILE_CHAINLINK="$PROJECT_DIR/data/chainlink_gno_usd_last.csv"

git checkout main
git reset --hard
git clean -fd
git pull --rebase origin main


# Afficher info RPC
if [[ -z "$RPC" ]]; then
  echo "WARNING: La variable RPC n'est pas définie." >&2
else
  echo "INFO: Utilisation de RPC=$RPC"
fi

# Vérifier l'existence du CSV Chainlink 

if [[ ! -f "$DATA_FILE_CHAINLINK" ]]; then
  echo "[ERROR] Fichier $DATA_FILE_CHAINLINK introuvable." >&2
  exit 1
fi
echo "[INFO] Fichier de données: $DATA_FILE_CHAINLINK"

# Récupérer et ajouter +1 seconde à la date de dernière modif des CSVs

# Extraire le champ “round_updated_at_utc” de la dernière ligne du CSV
last_iso_chainlink=$(tail -n 1 “$DATA_FILE_CHAINLINK” | cut -d',' -f4)

# Convertir ce timestamp ISO en secondes Unix puis +1 (avec fallback si CSV vide)
if [[ “$last_iso_chainlink” == “round_updated_at_utc” ]] || [[ -z “$last_iso_chainlink” ]]; then
  start_ts_chainlink=1546300800
  echo “[INFO] CSV Chainlink vide, démarrage depuis la date par défaut.”
else
  start_ts_chainlink=$(( $(date -d “$last_iso_chainlink” +”%s”) + 1 ))
fi

echo "[INFO] Timestamp de démarrage pour Chainlink (dernière date +1s) : $start_ts_chainlink"


# Exécuter le traitement pour récupérer les prix de Chainlink
echo "[INFO] Lancement de chainlink_gno_usd.py..."
python3 "$PROJECT_DIR/scripts/chainlink_gno_usd.py" --debut "$start_ts_chainlink"
echo "[INFO] Traitement Chainlink terminé"


concat_with_header_sync "$LAST_FILE_CHAINLINK" "$DATA_FILE_CHAINLINK"

# MAJ du README
echo "[INFO] Lancement de generate_readme.py..."
python3 "$PROJECT_DIR/scripts/generate_readme.py"
echo "[INFO] Generate_readme terminé"


# SCP dans Filebrowser des data

MAX=5

for i in $(seq 1 $MAX); do
  echo "[INFO] Tentative #$i..."
  scp data/{chainlink_gno_usd.csv} debian@extract.lan.text-analytics.ch:/data/gnosis/prices && break
  echo "[WARNING] Échec (code : $?). Nouvelle tentative dans 3s." >&2
  sleep 3
done


if [ $i -le $MAX ]; then
  echo "[INFO] Transfert réussi à la tentative #$i."
else
  echo "[ERROR] Impossible de transférer après $MAX tentatives." >&2
  exit 1
fi

# 11. Commit & Push du README mis-à-jour sur Github

git add README.md
git commit -m "Update data"

git push origin main

# Fin du script
sleep 3
echo "=== Fin du script ==="