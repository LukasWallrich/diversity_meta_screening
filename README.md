# Code for Search and Screening

This folder contains the code (and results) for the searching and screening steps. These involved:

- Retrieval of search results (databases, as well as forward- and backward-chasing) and alignment into common tibble structure (see `1 - data access and alignment.Rmd`)
- Deduplication of results - firstly within each source, then based on DOI across sources, and then with `ASySD`-package (see `2 - deduplication.Rmd`)
- Retrieval of search results in languages other than English (from Google Scholar), scraping of their abstracts and translation (see `3 - other languages.Rmd`)

After abstract screening, some steps were automated to support full-text screening and coding:

- PDFs were automatically downloaded where Google Scholar provided full-text links, and non-English results translated (see `4 - GS foreign - get FT and prepare.Rmd` & `5 - post-screening - prepping for coding.Rmd`)
- We retrieved suggestion for coding from ChatGPT based on the abstracts (e.g., re locations, sample sizes and types of diversity and performance). These were all validated manually, yet they accelerated the process. See `6 - ChatGPT abstract coding.Rmd`.

After screening database results, we contacted authors and conducted backward citation chasing. These processes were semi-automated, so that the following code may be reusable.

- Author contacts - we scraped emails from journal websites as far as possible (see `7a - scrape_emails.R`) and then composed emails programmatically, using Apple Script to create Outlook drafts (essentially a customised mail-merge process with some extra processing steps appropriate to this context - see `7n - Contact-included-authors.Rmd`). Note that the email addresses themselves are not included here to reduce spam - that list is available on reasonable request.
- Backwards citation chasing in included articles - we extracted references in included articles from Scopus where possible, and with GROBID otherwise (see `8 - extract for backwards citation chasing.Rmd`), and then filtered them for screening using the ChatGPT API alongside the original search string (see `9 - backwards-chasing automated screening.Rmd`)