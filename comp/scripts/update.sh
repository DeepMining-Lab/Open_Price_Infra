# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH

#!/usr/bin/env bash

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

concat_with_header_sync() {
  local last="$1" data="$2" ts_col="${3:-1}"
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
  local last_ts
  last_ts=$(tail -n 1 "$data" | cut -d',' -f"$ts_col")
  echo "[INFO] Concaténation de $last dans $data (depuis $last_ts)"
  if [[ -z "$last_ts" ]] || [[ "$last_ts" == "timestamp" ]] || [[ "$last_ts" == "round_updated_at_utc" ]]; then
    tail -n +2 "$last" >> "$data"
  else
    awk -F',' -v ts="$last_ts" -v col="$ts_col" 'NR>1 && $(col) > ts' "$last" >> "$data"
  fi
  rm "$last"
}

DATA_FILE_UNISWAP="$PROJECT_DIR/data/comp_usdc_uniswap_v3_03.csv"
DATA_FILE_CHAINLINK="$PROJECT_DIR/data/chainlink_comp_usd.csv"
OUTPUT_DIR="$PROJECT_DIR/data/output"
LAST_FILE_UNISWAP="$PROJECT_DIR/data/comp_usdc_uniswap_v3_03_last.csv"
LAST_FILE_CHAINLINK="$PROJECT_DIR/data/chainlink_comp_usd_last.csv"

if [[ -z "$RPC" ]]; then
  echo "WARNING: La variable RPC n'est pas définie." >&2
else
  echo "INFO: Utilisation de RPC=$RPC"
fi

# 1. Vérifier l'existence des CSVs
if [[ ! -f "$DATA_FILE_UNISWAP" ]]; then
  echo "[ERROR] Fichier $DATA_FILE_UNISWAP introuvable." >&2
  exit 1
fi
if [[ ! -f "$DATA_FILE_CHAINLINK" ]]; then
  echo "[ERROR] Fichier $DATA_FILE_CHAINLINK introuvable." >&2
  exit 1
fi

# 2. Récupérer le timestamp de la dernière ligne (avec fallback si CSV vide)
last_iso_uniswap=$(tail -n 1 "$DATA_FILE_UNISWAP" | cut -d',' -f1)
if [[ "$last_iso_uniswap" == "timestamp" ]] || [[ -z "$last_iso_uniswap" ]]; then
  start_ts_uniswap=1546300800
  echo "[INFO] CSV Uniswap vide, démarrage depuis la date par défaut."
else
  start_ts_uniswap=$(( $(date -d "$last_iso_uniswap" +"%s") + 1 ))
fi

last_iso_chainlink=$(tail -n 1 "$DATA_FILE_CHAINLINK" | cut -d',' -f4)
if [[ "$last_iso_chainlink" == "round_updated_at_utc" ]] || [[ -z "$last_iso_chainlink" ]]; then
  start_ts_chainlink=1546300800
  echo "[INFO] CSV Chainlink vide, démarrage depuis la date par défaut."
else
  start_ts_chainlink=$(( $(date -d "$last_iso_chainlink" +"%s") + 1 ))
fi

echo "[INFO] Timestamp Uniswap : $start_ts_uniswap"
echo "[INFO] Timestamp Chainlink : $start_ts_chainlink"

# 3. Cryo logs
echo "[INFO] Lancement de 'cryo logs'..."
cryo logs \
  --address 0xF15054BC50c39ad15FDC67f2AedD7c2c945ca5f6 \
  --rpc $RPC \
  --output-dir $PROJECT_DIR/data/output \
  --csv \
  --timestamps ${start_ts_uniswap}: \
|| echo "[WARNING] 'cryo logs' a rencontré un problème... Le script continue..."
echo "[INFO] 'cryo logs' terminé"

