#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
  library(tidyr)
  library(grid)
})

args <- commandArgs(trailingOnly = FALSE)
file_arg <- args[grepl("^--file=", args)]
if (length(file_arg) > 0) {
  script_dir <- dirname(normalizePath(sub("^--file=", "", file_arg[[1]])))
  repo_root <- normalizePath(file.path(script_dir, "..", ".."))
} else {
  repo_root <- normalizePath(getwd())
}

fig_dir <- file.path(repo_root, "results", "final", "figures", "enhancement")
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)

read_artifact <- function(...) {
  read.csv(file.path(repo_root, ...), stringsAsFactors = FALSE, check.names = FALSE)
}

write_plot <- function(plot, filename, width, height) {
  ggsave(
    filename = file.path(fig_dir, filename),
    plot = plot,
    width = width,
    height = height,
    dpi = 320,
    bg = "white"
  )
}

theme_thesis <- function(base_size = 11) {
  theme_minimal(base_size = base_size, base_family = "serif") +
    theme(
      plot.title = element_text(face = "bold", size = base_size + 2),
      plot.subtitle = element_text(color = "#4b5563", margin = margin(b = 8)),
      panel.grid.minor = element_blank(),
      panel.grid.major = element_line(color = "#e5e7eb", linewidth = 0.25),
      strip.text = element_text(face = "bold", size = base_size - 1),
      legend.position = "bottom",
      legend.title = element_blank(),
      axis.title = element_text(face = "bold"),
      plot.caption = element_text(size = base_size - 2, color = "#4b5563", hjust = 0)
    )
}

selected <- c(
  "ecb_house_purchase_growth_yoy",
  "ln_ecb_house_purchase_pure_new_loans",
  "ecb_mir_mortgage_lending_spread_dfr",
  "ecb_mir_nfc_lending_spread_dfr",
  "ln_dax_real_de",
  "ln_ecb_assets_ea_stock",
  "ecb_wage_tracker_ex_oneoffs_real_yoy",
  "eurostat_ecfin_eei_ea20",
  "eurostat_sts_industry_wage_bill_de_real_yoy"
)

response_order <- c(
  "house-purchase lending growth",
  "pure new house-purchase loans",
  "mortgage lending spread",
  "NFC lending spread",
  "real DAX",
  "ECB assets",
  "real wage tracker excl. one-offs",
  "employment expectations",
  "German industry real wage bill growth"
)

block_for <- function(response) {
  case_when(
    response %in% c("ecb_house_purchase_growth_yoy", "ln_ecb_house_purchase_pure_new_loans") ~ "Housing finance",
    response %in% c("ecb_mir_mortgage_lending_spread_dfr", "ecb_mir_nfc_lending_spread_dfr") ~ "Lending conditions",
    response %in% c("ln_dax_real_de", "ln_ecb_assets_ea_stock") ~ "Market and liquidity",
    TRUE ~ "Compensation and labor"
  )
}

block_palette <- c(
  "Housing finance" = "#0f766e",
  "Lending conditions" = "#1d4ed8",
  "Market and liquidity" = "#7c2d12",
  "Compensation and labor" = "#7e22ce"
)

irf <- read_artifact("results", "final", "tables", "normalized_irf_outputs.csv") %>%
  filter(shock == "target_factor_monthly_easing", response %in% selected) %>%
  mutate(
    block = block_for(response),
    response_label = factor(response_label, levels = response_order),
    horizon_months = as.numeric(horizon_months)
  )

comparative_irf <- ggplot(irf, aes(x = horizon_months, y = coefficient)) +
  geom_hline(yintercept = 0, color = "#111827", linewidth = 0.3) +
  geom_ribbon(aes(ymin = ci_90_low, ymax = ci_90_high, fill = block), alpha = 0.16, color = NA) +
  geom_line(aes(color = block), linewidth = 0.85) +
  geom_point(aes(color = block), size = 1.8) +
  facet_wrap(~response_label, scales = "free_y", ncol = 3) +
  scale_color_manual(values = block_palette) +
  scale_fill_manual(values = block_palette) +
  scale_x_continuous(breaks = c(0, 1, 3, 6, 12, 24)) +
  labs(
    title = "Comparative IRF Panels by Transmission Block",
    subtitle = "Monthly responses to a one-standard-deviation ECB target-factor easing surprise; shaded areas are 90 percent HAC intervals.",
    x = "Horizon in months",
    y = "Normalized response",
    caption = "Source: results/final/tables/normalized_irf_outputs.csv."
  ) +
  theme_thesis(11)
write_plot(comparative_irf, "comparative_irf_panel.png", 10.5, 7.5)

