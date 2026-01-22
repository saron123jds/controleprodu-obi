\
from __future__ import annotations
from dash import html, dcc

def sidebar():
    return html.Div(
        [
            html.Div("Dashboard PCP", className="app-title"),
            html.Div(className="sidebar-sep"),
            dcc.RadioItems(
                id="nav",
                options=[
                    {"label":"Dashboard", "value":"dashboard"},
                    {"label":"Admin", "value":"admin"},
                ],
                value="dashboard",
                className="nav-hidden",
            ),
            html.Div(id="logo-slot"),
            html.Div(id="data-status", className="muted"),
        ],
        className="sidebar",
    )

def top_bar():
    return html.Div(
        [
            html.Div("Visão geral completa", className="top-title"),
            html.Button("⚙️", id="admin-gear", className="gear-btn", title="Admin"),
        ],
        className="top-bar",
    )

def top_filters():
    return html.Div(
        [
            html.Div(
                [
                    html.Div("Filtros", className="section-title"),
                    dcc.Dropdown(id="f_marca", multi=True, placeholder="Marca(s)"),
                    dcc.Dropdown(id="f_colecao", multi=True, placeholder="Coleção(ões)"),
                    dcc.Dropdown(id="f_processo", multi=True, placeholder="Processo(s)"),
                    dcc.Dropdown(id="f_status_prod", multi=True, placeholder="Status Produção"),
                    dcc.Dropdown(id="f_status_venc", multi=True, placeholder="Status Vencimento"),
                ],
                className="filters-card",
            )
        ],
        className="top-filters",
    )

def kpi_card(title: str, value: str, subtitle: str | None = None):
    return html.Div(
        [
            html.Div(title, className="kpi-title"),
            html.Div(value, className="kpi-value"),
            html.Div(subtitle or "", className="kpi-subtitle"),
        ],
        className="kpi-card",
    )

def page_container():
    return html.Div(id="page", className="page")
