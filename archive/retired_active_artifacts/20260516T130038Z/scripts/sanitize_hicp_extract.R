#!/usr/bin/env Rscript

root <- normalizePath(getwd(), mustWork = TRUE)
source_path <- file.path(root, "archive", "source_raw_downloads", "11. HICP - monthly data (index).tsv")
output_path <- file.path(root, "data", "raw", "eu_de", "hicp_selected_cp00_de_ea20_ea.tsv")

if (!file.exists(source_path)) {
  stop("Missing archived Eurostat HICP source: ", source_path, call. = FALSE)
}

hicp <- read.delim(source_path, sep = "\t", check.names = FALSE, stringsAsFactors = FALSE)
key_col <- names(hicp)[1]
target_keys <- c("M,I05,CP00,DE", "M,I05,CP00,EA", "M,I05,CP00,EA20")

hicp[[key_col]] <- trimws(hicp[[key_col]])
names(hicp) <- trimws(names(hicp))

selected <- hicp[hicp[[key_col]] %in% target_keys, , drop = FALSE]
selected <- selected[match(target_keys, selected[[key_col]]), , drop = FALSE]

if (nrow(selected) != length(target_keys) || any(is.na(selected[[key_col]]))) {
  stop("Sanitized HICP extract did not recover exactly DE, EA, and EA20 rows.", call. = FALSE)
}

for (col in names(selected)[-1]) {
  selected[[col]] <- trimws(as.character(selected[[col]]))
}

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
write.table(selected, output_path, sep = "\t", row.names = FALSE, quote = FALSE, na = "")

cat("Wrote sanitized HICP extract: ", output_path, "\n", sep = "")
cat("Rows retained: ", paste(selected[[key_col]], collapse = ", "), "\n", sep = "")
