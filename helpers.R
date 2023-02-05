safe_str_detect <- function(...) {
  (purrr::possibly(str_detect, FALSE, quiet = FALSE))(...) %>% {(!is.na(.) & .)}
}

get_longer <- function(vec1, vec2){
  if(is.null(vec1) | is.null(vec2)) {
    if (!is.null(vec1)) return(vec1)
    if (!is.null(vec2)) return(vec2)
    return(NA)
  }
  vec1_length <- stringr::str_length(vec1)
  vec2_length <- stringr::str_length(vec2)
  result <- ifelse(vec1_length > vec2_length, vec1, vec2)
  result[is.na(vec1) & is.na(vec2)] <- NA
  result[is.na(vec1) & !is.na(vec2)] <- vec2[is.na(vec1) & !is.na(vec2)]
  result[!is.na(vec1) & is.na(vec2)] <- vec1[!is.na(vec1) & is.na(vec2)]
  result[stringr::str_length(result) == 0] <- NA
  return(result)
}

get_longest <- function(x) {
  res <- x[which(stringr::str_length(x) == max(c(0, stringr::str_length(x)), na.rm = TRUE))]
  if (length(res) == 0) res <- NA
  res[1]
}

bind_rows_to_chr <- function(...){
  dfs <- list(...)

  # Get the column names that have different types between the data frames
  # Note that this only considers columns included in the first data frame - usually good enough here
  differing_cols <- unique(map(dfs[-1], function(df) {
    cols <- intersect(names(dfs[[1]]), names(df))
    names(which(map2_lgl(dfs[[1]][cols], df[cols], ~class(.x) != class(.y) & (is.character(.x) | is.character(.y)))))
  }) %>% unlist())

  # Convert the differing columns in all dfs to character
  dfs <- map(dfs, \(df) {
    df[intersect(differing_cols, names(df))] <- map_dfc(df[intersect(differing_cols, names(df))], as.character)
    df
    })

  # Bind the rows of all data frames, using bind_rows so that other type conflicts are shown
  bind_rows(dfs)
}

unlist_w_NULLs <- function(x) {
  x[map_lgl(x, is.null)] <- NA
  if (any(lengths(x) > 1)) warning("Some list elements had lengths > 1. Beware if using this in a dataframe.")
  unlist(x)
}

bind_rows_to_list <- function(..., .id = NULL){
  dfs <- rlang::list2(...)
  if (length(dfs) == 1) {stop("This function requires different dataframe. If they are in a list, splice them in ",
                              "the call using bind_rows_to_list(!!!dfs)")}

  # Get the column names that have different types between the data frames - and where at least one is a list
  # Note that this only considers columns included in the first data frame - usually good enough here
  differing_cols <- unique(map(dfs[-1], function(df) {
    cols <- intersect(names(dfs[[1]]), names(df))
    names(which(map2_lgl(dfs[[1]][cols], df[cols], ~class(.x) != class(.y) & (is.list(.x) | is.list(.y)))))
  }) %>% unlist())


  # Convert the differing columns in all dfs to list
  dfs <- map(dfs, \(df) {
    walk(intersect(differing_cols, names(df)), ~{df[[.x]] <<- df[[.x]] %>% as.list()})
    df
  })

  # Bind the rows of all data frames, using bind_rows so that other type conflicts are shown
  bind_rows(dfs, .id = .id)
}


# Copyright (c) 2020 Metrum Research Group under the MIT licence
# Retrieved from https://github.com/metrumresearchgroup/bbr/blob/main/LICENSE.md

collapse_to_string <- function(.data, ..., .sep = ", ") {
  checkmate::assert_scalar(.sep)

  cols <- tidyselect::eval_select(rlang::expr(c(...)), .data)

  # subset to only list cols and warn if passed any columns that are not lists
  valid_cols <- map_lgl(cols, ~ inherits(.data[[.x]], "list"))
  if (any(!valid_cols)) {
    bad_cols <- names(valid_cols)[!valid_cols]
    warning(glue("collapse_to_string() only works on list columns. The following columns are not lists and will be ignored: {paste(bad_cols, collapse = ', ')}"))
  }
  cols <- cols[valid_cols]

  # collapse together any lists of vectors
  .data %>%
    modify_at(.at = cols, .f = function(x) {
      map_chr(x, .f = function(.vec) {
        if (inherits(.vec, c("character", "numeric", "logical"))) {
          .vec <- paste0(.vec, collapse = .sep)
        } else if (is.null(.vec)) {
          .vec <- NA_character_
        } else {
          .vec <- paste(
            capture.output(dput(.vec)),
            collapse = ""
          )
        }
        return(.vec)
      })
    })
}

