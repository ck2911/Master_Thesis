#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(readxl)
  library(jsonlite)
})

root <- normalizePath(getwd(), mustWork = TRUE)
data_dir <- file.path(root, "data", "EU:DE")
out_dir <- file.path(root, "results", "eu_de_forensic", "tables")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

as_num <- function(x) suppressWarnings(as.numeric(gsub("[^0-9.\\-]", "", as.character(x))))

month_end <- function(d) {
  d <- as.Date(d)
  as.Date(vapply(d, function(one_date) {
    first <- as.Date(format(one_date, "%Y-%m-01"))
    as.character(seq(first, by = "1 month", length.out = 2)[2] - 1)
  }, character(1)))
}

quarter_end <- function(d) {
  d <- as.Date(d)
  as.Date(vapply(d, function(one_date) {
    y <- as.integer(format(one_date, "%Y"))
    m <- as.integer(format(one_date, "%m"))
    qm <- ((m - 1) %/% 3 + 1) * 3
    first <- as.Date(sprintf("%04d-%02d-01", y, qm))
    as.character(seq(first, by = "1 month", length.out = 2)[2] - 1)
  }, character(1)))
}

merge_series <- function(series_list) {
  Reduce(function(x, y) merge(x, y, by = "date", all = TRUE), series_list)
}

read_ecb_portal <- function(path, name) {
  x <- read_excel(path, sheet = "DATA", col_names = FALSE, .name_repair = "minimal")
  data <- x[16:nrow(x), c(1, 3)]
  names(data) <- c("date", name)
  data$date <- as.Date(data$date)
  data[[name]] <- as_num(data[[name]])
  data[!is.na(data$date), ]
}

metadata <- list()
add_meta <- function(variable, file, geography, frequency, unit, source, transform, notes) {
  metadata[[length(metadata) + 1]] <<- data.frame(
    variable = variable,
    file = file,
    geography = geography,
    frequency = frequency,
    unit = unit,
    source = source,
    transformation_status = transform,
    notes = notes,
    stringsAsFactors = FALSE
  )
}

# 1. Wu-Xia Euro Area shadow rate.
wx_path <- file.path(data_dir, "1. Wu-Xia Euro Area Shadow Rate.xls")
wx <- read_excel(wx_path, sheet = 1, col_names = FALSE, .name_repair = "minimal")
names(wx) <- c("yyyymm", "wx_shadow_rate")
wx$yyyymm <- as.integer(wx$yyyymm)
wx$date <- as.Date(sprintf("%04d-%02d-01", wx$yyyymm %/% 100, wx$yyyymm %% 100))
wx$date <- month_end(wx$date)
wx <- wx[, c("date", "wx_shadow_rate")]
add_meta("wx_shadow_rate", basename(wx_path), "Euro Area", "Monthly", "percent",
         "Wu-Xia", "raw policy shadow-rate level", "No metadata/header row; two columns YYYYMM and value; ends in 2022-08.")

# 2. Annual Eurosystem consolidated balance sheet.
bs_path <- file.path(data_dir, "2. Annual_consolidated_balance_sheet_Eurosystem.xls")
bs <- read_excel(bs_path, sheet = 1, col_names = FALSE, .name_repair = "minimal")
years <- as.integer(gsub(".*(19|20)([0-9]{2}).*", "\\1\\2", as.character(unlist(bs[5, -1]))))
extract_bs_row <- function(label_regex, var_name) {
  idx <- grep(label_regex, as.character(bs[[1]]), ignore.case = TRUE)
  if (!length(idx)) return(NULL)
  vals <- as_num(unlist(bs[idx[1], -1]))
  data.frame(date = as.Date(sprintf("%04d-12-31", years)), value = vals, variable = var_name)
}
bs_long <- rbind(
  extract_bs_row("^Total assets$", "ecb_total_assets"),
  extract_bs_row("Securities held for monetary policy purposes", "ecb_monetary_policy_securities")
)
bs_wide <- reshape(bs_long, idvar = "date", timevar = "variable", direction = "wide")
names(bs_wide) <- sub("^value\\.", "", names(bs_wide))
add_meta("ecb_total_assets", basename(bs_path), "Eurosystem", "Annual", "EUR millions",
         "ECB annual consolidated balance sheet", "year-end stock level", "Metadata rows 1-5; row 27 is Total assets; annual only.")
