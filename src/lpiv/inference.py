from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist
from typing import Iterable

import numpy as np
import pandas as pd


CONFIDENCE_LEVELS = (0.68, 0.90, 0.95)


@dataclass
class RegressionResult:
    method: str
    coefficients: pd.Series
    covariance: pd.DataFrame
    std_errors: pd.Series
    t_statistics: pd.Series
    p_values: pd.Series
    residuals: pd.Series
    fitted_values: pd.Series
    nobs: int
    df_resid: int
    r_squared: float
    hac_bandwidth: int
    x: pd.DataFrame
    z: pd.DataFrame | None = None
    x_hat: pd.DataFrame | None = None

    def confidence_intervals(self, levels: Iterable[float] = CONFIDENCE_LEVELS) -> pd.DataFrame:
        rows: dict[str, pd.Series] = {}
        for level in levels:
            critical = normal_critical_value(level)
            rows[f"lower_{int(level * 100)}"] = self.coefficients - critical * self.std_errors
            rows[f"upper_{int(level * 100)}"] = self.coefficients + critical * self.std_errors
        return pd.DataFrame(rows)


def normal_critical_value(level: float) -> float:
    if not 0 < level < 1:
        raise ValueError("Confidence level must be between 0 and 1.")
    return float(NormalDist().inv_cdf((1.0 + level) / 2.0))


def normal_p_value(statistic: float) -> float:
    if pd.isna(statistic):
        return np.nan
    return float(math.erfc(abs(float(statistic)) / math.sqrt(2.0)))


def hac_bandwidth_for_horizon(horizon: int, minimum: int = 1) -> int:
    if horizon < 0:
        raise ValueError("Horizon must be non-negative.")
    return max(minimum, int(horizon) + 1)


def add_constant(frame: pd.DataFrame, name: str = "const") -> pd.DataFrame:
    if name in frame.columns:
        return frame.copy()
    output = frame.copy()
    output.insert(0, name, 1.0)
    return output


