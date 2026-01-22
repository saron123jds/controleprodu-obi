\
from __future__ import annotations
import pandas as pd

def kpi_totals(df: pd.DataFrame) -> dict:
    total = int(df["QTDE_PRODUCAO"].sum()) if "QTDE_PRODUCAO" in df.columns else 0
    concl = int(df.loc[df["STATUS_PRODUCAO"].astype(str).str.upper().eq("CONCLUIDO"), "QTDE_PRODUCAO"].sum()) if "STATUS_PRODUCAO" in df.columns else 0
    aberto = int(df.loc[~df["STATUS_PRODUCAO"].astype(str).str.upper().eq("CONCLUIDO"), "QTDE_PRODUCAO"].sum()) if "STATUS_PRODUCAO" in df.columns else 0

    atrasados_itens = int((df.get("VENCIDO", False) == True).sum()) if "VENCIDO" in df.columns else 0
    pct_prazo = None
    if "STATUS_VENCIMENTO" in df.columns:
        sv = df["STATUS_VENCIMENTO"].astype(str).str.upper()
        if len(sv) > 0:
            pct_prazo = float((~sv.eq("EM ATRASO")).mean()) * 100.0

    lead = None
    if "DIAS_CONCLUSAO" in df.columns:
        lead = float(pd.to_numeric(df["DIAS_CONCLUSAO"], errors="coerce").dropna().mean()) if df["DIAS_CONCLUSAO"].notna().any() else None

    return {
        "total": total,
        "concluidas": concl,
        "aberto": aberto,
        "atrasados_itens": atrasados_itens,
        "pct_prazo": pct_prazo,
        "lead_medio": lead,
    }
