from __future__ import annotations

from dash import html, dcc

from . import configuracoes


def _login_panel():
    return html.Div(
        [
            html.Div("Área administrativa", className="panel-title"),
            html.Div("Use o login para acessar as configurações do sistema.", className="small"),
            html.Div("Usuário: admin • Senha: 123456", className="small", style={"marginTop": "4px"}),
            html.Div(
                [
                    dcc.Input(
                        id="admin-username",
                        type="text",
                        placeholder="Usuário",
                        className="input",
                    ),
                    dcc.Input(
                        id="admin-password",
                        type="password",
                        placeholder="Senha",
                        className="input",
                    ),
                    html.Button("Entrar", id="btn-admin-login", className="btn"),
                ],
                className="row",
                style={"marginTop": "10px"},
            ),
            html.Div(id="admin-login-msg", className="small", style={"marginTop": "10px"}),
        ],
        className="panel",
    )


def layout(available_brands, settings, is_authenticated: bool):
    content = [configuracoes.layout(available_brands, settings)]
    if not is_authenticated:
        content.insert(
            0,
            html.Div(
                [
                    html.Div("Configurações desbloqueadas", className="panel-title"),
                    html.Div(
                        "Para facilitar o uso inicial, as configurações estão abertas. "
                        "Se quiser proteger no futuro, reative o login.",
                        className="small",
                    ),
                ],
                className="panel",
            ),
        )
        content.append(_login_panel())

    return html.Div(
        [
            html.Div(
                [
                    html.Button("Voltar ao painel", id="btn-back-dashboard", className="btn"),
                    html.Div("Administração", className="panel-title"),
                ],
                className="row",
                style={"justifyContent": "space-between"},
            ),
            *content,
        ]
    )
