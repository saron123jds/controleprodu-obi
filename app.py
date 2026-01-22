from __future__ import annotations

import base64
import datetime as dt
import os
from pathlib import Path
import pandas as pd

from dash import Dash, Input, Output, State, callback_context, dcc, html, no_update
import plotly.io as pio

from src.data_loader import read_any, read_upload, validate_columns, coerce_types
from src.transforms import add_derived, apply_brand_filter, validate_data_quality
from src.settings_store import add_upload_history, get_all_settings, get_upload_history, set_setting
from src.ui_layout import sidebar, top_bar, top_filters, page_container
from src.pages import render_painel

APP_DIR = Path(__file__).parent.resolve()
DB_PATH = str(APP_DIR / "data" / "app.db")
UPLOAD_DIR = APP_DIR / "data" / "uploads"
ASSET_DIR = APP_DIR / "assets"
LATEST_UPLOAD_POINTER = APP_DIR / "data" / "latest_upload.txt"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ASSET_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DATA_PATH = os.environ.get("PCP_DATA_PATH", "")
ADMIN_PASSWORD = "123456"


def _read_latest_path() -> str | None:
    if LATEST_UPLOAD_POINTER.exists():
        path = LATEST_UPLOAD_POINTER.read_text(encoding="utf-8").strip()
        return path or None
    return None


def _write_latest_path(path: str) -> None:
    LATEST_UPLOAD_POINTER.write_text(path, encoding="utf-8")


def load_data() -> tuple[pd.DataFrame, str]:
    path = _read_latest_path() or (DEFAULT_DATA_PATH.strip() if DEFAULT_DATA_PATH else "")
    if path and Path(path).exists():
        df = read_any(path)
        ok, missing = validate_columns(df)
        if not ok:
            missing_str = ", ".join(missing)
            raise ValueError(f"Colunas faltando: {missing_str}")
        df = coerce_types(df)
        df = add_derived(df)
        return df, f"Arquivo: {path}"
    return pd.DataFrame(), "Nenhum arquivo carregado. Vá em Configurações e faça upload."


def compute_filter_options(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "marca": [],
            "colecao": [],
            "processo": [],
            "status_prod": [],
            "status_venc": [],
        }
    return {
        "marca": sorted(df["MARCA"].dropna().astype(str).unique().tolist()),
        "colecao": sorted(df["NOME_COLECAO"].dropna().astype(str).unique().tolist()),
        "processo": sorted(df["NOME_PROCESSO"].dropna().astype(str).unique().tolist()),
        "status_prod": sorted(df["STATUS_PRODUCAO"].dropna().astype(str).unique().tolist()),
        "status_venc": sorted(df["STATUS_VENCIMENTO"].dropna().astype(str).unique().tolist()),
    }


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    out = df
    if filters.get("marca"):
        out = out[out["MARCA"].isin(filters["marca"])]
    if filters.get("colecao"):
        out = out[out["NOME_COLECAO"].isin(filters["colecao"])]
    if filters.get("processo"):
        out = out[out["NOME_PROCESSO"].isin(filters["processo"])]
    if filters.get("status_prod"):
        out = out[out["STATUS_PRODUCAO"].isin(filters["status_prod"])]
    if filters.get("status_venc"):
        out = out[out["STATUS_VENCIMENTO"].isin(filters["status_venc"])]
    return out


app = Dash(__name__, suppress_callback_exceptions=True, title="Dashboard PCP")
server = app.server
pio.templates.default = "plotly_dark"

app.layout = html.Div(
    [
        dcc.Store(id="store-data"),
        dcc.Store(id="store-meta"),
        dcc.Store(id="store-settings"),
        dcc.Store(id="store-admin-auth", data=False),
        html.Div(
            [
                top_bar(),
                html.Div(
                    [
                        sidebar(),
                        html.Div(
                            [
                                top_filters(),
                                page_container(),
                            ],
                            className="content-area",
                        ),
                    ],
                    className="workspace",
                ),
            ],
            className="app-shell",
        ),
    ]
)


