#!/usr/bin/env Rscript

# Rebuild the browser-ready facility dataset from the supplied updated CSV.
# Coordinates are display anchors, not rooftop geocodes; the source location remains in each record.

source_path <- "/home/ubuntu/upload/deepseek_csv_20261027_e08391.txt"
out_dir <- "data"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

split_csv_line <- function(line) {
  chars <- strsplit(line, "", fixed = TRUE)[[1]]
  values <- character(0)
  current <- ""
  quoted <- FALSE
  for (ch in chars) {
    if (ch == "\"") {
      quoted <- !quoted
      current <- paste0(current, ch)
    } else if (ch == "," && !quoted) {
      values <- c(values, trimws(current))
      current <- ""
    } else {
      current <- paste0(current, ch)
    }
  }
  c(values, trimws(current))
}

unquote_value <- function(x) {
  x <- trimws(x)
  x <- sub('^"', '', x)
  x <- sub('"$', '', x)
  x
}

lines <- readLines(source_path, warn = FALSE, encoding = "UTF-8")
rows <- lapply(lines[-1], function(line) {
  fields <- split_csv_line(line)
  # The quoted address is the reliable anchor: names and free-text remarks may each contain unquoted commas.
  address_index <- which(grepl('^"', trimws(fields)))[1]
  if (is.na(address_index) || address_index < 3L || length(fields) < address_index + 3L) {
    stop(sprintf("Could not identify name, district, address, type, contact, and remark fields in row: %s", line))
  }
  name <- paste(vapply(fields[seq_len(address_index - 2L)], unquote_value, character(1)), collapse = ", ")
  district <- unquote_value(fields[address_index - 1L])
  address <- unquote_value(fields[address_index])
  type <- unquote_value(fields[address_index + 1L])
  contact <- unquote_value(fields[address_index + 2L])
  remarks <- paste(vapply(fields[(address_index + 3L):length(fields)], unquote_value, character(1)), collapse = ",")
  c(name, district, address, type, contact, remarks)
})
raw <- as.data.frame(do.call(rbind, rows), stringsAsFactors = FALSE)
names(raw) <- c("Name", "District", "Address", "Type", "Contact", "Remarks")

normalise_district <- function(district) {
  switch(district,
    "Ropar" = "Rupnagar",
    "Shaheed Bhagat Singh Nagar (Nawanshahr)" = "Shaheed Bhagat Singh Nagar",
    "Nawanshahr" = "Shaheed Bhagat Singh Nagar",
    "Mohali" = "Sahibzada Ajit Singh Nagar",
    "Derabassi (Mohali)" = "Sahibzada Ajit Singh Nagar",
    "Khanpur (Patiala)" = "Patiala",
    "Ropar/Ludhiana" = "Ludhiana",
    "Punjab (multiple)" = "Punjab-wide",
    "Statewide" = "Statewide",
    district
  )
}

raw$mapDistrict <- vapply(raw$District, normalise_district, character(1))

region_map <- c(
  "Pathankot" = "Majha", "Gurdaspur" = "Majha", "Amritsar" = "Majha", "Tarn Taran" = "Majha",
  "Hoshiarpur" = "Doaba", "Jalandhar" = "Doaba", "Kapurthala" = "Doaba", "Shaheed Bhagat Singh Nagar" = "Doaba",
  "Ferozepur" = "Malwa", "Fazilka" = "Malwa", "Sri Muktsar Sahib" = "Malwa", "Faridkot" = "Malwa", "Moga" = "Malwa", "Ludhiana" = "Malwa", "Malerkotla" = "Malwa", "Barnala" = "Malwa", "Sangrur" = "Malwa", "Bathinda" = "Malwa", "Mansa" = "Malwa",
  "Patiala" = "Puadh", "Fatehgarh Sahib" = "Puadh", "Sahibzada Ajit Singh Nagar" = "Puadh", "Rupnagar" = "Puadh"
)
raw$region <- ifelse(raw$mapDistrict %in% names(region_map), unname(region_map[raw$mapDistrict]), "Punjab-wide")

raw$category <- ifelse(grepl("Helpline|District Office", raw$Type, ignore.case = TRUE), "Helpline / Office",
  ifelse(grepl("^Government|^District", raw$Type, ignore.case = TRUE), "Government",
    ifelse(grepl("^Private", raw$Type, ignore.case = TRUE), "Private", "NGO / Trust")))

raw$serviceGroup <- ifelse(grepl("Helpline|District Office", raw$Type, ignore.case = TRUE), "Helpline / information",
  ifelse(grepl("OOAT", raw$Type, ignore.case = TRUE), "OOAT service",
    ifelse(grepl("MMT", raw$Type, ignore.case = TRUE), "Methadone maintenance",
      ifelse(grepl("DDTC", raw$Type, ignore.case = TRUE), "DDTC",
        ifelse(grepl("50-bed", raw$Type, ignore.case = TRUE), "Model centre",
          ifelse(grepl("Government Society", raw$Type, ignore.case = TRUE), "District coordination",
            ifelse(grepl("^Private", raw$Type, ignore.case = TRUE), "Private provider",
              ifelse(grepl("^NGO", raw$Type, ignore.case = TRUE), "NGO / Trust", "Government service"))))))))