add_meta("ecb_monetary_policy_securities", basename(bs_path), "Eurosystem", "Annual", "EUR millions",
         "ECB annual consolidated balance sheet", "year-end stock level", "Row 23 is Securities held for monetary policy purposes; annual only.")

# 3. ECB deposit facility rate.
dfr_path <- file.path(data_dir, "3. ECB Deposit Facility Rate.xlsx")
dfr <- read_excel(dfr_path, sheet = "Daily, 7-Day")
dfr$date <- as.Date(dfr$observation_date)
dfr$month <- month_end(dfr$date)
dfr_m_last <- aggregate(dfr$ECBDFR, by = list(date = dfr$month), FUN = function(z) tail(z[!is.na(z)], 1))
names(dfr_m_last) <- c("date", "dfr_eop")
dfr_m_avg <- aggregate(dfr$ECBDFR, by = list(date = dfr$month), FUN = mean, na.rm = TRUE)
names(dfr_m_avg) <- c("date", "dfr_avg")
dfr_m <- merge(dfr_m_last, dfr_m_avg, by = "date", all = TRUE)
add_meta("dfr_eop", basename(dfr_path), "Euro Area", "Daily to monthly", "percent",
         "FRED / ECB", "end-of-month policy-rate level", "README metadata; daily data; piecewise constant.")
add_meta("dfr_avg", basename(dfr_path), "Euro Area", "Daily to monthly", "percent",
         "FRED / ECB", "monthly average policy-rate level", "Alternative aggregation for robustness.")

# 4 and 5. ECB MFI loans.
hh_path <- file.path(data_dir, "4. loans to euro area households granted by MFIs .xlsx")
hh <- read_ecb_portal(hh_path, "hh_loans_ea_stock")
add_meta("hh_loans_ea_stock", basename(hh_path), "Euro Area changing composition", "Monthly",
         "EUR millions", "ECB Data Portal BSI", "adjusted stock level, end of period",
         "Metadata rows 1-14; data from row 16; already adjusted loans, not a growth rate.")

nfc_path <- file.path(data_dir, "5. Adjusted loans to euro area NFCs granted by MFIs.xlsx")
nfc <- read_ecb_portal(nfc_path, "nfc_loans_ea_stock")
add_meta("nfc_loans_ea_stock", basename(nfc_path), "Euro Area changing composition", "Monthly",
         "EUR millions", "ECB Data Portal BSI", "adjusted stock level, end of period",
         "Metadata rows 1-14; data from row 16; already adjusted loans, not a growth rate.")

# 6 and 6.1. Credit standards.
ent_path <- file.path(data_dir, "6. Credit standards-Overall-Enterprise, Euro area, Quarterly.xlsx")
ent <- read_ecb_portal(ent_path, "credit_standards_enterprise")
ent$date <- quarter_end(ent$date)
add_meta("credit_standards_enterprise", basename(ent_path), "Euro Area changing composition", "Quarterly",
         "percent net tightening", "ECB Bank Lending Survey", "diffusion/survey balance",
         "Beginning-of-period survey series; bounded and likely stationary.")

hcs_path <- file.path(data_dir, "6.1 Credit standards-Household, Euro area, Quarterly.xlsx")
hcs <- read_ecb_portal(hcs_path, "credit_standards_household")
hcs$date <- quarter_end(hcs$date)
add_meta("credit_standards_household", basename(hcs_path), "Euro Area changing composition", "Quarterly",
         "percent net tightening", "ECB Bank Lending Survey", "diffusion/survey balance",
         "Beginning-of-period survey series; household/mortgage lending standards.")

# 7. Residential prices.
hpi_path <- file.path(data_dir, "7. Residential prices.xlsx")
hpi <- read_excel(hpi_path, sheet = "Quarterly")
hpi$date <- quarter_end(as.Date(hpi$observation_date))
hpi <- data.frame(date = hpi$date, house_price_de = as_num(hpi$QDEN628BIS))
add_meta("house_price_de", basename(hpi_path), "Germany", "Quarterly", "index 2010=100",
         "FRED / BIS", "nominal residential-property-price index level",
         "Not seasonally adjusted; quarter-start dates converted to quarter-end.")

