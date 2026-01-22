from __future__ import annotations

import pandas as pd


def _detect_brand(name: str) -> str:
    if "DAZUL" in name:
        return "DAZUL"
    if "SARON" in name:
        return "SARON"
    if "FILOBLU" in name:
        return "FILOBLU"
    return "OUTRAS"


def add_derived(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df["MARCA"] = df["NOME_COLECAO"].astype(str).str.upper().apply(_detect_brand)

    today = pd.Timestamp.today().normalize()
    df["EM_ABERTO"] = df["CONCLUSAO_PRODUCAO"].isna()
    df["VENCIDO"] = (df["VENCIMENTO_PRODUCAO"].dt.normalize() < today) & df["EM_ABERTO"]

    df["DIAS_EM_ABERTO"] = (today - df["EMISSAO_PRODUCAO"].dt.normalize()).dt.days
    df.loc[~df["EM_ABERTO"], "DIAS_EM_ABERTO"] = pd.NA

    df["ATRASO_DIAS"] = (today - df["VENCIMENTO_PRODUCAO"].dt.normalize()).dt.days
    df.loc[~df["VENCIDO"], "ATRASO_DIAS"] = 0

    df["CONCLUSAO_DIA"] = df["CONCLUSAO_PRODUCAO"].dt.date
    df["CONCLUSAO_SEMANA"] = df["CONCLUSAO_PRODUCAO"].dt.to_period("W").dt.start_time
    return df


def apply_brand_filter(df: pd.DataFrame, brands: list[str] | None) -> pd.DataFrame:
    if not brands:
        return df
    return df[df["MARCA"].isin(brands)]