# 4. Traitement Uniswap
echo "[INFO] Vérification CSV dans $OUTPUT_DIR..."
if ! ls "$OUTPUT_DIR"/*.csv >/dev/null 2>&1; then
  echo "[ERROR] Aucun CSV dans $OUTPUT_DIR." >&2
  exit 1
fi

echo "[INFO] Lancement de comp_usdc_uniswap_v3_03.py..."
if ! python3 "$PROJECT_DIR/scripts/comp_usdc_uniswap_v3_03.py"; then
  echo "[ERROR] Échec comp_usdc_uniswap_v3_03.py." >&2
  rm -rf "$OUTPUT_DIR"/* || true
  exit 1
fi
echo "[INFO] Traitement Uniswap terminé"

# 5. Traitement Chainlink
echo "[INFO] Lancement de chainlink_comp_usd.py..."
if ! python3 "$PROJECT_DIR/scripts/chainlink_comp_usd.py" --debut "$start_ts_chainlink"; then
  echo "[ERROR] Échec chainlink_comp_usd.py." >&2
  [[ -f "$LAST_FILE_CHAINLINK" ]] && rm "$LAST_FILE_CHAINLINK" || true
  exit 1
fi
echo "[INFO] Traitement Chainlink terminé"

# 6. Nettoyage output
echo "[INFO] Suppression du contenu de $OUTPUT_DIR"
rm -rf "$OUTPUT_DIR"/* || echo "[WARNING] Impossible de supprimer $OUTPUT_DIR." >&2

# 7. Concaténation
python3 "$PROJECT_DIR/scripts/dedup_concat.py" "$LAST_FILE_UNISWAP" "$DATA_FILE_UNISWAP" \
  || echo "[WARNING] Échec dedup_concat pour $(basename $DATA_FILE_UNISWAP)" >&2
concat_with_header_sync "$LAST_FILE_CHAINLINK" "$DATA_FILE_CHAINLINK" 4

# 9. Pools supplémentaires

# comp_usdt_uniswap_v3_03
echo "[INFO] --- Traitement comp_usdt_uniswap_v3_03 ---"
DATA_FILE_POOL="$PROJECT_DIR/data/comp_usdt_uniswap_v3_03.csv"
LAST_FILE_POOL="$PROJECT_DIR/data/comp_usdt_uniswap_v3_03_last.csv"
last_iso_pool=$(tail -n 1 "$DATA_FILE_POOL" | cut -d',' -f1)
if [[ "$last_iso_pool" == "timestamp" ]] || [[ -z "$last_iso_pool" ]]; then
  start_ts_pool=1546300800
  echo "[INFO] CSV comp_usdt vide, démarrage depuis la date par défaut."
else
  start_ts_pool=$(( $(date -d "$last_iso_pool" +"%s") + 1 ))
fi
echo "[INFO] Timestamp comp_usdt : $start_ts_pool"
cryo logs --address 0x68c5ea31aefe12713642aec96999df9319942641 --rpc $RPC --output-dir "$OUTPUT_DIR" --csv --timestamps ${start_ts_pool}: \
  || echo "[WARNING] cryo comp_usdt a rencontré un problème..."
if ls "$OUTPUT_DIR"/*.csv >/dev/null 2>&1; then
  python3 "$PROJECT_DIR/scripts/comp_usdt_uniswap_v3_03.py" || echo "[WARNING] Échec comp_usdt_uniswap_v3_03.py"
else
  echo "[WARNING] Aucun CSV cryo pour comp_usdt, aucun traitement."
fi
rm -rf "$OUTPUT_DIR"/* || true
python3 "$PROJECT_DIR/scripts/dedup_concat.py" "$LAST_FILE_POOL" "$DATA_FILE_POOL" \
  || echo "[WARNING] Échec dedup_concat pour $(basename $DATA_FILE_POOL)" >&2

# comp_weth_uniswap_v3_03
echo "[INFO] --- Traitement comp_weth_uniswap_v3_03 ---"
DATA_FILE_POOL="$PROJECT_DIR/data/comp_weth_uniswap_v3_03.csv"
LAST_FILE_POOL="$PROJECT_DIR/data/comp_weth_uniswap_v3_03_last.csv"
last_iso_pool=$(tail -n 1 "$DATA_FILE_POOL" | cut -d',' -f1)
if [[ "$last_iso_pool" == "timestamp" ]] || [[ -z "$last_iso_pool" ]]; then
  start_ts_pool=1546300800
  echo "[INFO] CSV comp_weth_v3 vide, démarrage depuis la date par défaut."
else
  start_ts_pool=$(( $(date -d "$last_iso_pool" +"%s") + 1 ))
fi
echo "[INFO] Timestamp comp_weth_v3 : $start_ts_pool"
cryo logs --address 0xea4ba4ce14fdd287f380b55419b1c5b6c3f22ab6 --rpc $RPC --output-dir "$OUTPUT_DIR" --csv --timestamps ${start_ts_pool}: \
  || echo "[WARNING] cryo comp_weth_v3 a rencontré un problème..."
if ls "$OUTPUT_DIR"/*.csv >/dev/null 2>&1; then
  python3 "$PROJECT_DIR/scripts/comp_weth_uniswap_v3_03.py" || echo "[WARNING] Échec comp_weth_uniswap_v3_03.py"
else
  echo "[WARNING] Aucun CSV cryo pour comp_weth_v3, aucun traitement."
fi
rm -rf "$OUTPUT_DIR"/* || true
python3 "$PROJECT_DIR/scripts/dedup_concat.py" "$LAST_FILE_POOL" "$DATA_FILE_POOL" \
  || echo "[WARNING] Échec dedup_concat pour $(basename $DATA_FILE_POOL)" >&2

# comp_weth_uniswap_v2_03
echo "[INFO] --- Traitement comp_weth_uniswap_v2_03 ---"
DATA_FILE_POOL="$PROJECT_DIR/data/comp_weth_uniswap_v2_03.csv"
LAST_FILE_POOL="$PROJECT_DIR/data/comp_weth_uniswap_v2_03_last.csv"
last_iso_pool=$(tail -n 1 "$DATA_FILE_POOL" | cut -d',' -f1)
if [[ "$last_iso_pool" == "timestamp" ]] || [[ -z "$last_iso_pool" ]]; then
  start_ts_pool=1546300800
  echo "[INFO] CSV comp_weth_v2 vide, démarrage depuis la date par défaut."
else
  start_ts_pool=$(( $(date -d "$last_iso_pool" +"%s") + 1 ))
fi
echo "[INFO] Timestamp comp_weth_v2 : $start_ts_pool"
cryo logs --address 0xcffdded873554f362ac02f8fb1f02e5ada10516f --rpc $RPC --output-dir "$OUTPUT_DIR" --csv --timestamps ${start_ts_pool}: \
  || echo "[WARNING] cryo comp_weth_v2 a rencontré un problème..."
if ls "$OUTPUT_DIR"/*.csv >/dev/null 2>&1; then
  python3 "$PROJECT_DIR/scripts/comp_weth_uniswap_v2_03.py" || echo "[WARNING] Échec comp_weth_uniswap_v2_03.py"
else
  echo "[WARNING] Aucun CSV cryo pour comp_weth_v2, aucun traitement."
fi
rm -rf "$OUTPUT_DIR"/* || true
python3 "$PROJECT_DIR/scripts/dedup_concat.py" "$LAST_FILE_POOL" "$DATA_FILE_POOL" \
  || echo "[WARNING] Échec dedup_concat pour $(basename $DATA_FILE_POOL)" >&2

# comp_eth_sushiswap_v2_03
echo "[INFO] --- Traitement comp_eth_sushiswap_v2_03 ---"
DATA_FILE_POOL="$PROJECT_DIR/data/comp_eth_sushiswap_v2_03.csv"
LAST_FILE_POOL="$PROJECT_DIR/data/comp_eth_sushiswap_v2_03_last.csv"
last_iso_pool=$(tail -n 1 "$DATA_FILE_POOL" | cut -d',' -f1)
if [[ "$last_iso_pool" == "timestamp" ]] || [[ -z "$last_iso_pool" ]]; then
  start_ts_pool=1546300800
  echo "[INFO] CSV comp_eth_sushi_v2 vide, démarrage depuis la date par défaut."
else
  start_ts_pool=$(( $(date -d "$last_iso_pool" +"%s") + 1 ))
fi
echo "[INFO] Timestamp comp_eth_sushi_v2 : $start_ts_pool"
cryo logs --address 0x31503dCb60119A812feE820bb7042752019F2355 --rpc $RPC --output-dir "$OUTPUT_DIR" --csv --timestamps ${start_ts_pool}: \
  || echo "[WARNING] cryo comp_eth_sushi_v2 a rencontré un problème..."
if ls "$OUTPUT_DIR"/*.csv >/dev/null 2>&1; then
  python3 "$PROJECT_DIR/scripts/comp_eth_sushiswap_v2_03.py" || echo "[WARNING] Échec comp_eth_sushiswap_v2_03.py"
else
  echo "[WARNING] Aucun CSV cryo pour comp_eth_sushi_v2, aucun traitement."
fi
rm -rf "$OUTPUT_DIR"/* || true
python3 "$PROJECT_DIR/scripts/dedup_concat.py" "$LAST_FILE_POOL" "$DATA_FILE_POOL" \
  || echo "[WARNING] Échec dedup_concat pour $(basename $DATA_FILE_POOL)" >&2

# 10. MAJ README
echo "[INFO] Lancement de generate_readme.py..."
python3 "$PROJECT_DIR/scripts/generate_readme.py" || echo "[WARNING] Impossible de mettre à jour le README." >&2
echo "[INFO] Generate_readme terminé"

# 11. SCP
MAX=5
SCP_OK=false
for i in $(seq 1 $MAX); do
  echo "[INFO] Tentative #$i..."
  if scp data/{chainlink_comp_usd.csv,comp_usdc_uniswap_v3_03.csv,comp_usdt_uniswap_v3_03.csv,comp_weth_uniswap_v3_03.csv,comp_weth_uniswap_v2_03.csv,comp_eth_sushiswap_v2_03.csv} debian@extract.lan.text-analytics.ch:/data/ethereum/prices; then
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

# 12. Commit & Push
git add README.md
git commit -m "Update data" || echo "[WARNING] Rien à committer ou échec du commit."
git pull --rebase origin main || echo "[WARNING] git pull --rebase avant push a échoué."
git push origin main || echo "[WARNING] git push échoué (clé SSH ?). Données mises à jour localement."

sleep 3
echo "=== Fin du script ==="
