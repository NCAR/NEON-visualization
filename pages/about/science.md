---
layout: default
title: Our Science
---

## Our Science

### Vision ###

To provide localized and personalized risk information to all people affected by hurricanes and tropical cyclones for the purpose of saving lives and reducing property damage.

### Introduction ###

The HurricaneRiskCalculator&reg; web app is a public-facing decision support tool based on a probabilistic risk framework that intersects real-time tropical cyclone wind hazard predictions with information from a structural vulnerability assessment. Through this intersection of hazard, vulnerability, and exposure, the tool calculates the risks of various consequences, such as different degrees of structural damage and whether the structure will be habitable following the tropical cyclone.

### About the structural vulnerability assessment ###

When a user first registers with the web app, the tool directs them to our partner, [ResilientResidence (ResRe)](https://www.resilientresidence.com/), to take a guided structural vulnerability assessment questionnaire about the attributes of their residence. ResRe uses expert engineering judgment to compute a Cyclone Resilience Score and assign fragility curves for the various components and characteristics of the user's building. ResRe is a resources provided by the [Cyclone Testing Station at James Cook University](https://www.jcu.edu.au/cyclone-testing-station) and currently includes typical construction styles for single-family homes in Australia and the Unisted States. 

### About the wind hazard model ###

HurricaneRiskCalculator is driven by real-time wind hazard outputs from the [Forecasts of Hurricanes using Large-Ensemble Outputs (FHLO) model](https://tcs.mit.edu/)\*, a probabilistic tropical cyclone (TC) forecast framework at the Massachusetts Institute of Technology (MIT) that quantifies the forecast uncertainty of a TC. This is achieved by generating probabilistic forecasts of track, intensity, and wind speed that incorporate the state-dependent uncertainty in the large-scale field. The main goal of FHLO is to provide useful probabilistic forecasts of wind at fixed points in space, but these require large-ensembles with on the order of 1000 members or more to fully represent the probability of extreme winds. FHLO accomplishes this by using a computationally inexpensive framework, which consists of three components: (1) a track model that generates synthetic tracks from the TC tracks of an ensemble numerical weather prediction (NWP) model, (2) a simplified intensity model (FAST - see [Emanuel (2017)](https://link.springer.com/article/10.1007/s11069-017-2890-7)) that predicts the intensity along each synthetic track, and (3) a TC wind field model that estimates the time-varying two-dimensional surface wind field. The intensity and wind field of a TC evolve as though the TC were embedded in a time-evolving environmental field, which is derived from the forecast fields of ensemble NWP models. See [Lin et. al. (2020)](https://doi.org/10.1175/WAF-D-19-0255.1) for more details. FHLO is run in real-time at NCAR and disseminated via the [Tropical Cyclone Guidance Project (TCGP)](http://hurricanes.ral.ucar.edu/).

\* Copyright Notice and Disclaimer. The data incorporated herein is generated from the use of the Massachusetts Institute of Technology (MIT)’s Forecasts of Hurricanes Using Large-ensemble Outputs (FHLO) version 1.5, © MIT, used with permission. All Rights Reserved.

### Putting it all together ###

#### Wind Hazard ####

HurricaneRiskCalculator's first feature is a Wind Hazard tool which provides information about the predicted wind hazard related to the tropical cyclone at the user's location. First, the tool provides information about the probability that winds will exceed the following wind speed thresholds:
* Tropical Storm (39+ mph)
* Gale (58+ mph)
* Category 1 Hurricane (74+ mph)
* Category 2 Hurricane (96+ mph)
* Category 3 Hurricane (111+ mph)
* Category 4 Hurricane (130+ mph)
* Category 5 Hurricane (157+ mph)
Then, the tool provides information about the Time of Arrival of the winds, including the earliest reasonable (0.1% probability) and expected time of arrival (50% probability). The tool also provides information about the Time of Departure of winds, including the expected (50% probability) and latest reasonable (99.9% probability) departure time for winds. The tool also provides information about the Duration of Winds, including the expected (50% probability) and longest reasonable (99.9% probability) duration of winds for each wind speed threshold. Outputs are provided both in a plain-language summary (basic view) and in tables and a plot that provides the instantaneous probability density function and the cumulative density function for wind exceedance (advanced view).

#### Risk of Wind Damage ####

In a coming feature (late 2021), HurricaneRiskCalculator will use the ResRe-provided fragility curves to intersect the user’s structural vulnerability with the predicted probabilistic wind hazard for the user’s location (geolocated from the user’s provided address). This allows the tool to provide actionable information about potential tropical cyclone impacts at a user’s specific location and structure and then contextualize the potential risks into easily understandable forms that we hope in several years willwill become accurate enough to guide effective evacuation decisions and optimize the timing of other protective actions. The combination of structural vulnerability information with real-time wind hazard prediction via a probabilistic risk framework provides a powerful means of providing decision support that considers the various sources of uncertainty in the predicted tropical cyclone wind hazard and the underlying uncertainty about the structural vulnerability of the asset itself. 

### Researcher Collective ###

To bring in the relevant expertise needed for an interdisciplinary project like this, a [“Researcher Collective”](../involvement/collective.htm) was established in 2019, comprised of 41 researchers and practitioners. The Researcher Collective spans the disciplines of meteorology, numerical and geophysical modeling, verification, structural engineering, cloud computing, user design and user experience, social science, utility modeling, storm surge modeling, cognitive psychology, emergency management, and human vulnerability. 

### Journal articles related to this project ###

* Wind hazard model component
   * Lin, J., K. Emanuel, and J. L. Vigh, 2020: Forecasts of Hurricanes Using Large-Ensemble Outputs. Weather and Forecasting, 35 (5), 1713-1731, [https://doi.org/10.1175/WAF-D-19-0255.1](https://doi.org/10.1175/WAF-D-19-0255.1).
   * Emanuel, K. A fast intensity simulator for tropical cyclone risk analysis. Nat Hazards 88, 779–796 (2017). [https://doi.org/10.1007/s11069-017-2890-7](https://doi.org/10.1007/s11069-017-2890-7)

### Conference and workshop abstracts about this project ###

* Vigh, J. L., D. J. Smith, D. T. Hahn, J. Lin, A. Bol, D. O. Prevatt, D. B. Roueche, J. M. Collins, B. R. Ellingwood, G. Nain, J. E. Rovins, K. Emanuel, T. Ross-Lazarov, P. Mozumder, S. F. Pilkington, S. J. Weaver, G. Wong-Parodi, L. Myers, A. A. Merdjanoff, P. A. Kucera, C. Wang, T. Kloetzke, S. Joslyn, E. A. Holland, B. Brown, Y. P. Sheng, F. Tormos-Aponte, C. M. Appendini Albrechtsen, R. G. Goldhammer, H. Greatrex, M. Moulton, J. M. Done, E. A. Hendricks, C. M. Rozoff, J. J. Alland, M. Ge, C. Arthur, 2021: Updates on the Hurricane Risk Calculator: App capabilities, risk messaging, and pilot testing. Extended Abstract, 34th Conference on Hurricanes and Tropical Meteorology, Session 9B Interdisciplinary research to improve the hurricane forecasting-warning-response system: Past, current, and future foci, virtual conference, Amer. Meteor. Soc., Paper 9B.8. 
  * [Extended Abstract, pdf](https://staff.ral.ucar.edu/jvigh/documents/20210616_vighEA_34hurr_extended_abstract_hurricane_risk_calculator_FINAL2.pdf)
  * [Recorded homework presentation given 12 May 2021](https://staff.ral.ucar.edu/jvigh/documents/20210503_vighEA_34hurr_hurricane_risk_calculator_homework_recording.mp4)
  * [Presentation slides, pdf](https://staff.ral.ucar.edu/jvigh/documents/20210503_vighEA_34hurr_hurricane_risk_calculator_presentation.pdf)

* Vigh, J.L., D.J. Smith, B.R. Ellingwood, J. Lin, D.O. Prevatt, D. Roueche, B.G. Brown, D.T. Hahn, J.M. Collins, J.M. Done, G. Wong-Parodi, P.A. Kucera, C. Wang, J.J. Alland, T. Kloetzke, C.M. Rozoff, E.A. Hendricks, A.A. Merdjanoff, C. Arthur, M. Ge, Y. Peter Sheng, K. Emanuel, S.J. Weaver, J. Rovins, P. Mozumder, S. Joslyn, A. Bol, and T. Ross-Lazarov, 2020: The Hurricane Risk Calculator: Working toward Enhancing Our Nation's Readiness, Responsiveness, and Resilience to Hurricanes through Probabilistic Risk Frameworks for Evacuation Decision Support. Extended Abstract, Eighth Symposium on Building a Weather-Ready Nation: Enhancing Our Nation's Readiness, Responsiveness, and Resilience to High Impact Weather Events, Session 5 Hurricane Studies and Other Tropical Programmatic Achievements, Boston, MA, Amer. Meteor. Soc., Paper 5.5. 
  * [Extended Abstract, pdf](https://ral.ucar.edu/staff/jvigh/documents/vighEA2020_extended_abstract.pdf)
  * [Recorded presentation given 15 January 2020](https://ams.confex.com/ams/2020Annual/recordingredirect.cgi/oid/Recording516716/paper370408_1.mp4) 
  * [Presentation slides, pdf](https://ral.ucar.edu/staff/jvigh/documents/20200115_vigh_AMS100_hurricane_risk_calculator_presentation.pdf)

* Vigh, J. L., C. Arthur, J. Done, M. Ge, C. Wang, T. Kloetzke, C. M. Rozoff, B. Brown, B. Ellingwood: 2018: The Hurricane Risk Calculator: Translating Potential Wind Impacts for Coastal and Inland Residents. Extended Abstract (pdf file), 33rd Conf. on Hurricanes and Tropical Meteorology, Poster Session 21: Hazard Communication, Ponte Vedra Beach, FL, Amer. Meteor. Soc., Poster 203, [https://doi.org/10.13140/RG.2.2.33416.72965](https://doi.org/10.13140/RG.2.2.33416.72965). 
  * [pdf of poster presented 19 April 2018](https://staff.ral.ucar.edu/jvigh/documents/20180506_vighEA_33hurr_poster_hurricane_risk_calculator_36x56_FINAL3.pdf).

[Next: Our Team](team.html)

