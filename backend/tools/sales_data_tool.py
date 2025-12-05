"""
Sales Data Tool

Access to historical sales data.

API:
get_aggregated_sales(
    date_range: DateRange,
    grain: List[str]  # [date, channel, department, promo_flag]
) -> DataFrame
"""

from typing import List, Optional, Tuple
from datetime import date
from pathlib import Path
from functools import lru_cache

import pandas as pd
from pandas import DataFrame

from models.schemas import DateRange


class SalesDataTool:
    """Tool for accessing historical sales data."""
    
    def __init__(self, db_connection=None, data_path: Optional[str] = None, database_url: Optional[str] = None):
        """
        Initialize Sales Data Tool.
        
        Args:
            db_connection: Database connection object (legacy)
            data_path: Optional path to a CSV file with aggregated sales
            database_url: Optional database URL (e.g., "duckdb:///path/to/db" or "postgresql://...")
        """
        self.db_connection = db_connection
        self.database_url = database_url
        default_path = Path(__file__).resolve().parents[1] / "data" / "sample_sales.csv"
        self.data_path = Path(data_path) if data_path else default_path
        if not self.database_url and not self.data_path.exists():
            raise FileNotFoundError(f"Sample sales data not found at {self.data_path}")

    def _load_dataframe(self) -> DataFrame:
        """Load sales data from database or CSV."""
        # Try database first if configured
        if self.database_url:
            try:
                return self._load_from_database()
            except Exception:
                # Fall back to CSV if database fails
                pass
        
        # Load from CSV
        if self.data_path.exists():
            df = pd.read_csv(self.data_path, parse_dates=["date"])
            df["channel"] = df["channel"].str.lower()
            df["department"] = df["department"].str.upper()
            df["promo_flag"] = df["promo_flag"].astype(str)
            return df
        
        return pd.DataFrame()
    
    def _load_from_database(self) -> DataFrame:
        """Load sales data from database."""
        import os
        from sqlalchemy import create_engine, text
        
        database_url = self.database_url or os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("No database URL configured")
        
        if database_url.startswith('duckdb://'):
            import duckdb
            db_path = database_url.replace('duckdb://', '')
            conn = duckdb.connect(db_path)
            df = conn.execute("SELECT * FROM sales_aggregated").df()
            conn.close()
        else:
            engine = create_engine(database_url)
            with engine.connect() as conn:
                df = pd.read_sql(text("SELECT * FROM sales_aggregated"), conn)
        
        # Standardize columns
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        if "channel" in df.columns:
            df["channel"] = df["channel"].str.lower()
        if "department" in df.columns:
            df["department"] = df["department"].str.upper()
        if "promo_flag" in df.columns:
            df["promo_flag"] = df["promo_flag"].astype(str)
        
        return df

    def _filter_dataframe(
        self,
        date_range: Tuple[date, date],
        filters: Optional[dict] = None
    ) -> DataFrame:
        """Filter the cached dataframe by date range and optional filters."""
        df = self._load_dataframe()
        start_date, end_date = date_range
        mask = (df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))
        filtered = df.loc[mask].copy()

        if filters:
            if channel := filters.get("channel"):
                filtered = filtered[filtered["channel"] == channel.lower()]
            if department := filters.get("department"):
                filtered = filtered[filtered["department"] == department.upper()]
            if promo_flag := filters.get("promo_flag"):
                filtered = filtered[filtered["promo_flag"] == str(promo_flag)]
        return filtered
    
    def get_aggregated_sales(
        self,
        date_range: Tuple[date, date],
        grain: List[str],
        filters: Optional[dict] = None
    ) -> DataFrame:
        """
        Get aggregated sales data.
        
        Args:
            date_range: Tuple of (start_date, end_date)
            grain: List of aggregation dimensions (date, channel, department, promo_flag)
            filters: Optional dictionary of filters
        
        Returns:
            DataFrame with aggregated sales data
        """
        if not grain:
            raise ValueError("At least one grain dimension is required")

        df = self._filter_dataframe(date_range, filters)
        agg_df = (
            df.groupby(grain, dropna=False)
            .agg(
                sales_value=("sales_value", "sum"),
                margin_value=("margin_value", "sum"),
                units=("units", "sum"),
                discount_pct=("discount_pct", "mean"),
            )
            .reset_index()
        )
        return agg_df
    
    def get_daily_sales(
        self,
        date_range: Tuple[date, date],
        channel: Optional[str] = None,
        department: Optional[str] = None
    ) -> DataFrame:
        """
        Get daily sales data.
        
        Args:
            date_range: Tuple of (start_date, end_date)
            channel: Optional channel filter
            department: Optional department filter
        
        Returns:
            DataFrame with daily sales data
        """
        filters = {
            "channel": channel.lower() if channel else None,
            "department": department.upper() if department else None,
        }
        df = self._filter_dataframe(date_range, filters)
        daily_df = (
            df.groupby("date")
            .agg(
                sales_value=("sales_value", "sum"),
                margin_value=("margin_value", "sum"),
                units=("units", "sum"),
            )
            .reset_index()
        )
        return daily_df
