from typing import Optional

import streamlit as st
from supabase import Client, create_client


class UsageCounter:
    """
    Privacy-safe aggregate usage counter.

    Only two aggregate metrics are supported:
    - total_sessions
    - test_generations

    No user-entered requirement text, uploaded files,
    IP addresses, names, emails, or other personal
    information are stored.
    """

    ALLOWED_METRICS = {
        "total_sessions",
        "test_generations",
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
            # Analytics must never prevent Spec2Test
            # from running.
            self.client = None

    def increment(
        self,
        metric_name: str,
    ) -> None:
        """
        Atomically increments an approved aggregate metric.
        """

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
            # A metrics failure should never break
            # test generation.
            pass

    def get_count(
        self,
        metric_name: str,
    ) -> int:
        """
        Returns the current value of an approved metric.
        """

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