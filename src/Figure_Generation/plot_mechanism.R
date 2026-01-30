library(ggplot2)

output_dirs <- c("03_Output_Logs/")

boxes <- data.frame(
  x = c(5, 5, 5, 5, 5),
  y = c(10, 8, 6, 4, 2),
  label = c(
    "Energy Crisis (2021-22)\nGlobal Gas Price Spike",
    "Households Reduce Heating\n'Heat-or-Eat' Trade-off",
    "Cold Surface Temperatures +\nNormal Moisture Loads",
    "Condensation & Mould\nGrowth in Damp Homes",
    "COPD Admissions Increase\n(Observed Spike)"
  )
)

arrows <- data.frame(
  x = c(5, 5, 5, 5),
  y = c(9.3, 7.3, 5.3, 3.3),
  xend = c(5, 5, 5, 5),
  yend = c(8.7, 6.7, 4.7, 2.7)
)

p <- ggplot() +
  geom_rect(data = boxes, aes(xmin = 3, xmax = 7, ymin = y - 0.6, ymax = y + 0.6), fill = "white", color = "black", size = 0.8) +
  geom_text(data = boxes, aes(x = x, y = y, label = label), size = 4.5, fontface = "bold") +
  geom_segment(data = arrows, aes(x = x, y = y, xend = xend, yend = yend), arrow = arrow(length = unit(0.3, "cm")), size = 1) +
  
  annotate("label", x = 8.5, y = 6, label = "Worse in Poor Housing\n(Unimproved EPC)", fill = "lightyellow", color = "darkred", size = 4) +
  geom_curve(aes(x = 7.5, y = 6, xend = 7, yend = 6), arrow = arrow(length = unit(0.2, "cm")), curvature = -0.2) +
  
  theme_void() +
  xlim(2, 10) + ylim(1, 11) +
  theme(plot.margin = unit(c(0,0,0,0), "cm"))

for (dir in output_dirs) {
  ggsave(paste0(dir, "Figure5_Mechanism.png"), plot = p, width = 8, height = 10, dpi = 300)
}

print("Figure 5: Mechanism Diagram Generated.")