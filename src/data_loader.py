"""
Data Loader module.

Loads, validates, and prepares the synthetic business datasets used by the
Enterprise AI Control Tower:

- invoices.csv
- customer_tickets.csv
- approval_requests.csv
- risk_rules.csv

Each loader function checks that the file exists, validates that all required
columns are present, converts date and numeric columns to appropriate types, and
returns a clean pandas DataFrame. Validation failures raise ``DataLoadingError``
with a clear message.

This module is intentionally focused on loading and validation only. It does NOT
compute KPIs, classify risk, or call any external API.
"""

from __future__ import annotations

import os
from typing import Dict, List

import pandas as pd


class DataLoadingError(Exception):
    """Raised when a dataset cannot be loaded or fails validation."""


# --------------------------------------------------------------------------- #
# Column specifications
# --------------------------------------------------------------------------- #

INVOICE_COLUMNS: List[str] = [
    "invoice_id",
    "vendor_name",
    "department",
    "invoice_date",
    "due_date",
    "amount_usd",
    "currency",
    "approval_status",
    "payment_status",
    "assigned_approver",
    "days_overdue",
    "invoice_category",
    "priority_level",
]
INVOICE_DATE_COLUMNS: List[str] = ["invoice_date", "due_date"]
INVOICE_NUMERIC_COLUMNS: List[str] = ["amount_usd", "days_overdue"]

TICKET_COLUMNS: List[str] = [
    "ticket_id",
    "customer_name",
    "department",
    "issue_type",
    "priority",
    "opened_date",
    "sla_deadline",
    "resolved_date",
    "status",
    "assigned_team",
    "response_time_hours",
    "resolution_time_hours",
    "sla_status",
    "customer_segment",
]
TICKET_DATE_COLUMNS: List[str] = ["opened_date", "sla_deadline", "resolved_date"]
TICKET_NUMERIC_COLUMNS: List[str] = ["response_time_hours", "resolution_time_hours"]

APPROVAL_COLUMNS: List[str] = [
    "request_id",
    "request_type",
    "department",
    "requester",
    "approver",
    "requested_date",
    "approval_deadline",
    "approval_status",
    "waiting_days",
    "amount_usd",
    "business_impact",
    "bottleneck_flag",
]
APPROVAL_DATE_COLUMNS: List[str] = ["requested_date", "approval_deadline"]
APPROVAL_NUMERIC_COLUMNS: List[str] = ["waiting_days", "amount_usd"]
APPROVAL_BOOLEAN_COLUMNS: List[str] = ["bottleneck_flag"]

RISK_RULE_COLUMNS: List[str] = [
    "rule_id",
    "rule_name",
    "data_source",
    "condition_description",
    "risk_level",
    "recommended_action",
]


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #

