library(ggplot2)
library(dplyr)

input_file <- "01_Data/Spatial_Data/map_polygons_final.csv"
outline_file <- "01_Data/Spatial_Data/borough_outlines.csv"
output_dirs <- c("03_Output_Logs/")

df <- read.csv(input_file)
df_outlines <- read.csv(outline_file)

study_boroughs <- c('Manchester', 'Salford', 'Stockport', 'Trafford')
df$In_Sample <- ifelse(df$Borough %in% study_boroughs, "Analysis Sample", "Other GM Boroughs")

p <- ggplot() +
  geom_polygon(data = df, aes(x = x, y = y, group = ring_id, fill = factor(Eligible), alpha = In_Sample), 
               color = "white", linewidth = 0.05) +
  
  geom_segment(data = df_outlines, aes(x = x, y = y, xend = xend, yend = yend), 
               color = "black", linewidth = 0.8) +
  
  theme_void(base_size = 14) +
  scale_fill_manual(values = c("0" = "#D1E5F0", "1" = "#B2182B"),
                     labels = c("0" = "Control (Ineligible)", "1" = "Treated (Eligible)")) +
  scale_alpha_manual(values = c("Analysis Sample" = 1.0, "Other GM Boroughs" = 0.4)) +
  
  coord_fixed(ratio = 1) +
  labs(x = NULL, y = NULL,
       fill = "Eligibility Status",
       alpha = "Sample Inclusion") +
  
  theme(legend.position = "right")

for (dir in output_dirs) {
  if (!dir.exists(dir)) dir.create(dir, recursive = TRUE)
  ggsave(paste0(dir, "Figure1_Map.png"), plot = p, width = 12, height = 10, dpi = 300)
}

print("Plot 1: Map Updated.")