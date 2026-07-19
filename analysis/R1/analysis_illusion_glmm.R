############################################################
# GLMM analysis for Illusion of Instrument Presence
#
# This script performs mixed-effects logistic regression
# analyses examining the effects of:
#   1. Temporal synchrony
#   2. Gesture type
#   3. Sound type
#   4. Combined effects of all factors
#
# Dependent variable:
#   Illusion (binary: Yes/No)
#
# Random effect:
#   Participant ID
############################################################


# ==========================================================
# Load packages
# ==========================================================

library(lme4)
library(lmerTest)
library(tidyverse)


# ==========================================================
# Load data
# ==========================================================

df_long <- read.csv(
  "data/illusion_long.csv",
  stringsAsFactors = FALSE
)


# Check structure

str(df_long)

summary(df_long)



# ==========================================================
# Model 1:
# Effect of temporal synchrony
# ==========================================================

model_timing <- glmer(
  Illusion ~ Timing + (1|ID),
  data = df_long,
  family = binomial
)

summary(model_timing)



# Odds ratios

exp(fixef(model_timing))



# ==========================================================
# Model 2:
# Effect of gesture type
# ==========================================================

model_gesture <- glmer(
  Illusion ~ Gesture + (1|ID),
  data = df_long,
  family = binomial
)

summary(model_gesture)


# Odds ratios

exp(fixef(model_gesture))



# ==========================================================
# Model 3:
# Effect of sound type
# ==========================================================

model_sound <- glmer(
  Illusion ~ Sound + (1|ID),
  data = df_long,
  family = binomial
)

summary(model_sound)


# Odds ratios

exp(fixef(model_sound))



# ==========================================================
# Model 4:
# Full factorial model
# Timing × Gesture × Sound
# ==========================================================

model_full <- glmer(
  Illusion ~ Timing * Gesture * Sound + (1|ID),
  data = df_long,
  family = binomial
)

summary(model_full)


# Odds ratios

exp(fixef(model_full))



# ==========================================================
# Save model summaries
# ==========================================================

sink(
  "results/glmm_results.txt"
)

cat("\n\n===== Timing model =====\n")
print(summary(model_timing))

cat("\n\n===== Gesture model =====\n")
print(summary(model_gesture))

cat("\n\n===== Sound model =====\n")
print(summary(model_sound))

cat("\n\n===== Full factorial model =====\n")
print(summary(model_full))

sink()
