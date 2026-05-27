#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(readxl)
  library(jsonlite)
})

root <- normalizePath(getwd(), mustWork = TRUE)
data_dir <- file.path(root, "data", "EU:DE")
out_dir <- file.path(root, "results", "eu_de_forensic", "tables")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

files <- sort(list.files(data_dir, full.names = TRUE))

cell_to_text <- function(x) {
  if (is.na(x)) return("")
  if (inherits(x, "POSIXt") || inherits(x, "Date")) return(format(x))
  as.character(x)
}

excel_preview <- function(path) {
  sheets <- excel_sheets(path)
  sheet_info <- list()
  for (sheet in sheets) {
    full <- tryCatch(
      read_excel(path, sheet = sheet, col_names = FALSE, .name_repair = "minimal"),
      error = function(e) e
    )
    if (inherits(full, "error")) {
      sheet_info[[sheet]] <- list(error = full$message)
      next
    }
    preview <- full[seq_len(min(nrow(full), 35)), seq_len(min(ncol(full), 12)), drop = FALSE]
    preview_matrix <- apply(as.matrix(preview), c(1, 2), cell_to_text)
    sheet_info[[sheet]] <- list(
      rows = nrow(full),
      cols = ncol(full),
      first_nonempty_row = {
        nonempty <- which(rowSums(!is.na(full) & full != "") > 0)
        if (length(nonempty)) min(nonempty) else NA_integer_
      },
      first_nonempty_col = {
        nonempty <- which(colSums(!is.na(full) & full != "") > 0)
        if (length(nonempty)) min(nonempty) else NA_integer_
      },
      preview = unname(split(preview_matrix, row(preview_matrix)))
    )
  }
  list(sheets = sheets, sheet_info = sheet_info)
}

text_preview <- function(path) {
  lines <- readLines(path, n = 10, warn = FALSE)
  list(lines = lines)
}

inventory <- list()
for (path in files) {
  ext <- tolower(tools::file_ext(path))
  info <- file.info(path)
  entry <- list(
    file = basename(path),
    path = path,
    extension = ext,
    size_bytes = unname(info$size),
    modified = format(info$mtime, "%Y-%m-%d %H:%M:%S %Z")
  )
  if (ext %in% c("xls", "xlsx")) {
    entry$excel <- excel_preview(path)
  } else if (ext %in% c("csv", "tsv")) {
    entry$text <- text_preview(path)
  }
  inventory[[basename(path)]] <- entry
}

write_json(inventory, file.path(out_dir, "file_structure_inventory.json"), pretty = TRUE, auto_unbox = TRUE)

cat("Wrote", file.path(out_dir, "file_structure_inventory.json"), "\n")
for (nm in names(inventory)) {
  cat("\nFILE:", nm, "\n")
  item <- inventory[[nm]]
  if (!is.null(item$excel)) {
    for (sheet in item$excel$sheets) {
      si <- item$excel$sheet_info[[sheet]]
      cat("  SHEET:", sheet, "rows=", si$rows, "cols=", si$cols,
          "first_nonempty_row=", si$first_nonempty_row,
          "first_nonempty_col=", si$first_nonempty_col, "\n")
      preview_rows <- si$preview[seq_len(min(length(si$preview), 8))]
      for (i in seq_along(preview_rows)) {
        cat("    r", i, ": ", paste(preview_rows[[i]], collapse = " | "), "\n", sep = "")
      }
    }
  } else if (!is.null(item$text)) {
    for (line in item$text$lines[seq_len(min(length(item$text$lines), 4))]) {
      cat("  ", substr(line, 1, 220), "\n", sep = "")
    }
  }
}