@app.callback(
    Output("store-data", "data"),
    Output("store-meta", "data"),
    Output("store-settings", "data"),
    Output("data-status", "children"),
    Input("btn-reload", "n_clicks"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=False,
)
def init_or_reload(_, contents, filename):
    settings = get_all_settings(DB_PATH)

    if contents and filename:
        try:
            df = read_upload(contents, filename)
            ok, missing = validate_columns(df)
            if not ok:
                missing_str = ", ".join(missing)
                return no_update, no_update, settings, f"Erro: colunas faltando {missing_str}"
            df = coerce_types(df)
            df = add_derived(df)

            save_path = str((UPLOAD_DIR / filename).resolve())
            if filename.lower().endswith(".csv"):
                df.to_csv(save_path, index=False)
            else:
                df.to_excel(save_path, index=False)
            _write_latest_path(save_path)
            add_upload_history(DB_PATH, filename, save_path, dt.datetime.now().isoformat(timespec="seconds"))
            meta = {"source": f"Upload: {filename}", "path": save_path}
            return df.to_json(date_format="iso", orient="split"), meta, settings, f"Carregado: {filename}"
        except Exception as exc:
            return no_update, no_update, settings, f"Erro ao carregar: {exc}"

    try:
        df, status = load_data()
        meta = {"source": status}
        return df.to_json(date_format="iso", orient="split"), meta, settings, status
    except Exception as exc:
        return pd.DataFrame().to_json(date_format="iso", orient="split"), {"source": "erro"}, settings, f"Erro: {exc}"


@app.callback(
    Output("f_marca", "options"),
    Output("f_colecao", "options"),
    Output("f_processo", "options"),
    Output("f_status_prod", "options"),
    Output("f_status_venc", "options"),
    Input("store-data", "data"),
)
def update_filter_options(data_json):
    df = pd.read_json(data_json, orient="split") if data_json else pd.DataFrame()
    opts = compute_filter_options(df)
    return (
        [{"label": x, "value": x} for x in opts["marca"]],
        [{"label": x, "value": x} for x in opts["colecao"]],
        [{"label": x, "value": x} for x in opts["processo"]],
        [{"label": x, "value": x} for x in opts["status_prod"]],
        [{"label": x, "value": x} for x in opts["status_venc"]],
    )


@app.callback(
    Output("page", "children"),
    Output("logo-slot", "children"),
    Output("status-line", "children"),
    Input("store-data", "data"),
    Input("store-settings", "data"),
    Input("store-admin-auth", "data"),
    Input("f_marca", "value"),
    Input("f_colecao", "value"),
    Input("f_processo", "value"),
    Input("f_status_prod", "value"),
    Input("f_status_venc", "value"),
)
def render_page(data_json, settings, admin_auth, f_marca, f_colecao, f_processo, f_status_prod, f_status_venc):
    settings = settings or {}
    df = pd.read_json(data_json, orient="split") if data_json else pd.DataFrame()

    selected_brands = settings.get("selected_brands")
    if selected_brands:
        df = apply_brand_filter(df, selected_brands)

    df = apply_filters(
        df,
        {
            "marca": f_marca,
            "colecao": f_colecao,
            "processo": f_processo,
            "status_prod": f_status_prod,
            "status_venc": f_status_venc,
        },
    )

    critical_delay_days = int(settings.get("critical_delay_days") or 1)
    upload_history = get_upload_history(DB_PATH, limit=8)
    data_quality_alerts = validate_data_quality(df)

    brands = sorted(df["MARCA"].dropna().unique().tolist()) if not df.empty else []
    page = render_painel(
        df=df,
        settings=settings,
        brands=brands,
        admin_auth=bool(admin_auth),
        critical_delay_days=critical_delay_days,
        upload_history=upload_history,
        data_quality_alerts=data_quality_alerts,
    )

    logo_path = settings.get("logo_path", "assets/logo.png")
    logo_component = html.Img(src=f"/{logo_path}", className="logo") if Path(logo_path).exists() else html.Div("Logo")
    status = settings.get("status", "Pronto")
    if data_quality_alerts:
        status = f"{status} | Alertas de dados: {len(data_quality_alerts)}"
    return page, logo_component, status


@app.callback(
    Output("store-settings", "data", allow_duplicate=True),
    Output("settings-status", "children"),
    Input("btn-save-settings", "n_clicks"),
    Input("upload-logo", "contents"),
    State("upload-logo", "filename"),
    State("weekly-target", "value"),
    State("workdays", "value"),
    State("daily-target-override", "value"),
    State("selected-brands", "value"),
    State("critical-delay-days", "value"),
    prevent_initial_call=True,
)
def save_settings_or_logo(
    n_clicks,
    contents,
    filename,
    weekly_target,
    workdays,
    daily_target_override,
    selected_brands,
    critical_delay_days,
):
    triggered = (
        callback_context.triggered[0]["prop_id"].split(".")[0]
        if callback_context.triggered
        else None
    )
    if triggered == "upload-logo":
        if not contents or not filename:
            return no_update, no_update
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            return no_update, "Formato inválido. Use PNG ou JPG."

        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        logo_path = ASSET_DIR / "logo.png"
        logo_path.write_bytes(decoded)
        set_setting(DB_PATH, "logo_path", "assets/logo.png")
        settings = get_all_settings(DB_PATH)
        return settings, "Logo atualizado."

    if triggered == "btn-save-settings":
        set_setting(DB_PATH, "weekly_target", weekly_target)
        set_setting(DB_PATH, "workdays", workdays)
        set_setting(DB_PATH, "daily_target_override", daily_target_override)
        set_setting(DB_PATH, "selected_brands", selected_brands or [])
        set_setting(DB_PATH, "critical_delay_days", critical_delay_days)

        settings = get_all_settings(DB_PATH)
        return settings, "Configurações salvas."

    return no_update, no_update


@app.callback(
    Output("store-admin-auth", "data"),
    Output("admin-status", "children"),
    Input("btn-admin-login", "n_clicks"),
    State("admin-password", "value"),
    prevent_initial_call=True,
)
def authenticate_admin(_, password):
    if password == ADMIN_PASSWORD:
        return True, "Acesso liberado."
    return False, "Senha incorreta."


if __name__ == "__main__":
    app.run_server(debug=True, port=8000)
