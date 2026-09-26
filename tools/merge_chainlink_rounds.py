#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH
"""
merge_chainlink_rounds.py — Ajoute à un CSV Chainlink les rounds qui lui manquent.

Sert aux rattrapages : on relance chainlink_<feed>.py avec un --debut ancien (sortie dans un
dossier de travail, jamais dans data/), puis on fusionne cette ré-extraction dans le CSV.

  - clé d'un round : global_round_id ;
  - les rounds présents des deux côtés doivent être identiques (sinon la fusion est refusée) ;
  - les lignes existantes ne sont pas modifiées ni réordonnées : les nouvelles lignes sont insérées
    à leur place chronologique (round_updated_at_utc), après les lignes existantes de même horodatage ;
  - seul l'historique est complété : les rounds plus récents que la dernière ligne sont laissés à
    l'extraction quotidienne ;
  - écriture atomique (fichier .tmp puis os.replace), refusée si le CSV a changé pendant la fusion.

Sans --apply, le script n'écrit rien et affiche ce qu'il ferait.

Usage: python3 merge_chainlink_rounds.py <extraction.csv> <data.csv> [--apply --backup-dir DIR]
"""

import argparse
import csv
import os
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone

KEY = "global_round_id"
TS = "round_updated_at_utc"
COMPARED = ["phase", "aggregator_round", TS, "answer_raw", "answered_in_round", "round_started_at_utc"]


def read_rows(path):
    """(header, [(ligne brute, champs)]) ; les lignes brutes gardent leur fin de ligne d'origine."""
    with open(path, newline="", encoding="utf-8") as f:
        lines = f.readlines()
    eol = "\r\n" if lines[0].endswith("\r\n") else "\n"
    lines = [line if line.endswith("\n") else line + eol for line in lines]
    header = next(csv.reader([lines[0]]))
    rows = [(line, next(csv.reader([line]))) for line in lines[1:] if line.strip()]
    return lines[0], header, rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("extraction", help="CSV produit par chainlink_<feed>.py (ré-extraction)")
    ap.add_argument("data", help="CSV Chainlink à compléter")
    ap.add_argument("--apply", action="store_true", help="écrire le CSV fusionné (sinon simulation)")
    ap.add_argument("--backup-dir", help="dossier où copier le CSV d'origine avant écriture (obligatoire avec --apply)")
    args = ap.parse_args()
    if args.apply and not args.backup_dir:
        ap.error("--apply exige --backup-dir")

    stat_before = os.stat(args.data)
    header_line, header, data_rows = read_rows(args.data)
    _, ext_header, ext_rows = read_rows(args.extraction)
    if header != ext_header:
        sys.exit("[ERROR] Les deux fichiers n'ont pas le même header.")
    col = {name: i for i, name in enumerate(header)}

    # Le CSV doit être trié par horodatage pour une insertion à la bonne place
    for (_, prev), (_, cur) in zip(data_rows, data_rows[1:]):
        if cur[col[TS]] < prev[col[TS]]:
            sys.exit(f"[ERROR] {args.data} n'est pas trié par {TS} ({prev[col[TS]]} puis {cur[col[TS]]}).")

    existing = {fields[col[KEY]]: fields for _, fields in data_rows}
    extracted = {}
    for line, fields in ext_rows:
        extracted.setdefault(fields[col[KEY]], (line, fields))

    mismatches = [(key, existing[key], fields) for key, (_, fields) in extracted.items()
                  if key in existing and any(existing[key][col[c]] != fields[col[c]] for c in COMPARED)]
    missing = [v for k, v in extracted.items() if k not in existing]
    # Les rounds plus récents que la dernière ligne relèvent de l'extraction quotidienne : on ne prolonge pas le fichier
    last_ts = data_rows[-1][1][col[TS]] if data_rows else ""
    recent = [v for v in missing if v[1][col[TS]] > last_ts]
    new = sorted((v for v in missing if v[1][col[TS]] <= last_ts),
                 key=lambda v: (v[1][col[TS]], int(v[1][col["phase"]]), int(v[1][col["aggregator_round"]])))
    only_in_data = [k for k in existing if k not in extracted]

    print(f"[INFO] {os.path.basename(args.data)} : {len(data_rows)} lignes ; ré-extraction : {len(ext_rows)} lignes")
    print(f"[INFO] rounds communs : {len(existing) - len(only_in_data)}, dont {len(mismatches)} différent(s)")
    print(f"[INFO] rounds absents de la ré-extraction : {len(only_in_data)}")
    by_phase = Counter(fields[col["phase"]] for _, fields in new)
    for phase in sorted(by_phase, key=int):
        ts = [fields[col[TS]] for _, fields in new if fields[col["phase"]] == phase]
        print(f"[INFO] à ajouter — phase {phase} : {by_phase[phase]} rounds, {min(ts)} → {max(ts)}")
    print(f"[INFO] total à ajouter : {len(new)}")
    if recent:
        print(f"[INFO] {len(recent)} round(s) plus récent(s) que la dernière ligne ({last_ts}) : laissé(s) à l'extraction quotidienne")
    for key, old, fields in mismatches[:10]:
        print(f"[WARNING] round {key} différent : " +
              ", ".join(f"{c}={old[col[c]]}≠{fields[col[c]]}" for c in COMPARED if old[col[c]] != fields[col[c]]))

    if not args.apply:
        print("[INFO] Simulation : rien n'a été écrit (--apply pour fusionner).")
        return
    if mismatches:
        sys.exit("[ERROR] Des rounds communs diffèrent : fusion refusée.")
    if not new:
        print("[INFO] Rien à ajouter.")
        return

    os.makedirs(args.backup_dir, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = os.path.join(args.backup_dir, f"{os.path.basename(args.data)}.{stamp}")
    shutil.copy2(args.data, backup)
    print(f"[INFO] Copie de sauvegarde : {backup}")

    tmp = args.data + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as out:
        out.write(header_line)
        i = 0
        for line, fields in data_rows:
            while i < len(new) and new[i][1][col[TS]] < fields[col[TS]]:
                out.write(new[i][0])
                i += 1
            out.write(line)
        for line, _ in new[i:]:
            out.write(line)
    shutil.copymode(args.data, tmp)

    stat_now = os.stat(args.data)
    if (stat_now.st_size, stat_now.st_mtime_ns) != (stat_before.st_size, stat_before.st_mtime_ns):
        os.remove(tmp)
        sys.exit("[ERROR] Le CSV a changé pendant la fusion (extraction en cours ?) : rien n'a été écrit.")
    os.replace(tmp, args.data)
    print(f"[INFO] Terminé : {len(data_rows) + len(new)} lignes dans {os.path.basename(args.data)} (+{len(new)}).")


if __name__ == "__main__":
    main()
