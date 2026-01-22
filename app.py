\
from __future__ import annotations

import os
from pathlib import Path
import pandas as pd

from dash import Dash, html, dcc, Input, Output, State, no_update
import plotly.io as pio

from src.data_loader import read_any, read_upload, validate_columns, coerce_types
from src.transforms import add_derived, apply_brand_filter
from src.settings_store import get_all_settings, set_setting
from src.ui_layout import sidebar, top_filters, page_container

from src.pages import home, processos, produtos, atrasos, metas, configuracoes

APP_DIR = Path(__file__).parent.resolve()
DB_PATH = str(APP_DIR / "data" / "app.db")
UPLOAD_DIR = APP_DIR / "data" / "uploads"
ASSET_DATA_DIR = APP_DIR / "data" / "assets"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ASSET_DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DATA_PATH = os.environ.get("PCP_DATA_PATH", "")
LATEST_UPLOAD_POINTER = APP_DIR / "data" / "latest_upload.txt"

def _read_latest_path() -> str | None:
    if LATEST_UPLOAD_POINTER.exists():
        p = LATEST_UPLOAD_POINTER.read_text(encoding="utf-8").strip()
        return p or None
    return None

def _write_latest_path(p: str) -> None:
    LATEST_UPLOAD_POINTER.write_text(p, encoding="utf-8")

def load_data() -> tuple[pd.DataFrame, str]:
    # priority: latest uploaded path -> env var -> empty
    p = _read_latest_path() or (DEFAULT_DATA_PATH.strip() if DEFAULT_DATA_PATH else "")
    if p and Path(p).exists():
        df = read_any(p)
        ok, missing = validate_columns(df)
        if not ok:
            raise ValueError(f"Colunas faltando: {missing}")
        df = coerce_types(df)
        df = add_derived(df)
        return df, f"Arquivo: {p}"
    # empty scaffold
    return pd.DataFrame(), "Nenhum arquivo carregado ainda. Vá em Configurações e faça upload do Excel/CSV."

def compute_filter_options(df: pd.DataFrame):
    if df.empty:
        return {}, {}
    opts = {
        "marca": sorted(df["MARCA"].dropna().astype(str).unique().tolist()) if "MARCA" in df.columns else [],
        "colecao": sorted(df["NOME_COLECAO"].dropna().astype(str).unique().tolist()) if "NOME_COLECAO" in df.columns else [],
        "processo": sorted(df["NOME_PROCESSO"].dropna().astype(str).unique().tolist()) if "NOME_PROCESSO" in df.columns else [],
        "status_prod": sorted(df["STATUS_PRODUCAO"].dropna().astype(str).unique().tolist()) if "STATUS_PRODUCAO" in df.columns else [],
        "status_venc": sorted(df["STATUS_VENCIMENTO"].dropna().astype(str).unique().tolist()) if "STATUS_VENCIMENTO" in df.columns else [],
    }
    return opts

def apply_filters(df: pd.DataFrame, f):
    out = df
    if df.empty:
        return df
    if f.get("marca"):
        out = out[out["MARCA"].isin(f["marca"])]
    if f.get("colecao"):
        out = out[out["NOME_COLECAO"].isin(f["colecao"])]
    if f.get("processo"):
        out = out[out["NOME_PROCESSO"].isin(f["processo"])]
    if f.get("status_prod"):
        out = out[out["STATUS_PRODUCAO"].isin(f["status_prod"])]
    if f.get("status_venc"):
        out = out[out["STATUS_VENCIMENTO"].isin(f["status_venc"])]
    return out

# Dash setup
app = Dash(__name__, suppress_callback_exceptions=True, title="Dashboard PCP")
server = app.server

pio.templates.default = "plotly_dark"

