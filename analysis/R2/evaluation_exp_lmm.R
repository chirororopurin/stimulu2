##################################################
# H3: Relationship between illusion perception
# and aesthetic evaluation
#
# Linear Mixed Model
#
# Fixed effects:
#   Illusion perception
#   Musical experience
#   Illusion × Musical experience interaction
#
# Random effect:
#   Participant ID
##################################################

library(lme4)
library(lmerTest)


# Load data
df <- read.csv(
  "・・・/H3_illusion_aesthetic_long_with_experience.csv",
  stringsAsFactors = TRUE
)


# Check columns
print(colnames(df))


# Convert variables
df$ID <- factor(df$ID)

df$Illusion <- factor(
  df$Illusion,
  levels = c(0, 1)
)

df$Played_Instrument <- factor(
  df$Played_Instrument,
  levels = c("No", "Yes")
)


##################################################
# Linear mixed-effects model
##################################################

model_H3 <- lmer(
  Aesthetic_Score ~ Illusion * Played_Instrument + (1 | ID),
  data = df
)


##################################################
# Results
##################################################

summary(model_H3)


# Fixed effects only
fixef(model_H3)
