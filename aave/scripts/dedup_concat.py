#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH
"""
dedup_concat.py — Fusionne <last_file> dans <data_file> avec déduplication
par (pool_address, transaction_hash, log_index).

En cas de doublon, conserve la ligne ayant le plus de champs non-nuls
(i.e. la ligne enrichie issue du script corrigé).
Écrit le résultat de façon atomique via un fichier temporaire.
Supprime <last_file> après fusion réussie.

Usage: python3 dedup_concat.py <last_file> <data_file>
"""

import sys
import os
import pandas as pd

DEDUP_KEY = ['pool_address', 'transaction_hash', 'log_index']


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <last_file> <data_file>", file=sys.stderr)
        sys.exit(1)

    last_file = sys.argv[1]
    data_file = sys.argv[2]

    # Si last_file n'existe pas : rien à faire (comportement identique à concat_with_header_sync)
    if not os.path.isfile(last_file):
        print(f"[WARNING] {last_file} non trouvé, aucune concaténation effectuée.")
        sys.exit(0)

    if not os.path.isfile(data_file):
        print(f"[ERROR] {data_file} non trouvé.", file=sys.stderr)
        sys.exit(1)

    base_last = os.path.basename(last_file)
    base_data = os.path.basename(data_file)
    print(f"[INFO] dedup_concat: fusion de {base_last} dans {base_data}...")

    df_data = pd.read_csv(data_file, low_memory=False)
    df_last = pd.read_csv(last_file, low_memory=False)

    n_data = len(df_data)
    n_last = len(df_last)
    print(f"[INFO] {base_data}: {n_data} lignes existantes")
    print(f"[INFO] {base_last}: {n_last} nouvelles lignes")

    # Vérifier que la clé de dédup existe dans les deux DataFrames
    key_missing = [c for c in DEDUP_KEY if c not in df_data.columns or c not in df_last.columns]
    if key_missing:
        # Fallback : simple append sans dédup (Chainlink, ou CSV sans clé composite)
        print(f"[WARNING] Colonnes manquantes pour dédup ({key_missing}) — fallback append simple.")
        # Synchroniser le header si besoin
        if list(df_data.columns) != list(df_last.columns):
            print(f"[WARNING] Schema mismatch — header mis à jour depuis {base_last}.")
            df_data.columns = df_last.columns[:len(df_data.columns)]
        combined = pd.concat([df_data, df_last], ignore_index=True)
        _write_atomic(combined, data_file)
        os.remove(last_file)
        print(f"[INFO] Terminé (append simple): {len(combined)} lignes.")
        return

    # Synchroniser le header si besoin
    if list(df_data.columns) != list(df_last.columns):
        print(f"[WARNING] Schema mismatch pour {base_data} — header mis à jour depuis {base_last}.")
        df_data = df_data.reindex(columns=df_last.columns)

    # Normaliser la casse des clés
    for df in (df_data, df_last):
        df['pool_address']     = df['pool_address'].astype(str).str.lower().str.strip()
        df['transaction_hash'] = df['transaction_hash'].astype(str).str.lower().str.strip()
        df['log_index']        = pd.to_numeric(df['log_index'], errors='coerce')

    # Score de complétude : nombre de champs non-nuls par ligne
    df_data['_score'] = df_data.notna().sum(axis=1)
    df_last['_score'] = df_last.notna().sum(axis=1)

    # Fusion
    combined = pd.concat([df_data, df_last], ignore_index=True)
    n_before = len(combined)

    # Tri : clé composite croissante, score décroissant → keep='first' garde la ligne la plus complète
    combined = combined.sort_values(
        DEDUP_KEY + ['_score'],
        ascending=[True, True, True, False]
    )
    combined = combined.drop_duplicates(subset=DEDUP_KEY, keep='first')
    n_after = len(combined)
    n_removed = n_before - n_after

    combined = combined.drop(columns=['_score'])

    # Tri final par timestamp
    if 'timestamp' in combined.columns:
        combined = combined.sort_values(
            ['timestamp', 'block_number', 'log_index']
        ).reset_index(drop=True)

    _write_atomic(combined, data_file)
    os.remove(last_file)

    added = n_last - n_removed
    print(f"[INFO] Terminé: {n_after} lignes dans {base_data} "
          f"(+{n_last} nouvelles, -{n_removed} doublons supprimés, net +{added}).")


def _write_atomic(df, path):
    """Écriture atomique via fichier temporaire."""
    tmp = path + '.tmp'
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)


if __name__ == '__main__':
    main()
