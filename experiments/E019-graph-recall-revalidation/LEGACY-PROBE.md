# E019 supplemental probe preregistration

The main E019 fixture gives E009 B/C no graph path to its required note pages because both E009 arms only target entity pages. This supplemental probe was designed after viewing the main results and before running these new cases. It tests when the E009 mechanisms can recover an eligible entity page. The main experiment's conclusion and rules remain fixed.

Freeze 60 adapted synthetic tasks, six in each of the ten domains. Each needs one operational note and one operational fact on an entity page. There are 20 tasks each with a named subject and a sourced entity edge, a named subject and the same edge without a source, and a generic query with a sourced edge. The entity graph source gate, dense and keyword global search, raw score scale, weak seed floor, and E009 B/C replay rules remain as registered for the main suite. Report how often the intended owner is actually selected as an E009 seed and how often the required entity was outside A's first ten.

Report required entity hits and all-required-page hits at equal reading depth six and at the original native cutoffs (A and C at ten, B up to fifteen). Score the same evidence and wrong-page rubric with two separate blinded GPT-6.2 Sol runs per arm at depth six. Report paired repeat noise with 10,000 domain cluster draws using seed 190057. This is a descriptive probe of opportunity and mechanisms without a separate success threshold. It cannot supply an independent replication across new domains because it adapts the same fictional domains.

[Probe implementation and fixture hash](legacy_probe.py) · [Main preregistration](PREREGISTRATION.md)
