library(ggplot2)
library(dplyr)
library(tidyr)

input_file <- "01_Data/Processed_Data/energy_prices_final.csv"
output_dirs <- c("03_Output_Logs/")

df <- read.csv(input_file)
df$Date <- as.Date(df$Date)

df_long <- df %>%
  select(Date, Gas_Index, Electricity_Index) %>%
  pivot_longer(cols = c(Gas_Index, Electricity_Index), 
               names_to = "Fuel", 
               values_to = "Index") %>%
  mutate(Fuel = ifelse(Fuel == "Gas_Index", "Gas", "Electricity"))

max_y <- max(df_long$Index, na.rm = TRUE)
y_limit <- max_y * 1.15 # Keep padding at top for lines
label_y <- max_y * 0.05 # Position labels slightly above the x-axis (y=0)

p <- ggplot(df_long, aes(x = Date, y = Index, color = Fuel)) +
  geom_line(linewidth = 1.2) +
  theme_minimal(base_size = 14) +
  scale_color_manual(values = c("Gas" = "#E41A1C", "Electricity" = "#377EB8")) +
  
  coord_cartesian(ylim = c(0, y_limit), expand = FALSE) +
  
      labs(x = "Year", y = "Price Index (2010 = 100)", 
  
           colour = "Fuel Type") +
  
  geom_vline(xintercept = as.Date("2019-01-01"), linetype = "dashed", color = "grey50") +
  annotate("text", x = as.Date("2019-01-01"), y = label_y, label = "Policy Start", angle = 90, vjust = -0.5, hjust = 0, size = 3.5, color = "grey30") +
  
  geom_vline(xintercept = as.Date("2021-10-01"), linetype = "dashed", color = "grey50") +
  annotate("text", x = as.Date("2021-10-01"), y = label_y, label = "Price Spike Begins", angle = 90, vjust = -0.5, hjust = 0, size = 3.5, color = "grey30") +
  
  geom_vline(xintercept = as.Date("2022-10-01"), linetype = "dashed", color = "grey50") +
  annotate("text", x = as.Date("2022-10-01"), y = label_y, label = "EPG & EBSS Support", angle = 90, vjust = -0.5, hjust = 0, size = 3.5, color = "grey30") +
  
  theme(legend.position = "bottom")

for (dir in output_dirs) {
  if (!dir.exists(dir)) dir.create(dir, recursive = TRUE)
  ggsave(paste0(dir, "Figure4_EnergyPrices.png"), plot = p, width = 10, height = 6, dpi = 300)
}

print("Figure 4: Energy Prices Generated.")