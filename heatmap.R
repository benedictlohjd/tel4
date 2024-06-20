
library(tidyverse)
library(sf)
library(tmap)

# Read in data with long and lat
ws1_dat <- read.csv('C:\\Users\\bened\\OneDrive\\Desktop\\NUS-econ-predoc\\03-TEL-LG-TW-PL\\01_Data\\Output\\loc_lat_long_V1_and_V2_17Jun2024_0.csv')
# Read in data of Singapore map
sg_map <- sf::st_read("C:/Users/bened/OneDrive/Desktop/NUS-econ-predoc/03-TEL-LG-TW-PL/01_Data/MP14_SUBZONE_NO_SEA_PL.shp")
# Read in data of Singapore MRT lines
rail_lines <- sf::read_sf("C:/Users/bened/OneDrive/Desktop/NUS-econ-predoc/03-TEL-LG-TW-PL/01_Data/MasterPlan2019RailLinelayer.geojson")

ws1_dat <- ws1_dat %>% 
  dplyr::select(WS1_Postal_lat, WS1_Postal_long) %>% 
  na.omit()

ws1_sf <- ws1_dat %>% 
  sf::st_as_sf(
    coords = c("WS1_Postal_long", "WS1_Postal_lat"),
    crs=4326 # try 3857 or 4326 OR 3414 or 4757
  ) 

# Make valid coordinates/ boundaries in sg_map, and transform coordinates to be on the same coordinate system
sg_map_transformed <- sg_map %>% 
  st_make_valid() %>% 
  st_transform(crs=4326)

ws1_sg_map <- ws1_sf %>% 
  st_join(
    sg_map_transformed,
    join=st_intersects
  )

ws1_density <- ws1_sg_map %>% 
  dplyr::group_by(SUBZONE_N) %>% 
  summarize(density = n()) %>% 
  as.data.frame()

ws1_subzone_density <- sg_map %>% 
  dplyr::left_join(
    ws1_density,
    by=c('SUBZONE_N')
  )

tm_shape(ws1_subzone_density) + # tm_shape() + tm_fill() produces similar graph as qtm(shp_data, fill=x)
  tm_fill("density") + 
  tm_borders(alpha=0.5) +
  tm_shape(rail_lines) +
  tm_lines(col="black", lwd=2)

### ==================================================================== ###
### Overlay grid over map
### ==================================================================== ###

# create 5km grid
grid_5 <- st_make_grid(sg_map, cellsize = c(500, 500)) %>% 
  st_sf(grid_id = 1:length(.))

# create labels for each grid_id
grid_lab <- st_centroid(grid_5) %>% 
  cbind(st_coordinates(.))

# view the points, polygons and grid
ggplot() +
  geom_sf(data = sg_map, fill = 'white', lwd = 0.05) +
  geom_sf(data = ws1_sf, color = 'red', size = 1.7) + 
  #geom_sf(data = grid_5, fill = 'transparent', lwd = 0.1) +
  #geom_text(data = grid_lab, aes(x = X, y = Y, label = grid_id), size = 2) +
  coord_sf(datum = NA)  +
  labs(x = "") +
  labs(y = "")

