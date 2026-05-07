#!/usr/bin/env bash

cd /app/aave || exit 1

RPC=${RPC:-"http://172.30.122.3:8552"}
export RPC

INTERVAL_DAYS=${INTERVAL_DAYS:-0}

if [[ ! "$INTERVAL_DAYS" =~ ^[0-9]+$ ]] || [[ "$INTERVAL_DAYS" -lt 0 ]]; then
  echo "ERREUR: L'intervalle doit être un nombre positif de jours" >&2
  exit 1
fi

INTERVAL=$(( INTERVAL_DAYS * 24 * 60 * 60 ))

trap "echo 'Arrêt du conteneur'; exit 0" SIGTERM SIGINT

echo "=== Démarrage initial ==="
./scripts/update.sh

while [[ "$INTERVAL" -gt 0 ]]; do
  echo "=== Prochaine exécution dans $INTERVAL_DAYS jours ==="
  sleep "$INTERVAL"
  echo "=== Démarrage planifié ==="
  ./scripts/update.sh
done
