library(ggplot2)
library(dplyr)

input_file <- "01_Data/Processed_Data/deprivation_distribution.csv"
quantile_file <- "01_Data/Processed_Data/quantiles.txt"
output_dirs <- c("03_Output_Logs/")

df <- read.csv(input_file)
quants <- read.csv(quantile_file, header = FALSE)
colnames(quants) <- c("Label", "Value")

h <- hist(df$Income_Score, breaks = 30, plot = FALSE)
max_count <- max(h$counts)
y_limit <- max_count * 1.15
label_y <- y_limit * 0.95

p <- ggplot(df, aes(x = Income_Score)) +
  geom_histogram(bins = 30, fill = "steelblue", color = "white", alpha = 0.7) +
  theme_minimal(base_size = 14) +
  
  coord_cartesian(ylim = c(0, y_limit), expand = FALSE) +
  
  labs(x = "Income Deprivation Score (IMD Domain)",
       y = "Number of MSOAs",
       color = NULL) + # No Legend Title
  
  geom_vline(data = quants, aes(xintercept = Value), linetype = "dashed", color = "grey50", linewidth = 0.8) +
  
  annotate("text", x = quants$Value[quants$Label=="Top10"], y = label_y, label = "Top 10%", angle = 90, vjust = -0.5, hjust = 1, size = 3.5, color = "grey30") +
  annotate("text", x = quants$Value[quants$Label=="Top20"], y = label_y, label = "Top 20%", angle = 90, vjust = -0.5, hjust = 1, size = 3.5, color = "grey30") +
  annotate("text", x = quants$Value[quants$Label=="Top30"], y = label_y, label = "Top 30% (Treated)", angle = 90, vjust = -0.5, hjust = 1, size = 3.5, color = "grey30", fontface = "bold") +
  annotate("text", x = quants$Value[quants$Label=="Top40"], y = label_y, label = "Top 40%", angle = 90, vjust = -0.5, hjust = 1, size = 3.5, color = "grey30") +
  
  theme(legend.position = "none") # Remove Legend

for (dir in output_dirs) {
  ggsave(paste0(dir, "Figure2_DeprivationDistribution.png"), plot = p, width = 10, height = 6, dpi = 300)
}

print("Plot 2: Deprivation Distribution Generated.")