# Rtest.R

if (!requireNamespace("reticulate", quietly=TRUE)) {
  install.packages("reticulate")
}
library(reticulate)
use_python(
  "C:/Users/shanm/AppData/Local/Programs/Python/Python313/python.exe",
  required = TRUE
)

cat(">>> Using Python at:\n")
print(py_config()$python)

cat("\n>>> Importing binom_misprice:\n")
if (!py_module_available("binom_misprice")) {
  stop("❌ binom_misprice not found in this Python environment")
}
bm <- import("binom_misprice")
cat("✅ binom_misprice loaded\n")

cat("\n>>> Running compute_call_mispricing:\n")
df <- bm$compute_call_mispricing(
  symbol   = "AAPL",
  expiry   = "2025-12-19",
  steps    = 2L,
  american = FALSE
)
print(head(df, 5))
cat("…got", nrow(df), "rows with columns:", paste(colnames(df), collapse=", "), "\n")