def _as_float_frame(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.apply(pd.to_numeric, errors="coerce").astype(float)


def _safe_inverse(matrix: np.ndarray) -> np.ndarray:
    return np.linalg.pinv(matrix)


def newey_west_s_matrix(design: np.ndarray, residuals: np.ndarray, bandwidth: int) -> np.ndarray:
    nobs, nvars = design.shape
    xu = design * residuals.reshape(-1, 1)
    sandwich = xu.T @ xu
    for lag in range(1, min(bandwidth, nobs - 1) + 1):
        weight = 1.0 - lag / (bandwidth + 1.0)
        gamma = xu[lag:].T @ xu[:-lag]
        sandwich += weight * (gamma + gamma.T)
    if nobs > nvars:
        sandwich *= nobs / (nobs - nvars)
    return sandwich


def fit_ols(
    y: pd.Series,
    x: pd.DataFrame,
    hac_bandwidth: int,
    add_intercept: bool = True,
    method: str = "ols_hac",
) -> RegressionResult:
    y_clean = pd.to_numeric(y, errors="coerce").astype(float)
    x_clean = _as_float_frame(x)
    if add_intercept:
        x_clean = add_constant(x_clean)
    joined = pd.concat([y_clean.rename("_y"), x_clean], axis=1).dropna()
    if joined.empty:
        raise ValueError("No complete observations available for OLS estimation.")

    yv = joined["_y"].to_numpy(dtype=float)
    xv = joined.drop(columns=["_y"]).to_numpy(dtype=float)
    columns = joined.drop(columns=["_y"]).columns
    xtx_inv = _safe_inverse(xv.T @ xv)
    beta = xtx_inv @ xv.T @ yv
    fitted = xv @ beta
    residuals = yv - fitted
    s_matrix = newey_west_s_matrix(xv, residuals, hac_bandwidth)
    cov = xtx_inv @ s_matrix @ xtx_inv
    return _build_result(
        method=method,
        beta=beta,
        cov=cov,
        residuals=residuals,
        fitted=fitted,
        yv=yv,
        columns=columns,
        index=joined.index,
        hac_bandwidth=hac_bandwidth,
        x=joined.drop(columns=["_y"]),
    )


def fit_2sls(
    y: pd.Series,
    x: pd.DataFrame,
    z: pd.DataFrame,
    hac_bandwidth: int,
    add_intercept: bool = True,
) -> RegressionResult:
    y_clean = pd.to_numeric(y, errors="coerce").astype(float)
    x_clean = _as_float_frame(x)
    z_clean = _as_float_frame(z)
    if add_intercept:
        x_clean = add_constant(x_clean)
        z_clean = add_constant(z_clean)
    joined = pd.concat([y_clean.rename("_y"), x_clean.add_prefix("x__"), z_clean.add_prefix("z__")], axis=1).dropna()
    if joined.empty:
        raise ValueError("No complete observations available for 2SLS estimation.")

    x_columns = [column.replace("x__", "", 1) for column in joined.columns if column.startswith("x__")]
    z_columns = [column.replace("z__", "", 1) for column in joined.columns if column.startswith("z__")]
    yv = joined["_y"].to_numpy(dtype=float)
    xv = joined[[f"x__{column}" for column in x_columns]].to_numpy(dtype=float)
    zv = joined[[f"z__{column}" for column in z_columns]].to_numpy(dtype=float)

    ztz_inv = _safe_inverse(zv.T @ zv)
    x_hat = zv @ ztz_inv @ (zv.T @ xv)
    a_matrix = x_hat.T @ xv
    a_inv = _safe_inverse(a_matrix)
    beta = a_inv @ x_hat.T @ yv
    fitted = xv @ beta
    residuals = yv - fitted
    s_matrix = newey_west_s_matrix(x_hat, residuals, hac_bandwidth)
    cov = a_inv @ s_matrix @ a_inv.T

    index = joined.index
    x_frame = pd.DataFrame(xv, index=index, columns=x_columns)
    z_frame = pd.DataFrame(zv, index=index, columns=z_columns)
    x_hat_frame = pd.DataFrame(x_hat, index=index, columns=x_columns)
    return _build_result(
        method="2sls_hac",
        beta=beta,
        cov=cov,
        residuals=residuals,
        fitted=fitted,
        yv=yv,
        columns=pd.Index(x_columns),
        index=index,
        hac_bandwidth=hac_bandwidth,
        x=x_frame,
        z=z_frame,
        x_hat=x_hat_frame,
    )


def _build_result(
    method: str,
    beta: np.ndarray,
    cov: np.ndarray,
    residuals: np.ndarray,
    fitted: np.ndarray,
    yv: np.ndarray,
    columns: pd.Index,
    index: pd.Index,
    hac_bandwidth: int,
    x: pd.DataFrame,
    z: pd.DataFrame | None = None,
    x_hat: pd.DataFrame | None = None,
) -> RegressionResult:
    coefficients = pd.Series(beta, index=columns, name="coefficient")
    covariance = pd.DataFrame(cov, index=columns, columns=columns)
    std_errors = pd.Series(np.sqrt(np.maximum(np.diag(cov), 0.0)), index=columns, name="std_error")
    t_statistics = coefficients / std_errors.replace(0.0, np.nan)
    p_values = t_statistics.map(normal_p_value)
    residual_series = pd.Series(residuals, index=index, name="residual")
    fitted_series = pd.Series(fitted, index=index, name="fitted")
    rss = float(np.sum(residuals**2))
    tss = float(np.sum((yv - yv.mean()) ** 2))
    r_squared = np.nan if math.isclose(tss, 0.0) else 1.0 - rss / tss
    nobs = int(len(yv))
    df_resid = int(max(nobs - len(columns), 0))
    return RegressionResult(
        method=method,
        coefficients=coefficients,
        covariance=covariance,
        std_errors=std_errors,
        t_statistics=t_statistics,
        p_values=p_values,
        residuals=residual_series,
        fitted_values=fitted_series,
        nobs=nobs,
        df_resid=df_resid,
        r_squared=float(r_squared),
        hac_bandwidth=hac_bandwidth,
        x=x,
        z=z,
        x_hat=x_hat,
    )


def coefficient_summary_row(
    result: RegressionResult,
    coefficient: str,
    levels: Iterable[float] = CONFIDENCE_LEVELS,
) -> dict[str, float]:
    if coefficient not in result.coefficients.index:
        raise KeyError(f"Coefficient not found in result: {coefficient}")
    row: dict[str, float] = {
        "coefficient": float(result.coefficients[coefficient]),
        "std_error": float(result.std_errors[coefficient]),
        "t_stat": float(result.t_statistics[coefficient]),
        "p_value": float(result.p_values[coefficient]),
    }
    ci = result.confidence_intervals(levels=levels)
    for column in ci.columns:
        row[column] = float(ci.loc[coefficient, column])
    return row
