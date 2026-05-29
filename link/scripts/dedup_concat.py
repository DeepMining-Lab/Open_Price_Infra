#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH
"""
dedup_concat.py — Fusionne <last_file> dans <data_file> avec déduplication
par (transaction_hash, log_index) à la frontière.

Approche streaming : data_file n'est jamais chargé en mémoire.
Seul last_file (petit, ~quelques MB) est chargé.

Algorithme :
  1. Lit la dernière ligne de data_file pour trouver le bloc frontière.
  2. Charge last_file en mémoire et exclut les lignes déjà présentes à la frontière.
  3. Appende les nouvelles lignes à data_file de façon atomique (fichier .tmp).
  4. Supprime last_file après fusion réussie.

Usage: python3 dedup_concat.py <last_file> <data_file>
"""

import sys
import os
import csv
import shutil
import pandas as pd

BLOCK_COL     = 'block_number'
TX_COL        = 'transaction_hash'
LOG_IDX_COL   = 'log_index'
TIMESTAMP_COL = 'timestamp'


def _last_line(path):
    """Retourne la dernière ligne non-vide d'un fichier (lecture en O(1) mémoire)."""
    with open(path, 'rb') as f:
        f.seek(0, 2)
        size = f.tell()
        if size == 0:
            return b''
        buf_size = min(4096, size)
        f.seek(-buf_size, 2)
        buf = f.read()
    lines = buf.split(b'\n')
    for line in reversed(lines):
        if line.strip():
            return line.decode('utf-8', errors='replace')
    return ''


def _header_columns(path):
    """Retourne la liste des colonnes depuis le header du fichier."""
    with open(path, 'r', newline='') as f:
        reader = csv.reader(f)
        return next(reader, [])


