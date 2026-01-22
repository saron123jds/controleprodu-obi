from __future__ import annotations

import pandas as pd


def compute_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "pecas": 0,
            "concluidas": 0,
            "em_aberto": 0,
            "atrasados": 0,
            "percentual_no_prazo": 0,
            "lead_time_medio": 0,
        }

    total_pecas = df["QTDE_PRODUCAO"].sum()
    concluidas = df.loc[df["STATUS_PRODUCAO"].astype(str).str.upper() == "CONCLUIDO", "QTDE_PRODUCAO"].sum()
    em_aberto = df["EM_ABERTO"].sum()
    atrasados = df["VENCIDO"].sum()

    status_venc = df["STATUS_VENCIMENTO"].astype(str).str.upper()
    percentual_em_atraso = (status_venc == "EM ATRASO").mean() if len(df) else 0
    percentual_no_prazo = 1 - percentual_em_atraso

    lead_time_medio = df["DIAS_CONCLUSAO"].mean() if "DIAS_CONCLUSAO" in df.columns else 0

    return {
        "pecas": int(total_pecas),
        "concluidas": int(concluidas),
        "em_aberto": int(em_aberto),
        "atrasados": int(atrasados),
        "percentual_no_prazo": float(percentual_no_prazo),
        "lead_time_medio": float(lead_time_medio) if lead_time_medio == lead_time_medio else 0,
    }


def compute_kpis_by(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if df.empty or group_col not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df["CONCLUIDO_QTDE"] = df["QTDE_PRODUCAO"].where(
        df["STATUS_PRODUCAO"].astype(str).str.upper() == "CONCLUIDO",
        0,
    )

    grouped = df.groupby(group_col, as_index=False).agg(
        pecas=("QTDE_PRODUCAO", "sum"),
        concluidas=("CONCLUIDO_QTDE", "sum"),
        em_aberto=("EM_ABERTO", "sum"),
        atrasados=("VENCIDO", "sum"),
        lead_time_medio=("DIAS_CONCLUSAO", "mean"),
    )
    grouped["lead_time_medio"] = grouped["lead_time_medio"].fillna(0)
    return grouped


def compute_projection(
    weekly_target: float,
    concluded_week: float,
    workdays: int,
    today: pd.Timestamp,
) -> dict:
    elapsed_workdays = max(min(today.weekday() + 1, workdays), 1)
    pace_daily = concluded_week / elapsed_workdays if elapsed_workdays else 0
    projected_week = pace_daily * workdays
    gap = weekly_target - projected_week
    return {
        "pace_daily": pace_daily,
        "projected_week": projected_week,
        "gap": gap,
    }
