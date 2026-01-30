ensure_package <- function(pkg) {
  if (!require(pkg, character.only = TRUE)) {
    message(paste("Installing package:", pkg))
    install.packages(pkg, repos = "http://cran.us.r-project.org")
    if (!require(pkg, character.only = TRUE)) {
      stop(paste("Failed to install/load package:", pkg))
    }
  }
}

ensure_package("ggplot2")
ensure_package("dplyr")
ensure_package("broom")

args <- commandArgs(trailingOnly = FALSE)
script_path <- sub("--file=", "", args[grep("--file=", args)])

# Default paths assuming running from Replication_Package root
input_path <- "03_Output_Logs/did_results.csv"

if (length(script_path) > 0) {
  base_dir <- dirname(script_path)
  # If running via Rscript path/to/script.R
  # script is in 02_Code/Figure_Generation
  # output is in 03_Output_Logs (../../03_Output_Logs)
  input_path <- file.path(base_dir, "../../03_Output_Logs/did_results.csv")
}

input_path <- normalizePath(input_path, mustWork = FALSE)
print(paste("Input Path:", input_path))

if (!file.exists(input_path)) {
   stop(paste("Data file not found at:", input_path, "\nPlease run did_analysis.py first."))
}

df <- read.csv(input_path)

df$Year <- as.factor(df$Year)

print("Running regression...")
model <- lm(COPD_Rate ~ Treatment_Group * Year, data = df)

print("Extracting coefficients...")
coefs <- tidy(model, conf.int = TRUE)

interaction_coefs <- coefs %>%
  filter(grepl("Treatment_Group:Year", term)) %>%
  mutate(
    Year = as.numeric(gsub("Treatment_Group:Year", "", term))
  ) %>%
  select(Year, estimate, conf.low, conf.high)

ref_year <- 2018
ref_coef <- interaction_coefs %>% filter(Year == ref_year)

if (nrow(ref_coef) == 0) {
  offset <- 0
} else {
  offset <- ref_coef$estimate
}

all_years <- sort(unique(as.numeric(as.character(df$Year))))
missing_years <- setdiff(all_years, interaction_coefs$Year)

for (yr in missing_years) {
  interaction_coefs <- rbind(interaction_coefs, data.frame(Year = yr, estimate = 0, conf.low = 0, conf.high = 0))
}

interaction_coefs <- interaction_coefs %>%
  mutate(
    estimate_norm = estimate - offset,
    conf.low_norm = conf.low - offset,
    conf.high_norm = conf.high - offset
  ) %>%
  mutate(
    conf.low_norm = ifelse(Year == ref_year, 0, conf.low_norm),
    conf.high_norm = ifelse(Year == ref_year, 0, conf.high_norm)
  )

print("Plotting...")
p <- ggplot(interaction_coefs, aes(x = Year, y = estimate_norm)) + 
  geom_hline(yintercept = 0, color = "#d73027", linetype = "dashed", linewidth = 0.8) + 
  geom_vline(xintercept = 2018.5, color = "black", linetype = "dotted", linewidth = 0.8) + 
    geom_errorbar(aes(ymin = conf.low_norm, ymax = conf.high_norm), 
                  width = 0.2, color = "#2c3e50", alpha = 0.8) + 
    geom_point(color = "#2c3e50", size = 3) + 
    labs(
      x = "Year",
      y = "Estimated Treatment Effect (Rate per 100k)"
    ) + 
    theme_minimal(base_family = "sans") + 
    theme(
      axis.title = element_text(face = "bold", size = 10),
      axis.text = element_text(size = 9, color = "black"),
      panel.grid.minor = element_blank(),
      panel.grid.major.x = element_blank(),
      panel.grid.major.y = element_line(color = "grey90"),
      plot.background = element_rect(fill = "white", color = NA)
    ) + 
    scale_x_continuous(breaks = all_years)
  
  output_path_model <- file.path(dirname(input_path), "Figure3_EventStudy.png")
  
  ggsave(output_path_model, plot = p, width = 8, height = 5, dpi = 300)
  print(paste("Plots saved to:", output_path_model))