sign_score <- function(value) {
  case_when(
    value == "not_estimated" ~ "not estimated",
    grepl("^positive_p05", value) ~ "positive, p<0.05",
    grepl("^positive_p10", value) ~ "positive, p<0.10",
    grepl("^positive", value) ~ "positive, n.s.",
    grepl("^negative_p05", value) ~ "negative, p<0.05",
    grepl("^negative_p10", value) ~ "negative, p<0.10",
    grepl("^negative", value) ~ "negative, n.s.",
    TRUE ~ "not estimated"
  )
}

sign_label <- function(value) {
  case_when(
    value == "positive, p<0.05" ~ "++",
    value == "positive, p<0.10" ~ "+",
    value == "positive, n.s." ~ "+",
    value == "negative, p<0.05" ~ "--",
    value == "negative, p<0.10" ~ "-",
    value == "negative, n.s." ~ "-",
    TRUE ~ ""
  )
}

sign_heat <- read_artifact("results", "final", "uncertainty", "significance_heatmap.csv") %>%
  filter(response %in% selected) %>%
  pivot_longer(cols = starts_with("h"), names_to = "horizon", values_to = "classification") %>%
  mutate(
    response_label = factor(response_label, levels = rev(response_order)),
    horizon = factor(gsub("^h", "", horizon), levels = c("0", "1", "3", "6", "12", "24")),
    class = factor(
      sign_score(classification),
      levels = c(
        "negative, p<0.05", "negative, p<0.10", "negative, n.s.",
        "not estimated",
        "positive, n.s.", "positive, p<0.10", "positive, p<0.05"
      )
    ),
    label = sign_label(as.character(class))
  )

sign_persistence <- ggplot(sign_heat, aes(x = horizon, y = response_label, fill = class)) +
  geom_tile(color = "white", linewidth = 0.8) +
  geom_text(aes(label = label), size = 3.4, family = "serif", fontface = "bold") +
  scale_fill_manual(values = c(
    "negative, p<0.05" = "#991b1b",
    "negative, p<0.10" = "#ef4444",
    "negative, n.s." = "#fecaca",
    "not estimated" = "#e5e7eb",
    "positive, n.s." = "#bfdbfe",
    "positive, p<0.10" = "#60a5fa",
    "positive, p<0.05" = "#1d4ed8"
  )) +
  labs(
    title = "Sign Persistence Map",
    subtitle = "Direction and statistical strength across local-projection horizons.",
    x = "Horizon in months",
    y = NULL,
    caption = "Source: results/final/uncertainty/significance_heatmap.csv."
  ) +
  theme_thesis(11) +
  theme(panel.grid = element_blank())
write_plot(sign_persistence, "sign_persistence_map.png", 9.8, 5.8)

persistence <- read_artifact("results", "final", "uncertainty", "persistence_confidence_matrix.csv") %>%
  filter(response %in% selected) %>%
  pivot_longer(cols = starts_with("h"), names_to = "horizon", values_to = "cum90") %>%
  mutate(
    response_label = factor(response_label, levels = rev(response_order)),
    horizon = factor(gsub("^h|_cum90$", "", horizon), levels = c("0", "1", "3", "6", "12", "24")),
    durability = ifelse(cum90 %in% c(TRUE, "True", "TRUE"), "90 percent interval excludes zero", "includes zero"),
    label = ifelse(durability == "90 percent interval excludes zero", "yes", "")
  )

durability_plot <- ggplot(persistence, aes(x = horizon, y = response_label, fill = durability)) +
  geom_tile(color = "white", linewidth = 0.8) +
  geom_text(aes(label = label), size = 2.9, family = "serif", fontface = "bold") +
  scale_fill_manual(values = c(
    "90 percent interval excludes zero" = "#0f766e",
    "includes zero" = "#e5e7eb"
  )) +
  labs(
    title = "Cumulative Horizon Durability",
    subtitle = "Cells show where cumulative 90 percent intervals exclude zero.",
    x = "Horizon in months",
    y = NULL,
    caption = "Source: results/final/uncertainty/persistence_confidence_matrix.csv."
  ) +
  theme_thesis(11) +
  theme(panel.grid = element_blank())
write_plot(durability_plot, "horizon_durability_matrix.png", 9.8, 5.6)

stab <- read_artifact("results", "final", "stability", "monthly_cumulative_stability_long.csv") %>%
  filter(response %in% selected, horizon_months %in% c(6, 12, 24)) %>%
  mutate(
    response_label = factor(response_label, levels = rev(response_order)),
    filter = factor(
      sample_name,
      levels = c("full", "clean_events_only", "contaminated_events_only",
                 "exclude_covid", "exclude_crisis_windows",
                 "exclude_extreme_shock_outliers", "exclude_qe_launch"),
      labels = c("full", "clean", "contaminated", "ex-COVID",
                 "ex-crisis", "ex-outliers", "ex-QE launch")
    ),
    horizon_months = factor(paste0("h", horizon_months), levels = c("h6", "h12", "h24")),
    direction = case_when(
      cumulative_response > 0 ~ "positive",
      cumulative_response < 0 ~ "negative",
      TRUE ~ "mixed"
    )
  )

