from __future__ import annotations
import io
from dataclasses import dataclass
from typing import Optional, Tuple, List
import pandas as pd

REQUIRED_COLS = [
    "CODIGO_COLECAO","NOME_COLECAO","CODIGO_PRODUTO","REFERENCIA_PRODUTO","DESCRICAO_PRODUTO",
    "CODIGO_PROCESSO","NOME_PROCESSO","ORDEM_PROCESSO",
    "EMISSAO_PRODUCAO","VENCIMENTO_PRODUCAO","CONCLUSAO_PRODUCAO",
    "STATUS_PRODUCAO","STATUS_VENCIMENTO",
    "DIAS_PREVISAO","DIAS_CONCLUSAO",
    "LOTE_PRODUCAO","QTDE_PRODUCAO","RESPONSAVEL"
]

DATE_COLS = ["EMISSAO_PRODUCAO","VENCIMENTO_PRODUCAO","CONCLUSAO_PRODUCAO"]

def _to_datetime_series(s: pd.Series) -> pd.Series:
    # Try multiple formats; keep NaT where invalid
    return pd.to_datetime(s, errors="coerce", dayfirst=True)

def validate_columns(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    return (len(missing) == 0, missing)

def read_any(path: str) -> pd.DataFrame:
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path, dtype=str)
    elif path.lower().endswith(".xlsx") or path.lower().endswith(".xls"):
        df = pd.read_excel(path, dtype=str)
    else:
        raise ValueError("Formato não suportado. Envie Excel/CSV (.xlsx/.xls/.csv).")
    # drop unnamed empty columns
    df = df.loc[:, ~df.columns.str.match(r"^Unnamed")]
    return df

def read_upload(contents: str, filename: str) -> pd.DataFrame:
    content_type, content_string = contents.split(",")
    decoded = io.BytesIO(__import__("base64").b64decode(content_string))
    if filename.lower().endswith(".csv"):
        df = pd.read_csv(decoded, dtype=str)
    elif filename.lower().endswith(".xlsx") or filename.lower().endswith(".xls"):
        df = pd.read_excel(decoded, dtype=str)
    else:
        raise ValueError("Formato não suportado. Envie Excel/CSV (.xlsx/.xls/.csv).")
    df = df.loc[:, ~df.columns.str.match(r"^Unnamed")]
    return df

def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # numeric
    if "QTDE_PRODUCAO" in out.columns:
        out["QTDE_PRODUCAO"] = pd.to_numeric(out["QTDE_PRODUCAO"], errors="coerce").fillna(0).astype(int)
    for c in ["DIAS_PREVISAO","DIAS_CONCLUSAO","ORDEM_PROCESSO"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    for c in DATE_COLS:
        if c in out.columns:
            out[c] = _to_datetime_series(out[c])
    return out
