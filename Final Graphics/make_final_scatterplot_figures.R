# final plots for beepocalypse paper
# Jenna Jordan

library(tidyverse)
library(lubridate)

df = read.csv("../Data/Analyze/BLNqueries_timeseries_weekly_3Mar.csv")
df$publication_date <- lubridate::ymd(df$publication_date)
df$publisher <- factor(df$publisher, levels=c("NYT", "WP", "AP", "AFP", "DPA", "XGNS"), ordered = TRUE)
df$region <- if_else(df$publisher %in% c("NYT", "WP", "AP"), "US News Sources", "Non-US News Sources")
df$region <- factor(df$region, levels=c("US News Sources", "Non-US News Sources"), ordered = TRUE)
#df <- df %>% drop_na()

# Climate Change
cc = select(df, publisher, region, publication_date, climate_change_proportion)
cc$climate_change_proportion <- cc$climate_change_proportion * 100

# faceted plot
cc_plot <- ggplot(cc, aes(publication_date, climate_change_proportion, color=publisher)) + 
  geom_point(shape='.') + 
  geom_smooth(method = "loess", span=.1) +
  scale_color_manual(values=c('#2171b5','#6baed6', '#bdd7e7', '#238b45', '#74c476', '#bae4b3')) +
  labs(y= "% of Total Coverage", x = "Date (aggregated weekly)", color = "Source") +
  facet_grid(region ~ .) +
  theme(strip.text.y = element_text(size = 12)) +
  ylim(0,6) 
cc_plot
ggsave("USvNonUS_ClimateChange_final.png", dpi=600)

# Pollinator Population
pp = select(df, publisher, region, publication_date, pollinator_population_proportion)
pp$pollinator_population_proportion <- pp$pollinator_population_proportion * 100

# faceted plot
pp_plot <- ggplot(pp, aes(publication_date, pollinator_population_proportion, color=publisher)) + 
  geom_point(shape='.') + 
  geom_smooth(method = "loess", span=.1) +
  scale_color_manual(values=c('#2171b5','#6baed6', '#bdd7e7', '#238b45', '#74c476', '#bae4b3')) +
  labs(y= "% of Total Coverage", x = "Date (aggregated weekly)", color = "Source") +
  facet_grid(region ~ .) +
  theme(strip.text.y = element_text(size = 12)) +
  ylim(0,.2) 
pp_plot
ggsave("USvNonUS_PollinatorPopulation_final.png", dpi=600)