def _load_csv_file(file_path: str, dataset_name: str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame, raising ``DataLoadingError`` on failure.

    Args:
        file_path: Path to the CSV file.
        dataset_name: Human-readable dataset name used in error messages.

    Returns:
        The loaded DataFrame.

    Raises:
        DataLoadingError: If the file is missing or cannot be parsed.
    """
    if not os.path.exists(file_path):
        raise DataLoadingError(
            f"{dataset_name}: file not found at '{file_path}'. "
            "Run 'python scripts/generate_synthetic_data.py' to generate it."
        )
    try:
        return pd.read_csv(file_path)
    except Exception as exc:  # pragma: no cover - defensive
        raise DataLoadingError(
            f"{dataset_name}: failed to read CSV at '{file_path}': {exc}"
        ) from exc


def _validate_columns(
    df: pd.DataFrame, required_columns: List[str], dataset_name: str
) -> None:
    """Validate that all required columns are present in the DataFrame.

    Raises:
        DataLoadingError: If any required column is missing.
    """
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise DataLoadingError(
            f"{dataset_name}: missing required column(s): {', '.join(missing)}"
        )


def _convert_date_columns(
    df: pd.DataFrame, date_columns: List[str], dataset_name: str
) -> pd.DataFrame:
    """Convert the given columns to pandas datetime (invalid values -> NaT).

    Empty / missing values are handled safely and become ``NaT``.
    """
    for col in date_columns:
        try:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        except Exception as exc:  # pragma: no cover - defensive
            raise DataLoadingError(
                f"{dataset_name}: failed to convert date column '{col}': {exc}"
            ) from exc
    return df


def _convert_numeric_columns(
    df: pd.DataFrame, numeric_columns: List[str], dataset_name: str
) -> pd.DataFrame:
    """Convert the given columns to numeric values (invalid values -> NaN)."""
    for col in numeric_columns:
        try:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        except Exception as exc:  # pragma: no cover - defensive
            raise DataLoadingError(
                f"{dataset_name}: failed to convert numeric column '{col}': {exc}"
            ) from exc
    return df


def _convert_boolean_columns(
    df: pd.DataFrame, boolean_columns: List[str], dataset_name: str
) -> pd.DataFrame:
    """Convert the given columns to boolean values.

    Handles common textual representations ("True"/"False", "1"/"0", etc.).
    """
    true_values = {"true", "1", "yes", "y", "t"}
    for col in boolean_columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(true_values)
        )
    return df


# --------------------------------------------------------------------------- #
# Public loaders
# --------------------------------------------------------------------------- #

def load_invoices(data_dir: str = "data") -> pd.DataFrame:
    """Load and validate the invoices dataset."""
    name = "invoices"
    path = os.path.join(data_dir, "invoices.csv")
    df = _load_csv_file(path, name)
    _validate_columns(df, INVOICE_COLUMNS, name)
    df = _convert_date_columns(df, INVOICE_DATE_COLUMNS, name)
    df = _convert_numeric_columns(df, INVOICE_NUMERIC_COLUMNS, name)
    return df


def load_customer_tickets(data_dir: str = "data") -> pd.DataFrame:
    """Load and validate the customer tickets dataset.

    Note: ``resolved_date`` may be missing for unresolved tickets; such values
    are safely converted to ``NaT``.
    """
    name = "customer_tickets"
    path = os.path.join(data_dir, "customer_tickets.csv")
    df = _load_csv_file(path, name)
    _validate_columns(df, TICKET_COLUMNS, name)
    df = _convert_date_columns(df, TICKET_DATE_COLUMNS, name)
    df = _convert_numeric_columns(df, TICKET_NUMERIC_COLUMNS, name)
    return df


def load_approval_requests(data_dir: str = "data") -> pd.DataFrame:
    """Load and validate the approval requests dataset."""
    name = "approval_requests"
    path = os.path.join(data_dir, "approval_requests.csv")
    df = _load_csv_file(path, name)
    _validate_columns(df, APPROVAL_COLUMNS, name)
    df = _convert_date_columns(df, APPROVAL_DATE_COLUMNS, name)
    df = _convert_numeric_columns(df, APPROVAL_NUMERIC_COLUMNS, name)
    df = _convert_boolean_columns(df, APPROVAL_BOOLEAN_COLUMNS, name)
    return df


def load_risk_rules(data_dir: str = "data") -> pd.DataFrame:
    """Load and validate the risk rules reference table."""
    name = "risk_rules"
    path = os.path.join(data_dir, "risk_rules.csv")
    df = _load_csv_file(path, name)
    _validate_columns(df, RISK_RULE_COLUMNS, name)
    return df


def load_all_data(data_dir: str = "data") -> Dict[str, pd.DataFrame]:
    """Load all datasets and return them in a dictionary.

    Returns:
        A dictionary with keys ``invoices``, ``customer_tickets``,
        ``approval_requests``, and ``risk_rules``.
    """
    return {
        "invoices": load_invoices(data_dir),
        "customer_tickets": load_customer_tickets(data_dir),
        "approval_requests": load_approval_requests(data_dir),
        "risk_rules": load_risk_rules(data_dir),
    }
