# How Gesture–Sound Mapping Shapes Audience Perception in Digital Musical Instrument Performances

This repository contains the experimental materials, system implementation, stimuli, and analysis code for the study investigating the illusion of instrument presence in digital musical instrument performances.

The study examines how gesture--sound mapping factors, including temporal synchrony and sound type, influence the perceived presence of virtual instruments and how this perception relates to audience evaluation.

---

## Repository Structure
├── analysis/
│   ├── R scripts for statistical analyses of RQ1, RQ2, and RQ3
│   └── Anonymized participant data used for the analyses
│
├── experiment_system/
│   └── Source code for the experimental system
│
├── stimulus/
│   └── Video stimuli used in the user study
│
└── generation_stimulus/
└── Python scripts used to generate the experimental stimuli

---

## Folder Description

### `analysis/`

This folder contains the statistical analysis scripts and anonymized datasets used to evaluate the research questions.

The analyses include:

- **RQ1:** Analysis of factors influencing the illusion of instrument presence, including action type, temporal synchrony, and sound type.
- **RQ2:** Analysis of the relationship between the illusion of instrument presence and aesthetic evaluation.
- **RQ3:** Analysis of the perceived spatial location of the virtual instrument using visual mapping data.

All participant data included in this folder have been anonymized.

---

### `experiment_system/`

This folder contains the source code of the experimental system used in the user study.

The system presents gesture-based digital musical instrument performances and collects participants' responses regarding:

- perceived instrument presence
- aesthetic evaluation
- perceived instrument location

---

### `stimulus/`

This folder contains the video stimuli presented during the user study.

The stimuli include different combinations of:

- action type
- temporal synchrony between gesture and sound
- sound type (instrumental/environmental)

used to investigate factors affecting the illusion of instrument presence.

---

### `stimulus_generation/`

This folder contains Python scripts used to generate the experimental stimuli.

These scripts include procedures for:

- processing performance videos
- synchronizing gesture and sound
- generating stimulus variations used in the experiment

---

## Data Availability

The participant data provided in this repository are anonymized and intended solely for research reproducibility.

---

## Requirements

Analysis scripts require:

- R
- Required R packages are specified within each analysis script

Stimulus generation scripts require:

- Python
- Required Python packages are specified within each script

---

## Citation

If you use this repository or related materials, please cite the corresponding publication.