anchors <- data.frame(
  mapDistrict = c("Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib", "Fazilka", "Ferozepur", "Gurdaspur", "Hoshiarpur", "Jalandhar", "Kapurthala", "Ludhiana", "Malerkotla", "Mansa", "Moga", "Pathankot", "Patiala", "Rupnagar", "Sahibzada Ajit Singh Nagar", "Sangrur", "Shaheed Bhagat Singh Nagar", "Tarn Taran", "Punjab-wide", "Statewide"),
  anchorLat = c(31.6357, 30.3717, 30.1795, 30.6015, 30.6634, 30.3198, 30.9237, 31.9037, 31.6093, 31.2922, 31.3856, 30.9090, 30.5331, 29.8764, 30.7878, 32.3022, 30.2093, 31.0917, 30.6909, 30.1357, 31.1270, 31.3212, 30.9000, 30.9000),
  anchorLon = c(74.8787, 75.5040, 75.0471, 74.7950, 76.3803, 74.1218, 74.6103, 75.2276, 75.8460, 75.5679, 75.3053, 75.8516, 75.8808, 75.4890, 75.1594, 75.6589, 76.3397, 76.5290, 76.7115, 75.8533, 76.1599, 74.8417, 75.6700, 75.9300),
  stringsAsFactors = FALSE
)
raw <- merge(raw, anchors, by = "mapDistrict", all.x = TRUE, sort = FALSE)
if (any(is.na(raw$anchorLat))) stop("Missing display anchor for: ", paste(unique(raw$mapDistrict[is.na(raw$anchorLat)]), collapse = ", "))

# Spread same-anchor records using a deterministic sunflower arrangement for clickable, non-overlapping marks.
raw$lat <- raw$anchorLat
raw$lon <- raw$anchorLon
for (place in unique(raw$mapDistrict)) {
  idx <- which(raw$mapDistrict == place)
  count <- length(idx)
  for (position in seq_along(idx)) {
    if (count > 1L) {
      angle <- position * 2.39996323
      radius <- 0.012 + 0.016 * sqrt(position - 1)
      raw$lat[idx[position]] <- raw$anchorLat[idx[position]] + sin(angle) * radius
      raw$lon[idx[position]] <- raw$anchorLon[idx[position]] + cos(angle) * radius / cos(raw$anchorLat[idx[position]] * pi / 180)
    }
  }
}
raw$id <- sprintf("F%03d", seq_len(nrow(raw)))
raw$sourceDistrict <- raw$District
raw$sourceLocation <- raw$Address
raw$sourceRow <- seq_len(nrow(raw)) + 1L

out <- raw[c("id", "Name", "District", "Address", "Type", "Contact", "Remarks", "sourceDistrict", "sourceLocation", "mapDistrict", "region", "category", "serviceGroup", "lat", "lon", "sourceRow")]

json_escape <- function(x) {
  x <- enc2utf8(ifelse(is.na(x), "", x))
  x <- gsub("\\\\", "\\\\\\\\", x)
  x <- gsub("\"", "\\\\\"", x)
  x <- gsub("\n", "\\\\n", x, fixed = TRUE)
  x <- gsub("\r", "\\\\r", x, fixed = TRUE)
  paste0("\"", x, "\"")
}
json_row <- function(r) {
  keys <- c("id", "Name", "District", "Address", "Type", "Contact", "Remarks", "sourceDistrict", "sourceLocation", "mapDistrict", "region", "category", "serviceGroup", "lat", "lon", "sourceRow")
  values <- character(length(keys))
  for (i in seq_along(keys)) {
    key <- keys[i]
    if (key %in% c("lat", "lon")) values[i] <- sprintf("%.6f", as.numeric(r[[key]]))
    else if (key == "sourceRow") values[i] <- as.character(as.integer(r[[key]]))
    else values[i] <- json_escape(as.character(r[[key]]))
  }
  paste0("{", paste(sprintf("\"%s\":%s", keys, values), collapse = ","), "}")
}
json <- paste0("[", paste(vapply(seq_len(nrow(out)), function(i) json_row(out[i, ]), character(1)), collapse = ","), "]")
writeLines(json, file.path(out_dir, "facilities.updated.json"), useBytes = TRUE)

summary_lines <- c(
  sprintf("Updated records: %d", nrow(out)),
  sprintf("Mapped display anchors: %d", length(unique(out$mapDistrict))),
  "", "Primary categories:"
)
summary_lines <- c(summary_lines, sprintf("- %s: %d", names(sort(table(out$category), decreasing = TRUE)), as.integer(sort(table(out$category), decreasing = TRUE))))
summary_lines <- c(summary_lines, "", "Service groups:")
summary_lines <- c(summary_lines, sprintf("- %s: %d", names(sort(table(out$serviceGroup), decreasing = TRUE)), as.integer(sort(table(out$serviceGroup), decreasing = TRUE))))
writeLines(summary_lines, file.path(out_dir, "facility-refresh-summary.txt"), useBytes = TRUE)

cat(paste(summary_lines, collapse = "\n"), "\n")
