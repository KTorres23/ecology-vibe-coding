# Install packages if you haven't already
# install.packages(c("rgbif", "ggplot2", "dplyr", "maps", "readr"))

library(rgbif)
library(ggplot2)
library(dplyr)
library(maps)

ept_keys <- c(787, 1003, 1225)
# 2. Request the Download
# NOTE: This requests ALL records. This can be millions of rows.
# Replace the placeholders with your GBIF account details.
user <- ""
pwd <- ""
email <- ""

# We use predicates to filter for records with coordinates and no major issues.
download_job <- occ_download(
  pred_in("taxonKey", ept_keys),
  pred("hasCoordinate", TRUE),
  pred("hasGeospatialIssue", FALSE),
  pred("occurrenceStatus", "PRESENT"),
  format = "SIMPLE_CSV", # Faster and lighter for occurrence data
  user = user,
  pwd = pwd,
  email = email
)

# 3. Wait and Import
# This will pause your R session until GBIF finishes preparing the file.
occ_download_wait(download_job)

# Download the file to your computer and import it into R
ept_data <- occ_download_get(download_job) %>%
  occ_download_import()

# 4. Clean Data (Optional but recommended)
# GBIF column names: 'decimalLatitude', 'decimalLongitude', and 'order'
plot_data <- ept_data %>%
  filter(!is.na(decimalLongitude) & !is.na(decimalLatitude)) |>
  filter(order %in% c("Trichoptera", "Plecoptera", "Ephemeroptera"))

# 5. Map the Data
world <- map_data("world")

save <- ggplot() +
  # Draw the world base map
  geom_polygon(
    data = world,
    aes(x = long, y = lat, group = group),
    fill = "#f0f0f0",
    color = "white"
  ) +
  # Plot occurrence points colored by Order
  geom_point(
    data = plot_data,
    aes(x = decimalLongitude, y = decimalLatitude, color = order),
    alpha = 0.4,
    size = 0.5
  ) +
  # Custom Colors
  scale_color_manual(
    values = c(
      "Plecoptera" = "#E41A1C", # Red
      "Trichoptera" = "#377EB8", # Blue
      "Ephemeroptera" = "#4DAF4A"
    )
  ) + # Green
  theme_minimal() +
  labs(
    title = "Global Distribution of Ephemeroptera, Plecoptera, and Trichoptera",
    subtitle = paste("Total records:", nrow(plot_data)),
    caption = "Data Source: GBIF.org",
    color = "Order"
  ) +
  coord_fixed(1.3)

# save as png
ggsave("ept_map.png")
