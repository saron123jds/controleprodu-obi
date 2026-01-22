from __future__ import annotations

import base64
import io
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "CODIGO_COLECAO",
    "NOME_COLECAO",
    "CODIGO_PRODUTO",
    "REFERENCIA_PRODUTO",
    "DESCRICAO_PRODUTO",
    "CODIGO_PROCESSO",
    "NOME_PROCESSO",
    "ORDEM_PROCESSO",
    "EMISSAO_PRODUCAO",
    "VENCIMENTO_PRODUCAO",
    "CONCLUSAO_PRODUCAO",
    "STATUS_PRODUCAO",
    "STATUS_VENCIMENTO",
    "DIAS_PREVISAO",
    "DIAS_CONCLUSAO",
    "LOTE_PRODUCAO",
    "QTDE_PRODUCAO",
    "RESPONSAVEL",
]

COLUMN_ALIASES = {
    "COD_COLECAO": "CODIGO_COLECAO",
    "COLECAO": "NOME_COLECAO",
    "COD_PRODUTO": "CODIGO_PRODUTO",
    "REF_PRODUTO": "REFERENCIA_PRODUTO",
    "DESCRICAO": "DESCRICAO_PRODUTO",
    "COD_PROCESSO": "CODIGO_PROCESSO",
    "PROCESSO": "NOME_PROCESSO",
    "ORDEM": "ORDEM_PROCESSO",
    "EMISSAO": "EMISSAO_PRODUCAO",
    "VENCIMENTO": "VENCIMENTO_PRODUCAO",
    "CONCLUSAO": "CONCLUSAO_PRODUCAO",
    "STATUS_PROD": "STATUS_PRODUCAO",
    "STATUS_VENC": "STATUS_VENCIMENTO",
    "DIAS_PREV": "DIAS_PREVISAO",
    "DIAS_CONC": "DIAS_CONCLUSAO",
    "LOTE": "LOTE_PRODUCAO",
    "QTDE": "QTDE_PRODUCAO",
    "RESP": "RESPONSAVEL",
    "RESPONSAVEL": "RESPONSAVEL",
}


def _drop_unnamed(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[:, ~df.columns.str.contains("^Unnamed", case=False, na=False)]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {}
    for col in df.columns:
        normalized = str(col).strip().upper().replace(" ", "_")
        normalized = COLUMN_ALIASES.get(normalized, normalized)
        renamed[col] = normalized
    return df.rename(columns=renamed)


def read_any(path: str) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    if file_path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(file_path)
    elif file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path, sep=None, engine="python")
    else:
        raise ValueError("Formato inválido. Use .xlsx, .xls ou .csv")
    df = _drop_unnamed(df)
    return normalize_columns(df)


def read_upload(contents: str, filename: str) -> pd.DataFrame:
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    if filename.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(decoded))
    elif filename.lower().endswith(".csv"):
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), sep=None, engine="python")
    else:
        raise ValueError("Formato inválido. Use .xlsx, .xls ou .csv")
    df = _drop_unnamed(df)
    return normalize_columns(df)


def validate_columns(df: pd.DataFrame) -> tuple[bool, list[str]]:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    return len(missing) == 0, missing


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    date_cols = ["EMISSAO_PRODUCAO", "VENCIMENTO_PRODUCAO", "CONCLUSAO_PRODUCAO"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

    if "QTDE_PRODUCAO" in df.columns:
        df["QTDE_PRODUCAO"] = pd.to_numeric(df["QTDE_PRODUCAO"], errors="coerce").fillna(0).astype(int)

    for col in ["DIAS_PREVISAO", "DIAS_CONCLUSAO", "ORDEM_PROCESSO"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df
