from typing import Optional

import streamlit as st
from supabase import Client, create_client


class UsageCounter:
    """
    Privacy-safe aggregate usage counter.

    Stores only aggregate counts:
    - total_sessions
    - test_generations
    - aggregate source session counts
    - aggregate source generation counts

    No user identity or user-entered content is stored.
    """

    ALLOWED_METRICS = {
        "total_sessions",
        "test_generations",
    }

    ALLOWED_SOURCES = {
        "github",
        "hackernoon",
        "linkedin",
        "reddit",
        "direct",
    }

    def __init__(self) -> None:
        self.client: Optional[Client] = None

        try:
            supabase_url = st.secrets["supabase"]["url"]
            supabase_key = st.secrets["supabase"]["key"]

            self.client = create_client(
                supabase_url,
                supabase_key,
            )

        except Exception:
            self.client = None

    def normalize_source(
        self,
        source: str | None,
    ) -> str:
        if not source:
            return "direct"

        normalized = source.strip().lower()

        if normalized in self.ALLOWED_SOURCES:
            return normalized

        return "direct"

    def increment(
        self,
        metric_name: str,
    ) -> None:
        if self.client is None:
            return

        if metric_name not in self.ALLOWED_METRICS:
            return

        try:
            self.client.rpc(
                "increment_metric",
                {
                    "metric": metric_name,
                },
            ).execute()

        except Exception:
            pass

    def increment_source_session(
        self,
        source: str | None,
    ) -> None:
        if self.client is None:
            return

        normalized_source = self.normalize_source(
            source
        )

        try:
            self.client.rpc(
                "increment_source_session",
                {
                    "source": normalized_source,
                },
            ).execute()

        except Exception:
            pass

    def increment_source_generation(
        self,
        source: str | None,
    ) -> None:
        if self.client is None:
            return

        normalized_source = self.normalize_source(
            source
        )

        try:
            self.client.rpc(
                "increment_source_generation",
                {
                    "source": normalized_source,
                },
            ).execute()

        except Exception:
            pass

    def get_count(
        self,
        metric_name: str,
    ) -> int:
        if self.client is None:
            return 0

        if metric_name not in self.ALLOWED_METRICS:
            return 0

        try:
            response = (
                self.client
                .table("app_metrics")
                .select("count")
                .eq(
                    "metric_name",
                    metric_name,
                )
                .single()
                .execute()
            )

            if response.data:
                return int(
                    response.data["count"]
                )

        except Exception:
            pass

        return 0