from __future__ import annotations

from dash import html
import pandas as pd

from src.pages.home import render_home
from src.pages.processos import render_processos
from src.pages.produtos import render_produtos
from src.pages.atrasos import render_atrasos
from src.pages.metas import render_metas
from src.pages.admin import render_admin_panel


def _section(title: str, content: html.Div) -> html.Div:
    return html.Div(
        [
            html.H3(title, className="section-title"),
            content,
        ],
        className="section",
    )


def render_dashboard(df: pd.DataFrame, settings: dict, admin_auth: bool) -> html.Div:
    critical_delay_days = int(settings.get("critical_delay_days") or 1)
    brands = sorted(df["MARCA"].dropna().unique().tolist()) if not df.empty else []

    return html.Div(
        [
            _section("Visão Geral", render_home(df)),
            _section("Processos", render_processos(df)),
            _section("Produtos", render_produtos(df)),
            _section("Atrasos Críticos", render_atrasos(df, critical_delay_days)),
            _section("Metas", render_metas(df, settings)),
            _section("Admin", render_admin_panel(brands, settings, admin_auth)),
        ],
        className="page",
    )