def _count_data_lines(path):
    """Compte les lignes de données (sans le header)."""
    with open(path, 'rb') as f:
        return sum(1 for _ in f) - 1


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <last_file> <data_file>", file=sys.stderr)
        sys.exit(1)

    last_file = sys.argv[1]
    data_file = sys.argv[2]

    if not os.path.isfile(last_file):
        print(f"[WARNING] {last_file} non trouvé, aucune concaténation effectuée.")
        sys.exit(0)

    if not os.path.isfile(data_file):
        print(f"[ERROR] {data_file} non trouvé.", file=sys.stderr)
        sys.exit(1)

    base_last = os.path.basename(last_file)
    base_data = os.path.basename(data_file)
    print(f"[INFO] dedup_concat: fusion de {base_last} dans {base_data}...")

    # --- Charger last_file (petit) ---
    df_last = pd.read_csv(last_file, low_memory=False)
    n_last = len(df_last)
    print(f"[INFO] {base_last}: {n_last} nouvelles lignes")

    if n_last == 0:
        print(f"[INFO] {base_last} vide — rien à fusionner.")
        os.remove(last_file)
        return

    # --- Vérifier le header de data_file ---
    data_cols = _header_columns(data_file)
    last_cols = list(df_last.columns)

    if data_cols != last_cols:
        print(f"[WARNING] Schema mismatch pour {base_data} — header mis à jour depuis {base_last}.")
        # On ne peut pas corriger le header sans relire tout le fichier ;
        # on continue avec le header existant de data_file.

    # --- Lire la dernière ligne de data_file pour trouver la frontière ---
    last_line_str = _last_line(data_file)

    if not last_line_str or last_line_str.startswith(data_cols[0]):
        # data_file est vide (ou seulement le header) : append complet
        print(f"[INFO] {base_data} vide — append complet de {n_last} lignes.")
        _append_df_to_file(df_last, data_file, write_header=True)
        os.remove(last_file)
        print(f"[INFO] Terminé: {n_last} lignes ajoutées.")
        return

    # Parser la dernière ligne pour extraire le bloc frontière et les clés de dédup
    try:
        last_row = dict(zip(data_cols, next(csv.reader([last_line_str]))))
        boundary_block = int(float(last_row.get(BLOCK_COL, -1)))
    except Exception as e:
        print(f"[ERROR] Impossible de parser la dernière ligne de {base_data}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Frontière: bloc {boundary_block}")

    # Normaliser les colonnes de dédup dans last_file
    if TX_COL in df_last.columns:
        df_last[TX_COL] = df_last[TX_COL].astype(str).str.lower().str.strip()
    if LOG_IDX_COL in df_last.columns:
        df_last[LOG_IDX_COL] = pd.to_numeric(df_last[LOG_IDX_COL], errors='coerce')
    if BLOCK_COL in df_last.columns:
        df_last[BLOCK_COL] = pd.to_numeric(df_last[BLOCK_COL], errors='coerce')

    # Identifier les doublons potentiels au bloc frontière
    # (on lit les N dernières lignes de data_file au bloc frontière pour construire le set)
    boundary_keys = _read_boundary_keys(data_file, data_cols, boundary_block)
    print(f"[INFO] {len(boundary_keys)} clé(s) au bloc frontière dans {base_data}.")

    # Filtrer last_file : garder les lignes strictement après la frontière,
    # ou à la frontière mais pas encore présentes
    mask_after    = df_last[BLOCK_COL] > boundary_block
    mask_boundary = df_last[BLOCK_COL] == boundary_block
    if boundary_keys and TX_COL in df_last.columns:
        key_tuples = list(zip(
            df_last[TX_COL].astype(str).str.lower().str.strip(),
            df_last[LOG_IDX_COL]
        ))
        mask_new_at_boundary = mask_boundary & pd.Series(
            [k not in boundary_keys for k in key_tuples], index=df_last.index
        )
    else:
        mask_new_at_boundary = mask_boundary

    df_new = df_last[mask_after | mask_new_at_boundary].copy()
    n_added  = len(df_new)
    n_removed = n_last - n_added

    if n_added == 0:
        print(f"[INFO] Aucune nouvelle ligne à ajouter ({n_removed} doublon(s) ignoré(s)).")
        os.remove(last_file)
        return

    # Tri de df_new (devrait déjà l'être, par sécurité)
    sort_cols = [c for c in [TIMESTAMP_COL, BLOCK_COL, LOG_IDX_COL] if c in df_new.columns]
    if sort_cols:
        df_new = df_new.sort_values(sort_cols).reset_index(drop=True)

    # Append atomique : écrire dans .tmp puis renommer
    tmp_file = data_file + '.tmp'
    shutil.copy2(data_file, tmp_file)
    try:
        _append_df_to_file(df_new, tmp_file, write_header=False)
        os.replace(tmp_file, data_file)
    except Exception as e:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        print(f"[ERROR] Écriture atomique échouée: {e}", file=sys.stderr)
        sys.exit(1)

    os.remove(last_file)
    n_data_approx = _count_data_lines(data_file)
    print(f"[INFO] Terminé: ~{n_data_approx} lignes dans {base_data} "
          f"(+{n_added} nouvelles, -{n_removed} doublons supprimés).")


def _read_boundary_keys(path, columns, boundary_block):
    """
    Lit le fichier en streaming et retourne le set des (tx_hash, log_index)
    présents exactement au bloc boundary_block.
    Utilise O(k) mémoire où k = nombre de lignes au bloc frontière.
    """
    if BLOCK_COL not in columns or TX_COL not in columns or LOG_IDX_COL not in columns:
        return set()

    block_idx   = columns.index(BLOCK_COL)
    tx_idx      = columns.index(TX_COL)
    logidx_idx  = columns.index(LOG_IDX_COL)

    keys = set()
    with open(path, 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if len(row) <= max(block_idx, tx_idx, logidx_idx):
                continue
            try:
                blk = int(float(row[block_idx]))
            except (ValueError, IndexError):
                continue
            if blk == boundary_block:
                try:
                    tx  = row[tx_idx].lower().strip()
                    li  = int(float(row[logidx_idx]))
                    keys.add((tx, li))
                except (ValueError, IndexError):
                    pass
    return keys


def _append_df_to_file(df, path, write_header):
    """Appende df au fichier path (sans index, header optionnel)."""
    with open(path, 'a', newline='') as f:
        df.to_csv(f, index=False, header=write_header)


if __name__ == '__main__':
    main()
