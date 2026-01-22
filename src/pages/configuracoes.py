from __future__ import annotations

from dash import dcc, html


def render_configuracoes(brands: list[str], settings: dict, admin_auth: bool) -> html.Div:
    selected = settings.get("selected_brands") or []
    weekly_target = settings.get("weekly_target") or 0
    workdays = settings.get("workdays") or 5
    daily_target_override = settings.get("daily_target_override")
    critical_delay_days = settings.get("critical_delay_days") or 1

    daily_auto = weekly_target / workdays if workdays else 0
    locked = not admin_auth

    return html.Div(
        [
            html.H3("Configurações"),
            html.Div(
                "Faça login no admin para liberar as configurações.",
                className="hint",
                hidden=not locked,
            ),
            html.Div(
                [
                    html.H4("Upload de dados"),
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div(["Arraste e solte ou ", html.A("Selecione um arquivo")]),
                        className="upload",
                        multiple=False,
                        disabled=locked,
                    ),
                    html.Button("Recarregar dados", id="btn-reload", className="primary-btn", disabled=locked),
                ],
                className="card",
            ),
            html.Div(
                [
                    html.H4("Marcas exibidas"),
                    dcc.Dropdown(
                        id="selected-brands",
                        options=[{"label": b, "value": b} for b in brands],
                        value=selected,
                        multi=True,
                        placeholder="Selecione as marcas",
                        disabled=locked,
                    ),
                ],
                className="card",
            ),
            html.Div(
                [
                    html.H4("Metas"),
                    html.Div(
                        [
                            html.Label("Meta semanal"),
                            dcc.Input(id="weekly-target", type="number", value=weekly_target, disabled=locked),
                        ]
                    ),
                    html.Div(
                        [
                            html.Label("Dias úteis"),
                            dcc.Input(id="workdays", type="number", value=workdays, disabled=locked),
                        ]
                    ),
                    html.Div(
                        [
                            html.Label("Meta diária (override opcional)"),
                            dcc.Input(
                                id="daily-target-override",
                                type="number",
                                value=daily_target_override,
                                disabled=locked,
                            ),
                        ]
                    ),
                    html.Div(f"Meta diária automática: {daily_auto:,.0f}", className="hint"),
                ],
                className="card",
            ),
            html.Div(
                [
                    html.H4("Logo"),
                    dcc.Upload(
                        id="upload-logo",
                        children=html.Div(["Enviar logo (PNG/JPG)"]),
                        className="upload",
                        multiple=False,
                        disabled=locked,
                    ),
                ],
                className="card",
            ),
            html.Div(
                [
                    html.H4("Regras"),
                    html.Label("Atraso crítico (dias)"),
                    dcc.Input(
                        id="critical-delay-days",
                        type="number",
                        value=critical_delay_days,
                        disabled=locked,
                    ),
                ],
                className="card",
            ),
            html.Button("Salvar configurações", id="btn-save-settings", className="primary-btn", disabled=locked),
            html.Div(id="settings-status", className="status-line"),
        ],
        className="page",
    )
