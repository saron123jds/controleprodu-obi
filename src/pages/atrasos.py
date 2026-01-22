\
from __future__ import annotations
from dash import html, dcc, dash_table
import pandas as pd

def layout(df: pd.DataFrame, meta: dict):
    crit = int(meta.get("critical_delay_days", 3) or 3)
    view = df.copy()
    if "ATRASO_DIAS" in view.columns:
        view = view[view["ATRASO_DIAS"].fillna(0).astype(float) >= crit]
        view = view.sort_values("ATRASO_DIAS", ascending=False)
    cols = ["MARCA","NOME_COLECAO","REFERENCIA_PRODUTO","NOME_PROCESSO","LOTE_PRODUCAO","QTDE_PRODUCAO","VENCIMENTO_PRODUCAO","ATRASO_DIAS","RESPONSAVEL"]
    cols = [c for c in cols if c in view.columns]
    table = dash_table.DataTable(
        columns=[{"name": c, "id": c} for c in cols],
        data=view[cols].head(300).to_dict("records"),
        page_size=15,
        style_table={"overflowX":"auto"},
        style_cell={"backgroundColor":"#0f172a","color":"#e7eefc","border":"1px solid rgba(255,255,255,.06)","fontFamily":"inherit","fontSize":"12px","padding":"8px"},
        style_header={"fontWeight":"700"},
        sort_action="native",
        filter_action="native",
    )
    return html.Div(
        [
            html.Div(
                [
                    html.Div(f"Atrasos críticos (>= {crit} dias)", className="panel-title"),
                    html.Div("Dica: use o filtro da tabela para achar por referência, lote, responsável…", className="small"),
                    html.Div(table, style={"marginTop":"10px"}),
                ],
                className="panel",
            )
        ]
    )
