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
    df["ATRASO_FAIXA"] = pd.cut(
        df["ATRASO_DIAS"],
        bins=[-1, 0, 3, 7, 14, float("inf")],
        labels=["Em dia", "1-3 dias", "4-7 dias", "8-14 dias", "15+ dias"],
    )

    df["CONCLUSAO_DIA"] = df["CONCLUSAO_PRODUCAO"].dt.date
    df["CONCLUSAO_SEMANA"] = df["CONCLUSAO_PRODUCAO"].dt.to_period("W").dt.start_time
    return df


def apply_brand_filter(df: pd.DataFrame, brands: list[str] | None) -> pd.DataFrame:
    if not brands:
        return df
    return df[df["MARCA"].isin(brands)]


def compute_completion_trends(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    if df.empty:
        return {"weekly": pd.DataFrame(), "monthly": pd.DataFrame()}

    concluded = df[df["STATUS_PRODUCAO"].astype(str).str.upper() == "CONCLUIDO"]
    if concluded.empty:
        return {"weekly": pd.DataFrame(), "monthly": pd.DataFrame()}

    weekly = (
        concluded.groupby(concluded["CONCLUSAO_PRODUCAO"].dt.to_period("W").dt.start_time, as_index=False)[
            "QTDE_PRODUCAO"
        ]
        .sum()
        .rename(columns={"CONCLUSAO_PRODUCAO": "PERIODO"})
    )
    monthly = (
        concluded.groupby(concluded["CONCLUSAO_PRODUCAO"].dt.to_period("M").dt.start_time, as_index=False)[
            "QTDE_PRODUCAO"
        ]
        .sum()
        .rename(columns={"CONCLUSAO_PRODUCAO": "PERIODO"})
    )
    return {"weekly": weekly, "monthly": monthly}


def validate_data_quality(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return []

    alerts = []
    missing_emissao = df["EMISSAO_PRODUCAO"].isna().sum()
    if missing_emissao:
        alerts.append(f"{missing_emissao} registros sem data de emissão.")

    missing_venc = df["VENCIMENTO_PRODUCAO"].isna().sum()
    if missing_venc:
        alerts.append(f"{missing_venc} registros sem data de vencimento.")

    missing_conc = df["CONCLUSAO_PRODUCAO"].isna().sum()
    if missing_conc:
        alerts.append(f"{missing_conc} registros sem data de conclusão.")

    invalid_conc = df["CONCLUSAO_PRODUCAO"] < df["EMISSAO_PRODUCAO"]
    invalid_conc_count = invalid_conc.sum()
    if invalid_conc_count:
        alerts.append(f"{invalid_conc_count} registros com conclusão antes da emissão.")

    invalid_venc = df["VENCIMENTO_PRODUCAO"] < df["EMISSAO_PRODUCAO"]
    invalid_venc_count = invalid_venc.sum()
    if invalid_venc_count:
        alerts.append(f"{invalid_venc_count} registros com vencimento antes da emissão.")

    zero_qty = (df["QTDE_PRODUCAO"] <= 0).sum()
    if zero_qty:
        alerts.append(f"{zero_qty} registros com quantidade zerada.")

    return alerts
