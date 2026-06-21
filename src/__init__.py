"""
Enterprise AI Control Tower — core package.

This package contains the modular engines that power the control tower:

- data_loader : loads and validates synthetic business datasets
- kpi_engine  : computes business KPIs
- risk_engine : detects business risks
- ai_summary  : generates AI executive summaries
- assistant   : AI manager assistant

Each module is developed and integrated independently. See the development
roadmap in ``docs/development_roadmap.md`` for stage details.
"""

__version__ = "0.1.0"
