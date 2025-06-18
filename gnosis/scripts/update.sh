# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH

#!/usr/bin/env bash

# Description: Met à jour les données de Chainlink et d'Uniswap et concatène aux données existantes
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


echo "=== Démarrage du script update.sh ($(date)) ===" | tee -a "$LOG_FILE"
# Rediriger stdout et stderr vers le fichier de log (tout en conservant l'affichage)
exec > >(awk '{ print strftime("%Y-%m-%d %H:%M:%S"), "-", $0; fflush(); }' | tee -a "$LOG_FILE") 2>&1


# Chemins absolus
DATA_FILE_CHAINLINK="$PROJECT_DIR/data/chainlink_gno_usd.csv"
OUTPUT_DIR="$PROJECT_DIR/data/output"
LAST_FILE_CHAINLINK="$PROJECT_DIR/data/chainlink_gno_usd_last.csv"

# Vérifier l'existence du CSV Uniswap & du CSV Chainlink 
if [[ ! -f "$DATA_FILE_UNISWAP" ]]; then
  echo "[ERROR] Fichier $DATA_FILE_UNISWAP introuvable." >&2
  exit 1
fi
echo "[INFO] Fichier de données: $DATA_FILE_UNISWAP"

if [[ ! -f "$DATA_FILE_CHAINLINK" ]]; then
  echo "[ERROR] Fichier $DATA_FILE_CHAINLINK introuvable." >&2
  exit 1
fi
echo "[INFO] Fichier de données: $DATA_FILE_CHAINLINK"

# Récupérer et ajouter +1 seconde à la date de dernière modif des CSVs

# Extraire le champ “timestamp” de la dernière ligne des CSVs
last_iso_uniswap=$(tail -n 1 "$DATA_FILE_UNISWAP" | cut -d',' -f1)
last_iso_chainlink=$(tail -n 1 "$DATA_FILE_CHAINLINK" | cut -d',' -f4)

# Convertir ce timestamp ISO en secondes Unix puis +1
start_ts_uniswap=$(( $(date -d "$last_iso_uniswap" +"%s") + 1 ))
start_ts_chainlink=$(( $(date -d "$last_iso_chainlink" +"%s") + 1 ))

echo "[INFO] Timestamp de démarrage pour Uniswap (dernière date +1s) : $start_ts_uniswap"
echo "[INFO] Timestamp de démarrage pour Chainlink (dernière date +1s) : $start_ts_chainlink"

# 3. Lancer cryo logs avec timestamp
echo "[INFO] Lancement de 'cryo logs'..."

# https://eth.rpc.faironchain.org/
echo "$PROJECT_DIR"

cryo logs \
  --address 0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640 \
  --rpc https://ethereum-rpc.publicnode.com \
  --output-dir $PROJECT_DIR/data/output \
  --csv \
  --timestamps ${start_ts_uniswap}: \
|| echo "[WARNING] 'cryo logs' a rencontré un problème... Le script continue..."

echo "[INFO] 'cryo logs' terminé"

# Exécuter le traitement pour traiter les logs d'Uniswap
echo "[INFO] Lancement de Uniswap_process_logs.py..."
python3 "$PROJECT_DIR/scripts/Uniswap_process_logs.py"
echo "[INFO] Traitement Uniswap terminé"

# Exécuter le traitement pour récupérer les prix de Chainlink
echo "[INFO] Lancement de chainlink_dicho.py..."
python3 "$PROJECT_DIR/scripts/chainlink_dicho.py" --debut "$start_ts_chainlink"
echo "[INFO] Traitement Chainlink terminé"


# Concaténer chainlink_eth_usd_last.csv dans chainlink_eth_usd.csv

if [[ -f "$LAST_FILE_CHAINLINK" ]]; then
  echo "[INFO] Concaténation de $LAST_FILE_CHAINLINK dans $DATA_FILE_CHAINLINK"
  tail -n +2 "$LAST_FILE_CHAINLINK" >> "$DATA_FILE_CHAINLINK"
else
  echo "[WARNING] $LAST_FILE_CHAINLINK non trouvé, aucune concaténation effectuée."
fi

# Supprimer les fichiers une fois concaténés

if [[ -f "$LAST_FILE_CHAINLINK" ]]; then
  echo "[INFO] Suppression de $LAST_FILE_CHAINLINK"
  rm "$LAST_FILE_CHAINLINK"
else
  echo "[WARNING] $LAST_FILE_CHAINLINK non n'a pas été supprimé."
fi

# MAJ du README
echo "[INFO] Lancement de generate_readme.py..."
python3 "$PROJECT_DIR/scripts/generate_readme.py"
echo "[INFO] Generate_readme terminé"

# Commit & Push du README mis-à-jour sur Github
# git checkout main
# git add "README.md"
# git commit -m "Update data"

# git pull --rebase origin main

# git push origin main


# SCP dans Filebrowser sur les data



# Fin du script
echo "=== Fin du script ==="