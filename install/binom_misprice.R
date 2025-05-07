# Updated R wrapper for binom_misprice (place this in your R working directory or 
# copy into your project and source it)

#' binom_misprice R‑wrapper
#'
#' @description
#' Reticulate interface for the Python **binom_misprice** package.
#' Provides call, put, composite, range and batch mispricing functions.
#'
#' @import reticulate
#' @importFrom utils stop
NULL

# internal helper: load the Python package
.bpm_pkg <- function() {
  # Change "binom_misprice_env" to the name of your virtualenv if different
  reticulate::use_virtualenv("binom_misprice_env", required = TRUE)
  if (!reticulate::py_module_available("binom_misprice")) {
    stop("Python package 'binom_misprice' not found in virtualenv 'binom_misprice_env'")
  }
  reticulate::import("binom_misprice", delay_load = TRUE)
}

#' Compute call mispricing
#'
#' @param symbol      Stock ticker (character, length 1)
#' @param expiry      Expiry date (YYYY-MM-DD)
#' @param sigma       Optional flat volatility override (numeric)
#' @param r           Risk‑free rate (numeric, default 0.03)
#' @param steps       Binomial tree steps (integer, default 2)
#' @param american    Logical; TRUE = allow early exercise (default FALSE)
#' @param valuation_date  Valuation date (YYYY-MM-DD, optional)
#' @return A data.frame with columns strike, market_price, theo_price, mispricing
#' @export
compute_call_mispricing <- function(
  symbol,
  expiry,
  sigma = NULL,
  r = 0.03,
  steps = 2L,
  american = FALSE,
  valuation_date = NULL
) {
  if (!is.character(symbol) || length(symbol) != 1) stop("symbol must be a single string")
  if (!is.character(expiry) || !grepl("^\\d{4}-\\d{2}-\\d{2}$", expiry))
    stop("expiry must be 'YYYY-MM-DD'")
  if (!is.logical(american) || length(american) != 1) stop("american must be TRUE or FALSE")
  if (!is.null(valuation_date) && (!is.character(valuation_date) ||
      !grepl("^\\d{4}-\\d{2}-\\d{2}$", valuation_date)))
    stop("valuation_date must be 'YYYY-MM-DD'")

  pkg <- .bpm_pkg()
  df_py <- pkg$compute_call_mispricing(
    symbol,
    expiry,
    if (is.null(sigma)) NULL else sigma,
    r,
    as.integer(steps),
    american,
    if (is.null(valuation_date)) NULL else valuation_date
  )
  reticulate::py_to_r(df_py)
}

#' Compute put mispricing
#'
#' @export
compute_put_mispricing <- function(
  symbol,
  expiry,
  sigma = NULL,
  r = 0.03,
  steps = 2L,
  american = FALSE,
  valuation_date = NULL
) {
  if (!is.character(symbol) || length(symbol) != 1) stop("symbol must be a single string")
  if (!is.character(expiry) || !grepl("^\\d{4}-\\d{2}-\\d{2}$", expiry))
    stop("expiry must be 'YYYY-MM-DD'")
  if (!is.logical(american) || length(american) != 1) stop("american must be TRUE or FALSE")
  if (!is.null(valuation_date) && (!is.character(valuation_date) ||
      !grepl("^\\d{4}-\\d{2}-\\d{2}$", valuation_date)))
    stop("valuation_date must be 'YYYY-MM-DD'")

  pkg <- .bpm_pkg()
  df_py <- pkg$compute_put_mispricing(
    symbol,
    expiry,
    if (is.null(sigma)) NULL else sigma,
    r,
    as.integer(steps),
    american,
    if (is.null(valuation_date)) NULL else valuation_date
  )
  reticulate::py_to_r(df_py)
}

