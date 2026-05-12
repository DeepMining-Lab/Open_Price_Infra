# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH

import csv
import logging
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateError

def get_last_csv_timestamp(
    path: Path,
    col_name: str,
    datetime_format: str | None = None,
    tz_aware: bool = False
) -> datetime | str | None:
    try:
        with path.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            try:
                last_row = deque(reader, maxlen=1)[0]
            except IndexError:
                logging.warning("CSV vide ou sans en-têtes : %s", path)
                return None
            last_value = last_row.get(col_name)
            if last_value is None:
                logging.warning("Colonne '%s' introuvable dans %s", col_name, path)
                return None
    except FileNotFoundError:
        logging.error("Fichier non trouvé : %s", path)
        return None
    except csv.Error as e:
        logging.error("Erreur CSV pour %s : %s", path, e)
        return None

    if datetime_format:
        try:
            dt = datetime.strptime(last_value, datetime_format)
        except ValueError as e:
            logging.error(
                "Impossible de parser '%s' avec le format '%s' : %s",
                last_value, datetime_format, e
            )
            return None
        return dt if tz_aware else dt.replace(tzinfo=None)

    return last_value

TEMPLATE_DIR = Path(__file__).parent
TEMPLATE_NAME = "README.tpl.md"
OUTPUT_PATH = TEMPLATE_DIR.parent / "README.md"

data_info = {
    "usdc": {
        "path": TEMPLATE_DIR.parent / "data" / "chainlink_usdc_usd.csv",
        "col_name": "datetime_utc",
        "fmt": "%Y-%m-%d %H:%M:%S+00:00",
        "tz_aware": False,
    },
    "usdt": {
        "path": TEMPLATE_DIR.parent / "data" / "chainlink_usdt_usd.csv",
        "col_name": "datetime_utc",
        "fmt": "%Y-%m-%d %H:%M:%S+00:00",
        "tz_aware": False,
    },
}

context: dict[str, dict[str, str]] = {}
for name, info in data_info.items():
    last_ts = get_last_csv_timestamp(
        info["path"],
        col_name=info["col_name"],
        datetime_format=info.get("fmt"),
        tz_aware=info.get("tz_aware", False)
    )

    if isinstance(last_ts, datetime):
        display_ts = last_ts.strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    else:
        display_ts = last_ts or "N/A"

    context[name] = {"extraction": display_ts}

try:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        keep_trailing_newline=True
    )
    template = env.get_template(TEMPLATE_NAME)
    rendered = template.render(**context)
    OUTPUT_PATH.write_text(rendered, encoding='utf-8')
    logging.info("README généré à %s", OUTPUT_PATH)
except (TemplateError, OSError) as e:
    logging.exception("Échec de génération du README : %s", e)
