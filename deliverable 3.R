folder <- "E:/UC Study/Data201"

files <- c(
  "Oct2025.csv",
  "Nov2025.csv",
  "Dec2025.csv",
  "Jan2026.csv",
  "Feb2026.csv",
  "Mar2026.csv",
  "Apr2026.csv",
  "May2026.csv",
  "Jun2026.csv"
)

# Month + year corresponding to each dataset
months <- c(
  "October 2025",
  "November 2025",
  "December 2025",
  "January 2026",
  "February 2026",
  "March 2026",
  "April 2026",
  "May 2026",
  "June 2026"
)

# Reusable function
process_data <- function(filename, month_label) {
  
  # Load dataset
  data <- read.csv(file.path(folder, filename))
  
  # Keep Christchurch only
  data <- subset(
    data,
    neighbourhood_group == "Christchurch City"
  )
  
  # Add month + year column
  data$month_year <- month_label
  
  return(data)
}

# Apply the function to all 9 datasets
christchurch_data <- Map(
  process_data,
  files,
  months
)

# Give each dataset a name
names(christchurch_data) <- c(
  "Oct2025",
  "Nov2025",
  "Dec2025",
  "Jan2026",
  "Feb2026",
  "Mar2026",
  "Apr2026",
  "May2026",
  "Jun2026"
)

View(christchurch_data$Oct2025)
View(christchurch_data$Jun2026)
unique(christchurch_data$Jun2026$month_year)

# creates individual vector datasets for every month.
list2env(christchurch_data, envir = .GlobalEnv)
View(Oct2025)

all_christchurch <- do.call(
  rbind,
  christchurch_data
)


# Missing values and general overview - in every column
row.names(all_christchurch) <- NULL

View(all_christchurch)


column_overview <- data.frame(
  column = names(all_christchurch),
  
  type = sapply(all_christchurch, function(x) class(x)[1]),
  
  non_missing = sapply(
    all_christchurch,
    function(x) sum(!is.na(x))
  ),
  
  missing = sapply(
    all_christchurch,
    function(x) sum(is.na(x))
  ),
  
  percent_missing = round(
    sapply(
      all_christchurch,
      function(x) mean(is.na(x)) * 100
    ),
    2
  ),
  
  unique_values = sapply(
    all_christchurch,
    function(x) length(unique(x[!is.na(x)]))
  )
)

View(column_overview)


# Numeric columns: Min, Max, Mean, sd
numeric_cols <- c(
  "latitude",
  "longitude",
  "price",
  "minimum_nights",
  "number_of_reviews",
  "reviews_per_month",
  "calculated_host_listings_count",
  "availability_365",
  "number_of_reviews_ltm"
)

numeric_summary <- data.frame(
  variable = numeric_cols,
  
  count = sapply(
    all_christchurch[numeric_cols],
    function(x) sum(!is.na(x))
  ),
  
  missing = sapply(
    all_christchurch[numeric_cols],
    function(x) sum(is.na(x))
  ),
  
  min = sapply(
    all_christchurch[numeric_cols],
    function(x) min(x, na.rm = TRUE)
  ),
  
  max = sapply(
    all_christchurch[numeric_cols],
    function(x) max(x, na.rm = TRUE)
  ),
  
  mean = sapply(
    all_christchurch[numeric_cols],
    function(x) mean(x, na.rm = TRUE)
  ),
  
  sd = sapply(
    all_christchurch[numeric_cols],
    function(x) sd(x, na.rm = TRUE)
  )
)

numeric_summary[, c("min", "max", "mean", "sd")] <-
  round(numeric_summary[, c("min", "max", "mean", "sd")], 2)

View(numeric_summary)


# Categories & counts
categorical_cols <- c(
  "neighbourhood_group",
  "neighbourhood",
  "room_type",
  "month_year"
)

categorical_summary <- do.call(
  rbind,
  lapply(categorical_cols, function(col) {
    
    counts <- table(
      all_christchurch[[col]],
      useNA = "ifany"
    )
    
    data.frame(
      variable = col,
      category = names(counts),
      count = as.numeric(counts)
    )
  })
)

row.names(categorical_summary) <- NULL

View(categorical_summary)


# ids & text columns
identifier_cols <- c(
  "id",
  "name",
  "host_id",
  "host_name",
  "license"
)

identifier_summary <- data.frame(
  variable = identifier_cols,
  
  count = sapply(
    all_christchurch[identifier_cols],
    function(x) sum(!is.na(x))
  ),
   
  missing = sapply(
    all_christchurch[identifier_cols],
    function(x) sum(is.na(x))
  ),
  colSums(is.na(all_christchurch))
  
  unique_values = sapply(
    all_christchurch[identifier_cols],
    function(x) length(unique(x[!is.na(x)]))
  )
)

View(identifier_summary)


# Store the concatenated dataset in a new file.
write.csv(
  all_christchurch,
  "E:/UC Study/Data201/all_christchurch.csv",
  row.names = FALSE
)

