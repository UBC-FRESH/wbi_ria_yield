"""Helpers for summarizing Patchworks account/target coverage surfaces."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

_YIELD_SPECIES_PATTERN = re.compile(r"^product\.Yield\.managed\.([^.]+)$")
_HARVEST_SPECIES_PATTERN = re.compile(
    r"^product\.HarvestedVolume\.managed\.([^.]+)\.CC$"
)
_FEATURE_SERAL_PATTERN = re.compile(r"^feature\.Seral\.([^.]+)\.([^.]+)$")
_PRODUCT_SERAL_PATTERN = re.compile(r"^product\.Seral\.area\.([^.]+)\.([^.]+)\.CC$")


def summarize_account_surface(accounts_csv_path: Path) -> dict[str, Any]:
    """Build species/AU account coverage summary from tracks/accounts.csv."""
    accounts: set[str] = set()
    with accounts_csv_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            account = str(row.get("ACCOUNT", "")).strip()
            if account:
                accounts.add(account)

    species_summary: dict[str, dict[str, Any]] = {}
    au_summary: dict[str, dict[str, Any]] = {}
    for account in sorted(accounts):
        yield_match = _YIELD_SPECIES_PATTERN.match(account)
        if yield_match:
            species = yield_match.group(1)
            item = species_summary.setdefault(
                species,
                {"yield_account_present": False, "harvest_cc_account_present": False},
            )
            item["yield_account_present"] = True
            continue

        harvest_match = _HARVEST_SPECIES_PATTERN.match(account)
        if harvest_match:
            species = harvest_match.group(1)
            item = species_summary.setdefault(
                species,
                {"yield_account_present": False, "harvest_cc_account_present": False},
            )
            item["harvest_cc_account_present"] = True
            continue

        feature_seral_match = _FEATURE_SERAL_PATTERN.match(account)
        if feature_seral_match:
            stage = feature_seral_match.group(1)
            au = feature_seral_match.group(2)
            item = au_summary.setdefault(
                au,
                {
                    "feature_seral_stages": [],
                    "product_seral_cc_stages": [],
                    "feature_seral_count": 0,
                    "product_seral_cc_count": 0,
                },
            )
            stages = item["feature_seral_stages"]
            if stage not in stages:
                stages.append(stage)
            continue

        product_seral_match = _PRODUCT_SERAL_PATTERN.match(account)
        if product_seral_match:
            stage = product_seral_match.group(1)
            au = product_seral_match.group(2)
            item = au_summary.setdefault(
                au,
                {
                    "feature_seral_stages": [],
                    "product_seral_cc_stages": [],
                    "feature_seral_count": 0,
                    "product_seral_cc_count": 0,
                },
            )
            stages = item["product_seral_cc_stages"]
            if stage not in stages:
                stages.append(stage)

    complete_species = 0
    missing_yield: list[str] = []
    missing_harvest_cc: list[str] = []
    for species in sorted(species_summary):
        row = species_summary[species]
        if row["yield_account_present"] and row["harvest_cc_account_present"]:
            complete_species += 1
        if not row["yield_account_present"]:
            missing_yield.append(species)
        if not row["harvest_cc_account_present"]:
            missing_harvest_cc.append(species)

    for au in sorted(au_summary):
        item = au_summary[au]
        item["feature_seral_stages"] = sorted(item["feature_seral_stages"])
        item["product_seral_cc_stages"] = sorted(item["product_seral_cc_stages"])
        item["feature_seral_count"] = len(item["feature_seral_stages"])
        item["product_seral_cc_count"] = len(item["product_seral_cc_stages"])

    return {
        "accounts_path": str(accounts_csv_path),
        "total_accounts": len(accounts),
        "target_count_inferred": len(accounts),
        "species_count": len(species_summary),
        "species_complete_count": complete_species,
        "species_missing_yield": missing_yield,
        "species_missing_harvest_cc": missing_harvest_cc,
        "species": species_summary,
        "au_count": len(au_summary),
        "au": au_summary,
    }
