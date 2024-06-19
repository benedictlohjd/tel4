library(tidyverse)

set.seed(1)

subjects <- read_csv("subjectV2cut18062024.csv")
lat_long <- read_csv("loc_lat_long_V1_and_V2_17Jun2024_0.csv")

test2 <- left_join(subjects, lat_long, by = c("Name", "Mobile"))

drop_missing_lat_long <- test2[-which(is.na(test2$WS1_Postal_lat)),]

# write.csv(drop_missing_lat_long, "joined_lat_long.csv")

clusters <- read_csv("clusters.csv")

assign_group <- function(n) {
  assigned <- sample.int(4, size = 4, replace = FALSE)
  if (n == 5) {
    assigned <- c(assigned, sample.int(4, size = 1, replace = FALSE))
  }
  return(assigned)
}

res <- clusters %>% 
  group_by(cluster_id) %>% 
  mutate(group_id = assign_group(n()))