# 8. DAX 40.
dax_path <- file.path(data_dir, "8. DAX 40.csv")
dax <- read.csv(dax_path, stringsAsFactors = FALSE)
dax$date <- as.Date(dax$Date)
dax <- data.frame(date = dax$date, dax_close = as.numeric(dax$Close), dax_volume = as.numeric(dax$Volume))
add_meta("dax_close", basename(dax_path), "Germany", "Monthly", "index level",
         "CSV market data", "month-end close", "Financial asset proxy; source metadata absent in file.")

# 9. Compensation per employee.
comp_path <- file.path(data_dir, "9. Compensation per employee.xlsx")
comp <- read_ecb_portal(comp_path, "compensation_ea20_nominal")
comp$date <- quarter_end(comp$date)
add_meta("compensation_ea20_nominal", basename(comp_path), "Euro Area 20 fixed composition", "Quarterly",
         "index", "ECB Data Portal MNA", "nominal index level, average through period",
         "Not Germany-specific; requires HICP deflation for purchasing-power proxy.")

# 10. Retail volume growth.
retail_path <- file.path(data_dir, "10 volume of sales in wholesale and retail trade .xlsx")
ret <- read_excel(retail_path, sheet = "Sheet 1", col_names = FALSE, .name_repair = "minimal")
month_cells <- as.character(unlist(ret[10, ]))
month_cols <- which(grepl("^[0-9]{4}-[0-9]{2}$", month_cells))
de_row <- which(as.character(ret[[1]]) == "Germany" &
                  as.character(ret[[2]]) == "Retail trade, except of motor vehicles and motorcycles")[1]
retail_mom <- as_num(unlist(ret[de_row, month_cols]))
retail_dates <- month_end(as.Date(paste0(month_cells[month_cols], "-01")))
retail <- data.frame(date = retail_dates, retail_de_mom_pct = retail_mom)
retail$retail_de_chained_index <- 100 * cumprod(1 + retail$retail_de_mom_pct / 100)
add_meta("retail_de_mom_pct", basename(retail_path), "Germany", "Monthly", "percent",
         "Eurostat STS", "seasonally and calendar-adjusted percentage change on previous period",
         "Not a volume index level; data row is Germany retail trade; adjacent columns are flags.")
add_meta("retail_de_chained_index", basename(retail_path), "Germany", "Monthly", "constructed index",
         "Derived from Eurostat STS growth file", "chain index normalized to 2005-01=100",
         "Useful for visualization only; not an official downloaded level index.")

# 11. HICP.
hicp_path <- file.path(data_dir, "11. HICP - monthly data (index).tsv")
hicp_raw <- read.delim(hicp_path, sep = "\t", check.names = FALSE, stringsAsFactors = FALSE)
key_col <- names(hicp_raw)[1]
read_hicp_key <- function(key, var_name) {
  row <- hicp_raw[hicp_raw[[key_col]] == key, , drop = FALSE]
  if (!nrow(row)) return(NULL)
  dates <- trimws(names(row)[-1])
  vals <- as_num(unlist(row[1, -1]))
  data.frame(date = month_end(as.Date(paste0(dates, "-01"))), value = vals, variable = var_name)
}
hicp_long <- rbind(
  read_hicp_key("M,I05,CP00,DE", "hicp_de"),
  read_hicp_key("M,I05,CP00,EA20", "hicp_ea20"),
  read_hicp_key("M,I05,CP00,EA", "hicp_ea")
)
hicp_wide <- reshape(hicp_long, idvar = "date", timevar = "variable", direction = "wide")
names(hicp_wide) <- sub("^value\\.", "", names(hicp_wide))
add_meta("hicp_de", basename(hicp_path), "Germany", "Monthly", "index 2015=100",
         "Eurostat HICP", "headline price-level index", "Wide TSV; selected CP00 Germany row.")
add_meta("hicp_ea20", basename(hicp_path), "Euro Area 20", "Monthly", "index 2015=100",
         "Eurostat HICP", "headline price-level index", "Wide TSV; selected CP00 EA20 row for real EA compensation.")
add_meta("hicp_ea", basename(hicp_path), "Euro Area aggregate", "Monthly", "index 2015=100",
         "Eurostat HICP", "headline price-level index", "Wide TSV; retained for robustness.")

