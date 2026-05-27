#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(urca)
  library(vars)
  library(ggplot2)
})

root <- normalizePath(getwd(), mustWork = TRUE)
dataset_path <- file.path(root, "data", "processed", "eu_de", "final_quarterly_model_dataset.csv")
stress_dir <- file.path(root, "results", "stress_testing")
beta_dir <- file.path(stress_dir, "beta_stability")
dir.create(stress_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(beta_dir, recursive = TRUE, showWarnings = FALSE)

fmt <- function(x, digits = 3) {
  ifelse(is.na(x), "NA", formatC(x, digits = digits, format = "f"))
}

collapse_vars <- function(vars) paste(vars, collapse = ", ")

data <- read.csv(dataset_path, stringsAsFactors = FALSE)
data$date <- as.Date(data$date)
data$baseline_sample <- as.logical(data$baseline_sample)
data$robustness_sample <- as.logical(data$robustness_sample)

systems <- list(
  system_a_ecb_inside_beta = c(
    "ln_ecb_assets_ea_stock",
    "ln_hh_loans_ea_stock",
    "ln_nfc_loans_ea_stock",
    "ln_house_price_de_real",
    "ln_compensation_ea20_real"
  ),
  system_b_ecb_forcing_beta_block = c(
    "ln_hh_loans_ea_stock",
    "ln_nfc_loans_ea_stock",
    "ln_house_price_de_real",
    "ln_compensation_ea20_real"
  ),
  system_c_dax_excluded = c(
    "ln_ecb_assets_ea_stock",
    "ln_hh_loans_ea_stock",
    "ln_nfc_loans_ea_stock",
    "ln_house_price_de_real",
    "ln_compensation_ea20_real"
  ),
  system_d_ecb_excluded = c(
    "ln_hh_loans_ea_stock",
    "ln_nfc_loans_ea_stock",
    "ln_house_price_de_real",
    "ln_compensation_ea20_real"
  ),
  expanded_with_dax = c(
    "ln_ecb_assets_ea_stock",
    "ln_hh_loans_ea_stock",
    "ln_nfc_loans_ea_stock",
    "ln_house_price_de_real",
    "ln_compensation_ea20_real",
    "ln_dax_real_de"
  )
)

rank_blocks <- list(
  block_1_credit_housing_income = c(
    "ln_hh_loans_ea_stock",
    "ln_nfc_loans_ea_stock",
    "ln_house_price_de_real",
    "ln_compensation_ea20_real"
  ),
  block_2_plus_ecb_assets = c(
    "ln_ecb_assets_ea_stock",
    "ln_hh_loans_ea_stock",
    "ln_nfc_loans_ea_stock",
    "ln_house_price_de_real",
    "ln_compensation_ea20_real"
  ),
  block_3_plus_dax = c(
    "ln_ecb_assets_ea_stock",
    "ln_hh_loans_ea_stock",
    "ln_nfc_loans_ea_stock",
    "ln_house_price_de_real",
    "ln_compensation_ea20_real",
    "ln_dax_real_de"
  ),
  block_4_household_credit_only = c(
    "ln_ecb_assets_ea_stock",
    "ln_hh_loans_ea_stock",
    "ln_house_price_de_real",
    "ln_compensation_ea20_real"
  ),
  block_5_nfc_credit_only = c(
    "ln_ecb_assets_ea_stock",
    "ln_nfc_loans_ea_stock",
    "ln_house_price_de_real",
    "ln_compensation_ea20_real"
  ),
  block_6_real_variables_only = c(
    "ln_house_price_de_real",
    "ln_compensation_ea20_real",
    "ln_dax_real_de"
  )
)

level_map <- c(
  ln_ecb_assets_ea_stock = "ecb_assets_ea_stock",
  ln_hh_loans_ea_stock = "hh_loans_ea_stock",
  ln_nfc_loans_ea_stock = "nfc_loans_ea_stock",
  ln_house_price_de_real = "house_price_de_real",
  ln_compensation_ea20_real = "compensation_ea20_real",
  ln_dax_real_de = "dax_real_de",
  wx_shadow_rate = "wx_shadow_rate",
  dfr_eop = "dfr_eop"
)

sample_data <- function(sample_name, vars) {
  flag <- if (sample_name == "baseline") "baseline_sample" else "robustness_sample"
  out <- data[data[[flag]], c("date", "quarter", vars), drop = FALSE]
  out <- out[complete.cases(out[, vars, drop = FALSE]), , drop = FALSE]
  rownames(out) <- out$quarter
  out
}

numeric_matrix <- function(sample_name, vars) {
  out <- sample_data(sample_name, vars)
  as.data.frame(out[, vars, drop = FALSE])
}

safe_ca <- function(x, type = "trace", ecdet = "const", K = 2) {
  tryCatch(
    ca.jo(x, type = type, ecdet = ecdet, K = K, spec = "transitory"),
    error = function(e) e
  )
}

selected_rank <- function(jo, alpha_col = "5pct") {
  if (inherits(jo, "error")) return(NA_integer_)
  p <- length(jo@teststat)
  stats <- as.numeric(jo@teststat)
  cvals <- as.numeric(jo@cval[, alpha_col])
  for (r in 0:(p - 1)) {
    idx <- p - r
    if (stats[idx] <= cvals[idx]) return(as.integer(r))
  }
  as.integer(p)
}

lag_selection <- function(x) {
  out <- tryCatch(VARselect(x, lag.max = 4, type = "const")$selection, error = function(e) NULL)
  if (is.null(out)) {
    return(c(aic = NA_integer_, hq = NA_integer_, sc = NA_integer_, fpe = NA_integer_))
  }
  c(
    aic = as.integer(out[["AIC(n)"]]),
    hq = as.integer(out[["HQ(n)"]]),
    sc = as.integer(out[["SC(n)"]]),
    fpe = as.integer(out[["FPE(n)"]])
  )
}

rank_grid <- function(system_name, vars, sample_name, det_values = c("none", "const", "trend"), k_values = 2:4) {
  x <- numeric_matrix(sample_name, vars)
  lag_sel <- lag_selection(x)
  rows <- list()
  row_id <- 1
  for (ecdet in det_values) {
    for (K in k_values) {
      trace <- safe_ca(x, type = "trace", ecdet = ecdet, K = K)
      eigen <- safe_ca(x, type = "eigen", ecdet = ecdet, K = K)
      trace_rank <- selected_rank(trace)
      maxeig_rank <- selected_rank(eigen)
      error <- ""
      eigenvalues <- NA_character_
      trace_r0_stat <- NA_real_
      trace_r0_cv5 <- NA_real_
      maxeig_r0_stat <- NA_real_
      maxeig_r0_cv5 <- NA_real_
      if (inherits(trace, "error")) {
        error <- trace$message
      } else {
        p <- length(vars)
        eigenvalues <- paste(fmt(trace@lambda[seq_len(p)], 4), collapse = "; ")
        trace_r0_stat <- trace@teststat[p]
        trace_r0_cv5 <- trace@cval[p, "5pct"]
      }
      if (inherits(eigen, "error")) {
        error <- paste(error, eigen$message)
      } else {
        p <- length(vars)
        maxeig_r0_stat <- eigen@teststat[p]
        maxeig_r0_cv5 <- eigen@cval[p, "5pct"]
      }
      comment <- if (is.na(trace_rank) || is.na(maxeig_rank)) {
        "estimation failed"
      } else if (trace_rank == maxeig_rank) {
        "trace and max-eigen agree"
      } else {
        "trace/max-eigen disagreement"
      }
      if (!is.na(trace_rank) && trace_rank >= length(vars)) comment <- paste(comment, "full-rank warning", sep = "; ")
      if (!is.na(trace_rank) && trace_rank == 0) comment <- paste(comment, "zero-rank warning", sep = "; ")
      rows[[row_id]] <- data.frame(
        sample = sample_name,
        system = system_name,
        variables = collapse_vars(vars),
        n_variables = length(vars),
        nobs = nrow(x),
        sample_start = as.character(sample_data(sample_name, vars)$date[1]),
        sample_end = as.character(tail(sample_data(sample_name, vars)$date, 1)),
        deterministic = ecdet,
        var_lag_K = K,
        k_ar_diff = K - 1,
        selected_aic_levels_lag = lag_sel[["aic"]],
        selected_hq_levels_lag = lag_sel[["hq"]],
        selected_sc_levels_lag = lag_sel[["sc"]],
        selected_fpe_levels_lag = lag_sel[["fpe"]],
        trace_rank_5pct = trace_rank,
        maxeig_rank_5pct = maxeig_rank,
        trace_r0_stat = trace_r0_stat,
        trace_r0_cv5 = trace_r0_cv5,
        maxeig_r0_stat = maxeig_r0_stat,
        maxeig_r0_cv5 = maxeig_r0_cv5,
        eigenvalues = eigenvalues,
        stability_comment = comment,
        error = trimws(error),
        stringsAsFactors = FALSE
      )
      row_id <- row_id + 1
    }
  }
  do.call(rbind, rows)
}

extract_beta <- function(system_name, vars, sample_name, ecdet = "const", K = 2, r = NULL) {
  x <- numeric_matrix(sample_name, vars)
  jo <- safe_ca(x, type = "trace", ecdet = ecdet, K = K)
  if (inherits(jo, "error")) return(data.frame())
  rank <- if (is.null(r)) selected_rank(jo) else r
  rank <- max(1, min(rank, length(vars) - 1))
  beta <- jo@V[seq_along(vars), 1, drop = TRUE]
  if (!is.na(beta[1]) && abs(beta[1]) > 1e-10) beta <- beta / beta[1]
  data.frame(
    system = system_name,
    sample = sample_name,
    rank_used = rank,
    normalized_on = vars[1],
    variable = vars,
    beta_first_vector = as.numeric(beta),
    stringsAsFactors = FALSE
  )
}

weak_exog_test <- function(system_name, vars, candidate, sample_name, ecdet = "const", K = 2) {
  x <- numeric_matrix(sample_name, vars)
  jo <- safe_ca(x, type = "trace", ecdet = ecdet, K = K)
  if (inherits(jo, "error")) {
    return(data.frame(
      system = system_name, sample = sample_name, candidate = candidate,
      nobs = nrow(x), rank_selected_trace = NA_integer_, rank_tested = NA_integer_,
      lr_stat = NA_real_, df = NA_integer_, p_value = NA_real_,
      decision_5pct = "not estimable", interpretation = jo$message,
      stringsAsFactors = FALSE
    ))
  }
  p <- length(vars)
  selected <- selected_rank(jo)
  rank_tested <- max(1, min(selected, p - 1))
  idx <- match(candidate, vars)
  A <- diag(p)[, -idx, drop = FALSE]
  test <- tryCatch(alrtest(jo, A = A, r = rank_tested), error = function(e) e)
  if (inherits(test, "error")) {
    return(data.frame(
      system = system_name, sample = sample_name, candidate = candidate,
      nobs = nrow(x), rank_selected_trace = selected, rank_tested = rank_tested,
      lr_stat = NA_real_, df = rank_tested, p_value = NA_real_,
      decision_5pct = "not estimable", interpretation = test$message,
      stringsAsFactors = FALSE
    ))
  }
  lr <- as.numeric(test@teststat[1])
  pval <- as.numeric(test@pval[1])
  decision <- if (pval < 0.05) "reject alpha_i = 0" else "fail to reject alpha_i = 0"
  interpretation <- if (pval < 0.05) {
    "not weakly exogenous at 5%; variable adjusts to the long-run relation"
  } else {
    "compatible with weak exogeneity at 5%; candidate can be treated as policy-side/forcing for beta purposes"
  }
  data.frame(
    system = system_name,
    sample = sample_name,
    candidate = candidate,
    nobs = nrow(x),
    deterministic = ecdet,
    var_lag_K = K,
    k_ar_diff = K - 1,
    rank_selected_trace = selected,
    rank_tested = rank_tested,
    lr_stat = lr,
    df = rank_tested,
    p_value = pval,
    decision_5pct = decision,
    interpretation = interpretation,
    stringsAsFactors = FALSE
  )
}

rank_comparisons <- do.call(rbind, list(
  rank_grid("System A: ECB assets inside beta", systems$system_a_ecb_inside_beta, "baseline"),
  rank_grid("System A: ECB assets inside beta", systems$system_a_ecb_inside_beta, "robustness"),
  rank_grid("System B: ECB assets outside beta block", systems$system_b_ecb_forcing_beta_block, "baseline"),
  rank_grid("System B: ECB assets outside beta block", systems$system_b_ecb_forcing_beta_block, "robustness"),
  rank_grid("System C: DAX excluded", systems$system_c_dax_excluded, "baseline"),
  rank_grid("System C: DAX excluded", systems$system_c_dax_excluded, "robustness"),
  rank_grid("System D: ECB assets excluded", systems$system_d_ecb_excluded, "baseline"),
  rank_grid("System D: ECB assets excluded", systems$system_d_ecb_excluded, "robustness"),
  rank_grid("Expanded: ECB assets plus DAX", systems$expanded_with_dax, "baseline"),
  rank_grid("Expanded: ECB assets plus DAX", systems$expanded_with_dax, "robustness")
))
write.csv(rank_comparisons, file.path(stress_dir, "weak_exogeneity_rank_sensitivity.csv"), row.names = FALSE)

weak_tests <- do.call(rbind, list(
  weak_exog_test("System A: ECB assets inside beta", systems$system_a_ecb_inside_beta, "ln_ecb_assets_ea_stock", "baseline"),
  weak_exog_test("System A: ECB assets inside beta", systems$system_a_ecb_inside_beta, "ln_ecb_assets_ea_stock", "robustness"),
  weak_exog_test("Policy extension: Wu-Xia in beta candidate", c(systems$system_a_ecb_inside_beta, "wx_shadow_rate"), "wx_shadow_rate", "baseline"),
  weak_exog_test("Policy extension: DFR in beta candidate", c(systems$system_a_ecb_inside_beta, "dfr_eop"), "dfr_eop", "robustness"),
  weak_exog_test("Expanded: DAX in beta candidate", systems$expanded_with_dax, "ln_dax_real_de", "baseline"),
  weak_exog_test("Expanded: DAX in beta candidate", systems$expanded_with_dax, "ln_dax_real_de", "robustness")
))
write.csv(weak_tests, file.path(stress_dir, "weak_exogeneity_alpha_tests.csv"), row.names = FALSE)

beta_vectors <- do.call(rbind, list(
  extract_beta("System A: ECB assets inside beta", systems$system_a_ecb_inside_beta, "baseline"),
  extract_beta("System A: ECB assets inside beta", systems$system_a_ecb_inside_beta, "robustness"),
  extract_beta("System B/D: ECB assets excluded beta block", systems$system_b_ecb_forcing_beta_block, "baseline"),
  extract_beta("System B/D: ECB assets excluded beta block", systems$system_b_ecb_forcing_beta_block, "robustness"),
  extract_beta("Expanded: ECB assets plus DAX", systems$expanded_with_dax, "baseline"),
  extract_beta("Expanded: ECB assets plus DAX", systems$expanded_with_dax, "robustness")
))
write.csv(beta_vectors, file.path(stress_dir, "weak_exogeneity_beta_vectors.csv"), row.names = FALSE)

markdown_table <- function(df, cols, digits = 3) {
  d <- df[, cols, drop = FALSE]
  for (nm in names(d)) {
    if (is.numeric(d[[nm]])) d[[nm]] <- fmt(d[[nm]], digits)
  }
  lines <- c(
    paste("|", paste(names(d), collapse = " | "), "|"),
    paste("|", paste(rep("---", length(d)), collapse = " | "), "|")
  )
  for (i in seq_len(nrow(d))) {
    lines <- c(lines, paste("|", paste(as.character(d[i, ]), collapse = " | "), "|"))
  }
  lines
}

default_rank_rows <- rank_comparisons[
  rank_comparisons$deterministic == "const" & rank_comparisons$var_lag_K == 2,
  c("sample", "system", "nobs", "trace_rank_5pct", "maxeig_rank_5pct", "trace_r0_stat", "trace_r0_cv5", "stability_comment")
]

weak_report <- c(
  "# Weak Exogeneity Report",
  "",
  "Scope: pre-identification stress testing only. These tests do not estimate the final SVECM.",
  "",
  "## Alpha Restriction Tests",
  "",
  "Null hypothesis: `alpha_i = 0`. Rejection means the candidate adjusts to the long-run relation and is not weakly exogenous under the tested system/rank.",
  "",
  markdown_table(weak_tests, c("sample", "system", "candidate", "nobs", "rank_selected_trace", "rank_tested", "lr_stat", "df", "p_value", "decision_5pct")),
  "",
  "## System Rank Comparison",
  "",
  "Default comparison uses a restricted constant in the cointegrating relation (`ecdet = const`) and VAR lag `K = 2`.",
  "",
  markdown_table(default_rank_rows, names(default_rank_rows)),
  "",
  "## Beta Interpretation",
  "",
  "The first unrestricted Johansen beta vector is normalized on the first listed variable. Large opposite-signed coefficients are a warning sign in this trend-dominated system, not a final structural restriction.",
  "",
  markdown_table(beta_vectors[beta_vectors$sample == "baseline", c("system", "sample", "normalized_on", "variable", "beta_first_vector")], c("system", "sample", "normalized_on", "variable", "beta_first_vector")),
  "",
  "## Economic Interpretation",
  "",
  "- ECB assets should only remain inside beta if alpha and beta stability both support an endogenous liquidity equilibrium. A failure to reject `alpha_i = 0` for ECB assets supports treating liquidity as a forcing process; rejection supports endogenous adjustment but must be weighed against collinearity.",
  "- `wx_shadow_rate` and `dfr_eop` are policy-side stance variables. If their alpha restrictions fail to reject, they should stay outside beta and enter short-run or instrument-side identification.",
  "- DAX is structurally useful only if it contributes stable rank information without worsening near-singularity. Weak exogeneity alone is not sufficient because DAX is a high-volatility asset-price robustness variable.",
  "",
  "Supporting CSV outputs: `weak_exogeneity_alpha_tests.csv`, `weak_exogeneity_rank_sensitivity.csv`, and `weak_exogeneity_beta_vectors.csv`."
)
writeLines(weak_report, file.path(stress_dir, "weak_exogeneity_report.md"))

rolling_johansen <- function(system_name, vars, windows = c(40, 48, 56), sample_name = "robustness", ecdet = "const", K = 2) {
  sd <- sample_data(sample_name, vars)
  eig_rows <- list()
  beta_rows <- list()
  rank_rows <- list()
  eig_id <- beta_id <- rank_id <- 1
  for (window in windows) {
    if (nrow(sd) < window) next
    for (start in seq_len(nrow(sd) - window + 1)) {
      stop <- start + window - 1
      win <- sd[start:stop, , drop = FALSE]
      x <- as.data.frame(win[, vars, drop = FALSE])
      jo <- safe_ca(x, type = "trace", ecdet = ecdet, K = K)
      if (inherits(jo, "error")) next
      rank <- selected_rank(jo)
      p <- length(vars)
      for (j in seq_len(p)) {
        eig_rows[[eig_id]] <- data.frame(
          system = system_name,
          window = window,
          start_date = win$date[1],
          end_date = tail(win$date, 1),
          end_quarter = tail(win$quarter, 1),
          eigen_index = j,
          eigenvalue = as.numeric(jo@lambda[j]),
          stringsAsFactors = FALSE
        )
        eig_id <- eig_id + 1
      }
      beta <- as.numeric(jo@V[seq_len(p), 1])
      if (!is.na(beta[1]) && abs(beta[1]) > 1e-10) beta <- beta / beta[1]
      for (j in seq_len(p)) {
        beta_rows[[beta_id]] <- data.frame(
          system = system_name,
          window = window,
          start_date = win$date[1],
          end_date = tail(win$date, 1),
          end_quarter = tail(win$quarter, 1),
          normalized_on = vars[1],
          variable = vars[j],
          beta_first_vector = beta[j],
          stringsAsFactors = FALSE
        )
        beta_id <- beta_id + 1
      }
      rank_rows[[rank_id]] <- data.frame(
        system = system_name,
        window = window,
        start_date = win$date[1],
        end_date = tail(win$date, 1),
        end_quarter = tail(win$quarter, 1),
        rank_trace_5pct = rank,
        stringsAsFactors = FALSE
      )
      rank_id <- rank_id + 1
    }
  }
  list(
    eigen = if (length(eig_rows)) do.call(rbind, eig_rows) else data.frame(),
    beta = if (length(beta_rows)) do.call(rbind, beta_rows) else data.frame(),
    rank = if (length(rank_rows)) do.call(rbind, rank_rows) else data.frame()
  )
}

roll_core <- rolling_johansen("core_with_ecb_assets", systems$system_a_ecb_inside_beta)
roll_block <- rolling_johansen("credit_housing_income_no_ecb", systems$system_b_ecb_forcing_beta_block)
rolling_eigen <- rbind(roll_core$eigen, roll_block$eigen)
rolling_beta <- rbind(roll_core$beta, roll_block$beta)
rolling_rank <- rbind(roll_core$rank, roll_block$rank)

write.csv(rolling_eigen, file.path(beta_dir, "rolling_eigenvalues.csv"), row.names = FALSE)
write.csv(rolling_beta, file.path(beta_dir, "rolling_beta_vectors.csv"), row.names = FALSE)
write.csv(rolling_rank, file.path(beta_dir, "rolling_rank_selection.csv"), row.names = FALSE)

rank_freq <- as.data.frame(table(rolling_rank$system, rolling_rank$window, rolling_rank$rank_trace_5pct), stringsAsFactors = FALSE)
names(rank_freq) <- c("system", "window", "rank_trace_5pct", "count")
rank_freq$count <- as.integer(rank_freq$count)
rank_freq <- rank_freq[rank_freq$count > 0, ]
rank_freq$share <- ave(rank_freq$count, rank_freq$system, rank_freq$window, FUN = function(x) x / sum(x))
write.csv(rank_freq, file.path(beta_dir, "rank_frequency_tables.csv"), row.names = FALSE)

assign_regime <- function(d) {
  if (d <= as.Date("2014-12-31")) return("Pre-QE 2005-2014")
  if (d <= as.Date("2019-12-31")) return("QE era 2015-2019")
  if (d <= as.Date("2021-12-31")) return("COVID 2020-2021")
  "Tightening 2022-2025"
}
rolling_rank$regime <- vapply(rolling_rank$end_date, assign_regime, character(1))
regime_summary <- aggregate(
  rank_trace_5pct ~ system + window + regime,
  data = rolling_rank,
  FUN = function(x) paste0("median=", median(x), "; mode=", names(sort(table(x), decreasing = TRUE))[1], "; n=", length(x))
)
write.csv(regime_summary, file.path(beta_dir, "regime_rank_summary.csv"), row.names = FALSE)

plot_eigs <- rolling_eigen[rolling_eigen$eigen_index <= 3, ]
if (nrow(plot_eigs)) {
  p <- ggplot(plot_eigs, aes(x = end_date, y = eigenvalue, color = factor(eigen_index))) +
    geom_line(linewidth = 0.5) +
    facet_grid(system ~ window, scales = "free_x") +
    labs(x = NULL, y = "Johansen eigenvalue", color = "Eigenvalue", title = "Rolling Johansen Eigenvalue Evolution") +
    theme_minimal(base_size = 10)
  ggsave(file.path(beta_dir, "eigenvalue_evolution_plots.png"), p, width = 12, height = 7, dpi = 160)
}

plot_beta <- rolling_beta[rolling_beta$variable != rolling_beta$normalized_on, ]
if (nrow(plot_beta)) {
  p <- ggplot(plot_beta, aes(x = end_date, y = beta_first_vector, color = variable)) +
    geom_line(linewidth = 0.45) +
    facet_grid(system ~ window, scales = "free_y") +
    labs(x = NULL, y = "First beta vector coefficient", color = "Variable", title = "Rolling Beta Coefficient Drift") +
    theme_minimal(base_size = 10)
  ggsave(file.path(beta_dir, "beta_coefficient_drift_plots.png"), p, width = 12, height = 7, dpi = 160)
}

beta_stability_report <- c(
  "# Beta Stability Testing",
  "",
  "Rolling Johansen diagnostics were estimated over the robustness sample using 40-, 48-, and 56-quarter windows. The default specification uses `ecdet = const` and VAR lag `K = 2`.",
  "",
  "## Rank Frequencies",
  "",
  markdown_table(rank_freq, c("system", "window", "rank_trace_5pct", "count", "share")),
  "",
  "## Regime Summary",
  "",
  markdown_table(regime_summary, c("system", "window", "regime", "rank_trace_5pct")),
  "",
  "Generated plots: `eigenvalue_evolution_plots.png` and `beta_coefficient_drift_plots.png`."
)
writeLines(beta_stability_report, file.path(beta_dir, "beta_stability_report.md"))

condition_number <- function(x) {
  m <- as.matrix(na.omit(x))
  if (nrow(m) < 5 || ncol(m) < 2) return(NA_real_)
  s <- apply(m, 2, sd, na.rm = TRUE)
  m <- m[, s > 0, drop = FALSE]
  if (ncol(m) < 2) return(NA_real_)
  z <- scale(m)
  sv <- svd(z)$d
  if (min(sv) <= .Machine$double.eps) return(Inf)
  max(sv) / min(sv)
}

system_condition_rows <- list()
pca_rows <- list()
conclusion_rows <- list()
row_id <- pca_id <- conclusion_id <- 1
for (nm in names(rank_blocks)) {
  vars <- rank_blocks[[nm]]
  sd <- sample_data("robustness", vars)
  logs <- sd[, vars, drop = FALSE]
  level_vars <- unname(level_map[vars])
  levels <- sample_data("robustness", level_vars)[, level_vars, drop = FALSE]
  diffs <- as.data.frame(diff(as.matrix(logs)))
  names(diffs) <- vars
  jo <- safe_ca(as.data.frame(logs), type = "trace", ecdet = "const", K = 2)
  beta_cond <- NA_real_
  if (!inherits(jo, "error")) {
    r <- max(1, min(selected_rank(jo), length(vars) - 1))
    beta_mat <- as.data.frame(jo@V[seq_along(vars), seq_len(r), drop = FALSE])
    beta_cond <- if (ncol(beta_mat) == 1) 1 else condition_number(beta_mat)
  }
  conds <- data.frame(
    system = nm,
    level_condition_number = condition_number(levels),
    log_condition_number = condition_number(logs),
    differenced_log_condition_number = condition_number(diffs),
    cointegrating_space_condition_number = beta_cond,
    stringsAsFactors = FALSE
  )
  system_condition_rows[[row_id]] <- conds
  row_id <- row_id + 1

  z <- scale(as.matrix(na.omit(logs)))
  pc <- prcomp(z, center = FALSE, scale. = FALSE)
  shares <- pc$sdev^2 / sum(pc$sdev^2)
  for (j in seq_along(shares)) {
    pca_rows[[pca_id]] <- data.frame(
      system = nm,
      component = paste0("PC", j),
      variance_share = shares[j],
      cumulative_share = sum(shares[seq_len(j)]),
      stringsAsFactors = FALSE
    )
    pca_id <- pca_id + 1
  }
  corr <- cor(logs, use = "pairwise.complete.obs")
  max_corr <- max(abs(corr[upper.tri(corr)]), na.rm = TRUE)
  pc1 <- shares[1]
  worst_cond <- max(conds$level_condition_number, conds$log_condition_number, conds$differenced_log_condition_number, na.rm = TRUE)
  status <- if (is.infinite(worst_cond) || worst_cond > 1000 || max_corr > 0.98 || pc1 > 0.90) {
    "unusable"
  } else if (worst_cond > 100 || max_corr > 0.90 || pc1 > 0.75) {
    "borderline"
  } else {
    "acceptable"
  }
  conclusion_rows[[conclusion_id]] <- data.frame(
    system = nm,
    max_abs_level_log_correlation = max_corr,
    pc1_variance_share = pc1,
    worst_condition_number = worst_cond,
    conclusion = status,
    stringsAsFactors = FALSE
  )
  conclusion_id <- conclusion_id + 1
}
condition_table <- do.call(rbind, system_condition_rows)
pca_table <- do.call(rbind, pca_rows)
collinearity_conclusions <- do.call(rbind, conclusion_rows)
write.csv(condition_table, file.path(stress_dir, "collinearity_condition_numbers.csv"), row.names = FALSE)
write.csv(pca_table, file.path(stress_dir, "collinearity_pca_variance.csv"), row.names = FALSE)
write.csv(collinearity_conclusions, file.path(stress_dir, "collinearity_system_conclusions.csv"), row.names = FALSE)

rolling_corr_pair <- function(var_a, var_b, window = 40) {
  vars <- c(var_a, var_b)
  sd <- sample_data("robustness", vars)
  rows <- list()
  for (start in seq_len(nrow(sd) - window + 1)) {
    stop <- start + window - 1
    win <- sd[start:stop, , drop = FALSE]
    rows[[length(rows) + 1]] <- data.frame(
      pair = paste(var_a, var_b, sep = " vs "),
      window = window,
      start_date = win$date[1],
      end_date = tail(win$date, 1),
      end_quarter = tail(win$quarter, 1),
      correlation = cor(win[[var_a]], win[[var_b]], use = "complete.obs"),
      stringsAsFactors = FALSE
    )
  }
  do.call(rbind, rows)
}
rolling_corr <- do.call(rbind, list(
  rolling_corr_pair("ln_ecb_assets_ea_stock", "ln_hh_loans_ea_stock"),
  rolling_corr_pair("ln_ecb_assets_ea_stock", "ln_nfc_loans_ea_stock"),
  rolling_corr_pair("ln_hh_loans_ea_stock", "ln_house_price_de_real"),
  rolling_corr_pair("ln_nfc_loans_ea_stock", "ln_house_price_de_real"),
  rolling_corr_pair("ln_dax_real_de", "ln_house_price_de_real"),
  rolling_corr_pair("ln_dax_real_de", "ln_hh_loans_ea_stock")
))
rolling_corr_summary <- aggregate(correlation ~ pair, rolling_corr, function(x) {
  paste0("min=", fmt(min(x), 3), "; mean=", fmt(mean(x), 3), "; max=", fmt(max(x), 3))
})
write.csv(rolling_corr, file.path(stress_dir, "rolling_correlations.csv"), row.names = FALSE)
write.csv(rolling_corr_summary, file.path(stress_dir, "rolling_correlation_summary.csv"), row.names = FALSE)

if (nrow(rolling_corr)) {
  p <- ggplot(rolling_corr, aes(x = end_date, y = correlation, color = pair)) +
    geom_hline(yintercept = c(-0.9, 0.9), color = "grey55", linewidth = 0.3, linetype = "dashed") +
    geom_line(linewidth = 0.45) +
    labs(x = NULL, y = "40-quarter rolling correlation", color = "Pair", title = "Rolling Correlation Diagnostics") +
    theme_minimal(base_size = 10)
  ggsave(file.path(stress_dir, "rolling_correlation_diagnostics.png"), p, width = 11, height = 6, dpi = 160)
}

collinearity_report <- c(
  "# Collinearity Diagnostics",
  "",
  "The system is trend dominated, so diagnostics are evaluated on levels, logs, first-differenced logs, the estimated cointegrating space, rolling pairwise correlations, and principal components.",
  "",
  "## Condition Numbers",
  "",
  markdown_table(condition_table, names(condition_table)),
  "",
  "## Principal-Component Structure",
  "",
  markdown_table(pca_table[pca_table$component %in% c("PC1", "PC2", "PC3"), ], c("system", "component", "variance_share", "cumulative_share")),
  "",
  "## Rolling Correlation Summary",
  "",
  markdown_table(rolling_corr_summary, c("pair", "correlation")),
  "",
  "## System Conclusions",
  "",
  markdown_table(collinearity_conclusions, c("system", "max_abs_level_log_correlation", "pc1_variance_share", "worst_condition_number", "conclusion")),
  "",
  "Classification rule: `unusable` if standardized condition number exceeds 1000, maximum absolute log-level correlation exceeds 0.98, or PC1 exceeds 90 percent of variance; `borderline` if condition number exceeds 100, correlation exceeds 0.90, or PC1 exceeds 75 percent.",
  "",
  "Supporting files: `collinearity_condition_numbers.csv`, `collinearity_pca_variance.csv`, `rolling_correlations.csv`, and `rolling_correlation_diagnostics.png`."
)
writeLines(collinearity_report, file.path(stress_dir, "collinearity_diagnostics.md"))

rank_robustness <- list()
rr_id <- 1
for (sample_name in c("baseline", "robustness")) {
  for (nm in names(rank_blocks)) {
    rank_robustness[[rr_id]] <- rank_grid(nm, rank_blocks[[nm]], sample_name)
    rr_id <- rr_id + 1
  }
}
rank_robustness <- do.call(rbind, rank_robustness)
write.csv(rank_robustness, file.path(stress_dir, "rank_robustness_matrix.csv"), row.names = FALSE)

rank_summary <- aggregate(
  trace_rank_5pct ~ sample + system,
  data = rank_robustness,
  FUN = function(x) paste0("median=", median(x, na.rm = TRUE), "; unique=", paste(sort(unique(x)), collapse = "/"))
)
write.csv(rank_summary, file.path(stress_dir, "rank_robustness_summary.csv"), row.names = FALSE)

cat("Wrote pre-identification stress-test outputs to ", stress_dir, "\n", sep = "")
