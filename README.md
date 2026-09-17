# Data201
Christchurch rental group project   

Dataset

source: https://docs.google.com/spreadsheets/d/1iWCNJcSutYqpULSQHlNyGInUvHg2BoUGoNRIGa6Szc4/edit?gid=1322284596#gid=1322284596

Columns
id: The unique ID of every listing - integer  

name: The name of the listing - text  

host_id: The id of the user creating the listing - integer  

host_profile_id: The id of the profile of the user - integer

host_name: Name of the user - text

neighbourhood_group: The neighbourhood group as geocoded using the latitude and longitude against neighborhoods as defined by open or public digital shapefiles - text

neighbourhood: text

latitude: The latitudinal coordinate of the listing - numeric

longitude: The longitudinal coordinate of the listing - numeric

room_type: whether the listing is for a singular private room, a shared room or the entire house - text

price: The price of the listing - currency

minimum_nights: The minimum amount of nights to book the listing - integer

number_of_reviews: The number of reviews the listing has - integer

last_review: The date of the last review - date

reviews_per_month: The average number of reviews per month the listing has over the lifetime of the listing - numeric

calculated_host_listings_count: The number of listings the host has in the current scrape, in the city/region geography - integer

availability_365: The availability of the listing x days in the future as determined by the calendar. For example if availability_365 = 10, the listing is available 10 days from now. If availability_365 = 0, the listing isn't available at the specified date in the future - integer

number_of_reviews_ltm: The number of reviews the listing has in the last 12 months - integer

license: The license/permit/registration number - text



### Quarterly Tenancy dataset
About Tenancy dataset
  Source: https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/
The dataset comes from Tenancy Services NZ and contains private rental bonds information. The data is updated monthly and contains data from January 2020 to April 2026.

Columns:

  TimeFrame: The time at which the rental information is being reported
  Location Id: Identifier for the location
  Dwelling Type: What type of dwelling for example, house, flat etc
  Number Of Beds: Number of bedrooms in the dwelling
  Total Bonds: The total number of bonds recorded in that time frame in that specific area. Essentially shows how many new tenants moved into that area
  Active Bonds: The total number of bonds held by tenancy services during the specific time frame and area. Shows how many active tenants there are
  Closed Bonds: The total number of bonds that were refunded or closed during the specific time frame and area. Shows how many tenancies ended.
  Median Rent: The median rent for the specific area
  Geometric Mean Rent: The logarithmic mean rent which reduces the impact of outliers
  Upper Quartile Rent: The 75th percentile weekly rent
  Lower Quartile Rent: The 25th percentile weekly rent
  Log Std Dev Weekly Rent: The standard deviation of the log transformation of weekly rent