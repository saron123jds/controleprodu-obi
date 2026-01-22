from __future__ import annotations

from dash import dash_table, html
import pandas as pd

from .atrasos import render_atrasos
from .configuracoes import render_configuracoes
from .home import render_home
from .metas import render_metas
from .processos import render_processos
from .produtos import render_produtos


def _module(title: str, subtitle: str, content: html.Div) -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.H3(title, className="module-title"),
                    html.P(subtitle, className="module-subtitle"),
                ],
                className="module-header",
            ),
            html.Div(content, className="module-body"),
        ],
        className="module-card",
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
            html.Div(
                [
                    html.Div(
                        [
                            html.H2("Panorama da Produção", className="hero-title"),
                            html.P(
                                "Acompanhe metas, gargalos e alertas críticos em um único painel.",
                                className="hero-subtitle",
                            ),
                            html.Div(
                                [
                                    html.Div(f"Marcas ativas: {len(brands)}", className="hero-pill"),
                                    html.Div(
                                        f"Alertas de dados: {len(data_quality_alerts)}",
                                        className="hero-pill alert",
                                    ),
                                ],
                                className="hero-pills",
                            ),
                        ],
                        className="hero-card",
                    ),
                    html.Div(
                        [
                            html.H4("Status operacional"),
                            html.P(
                                "Revise os dados enviados e valide o progresso semanal da produção.",
                                className="muted",
                            ),
                            html.Ul(
                                [
                                    html.Li("Conferir uploads recentes"),
                                    html.Li("Ajustar metas e dias úteis"),
                                    html.Li("Atualizar logotipo e branding"),
                                ],
                                className="hero-list",
                            ),
                        ],
                        className="hero-card",
                    ),
                ],
                className="hero-grid",
            ),
            html.Div(
                [
                    _module(
                        "Visão Geral",
                        "Indicadores principais, alertas e tendências.",
                        render_home(df, data_quality_alerts),
                    ),
                    _module(
                        "Processos",
                        "Volume de produção e atraso médio por etapa.",
                        render_processos(df),
                    ),
                    _module(
                        "Produtos",
                        "Distribuição por produto e coleção.",
                        render_produtos(df),
                    ),
                ],
                className="module-grid",
            ),
            html.Div(
                [
                    _module(
                        "Atrasos",
                        "Itens críticos e acompanhamento diário.",
                        render_atrasos(df, critical_delay_days),
                    ),
                    _module(
                        "Metas",
                        "Comparativo entre produção realizada e objetivos.",
                        render_metas(df, settings),
                    ),
                ],
                className="module-grid two-col",
            ),
            html.Div(
                [
                    _module(
                        "Dados",
                        "Prévia dos registros carregados no sistema.",
                        html.Div(_data_table(df), className="card"),
                    ),
                    _module(
                        "Administração",
                        "Configuração de metas, upload e branding.",
                        admin_panel,
                    ),
                ],
                className="module-grid two-col",
            ),
        ],
        className="dashboard",
    )