#' Compute composite mispricing
#'
#' @export
compute_composite_mispricing <- function(
  symbol,
  expiry,
  sigma = NULL,
  r = 0.03,
  steps = 2L,
  american = FALSE,
  w_call = 0.5,
  w_put  = 0.5,
  valuation_date = NULL
) {
  if (!is.character(symbol) || length(symbol) != 1) stop("symbol must be a single string")
  if (!is.character(expiry) || !grepl("^\\d{4}-\\d{2}-\\d{2}$", expiry))
    stop("expiry must be 'YYYY-MM-DD'")
  if (!is.logical(american) || length(american) != 1) stop("american must be TRUE or FALSE")
  if (!is.numeric(w_call) || !is.numeric(w_put) ||
      w_call < 0 || w_put < 0 || abs((w_call + w_put) - 1) > 1e-6)
    stop("w_call and w_put must be ≥0 and sum to 1")

  pkg <- .bpm_pkg()
  df_py <- pkg$compute_composite_mispricing(
    symbol,
    expiry,
    if (is.null(sigma)) NULL else sigma,
    r,
    as.integer(steps),
    american,
    w_call,
    w_put,
    if (is.null(valuation_date)) NULL else valuation_date
  )
  reticulate::py_to_r(df_py)
}

#' Compute mispricing over a date range
#'
#' @export
compute_mispricing_range <- function(
  symbol,
  expiry,
  start_date,
  end_date,
  factor = "composite",
  sigma = NULL,
  r = 0.03,
  steps = 2L,
  american = FALSE,
  w_call = 0.5,
  w_put  = 0.5,
  output_path = NULL
) {
  if (!is.character(symbol) || length(symbol) != 1) stop("symbol must be a single string")
  if (!is.character(expiry) || !grepl("^\\d{4}-\\d{2}-\\d{2}$", expiry))
    stop("expiry must be 'YYYY-MM-DD'")
  if (!is.character(start_date) || !grepl("^\\d{4}-\\d{2}-\\d{2}$", start_date) ||
      !is.character(end_date)   || !grepl("^\\d{4}-\\d{2}-\\d{2}$", end_date))
    stop("start_date and end_date must be 'YYYY-MM-DD'")
  if (!factor %in% c("call","put","composite")) stop("factor must be 'call', 'put' or 'composite'")
  if (!is.logical(american) || length(american) != 1) stop("american must be TRUE or FALSE")
  if (!is.numeric(w_call) || !is.numeric(w_put) ||
      w_call < 0 || w_put < 0 || abs((w_call + w_put) - 1) > 1e-6)
    stop("w_call and w_put must be ≥0 and sum to 1")
  if (!is.null(output_path) && !is.character(output_path)) stop("output_path must be a string or NULL")

  pkg <- .bpm_pkg()
  df_py <- pkg$compute_mispricing_range(
    symbol,
    expiry,
    start_date,
    end_date,
    factor,
    if (is.null(sigma)) NULL else sigma,
    r,
    as.integer(steps),
    american,
    w_call,
    w_put,
    if (is.null(output_path)) NULL else output_path
  )
  reticulate::py_to_r(df_py)
}

#' Compute mispricing in parallel batch
#'
#' @export
compute_mispricing_batch <- function(
  tickers,
  expiry,
  start_date,
  end_date,
  factor = "composite",
  sigma = NULL,
  r = 0.03,
  steps = 2L,
  american = FALSE,
  w_call = 0.5,
  w_put  = 0.5,
  max_workers = 4L,
  output_path  = NULL
) {
  if (!is.character(tickers) || length(tickers) < 1) stop("tickers must be a character vector")
  pkg <- .bpm_pkg()
  df_py <- pkg$compute_mispricing_batch(
    tickers,
    expiry,
    start_date,
    end_date,
    factor,
    if (is.null(sigma)) NULL else sigma,
    r,
    as.integer(steps),
    american,
    w_call,
    w_put,
    as.integer(max_workers),
    if (is.null(output_path)) NULL else output_path
  )
  reticulate::py_to_r(df_py)
}