monthly <- merge_series(list(wx, dfr_m, hh, nfc, dax, retail, hicp_wide))
monthly <- monthly[order(monthly$date), ]
monthly$dax_real_de <- with(monthly, dax_close / hicp_de * 100)
monthly$hh_loans_real_de_hicp <- with(monthly, hh_loans_ea_stock / hicp_de * 100)
monthly$nfc_loans_real_de_hicp <- with(monthly, nfc_loans_ea_stock / hicp_de * 100)

q_last <- function(df, cols) {
  out <- data.frame(date = quarter_end(df$date))
  for (col in cols) out[[col]] <- df[[col]]
  do.call(rbind, lapply(split(out, out$date), function(z) {
    z <- z[order(z$date), , drop = FALSE]
    z[nrow(z), , drop = FALSE]
  }))
}
q_mean <- function(df, cols) {
  out <- data.frame(date = quarter_end(df$date))
  for (col in cols) out[[col]] <- df[[col]]
  aggregate(out[, cols, drop = FALSE], by = list(date = out$date), FUN = mean, na.rm = TRUE)
}

policy_q <- q_mean(merge(wx, dfr_m, by = "date", all = TRUE), c("wx_shadow_rate", "dfr_avg", "dfr_eop"))
loans_q <- q_last(merge(hh, nfc, by = "date", all = TRUE), c("hh_loans_ea_stock", "nfc_loans_ea_stock"))
dax_q <- q_last(dax, c("dax_close"))
retail_q <- q_mean(retail, c("retail_de_mom_pct", "retail_de_chained_index"))
hicp_q <- q_mean(hicp_wide, c("hicp_de", "hicp_ea20", "hicp_ea"))
annual_q4 <- bs_wide

quarterly <- merge_series(list(policy_q, loans_q, ent, hcs, hpi, comp, dax_q, retail_q, hicp_q, annual_q4))
quarterly <- quarterly[order(quarterly$date), ]
quarterly$house_price_de_real <- with(quarterly, house_price_de / hicp_de * 100)
quarterly$compensation_ea20_real <- with(quarterly, compensation_ea20_nominal / hicp_ea20 * 100)
quarterly$dax_real_de <- with(quarterly, dax_close / hicp_de * 100)
quarterly$hh_loans_real_de_hicp <- with(quarterly, hh_loans_ea_stock / hicp_de * 100)
quarterly$nfc_loans_real_de_hicp <- with(quarterly, nfc_loans_ea_stock / hicp_de * 100)

write.csv(monthly, file.path(out_dir, "eu_de_monthly_clean.csv"), row.names = FALSE)
write.csv(quarterly, file.path(out_dir, "eu_de_quarterly_clean.csv"), row.names = FALSE)
write.csv(bs_wide[order(bs_wide$date), ], file.path(out_dir, "eurosystem_balance_sheet_annual_clean.csv"), row.names = FALSE)
write.csv(do.call(rbind, metadata), file.path(out_dir, "eu_de_variable_metadata.csv"), row.names = FALSE)

summary_rows <- lapply(names(monthly)[names(monthly) != "date"], function(v) {
  z <- monthly[[v]]
  data.frame(dataset = "monthly", variable = v, start = as.character(min(monthly$date[!is.na(z)])),
             end = as.character(max(monthly$date[!is.na(z)])), observations = sum(!is.na(z)),
             missing = sum(is.na(z)), min = suppressWarnings(min(z, na.rm = TRUE)),
             max = suppressWarnings(max(z, na.rm = TRUE)))
})
summary_rows <- c(summary_rows, lapply(names(quarterly)[names(quarterly) != "date"], function(v) {
  z <- quarterly[[v]]
  data.frame(dataset = "quarterly", variable = v, start = as.character(min(quarterly$date[!is.na(z)])),
             end = as.character(max(quarterly$date[!is.na(z)])), observations = sum(!is.na(z)),
             missing = sum(is.na(z)), min = suppressWarnings(min(z, na.rm = TRUE)),
             max = suppressWarnings(max(z, na.rm = TRUE)))
}))
write.csv(do.call(rbind, summary_rows), file.path(out_dir, "eu_de_series_summary.csv"), row.names = FALSE)

cat("Wrote standardized monthly, quarterly, annual, metadata, and summary CSVs to", out_dir, "\n")
