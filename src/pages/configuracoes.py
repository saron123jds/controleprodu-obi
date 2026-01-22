from __future__ import annotations
from dash import html, dcc

def layout(available_brands, settings):
    weekly_target = settings.get("weekly_target", 0) or 0
    workdays = settings.get("workdays", 5) or 5
    daily_override = settings.get("daily_target_override", None)
    selected_brands = settings.get("selected_brands", None)
    crit = settings.get("critical_delay_days", 3) or 3

    daily_auto = (float(weekly_target) / int(workdays)) if int(workdays) else 0

    return html.Div(
        [
            html.Div(
                [
                    html.Div("Configurações", className="panel-title"),
                    html.Div("Aqui você define metas, escolhe marcas exibidas e envia a logo do dashboard.", className="small"),
                    html.Div("O upload do arquivo fica disponível na barra lateral esquerda.", className="small"),
                ],
                className="panel",
            ),

            html.Div(
                [
                    html.Div("1) Marcas exibidas no painel", className="panel-title"),
                    dcc.Dropdown(
                        id="cfg-brands",
                        options=[{"label": b, "value": b} for b in sorted(available_brands)],
                        value=selected_brands if selected_brands else sorted(available_brands),
                        multi=True,
                        placeholder="Selecione as marcas",
                    ),
                    html.Div("Se quiser ver todas, selecione todas.", className="small", style={"marginTop":"8px"}),
                ],
                className="panel",
            ),

            html.Div(
                [
                    html.Div("2) Metas", className="panel-title"),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div("Meta semanal (peças)", className="small"),
                                    dcc.Input(id="cfg-weekly", type="number", value=weekly_target, className="input"),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Div("Dias úteis na semana", className="small"),
                                    dcc.Input(id="cfg-workdays", type="number", value=workdays, className="input"),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Div("Meta diária (manual) — deixe vazio para automática", className="small"),
                                    dcc.Input(id="cfg-daily-override", type="number", value=daily_override, className="input"),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Div("Meta diária automática calculada", className="small"),
                                    html.Div(f"{daily_auto:.1f} peças/dia", style={"fontWeight":"800", "marginTop":"6px"}),
                                ]
                            ),
                        ],
                        className="row",
                    ),
                ],
                className="panel",
            ),

            html.Div(
                [
                    html.Div("3) Logo do dashboard", className="panel-title"),
                    dcc.Upload(
                        id="upload-logo",
                        children=html.Div(["Envie um PNG/JPG da sua logo"]),
                        style={
                            "width": "100%", "height": "70px", "lineHeight": "70px",
                            "borderWidth": "1px", "borderStyle": "dashed",
                            "borderRadius": "18px", "textAlign": "center",
                            "borderColor": "rgba(255,255,255,.18)",
                            "background": "rgba(255,255,255,.03)"
                        },
                        multiple=False,
                    ),
                    html.Div(id="logo-msg", className="small", style={"marginTop":"8px"}),
                ],
                className="panel",
            ),

            html.Div(
                [
                    html.Div("4) Regras", className="panel-title"),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div("Atraso crítico (dias)", className="small"),
                                    dcc.Input(id="cfg-critical", type="number", value=crit, className="input"),
                                ]
                            ),
                        ],
                        className="row",
                    ),
                ],
                className="panel",
            ),

            html.Div(
                [
                    html.Button("Salvar configurações", id="btn-save", className="btn"),
                    html.Div(id="cfg-msg", className="small", style={"marginTop":"10px"}),
                ],
                className="panel",
            ),
        ]
    )
