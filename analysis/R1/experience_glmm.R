############################################################
# GLMM analysis considering musical experience
#
# This script examines whether musical experience moderates
# the effects of timing, gesture type, and sound type on
# perceived illusion of instrument presence.
#
# Dependent variable:
#   Illusion (binary: Yes/No)
#
# Random effect:
#   Participant ID
#
############################################################


# ----------------------------------------------------------
# Load packages
# ----------------------------------------------------------

library(lme4)


# ----------------------------------------------------------
# Load data


df <- read.csv(
  "illusion_long_with_exp.csv",
  stringsAsFactors = TRUE
)


# ----------------------------------------------------------
# Convert variables to factors


df$Timing <- factor(
  df$Timing,
  levels = c("correct", "incorrect")
)

df$Gesture <- factor(
  df$Gesture,
  levels = c("drum", "slide")
)

df$Sound <- factor(
  df$Sound,
  levels = c("environment", "instrumental")
)

df$Experience <- factor(
  df$Experience,
  levels = c("No", "Yes")
)



# ==========================================================
# RQ1: Effect of timing considering musical experience


model_RQ1 <- glmer(
  Illusion ~ Timing * Experience + (1 | ID),
  data = df,
  family = binomial
)

summary(model_RQ1)

# Odds ratios
exp(fixef(model_RQ1))



# ==========================================================
# RQ2: Effect of gesture type considering musical experience


model_RQ2 <- glmer(
  Illusion ~ Gesture * Experience + (1 | ID),
  data = df,
  family = binomial
)

summary(model_RQ2)

# Odds ratios
exp(fixef(model_RQ2))



# ==========================================================
# RQ3: Effect of sound type considering musical experience


model_RQ3 <- glmer(
  Illusion ~ Sound * Experience + (1 | ID),
  data = df,
  family = binomial
)

summary(model_RQ3)

# Odds ratios
exp(fixef(model_RQ3))
