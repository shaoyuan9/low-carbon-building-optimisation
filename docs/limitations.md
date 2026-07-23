## Version 1 Limitations

Version 1 is designed as a base-case model and proof of concept. It provides a working techno-economic comparison of low-carbon electricity strategies, but it intentionally simplifies several real-world factors.

First, the model uses annual electricity demand rather than hourly load data. As a result, it does not yet capture time-of-day mismatch between solar generation and building electricity demand. This means that solar self-consumption is simplified, and the model does not yet evaluate hourly grid import, solar export, or curtailment.

Second, Version 1 uses one representative commercial rooftop PV technology. It does not yet compare different PV technologies such as standard mono PV, high-efficiency PV, or premium/future PV. Technology-specific comparison is reserved for later model extensions.

Third, the model does not include battery energy storage. Therefore, it cannot yet evaluate how storage affects solar self-consumption, peak demand reduction, curtailment, grid import, or investment economics.

Fourth, the renewable electricity purchase option is represented as a simple premium cost used for emissions accounting. The model does not yet distinguish between different renewable procurement mechanisms, contract structures, certificates, power purchase agreements, or market-based accounting rules.

Fifth, Version 1 does not include electricity price uncertainty, solar generation uncertainty, demand uncertainty, or stochastic scenario analysis. All assumptions are deterministic base-case values.

Sixth, policy and market mechanisms are only represented in a limited way. Version 1 includes the emissions reduction target and basic rooftop area constraint, but does not yet model carbon tax scenarios, solar aggregator models, merchant price exposure, fixed-price contracts, intermittency pricing mechanisms, or export rules in detail.

Seventh, the optimisation logic is still simple. The model compares predefined strategies rather than solving a full optimisation problem across PV size, battery size, renewable purchase amount, contract type, and technology choice. Full optimisation will be introduced in a later version.

Finally, the model requires further validation against external benchmarks such as published Singapore solar yield estimates, official grid emissions factors, market cost assumptions, or results from solar modelling tools. Version 1 should therefore be interpreted as a structured baseline model rather than a final investment-grade model.

These limitations are intentional. Version 1 establishes the modelling architecture, cost-emissions logic, results pipeline, and visualisation workflow. Later versions will progressively improve the model by adding hourly physical realism, PV + ESS simulation, optimisation, sensitivity analysis, policy scenario comparison, and stakeholder-specific recommendations.
