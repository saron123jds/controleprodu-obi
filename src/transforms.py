\
from __future__ import annotations
import pandas as pd
import numpy as np

def detect_brand(nome_colecao: str) -> str:
    if not isinstance(nome_colecao, str):
        return "DESCONHECIDA"
    up = nome_colecao.upper()
    if "DAZUL" in up or "D'AZUL" in up or "D AZUL" in up:
        return "DAZUL"
    if "SARON" in up:
        return "SARON"
    if "FILOBLU" in up or "FILO" in up:
        return "FILOBLU"
    return "OUTRAS"

def add_derived(df: pd.DataFrame, today: pd.Timestamp | None = None) -> pd.DataFrame:
    out = df.copy()
    if today is None:
        today = pd.Timestamp.today().normalize()

    out["MARCA"] = out["NOME_COLECAO"].apply(detect_brand)

    # status helpers
    out["EM_ABERTO"] = out["CONCLUSAO_PRODUCAO"].isna()
    out["VENCIDO"] = out["VENCIMENTO_PRODUCAO"].notna() & (out["VENCIMENTO_PRODUCAO"] < today) & out["EM_ABERTO"]

    # days
    out["DIAS_EM_ABERTO"] = np.where(
        out["EMISSAO_PRODUCAO"].notna() & out["EM_ABERTO"],
        (today - out["EMISSAO_PRODUCAO"]).dt.days,
        np.nan,
    )
    out["ATRASO_DIAS"] = np.where(
        out["VENCIDO"],
        (today - out["VENCIMENTO_PRODUCAO"]).dt.days,
        0,
    )

    # week/day keys for grouping
    if "CONCLUSAO_PRODUCAO" in out.columns:
        out["CONCLUSAO_DIA"] = out["CONCLUSAO_PRODUCAO"].dt.date
        out["CONCLUSAO_SEMANA"] = out["CONCLUSAO_PRODUCAO"].dt.to_period("W").astype(str)
    if "EMISSAO_PRODUCAO" in out.columns:
        out["EMISSAO_DIA"] = out["EMISSAO_PRODUCAO"].dt.date
        out["EMISSAO_SEMANA"] = out["EMISSAO_PRODUCAO"].dt.to_period("W").astype(str)

    return out

def apply_brand_filter(df: pd.DataFrame, selected_brands):
    if not selected_brands:
        return df
    return df[df["MARCA"].isin(selected_brands)]
