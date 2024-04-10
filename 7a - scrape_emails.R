library(rvest)
library(RSelenium)

driver <- rsDriver(browser="chrome", chromever = "113.0.5672.63", port = 5004L)
remote_driver <- driver[["client"]]
# Don't forget to close the session when you're done
remote_driver$close()

decode_email <- function(string) {
  r <- strtoi(substr(string, 1, 2), base = 16)
  string <- substr(string, 3, nchar(string))
  email <- character(0)
  for (i in seq(1, nchar(string), by = 2)) {
    ascii_value <- strtoi(substr(string, i, i+1), base = 16)
    xor_value <- bitwXor(ascii_value, r)
    email <- paste0(email, rawToChar(as.raw(xor_value)))
  }
  return(email)
}

vectorized_decode <- Vectorize(decode_email)

get_email <- function(doi, selenium_driver) {
  if (!stringr::str_detect(doi, stringr::fixed("doi.org"))) {
    doi <- paste0("https://doi.org/", doi)
  }
  response <- purrr::possibly(httr::GET)(doi, httr::add_headers("User-Agent" = "Mozilla/5.0"))

    if (is.null(response) || response$status_code == 403) {

    selenium_driver$navigate(doi)
    page <- selenium_driver$getPageSource() %>% .[[1]] %>% rvest::read_html()

  } else if (stringr::str_detect(response$url, "linkinghub.elsevier.com"))  {
    selenium_driver$navigate(doi)
    Sys.sleep(1)

    # Click the button that brings up details of first author (not necessarily corresponding author)
    button <- selenium_driver$findElement(using = "css selector", "div.author-group button")
    button$clickElement()

    # Wait some seconds to make sure the content is loaded
    Sys.sleep(1)

    page <- selenium_driver$getPageSource() %>% .[[1]] %>% rvest::read_html()

  } else {

    page <- rvest::read_html(response)

  }

  if (!(str_detect(tolower(page %>% rvest::html_node("title") %>%
      rvest::html_text()), "just a moment") %in% c(NA, FALSE))) {
    resp <- httr::GET(paste0("https://proxy.scrapeops.io/v1/?api_key=d899d6da-8c71-4b47-86c8-f573d084f067&url=", selenium_driver$getCurrentUrl()[[1]]))
    if (resp$status_code != 200) {
      resp <- httr::GET(paste0("https://proxy.scrapeops.io/v1/?api_key=d899d6da-8c71-4b47-86c8-f573d084f067&url=", selenium_driver$getCurrentUrl()[[1]]))
      if (resp$status_code != 200) return(NA)
    }
    page <- rvest::read_html(resp)
  }

  mailto_links <- page %>%
    rvest::html_nodes("a[href^='mailto']") %>%
    rvest::html_attr("href") %>%
    unlist() %>%
    stringr::str_remove(stringr::fixed("mailto:"))

  # Extract links with "email-protection#" in href and decode (these are encrypted by cloudflare)
  email_protection_links <- page %>%
    rvest::html_nodes("a[href*='email-protection#']") %>%
    rvest::html_attr("href") %>%
    stringr::str_replace_all(".+email-protection#", "") %>%
    vectorized_decode() %>% unlist()

  out <- c(mailto_links, email_protection_links) %>% unique()

  if (length(out) == 0) return(NA)

  out

}

input <- read.csv("email_scrape/in.csv")
output <- read.csv("email_scrape/out.csv", colClasses = "character")


input <- input %>% filter(!DOI %in% output$DOI)
ambpp <- input %>% filter(str_detect(tolower(DOI), "/ambpp")) %>% mutate(email = NA_character_)

output <- bind_rows(output, ambpp)

input <- input %>% filter(!str_detect(tolower(DOI), "/ambpp"))

for (i in seq_len(nrow(input))) {
  output <- bind_rows(output,
                      data.frame(DOI = input$DOI[i], email = paste(
                        purrr::possibly(get_email, otherwise = NA)(input$DOI[i], remote_driver), collapse = "; ")))
  message(last(output$email))
}

output %>% write.csv("email_scrape/out.csv")