app.layout = html.Div(
    [
        dcc.Store(id="store-data"),
        dcc.Store(id="store-meta"),
        dcc.Store(id="store-settings"),
        html.Div(
            [
                sidebar(),
                html.Div(
                    [
                        top_filters(),
                        page_container(),
                    ],
                    className="content",
                )
            ],
            className="app",
        )
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
def init_or_reload(n_clicks, contents, filename):
    settings = get_all_settings(DB_PATH)

    # Handle upload
    if contents and filename:
        try:
            df = read_upload(contents, filename)
            ok, missing = validate_columns(df)
            if not ok:
                return no_update, no_update, settings, f"Erro no arquivo: colunas faltando {missing}"
            df = coerce_types(df)
            df = add_derived(df)

            save_path = str((UPLOAD_DIR / filename).resolve())
            # overwrite
            if Path(save_path).exists():
                Path(save_path).unlink()
            # re-save (csv if csv)
            if filename.lower().endswith(".csv"):
                df.to_csv(save_path, index=False)
            else:
                df.to_excel(save_path, index=False)
            _write_latest_path(save_path)

            meta = {"source": f"Upload: {filename}", "path": save_path}
            return df.to_json(date_format="iso", orient="split"), meta, settings, f"Carregado: {filename}"
        except Exception as e:
            return no_update, no_update, settings, f"Erro ao carregar upload: {e}"

    # otherwise load existing
    try:
        df, status = load_data()
        meta = {"source": status}
        return df.to_json(date_format="iso", orient="split"), meta, settings, status
    except Exception as e:
        return pd.DataFrame().to_json(date_format="iso", orient="split"), {"source": "erro"}, settings, f"Erro: {e}"

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
        [{"label": x, "value": x} for x in opts.get("marca", [])],
        [{"label": x, "value": x} for x in opts.get("colecao", [])],
        [{"label": x, "value": x} for x in opts.get("processo", [])],
        [{"label": x, "value": x} for x in opts.get("status_prod", [])],
        [{"label": x, "value": x} for x in opts.get("status_venc", [])],
    )

@app.callback(
    Output("page", "children"),
    Output("logo-slot", "children"),
    Input("nav", "value"),
    Input("store-data", "data"),
    Input("store-settings", "data"),
    Input("f_marca", "value"),
    Input("f_colecao", "value"),
    Input("f_processo", "value"),
    Input("f_status_prod", "value"),
    Input("f_status_venc", "value"),
)
def render_page(nav, data_json, settings, f_marca, f_colecao, f_processo, f_status_prod, f_status_venc):
    settings = settings or {}
    df = pd.read_json(data_json, orient="split") if data_json else pd.DataFrame()

    # Apply brand selection from settings first
    selected_brands = settings.get("selected_brands")
    if selected_brands:
        df = apply_brand_filter(df, selected_brands)

    # Apply UI filters
    df = apply_filters(df, {
        "marca": f_marca,
        "colecao": f_colecao,
        "processo": f_processo,
        "status_prod": f_status_prod,
        "status_venc": f_status_venc,
    })

    # logo
    logo_path = settings.get("logo_path")
    logo = None
    if logo_path and Path(logo_path).exists():
        # Use /assets route by copying to app assets if needed
        # We'll render from a file served by Dash if it's placed in ./assets
        # During save we copy into ./assets/logo.png
        if Path(logo_path).name == "logo.png":
            logo = html.Img(src="/assets/logo.png", style={"maxWidth":"100%", "borderRadius":"14px", "marginTop":"6px"})
        else:
            logo = html.Div("Logo carregada", className="small")
    else:
        logo = html.Div("Envie uma logo em Configurações", className="small")

    available_brands = sorted(df["MARCA"].dropna().astype(str).unique().tolist()) if not df.empty and "MARCA" in df.columns else []
    if nav == "home":
        return home.layout(df, settings), logo
    if nav == "processos":
        return processos.layout(df, settings), logo
    if nav == "produtos":
        return produtos.layout(df, settings), logo
    if nav == "atrasos":
        return atrasos.layout(df, settings), logo
    if nav == "metas":
        return metas.layout(df, settings), logo
    if nav == "config":
        return configuracoes.layout(available_brands, settings), logo
    return home.layout(df, settings), logo

@app.callback(
    Output("cfg-msg", "children"),
    Output("store-settings", "data"),
    Input("btn-save", "n_clicks"),
    State("cfg-weekly", "value"),
    State("cfg-workdays", "value"),
    State("cfg-daily-override", "value"),
    State("cfg-brands", "value"),
    State("cfg-critical", "value"),
    State("store-settings", "data"),
    prevent_initial_call=True,
)
def save_settings(n, weekly, workdays, daily_override, brands, critical, settings):
    settings = settings or {}
    # Normalize
    weekly = 0 if weekly is None else float(weekly)
    workdays = 5 if workdays is None else int(workdays)
    daily_override = None if daily_override in ("", None) else float(daily_override)
    brands = None if not brands else list(brands)
    critical = 3 if critical is None else int(critical)

    set_setting(DB_PATH, "weekly_target", weekly)
    set_setting(DB_PATH, "workdays", workdays)
    set_setting(DB_PATH, "daily_target_override", daily_override)
    set_setting(DB_PATH, "selected_brands", brands)
    set_setting(DB_PATH, "critical_delay_days", critical)

    # refresh settings store
    new_settings = get_all_settings(DB_PATH)
    return "Configurações salvas ✅", new_settings

@app.callback(
    Output("logo-msg", "children"),
    Output("store-settings", "data"),
    Input("upload-logo", "contents"),
    State("upload-logo", "filename"),
    State("store-settings", "data"),
    prevent_initial_call=True,
)
def upload_logo(contents, filename, settings):
    if not contents or not filename:
        return no_update, no_update
    settings = settings or {}
    try:
        import base64
        content_type, content_string = contents.split(",")
        data = base64.b64decode(content_string)
        # save to app assets so dash serves it
        out_path = APP_DIR / "assets" / "logo.png"
        out_path.parent.mkdir(exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(data)
        # store pointer
        set_setting(DB_PATH, "logo_path", str(out_path.resolve()))
        new_settings = get_all_settings(DB_PATH)
        return "Logo atualizada ✅", new_settings
    except Exception as e:
        return f"Erro ao salvar logo: {e}", settings

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8000, debug=False)