robustness_matrix <- ggplot(stab, aes(x = filter, y = response_label, fill = direction)) +
  geom_tile(color = "white", linewidth = 0.65) +
  facet_wrap(~horizon_months, nrow = 1) +
  scale_fill_manual(values = c("positive" = "#0f766e", "negative" = "#b91c1c", "mixed" = "#d1d5db")) +
  labs(
    title = "Robustness Consistency Matrix",
    subtitle = "Cumulative response direction across event filters and historical exclusions at medium and long horizons.",
    x = NULL,
    y = NULL,
    caption = "Source: results/final/stability/monthly_cumulative_stability_long.csv."
  ) +
  theme_thesis(10) +
  theme(
    panel.grid = element_blank(),
    axis.text.x = element_text(angle = 35, hjust = 1)
  )
write_plot(robustness_matrix, "robustness_consistency_matrix.png", 11.2, 6.2)

metrics <- read_artifact("results", "final", "stability", "monthly_stability_metrics.csv") %>%
  filter(response %in% selected) %>%
  mutate(response_label = factor(response_label, levels = response_order)) %>%
  select(response_label, sign_consistency, cumulative_direction_consistency) %>%
  pivot_longer(
    cols = c(sign_consistency, cumulative_direction_consistency),
    names_to = "metric",
    values_to = "value"
  ) %>%
  mutate(metric = factor(
    metric,
    levels = c("sign_consistency", "cumulative_direction_consistency"),
    labels = c("Sign consistency", "Cumulative direction consistency")
  ))

robustness_summary <- ggplot(metrics, aes(x = response_label, y = value, fill = metric)) +
  geom_col(position = position_dodge(width = 0.72), width = 0.62) +
  coord_flip() +
  scale_y_continuous(limits = c(0, 1.05), breaks = seq(0, 1, 0.25)) +
  scale_fill_manual(values = c("Sign consistency" = "#1d4ed8", "Cumulative direction consistency" = "#0f766e")) +
  labs(
    title = "Robustness Summary",
    subtitle = "Stability metrics summarize whether response signs and cumulative directions survive robustness layers.",
    x = NULL,
    y = "Share of consistent robustness cells",
    caption = "Source: results/final/stability/monthly_stability_metrics.csv."
  ) +
  theme_thesis(11)
write_plot(robustness_summary, "robustness_summary.png", 9.8, 5.8)

flow_boxes <- data.frame(
  x = 1:5,
  y = 1,
  label = c(
    "ECB policy-news\nsurprise",
    "Financial conditions\nand lending spreads",
    "Housing-finance\nresponses",
    "Affordability-sensitive\naccess pressure",
    "Compensation-pressure\ndynamics"
  ),
  fill = c("#1d4ed8", "#0f766e", "#92400e", "#7e22ce", "#374151")
)

flow <- ggplot(flow_boxes, aes(x = x, y = y)) +
  xlim(0.45, 5.55) +
  ylim(0.55, 1.65) +
  geom_segment(
    data = data.frame(x = 1.48:4.48, xend = 1.78:4.78),
    aes(x = x, xend = xend, y = 1, yend = 1),
    inherit.aes = FALSE,
    arrow = arrow(type = "closed", length = unit(0.14, "inches")),
    linewidth = 0.55,
    color = "#111827"
  ) +
  geom_rect(
    aes(xmin = x - 0.39, xmax = x + 0.39, ymin = 0.78, ymax = 1.22, fill = fill),
    color = "white",
    linewidth = 0.8
  ) +
  geom_text(aes(label = label), color = "white", family = "serif", fontface = "bold", size = 3.2, lineheight = 0.95) +
  annotate(
    "text",
    x = 3,
    y = 1.48,
    label = "Conceptual contribution: persistent financial and housing-finance responses can amplify affordability-sensitive dynamics relative to compensation pressure.",
    family = "serif",
    size = 3.35,
    fontface = "bold",
    color = "#111827"
  ) +
  scale_fill_identity() +
  labs(
    title = "Affordability-Sensitive Transmission Channel",
    subtitle = "The diagram positions the empirical comparison; it is not a structural mediation estimate.",
    caption = "Source: author synthesis from the thesis research design."
  ) +
  theme_void(base_family = "serif", base_size = 11) +
  theme(
    plot.title = element_text(face = "bold", size = 13, margin = margin(b = 3)),
    plot.subtitle = element_text(color = "#4b5563", margin = margin(b = 4)),
    plot.caption = element_text(color = "#4b5563", hjust = 0),
    plot.margin = margin(12, 14, 8, 14)
  )
write_plot(flow, "conceptual_affordability_transmission_flow.png", 10.4, 3.2)

message("Created enhancement figures in ", fig_dir)
