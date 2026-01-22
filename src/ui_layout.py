from __future__ import annotations

from dash import dcc, html


def sidebar() -> html.Div:
    return html.Div(
        [
            html.Div(id="logo-slot", className="logo-slot"),
            html.Div("Resumo do PCP", className="nav-title"),
            html.Div(
                [
                    html.H4("Contexto", className="panel-title"),
                    html.P(
                        "Use os filtros para investigar marcas, coleções e status de produção.",
                        className="panel-text",
                    ),
                ],
                className="panel-card",
            ),
            html.Div(id="data-status", className="data-status"),
        ],
        className="side-panel",
    )


def top_bar() -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.H2("Centro de Controle PCP", className="app-title"),
                    html.Span("Visão executiva e operacional", className="app-subtitle"),
                ],
                className="title-group",
            ),
            html.Div(id="status-line", className="status-line"),
        ],
        className="top-bar",
    )


def top_filters() -> html.Div:
    return html.Div(
        [
            html.Div("Filtros rápidos", className="filters-title"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Marca"),
                            dcc.Dropdown(id="f_marca", multi=True, placeholder="Todas"),
                        ],
                        className="filter-item",
                    ),
                    html.Div(
                        [
                            html.Label("Coleção"),
                            dcc.Dropdown(id="f_colecao", multi=True, placeholder="Todas"),
                        ],
                        className="filter-item",
                    ),
                    html.Div(
                        [
                            html.Label("Processo"),
                            dcc.Dropdown(id="f_processo", multi=True, placeholder="Todos"),
                        ],
                        className="filter-item",
                    ),
                    html.Div(
                        [
                            html.Label("Status produção"),
                            dcc.Dropdown(id="f_status_prod", multi=True, placeholder="Todos"),
                        ],
                        className="filter-item",
                    ),
                    html.Div(
                        [
                            html.Label("Status vencimento"),
                            dcc.Dropdown(id="f_status_venc", multi=True, placeholder="Todos"),
                        ],
                        className="filter-item",
                    ),
                ],
                className="filters-grid",
            ),
        ],
        className="filters-panel",
    )


def page_container() -> html.Div:
    return html.Div(id="page", className="page-container")
