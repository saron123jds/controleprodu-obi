from __future__ import annotations

from dash import dash_table, html
import pandas as pd

from .atrasos import render_atrasos
from .configuracoes import render_configuracoes
from .home import render_home
from .metas import render_metas
from .processos import render_processos
from .produtos import render_produtos


def _section(title: str, content: html.Div) -> html.Div:
    return html.Div(
        [
            html.H3(title, className="section-title"),
            content,
        ],
        className="section",
    )


def _data_table(df: pd.DataFrame) -> html.Div:
    if df.empty:
        return html.Div("Nenhum dado carregado.", className="muted")

    preview = df.head(200)
    return dash_table.DataTable(
        data=preview.to_dict("records"),
        columns=[{"name": col, "id": col} for col in preview.columns],
        page_size=15,
        style_table={"overflowX": "auto"},
        style_cell={
            "backgroundColor": "var(--panel)",
            "color": "var(--text)",
            "border": "1px solid var(--panel-2)",
            "fontFamily": "Inter, sans-serif",
            "fontSize": "12px",
            "padding": "8px",
        },
        style_header={
            "backgroundColor": "var(--panel-2)",
            "fontWeight": "600",
            "color": "var(--text)",
        },
    )


def render_painel(
    df: pd.DataFrame,
    settings: dict,
    brands: list[str],
    admin_auth: bool,
    critical_delay_days: int,
    upload_history: list[dict],
    data_quality_alerts: list[str],
) -> html.Div:
    admin_panel = html.Div(
        [
            html.Div(
                [
                    html.Label("Senha do admin"),
                    html.Div(
                        [
                            html.Input(
                                id="admin-password",
                                type="password",
                                placeholder="Digite a senha",
                                className="admin-input",
                            ),
                            html.Button("Entrar", id="btn-admin-login", className="primary-btn"),
                        ],
                        className="admin-login",
                    ),
                    html.Div(id="admin-status", className="status-line"),
                ],
                className="card",
            ),
            html.Div(
                [
                    render_configuracoes(brands, settings, admin_auth, upload_history),
                ],
                className="admin-config",
            ),
        ],
        className="admin-panel",
    )

    return html.Div(
        [
            _section("Visão Geral", render_home(df, data_quality_alerts)),
            _section("Processos", render_processos(df)),
            _section("Produtos", render_produtos(df)),
            _section("Atrasos", render_atrasos(df, critical_delay_days)),
            _section("Metas", render_metas(df, settings)),
            _section("Dados", html.Div(_data_table(df), className="card")),
            _section("Painel do Admin", admin_panel),
        ],
        className="page",
    )
