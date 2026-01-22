from __future__ import annotations

from dash import dcc, html


NAV_OPTIONS = [
    {"label": "Visão Geral", "value": "home"},
    {"label": "Processos", "value": "processos"},
    {"label": "Produtos", "value": "produtos"},
    {"label": "Atrasos", "value": "atrasos"},
    {"label": "Metas", "value": "metas"},
    {"label": "Configurações", "value": "configuracoes"},
]


def sidebar() -> html.Div:
    return html.Div(
        [
            html.Div(id="logo-slot", className="logo-slot"),
            dcc.RadioItems(
                id="nav",
                options=NAV_OPTIONS,
                value="home",
                className="nav",
            ),
            html.Div(id="data-status", className="data-status"),
        ],
        className="sidebar",
    )


def top_bar() -> html.Div:
    return html.Div(
        [
            html.H2("Dashboard PCP", className="app-title"),
            html.Div(id="status-line", className="status-line"),
        ],
        className="top-bar",
    )


def top_filters() -> html.Div:
    return html.Div(
        [
            dcc.Dropdown(id="f_marca", multi=True, placeholder="Marca"),
            dcc.Dropdown(id="f_colecao", multi=True, placeholder="Coleção"),
            dcc.Dropdown(id="f_processo", multi=True, placeholder="Processo"),
            dcc.Dropdown(id="f_status_prod", multi=True, placeholder="Status Produção"),
            dcc.Dropdown(id="f_status_venc", multi=True, placeholder="Status Vencimento"),
        ],
        className="top-filters",
    )


def page_container() -> html.Div:
    return html.Div(id="page", className="page-container")
