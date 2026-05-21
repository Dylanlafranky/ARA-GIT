window.ARA_GEOMETRY_STATE_TRANSITION = {
  "date": "2026-05-21",
  "method": "strict-causal ARA geometry state-transition ENSO test",
  "leakage_guard": "At origin t, transition training uses only s+h<t and decoder training uses only a<t.",
  "oracle_note": "oracle_actual_future_geometry_decoder uses the true future geometry and is diagnostic only, not a forecast.",
  "system": "ENSO",
  "target": "NINO3.4 anomaly",
  "feeders": [
    "SOI",
    "PDO"
  ],
  "base": 2.0,
  "home_period_months": 47.0,
  "rungs_k": [
    3,
    4,
    5,
    6,
    7
  ],
  "horizons_months": [
    1,
    3,
    6,
    12,
    24,
    60
  ],
  "ridge_alpha": 5.0,
  "min_train_examples": 96,
  "origin_stride_months": 3,
  "sample": {
    "start": "1951-01-01",
    "end": "2025-12-01",
    "n": 900,
    "test_start_origin": "2006-09-01",
    "test_last_origin_longest_horizon": "2020-12-01"
  },
  "models": {
    "event_ordered_cascade_decoder": "Deterministic small-to-large event-ordered cascade, then causal geometry decoder.",
    "state_transition_decoder": "Predict full future geometry state from current geometry, then decode value.",
    "state_transition_decoder_current": "Same, with observed current subsystem values included in the transition input.",
    "phi_flow_decoder": "Deterministic phi-decayed geometry flow, then causal geometry decoder.",
    "direct_value_geometry_ridge": "Control: direct current-geometry to future-value delta regression.",
    "lag_ridge": "Control: causal NINO lags and slopes to future-value delta.",
    "oracle_actual_future_geometry_decoder": "Diagnostic only: causal decoder applied to actual future geometry."
  },
  "scores": {
    "event_ordered_cascade_decoder": {
      "1": {
        "n": 77,
        "mae": 0.39954524491690147,
        "rmse": 0.5015383057744882,
        "corr": 0.8300016582072282,
        "direction": 0.4155844155844156,
        "persistence_mae": 0.2149350649350649,
        "mae_lift_vs_persistence": -0.18461017998183657,
        "r2_vs_persistence": -2.744829325854892,
        "pred_delta_std": 0.4158881365195097,
        "truth_delta_std": 0.2590805908826503
      },
      "3": {
        "n": 77,
        "mae": 0.6828469749185121,
        "rmse": 0.8374903956098005,
        "corr": 0.5734273904674223,
        "direction": 0.5194805194805194,
        "persistence_mae": 0.49103896103896105,
        "mae_lift_vs_persistence": -0.19180801387955104,
        "r2_vs_persistence": -0.9205167127486775,
        "pred_delta_std": 0.682197516309445,
        "truth_delta_std": 0.6041533595330312
      },
      "6": {
        "n": 76,
        "mae": 0.8874911586071237,
        "rmse": 1.0998769509817545,
        "corr": 0.3417156734318397,
        "direction": 0.6052631578947368,
        "persistence_mae": 0.7817105263157895,
        "mae_lift_vs_persistence": -0.10578063229133416,
        "r2_vs_persistence": -0.2656179989630236,
        "pred_delta_std": 1.0271768230652907,
        "truth_delta_std": 0.9771131213626487
      },
      "12": {
        "n": 74,
        "mae": 1.1045801563663091,
        "rmse": 1.4101631225797764,
        "corr": 0.024129924153590724,
        "direction": 0.6351351351351351,
        "persistence_mae": 1.005135135135135,
        "mae_lift_vs_persistence": -0.09944502123117416,
        "r2_vs_persistence": -0.182198447142641,
        "pred_delta_std": 1.1538023423275625,
        "truth_delta_std": 1.2966303184080832
      },
      "24": {
        "n": 70,
        "mae": 1.172532134534512,
        "rmse": 1.3859540354846214,
        "corr": 0.14497349276147042,
        "direction": 0.7,
        "persistence_mae": 1.1871428571428573,
        "mae_lift_vs_persistence": 0.014610722608345172,
        "r2_vs_persistence": 0.07494381866277366,
        "pred_delta_std": 1.4601200687533975,
        "truth_delta_std": 1.44045525683333
      },
      "60": {
        "n": 58,
        "mae": 1.1452227864189384,
        "rmse": 1.428142476836954,
        "corr": -0.002130856268945531,
        "direction": 0.5172413793103449,
        "persistence_mae": 0.8901724137931035,
        "mae_lift_vs_persistence": -0.25505037262583485,
        "r2_vs_persistence": -0.24143299440831112,
        "pred_delta_std": 1.2087873866147347,
        "truth_delta_std": 1.279847096712392
      }
    },
    "phi_flow_decoder": {
      "1": {
        "n": 77,
        "mae": 0.39886681226886966,
        "rmse": 0.5027806132386874,
        "corr": 0.8299070666159086,
        "direction": 0.4155844155844156,
        "persistence_mae": 0.2149350649350649,
        "mae_lift_vs_persistence": -0.18393174733380477,
        "r2_vs_persistence": -2.763404143142561,
        "pred_delta_std": 0.4169489388646186,
        "truth_delta_std": 0.2590805908826503
      },
      "3": {
        "n": 77,
        "mae": 0.6866874601858594,
        "rmse": 0.8426204199918566,
        "corr": 0.5728404825510841,
        "direction": 0.5064935064935064,
        "persistence_mae": 0.49103896103896105,
        "mae_lift_vs_persistence": -0.1956484991468983,
        "r2_vs_persistence": -0.9441169178452644,
        "pred_delta_std": 0.6855243209637981,
        "truth_delta_std": 0.6041533595330312
      },
      "6": {
        "n": 76,
        "mae": 0.8896173468430935,
        "rmse": 1.1102381391190481,
        "corr": 0.3343727343743237,
        "direction": 0.6578947368421053,
        "persistence_mae": 0.7817105263157895,
        "mae_lift_vs_persistence": -0.10790682052730394,
        "r2_vs_persistence": -0.2895753551522431,
        "pred_delta_std": 1.0246719183763477,
        "truth_delta_std": 0.9771131213626487
      },
      "12": {
        "n": 74,
        "mae": 1.1029787973726155,
        "rmse": 1.437745197812135,
        "corr": 0.02080942666481199,
        "direction": 0.6486486486486487,
        "persistence_mae": 1.005135135135135,
        "mae_lift_vs_persistence": -0.09784366223748053,
        "r2_vs_persistence": -0.22889712891612435,
        "pred_delta_std": 1.1603661044624622,
        "truth_delta_std": 1.2966303184080832
      },
      "24": {
        "n": 70,
        "mae": 1.1787910382161972,
        "rmse": 1.4055175664026314,
        "corr": 0.1363264642088023,
        "direction": 0.7,
        "persistence_mae": 1.1871428571428573,
        "mae_lift_vs_persistence": 0.008351818926660037,
        "r2_vs_persistence": 0.04864411167584948,
        "pred_delta_std": 1.4651741412808064,
        "truth_delta_std": 1.44045525683333
      },
      "60": {
        "n": 58,
        "mae": 1.300009198815236,
        "rmse": 1.5909103497593664,
        "corr": -0.06623605441755792,
        "direction": 0.5344827586206896,
        "persistence_mae": 0.8901724137931035,
        "mae_lift_vs_persistence": -0.4098367850221325,
        "r2_vs_persistence": -0.5405351970072991,
        "pred_delta_std": 1.3548408457589438,
        "truth_delta_std": 1.279847096712392
      }
    },
    "state_transition_decoder": {
      "1": {
        "n": 77,
        "mae": 0.41066449205248085,
        "rmse": 0.4947567523859977,
        "corr": 0.8274746393867893,
        "direction": 0.42857142857142855,
        "persistence_mae": 0.2149350649350649,
        "mae_lift_vs_persistence": -0.19572942711741595,
        "r2_vs_persistence": -2.6442425301963497,
        "pred_delta_std": 0.401334737911239,
        "truth_delta_std": 0.2590805908826503,
        "mean_abs_state_feature_error": 0.12734576456575597
      },
      "3": {
        "n": 77,
        "mae": 0.6163950416449947,
        "rmse": 0.7723053508180473,
        "corr": 0.5530488486266679,
        "direction": 0.6103896103896104,
        "persistence_mae": 0.49103896103896105,
        "mae_lift_vs_persistence": -0.12535608060603365,
        "r2_vs_persistence": -0.6331892325502346,
        "pred_delta_std": 0.6957427170903802,
        "truth_delta_std": 0.6041533595330312,
        "mean_abs_state_feature_error": 0.20482925019106107
      },
      "6": {
        "n": 76,
        "mae": 0.7886162426511136,
        "rmse": 0.9715500168195821,
        "corr": 0.3221342932385934,
        "direction": 0.5921052631578947,
        "persistence_mae": 0.7817105263157895,
        "mae_lift_vs_persistence": -0.006905716335324108,
        "r2_vs_persistence": 0.012482574946528269,
        "pred_delta_std": 0.8107970012549112,
        "truth_delta_std": 0.9771131213626487,
        "mean_abs_state_feature_error": 0.26996565793386346
      },
      "12": {
        "n": 74,
        "mae": 1.1009761966307856,
        "rmse": 1.3567124596906088,
        "corr": -0.25050414776337393,
        "direction": 0.581081081081081,
        "persistence_mae": 1.005135135135135,
        "mae_lift_vs_persistence": -0.09584106149565064,
        "r2_vs_persistence": -0.09427708567143855,
        "pred_delta_std": 1.2682132525487657,
        "truth_delta_std": 1.2966303184080832,
        "mean_abs_state_feature_error": 0.340120999188294
      },
      "24": {
        "n": 70,
        "mae": 0.9270061699240565,
        "rmse": 1.1838757577148842,
        "corr": 0.03926200359612943,
        "direction": 0.7571428571428571,
        "persistence_mae": 1.1871428571428573,
        "mae_lift_vs_persistence": 0.2601366872188008,
        "r2_vs_persistence": 0.32503273603824745,
        "pred_delta_std": 0.9638667440934839,
        "truth_delta_std": 1.44045525683333,
        "mean_abs_state_feature_error": 0.4052483876158092
      },
      "60": {
        "n": 58,
        "mae": 1.1560787364348195,
        "rmse": 1.4038159946479003,
        "corr": -0.03620031164599335,
        "direction": 0.6551724137931034,
        "persistence_mae": 0.8901724137931035,
        "mae_lift_vs_persistence": -0.265906322641716,
        "r2_vs_persistence": -0.19950091474453147,
        "pred_delta_std": 1.034966972439001,
        "truth_delta_std": 1.279847096712392,
        "mean_abs_state_feature_error": 0.432194562820479
      }
    },
    "state_transition_decoder_current": {
      "1": {
        "n": 77,
        "mae": 0.3298324326095133,
        "rmse": 0.39919704820902424,
        "corr": 0.8894596630181336,
        "direction": 0.45454545454545453,
        "persistence_mae": 0.2149350649350649,
        "mae_lift_vs_persistence": -0.11489736767444839,
        "r2_vs_persistence": -1.3724575731342106,
        "pred_delta_std": 0.29863839369273043,
        "truth_delta_std": 0.2590805908826503,
        "mean_abs_state_feature_error": 0.1250423301306658
      },
      "3": {
        "n": 77,
        "mae": 0.571867640343585,
        "rmse": 0.7348804166212047,
        "corr": 0.6024972645946451,
        "direction": 0.6233766233766234,
        "persistence_mae": 0.49103896103896105,
        "mae_lift_vs_persistence": -0.0808286793046239,
        "r2_vs_persistence": -0.478739823778884,
        "pred_delta_std": 0.6455075489237962,
        "truth_delta_std": 0.6041533595330312,
        "mean_abs_state_feature_error": 0.20216782607932332
      },
      "6": {
        "n": 76,
        "mae": 0.804937136406286,
        "rmse": 0.9997607314276724,
        "corr": 0.2859488596339902,
        "direction": 0.6052631578947368,
        "persistence_mae": 0.7817105263157895,
        "mae_lift_vs_persistence": -0.023226610090496425,
        "r2_vs_persistence": -0.045698751415664374,
        "pred_delta_std": 0.8517720881455586,
        "truth_delta_std": 0.9771131213626487,
        "mean_abs_state_feature_error": 0.2664315400898083
      },
      "12": {
        "n": 74,
        "mae": 1.111281298845164,
        "rmse": 1.3710059830593984,
        "corr": -0.24087023398386623,
        "direction": 0.6216216216216216,
        "persistence_mae": 1.005135135135135,
        "mae_lift_vs_persistence": -0.10614616371002894,
        "r2_vs_persistence": -0.11745586251683382,
        "pred_delta_std": 1.3226805504998986,
        "truth_delta_std": 1.2966303184080832,
        "mean_abs_state_feature_error": 0.33689620358643096
      },
      "24": {
        "n": 70,
        "mae": 0.8914556421563201,
        "rmse": 1.1343708870269558,
        "corr": 0.06000640326916171,
        "direction": 0.7857142857142857,
        "persistence_mae": 1.1871428571428573,
        "mae_lift_vs_persistence": 0.29568721498653716,
        "r2_vs_persistence": 0.380301280228555,
        "pred_delta_std": 0.9624850051706937,
        "truth_delta_std": 1.44045525683333,
        "mean_abs_state_feature_error": 0.4043614064639673
      },
      "60": {
        "n": 58,
        "mae": 1.1318198237342472,
        "rmse": 1.3772151886356871,
        "corr": -0.017920542041052076,
        "direction": 0.6206896551724138,
        "persistence_mae": 0.8901724137931035,
        "mae_lift_vs_persistence": -0.24164740994114364,
        "r2_vs_persistence": -0.15447310053103336,
        "pred_delta_std": 1.0242123381759964,
        "truth_delta_std": 1.279847096712392,
        "mean_abs_state_feature_error": 0.4293756308856313
      }
    },
    "direct_value_geometry_ridge": {
      "1": {
        "n": 77,
        "mae": 0.2551078800147956,
        "rmse": 0.33153121970736643,
        "corr": 0.9312856856745914,
        "direction": 0.5584415584415584,
        "persistence_mae": 0.2149350649350649,
        "mae_lift_vs_persistence": -0.04017281507973072,
        "r2_vs_persistence": -0.6363367147445649,
        "pred_delta_std": 0.25381289158275866,
        "truth_delta_std": 0.2590805908826503
      },
      "3": {
        "n": 77,
        "mae": 0.5943282971689404,
        "rmse": 0.7647642761828631,
        "corr": 0.6885327438029913,
        "direction": 0.6363636363636364,
        "persistence_mae": 0.49103896103896105,
        "mae_lift_vs_persistence": -0.10328933612997937,
        "r2_vs_persistence": -0.6014508200484117,
        "pred_delta_std": 0.6165959804579136,
        "truth_delta_std": 0.6041533595330312
      },
      "6": {
        "n": 76,
        "mae": 0.8774363947946856,
        "rmse": 1.121348466973872,
        "corr": 0.41371340304437676,
        "direction": 0.631578947368421,
        "persistence_mae": 0.7817105263157895,
        "mae_lift_vs_persistence": -0.09572586847889608,
        "r2_vs_persistence": -0.31551446457629106,
        "pred_delta_std": 0.8010338852758238,
        "truth_delta_std": 0.9771131213626487
      },
      "12": {
        "n": 74,
        "mae": 1.3498086163030927,
        "rmse": 1.6791731263769256,
        "corr": -0.17823443060660177,
        "direction": 0.4189189189189189,
        "persistence_mae": 1.005135135135135,
        "mae_lift_vs_persistence": -0.3446734811679577,
        "r2_vs_persistence": -0.6762648121833721,
        "pred_delta_std": 1.2435292081785057,
        "truth_delta_std": 1.2966303184080832
      },
      "24": {
        "n": 70,
        "mae": 1.388976016500387,
        "rmse": 1.905791461656532,
        "corr": -0.06329866220849385,
        "direction": 0.6,
        "persistence_mae": 1.1871428571428573,
        "mae_lift_vs_persistence": -0.20183315935752977,
        "r2_vs_persistence": -0.749126455737817,
        "pred_delta_std": 1.3280086485185685,
        "truth_delta_std": 1.44045525683333
      },
      "60": {
        "n": 58,
        "mae": 1.3962713526444246,
        "rmse": 1.8223375757713915,
        "corr": 0.004499431834883541,
        "direction": 0.6206896551724138,
        "persistence_mae": 0.8901724137931035,
        "mae_lift_vs_persistence": -0.5060989388513211,
        "r2_vs_persistence": -1.0213330233042512,
        "pred_delta_std": 1.4739243498704344,
        "truth_delta_std": 1.279847096712392
      }
    },
    "lag_ridge": {
      "1": {
        "n": 77,
        "mae": 0.17581966493194348,
        "rmse": 0.22654927032770622,
        "corr": 0.965392771785201,
        "direction": 0.6753246753246753,
        "persistence_mae": 0.2149350649350649,
        "mae_lift_vs_persistence": 0.039115400003121414,
        "r2_vs_persistence": 0.23590185123581509,
        "pred_delta_std": 0.13740755855710546,
        "truth_delta_std": 0.2590805908826503
      },
      "3": {
        "n": 77,
        "mae": 0.3806773805853117,
        "rmse": 0.501413569405729,
        "corr": 0.815619623470051,
        "direction": 0.7142857142857143,
        "persistence_mae": 0.49103896103896105,
        "mae_lift_vs_persistence": 0.11036158045364935,
        "r2_vs_persistence": 0.3115845858098394,
        "pred_delta_std": 0.35373095619010264,
        "truth_delta_std": 0.6041533595330312
      },
      "6": {
        "n": 76,
        "mae": 0.6142566289810578,
        "rmse": 0.7723928776434155,
        "corr": 0.45054761608816696,
        "direction": 0.6842105263157895,
        "persistence_mae": 0.7817105263157895,
        "mae_lift_vs_persistence": 0.1674538973347317,
        "r2_vs_persistence": 0.37584714525232,
        "pred_delta_std": 0.6369921835028125,
        "truth_delta_std": 0.9771131213626487
      },
      "12": {
        "n": 74,
        "mae": 0.6739400312357423,
        "rmse": 0.874675865531928,
        "corr": 0.13884078483793388,
        "direction": 0.8108108108108109,
        "persistence_mae": 1.005135135135135,
        "mae_lift_vs_persistence": 0.33119510389939266,
        "r2_vs_persistence": 0.5451732857434297,
        "pred_delta_std": 0.9837346001160541,
        "truth_delta_std": 1.2966303184080832
      },
      "24": {
        "n": 70,
        "mae": 0.6231792691946321,
        "rmse": 0.8389927705445562,
        "corr": 0.2340266412460315,
        "direction": 0.7857142857142857,
        "persistence_mae": 1.1871428571428573,
        "mae_lift_vs_persistence": 0.5639635879482252,
        "r2_vs_persistence": 0.6610099960522495,
        "pred_delta_std": 1.1272994674708157,
        "truth_delta_std": 1.44045525683333
      },
      "60": {
        "n": 58,
        "mae": 0.6724945284475887,
        "rmse": 0.9051381740637549,
        "corr": -0.44845777231964934,
        "direction": 0.7413793103448276,
        "persistence_mae": 0.8901724137931035,
        "mae_lift_vs_persistence": 0.2176778853455148,
        "r2_vs_persistence": 0.5013337521888093,
        "pred_delta_std": 0.9000837830507458,
        "truth_delta_std": 1.279847096712392
      }
    },
    "oracle_actual_future_geometry_decoder": {
      "1": {
        "n": 77,
        "mae": 0.3396152981259831,
        "rmse": 0.4218206839878421,
        "corr": 0.8767244200727903,
        "direction": 0.5974025974025974,
        "persistence_mae": 0.2149350649350649,
        "mae_lift_vs_persistence": -0.12468023319091823,
        "r2_vs_persistence": -1.6489853419071108,
        "pred_delta_std": 0.3661696465411544,
        "truth_delta_std": 0.2590805908826503
      },
      "3": {
        "n": 77,
        "mae": 0.4139405190477659,
        "rmse": 0.5147276969382899,
        "corr": 0.812786288396937,
        "direction": 0.7272727272727273,
        "persistence_mae": 0.49103896103896105,
        "mae_lift_vs_persistence": 0.07709844199119514,
        "r2_vs_persistence": 0.27453995918916785,
        "pred_delta_std": 0.6038230032036529,
        "truth_delta_std": 0.6041533595330312
      },
      "6": {
        "n": 76,
        "mae": 0.49079088395537135,
        "rmse": 0.5921939663898206,
        "corr": 0.7449396736940733,
        "direction": 0.75,
        "persistence_mae": 0.7817105263157895,
        "mae_lift_vs_persistence": 0.2909196423604182,
        "r2_vs_persistence": 0.6331044901090581,
        "pred_delta_std": 0.9153833320669735,
        "truth_delta_std": 0.9771131213626487
      },
      "12": {
        "n": 74,
        "mae": 0.560593979360564,
        "rmse": 0.7122364475287034,
        "corr": 0.6256367060600275,
        "direction": 0.7837837837837838,
        "persistence_mae": 1.005135135135135,
        "mae_lift_vs_persistence": 0.444541155774571,
        "r2_vs_persistence": 0.6984217153733238,
        "pred_delta_std": 1.1204537853753953,
        "truth_delta_std": 1.2966303184080832
      },
      "24": {
        "n": 70,
        "mae": 0.5458638485343881,
        "rmse": 0.7190781598188482,
        "corr": 0.624611272397892,
        "direction": 0.7571428571428571,
        "persistence_mae": 1.1871428571428573,
        "mae_lift_vs_persistence": 0.6412790086084692,
        "r2_vs_persistence": 0.7509866381914505,
        "pred_delta_std": 1.2821111355882968,
        "truth_delta_std": 1.44045525683333
      },
      "60": {
        "n": 58,
        "mae": 0.5332591412341415,
        "rmse": 0.6554036143570073,
        "corr": 0.6654924626529779,
        "direction": 0.7758620689655172,
        "persistence_mae": 0.8901724137931035,
        "mae_lift_vs_persistence": 0.356913272558962,
        "r2_vs_persistence": 0.7385444440995521,
        "pred_delta_std": 1.3657102633393678,
        "truth_delta_std": 1.279847096712392
      }
    }
  },
  "winners": {
    "1": "lag_ridge",
    "3": "lag_ridge",
    "6": "lag_ridge",
    "12": "lag_ridge",
    "24": "lag_ridge",
    "60": "lag_ridge"
  },
  "points": {
    "event_ordered_cascade_decoder": {
      "1": [
        {
          "origin": "2006-09-01",
          "date": "2006-10-01",
          "pred": 0.4831582321935518,
          "actual": 0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-01-01",
          "pred": 1.220657831183102,
          "actual": 0.59,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-04-01",
          "pred": 0.3895556629874809,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-07-01",
          "pred": -0.11888953937837385,
          "actual": -0.37,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-10-01",
          "pred": -0.3979573736390348,
          "actual": -1.41,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-01-01",
          "pred": -0.605085435022473,
          "actual": -1.79,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-04-01",
          "pred": -0.9842350076832362,
          "actual": -0.89,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-07-01",
          "pred": -0.9260769795078886,
          "actual": -0.04,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-10-01",
          "pred": -0.36633280034389604,
          "actual": -0.3,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-01-01",
          "pred": -0.010906559048962754,
          "actual": -1.0,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-04-01",
          "pred": -0.8116587481278409,
          "actual": -0.25,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-07-01",
          "pred": 0.65576969015573,
          "actual": 0.69,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-10-01",
          "pred": 1.1034599688490283,
          "actual": 0.96,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-01-01",
          "pred": 1.841267311258846,
          "actual": 1.43,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-04-01",
          "pred": 0.10930696406005311,
          "actual": 0.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-07-01",
          "pred": -0.5892606241790023,
          "actual": -0.89,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-10-01",
          "pred": -1.3469256878914666,
          "actual": -1.65,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-01-01",
          "pred": -1.1030866201372878,
          "actual": -1.7,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-04-01",
          "pred": -1.2592628185820216,
          "actual": -0.74,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-07-01",
          "pred": -0.9443064595768726,
          "actual": -0.23,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-10-01",
          "pred": -0.5753399856145746,
          "actual": -0.93,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-01-01",
          "pred": -1.3044556199418562,
          "actual": -0.93,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-04-01",
          "pred": -0.8700080935825643,
          "actual": -0.29,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-07-01",
          "pred": 0.2851560815331085,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-10-01",
          "pred": 0.8505594128798188,
          "actual": 0.23,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-01-01",
          "pred": -0.044250986168977255,
          "actual": -0.42,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-04-01",
          "pred": -0.7423179220914653,
          "actual": -0.08,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-07-01",
          "pred": -0.5639802764469227,
          "actual": -0.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-10-01",
          "pred": -0.2677908471768755,
          "actual": -0.24,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-01-01",
          "pred": -0.2780670021631735,
          "actual": -0.42,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-04-01",
          "pred": -0.19539316231429724,
          "actual": 0.28,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-07-01",
          "pred": 0.9525357603607904,
          "actual": 0.13,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-10-01",
          "pred": 0.585721390220659,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-01-01",
          "pred": 1.0877354076180479,
          "actual": 0.59,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-04-01",
          "pred": 0.4707311226905237,
          "actual": 0.9,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-07-01",
          "pred": 0.611019630542639,
          "actual": 1.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-10-01",
          "pred": 2.1941467388810163,
          "actual": 2.21,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-01-01",
          "pred": 2.504067674497761,
          "actual": 2.56,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-04-01",
          "pred": 1.898734969724942,
          "actual": 1.05,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-07-01",
          "pred": 0.3866087286175494,
          "actual": -0.25,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-10-01",
          "pred": -1.285802673476723,
          "actual": -0.75,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-01-01",
          "pred": -0.19553904926219715,
          "actual": -0.34,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-04-01",
          "pred": 0.03838730814726993,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-07-01",
          "pred": -0.020862282760640873,
          "actual": 0.22,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-10-01",
          "pred": -0.5140122904066928,
          "actual": -0.52,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-01-01",
          "pred": -0.663253551848105,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-04-01",
          "pred": 0.20851800892883507,
          "actual": -0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-07-01",
          "pred": 0.23364267462131305,
          "actual": 0.27,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-10-01",
          "pred": 0.24552446004449663,
          "actual": 0.84,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-01-01",
          "pred": 1.0481037448372454,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-04-01",
          "pred": -0.17761658523345433,
          "actual": 0.67,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-07-01",
          "pred": 0.3775208964719815,
          "actual": 0.41,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-10-01",
          "pred": 0.18488572843123074,
          "actual": 0.55,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-01-01",
          "pred": 0.5548984167664138,
          "actual": 0.64,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-04-01",
          "pred": 0.5175166265159251,
          "actual": 0.49,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-07-01",
          "pred": -0.08605505801641176,
          "actual": -0.04,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-10-01",
          "pred": -0.5451179875788388,
          "actual": -1.19,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-01-01",
          "pred": -0.807792430959029,
          "actual": -1.04,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-04-01",
          "pred": -0.013697246972203512,
          "actual": -0.55,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-07-01",
          "pred": -0.3780430410913026,
          "actual": -0.2,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-10-01",
          "pred": -0.05904094673526541,
          "actual": -0.78,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-01-01",
          "pred": -0.4243430144061607,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-04-01",
          "pred": -0.6001330293795213,
          "actual": -0.9,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-07-01",
          "pred": -0.5034387442947509,
          "actual": -0.56,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-10-01",
          "pred": -0.5756675934221188,
          "actual": -0.99,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-01-01",
          "pred": -0.8059783921245255,
          "actual": -0.78,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-04-01",
          "pred": -0.5053998737479094,
          "actual": 0.24,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-07-01",
          "pred": 0.6587678546368462,
          "actual": 1.2,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-10-01",
          "pred": 1.299987826492451,
          "actual": 1.59,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-01-01",
          "pred": 1.7205952313813657,
          "actual": 1.71,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-04-01",
          "pred": 1.1692422871641468,
          "actual": 0.93,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-07-01",
          "pred": -0.02393288314810719,
          "actual": 0.2,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-10-01",
          "pred": -0.0789686437284325,
          "actual": -0.24,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-01-01",
          "pred": 0.595372720776372,
          "actual": -0.76,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-04-01",
          "pred": 0.43365355577591813,
          "actual": -0.08,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-07-01",
          "pred": 0.062388064535996046,
          "actual": -0.03,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-10-01",
          "pred": -0.8009932924135656,
          "actual": -0.5,
          "persistence": -0.3
        }
      ],
      "3": [
        {
          "origin": "2006-09-01",
          "date": "2006-12-01",
          "pred": 0.4141179934235665,
          "actual": 1.1,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-03-01",
          "pred": 1.4119414361477103,
          "actual": -0.15,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-06-01",
          "pred": 0.47232559316921285,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-09-01",
          "pred": 0.24335122981370613,
          "actual": -1.04,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-12-01",
          "pred": -0.2537118290670292,
          "actual": -1.61,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-03-01",
          "pred": 0.030500349127014017,
          "actual": -1.17,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-06-01",
          "pred": -0.9775863487058964,
          "actual": -0.44,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-09-01",
          "pred": -1.3860831165907128,
          "actual": -0.28,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-12-01",
          "pred": -0.0739201593038211,
          "actual": -0.9,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-03-01",
          "pred": -0.1096816141723927,
          "actual": -0.72,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-06-01",
          "pred": -1.18765526578239,
          "actual": 0.49,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-09-01",
          "pred": 0.7522741024374937,
          "actual": 0.68,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-12-01",
          "pred": 1.8106728870885602,
          "actual": 1.81,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-03-01",
          "pred": 0.6116612473688806,
          "actual": 1.07,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-06-01",
          "pred": -0.2896225552430315,
          "actual": -0.62,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-09-01",
          "pred": -0.0669692303616217,
          "actual": -1.56,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-12-01",
          "pred": -1.1986619520173807,
          "actual": -1.63,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-03-01",
          "pred": -0.6260575776342521,
          "actual": -0.98,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-06-01",
          "pred": -0.9595738957972663,
          "actual": -0.25,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-09-01",
          "pred": -1.5814488896992511,
          "actual": -0.76,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-12-01",
          "pred": -0.8377516006985797,
          "actual": -1.05,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-03-01",
          "pred": -1.2969070043266393,
          "actual": -0.48,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-06-01",
          "pred": -0.7932372294517762,
          "actual": 0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-09-01",
          "pred": 1.1261139921669974,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-12-01",
          "pred": 0.8800706942358538,
          "actual": -0.13,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-03-01",
          "pred": -0.5777046169890296,
          "actual": -0.14,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-06-01",
          "pred": -1.2441344956683031,
          "actual": -0.33,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-09-01",
          "pred": -0.7596767719520434,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-12-01",
          "pred": -0.3077159628773442,
          "actual": -0.09,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-03-01",
          "pred": -0.151977785371132,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-06-01",
          "pred": 0.140024807367836,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-09-01",
          "pred": 1.0807579330627277,
          "actual": 0.37,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-12-01",
          "pred": 0.7992782099080453,
          "actual": 0.77,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-03-01",
          "pred": 0.9883065091469023,
          "actual": 0.48,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-06-01",
          "pred": 0.8063459185194072,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-09-01",
          "pred": 0.1584764339925855,
          "actual": 2.01,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-12-01",
          "pred": 2.064739802925448,
          "actual": 2.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-03-01",
          "pred": 2.5783959898168907,
          "actual": 1.6,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-06-01",
          "pred": 1.7334289834053098,
          "actual": 0.06,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-09-01",
          "pred": 0.7987462964090216,
          "actual": -0.46,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-12-01",
          "pred": -1.5626128453114967,
          "actual": -0.51,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-03-01",
          "pred": 0.13453819408390416,
          "actual": -0.09,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-06-01",
          "pred": -0.26190008601985765,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-09-01",
          "pred": -0.35952073205763224,
          "actual": -0.56,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-12-01",
          "pred": -0.7250183536509877,
          "actual": -0.85,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-03-01",
          "pred": -1.0443803480011278,
          "actual": -0.73,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-06-01",
          "pred": 0.6746680232542502,
          "actual": 0.12,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-09-01",
          "pred": 0.4193085697170369,
          "actual": 0.3,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-12-01",
          "pred": 0.6518284800594016,
          "actual": 0.97,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-03-01",
          "pred": 0.2523273918989989,
          "actual": 0.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-06-01",
          "pred": -0.6865303390826907,
          "actual": 0.66,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-09-01",
          "pred": -0.3658649481283493,
          "actual": 0.11,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-12-01",
          "pred": 0.28144358313003554,
          "actual": 0.51,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-03-01",
          "pred": 0.3703976368964558,
          "actual": 0.36,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-06-01",
          "pred": 1.1162585115136174,
          "actual": -0.21,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-09-01",
          "pred": -0.026288098581420453,
          "actual": -0.66,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-12-01",
          "pred": -0.4195292239531939,
          "actual": -0.98,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-03-01",
          "pred": -0.9308733451234416,
          "actual": -0.72,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-06-01",
          "pred": -0.13931597029879167,
          "actual": -0.06,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-09-01",
          "pred": -0.8673977460838195,
          "actual": -0.5,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-12-01",
          "pred": 0.36345294368616415,
          "actual": -1.07,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-03-01",
          "pred": -0.3291949665049495,
          "actual": -0.84,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-06-01",
          "pred": -0.7029488695904444,
          "actual": -0.77,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-09-01",
          "pred": -0.420802010029854,
          "actual": -1.06,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-12-01",
          "pred": -0.8174412924135337,
          "actual": -0.86,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-03-01",
          "pred": -1.348746008840419,
          "actual": -0.13,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-06-01",
          "pred": -0.8263419090653601,
          "actual": 0.95,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-09-01",
          "pred": 0.31790569837735566,
          "actual": 1.65,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-12-01",
          "pred": 1.656165427019838,
          "actual": 1.81,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-03-01",
          "pred": 1.990535716057512,
          "actual": 1.1,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-06-01",
          "pred": 1.5749007299716762,
          "actual": 0.25,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-09-01",
          "pred": 0.43122612439520913,
          "actual": -0.11,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-12-01",
          "pred": 0.3140190069614409,
          "actual": -0.58,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-03-01",
          "pred": 1.256903904763763,
          "actual": 0.05,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-06-01",
          "pred": 0.46491810038541237,
          "actual": 0.01,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-09-01",
          "pred": -0.45456486817853026,
          "actual": -0.3,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-12-01",
          "pred": -0.7918524531213579,
          "actual": -0.49,
          "persistence": -0.3
        }
      ],
      "6": [
        {
          "origin": "2006-09-01",
          "date": "2007-03-01",
          "pred": 0.37656662979575867,
          "actual": -0.15,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-06-01",
          "pred": 0.5801299620035337,
          "actual": -0.16,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-09-01",
          "pred": 0.8800217785112077,
          "actual": -1.04,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-12-01",
          "pred": 0.7983330530690895,
          "actual": -1.61,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-03-01",
          "pred": 0.9183448706553013,
          "actual": -1.17,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-06-01",
          "pred": -0.3004702187467909,
          "actual": -0.44,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-09-01",
          "pred": -1.1493472350718836,
          "actual": -0.28,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-12-01",
          "pred": -1.5068710268641818,
          "actual": -0.9,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-03-01",
          "pred": -0.9387453471998429,
          "actual": -0.72,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-06-01",
          "pred": -0.9042748863434509,
          "actual": 0.49,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-09-01",
          "pred": 0.10276165046847127,
          "actual": 0.68,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-12-01",
          "pred": 1.7854629468782823,
          "actual": 1.81,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-03-01",
          "pred": 0.6699520755206552,
          "actual": 1.07,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-06-01",
          "pred": -1.1180090567376257,
          "actual": -0.62,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-09-01",
          "pred": -0.3670844101331253,
          "actual": -1.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-12-01",
          "pred": 0.29348488424939206,
          "actual": -1.63,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-03-01",
          "pred": -0.027587448602313016,
          "actual": -0.98,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-06-01",
          "pred": 0.6709407249996366,
          "actual": -0.25,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-09-01",
          "pred": -1.3433952880951798,
          "actual": -0.76,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-12-01",
          "pred": -1.7909746384799115,
          "actual": -1.05,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-03-01",
          "pred": -1.5632731239736104,
          "actual": -0.48,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-06-01",
          "pred": -1.1396807252326893,
          "actual": 0.14,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-09-01",
          "pred": 0.7937219997136344,
          "actual": 0.44,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-12-01",
          "pred": 1.7633603876324409,
          "actual": -0.13,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-03-01",
          "pred": 0.17418382822327683,
          "actual": -0.14,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-06-01",
          "pred": -1.267756568798002,
          "actual": -0.33,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-09-01",
          "pred": -1.171924413913973,
          "actual": -0.09,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-12-01",
          "pred": -0.39770078485954186,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-03-01",
          "pred": -0.16100657695483817,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-06-01",
          "pred": -0.4814614573420343,
          "actual": 0.48,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-09-01",
          "pred": 0.5090831145420083,
          "actual": 0.37,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-12-01",
          "pred": 1.4209288437267902,
          "actual": 0.77,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-03-01",
          "pred": 1.0629338609158194,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-06-01",
          "pred": 1.255432022407572,
          "actual": 1.28,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-09-01",
          "pred": 1.7341086144152253,
          "actual": 2.01,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-12-01",
          "pred": 0.85327634639414,
          "actual": 2.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-03-01",
          "pred": 2.1050413141669586,
          "actual": 1.6,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-06-01",
          "pred": 2.0198261645978084,
          "actual": 0.06,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-09-01",
          "pred": 0.904062307483905,
          "actual": -0.46,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-12-01",
          "pred": 0.6173905846587041,
          "actual": -0.51,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-03-01",
          "pred": -0.005870653227500263,
          "actual": -0.09,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-06-01",
          "pred": 1.2794706716634396,
          "actual": 0.22,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-09-01",
          "pred": -0.8147773176691446,
          "actual": -0.56,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-12-01",
          "pred": -1.1183565242161049,
          "actual": -0.85,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-03-01",
          "pred": -0.49725380404855196,
          "actual": -0.73,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-06-01",
          "pred": 0.08424849389955648,
          "actual": 0.12,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-09-01",
          "pred": 1.5031124192379894,
          "actual": 0.3,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-12-01",
          "pred": 0.6181982355168315,
          "actual": 0.97,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-03-01",
          "pred": -0.20653091225681855,
          "actual": 0.81,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-06-01",
          "pred": -0.8664737049691024,
          "actual": 0.66,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-09-01",
          "pred": -1.0279474537309448,
          "actual": 0.11,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-12-01",
          "pred": -0.37427513988959554,
          "actual": 0.51,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-03-01",
          "pred": 0.29818254855223836,
          "actual": 0.36,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-06-01",
          "pred": 0.6134351439227184,
          "actual": -0.21,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-09-01",
          "pred": 1.0517197769151228,
          "actual": -0.66,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-12-01",
          "pred": -0.24882801990065548,
          "actual": -0.98,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-03-01",
          "pred": -0.03293968200319128,
          "actual": -0.72,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-06-01",
          "pred": -0.4314780315311186,
          "actual": -0.06,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-09-01",
          "pred": -0.04728332019302879,
          "actual": -0.5,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-12-01",
          "pred": -0.7062779608519741,
          "actual": -1.07,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-03-01",
          "pred": -0.4630456061262979,
          "actual": -0.84,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-06-01",
          "pred": -0.44507905537765907,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-09-01",
          "pred": 0.1860013869246772,
          "actual": -1.06,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-12-01",
          "pred": -0.4176818731846645,
          "actual": -0.86,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-03-01",
          "pred": -0.8650574591823526,
          "actual": -0.13,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-06-01",
          "pred": -1.863462405674445,
          "actual": 0.95,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-09-01",
          "pred": -0.8274643979065948,
          "actual": 1.65,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-12-01",
          "pred": 0.5033381448970964,
          "actual": 1.81,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-03-01",
          "pred": 1.5235384539786527,
          "actual": 1.1,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-06-01",
          "pred": 1.630486551273649,
          "actual": 0.25,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-09-01",
          "pred": 1.9061791009510618,
          "actual": -0.11,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-12-01",
          "pred": 0.6596004131039434,
          "actual": -0.58,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-03-01",
          "pred": 1.5485395220829832,
          "actual": 0.05,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-06-01",
          "pred": 1.711740592974414,
          "actual": 0.01,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-09-01",
          "pred": -0.6245357178316329,
          "actual": -0.3,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-12-01",
          "pred": -1.0067326487886852,
          "actual": -0.49,
          "persistence": 0.01
        }
      ],
      "12": [
        {
          "origin": "2006-09-01",
          "date": "2007-09-01",
          "pred": 1.4488492773253057,
          "actual": -1.04,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-12-01",
          "pred": 2.0292137432819057,
          "actual": -1.61,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2008-03-01",
          "pred": 1.280084694816218,
          "actual": -1.17,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2008-06-01",
          "pred": -0.28325340620288736,
          "actual": -0.44,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-09-01",
          "pred": -0.6550591963197571,
          "actual": -0.28,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-12-01",
          "pred": -0.5678765041164524,
          "actual": -0.9,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2009-03-01",
          "pred": -0.7910106364494056,
          "actual": -0.72,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2009-06-01",
          "pred": -1.54451327921192,
          "actual": 0.49,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-09-01",
          "pred": -0.38640313976746954,
          "actual": 0.68,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-12-01",
          "pred": 1.3340789656921905,
          "actual": 1.81,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2010-03-01",
          "pred": -0.5223873898031803,
          "actual": 1.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2010-06-01",
          "pred": -1.0724610882592849,
          "actual": -0.62,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-09-01",
          "pred": -1.140872511397081,
          "actual": -1.56,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-12-01",
          "pred": 0.5337943980227065,
          "actual": -1.63,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2011-03-01",
          "pred": 0.6716219279652632,
          "actual": -0.98,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2011-06-01",
          "pred": 0.17772482589832111,
          "actual": -0.25,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-09-01",
          "pred": 0.100393039108226,
          "actual": -0.76,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-12-01",
          "pred": -0.41661896587268926,
          "actual": -1.05,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2012-03-01",
          "pred": -0.8885678061144959,
          "actual": -0.48,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2012-06-01",
          "pred": -0.54892416248153,
          "actual": 0.14,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-09-01",
          "pred": 0.7537178226800012,
          "actual": 0.44,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-12-01",
          "pred": 0.9957916255748034,
          "actual": -0.13,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2013-03-01",
          "pred": -0.32423986133885907,
          "actual": -0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2013-06-01",
          "pred": -1.6877299979914613,
          "actual": -0.33,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-09-01",
          "pred": -1.6740204266831749,
          "actual": -0.09,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-12-01",
          "pred": 0.15609506484948588,
          "actual": -0.09,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2014-03-01",
          "pred": -0.672637246135114,
          "actual": -0.07,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2014-06-01",
          "pred": -0.9281238641490064,
          "actual": 0.48,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-09-01",
          "pred": 0.19879184065283512,
          "actual": 0.37,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-12-01",
          "pred": 1.0324710929763774,
          "actual": 0.77,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2015-03-01",
          "pred": 2.025583801131161,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2015-06-01",
          "pred": 1.3138634475821163,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-09-01",
          "pred": 2.1483314089081404,
          "actual": 2.01,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-12-01",
          "pred": 1.7653837341801473,
          "actual": 2.56,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2016-03-01",
          "pred": 1.7133864517804014,
          "actual": 1.6,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2016-06-01",
          "pred": -0.5043069630730963,
          "actual": 0.06,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-09-01",
          "pred": 0.8858894598259632,
          "actual": -0.46,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-12-01",
          "pred": 1.4771473230503136,
          "actual": -0.51,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2017-03-01",
          "pred": 1.520129803683376,
          "actual": -0.09,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2017-06-01",
          "pred": 0.38302100409752454,
          "actual": 0.22,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-09-01",
          "pred": -0.41001380068279536,
          "actual": -0.56,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-12-01",
          "pred": -0.12467643465000042,
          "actual": -0.85,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2018-03-01",
          "pred": 0.1264716489748213,
          "actual": -0.73,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2018-06-01",
          "pred": 0.9829793801200598,
          "actual": 0.12,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-09-01",
          "pred": 2.0831076832456485,
          "actual": 0.3,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-12-01",
          "pred": 0.8491201944494493,
          "actual": 0.97,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2019-03-01",
          "pred": -1.303455148649556,
          "actual": 0.81,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2019-06-01",
          "pred": -2.0451098972001343,
          "actual": 0.66,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-09-01",
          "pred": -1.94609484162193,
          "actual": 0.11,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-12-01",
          "pred": 0.21703881767685507,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2020-03-01",
          "pred": -0.023405209903594928,
          "actual": 0.36,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2020-06-01",
          "pred": -0.22462927209312616,
          "actual": -0.21,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-09-01",
          "pred": -0.45541624229758765,
          "actual": -0.66,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-12-01",
          "pred": -0.04204787871192692,
          "actual": -0.98,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2021-03-01",
          "pred": 1.131695693723936,
          "actual": -0.72,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2021-06-01",
          "pred": 1.5382896688004626,
          "actual": -0.06,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-09-01",
          "pred": 1.419797599873967,
          "actual": -0.5,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-12-01",
          "pred": 0.4338307170515381,
          "actual": -1.07,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2022-03-01",
          "pred": -0.12746232214759823,
          "actual": -0.84,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2022-06-01",
          "pred": 0.1602031539092811,
          "actual": -0.77,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-09-01",
          "pred": 0.1882733489408479,
          "actual": -1.06,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-12-01",
          "pred": 0.30898239657657783,
          "actual": -0.86,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2023-03-01",
          "pred": -1.0838082677659495,
          "actual": -0.13,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2023-06-01",
          "pred": -2.396048964972074,
          "actual": 0.95,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-09-01",
          "pred": -1.9887821137135975,
          "actual": 1.65,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-12-01",
          "pred": 0.00943702719396284,
          "actual": 1.81,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2024-03-01",
          "pred": -0.5165921340027928,
          "actual": 1.1,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2024-06-01",
          "pred": 0.6054707379580689,
          "actual": 0.25,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-09-01",
          "pred": 1.6653350741763144,
          "actual": -0.11,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-12-01",
          "pred": 1.9225039505260693,
          "actual": -0.58,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2025-03-01",
          "pred": 0.6509801433620211,
          "actual": 0.05,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2025-06-01",
          "pred": 0.3213800304027443,
          "actual": 0.01,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-09-01",
          "pred": 1.1610949394536125,
          "actual": -0.3,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-12-01",
          "pred": 0.8052029296772248,
          "actual": -0.49,
          "persistence": -0.58
        }
      ],
      "24": [
        {
          "origin": "2006-09-01",
          "date": "2008-09-01",
          "pred": -0.008490236431242065,
          "actual": -0.28,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2008-12-01",
          "pred": 0.0344562888721684,
          "actual": -0.9,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2009-03-01",
          "pred": 1.5338863209393776,
          "actual": -0.72,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2009-06-01",
          "pred": 1.8209391351583926,
          "actual": 0.49,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2009-09-01",
          "pred": 1.7342578983901118,
          "actual": 0.68,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2009-12-01",
          "pred": 0.00538977441495827,
          "actual": 1.81,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2010-03-01",
          "pred": -0.4951004811137004,
          "actual": 1.07,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2010-06-01",
          "pred": -1.4608974164069368,
          "actual": -0.62,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2010-09-01",
          "pred": -2.5772536181851087,
          "actual": -1.56,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2010-12-01",
          "pred": -1.9946540453671349,
          "actual": -1.63,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2011-03-01",
          "pred": 0.45441414505254063,
          "actual": -0.98,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2011-06-01",
          "pred": 0.8964739407647287,
          "actual": -0.25,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2011-09-01",
          "pred": -0.23926093958172207,
          "actual": -0.76,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2011-12-01",
          "pred": 0.46675250348956165,
          "actual": -1.05,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2012-03-01",
          "pred": 0.8249684593746387,
          "actual": -0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2012-06-01",
          "pred": 1.880270464540412,
          "actual": 0.14,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2012-09-01",
          "pred": 1.6534082781139106,
          "actual": 0.44,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2012-12-01",
          "pred": 0.47951236053079455,
          "actual": -0.13,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2013-03-01",
          "pred": -1.970503349965191,
          "actual": -0.14,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2013-06-01",
          "pred": -2.2582874979332996,
          "actual": -0.33,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2013-09-01",
          "pred": -2.5964023982188356,
          "actual": -0.09,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2013-12-01",
          "pred": -1.2064428836695313,
          "actual": -0.09,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2014-03-01",
          "pred": 0.6088470055733144,
          "actual": -0.07,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2014-06-01",
          "pred": -0.463478563730031,
          "actual": 0.48,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2014-09-01",
          "pred": 0.4671017033214951,
          "actual": 0.37,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2014-12-01",
          "pred": 1.0754811261594177,
          "actual": 0.77,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2015-03-01",
          "pred": 2.022890893755577,
          "actual": 0.48,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2015-06-01",
          "pred": 2.292672005696591,
          "actual": 1.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2015-09-01",
          "pred": 1.7177692281971313,
          "actual": 2.01,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2015-12-01",
          "pred": 0.5969082515854833,
          "actual": 2.56,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2016-03-01",
          "pred": -0.28519822669472605,
          "actual": 1.6,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2016-06-01",
          "pred": -0.10549434366505744,
          "actual": 0.06,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2016-09-01",
          "pred": -0.9146317556844931,
          "actual": -0.46,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2016-12-01",
          "pred": -0.5023053003889272,
          "actual": -0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2017-03-01",
          "pred": -0.5467205947487196,
          "actual": -0.09,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2017-06-01",
          "pred": 2.120800131979567,
          "actual": 0.22,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2017-09-01",
          "pred": -0.16766161180762323,
          "actual": -0.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2017-12-01",
          "pred": -0.4329882640324423,
          "actual": -0.85,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2018-03-01",
          "pred": 0.781819360335099,
          "actual": -0.73,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2018-06-01",
          "pred": 1.6122105068408414,
          "actual": 0.12,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2018-09-01",
          "pred": 1.5865038195517418,
          "actual": 0.3,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2018-12-01",
          "pred": 1.2030896024842137,
          "actual": 0.97,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2019-03-01",
          "pred": -1.0606336878737705,
          "actual": 0.81,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2019-06-01",
          "pred": -1.6556734530338597,
          "actual": 0.66,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2019-09-01",
          "pred": -1.41203005804676,
          "actual": 0.11,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2019-12-01",
          "pred": -0.28236111546419673,
          "actual": 0.51,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2020-03-01",
          "pred": 0.00933951385844932,
          "actual": 0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2020-06-01",
          "pred": -1.599125224798219,
          "actual": -0.21,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2020-09-01",
          "pred": -0.8602524813215804,
          "actual": -0.66,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2020-12-01",
          "pred": -0.7140424823842889,
          "actual": -0.98,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2021-03-01",
          "pred": 0.7504301013840047,
          "actual": -0.72,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2021-06-01",
          "pred": 1.5321828591234539,
          "actual": -0.06,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2021-09-01",
          "pred": 1.7078605323906821,
          "actual": -0.5,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2021-12-01",
          "pred": 1.5967754974944233,
          "actual": -1.07,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2022-03-01",
          "pred": 0.5277716571016604,
          "actual": -0.84,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2022-06-01",
          "pred": 0.48120969571765654,
          "actual": -0.77,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2022-09-01",
          "pred": 0.30699994542142206,
          "actual": -1.06,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2022-12-01",
          "pred": -0.0031377136508982835,
          "actual": -0.86,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2023-03-01",
          "pred": 0.0038491990333189806,
          "actual": -0.13,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2023-06-01",
          "pred": -1.340155791272265,
          "actual": 0.95,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2023-09-01",
          "pred": -1.6471431729558201,
          "actual": 1.65,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2023-12-01",
          "pred": -0.6880336373824509,
          "actual": 1.81,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2024-03-01",
          "pred": 0.23618196070719344,
          "actual": 1.1,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2024-06-01",
          "pred": 0.2995410485871695,
          "actual": 0.25,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2024-09-01",
          "pred": 0.5173250053680836,
          "actual": -0.11,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2024-12-01",
          "pred": 1.115243378939327,
          "actual": -0.58,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2025-03-01",
          "pred": 1.5151390880781337,
          "actual": 0.05,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2025-06-01",
          "pred": -0.4960812225130091,
          "actual": 0.01,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2025-09-01",
          "pred": -0.5948733961440584,
          "actual": -0.3,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2025-12-01",
          "pred": 1.0342123187036272,
          "actual": -0.49,
          "persistence": 1.81
        }
      ],
      "60": [
        {
          "origin": "2006-09-01",
          "date": "2011-09-01",
          "pred": -0.2954258805416403,
          "actual": -0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2011-12-01",
          "pred": 0.09013706735702712,
          "actual": -1.05,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2012-03-01",
          "pred": 1.6287050112425514,
          "actual": -0.48,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2012-06-01",
          "pred": 0.6056174380205341,
          "actual": 0.14,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2012-09-01",
          "pred": 0.1820014977003161,
          "actual": 0.44,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2012-12-01",
          "pred": 0.21611234898302706,
          "actual": -0.13,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2013-03-01",
          "pred": -1.2478565189868018,
          "actual": -0.14,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2013-06-01",
          "pred": -1.6512103186488687,
          "actual": -0.33,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2013-09-01",
          "pred": -0.5164546762924322,
          "actual": -0.09,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2013-12-01",
          "pred": 1.2367572947918835,
          "actual": -0.09,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2014-03-01",
          "pred": 0.7143662582531731,
          "actual": -0.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2014-06-01",
          "pred": -0.2645333493558295,
          "actual": 0.48,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2014-09-01",
          "pred": 0.5452049788752301,
          "actual": 0.37,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2014-12-01",
          "pred": 2.142687189435721,
          "actual": 0.77,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2015-03-01",
          "pred": 2.3553607511101498,
          "actual": 0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2015-06-01",
          "pred": 1.4589154180181967,
          "actual": 1.28,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2015-09-01",
          "pred": 0.05968421299659117,
          "actual": 2.01,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2015-12-01",
          "pred": -1.5481649444770675,
          "actual": 2.56,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2016-03-01",
          "pred": -1.78265500896495,
          "actual": 1.6,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2016-06-01",
          "pred": -1.0566489750752324,
          "actual": 0.06,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2016-09-01",
          "pred": -0.13038970565399355,
          "actual": -0.46,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2016-12-01",
          "pred": 0.4736441509423248,
          "actual": -0.51,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2017-03-01",
          "pred": -0.2893601214790511,
          "actual": -0.09,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2017-06-01",
          "pred": -0.9904097211152934,
          "actual": 0.22,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2017-09-01",
          "pred": 0.8517244070632013,
          "actual": -0.56,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2017-12-01",
          "pred": 1.6933584933855539,
          "actual": -0.85,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2018-03-01",
          "pred": 0.9651761714392806,
          "actual": -0.73,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2018-06-01",
          "pred": -0.43696057482913253,
          "actual": 0.12,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2018-09-01",
          "pred": 0.5912572662050531,
          "actual": 0.3,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2018-12-01",
          "pred": 0.7911663771047616,
          "actual": 0.97,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2019-03-01",
          "pred": 0.5500789765953826,
          "actual": 0.81,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2019-06-01",
          "pred": -0.3029316275029925,
          "actual": 0.66,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2019-09-01",
          "pred": 1.0142702042810015,
          "actual": 0.11,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2019-12-01",
          "pred": 0.6042406376010862,
          "actual": 0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2020-03-01",
          "pred": 1.0877106984972644,
          "actual": 0.36,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2020-06-01",
          "pred": 1.2685825139105302,
          "actual": -0.21,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2020-09-01",
          "pred": -1.05165498537332,
          "actual": -0.66,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2020-12-01",
          "pred": 0.4802599025684462,
          "actual": -0.98,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2021-03-01",
          "pred": 1.8192456844401343,
          "actual": -0.72,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2021-06-01",
          "pred": 0.595858086763435,
          "actual": -0.06,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2021-09-01",
          "pred": -0.9923030500632212,
          "actual": -0.5,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2021-12-01",
          "pred": -2.2337429546507015,
          "actual": -1.07,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2022-03-01",
          "pred": -1.8557748136570267,
          "actual": -0.84,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2022-06-01",
          "pred": -1.2677678191458324,
          "actual": -0.77,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2022-09-01",
          "pred": -0.3152265268689313,
          "actual": -1.06,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2022-12-01",
          "pred": -0.19261054988919016,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2023-03-01",
          "pred": -1.94519500203448,
          "actual": -0.13,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2023-06-01",
          "pred": -2.7814632852932304,
          "actual": 0.95,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2023-09-01",
          "pred": -0.5887831263477095,
          "actual": 1.65,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2023-12-01",
          "pred": 0.6860778965318634,
          "actual": 1.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2024-03-01",
          "pred": 1.9562886777476653,
          "actual": 1.1,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2024-06-01",
          "pred": 1.6796273919694884,
          "actual": 0.25,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2024-09-01",
          "pred": 0.9909806775688368,
          "actual": -0.11,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2024-12-01",
          "pred": 0.8891966333084851,
          "actual": -0.58,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2025-03-01",
          "pred": 0.7865507769935693,
          "actual": 0.05,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2025-06-01",
          "pred": 1.1345347165647746,
          "actual": 0.01,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2025-09-01",
          "pred": 0.9063258405028698,
          "actual": -0.3,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2025-12-01",
          "pred": 0.9890156750474345,
          "actual": -0.49,
          "persistence": -0.98
        }
      ]
    },
    "phi_flow_decoder": {
      "1": [
        {
          "origin": "2006-09-01",
          "date": "2006-10-01",
          "pred": 0.5048251423418392,
          "actual": 0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-01-01",
          "pred": 1.2566708786464473,
          "actual": 0.59,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-04-01",
          "pred": 0.4202516613790309,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-07-01",
          "pred": -0.08859932536382972,
          "actual": -0.37,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-10-01",
          "pred": -0.37668247660982995,
          "actual": -1.41,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-01-01",
          "pred": -0.5862974608811357,
          "actual": -1.79,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-04-01",
          "pred": -0.9675357329699321,
          "actual": -0.89,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-07-01",
          "pred": -0.9091796326538785,
          "actual": -0.04,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-10-01",
          "pred": -0.3510773656951216,
          "actual": -0.3,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-01-01",
          "pred": 0.010532176376812072,
          "actual": -1.0,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-04-01",
          "pred": -0.7944851234806066,
          "actual": -0.25,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-07-01",
          "pred": 0.6629490597596018,
          "actual": 0.69,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-10-01",
          "pred": 1.1372808652127986,
          "actual": 0.96,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-01-01",
          "pred": 1.8457948250761718,
          "actual": 1.43,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-04-01",
          "pred": 0.10350814867434699,
          "actual": 0.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-07-01",
          "pred": -0.5869835417553504,
          "actual": -0.89,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-10-01",
          "pred": -1.3451511227522484,
          "actual": -1.65,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-01-01",
          "pred": -1.0969166689466803,
          "actual": -1.7,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-04-01",
          "pred": -1.2607315921430142,
          "actual": -0.74,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-07-01",
          "pred": -0.9442563862354013,
          "actual": -0.23,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-10-01",
          "pred": -0.5911065675001997,
          "actual": -0.93,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-01-01",
          "pred": -1.2974577890086931,
          "actual": -0.93,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-04-01",
          "pred": -0.866044839545922,
          "actual": -0.29,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-07-01",
          "pred": 0.2946807904392342,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-10-01",
          "pred": 0.8546637056227329,
          "actual": 0.23,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-01-01",
          "pred": -0.041456007302567696,
          "actual": -0.42,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-04-01",
          "pred": -0.7325453012720797,
          "actual": -0.08,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-07-01",
          "pred": -0.5522243445542268,
          "actual": -0.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-10-01",
          "pred": -0.2563544625488971,
          "actual": -0.24,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-01-01",
          "pred": -0.2712006459359483,
          "actual": -0.42,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-04-01",
          "pred": -0.1896238615249155,
          "actual": 0.28,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-07-01",
          "pred": 0.95491106892593,
          "actual": 0.13,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-10-01",
          "pred": 0.5874065275944191,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-01-01",
          "pred": 1.095727764704082,
          "actual": 0.59,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-04-01",
          "pred": 0.4703486913227854,
          "actual": 0.9,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-07-01",
          "pred": 0.6121178426383589,
          "actual": 1.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-10-01",
          "pred": 2.210903765743047,
          "actual": 2.21,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-01-01",
          "pred": 2.5175674917886126,
          "actual": 2.56,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-04-01",
          "pred": 1.90628589730575,
          "actual": 1.05,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-07-01",
          "pred": 0.38616339674092687,
          "actual": -0.25,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-10-01",
          "pred": -1.2853596865394739,
          "actual": -0.75,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-01-01",
          "pred": -0.19120648843345422,
          "actual": -0.34,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-04-01",
          "pred": 0.054638822083876694,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-07-01",
          "pred": -0.016348032063403267,
          "actual": 0.22,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-10-01",
          "pred": -0.5133018548199489,
          "actual": -0.52,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-01-01",
          "pred": -0.649545725839813,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-04-01",
          "pred": 0.2220060617404511,
          "actual": -0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-07-01",
          "pred": 0.2440623526093348,
          "actual": 0.27,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-10-01",
          "pred": 0.24760926242884124,
          "actual": 0.84,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-01-01",
          "pred": 1.0595826989147472,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-04-01",
          "pred": -0.16799627810223872,
          "actual": 0.67,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-07-01",
          "pred": 0.3926752125345231,
          "actual": 0.41,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-10-01",
          "pred": 0.18843234816305915,
          "actual": 0.55,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-01-01",
          "pred": 0.5520046397097558,
          "actual": 0.64,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-04-01",
          "pred": 0.5098838312522952,
          "actual": 0.49,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-07-01",
          "pred": -0.08865646677900428,
          "actual": -0.04,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-10-01",
          "pred": -0.5456733180242145,
          "actual": -1.19,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-01-01",
          "pred": -0.8138499349448457,
          "actual": -1.04,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-04-01",
          "pred": -0.02499567337023981,
          "actual": -0.55,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-07-01",
          "pred": -0.3933967447833581,
          "actual": -0.2,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-10-01",
          "pred": -0.07752867001840787,
          "actual": -0.78,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-01-01",
          "pred": -0.4298425338116874,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-04-01",
          "pred": -0.6162782441076391,
          "actual": -0.9,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-07-01",
          "pred": -0.5310185228509887,
          "actual": -0.56,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-10-01",
          "pred": -0.5851016893647942,
          "actual": -0.99,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-01-01",
          "pred": -0.807388800930826,
          "actual": -0.78,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-04-01",
          "pred": -0.503091058753841,
          "actual": 0.24,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-07-01",
          "pred": 0.6608723747826548,
          "actual": 1.2,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-10-01",
          "pred": 1.294530612656122,
          "actual": 1.59,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-01-01",
          "pred": 1.721907207676077,
          "actual": 1.71,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-04-01",
          "pred": 1.159631002672971,
          "actual": 0.93,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-07-01",
          "pred": -0.028343360727056562,
          "actual": 0.2,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-10-01",
          "pred": -0.08878137341144515,
          "actual": -0.24,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-01-01",
          "pred": 0.5832172133784592,
          "actual": -0.76,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-04-01",
          "pred": 0.43994963691561334,
          "actual": -0.08,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-07-01",
          "pred": 0.0651870730775789,
          "actual": -0.03,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-10-01",
          "pred": -0.8150310634129436,
          "actual": -0.5,
          "persistence": -0.3
        }
      ],
      "3": [
        {
          "origin": "2006-09-01",
          "date": "2006-12-01",
          "pred": 0.45525604472945946,
          "actual": 1.1,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-03-01",
          "pred": 1.5020490663195207,
          "actual": -0.15,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-06-01",
          "pred": 0.5764637250755968,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-09-01",
          "pred": 0.3391451823295632,
          "actual": -1.04,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-12-01",
          "pred": -0.19585289902406033,
          "actual": -1.61,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-03-01",
          "pred": 0.09289565018270768,
          "actual": -1.17,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-06-01",
          "pred": -0.9466809444143144,
          "actual": -0.44,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-09-01",
          "pred": -1.3505622958123225,
          "actual": -0.28,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-12-01",
          "pred": -0.009357014727731282,
          "actual": -0.9,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-03-01",
          "pred": -0.018175720005345515,
          "actual": -0.72,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-06-01",
          "pred": -1.1516985533867354,
          "actual": 0.49,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-09-01",
          "pred": 0.7745605101278646,
          "actual": 0.68,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-12-01",
          "pred": 1.8726079587041742,
          "actual": 1.81,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-03-01",
          "pred": 0.6467730517710786,
          "actual": 1.07,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-06-01",
          "pred": -0.3017341387399798,
          "actual": -0.62,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-09-01",
          "pred": -0.03753952302739959,
          "actual": -1.56,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-12-01",
          "pred": -1.2361301273374794,
          "actual": -1.63,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-03-01",
          "pred": -0.6103188320951449,
          "actual": -0.98,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-06-01",
          "pred": -0.9528009398106301,
          "actual": -0.25,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-09-01",
          "pred": -1.5949342954608428,
          "actual": -0.76,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-12-01",
          "pred": -0.8044717541688922,
          "actual": -1.05,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-03-01",
          "pred": -1.212867281145806,
          "actual": -0.48,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-06-01",
          "pred": -0.7872788691768184,
          "actual": 0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-09-01",
          "pred": 1.1473806965318791,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-12-01",
          "pred": 0.8587747838927138,
          "actual": -0.13,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-03-01",
          "pred": -0.5370735723710244,
          "actual": -0.14,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-06-01",
          "pred": -1.223667330967767,
          "actual": -0.33,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-09-01",
          "pred": -0.7319799448992519,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-12-01",
          "pred": -0.2723095922027674,
          "actual": -0.09,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-03-01",
          "pred": -0.14814482840225612,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-06-01",
          "pred": 0.19528564122527103,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-09-01",
          "pred": 1.089188034567084,
          "actual": 0.37,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-12-01",
          "pred": 0.8056397766845793,
          "actual": 0.77,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-03-01",
          "pred": 1.053385961026234,
          "actual": 0.48,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-06-01",
          "pred": 0.8038642266118847,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-09-01",
          "pred": 0.1438958818785398,
          "actual": 2.01,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-12-01",
          "pred": 2.119465519934184,
          "actual": 2.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-03-01",
          "pred": 2.6278565076495797,
          "actual": 1.6,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-06-01",
          "pred": 1.7711941647556066,
          "actual": 0.06,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-09-01",
          "pred": 0.8234359791529432,
          "actual": -0.46,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-12-01",
          "pred": -1.5658913346749617,
          "actual": -0.51,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-03-01",
          "pred": 0.13921919514040182,
          "actual": -0.09,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-06-01",
          "pred": -0.23721767426936036,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-09-01",
          "pred": -0.3628672359085914,
          "actual": -0.56,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-12-01",
          "pred": -0.6866941730521607,
          "actual": -0.85,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-03-01",
          "pred": -1.0116077564888721,
          "actual": -0.73,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-06-01",
          "pred": 0.698224475894184,
          "actual": 0.12,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-09-01",
          "pred": 0.432139638328225,
          "actual": 0.3,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-12-01",
          "pred": 0.6422908699888041,
          "actual": 0.97,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-03-01",
          "pred": 0.28659161198350336,
          "actual": 0.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-06-01",
          "pred": -0.6404496016877532,
          "actual": 0.66,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-09-01",
          "pred": -0.35250434458696966,
          "actual": 0.11,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-12-01",
          "pred": 0.21924170287858946,
          "actual": 0.51,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-03-01",
          "pred": 0.3508324676289542,
          "actual": 0.36,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-06-01",
          "pred": 1.1068326164824906,
          "actual": -0.21,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-09-01",
          "pred": -0.008262482612852718,
          "actual": -0.66,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-12-01",
          "pred": -0.4423384658596541,
          "actual": -0.98,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-03-01",
          "pred": -0.9597910025065522,
          "actual": -0.72,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-06-01",
          "pred": -0.190365188005288,
          "actual": -0.06,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-09-01",
          "pred": -0.9211264893792518,
          "actual": -0.5,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-12-01",
          "pred": 0.31893212615748856,
          "actual": -1.07,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-03-01",
          "pred": -0.31348096454887425,
          "actual": -0.84,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-06-01",
          "pred": -0.756120863727057,
          "actual": -0.77,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-09-01",
          "pred": -0.48848235041104887,
          "actual": -1.06,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-12-01",
          "pred": -0.8428403555255501,
          "actual": -0.86,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-03-01",
          "pred": -1.3345542701732873,
          "actual": -0.13,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-06-01",
          "pred": -0.8409141506500261,
          "actual": 0.95,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-09-01",
          "pred": 0.32597586246839527,
          "actual": 1.65,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-12-01",
          "pred": 1.638383049615205,
          "actual": 1.81,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-03-01",
          "pred": 1.9959789203922562,
          "actual": 1.1,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-06-01",
          "pred": 1.5767313753249086,
          "actual": 0.25,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-09-01",
          "pred": 0.43535713762718037,
          "actual": -0.11,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-12-01",
          "pred": 0.26108635358784005,
          "actual": -0.58,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-03-01",
          "pred": 1.222637429331992,
          "actual": 0.05,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-06-01",
          "pred": 0.4731592876564629,
          "actual": 0.01,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-09-01",
          "pred": -0.4602664395540926,
          "actual": -0.3,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-12-01",
          "pred": -0.8078940128464381,
          "actual": -0.49,
          "persistence": -0.3
        }
      ],
      "6": [
        {
          "origin": "2006-09-01",
          "date": "2007-03-01",
          "pred": 0.5291322531556879,
          "actual": -0.15,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-06-01",
          "pred": 0.702046660066225,
          "actual": -0.16,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-09-01",
          "pred": 1.077498253400389,
          "actual": -1.04,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-12-01",
          "pred": 0.9585332144979412,
          "actual": -1.61,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-03-01",
          "pred": 1.0280283600023115,
          "actual": -1.17,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-06-01",
          "pred": -0.22062613195253478,
          "actual": -0.44,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-09-01",
          "pred": -1.06034857648838,
          "actual": -0.28,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-12-01",
          "pred": -1.4144592503538689,
          "actual": -0.9,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-03-01",
          "pred": -0.8280468854910846,
          "actual": -0.72,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-06-01",
          "pred": -0.8382694112465793,
          "actual": 0.49,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-09-01",
          "pred": 0.14218527088702057,
          "actual": 0.68,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-12-01",
          "pred": 1.897281852588224,
          "actual": 1.81,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-03-01",
          "pred": 0.6810639119120152,
          "actual": 1.07,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-06-01",
          "pred": -1.0544978698890963,
          "actual": -0.62,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-09-01",
          "pred": -0.33501964263921424,
          "actual": -1.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-12-01",
          "pred": 0.2660390960483045,
          "actual": -1.63,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-03-01",
          "pred": -0.07162444483625349,
          "actual": -0.98,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-06-01",
          "pred": 0.7717224036586318,
          "actual": -0.25,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-09-01",
          "pred": -1.2818523788751854,
          "actual": -0.76,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-12-01",
          "pred": -1.787702283556679,
          "actual": -1.05,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-03-01",
          "pred": -1.4683800955006543,
          "actual": -0.48,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-06-01",
          "pred": -1.1716829778978832,
          "actual": 0.14,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-09-01",
          "pred": 0.8226216012875727,
          "actual": 0.44,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-12-01",
          "pred": 1.8422184140141338,
          "actual": -0.13,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-03-01",
          "pred": 0.25069208045825514,
          "actual": -0.14,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-06-01",
          "pred": -1.2775745888959655,
          "actual": -0.33,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-09-01",
          "pred": -1.2087004772619048,
          "actual": -0.09,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-12-01",
          "pred": -0.31041639967222845,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-03-01",
          "pred": -0.12270361419008503,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-06-01",
          "pred": -0.49048211105563855,
          "actual": 0.48,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-09-01",
          "pred": 0.5528070169349464,
          "actual": 0.37,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-12-01",
          "pred": 1.4401858134056034,
          "actual": 0.77,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-03-01",
          "pred": 0.9170388288924627,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-06-01",
          "pred": 1.1936557879874758,
          "actual": 1.28,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-09-01",
          "pred": 1.6201722478998193,
          "actual": 2.01,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-12-01",
          "pred": 0.830856427464364,
          "actual": 2.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-03-01",
          "pred": 2.161224867964969,
          "actual": 1.6,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-06-01",
          "pred": 2.114560687259419,
          "actual": 0.06,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-09-01",
          "pred": 0.9493914959660534,
          "actual": -0.46,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-12-01",
          "pred": 0.6901218222841724,
          "actual": -0.51,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-03-01",
          "pred": 0.00882385656033747,
          "actual": -0.09,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-06-01",
          "pred": 1.2941974803529195,
          "actual": 0.22,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-09-01",
          "pred": -0.7498539071409,
          "actual": -0.56,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-12-01",
          "pred": -1.085388128880248,
          "actual": -0.85,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-03-01",
          "pred": -0.45460018272575914,
          "actual": -0.73,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-06-01",
          "pred": 0.07067063246021225,
          "actual": 0.12,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-09-01",
          "pred": 1.6015009743490551,
          "actual": 0.3,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-12-01",
          "pred": 0.6738638460798823,
          "actual": 0.97,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-03-01",
          "pred": -0.21069997514472533,
          "actual": 0.81,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-06-01",
          "pred": -0.8657075078554861,
          "actual": 0.66,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-09-01",
          "pred": -0.9905449553309311,
          "actual": 0.11,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-12-01",
          "pred": -0.3663764611166872,
          "actual": 0.51,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-03-01",
          "pred": 0.33999836448077053,
          "actual": 0.36,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-06-01",
          "pred": 0.655723133906462,
          "actual": -0.21,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-09-01",
          "pred": 0.8993235751890889,
          "actual": -0.66,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-12-01",
          "pred": -0.2830590901181855,
          "actual": -0.98,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-03-01",
          "pred": -0.11495681930014776,
          "actual": -0.72,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-06-01",
          "pred": -0.5606767475736751,
          "actual": -0.06,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-09-01",
          "pred": -0.1429045144990556,
          "actual": -0.5,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-12-01",
          "pred": -0.7792793349846897,
          "actual": -1.07,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-03-01",
          "pred": -0.5178614252770587,
          "actual": -0.84,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-06-01",
          "pred": -0.5158049207159102,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-09-01",
          "pred": 0.060160928286677746,
          "actual": -1.06,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-12-01",
          "pred": -0.4167952276983905,
          "actual": -0.86,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-03-01",
          "pred": -0.89776187069622,
          "actual": -0.13,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-06-01",
          "pred": -1.9032559479511262,
          "actual": 0.95,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-09-01",
          "pred": -0.7841591968351171,
          "actual": 1.65,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-12-01",
          "pred": 0.507998248958906,
          "actual": 1.81,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-03-01",
          "pred": 1.5015479265070129,
          "actual": 1.1,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-06-01",
          "pred": 1.6693441314164017,
          "actual": 0.25,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-09-01",
          "pred": 1.8929971412527444,
          "actual": -0.11,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-12-01",
          "pred": 0.6153293597408552,
          "actual": -0.58,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-03-01",
          "pred": 1.4098217268354007,
          "actual": 0.05,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-06-01",
          "pred": 1.6899826268720748,
          "actual": 0.01,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-09-01",
          "pred": -0.70007748557012,
          "actual": -0.3,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-12-01",
          "pred": -0.9943981453279706,
          "actual": -0.49,
          "persistence": 0.01
        }
      ],
      "12": [
        {
          "origin": "2006-09-01",
          "date": "2007-09-01",
          "pred": 1.603326589703757,
          "actual": -1.04,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-12-01",
          "pred": 2.377322945037828,
          "actual": -1.61,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2008-03-01",
          "pred": 1.6747671790785208,
          "actual": -1.17,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2008-06-01",
          "pred": 0.09167011108450013,
          "actual": -0.44,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-09-01",
          "pred": -0.4301152684243054,
          "actual": -0.28,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-12-01",
          "pred": -0.4051999914163045,
          "actual": -0.9,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2009-03-01",
          "pred": -0.609483867906656,
          "actual": -0.72,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2009-06-01",
          "pred": -1.375328056657576,
          "actual": 0.49,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-09-01",
          "pred": -0.20868207271369682,
          "actual": 0.68,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-12-01",
          "pred": 1.5515367818727044,
          "actual": 1.81,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2010-03-01",
          "pred": -0.4030981172479712,
          "actual": 1.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2010-06-01",
          "pred": -1.10340910572608,
          "actual": -0.62,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-09-01",
          "pred": -1.0289302401486338,
          "actual": -1.56,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-12-01",
          "pred": 0.5699282716120375,
          "actual": -1.63,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2011-03-01",
          "pred": 0.6707268254963669,
          "actual": -0.98,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2011-06-01",
          "pred": 0.29634543882536496,
          "actual": -0.25,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-09-01",
          "pred": 0.06915591468956839,
          "actual": -0.76,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-12-01",
          "pred": -0.5851637618255616,
          "actual": -1.05,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2012-03-01",
          "pred": -0.9632027693300866,
          "actual": -0.48,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2012-06-01",
          "pred": -0.6548319499481597,
          "actual": 0.14,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-09-01",
          "pred": 0.7482226256330152,
          "actual": 0.44,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-12-01",
          "pred": 1.2071184005978093,
          "actual": -0.13,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2013-03-01",
          "pred": -0.29788115016120437,
          "actual": -0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2013-06-01",
          "pred": -1.7492462449675341,
          "actual": -0.33,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-09-01",
          "pred": -1.5665386928181406,
          "actual": -0.09,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-12-01",
          "pred": 0.21353107451131986,
          "actual": -0.09,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2014-03-01",
          "pred": -0.7268996674739203,
          "actual": -0.07,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2014-06-01",
          "pred": -0.9165926311856766,
          "actual": 0.48,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-09-01",
          "pred": 0.2516893146709158,
          "actual": 0.37,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-12-01",
          "pred": 0.9393745586393767,
          "actual": 0.77,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2015-03-01",
          "pred": 2.136902219186393,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2015-06-01",
          "pred": 1.2314434790204758,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-09-01",
          "pred": 2.031158394396596,
          "actual": 2.01,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-12-01",
          "pred": 1.6588259323531802,
          "actual": 2.56,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2016-03-01",
          "pred": 1.6523805200950505,
          "actual": 1.6,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2016-06-01",
          "pred": -0.5866985048563693,
          "actual": 0.06,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-09-01",
          "pred": 1.172775025210523,
          "actual": -0.46,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-12-01",
          "pred": 1.6325313519327367,
          "actual": -0.51,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2017-03-01",
          "pred": 1.4366333662083377,
          "actual": -0.09,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2017-06-01",
          "pred": 0.2091254475616387,
          "actual": 0.22,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-09-01",
          "pred": -0.41001597472669593,
          "actual": -0.56,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-12-01",
          "pred": -0.14693969607620025,
          "actual": -0.85,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2018-03-01",
          "pred": 0.13049220756273883,
          "actual": -0.73,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2018-06-01",
          "pred": 0.9844437248466579,
          "actual": 0.12,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-09-01",
          "pred": 2.2393191074200693,
          "actual": 0.3,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-12-01",
          "pred": 1.0624496837731083,
          "actual": 0.97,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2019-03-01",
          "pred": -1.226587906630999,
          "actual": 0.81,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2019-06-01",
          "pred": -2.0209068022837706,
          "actual": 0.66,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-09-01",
          "pred": -1.9938116876318086,
          "actual": 0.11,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-12-01",
          "pred": 0.320814266862672,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2020-03-01",
          "pred": 0.12300830737250497,
          "actual": 0.36,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2020-06-01",
          "pred": -0.1999486929980262,
          "actual": -0.21,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-09-01",
          "pred": -0.4181519044356209,
          "actual": -0.66,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-12-01",
          "pred": -0.2002426678927457,
          "actual": -0.98,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2021-03-01",
          "pred": 1.0287221507135347,
          "actual": -0.72,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2021-06-01",
          "pred": 1.4917519498706742,
          "actual": -0.06,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-09-01",
          "pred": 1.2162932907911523,
          "actual": -0.5,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-12-01",
          "pred": 0.20179864870441677,
          "actual": -1.07,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2022-03-01",
          "pred": -0.543175025832468,
          "actual": -0.84,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2022-06-01",
          "pred": -0.2783233034999175,
          "actual": -0.77,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-09-01",
          "pred": -0.019961397810982648,
          "actual": -1.06,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-12-01",
          "pred": 0.17682841021758217,
          "actual": -0.86,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2023-03-01",
          "pred": -1.2206676136535877,
          "actual": -0.13,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2023-06-01",
          "pred": -2.4523026982213025,
          "actual": 0.95,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-09-01",
          "pred": -2.176224621776089,
          "actual": 1.65,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-12-01",
          "pred": 0.007980336536424736,
          "actual": 1.81,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2024-03-01",
          "pred": -0.5336951304181365,
          "actual": 1.1,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2024-06-01",
          "pred": 0.7236268158723507,
          "actual": 0.25,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-09-01",
          "pred": 1.7625962680145237,
          "actual": -0.11,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-12-01",
          "pred": 2.0285992026960686,
          "actual": -0.58,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2025-03-01",
          "pred": 0.7755369573743395,
          "actual": 0.05,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2025-06-01",
          "pred": 0.40785786653639966,
          "actual": 0.01,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-09-01",
          "pred": 1.0954039330344927,
          "actual": -0.3,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-12-01",
          "pred": 0.6440796749002455,
          "actual": -0.49,
          "persistence": -0.58
        }
      ],
      "24": [
        {
          "origin": "2006-09-01",
          "date": "2008-09-01",
          "pred": 0.28109039552245707,
          "actual": -0.28,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2008-12-01",
          "pred": 0.4351452962516622,
          "actual": -0.9,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2009-03-01",
          "pred": 2.139871427171658,
          "actual": -0.72,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2009-06-01",
          "pred": 2.256766410736135,
          "actual": 0.49,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2009-09-01",
          "pred": 1.9148198589712897,
          "actual": 0.68,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2009-12-01",
          "pred": 0.3206135343303228,
          "actual": 1.81,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2010-03-01",
          "pred": -0.19914237472734464,
          "actual": 1.07,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2010-06-01",
          "pred": -1.2486910851100863,
          "actual": -0.62,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2010-09-01",
          "pred": -2.1992901411587016,
          "actual": -1.56,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2010-12-01",
          "pred": -1.5360244950638842,
          "actual": -1.63,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2011-03-01",
          "pred": 0.6912819612396353,
          "actual": -0.98,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2011-06-01",
          "pred": 1.2086553995445877,
          "actual": -0.25,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2011-09-01",
          "pred": -0.2020639576055857,
          "actual": -0.76,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2011-12-01",
          "pred": 0.6237776324126089,
          "actual": -1.05,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2012-03-01",
          "pred": 0.5790983276147874,
          "actual": -0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2012-06-01",
          "pred": 1.8293528817276232,
          "actual": 0.14,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2012-09-01",
          "pred": 1.8844744279279704,
          "actual": 0.44,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2012-12-01",
          "pred": 0.6726109760531073,
          "actual": -0.13,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2013-03-01",
          "pred": -1.838841381401984,
          "actual": -0.14,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2013-06-01",
          "pred": -2.257900942852086,
          "actual": -0.33,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2013-09-01",
          "pred": -2.4870040144405388,
          "actual": -0.09,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2013-12-01",
          "pred": -1.3977916020659944,
          "actual": -0.09,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2014-03-01",
          "pred": 0.6939991823101697,
          "actual": -0.07,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2014-06-01",
          "pred": -0.6759187048653983,
          "actual": 0.48,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2014-09-01",
          "pred": 0.4902057851537995,
          "actual": 0.37,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2014-12-01",
          "pred": 1.0841704677643704,
          "actual": 0.77,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2015-03-01",
          "pred": 2.0884578245686902,
          "actual": 0.48,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2015-06-01",
          "pred": 2.4094636491309362,
          "actual": 1.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2015-09-01",
          "pred": 2.0071375662935242,
          "actual": 2.01,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2015-12-01",
          "pred": 0.8140360964130282,
          "actual": 2.56,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2016-03-01",
          "pred": -0.0568930289858581,
          "actual": 1.6,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2016-06-01",
          "pred": -0.14324668610469937,
          "actual": 0.06,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2016-09-01",
          "pred": -1.0035141937525587,
          "actual": -0.46,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2016-12-01",
          "pred": -0.35200621232185136,
          "actual": -0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2017-03-01",
          "pred": -0.4852703824307037,
          "actual": -0.09,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2017-06-01",
          "pred": 2.0408113693702923,
          "actual": 0.22,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2017-09-01",
          "pred": -0.237587160022206,
          "actual": -0.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2017-12-01",
          "pred": -0.3318509944659342,
          "actual": -0.85,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2018-03-01",
          "pred": 1.0413597959329537,
          "actual": -0.73,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2018-06-01",
          "pred": 1.5999147223403127,
          "actual": 0.12,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2018-09-01",
          "pred": 1.279104516455811,
          "actual": 0.3,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2018-12-01",
          "pred": 1.0337730730370693,
          "actual": 0.97,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2019-03-01",
          "pred": -0.9114974461670362,
          "actual": 0.81,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2019-06-01",
          "pred": -1.3605213835555285,
          "actual": 0.66,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2019-09-01",
          "pred": -1.1241172166786038,
          "actual": 0.11,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2019-12-01",
          "pred": -0.15738592642262628,
          "actual": 0.51,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2020-03-01",
          "pred": 0.301710392460476,
          "actual": 0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2020-06-01",
          "pred": -1.7270869360950276,
          "actual": -0.21,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2020-09-01",
          "pred": -0.5256644285722722,
          "actual": -0.66,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2020-12-01",
          "pred": -0.5823654567403526,
          "actual": -0.98,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2021-03-01",
          "pred": 0.8505288044863786,
          "actual": -0.72,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2021-06-01",
          "pred": 1.5955447279264716,
          "actual": -0.06,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2021-09-01",
          "pred": 1.5886529285986535,
          "actual": -0.5,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2021-12-01",
          "pred": 1.5228935839074125,
          "actual": -1.07,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2022-03-01",
          "pred": 0.437046622903553,
          "actual": -0.84,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2022-06-01",
          "pred": 0.10571015190333238,
          "actual": -0.77,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2022-09-01",
          "pred": -0.018877760174315264,
          "actual": -1.06,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2022-12-01",
          "pred": -0.12078052200789868,
          "actual": -0.86,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2023-03-01",
          "pred": -0.3897227719095592,
          "actual": -0.13,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2023-06-01",
          "pred": -1.5197221994827077,
          "actual": 0.95,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2023-09-01",
          "pred": -1.8808535713745027,
          "actual": 1.65,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2023-12-01",
          "pred": -0.8340769749879453,
          "actual": 1.81,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2024-03-01",
          "pred": 0.02282484733278467,
          "actual": 1.1,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2024-06-01",
          "pred": -0.0456530230422985,
          "actual": 0.25,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2024-09-01",
          "pred": 0.39780318571747514,
          "actual": -0.11,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2024-12-01",
          "pred": 1.1835177845251685,
          "actual": -0.58,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2025-03-01",
          "pred": 1.730955017735006,
          "actual": 0.05,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2025-06-01",
          "pred": -0.396263234411535,
          "actual": 0.01,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2025-09-01",
          "pred": -0.6710895913485797,
          "actual": -0.3,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2025-12-01",
          "pred": 1.1065630966249613,
          "actual": -0.49,
          "persistence": 1.81
        }
      ],
      "60": [
        {
          "origin": "2006-09-01",
          "date": "2011-09-01",
          "pred": 0.04779307329246858,
          "actual": -0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2011-12-01",
          "pred": 1.0620988498084207,
          "actual": -1.05,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2012-03-01",
          "pred": 2.423222274702946,
          "actual": -0.48,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2012-06-01",
          "pred": 1.5979254863645318,
          "actual": 0.14,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2012-09-01",
          "pred": 0.591107030148504,
          "actual": 0.44,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2012-12-01",
          "pred": 0.6829054883395462,
          "actual": -0.13,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2013-03-01",
          "pred": -0.1992470573157005,
          "actual": -0.14,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2013-06-01",
          "pred": 0.14548115473691808,
          "actual": -0.33,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2013-09-01",
          "pred": 0.34245279415681196,
          "actual": -0.09,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2013-12-01",
          "pred": 2.7323499283794934,
          "actual": -0.09,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2014-03-01",
          "pred": 1.552289077195574,
          "actual": -0.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2014-06-01",
          "pred": 0.5943434111622864,
          "actual": 0.48,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2014-09-01",
          "pred": 1.5965363488021231,
          "actual": 0.37,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2014-12-01",
          "pred": 2.6767126023294603,
          "actual": 0.77,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2015-03-01",
          "pred": 2.752435951560306,
          "actual": 0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2015-06-01",
          "pred": 1.741638995676072,
          "actual": 1.28,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2015-09-01",
          "pred": 0.05526493009796529,
          "actual": 2.01,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2015-12-01",
          "pred": -1.0710097297848649,
          "actual": 2.56,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2016-03-01",
          "pred": -1.4344096410462914,
          "actual": 1.6,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2016-06-01",
          "pred": -0.9308335874168044,
          "actual": 0.06,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2016-09-01",
          "pred": -0.2699842025803677,
          "actual": -0.46,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2016-12-01",
          "pred": 0.9532965863956946,
          "actual": -0.51,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2017-03-01",
          "pred": -0.20212280082209821,
          "actual": -0.09,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2017-06-01",
          "pred": -0.889630272485386,
          "actual": 0.22,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2017-09-01",
          "pred": 0.8429984726213382,
          "actual": -0.56,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2017-12-01",
          "pred": 2.318205537085882,
          "actual": -0.85,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2018-03-01",
          "pred": 0.5218305826193714,
          "actual": -0.73,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2018-06-01",
          "pred": -0.5338139394337483,
          "actual": 0.12,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2018-09-01",
          "pred": 0.7132806841507976,
          "actual": 0.3,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2018-12-01",
          "pred": 1.0388881766534224,
          "actual": 0.97,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2019-03-01",
          "pred": -0.3506653657266673,
          "actual": 0.81,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2019-06-01",
          "pred": -1.3109354240261286,
          "actual": 0.66,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2019-09-01",
          "pred": 0.5930502780513408,
          "actual": 0.11,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2019-12-01",
          "pred": -0.09692027726476105,
          "actual": 0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2020-03-01",
          "pred": 0.3952945709596683,
          "actual": 0.36,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2020-06-01",
          "pred": 0.5690004220946396,
          "actual": -0.21,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2020-09-01",
          "pred": -0.8083301327043685,
          "actual": -0.66,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2020-12-01",
          "pred": 0.6953333652938883,
          "actual": -0.98,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2021-03-01",
          "pred": 2.1004717514344993,
          "actual": -0.72,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2021-06-01",
          "pred": 1.4137150145729847,
          "actual": -0.06,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2021-09-01",
          "pred": -1.115516517648132,
          "actual": -0.5,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2021-12-01",
          "pred": -1.636512986536806,
          "actual": -1.07,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2022-03-01",
          "pred": -1.671559025133907,
          "actual": -0.84,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2022-06-01",
          "pred": -1.0723638957643724,
          "actual": -0.77,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2022-09-01",
          "pred": 0.3378036615688866,
          "actual": -1.06,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2022-12-01",
          "pred": -0.49039816865597524,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2023-03-01",
          "pred": -1.5630865774438376,
          "actual": -0.13,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2023-06-01",
          "pred": -2.2641801896409848,
          "actual": 0.95,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2023-09-01",
          "pred": -0.5655602423497135,
          "actual": 1.65,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2023-12-01",
          "pred": 0.5455040512209958,
          "actual": 1.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2024-03-01",
          "pred": 2.244094040814618,
          "actual": 1.1,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2024-06-01",
          "pred": 2.2556585638224362,
          "actual": 0.25,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2024-09-01",
          "pred": 2.285325570811145,
          "actual": -0.11,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2024-12-01",
          "pred": 0.8290483286953091,
          "actual": -0.58,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2025-03-01",
          "pred": 1.1723720439765208,
          "actual": 0.05,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2025-06-01",
          "pred": 1.5855988226630207,
          "actual": 0.01,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2025-09-01",
          "pred": 1.303240613182152,
          "actual": -0.3,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2025-12-01",
          "pred": 1.2071876671713382,
          "actual": -0.49,
          "persistence": -0.98
        }
      ]
    },
    "state_transition_decoder": {
      "1": [
        {
          "origin": "2006-09-01",
          "date": "2006-10-01",
          "pred": -0.29232649047934545,
          "actual": 0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-01-01",
          "pred": 1.1540302876040096,
          "actual": 0.59,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-04-01",
          "pred": 0.18304189670310095,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-07-01",
          "pred": -0.2386215605095758,
          "actual": -0.37,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-10-01",
          "pred": -0.5979855880430331,
          "actual": -1.41,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-01-01",
          "pred": -1.024624602289004,
          "actual": -1.79,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-04-01",
          "pred": -0.628520269432815,
          "actual": -0.89,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-07-01",
          "pred": -0.465007484385881,
          "actual": -0.04,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-10-01",
          "pred": -0.4680587277523708,
          "actual": -0.3,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-01-01",
          "pred": -0.14699412814163842,
          "actual": -1.0,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-04-01",
          "pred": -0.9660169295811053,
          "actual": -0.25,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-07-01",
          "pred": 0.10879306867363041,
          "actual": 0.69,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-10-01",
          "pred": 0.6429544745741608,
          "actual": 0.96,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-01-01",
          "pred": 1.9186888846790096,
          "actual": 1.43,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-04-01",
          "pred": 0.6997328522229422,
          "actual": 0.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-07-01",
          "pred": -0.6822422063985378,
          "actual": -0.89,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-10-01",
          "pred": -1.259494878623503,
          "actual": -1.65,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-01-01",
          "pred": -1.0012707649976247,
          "actual": -1.7,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-04-01",
          "pred": -1.122867971593352,
          "actual": -0.74,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-07-01",
          "pred": -0.5826206561356189,
          "actual": -0.23,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-10-01",
          "pred": -0.08803534873517714,
          "actual": -0.93,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-01-01",
          "pred": -1.4389138216157866,
          "actual": -0.93,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-04-01",
          "pred": -0.4130174335805644,
          "actual": -0.29,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-07-01",
          "pred": 0.11955436175456165,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-10-01",
          "pred": 1.3185654428045228,
          "actual": 0.23,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-01-01",
          "pred": 0.2454544874147278,
          "actual": -0.42,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-04-01",
          "pred": -0.48807547853780003,
          "actual": -0.08,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-07-01",
          "pred": -0.19422531441040525,
          "actual": -0.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-10-01",
          "pred": -0.31161538027135255,
          "actual": -0.24,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-01-01",
          "pred": -0.141374213160077,
          "actual": -0.42,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-04-01",
          "pred": 0.04249807474424852,
          "actual": 0.28,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-07-01",
          "pred": 0.9395037268807395,
          "actual": 0.13,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-10-01",
          "pred": 0.40948157262627544,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-01-01",
          "pred": 1.0111096743037211,
          "actual": 0.59,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-04-01",
          "pred": 0.18924906886863418,
          "actual": 0.9,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-07-01",
          "pred": 0.9669297896875317,
          "actual": 1.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-10-01",
          "pred": 1.9150531762457947,
          "actual": 2.21,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-01-01",
          "pred": 2.4254907890837867,
          "actual": 2.56,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-04-01",
          "pred": 1.936004464910464,
          "actual": 1.05,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-07-01",
          "pred": 0.13794257516619451,
          "actual": -0.25,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-10-01",
          "pred": -0.7137245895691373,
          "actual": -0.75,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-01-01",
          "pred": -0.03580645823301744,
          "actual": -0.34,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-04-01",
          "pred": -0.18218098005681008,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-07-01",
          "pred": -0.1311871075389013,
          "actual": 0.22,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-10-01",
          "pred": -0.4981790411414901,
          "actual": -0.52,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-01-01",
          "pred": -0.8746791919098028,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-04-01",
          "pred": -0.08591614010345303,
          "actual": -0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-07-01",
          "pred": 0.4014903537017227,
          "actual": 0.27,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-10-01",
          "pred": 0.29056197914623627,
          "actual": 0.84,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-01-01",
          "pred": 0.8679858563503626,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-04-01",
          "pred": -0.2630086867411965,
          "actual": 0.67,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-07-01",
          "pred": 0.39474538264894016,
          "actual": 0.41,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-10-01",
          "pred": 0.03369501426787943,
          "actual": 0.55,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-01-01",
          "pred": 0.736453201667162,
          "actual": 0.64,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-04-01",
          "pred": 0.7028719271261025,
          "actual": 0.49,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-07-01",
          "pred": -0.033276210453589916,
          "actual": -0.04,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-10-01",
          "pred": -0.596632433020601,
          "actual": -1.19,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-01-01",
          "pred": -0.8469800265748443,
          "actual": -1.04,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-04-01",
          "pred": -0.22231923742112064,
          "actual": -0.55,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-07-01",
          "pred": -0.0344759605015639,
          "actual": -0.2,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-10-01",
          "pred": -0.23296740429909252,
          "actual": -0.78,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-01-01",
          "pred": -0.26438484263343637,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-04-01",
          "pred": -0.3575999796808015,
          "actual": -0.9,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-07-01",
          "pred": -0.38574941630168724,
          "actual": -0.56,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-10-01",
          "pred": -0.20462147391153085,
          "actual": -0.99,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-01-01",
          "pred": -0.7126052411594079,
          "actual": -0.78,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-04-01",
          "pred": -0.2480698952106334,
          "actual": 0.24,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-07-01",
          "pred": 0.5525425501878442,
          "actual": 1.2,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-10-01",
          "pred": 1.0735576204625452,
          "actual": 1.59,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-01-01",
          "pred": 1.5019007142714118,
          "actual": 1.71,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-04-01",
          "pred": 0.5989531480238646,
          "actual": 0.93,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-07-01",
          "pred": -0.24289083091118438,
          "actual": 0.2,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-10-01",
          "pred": 0.011855450508506348,
          "actual": -0.24,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-01-01",
          "pred": 0.4028070111572013,
          "actual": -0.76,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-04-01",
          "pred": 0.2831679788419707,
          "actual": -0.08,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-07-01",
          "pred": 0.058792580418428025,
          "actual": -0.03,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-10-01",
          "pred": -0.9057182842919406,
          "actual": -0.5,
          "persistence": -0.3
        }
      ],
      "3": [
        {
          "origin": "2006-09-01",
          "date": "2006-12-01",
          "pred": -0.47451463830811286,
          "actual": 1.1,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-03-01",
          "pred": 0.7607219356441411,
          "actual": -0.15,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-06-01",
          "pred": 0.38136305767671425,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-09-01",
          "pred": -0.15402090472253765,
          "actual": -1.04,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-12-01",
          "pred": 0.08074667568858392,
          "actual": -1.61,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-03-01",
          "pred": -1.3525823245925355,
          "actual": -1.17,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-06-01",
          "pred": -0.14740918368879258,
          "actual": -0.44,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-09-01",
          "pred": 0.08246752281957656,
          "actual": -0.28,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-12-01",
          "pred": -0.9894194851344699,
          "actual": -0.9,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-03-01",
          "pred": -0.6697726796773041,
          "actual": -0.72,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-06-01",
          "pred": -1.0924186867948,
          "actual": 0.49,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-09-01",
          "pred": -0.43416314585555255,
          "actual": 0.68,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-12-01",
          "pred": 0.2923884119703338,
          "actual": 1.81,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-03-01",
          "pred": 0.5908928992413963,
          "actual": 1.07,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-06-01",
          "pred": 0.1346028169434239,
          "actual": -0.62,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-09-01",
          "pred": -0.04674042412742052,
          "actual": -1.56,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-12-01",
          "pred": -0.8718807967507137,
          "actual": -1.63,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-03-01",
          "pred": 0.16777786614272272,
          "actual": -0.98,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-06-01",
          "pred": -0.30253802430546534,
          "actual": -0.25,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-09-01",
          "pred": -0.9831103275115275,
          "actual": -0.76,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-12-01",
          "pred": -0.4166496729943599,
          "actual": -1.05,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-03-01",
          "pred": -1.1583339762262084,
          "actual": -0.48,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-06-01",
          "pred": -0.7019285991686651,
          "actual": 0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-09-01",
          "pred": 0.04065145934824073,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-12-01",
          "pred": -0.32043606599324886,
          "actual": -0.13,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-03-01",
          "pred": -0.5907178090765229,
          "actual": -0.14,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-06-01",
          "pred": -0.897460427861853,
          "actual": -0.33,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-09-01",
          "pred": -0.48287367575590595,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-12-01",
          "pred": -0.20902004843185695,
          "actual": -0.09,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-03-01",
          "pred": 0.13854821095473868,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-06-01",
          "pred": 0.6046336023023651,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-09-01",
          "pred": 0.8444686205001449,
          "actual": 0.37,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-12-01",
          "pred": 0.5634112570713274,
          "actual": 0.77,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-03-01",
          "pred": 1.3729529284681228,
          "actual": 0.48,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-06-01",
          "pred": 0.5245693153047231,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-09-01",
          "pred": 0.5074183078637384,
          "actual": 2.01,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-12-01",
          "pred": 1.8965964567362412,
          "actual": 2.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-03-01",
          "pred": 2.3782910617224964,
          "actual": 1.6,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-06-01",
          "pred": 2.159234565664237,
          "actual": 0.06,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-09-01",
          "pred": 0.38400466471142414,
          "actual": -0.46,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-12-01",
          "pred": -0.7521012050030808,
          "actual": -0.51,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-03-01",
          "pred": -0.24626791990586816,
          "actual": -0.09,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-06-01",
          "pred": -0.0708246567105423,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-09-01",
          "pred": -1.0228007105245467,
          "actual": -0.56,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-12-01",
          "pred": -1.041941260176173,
          "actual": -0.85,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-03-01",
          "pred": -0.6512199974408204,
          "actual": -0.73,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-06-01",
          "pred": 0.7547167043285092,
          "actual": 0.12,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-09-01",
          "pred": 0.7827981543327373,
          "actual": 0.3,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-12-01",
          "pred": 0.6714328908235833,
          "actual": 0.97,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-03-01",
          "pred": 1.273313988767915,
          "actual": 0.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-06-01",
          "pred": 0.0774370052716804,
          "actual": 0.66,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-09-01",
          "pred": -0.032817857861469076,
          "actual": 0.11,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-12-01",
          "pred": 0.36537385437989395,
          "actual": 0.51,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-03-01",
          "pred": 0.3875094608222172,
          "actual": 0.36,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-06-01",
          "pred": 0.46480230914592646,
          "actual": -0.21,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-09-01",
          "pred": 0.030096887233402994,
          "actual": -0.66,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-12-01",
          "pred": -0.5944252911564046,
          "actual": -0.98,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-03-01",
          "pred": -0.2624296187794704,
          "actual": -0.72,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-06-01",
          "pred": -0.44653332900353576,
          "actual": -0.06,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-09-01",
          "pred": -0.5220296516457252,
          "actual": -0.5,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-12-01",
          "pred": -0.6249139235344595,
          "actual": -1.07,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-03-01",
          "pred": -0.28858392342531103,
          "actual": -0.84,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-06-01",
          "pred": -0.04191644185501653,
          "actual": -0.77,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-09-01",
          "pred": 0.541384893885495,
          "actual": -1.06,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-12-01",
          "pred": -0.40780117543516786,
          "actual": -0.86,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-03-01",
          "pred": -0.3534150553201626,
          "actual": -0.13,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-06-01",
          "pred": -0.24934787779744283,
          "actual": 0.95,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-09-01",
          "pred": 0.6998204544995636,
          "actual": 1.65,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-12-01",
          "pred": 0.7867575669363647,
          "actual": 1.81,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-03-01",
          "pred": 0.8019820636506197,
          "actual": 1.1,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-06-01",
          "pred": -0.8955413226892766,
          "actual": 0.25,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-09-01",
          "pred": -0.7909949341325043,
          "actual": -0.11,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-12-01",
          "pred": 0.7491007064769188,
          "actual": -0.58,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-03-01",
          "pred": 0.6070288581008719,
          "actual": 0.05,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-06-01",
          "pred": -0.2931896691335772,
          "actual": 0.01,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-09-01",
          "pred": -0.23592540109453697,
          "actual": -0.3,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-12-01",
          "pred": -1.0369514071912909,
          "actual": -0.49,
          "persistence": -0.3
        }
      ],
      "6": [
        {
          "origin": "2006-09-01",
          "date": "2007-03-01",
          "pred": 0.04902506059578898,
          "actual": -0.15,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-06-01",
          "pred": 0.1292863270567892,
          "actual": -0.16,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-09-01",
          "pred": -0.0061292490234833505,
          "actual": -1.04,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-12-01",
          "pred": 0.24942799979031274,
          "actual": -1.61,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-03-01",
          "pred": -0.04845883071949712,
          "actual": -1.17,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-06-01",
          "pred": -0.7042874909505952,
          "actual": -0.44,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-09-01",
          "pred": -1.369313788139684,
          "actual": -0.28,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-12-01",
          "pred": -0.5979293799538618,
          "actual": -0.9,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-03-01",
          "pred": -0.14426311512112142,
          "actual": -0.72,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-06-01",
          "pred": -1.3647843486220073,
          "actual": 0.49,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-09-01",
          "pred": -0.6454623848544566,
          "actual": 0.68,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-12-01",
          "pred": 0.12765694451957182,
          "actual": 1.81,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-03-01",
          "pred": -0.12800331869401557,
          "actual": 1.07,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-06-01",
          "pred": -0.40196239612318435,
          "actual": -0.62,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-09-01",
          "pred": 0.24195790282217625,
          "actual": -1.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-12-01",
          "pred": 0.26789512345100064,
          "actual": -1.63,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-03-01",
          "pred": 0.04596335868144297,
          "actual": -0.98,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-06-01",
          "pred": -0.481263106389756,
          "actual": -0.25,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-09-01",
          "pred": -0.8977204076623664,
          "actual": -0.76,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-12-01",
          "pred": -1.0216322636114892,
          "actual": -1.05,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-03-01",
          "pred": -0.8911435697362153,
          "actual": -0.48,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-06-01",
          "pred": -0.723772984668785,
          "actual": 0.14,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-09-01",
          "pred": -0.6088569414768333,
          "actual": 0.44,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-12-01",
          "pred": -0.9294215767124142,
          "actual": -0.13,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-03-01",
          "pred": -1.6069676156930222,
          "actual": -0.14,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-06-01",
          "pred": -1.6198099336428105,
          "actual": -0.33,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-09-01",
          "pred": -0.692349974195654,
          "actual": -0.09,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-12-01",
          "pred": -0.5585371419561999,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-03-01",
          "pred": -0.7775625350995949,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-06-01",
          "pred": -0.346703029356765,
          "actual": 0.48,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-09-01",
          "pred": 0.6252950717140215,
          "actual": 0.37,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-12-01",
          "pred": 1.1217314428809044,
          "actual": 0.77,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-03-01",
          "pred": 0.23240713786061235,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-06-01",
          "pred": 0.7634852232504183,
          "actual": 1.28,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-09-01",
          "pred": 0.6563801058566459,
          "actual": 2.01,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-12-01",
          "pred": 1.1724015663915321,
          "actual": 2.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-03-01",
          "pred": 2.021279380805736,
          "actual": 1.6,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-06-01",
          "pred": 2.360360314958574,
          "actual": 0.06,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-09-01",
          "pred": 1.6842298252440158,
          "actual": -0.46,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-12-01",
          "pred": 0.5868293696898054,
          "actual": -0.51,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-03-01",
          "pred": 0.10801767823067178,
          "actual": -0.09,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-06-01",
          "pred": 1.081112983768656,
          "actual": 0.22,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-09-01",
          "pred": 0.4036166442475258,
          "actual": -0.56,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-12-01",
          "pred": -0.351073985256154,
          "actual": -0.85,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-03-01",
          "pred": -0.4744958217078862,
          "actual": -0.73,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-06-01",
          "pred": -0.12886593026975102,
          "actual": 0.12,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-09-01",
          "pred": 0.6586720158730223,
          "actual": 0.3,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-12-01",
          "pred": 0.7944996085203493,
          "actual": 0.97,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-03-01",
          "pred": 0.2358460468421443,
          "actual": 0.81,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-06-01",
          "pred": 1.1506703252232608,
          "actual": 0.66,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-09-01",
          "pred": -0.09461189925271647,
          "actual": 0.11,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-12-01",
          "pred": -0.22135005621576154,
          "actual": 0.51,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-03-01",
          "pred": 0.18510976453795783,
          "actual": 0.36,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-06-01",
          "pred": 0.4137942698182253,
          "actual": -0.21,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-09-01",
          "pred": 0.45182412898191576,
          "actual": -0.66,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-12-01",
          "pred": -0.4761844426172463,
          "actual": -0.98,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-03-01",
          "pred": -1.0720177210982533,
          "actual": -0.72,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-06-01",
          "pred": -0.10532914278535563,
          "actual": -0.06,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-09-01",
          "pred": 0.680918664297481,
          "actual": -0.5,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-12-01",
          "pred": -0.1396312813067179,
          "actual": -1.07,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-03-01",
          "pred": -0.2655512246925894,
          "actual": -0.84,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-06-01",
          "pred": 0.2583602362789267,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-09-01",
          "pred": -0.24461980174268363,
          "actual": -1.06,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-12-01",
          "pred": -0.6978403274303365,
          "actual": -0.86,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-03-01",
          "pred": -1.7809802960503263,
          "actual": -0.13,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-06-01",
          "pred": -0.8146468712893894,
          "actual": 0.95,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-09-01",
          "pred": -0.394088331521273,
          "actual": 1.65,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-12-01",
          "pred": 0.9821109183573732,
          "actual": 1.81,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-03-01",
          "pred": 0.5715376796303113,
          "actual": 1.1,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-06-01",
          "pred": 0.3313710590882088,
          "actual": 0.25,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-09-01",
          "pred": -0.8418784788824043,
          "actual": -0.11,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-12-01",
          "pred": -0.24198712047313606,
          "actual": -0.58,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-03-01",
          "pred": 0.7486580807496013,
          "actual": 0.05,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-06-01",
          "pred": 0.8371436598672728,
          "actual": 0.01,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-09-01",
          "pred": -0.8336851555744543,
          "actual": -0.3,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-12-01",
          "pred": -0.6371737221247346,
          "actual": -0.49,
          "persistence": 0.01
        }
      ],
      "12": [
        {
          "origin": "2006-09-01",
          "date": "2007-09-01",
          "pred": 1.1206592526512569,
          "actual": -1.04,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-12-01",
          "pred": 1.1587981594770407,
          "actual": -1.61,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2008-03-01",
          "pred": 0.2612094885641851,
          "actual": -1.17,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2008-06-01",
          "pred": 0.4069645676293327,
          "actual": -0.44,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-09-01",
          "pred": 1.277124660376843,
          "actual": -0.28,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-12-01",
          "pred": 0.4212131044305959,
          "actual": -0.9,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2009-03-01",
          "pred": 0.18012977983672115,
          "actual": -0.72,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2009-06-01",
          "pred": 0.30799770505719576,
          "actual": 0.49,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-09-01",
          "pred": 0.0010776365454111675,
          "actual": 0.68,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-12-01",
          "pred": -0.37244831188652755,
          "actual": 1.81,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2010-03-01",
          "pred": -0.3805374147128807,
          "actual": 1.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2010-06-01",
          "pred": -0.4798306800828581,
          "actual": -0.62,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-09-01",
          "pred": -0.15756850223743035,
          "actual": -1.56,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-12-01",
          "pred": 0.09460056632301221,
          "actual": -1.63,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2011-03-01",
          "pred": 0.1382578209778043,
          "actual": -0.98,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2011-06-01",
          "pred": -0.20314950404286436,
          "actual": -0.25,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-09-01",
          "pred": -0.6496223839608768,
          "actual": -0.76,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-12-01",
          "pred": -1.049641150695413,
          "actual": -1.05,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2012-03-01",
          "pred": -1.2692524739252153,
          "actual": -0.48,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2012-06-01",
          "pred": -1.2715781581535612,
          "actual": 0.14,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-09-01",
          "pred": -1.5304241155299056,
          "actual": 0.44,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-12-01",
          "pred": -0.9786441273832944,
          "actual": -0.13,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2013-03-01",
          "pred": -0.5456600197211094,
          "actual": -0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2013-06-01",
          "pred": -0.5114002028936743,
          "actual": -0.33,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-09-01",
          "pred": -0.9920428113821225,
          "actual": -0.09,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-12-01",
          "pred": -1.3122923437786491,
          "actual": -0.09,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2014-03-01",
          "pred": -1.0818189794407083,
          "actual": -0.07,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2014-06-01",
          "pred": -1.118160262747296,
          "actual": 0.48,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-09-01",
          "pred": -0.29546087181765324,
          "actual": 0.37,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-12-01",
          "pred": -0.40179147737678766,
          "actual": 0.77,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2015-03-01",
          "pred": -0.30772018167791104,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2015-06-01",
          "pred": -1.2311026007833137,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-09-01",
          "pred": -0.5027347125064775,
          "actual": 2.01,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-12-01",
          "pred": -0.8281620927194149,
          "actual": 2.56,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2016-03-01",
          "pred": -0.7251604410491133,
          "actual": 1.6,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2016-06-01",
          "pred": -0.38266358995250765,
          "actual": 0.06,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-09-01",
          "pred": 0.27539172517356225,
          "actual": -0.46,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-12-01",
          "pred": -0.45135481436313546,
          "actual": -0.51,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2017-03-01",
          "pred": -0.5585273619860144,
          "actual": -0.09,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2017-06-01",
          "pred": -0.5201853861457233,
          "actual": 0.22,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-09-01",
          "pred": -0.8599149432472092,
          "actual": -0.56,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-12-01",
          "pred": -0.3942887619695682,
          "actual": -0.85,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2018-03-01",
          "pred": 0.012114751876175594,
          "actual": -0.73,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2018-06-01",
          "pred": 1.0984171802488738,
          "actual": 0.12,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-09-01",
          "pred": 1.9229368146829207,
          "actual": 0.3,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-12-01",
          "pred": 1.3413767650932082,
          "actual": 0.97,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2019-03-01",
          "pred": 1.2512184725907314,
          "actual": 0.81,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2019-06-01",
          "pred": 1.8930461289383627,
          "actual": 0.66,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-09-01",
          "pred": 0.3877104602488138,
          "actual": 0.11,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-12-01",
          "pred": 0.23263471526424806,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2020-03-01",
          "pred": -0.09834311685344063,
          "actual": 0.36,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2020-06-01",
          "pred": 0.8250691355142494,
          "actual": -0.21,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-09-01",
          "pred": 0.16400987986734392,
          "actual": -0.66,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-12-01",
          "pred": -0.5489940022092354,
          "actual": -0.98,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2021-03-01",
          "pred": 0.33378298086839553,
          "actual": -0.72,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2021-06-01",
          "pred": 0.9645142224077335,
          "actual": -0.06,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-09-01",
          "pred": 1.6339912145071351,
          "actual": -0.5,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-12-01",
          "pred": 1.0186068284634167,
          "actual": -1.07,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2022-03-01",
          "pred": 1.3331404553905695,
          "actual": -0.84,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2022-06-01",
          "pred": 1.244173222529087,
          "actual": -0.77,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-09-01",
          "pred": 1.1282240622327135,
          "actual": -1.06,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-12-01",
          "pred": 0.33036815076508425,
          "actual": -0.86,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2023-03-01",
          "pred": 0.013345405428784055,
          "actual": -0.13,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2023-06-01",
          "pred": -0.4946665179734554,
          "actual": 0.95,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-09-01",
          "pred": -0.10010361416726334,
          "actual": 1.65,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-12-01",
          "pred": -0.7659403145915243,
          "actual": 1.81,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2024-03-01",
          "pred": -1.3718278974124356,
          "actual": 1.1,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2024-06-01",
          "pred": -1.125529965099143,
          "actual": 0.25,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-09-01",
          "pred": -1.0292042569807083,
          "actual": -0.11,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-12-01",
          "pred": -0.3629780003048181,
          "actual": -0.58,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2025-03-01",
          "pred": -0.4387387313773947,
          "actual": 0.05,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2025-06-01",
          "pred": 0.4370334203405858,
          "actual": 0.01,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-09-01",
          "pred": -0.18967720355975734,
          "actual": -0.3,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-12-01",
          "pred": -0.5515876382639767,
          "actual": -0.49,
          "persistence": -0.58
        }
      ],
      "24": [
        {
          "origin": "2006-09-01",
          "date": "2008-09-01",
          "pred": 1.0165587913071357,
          "actual": -0.28,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2008-12-01",
          "pred": 1.0813205439557072,
          "actual": -0.9,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2009-03-01",
          "pred": 0.45188621387644873,
          "actual": -0.72,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2009-06-01",
          "pred": -0.31992578762381235,
          "actual": 0.49,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2009-09-01",
          "pred": -0.473616478076259,
          "actual": 0.68,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2009-12-01",
          "pred": -0.9326161607096938,
          "actual": 1.81,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2010-03-01",
          "pred": -1.991346056197876,
          "actual": 1.07,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2010-06-01",
          "pred": -1.9056144661780638,
          "actual": -0.62,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2010-09-01",
          "pred": -0.8632840485945634,
          "actual": -1.56,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2010-12-01",
          "pred": -1.2546474130060783,
          "actual": -1.63,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2011-03-01",
          "pred": -2.131250764593041,
          "actual": -0.98,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2011-06-01",
          "pred": -0.21426696727418432,
          "actual": -0.25,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2011-09-01",
          "pred": 0.18123709378783476,
          "actual": -0.76,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2011-12-01",
          "pred": 0.8313881440371582,
          "actual": -1.05,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2012-03-01",
          "pred": -0.11137854726765868,
          "actual": -0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2012-06-01",
          "pred": 0.8307630756138,
          "actual": 0.14,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2012-09-01",
          "pred": 0.5195147091311738,
          "actual": 0.44,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2012-12-01",
          "pred": 0.6438963903521552,
          "actual": -0.13,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2013-03-01",
          "pred": -0.12733164839149305,
          "actual": -0.14,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2013-06-01",
          "pred": -1.476038399395457,
          "actual": -0.33,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2013-09-01",
          "pred": -0.8901047118347233,
          "actual": -0.09,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2013-12-01",
          "pred": -0.8641695988259607,
          "actual": -0.09,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2014-03-01",
          "pred": -0.31163842040153,
          "actual": -0.07,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2014-06-01",
          "pred": -1.0784328187311119,
          "actual": 0.48,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2014-09-01",
          "pred": 0.14734969652949387,
          "actual": 0.37,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2014-12-01",
          "pred": 0.4259705675932116,
          "actual": 0.77,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2015-03-01",
          "pred": 0.436874851951448,
          "actual": 0.48,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2015-06-01",
          "pred": 1.3194589485251533,
          "actual": 1.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2015-09-01",
          "pred": 0.34153832200886414,
          "actual": 2.01,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2015-12-01",
          "pred": 0.9392897512287615,
          "actual": 2.56,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2016-03-01",
          "pred": 0.3783547498734932,
          "actual": 1.6,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2016-06-01",
          "pred": 0.641490876005692,
          "actual": 0.06,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2016-09-01",
          "pred": -0.7156966914422885,
          "actual": -0.46,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2016-12-01",
          "pred": -0.013501071665082867,
          "actual": -0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2017-03-01",
          "pred": -0.45231043570108953,
          "actual": -0.09,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2017-06-01",
          "pred": -0.3629834375559021,
          "actual": 0.22,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2017-09-01",
          "pred": -0.5066368871077923,
          "actual": -0.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2017-12-01",
          "pred": 0.5286186112540818,
          "actual": -0.85,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2018-03-01",
          "pred": 0.6160709126685809,
          "actual": -0.73,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2018-06-01",
          "pred": 0.2308077767939958,
          "actual": 0.12,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2018-09-01",
          "pred": 0.9477506886614365,
          "actual": 0.3,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2018-12-01",
          "pred": -0.2512640330855348,
          "actual": 0.97,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2019-03-01",
          "pred": 0.30084183451023044,
          "actual": 0.81,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2019-06-01",
          "pred": 0.14276571346502293,
          "actual": 0.66,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2019-09-01",
          "pred": 0.43750012579325787,
          "actual": 0.11,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2019-12-01",
          "pred": 0.33007349170370204,
          "actual": 0.51,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2020-03-01",
          "pred": 0.5334578879581896,
          "actual": 0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2020-06-01",
          "pred": 0.6427731164599927,
          "actual": -0.21,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2020-09-01",
          "pred": 0.06510607293527967,
          "actual": -0.66,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2020-12-01",
          "pred": 0.2921663917693004,
          "actual": -0.98,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2021-03-01",
          "pred": -0.2603776621798544,
          "actual": -0.72,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2021-06-01",
          "pred": 0.47077397286551265,
          "actual": -0.06,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2021-09-01",
          "pred": 0.9322953692148134,
          "actual": -0.5,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2021-12-01",
          "pred": -0.29313373618954636,
          "actual": -1.07,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2022-03-01",
          "pred": -1.421152378157963,
          "actual": -0.84,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2022-06-01",
          "pred": -1.1668523550808705,
          "actual": -0.77,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2022-09-01",
          "pred": -0.263906466654213,
          "actual": -1.06,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2022-12-01",
          "pred": -0.7529585430512048,
          "actual": -0.86,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2023-03-01",
          "pred": -0.5487998398754687,
          "actual": -0.13,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2023-06-01",
          "pred": -0.7465624247621403,
          "actual": 0.95,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2023-09-01",
          "pred": -0.8518484693182193,
          "actual": 1.65,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2023-12-01",
          "pred": -1.6362914458666442,
          "actual": 1.81,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2024-03-01",
          "pred": -1.2523154136650698,
          "actual": 1.1,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2024-06-01",
          "pred": -1.010960621875355,
          "actual": 0.25,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2024-09-01",
          "pred": -0.863390632209888,
          "actual": -0.11,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2024-12-01",
          "pred": 0.5071944718912953,
          "actual": -0.58,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2025-03-01",
          "pred": 0.4096300646614069,
          "actual": 0.05,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2025-06-01",
          "pred": 1.2257831461539432,
          "actual": 0.01,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2025-09-01",
          "pred": 1.5528341462717208,
          "actual": -0.3,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2025-12-01",
          "pred": 0.58945448182083,
          "actual": -0.49,
          "persistence": 1.81
        }
      ],
      "60": [
        {
          "origin": "2006-09-01",
          "date": "2011-09-01",
          "pred": -0.5830379028520672,
          "actual": -0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2011-12-01",
          "pred": -0.17316099655614714,
          "actual": -1.05,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2012-03-01",
          "pred": -0.07300996912037584,
          "actual": -0.48,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2012-06-01",
          "pred": -0.7343074601388901,
          "actual": 0.14,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2012-09-01",
          "pred": -0.3166910319873067,
          "actual": 0.44,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2012-12-01",
          "pred": -0.9698029487839,
          "actual": -0.13,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2013-03-01",
          "pred": -0.8741295822875967,
          "actual": -0.14,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2013-06-01",
          "pred": -0.17932528464112957,
          "actual": -0.33,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2013-09-01",
          "pred": -1.0297196899593977,
          "actual": -0.09,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2013-12-01",
          "pred": -0.3995509939939524,
          "actual": -0.09,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2014-03-01",
          "pred": -0.4597361835488446,
          "actual": -0.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2014-06-01",
          "pred": -0.40553305404746576,
          "actual": 0.48,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2014-09-01",
          "pred": 0.12344893095021298,
          "actual": 0.37,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2014-12-01",
          "pred": 1.0432116925638377,
          "actual": 0.77,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2015-03-01",
          "pred": 1.0133673768262699,
          "actual": 0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2015-06-01",
          "pred": 0.39898912367411643,
          "actual": 1.28,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2015-09-01",
          "pred": -0.3947615691833059,
          "actual": 2.01,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2015-12-01",
          "pred": -0.2906123983572994,
          "actual": 2.56,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2016-03-01",
          "pred": 0.47307053905068874,
          "actual": 1.6,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2016-06-01",
          "pred": 0.47681285253367095,
          "actual": 0.06,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2016-09-01",
          "pred": 1.4426001237114712,
          "actual": -0.46,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2016-12-01",
          "pred": 0.9604308335707306,
          "actual": -0.51,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2017-03-01",
          "pred": 1.23926539313117,
          "actual": -0.09,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2017-06-01",
          "pred": 1.2353453474638678,
          "actual": 0.22,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2017-09-01",
          "pred": 1.1327730482933736,
          "actual": -0.56,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2017-12-01",
          "pred": 0.013186179696099101,
          "actual": -0.85,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2018-03-01",
          "pred": -0.18326418899241187,
          "actual": -0.73,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2018-06-01",
          "pred": -0.14530259983827187,
          "actual": 0.12,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2018-09-01",
          "pred": 0.079372425624833,
          "actual": 0.3,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2018-12-01",
          "pred": 0.1367658541266601,
          "actual": 0.97,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2019-03-01",
          "pred": -0.330938919690796,
          "actual": 0.81,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2019-06-01",
          "pred": 0.267762650765191,
          "actual": 0.66,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2019-09-01",
          "pred": 0.8427207780014111,
          "actual": 0.11,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2019-12-01",
          "pred": 0.8851914343078987,
          "actual": 0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2020-03-01",
          "pred": 0.7587455599154036,
          "actual": 0.36,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2020-06-01",
          "pred": 1.3464947105672713,
          "actual": -0.21,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2020-09-01",
          "pred": 1.3702584005548133,
          "actual": -0.66,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2020-12-01",
          "pred": 1.5013457421634389,
          "actual": -0.98,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2021-03-01",
          "pred": 1.5322070766080242,
          "actual": -0.72,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2021-06-01",
          "pred": 2.057898144972913,
          "actual": -0.06,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2021-09-01",
          "pred": 1.8613756423564165,
          "actual": -0.5,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2021-12-01",
          "pred": 0.9362325312845184,
          "actual": -1.07,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2022-03-01",
          "pred": -0.1966713628083299,
          "actual": -0.84,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2022-06-01",
          "pred": -0.2112813947626578,
          "actual": -0.77,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2022-09-01",
          "pred": -0.037681744899876295,
          "actual": -1.06,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2022-12-01",
          "pred": 0.5251139007416179,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2023-03-01",
          "pred": 0.8247558861263462,
          "actual": -0.13,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2023-06-01",
          "pred": 1.5051789109251916,
          "actual": 0.95,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2023-09-01",
          "pred": 1.4340827503936135,
          "actual": 1.65,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2023-12-01",
          "pred": 1.4511366658906701,
          "actual": 1.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2024-03-01",
          "pred": 2.1287703171284,
          "actual": 1.1,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2024-06-01",
          "pred": 2.023284348128439,
          "actual": 0.25,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2024-09-01",
          "pred": 2.163344634340829,
          "actual": -0.11,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2024-12-01",
          "pred": 2.3270273023811616,
          "actual": -0.58,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2025-03-01",
          "pred": 2.1379712925577397,
          "actual": 0.05,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2025-06-01",
          "pred": 2.1314033180324956,
          "actual": 0.01,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2025-09-01",
          "pred": 2.2152014636258675,
          "actual": -0.3,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2025-12-01",
          "pred": 2.102027824000795,
          "actual": -0.49,
          "persistence": -0.98
        }
      ]
    },
    "state_transition_decoder_current": {
      "1": [
        {
          "origin": "2006-09-01",
          "date": "2006-10-01",
          "pred": -0.16060512421983886,
          "actual": 0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-01-01",
          "pred": 1.2360920785007308,
          "actual": 0.59,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-04-01",
          "pred": 0.12865158269014193,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-07-01",
          "pred": -0.3820380518670958,
          "actual": -0.37,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-10-01",
          "pred": -0.896552498209445,
          "actual": -1.41,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-01-01",
          "pred": -1.1997692975161056,
          "actual": -1.79,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-04-01",
          "pred": -0.8177670357448843,
          "actual": -0.89,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-07-01",
          "pred": -0.34655028467292776,
          "actual": -0.04,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-10-01",
          "pred": -0.42532649620676033,
          "actual": -0.3,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-01-01",
          "pred": -0.6679262997145337,
          "actual": -1.0,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-04-01",
          "pred": -1.0244983392321203,
          "actual": -0.25,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-07-01",
          "pred": 0.19428990275581143,
          "actual": 0.69,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-10-01",
          "pred": 0.6578690558280941,
          "actual": 0.96,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-01-01",
          "pred": 1.786909353009101,
          "actual": 1.43,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-04-01",
          "pred": 0.6090730152381554,
          "actual": 0.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-07-01",
          "pred": -0.6220439891766121,
          "actual": -0.89,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-10-01",
          "pred": -1.3718244872559842,
          "actual": -1.65,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-01-01",
          "pred": -1.0902146079183417,
          "actual": -1.7,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-04-01",
          "pred": -0.9894214739008347,
          "actual": -0.74,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-07-01",
          "pred": -0.3508557644600443,
          "actual": -0.23,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-10-01",
          "pred": -0.321028393656071,
          "actual": -0.93,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-01-01",
          "pred": -1.41147588716167,
          "actual": -0.93,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-04-01",
          "pred": -0.41172328444376405,
          "actual": -0.29,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-07-01",
          "pred": 0.2312924511277918,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-10-01",
          "pred": 1.020148091295141,
          "actual": 0.23,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-01-01",
          "pred": 0.272830580132554,
          "actual": -0.42,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-04-01",
          "pred": -0.35291201564284064,
          "actual": -0.08,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-07-01",
          "pred": -0.1944110176518511,
          "actual": -0.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-10-01",
          "pred": -0.24734419439428895,
          "actual": -0.24,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-01-01",
          "pred": -0.040852343939983035,
          "actual": -0.42,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-04-01",
          "pred": 0.12114084144683451,
          "actual": 0.28,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-07-01",
          "pred": 0.8143568520299808,
          "actual": 0.13,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-10-01",
          "pred": 0.40122119706332143,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-01-01",
          "pred": 1.0288989671606343,
          "actual": 0.59,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-04-01",
          "pred": 0.25815448592109047,
          "actual": 0.9,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-07-01",
          "pred": 1.1169502955041173,
          "actual": 1.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-10-01",
          "pred": 2.0068316033285143,
          "actual": 2.21,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-01-01",
          "pred": 2.479344055582578,
          "actual": 2.56,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-04-01",
          "pred": 1.8052419207654358,
          "actual": 1.05,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-07-01",
          "pred": -0.005636534891865757,
          "actual": -0.25,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-10-01",
          "pred": -0.5986040030191102,
          "actual": -0.75,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-01-01",
          "pred": -0.05658422508878891,
          "actual": -0.34,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-04-01",
          "pred": -0.1705940923941594,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-07-01",
          "pred": -0.036852357595608405,
          "actual": 0.22,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-10-01",
          "pred": -0.6765379420278385,
          "actual": -0.52,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-01-01",
          "pred": -0.8313411220949065,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-04-01",
          "pred": -0.41232712176626246,
          "actual": -0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-07-01",
          "pred": 0.5243465983637773,
          "actual": 0.27,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-10-01",
          "pred": 0.3441480318704327,
          "actual": 0.84,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-01-01",
          "pred": 0.8728420969047861,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-04-01",
          "pred": 0.008309943575489072,
          "actual": 0.67,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-07-01",
          "pred": 0.42854603097999017,
          "actual": 0.41,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-10-01",
          "pred": 0.050684929488973754,
          "actual": 0.55,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-01-01",
          "pred": 0.4894792194241288,
          "actual": 0.64,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-04-01",
          "pred": 0.6490364574593123,
          "actual": 0.49,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-07-01",
          "pred": -0.10851301682873518,
          "actual": -0.04,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-10-01",
          "pred": -0.7618844403542023,
          "actual": -1.19,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-01-01",
          "pred": -0.8971169922562423,
          "actual": -1.04,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-04-01",
          "pred": -0.48948895079469007,
          "actual": -0.55,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-07-01",
          "pred": -0.05273496968895148,
          "actual": -0.2,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-10-01",
          "pred": -0.3018044814471249,
          "actual": -0.78,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-01-01",
          "pred": -0.4872024300829467,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-04-01",
          "pred": -0.48446327529571087,
          "actual": -0.9,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-07-01",
          "pred": -0.7281298438263156,
          "actual": -0.56,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-10-01",
          "pred": -0.517748574340107,
          "actual": -0.99,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-01-01",
          "pred": -0.5906174366263555,
          "actual": -0.78,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-04-01",
          "pred": -0.20187302761151948,
          "actual": 0.24,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-07-01",
          "pred": 0.6817816290226353,
          "actual": 1.2,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-10-01",
          "pred": 1.3919197181591643,
          "actual": 1.59,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-01-01",
          "pred": 1.488612515735839,
          "actual": 1.71,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-04-01",
          "pred": 0.6196195743059726,
          "actual": 0.93,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-07-01",
          "pred": -0.166868986314685,
          "actual": 0.2,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-10-01",
          "pred": 0.1368626977362562,
          "actual": -0.24,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-01-01",
          "pred": 0.168856130785987,
          "actual": -0.76,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-04-01",
          "pred": 0.20817377116698346,
          "actual": -0.08,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-07-01",
          "pred": 0.0366521421036738,
          "actual": -0.03,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-10-01",
          "pred": -0.7143984969481696,
          "actual": -0.5,
          "persistence": -0.3
        }
      ],
      "3": [
        {
          "origin": "2006-09-01",
          "date": "2006-12-01",
          "pred": -0.5525055526987251,
          "actual": 1.1,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-03-01",
          "pred": 0.8782807518783744,
          "actual": -0.15,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-06-01",
          "pred": 0.30456258977075223,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-09-01",
          "pred": -0.08261805169746136,
          "actual": -1.04,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-12-01",
          "pred": -0.1401825910435311,
          "actual": -1.61,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-03-01",
          "pred": -1.3609325323486618,
          "actual": -1.17,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-06-01",
          "pred": -0.3163534999449776,
          "actual": -0.44,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-09-01",
          "pred": 0.08504329476523409,
          "actual": -0.28,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-12-01",
          "pred": -0.887327321896941,
          "actual": -0.9,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-03-01",
          "pred": -0.807241010942922,
          "actual": -0.72,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-06-01",
          "pred": -1.0791441499145724,
          "actual": 0.49,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-09-01",
          "pred": -0.17536480054954803,
          "actual": 0.68,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-12-01",
          "pred": 0.3575597071098269,
          "actual": 1.81,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-03-01",
          "pred": 0.5671331335772636,
          "actual": 1.07,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-06-01",
          "pred": 0.2037000519029547,
          "actual": -0.62,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-09-01",
          "pred": 0.09520224119902039,
          "actual": -1.56,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-12-01",
          "pred": -1.0860762536428454,
          "actual": -1.63,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-03-01",
          "pred": -0.02230777639181128,
          "actual": -0.98,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-06-01",
          "pred": -0.33058122471094253,
          "actual": -0.25,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-09-01",
          "pred": -0.6279968129904476,
          "actual": -0.76,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-12-01",
          "pred": -0.5510374661151143,
          "actual": -1.05,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-03-01",
          "pred": -1.167120304785232,
          "actual": -0.48,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-06-01",
          "pred": -0.5998406403007102,
          "actual": 0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-09-01",
          "pred": 0.05896198241093191,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-12-01",
          "pred": -0.514449362844073,
          "actual": -0.13,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-03-01",
          "pred": -0.647861322794057,
          "actual": -0.14,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-06-01",
          "pred": -0.9547011741007758,
          "actual": -0.33,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-09-01",
          "pred": -0.48610462951004424,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-12-01",
          "pred": -0.19901383536424722,
          "actual": -0.09,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-03-01",
          "pred": 0.2547566221057662,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-06-01",
          "pred": 0.7617573247504776,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-09-01",
          "pred": 0.7292529654833203,
          "actual": 0.37,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-12-01",
          "pred": 0.4846129833724138,
          "actual": 0.77,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-03-01",
          "pred": 1.2897366811333848,
          "actual": 0.48,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-06-01",
          "pred": 0.5990782769599439,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-09-01",
          "pred": 0.6517420222715034,
          "actual": 2.01,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-12-01",
          "pred": 1.9715289507672231,
          "actual": 2.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-03-01",
          "pred": 2.352591925328432,
          "actual": 1.6,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-06-01",
          "pred": 2.140679374997753,
          "actual": 0.06,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-09-01",
          "pred": 0.22124598899088027,
          "actual": -0.46,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-12-01",
          "pred": -0.7542962933090821,
          "actual": -0.51,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-03-01",
          "pred": -0.054659827310163195,
          "actual": -0.09,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-06-01",
          "pred": -0.09345713378609578,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-09-01",
          "pred": -0.8932334201337159,
          "actual": -0.56,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-12-01",
          "pred": -1.1928374755211173,
          "actual": -0.85,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-03-01",
          "pred": -0.6488316215266968,
          "actual": -0.73,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-06-01",
          "pred": 0.47363945702147187,
          "actual": 0.12,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-09-01",
          "pred": 0.68735042865832,
          "actual": 0.3,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-12-01",
          "pred": 0.7548655151753024,
          "actual": 0.97,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-03-01",
          "pred": 1.4155577141475086,
          "actual": 0.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-06-01",
          "pred": 0.11639811900411826,
          "actual": 0.66,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-09-01",
          "pred": 0.09061704068765446,
          "actual": 0.11,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-12-01",
          "pred": 0.40006167895523964,
          "actual": 0.51,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-03-01",
          "pred": 0.4096253637402552,
          "actual": 0.36,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-06-01",
          "pred": 0.48181347774427474,
          "actual": -0.21,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-09-01",
          "pred": -0.10713016543340745,
          "actual": -0.66,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-12-01",
          "pred": -0.7131137276532024,
          "actual": -0.98,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-03-01",
          "pred": -0.3786958306132875,
          "actual": -0.72,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-06-01",
          "pred": -0.5031509792274219,
          "actual": -0.06,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-09-01",
          "pred": -0.5429467920014253,
          "actual": -0.5,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-12-01",
          "pred": -0.6918846941981203,
          "actual": -1.07,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-03-01",
          "pred": -0.6491362963199317,
          "actual": -0.84,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-06-01",
          "pred": 0.02772612587727321,
          "actual": -0.77,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-09-01",
          "pred": 0.6783662410022143,
          "actual": -1.06,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-12-01",
          "pred": -0.7944081592963735,
          "actual": -0.86,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-03-01",
          "pred": -0.49670112655617193,
          "actual": -0.13,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-06-01",
          "pred": -0.0776645041126525,
          "actual": 0.95,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-09-01",
          "pred": 0.7594914030732864,
          "actual": 1.65,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-12-01",
          "pred": 1.1632477499651697,
          "actual": 1.81,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-03-01",
          "pred": 0.7697802158202139,
          "actual": 1.1,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-06-01",
          "pred": -0.8779356558914232,
          "actual": 0.25,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-09-01",
          "pred": -0.8317891633496304,
          "actual": -0.11,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-12-01",
          "pred": 0.6739062973478998,
          "actual": -0.58,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-03-01",
          "pred": 0.31448434950131726,
          "actual": 0.05,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-06-01",
          "pred": -0.4640820379951247,
          "actual": 0.01,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-09-01",
          "pred": -0.3533181329862118,
          "actual": -0.3,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-12-01",
          "pred": -0.7650946585989745,
          "actual": -0.49,
          "persistence": -0.3
        }
      ],
      "6": [
        {
          "origin": "2006-09-01",
          "date": "2007-03-01",
          "pred": 0.10951943612158406,
          "actual": -0.15,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-06-01",
          "pred": 0.0479750496541541,
          "actual": -0.16,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-09-01",
          "pred": 0.0557211756750446,
          "actual": -1.04,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-12-01",
          "pred": 0.25934234313053656,
          "actual": -1.61,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-03-01",
          "pred": 0.03230137043202539,
          "actual": -1.17,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-06-01",
          "pred": -0.580342419923235,
          "actual": -0.44,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-09-01",
          "pred": -1.1742442946865623,
          "actual": -0.28,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-12-01",
          "pred": -0.675194667664624,
          "actual": -0.9,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-03-01",
          "pred": -0.30005515220709245,
          "actual": -0.72,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-06-01",
          "pred": -1.2766284125185123,
          "actual": 0.49,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-09-01",
          "pred": -0.5682361948037021,
          "actual": 0.68,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-12-01",
          "pred": -0.09612370052740066,
          "actual": 1.81,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-03-01",
          "pred": -0.3701297461098276,
          "actual": 1.07,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-06-01",
          "pred": -0.3595034450520015,
          "actual": -0.62,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-09-01",
          "pred": 0.26104846349712807,
          "actual": -1.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-12-01",
          "pred": 0.4866199961617174,
          "actual": -1.63,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-03-01",
          "pred": 0.12473403343544745,
          "actual": -0.98,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-06-01",
          "pred": -0.4356137347189326,
          "actual": -0.25,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-09-01",
          "pred": -0.8385249399395791,
          "actual": -0.76,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-12-01",
          "pred": -1.072184319980264,
          "actual": -1.05,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-03-01",
          "pred": -0.8807300749774151,
          "actual": -0.48,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-06-01",
          "pred": -0.6908633785839908,
          "actual": 0.14,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-09-01",
          "pred": -0.6700638164440331,
          "actual": 0.44,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-12-01",
          "pred": -0.965160703061759,
          "actual": -0.13,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-03-01",
          "pred": -1.5838194704804944,
          "actual": -0.14,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-06-01",
          "pred": -1.6303623335978414,
          "actual": -0.33,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-09-01",
          "pred": -0.7981959349436767,
          "actual": -0.09,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-12-01",
          "pred": -0.4521349835494092,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-03-01",
          "pred": -0.826683767624619,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-06-01",
          "pred": -0.44720298448383644,
          "actual": 0.48,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-09-01",
          "pred": 0.5774352610436871,
          "actual": 0.37,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-12-01",
          "pred": 1.1596668157290062,
          "actual": 0.77,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-03-01",
          "pred": 0.201903552387727,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-06-01",
          "pred": 0.8916200075366817,
          "actual": 1.28,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-09-01",
          "pred": 0.522471417072166,
          "actual": 2.01,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-12-01",
          "pred": 1.0860798932500346,
          "actual": 2.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-03-01",
          "pred": 2.1758218543798584,
          "actual": 1.6,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-06-01",
          "pred": 2.3483878239189004,
          "actual": 0.06,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-09-01",
          "pred": 1.6477547966682584,
          "actual": -0.46,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-12-01",
          "pred": 0.554227441468575,
          "actual": -0.51,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-03-01",
          "pred": 0.08935395141955703,
          "actual": -0.09,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-06-01",
          "pred": 1.0802561441151155,
          "actual": 0.22,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-09-01",
          "pred": 0.3849713857564699,
          "actual": -0.56,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-12-01",
          "pred": -0.3585211154048745,
          "actual": -0.85,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-03-01",
          "pred": -0.34862558568232455,
          "actual": -0.73,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-06-01",
          "pred": -0.07231280137077574,
          "actual": 0.12,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-09-01",
          "pred": 0.9806643738261057,
          "actual": 0.3,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-12-01",
          "pred": 0.8448939743728391,
          "actual": 0.97,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-03-01",
          "pred": 0.24700647495375583,
          "actual": 0.81,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-06-01",
          "pred": 0.9434362578289194,
          "actual": 0.66,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-09-01",
          "pred": -0.031603132321387783,
          "actual": 0.11,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-12-01",
          "pred": -0.34567707622417193,
          "actual": 0.51,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-03-01",
          "pred": -0.06312423330730632,
          "actual": 0.36,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-06-01",
          "pred": 0.26015956974691373,
          "actual": -0.21,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-09-01",
          "pred": 0.4142849774491166,
          "actual": -0.66,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-12-01",
          "pred": -0.437141131798168,
          "actual": -0.98,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-03-01",
          "pred": -1.1122822996859782,
          "actual": -0.72,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-06-01",
          "pred": -0.15256913872902128,
          "actual": -0.06,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-09-01",
          "pred": 0.7728821797035144,
          "actual": -0.5,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-12-01",
          "pred": -0.17801526465602657,
          "actual": -1.07,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-03-01",
          "pred": -0.11989795278941481,
          "actual": -0.84,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-06-01",
          "pred": 0.41118261869717,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-09-01",
          "pred": -0.3533892513050113,
          "actual": -1.06,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-12-01",
          "pred": -0.484582345931402,
          "actual": -0.86,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-03-01",
          "pred": -1.959005820267509,
          "actual": -0.13,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-06-01",
          "pred": -0.8480647501845971,
          "actual": 0.95,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-09-01",
          "pred": -0.3879412323546767,
          "actual": 1.65,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-12-01",
          "pred": 0.9250114815676433,
          "actual": 1.81,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-03-01",
          "pred": 0.5215575624995687,
          "actual": 1.1,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-06-01",
          "pred": 0.19425179110895402,
          "actual": 0.25,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-09-01",
          "pred": -0.8777474513547734,
          "actual": -0.11,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-12-01",
          "pred": -0.5040434298200207,
          "actual": -0.58,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-03-01",
          "pred": 0.7023566478496609,
          "actual": 0.05,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-06-01",
          "pred": 0.8184618798454529,
          "actual": 0.01,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-09-01",
          "pred": -0.8943767772695888,
          "actual": -0.3,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-12-01",
          "pred": -0.5384720923592754,
          "actual": -0.49,
          "persistence": 0.01
        }
      ],
      "12": [
        {
          "origin": "2006-09-01",
          "date": "2007-09-01",
          "pred": 1.1188590297274765,
          "actual": -1.04,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-12-01",
          "pred": 1.1649551747146134,
          "actual": -1.61,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2008-03-01",
          "pred": 0.2901706418608488,
          "actual": -1.17,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2008-06-01",
          "pred": 0.3892127487942177,
          "actual": -0.44,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-09-01",
          "pred": 1.361802205606848,
          "actual": -0.28,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-12-01",
          "pred": 0.6193296954166,
          "actual": -0.9,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2009-03-01",
          "pred": 0.38110580849789905,
          "actual": -0.72,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2009-06-01",
          "pred": 0.6386374686100366,
          "actual": 0.49,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-09-01",
          "pred": -0.008870381258276078,
          "actual": 0.68,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-12-01",
          "pred": -0.3302205881739072,
          "actual": 1.81,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2010-03-01",
          "pred": -0.4989879503881163,
          "actual": 1.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2010-06-01",
          "pred": -0.5273889482438232,
          "actual": -0.62,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-09-01",
          "pred": -0.11563432745596149,
          "actual": -1.56,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-12-01",
          "pred": -0.03786881605645939,
          "actual": -1.63,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2011-03-01",
          "pred": 0.137160917433597,
          "actual": -0.98,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2011-06-01",
          "pred": -0.1876571042242416,
          "actual": -0.25,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-09-01",
          "pred": -0.5640012950459098,
          "actual": -0.76,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-12-01",
          "pred": -0.9134474549199331,
          "actual": -1.05,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2012-03-01",
          "pred": -1.1692787181760949,
          "actual": -0.48,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2012-06-01",
          "pred": -1.2819260636805572,
          "actual": 0.14,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-09-01",
          "pred": -1.4509326570114414,
          "actual": 0.44,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-12-01",
          "pred": -1.0605459063295006,
          "actual": -0.13,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2013-03-01",
          "pred": -0.6360525913221814,
          "actual": -0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2013-06-01",
          "pred": -0.5669896708805066,
          "actual": -0.33,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-09-01",
          "pred": -0.9541528557784372,
          "actual": -0.09,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-12-01",
          "pred": -1.3316847238385858,
          "actual": -0.09,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2014-03-01",
          "pred": -1.093443577898565,
          "actual": -0.07,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2014-06-01",
          "pred": -1.1733070126365737,
          "actual": 0.48,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-09-01",
          "pred": -0.3713866043785612,
          "actual": 0.37,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-12-01",
          "pred": -0.5343435699890444,
          "actual": 0.77,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2015-03-01",
          "pred": -0.2794362511778026,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2015-06-01",
          "pred": -1.250057730253808,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-09-01",
          "pred": -0.36386783438335585,
          "actual": 2.01,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-12-01",
          "pred": -0.6988887640098227,
          "actual": 2.56,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2016-03-01",
          "pred": -0.5277683923127521,
          "actual": 1.6,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2016-06-01",
          "pred": -0.22353109858662978,
          "actual": 0.06,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-09-01",
          "pred": 0.4403585220775629,
          "actual": -0.46,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-12-01",
          "pred": -0.4194200556445014,
          "actual": -0.51,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2017-03-01",
          "pred": -0.47213204841605844,
          "actual": -0.09,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2017-06-01",
          "pred": -0.3093601475545368,
          "actual": 0.22,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-09-01",
          "pred": -0.6832063601974062,
          "actual": -0.56,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-12-01",
          "pred": -0.4833010533961117,
          "actual": -0.85,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2018-03-01",
          "pred": 0.18431862711763244,
          "actual": -0.73,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2018-06-01",
          "pred": 1.1213698922476407,
          "actual": 0.12,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-09-01",
          "pred": 1.9919743424498968,
          "actual": 0.3,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-12-01",
          "pred": 1.2704829939865894,
          "actual": 0.97,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2019-03-01",
          "pred": 1.342539686806441,
          "actual": 0.81,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2019-06-01",
          "pred": 1.789969068784437,
          "actual": 0.66,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-09-01",
          "pred": 0.2635764246586153,
          "actual": 0.11,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-12-01",
          "pred": 0.2972092411804754,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2020-03-01",
          "pred": -0.17958144112245994,
          "actual": 0.36,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2020-06-01",
          "pred": 0.5977700073241146,
          "actual": -0.21,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-09-01",
          "pred": -0.01809466212252918,
          "actual": -0.66,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-12-01",
          "pred": -0.47669202828493834,
          "actual": -0.98,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2021-03-01",
          "pred": 0.25666530875007587,
          "actual": -0.72,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2021-06-01",
          "pred": 1.019488094643335,
          "actual": -0.06,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-09-01",
          "pred": 1.7151322650653842,
          "actual": -0.5,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-12-01",
          "pred": 1.250216231396859,
          "actual": -1.07,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2022-03-01",
          "pred": 1.6315745750980908,
          "actual": -0.84,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2022-06-01",
          "pred": 1.372035128048836,
          "actual": -0.77,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-09-01",
          "pred": 1.1485078437726612,
          "actual": -1.06,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-12-01",
          "pred": 0.6990997468041478,
          "actual": -0.86,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2023-03-01",
          "pred": 0.15568020449435271,
          "actual": -0.13,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2023-06-01",
          "pred": -0.32701050159093936,
          "actual": 0.95,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-09-01",
          "pred": 0.1781132373061724,
          "actual": 1.65,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-12-01",
          "pred": -0.7453869317550169,
          "actual": 1.81,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2024-03-01",
          "pred": -1.4397920697463182,
          "actual": 1.1,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2024-06-01",
          "pred": -1.2126526330535545,
          "actual": 0.25,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-09-01",
          "pred": -1.3590760324252293,
          "actual": -0.11,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-12-01",
          "pred": -0.6742173055224009,
          "actual": -0.58,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2025-03-01",
          "pred": -0.5015270228726729,
          "actual": 0.05,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2025-06-01",
          "pred": 0.03884462625540868,
          "actual": 0.01,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-09-01",
          "pred": -0.4228748310281673,
          "actual": -0.3,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-12-01",
          "pred": -0.18968320977033462,
          "actual": -0.49,
          "persistence": -0.58
        }
      ],
      "24": [
        {
          "origin": "2006-09-01",
          "date": "2008-09-01",
          "pred": 0.7985786345669212,
          "actual": -0.28,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2008-12-01",
          "pred": 1.0200914031623243,
          "actual": -0.9,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2009-03-01",
          "pred": 0.35097807496920413,
          "actual": -0.72,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2009-06-01",
          "pred": -0.4326329970500832,
          "actual": 0.49,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2009-09-01",
          "pred": -0.5390022527161996,
          "actual": 0.68,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2009-12-01",
          "pred": -0.9098422935990241,
          "actual": 1.81,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2010-03-01",
          "pred": -1.8692034628691636,
          "actual": 1.07,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2010-06-01",
          "pred": -1.7700240097572189,
          "actual": -0.62,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2010-09-01",
          "pred": -0.8504190347377323,
          "actual": -1.56,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2010-12-01",
          "pred": -1.2379611445140861,
          "actual": -1.63,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2011-03-01",
          "pred": -2.1428183123239655,
          "actual": -0.98,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2011-06-01",
          "pred": -0.15784644247154073,
          "actual": -0.25,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2011-09-01",
          "pred": 0.22747369040869897,
          "actual": -0.76,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2011-12-01",
          "pred": 0.8534289886050996,
          "actual": -1.05,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2012-03-01",
          "pred": -0.056535315886384184,
          "actual": -0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2012-06-01",
          "pred": 0.8862482499235776,
          "actual": 0.14,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2012-09-01",
          "pred": 0.5617191998381204,
          "actual": 0.44,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2012-12-01",
          "pred": 0.6865363408437205,
          "actual": -0.13,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2013-03-01",
          "pred": 0.12496700259013793,
          "actual": -0.14,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2013-06-01",
          "pred": -1.3411172199304242,
          "actual": -0.33,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2013-09-01",
          "pred": -0.5862636613417048,
          "actual": -0.09,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2013-12-01",
          "pred": -0.6597687552074166,
          "actual": -0.09,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2014-03-01",
          "pred": -0.36706610934602035,
          "actual": -0.07,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2014-06-01",
          "pred": -1.1145487443010273,
          "actual": 0.48,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2014-09-01",
          "pred": 0.12748885586510106,
          "actual": 0.37,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2014-12-01",
          "pred": 0.3883255212411789,
          "actual": 0.77,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2015-03-01",
          "pred": 0.33135405471774276,
          "actual": 0.48,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2015-06-01",
          "pred": 1.1390448748618796,
          "actual": 1.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2015-09-01",
          "pred": 0.14046571787285517,
          "actual": 2.01,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2015-12-01",
          "pred": 0.950096086045557,
          "actual": 2.56,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2016-03-01",
          "pred": 0.33322169223248405,
          "actual": 1.6,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2016-06-01",
          "pred": 0.6438018149577865,
          "actual": 0.06,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2016-09-01",
          "pred": -0.45240795493864644,
          "actual": -0.46,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2016-12-01",
          "pred": 0.4044747151683021,
          "actual": -0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2017-03-01",
          "pred": -0.13479810277567802,
          "actual": -0.09,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2017-06-01",
          "pred": -0.16588887358316115,
          "actual": 0.22,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2017-09-01",
          "pred": -0.4491134391692395,
          "actual": -0.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2017-12-01",
          "pred": 0.5388848263524008,
          "actual": -0.85,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2018-03-01",
          "pred": 0.9435055144859655,
          "actual": -0.73,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2018-06-01",
          "pred": 0.3920046186129755,
          "actual": 0.12,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2018-09-01",
          "pred": 1.0106990291268476,
          "actual": 0.3,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2018-12-01",
          "pred": -0.1607397024245382,
          "actual": 0.97,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2019-03-01",
          "pred": 0.3932593144292759,
          "actual": 0.81,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2019-06-01",
          "pred": 0.1486096947136139,
          "actual": 0.66,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2019-09-01",
          "pred": 0.48971313388219523,
          "actual": 0.11,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2019-12-01",
          "pred": 0.3723899127704467,
          "actual": 0.51,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2020-03-01",
          "pred": 0.8084436193522401,
          "actual": 0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2020-06-01",
          "pred": 0.5995063659665181,
          "actual": -0.21,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2020-09-01",
          "pred": 0.010079277362165412,
          "actual": -0.66,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2020-12-01",
          "pred": 0.14721290661718037,
          "actual": -0.98,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2021-03-01",
          "pred": -0.5455627849429694,
          "actual": -0.72,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2021-06-01",
          "pred": 0.28869468546560534,
          "actual": -0.06,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2021-09-01",
          "pred": 0.7076710727760185,
          "actual": -0.5,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2021-12-01",
          "pred": -0.3833667000502724,
          "actual": -1.07,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2022-03-01",
          "pred": -1.6348350624249932,
          "actual": -0.84,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2022-06-01",
          "pred": -1.190365859570188,
          "actual": -0.77,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2022-09-01",
          "pred": -0.22582723041268327,
          "actual": -1.06,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2022-12-01",
          "pred": -0.7420129964073509,
          "actual": -0.86,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2023-03-01",
          "pred": -0.3802165378829712,
          "actual": -0.13,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2023-06-01",
          "pred": -0.5588354745718485,
          "actual": 0.95,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2023-09-01",
          "pred": -0.7288679357771408,
          "actual": 1.65,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2023-12-01",
          "pred": -1.4209121003929563,
          "actual": 1.81,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2024-03-01",
          "pred": -0.9237438027117183,
          "actual": 1.1,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2024-06-01",
          "pred": -0.7884994021293174,
          "actual": 0.25,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2024-09-01",
          "pred": -0.5500553486264582,
          "actual": -0.11,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2024-12-01",
          "pred": 0.5691082871212041,
          "actual": -0.58,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2025-03-01",
          "pred": 0.4541824939603071,
          "actual": 0.05,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2025-06-01",
          "pred": 0.9390212601418096,
          "actual": 0.01,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2025-09-01",
          "pred": 1.2605156071713601,
          "actual": -0.3,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2025-12-01",
          "pred": 0.4196168844815541,
          "actual": -0.49,
          "persistence": 1.81
        }
      ],
      "60": [
        {
          "origin": "2006-09-01",
          "date": "2011-09-01",
          "pred": -0.7135652788960851,
          "actual": -0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2011-12-01",
          "pred": -0.19642103284049198,
          "actual": -1.05,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2012-03-01",
          "pred": -0.07886998286476131,
          "actual": -0.48,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2012-06-01",
          "pred": -0.7362444289571163,
          "actual": 0.14,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2012-09-01",
          "pred": -0.5323570440061883,
          "actual": 0.44,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2012-12-01",
          "pred": -1.1215929804798668,
          "actual": -0.13,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2013-03-01",
          "pred": -0.9994408735302366,
          "actual": -0.14,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2013-06-01",
          "pred": -0.30658953246398335,
          "actual": -0.33,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2013-09-01",
          "pred": -1.1150511410585684,
          "actual": -0.09,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2013-12-01",
          "pred": -0.5681157166152396,
          "actual": -0.09,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2014-03-01",
          "pred": -0.4282504070279326,
          "actual": -0.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2014-06-01",
          "pred": -0.39020265356248235,
          "actual": 0.48,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2014-09-01",
          "pred": 0.06942196170614542,
          "actual": 0.37,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2014-12-01",
          "pred": 0.9176106031603509,
          "actual": 0.77,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2015-03-01",
          "pred": 1.1134489377850474,
          "actual": 0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2015-06-01",
          "pred": 0.34510316005184205,
          "actual": 1.28,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2015-09-01",
          "pred": -0.48633589367493313,
          "actual": 2.01,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2015-12-01",
          "pred": -0.2913430339849483,
          "actual": 2.56,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2016-03-01",
          "pred": 0.33351786158275143,
          "actual": 1.6,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2016-06-01",
          "pred": 0.43157917164414167,
          "actual": 0.06,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2016-09-01",
          "pred": 1.3107300394843004,
          "actual": -0.46,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2016-12-01",
          "pred": 0.6023138267011836,
          "actual": -0.51,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2017-03-01",
          "pred": 1.051059086485219,
          "actual": -0.09,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2017-06-01",
          "pred": 0.9363733432638646,
          "actual": 0.22,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2017-09-01",
          "pred": 0.8455429755211872,
          "actual": -0.56,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2017-12-01",
          "pred": -0.09072005686903326,
          "actual": -0.85,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2018-03-01",
          "pred": -0.13338565707064046,
          "actual": -0.73,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2018-06-01",
          "pred": -0.26056346151412796,
          "actual": 0.12,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2018-09-01",
          "pred": 0.09290041804475581,
          "actual": 0.3,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2018-12-01",
          "pred": 0.11649900273653639,
          "actual": 0.97,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2019-03-01",
          "pred": -0.30991965047494263,
          "actual": 0.81,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2019-06-01",
          "pred": 0.2748421526884781,
          "actual": 0.66,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2019-09-01",
          "pred": 0.8732137915161615,
          "actual": 0.11,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2019-12-01",
          "pred": 0.9516846907971954,
          "actual": 0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2020-03-01",
          "pred": 0.8823948133570313,
          "actual": 0.36,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2020-06-01",
          "pred": 1.3555299634958913,
          "actual": -0.21,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2020-09-01",
          "pred": 1.3704797320137716,
          "actual": -0.66,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2020-12-01",
          "pred": 1.4707345608670748,
          "actual": -0.98,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2021-03-01",
          "pred": 1.2611978359842433,
          "actual": -0.72,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2021-06-01",
          "pred": 1.8966926471953156,
          "actual": -0.06,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2021-09-01",
          "pred": 1.8292470269167895,
          "actual": -0.5,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2021-12-01",
          "pred": 0.9034803062666567,
          "actual": -1.07,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2022-03-01",
          "pred": -0.18624108974806214,
          "actual": -0.84,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2022-06-01",
          "pred": -0.20105306802373205,
          "actual": -0.77,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2022-09-01",
          "pred": -0.036942618688895514,
          "actual": -1.06,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2022-12-01",
          "pred": 0.22039472974966115,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2023-03-01",
          "pred": 0.779350851674676,
          "actual": -0.13,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2023-06-01",
          "pred": 1.4943631908736528,
          "actual": 0.95,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2023-09-01",
          "pred": 1.4451105783492573,
          "actual": 1.65,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2023-12-01",
          "pred": 1.5418141536398282,
          "actual": 1.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2024-03-01",
          "pred": 1.9106611995140261,
          "actual": 1.1,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2024-06-01",
          "pred": 2.0102833310862938,
          "actual": 0.25,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2024-09-01",
          "pred": 2.092504790549027,
          "actual": -0.11,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2024-12-01",
          "pred": 2.3190225287568276,
          "actual": -0.58,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2025-03-01",
          "pred": 2.2768836785967093,
          "actual": 0.05,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2025-06-01",
          "pred": 2.1722580066064427,
          "actual": 0.01,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2025-09-01",
          "pred": 2.214806609815779,
          "actual": -0.3,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2025-12-01",
          "pred": 2.1052878282865013,
          "actual": -0.49,
          "persistence": -0.98
        }
      ]
    },
    "direct_value_geometry_ridge": {
      "1": [
        {
          "origin": "2006-09-01",
          "date": "2006-10-01",
          "pred": 0.5030895955541572,
          "actual": 0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-01-01",
          "pred": 1.3979412667546591,
          "actual": 0.59,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-04-01",
          "pred": -0.3239074945278139,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-07-01",
          "pred": -0.515907310693099,
          "actual": -0.37,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-10-01",
          "pred": -1.3874749717930706,
          "actual": -1.41,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-01-01",
          "pred": -1.480722997920844,
          "actual": -1.79,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-04-01",
          "pred": -1.1306831480194168,
          "actual": -0.89,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-07-01",
          "pred": -0.2803781092119012,
          "actual": -0.04,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-10-01",
          "pred": -0.5371320725979103,
          "actual": -0.3,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-01-01",
          "pred": -1.1392387045790104,
          "actual": -1.0,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-04-01",
          "pred": -1.1048123159329197,
          "actual": -0.25,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-07-01",
          "pred": 0.6652142677594728,
          "actual": 0.69,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-10-01",
          "pred": 0.5396880389687131,
          "actual": 0.96,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-01-01",
          "pred": 1.684719213925132,
          "actual": 1.43,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-04-01",
          "pred": 0.7910532191149713,
          "actual": 0.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-07-01",
          "pred": -0.9379239051574585,
          "actual": -0.89,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-10-01",
          "pred": -1.6270049647830895,
          "actual": -1.65,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-01-01",
          "pred": -0.8133947856162317,
          "actual": -1.7,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-04-01",
          "pred": -0.8068684681435564,
          "actual": -0.74,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-07-01",
          "pred": -0.265446187515667,
          "actual": -0.23,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-10-01",
          "pred": -0.7520364138470181,
          "actual": -0.93,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-01-01",
          "pred": -1.166224831864118,
          "actual": -0.93,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-04-01",
          "pred": -0.30941001292576087,
          "actual": -0.29,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-07-01",
          "pred": 0.2786480286188873,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-10-01",
          "pred": 0.7111140381448925,
          "actual": 0.23,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-01-01",
          "pred": -0.26025143517704885,
          "actual": -0.42,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-04-01",
          "pred": 0.034393999817264986,
          "actual": -0.08,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-07-01",
          "pred": -0.16226273091179202,
          "actual": -0.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-10-01",
          "pred": -0.022450434251601536,
          "actual": -0.24,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-01-01",
          "pred": 0.38699650273535424,
          "actual": -0.42,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-04-01",
          "pred": 0.13654043364684096,
          "actual": 0.28,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-07-01",
          "pred": 0.5424892036644983,
          "actual": 0.13,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-10-01",
          "pred": 0.7791037405665803,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-01-01",
          "pred": 1.0878472945671271,
          "actual": 0.59,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-04-01",
          "pred": 0.5007180616907367,
          "actual": 0.9,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-07-01",
          "pred": 1.2449916708660198,
          "actual": 1.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-10-01",
          "pred": 2.006763549860692,
          "actual": 2.21,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-01-01",
          "pred": 3.001143168851633,
          "actual": 2.56,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-04-01",
          "pred": 1.2540011167607736,
          "actual": 1.05,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-07-01",
          "pred": -0.2636276005942008,
          "actual": -0.25,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-10-01",
          "pred": -0.9748558098181659,
          "actual": -0.75,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-01-01",
          "pred": -0.18927800380815096,
          "actual": -0.34,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-04-01",
          "pred": -0.12181110494410997,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-07-01",
          "pred": 0.09749935538774859,
          "actual": 0.22,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-10-01",
          "pred": -0.9972261577246067,
          "actual": -0.52,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-01-01",
          "pred": -0.9581532511651889,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-04-01",
          "pred": -0.41659424845190096,
          "actual": -0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-07-01",
          "pred": 0.4481851389283526,
          "actual": 0.27,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-10-01",
          "pred": -0.07020001984066004,
          "actual": 0.84,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-01-01",
          "pred": 1.1455704432273683,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-04-01",
          "pred": 0.5457567535460197,
          "actual": 0.67,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-07-01",
          "pred": 0.7447544827866356,
          "actual": 0.41,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-10-01",
          "pred": 0.060470266447115596,
          "actual": 0.55,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-01-01",
          "pred": 0.6604574286469606,
          "actual": 0.64,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-04-01",
          "pred": 0.6569646457298055,
          "actual": 0.49,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-07-01",
          "pred": -0.5324840494420383,
          "actual": -0.04,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-10-01",
          "pred": -0.8584523814128754,
          "actual": -1.19,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-01-01",
          "pred": -0.8767193229037078,
          "actual": -1.04,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-04-01",
          "pred": -0.9797306869684215,
          "actual": -0.55,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-07-01",
          "pred": -0.021825470495141157,
          "actual": -0.2,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-10-01",
          "pred": -0.5859727300809054,
          "actual": -0.78,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-01-01",
          "pred": -0.8543613238713181,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-04-01",
          "pred": -0.758834164624575,
          "actual": -0.9,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-07-01",
          "pred": -0.623129827296419,
          "actual": -0.56,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-10-01",
          "pred": -1.12919995609567,
          "actual": -0.99,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-01-01",
          "pred": -0.4951005121707991,
          "actual": -0.78,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-04-01",
          "pred": -0.02224647449403022,
          "actual": 0.24,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-07-01",
          "pred": 1.226725786040382,
          "actual": 1.2,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-10-01",
          "pred": 1.9799087957394879,
          "actual": 1.59,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-01-01",
          "pred": 1.715032143781484,
          "actual": 1.71,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-04-01",
          "pred": 0.5908375286289395,
          "actual": 0.93,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-07-01",
          "pred": 0.12102933709268685,
          "actual": 0.2,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-10-01",
          "pred": 0.10669179342797659,
          "actual": -0.24,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-01-01",
          "pred": -0.5817017531230904,
          "actual": -0.76,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-04-01",
          "pred": -0.08648043387700356,
          "actual": -0.08,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-07-01",
          "pred": 0.10484352985869962,
          "actual": -0.03,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-10-01",
          "pred": -0.28993373669517236,
          "actual": -0.5,
          "persistence": -0.3
        }
      ],
      "3": [
        {
          "origin": "2006-09-01",
          "date": "2006-12-01",
          "pred": 0.481880776379364,
          "actual": 1.1,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-03-01",
          "pred": 1.1647591525897996,
          "actual": -0.15,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-06-01",
          "pred": -0.37746004476119155,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-09-01",
          "pred": -0.2873672466608052,
          "actual": -1.04,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-12-01",
          "pred": -1.2374058054839903,
          "actual": -1.61,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-03-01",
          "pred": -2.5743548557352476,
          "actual": -1.17,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-06-01",
          "pred": -1.306003121619689,
          "actual": -0.44,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-09-01",
          "pred": 0.4046915377415086,
          "actual": -0.28,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-12-01",
          "pred": 0.3213005927317343,
          "actual": -0.9,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-03-01",
          "pred": -2.6669584639215334,
          "actual": -0.72,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-06-01",
          "pred": -1.540106028041192,
          "actual": 0.49,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-09-01",
          "pred": 0.1737438856721496,
          "actual": 0.68,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-12-01",
          "pred": -0.2144308784838812,
          "actual": 1.81,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-03-01",
          "pred": 0.9784292889215724,
          "actual": 1.07,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-06-01",
          "pred": 0.5572391665229529,
          "actual": -0.62,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-09-01",
          "pred": -0.2676478797834858,
          "actual": -1.56,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-12-01",
          "pred": -1.3467457018322417,
          "actual": -1.63,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-03-01",
          "pred": -0.32023181906316367,
          "actual": -0.98,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-06-01",
          "pred": -0.38413329439349553,
          "actual": -0.25,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-09-01",
          "pred": -0.39458838302492083,
          "actual": -0.76,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-12-01",
          "pred": -1.1898458627140214,
          "actual": -1.05,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-03-01",
          "pred": -0.9797659452287986,
          "actual": -0.48,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-06-01",
          "pred": -0.2503061546740242,
          "actual": 0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-09-01",
          "pred": 0.8646485342046695,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-12-01",
          "pred": -0.24018857475353367,
          "actual": -0.13,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-03-01",
          "pred": -1.0366743889180081,
          "actual": -0.14,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-06-01",
          "pred": -0.830522371489678,
          "actual": -0.33,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-09-01",
          "pred": 0.20054432354293533,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-12-01",
          "pred": -0.2935719207338346,
          "actual": -0.09,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-03-01",
          "pred": 0.6447083595959284,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-06-01",
          "pred": 1.0455007343891471,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-09-01",
          "pred": 1.1420848847535918,
          "actual": 0.37,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-12-01",
          "pred": 0.022364865996689187,
          "actual": 0.77,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-03-01",
          "pred": 1.4146985156736278,
          "actual": 0.48,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-06-01",
          "pred": 0.2490091621011377,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-09-01",
          "pred": 1.183724022132301,
          "actual": 2.01,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-12-01",
          "pred": 2.3440120755503138,
          "actual": 2.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-03-01",
          "pred": 3.328946190327982,
          "actual": 1.6,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-06-01",
          "pred": 1.1917180028275707,
          "actual": 0.06,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-09-01",
          "pred": -0.41067503541519645,
          "actual": -0.46,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-12-01",
          "pred": -0.6502050919869948,
          "actual": -0.51,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-03-01",
          "pred": 0.08405260854378804,
          "actual": -0.09,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-06-01",
          "pred": 0.022043156422938442,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-09-01",
          "pred": -0.5382906671742962,
          "actual": -0.56,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-12-01",
          "pred": -1.2327826606177965,
          "actual": -0.85,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-03-01",
          "pred": -0.991708257404091,
          "actual": -0.73,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-06-01",
          "pred": -0.16957064023203028,
          "actual": 0.12,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-09-01",
          "pred": 0.5552858288923146,
          "actual": 0.3,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-12-01",
          "pred": 0.44208242411489823,
          "actual": 0.97,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-03-01",
          "pred": 1.9563186571160984,
          "actual": 0.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-06-01",
          "pred": 0.5504481382139521,
          "actual": 0.66,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-09-01",
          "pred": 0.6759347312813159,
          "actual": 0.11,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-12-01",
          "pred": 0.3216697155079974,
          "actual": 0.51,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-03-01",
          "pred": 0.38641615042787103,
          "actual": 0.36,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-06-01",
          "pred": 0.2817076297841701,
          "actual": -0.21,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-09-01",
          "pred": -0.6146353900462233,
          "actual": -0.66,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-12-01",
          "pred": -0.4955363499379818,
          "actual": -0.98,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-03-01",
          "pred": -0.28484999896080065,
          "actual": -0.72,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-06-01",
          "pred": -0.866411982805654,
          "actual": -0.06,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-09-01",
          "pred": -0.7938591908319359,
          "actual": -0.5,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-12-01",
          "pred": -0.6415781398962875,
          "actual": -1.07,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-03-01",
          "pred": -1.0725625672536232,
          "actual": -0.84,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-06-01",
          "pred": -0.7432099493191248,
          "actual": -0.77,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-09-01",
          "pred": -0.22186612225509295,
          "actual": -1.06,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-12-01",
          "pred": -1.4578936040733819,
          "actual": -0.86,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-03-01",
          "pred": -0.7039527890440932,
          "actual": -0.13,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-06-01",
          "pred": 0.20930903005396118,
          "actual": 0.95,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-09-01",
          "pred": 1.5794523301203205,
          "actual": 1.65,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-12-01",
          "pred": 2.1745734188743073,
          "actual": 1.81,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-03-01",
          "pred": 0.958443957799485,
          "actual": 1.1,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-06-01",
          "pred": -0.7123972824215483,
          "actual": 0.25,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-09-01",
          "pred": -0.5893638713888586,
          "actual": -0.11,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-12-01",
          "pred": 0.419083511862147,
          "actual": -0.58,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-03-01",
          "pred": -0.767152317838949,
          "actual": 0.05,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-06-01",
          "pred": -1.3239569592528673,
          "actual": 0.01,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-09-01",
          "pred": -0.4174926959871956,
          "actual": -0.3,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-12-01",
          "pred": -0.4333241484414979,
          "actual": -0.49,
          "persistence": -0.3
        }
      ],
      "6": [
        {
          "origin": "2006-09-01",
          "date": "2007-03-01",
          "pred": 0.9019720218840437,
          "actual": -0.15,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-06-01",
          "pred": 1.214449298775933,
          "actual": -0.16,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-09-01",
          "pred": -0.4714741484565229,
          "actual": -1.04,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-12-01",
          "pred": -0.2844579638848008,
          "actual": -1.61,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-03-01",
          "pred": -1.172142283758434,
          "actual": -1.17,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-06-01",
          "pred": -2.0946661366653085,
          "actual": -0.44,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-09-01",
          "pred": -3.0378253084152624,
          "actual": -0.28,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-12-01",
          "pred": -1.229038991824195,
          "actual": -0.9,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-03-01",
          "pred": 1.0529918094519068,
          "actual": -0.72,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-06-01",
          "pred": -0.9927105342862259,
          "actual": 0.49,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-09-01",
          "pred": -1.6029217683578776,
          "actual": 0.68,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-12-01",
          "pred": 0.03938154008645878,
          "actual": 1.81,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-03-01",
          "pred": -0.2753152127892896,
          "actual": 1.07,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-06-01",
          "pred": -0.5921749518148935,
          "actual": -0.62,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-09-01",
          "pred": 0.41868200452341353,
          "actual": -1.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-12-01",
          "pred": 0.03143023237097775,
          "actual": -1.63,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-03-01",
          "pred": -0.22805141431864406,
          "actual": -0.98,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-06-01",
          "pred": -1.046446789845647,
          "actual": -0.25,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-09-01",
          "pred": -1.204162807573729,
          "actual": -0.76,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-12-01",
          "pred": -0.8223169433905136,
          "actual": -1.05,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-03-01",
          "pred": -0.9743366819383529,
          "actual": -0.48,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-06-01",
          "pred": -0.7762066354295205,
          "actual": 0.14,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-09-01",
          "pred": -0.5882828555488117,
          "actual": 0.44,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-12-01",
          "pred": -0.6260159961599425,
          "actual": -0.13,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-03-01",
          "pred": -1.4519958352113618,
          "actual": -0.14,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-06-01",
          "pred": -1.515305190295102,
          "actual": -0.33,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-09-01",
          "pred": -0.9047115285135162,
          "actual": -0.09,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-12-01",
          "pred": -0.2647231168047985,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-03-01",
          "pred": -0.3825706865925427,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-06-01",
          "pred": 0.24837621164163956,
          "actual": 0.48,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-09-01",
          "pred": 0.7634117622266496,
          "actual": 0.37,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-12-01",
          "pred": 0.5688924214369502,
          "actual": 0.77,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-03-01",
          "pred": -0.46242022755712464,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-06-01",
          "pred": 0.1722073998692215,
          "actual": 1.28,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-09-01",
          "pred": 0.6797707737375341,
          "actual": 2.01,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-12-01",
          "pred": 1.6133269603700877,
          "actual": 2.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-03-01",
          "pred": 2.846346573844933,
          "actual": 1.6,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-06-01",
          "pred": 3.1746783389179236,
          "actual": 0.06,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-09-01",
          "pred": 1.0326708919812568,
          "actual": -0.46,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-12-01",
          "pred": -0.3441131122834883,
          "actual": -0.51,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-03-01",
          "pred": -0.3555677387853162,
          "actual": -0.09,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-06-01",
          "pred": 0.6853765266345482,
          "actual": 0.22,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-09-01",
          "pred": 0.16381165467493589,
          "actual": -0.56,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-12-01",
          "pred": -0.05504268945013027,
          "actual": -0.85,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-03-01",
          "pred": -0.7149105567894317,
          "actual": -0.73,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-06-01",
          "pred": -0.4558211970646689,
          "actual": 0.12,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-09-01",
          "pred": -0.4956026850696623,
          "actual": 0.3,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-12-01",
          "pred": 0.6580332919542847,
          "actual": 0.97,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-03-01",
          "pred": 0.22942722463800239,
          "actual": 0.81,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-06-01",
          "pred": 1.9612131103789316,
          "actual": 0.66,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-09-01",
          "pred": 1.1561086559417761,
          "actual": 0.11,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-12-01",
          "pred": 0.6119060240408758,
          "actual": 0.51,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-03-01",
          "pred": 0.15699443782288683,
          "actual": 0.36,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-06-01",
          "pred": 0.22581836243779135,
          "actual": -0.21,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-09-01",
          "pred": 0.39088931751510864,
          "actual": -0.66,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-12-01",
          "pred": -1.3584468091363813,
          "actual": -0.98,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-03-01",
          "pred": -1.5045245760796995,
          "actual": -0.72,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-06-01",
          "pred": -0.0358507219866272,
          "actual": -0.06,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-09-01",
          "pred": -0.16527266823553832,
          "actual": -0.5,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-12-01",
          "pred": -0.5966541348185954,
          "actual": -1.07,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-03-01",
          "pred": -0.8338386081192195,
          "actual": -0.84,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-06-01",
          "pred": -0.5337354196379746,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-09-01",
          "pred": -1.3138487837486463,
          "actual": -1.06,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-12-01",
          "pred": -1.4140905314329943,
          "actual": -0.86,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-03-01",
          "pred": -3.112784245221447,
          "actual": -0.13,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-06-01",
          "pred": -1.0509647005369265,
          "actual": 0.95,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-09-01",
          "pred": -0.056912411829172685,
          "actual": 1.65,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-12-01",
          "pred": 1.3339470655907197,
          "actual": 1.81,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-03-01",
          "pred": 1.715837190436804,
          "actual": 1.1,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-06-01",
          "pred": 1.1768467226968216,
          "actual": 0.25,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-09-01",
          "pred": -0.8629126614726152,
          "actual": -0.11,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-12-01",
          "pred": -0.4898479566888778,
          "actual": -0.58,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-03-01",
          "pred": 0.2312543719046533,
          "actual": 0.05,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-06-01",
          "pred": -0.6588752638877861,
          "actual": 0.01,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-09-01",
          "pred": -2.0097418026631795,
          "actual": -0.3,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-12-01",
          "pred": -1.8356777562843294,
          "actual": -0.49,
          "persistence": 0.01
        }
      ],
      "12": [
        {
          "origin": "2006-09-01",
          "date": "2007-09-01",
          "pred": 2.161209826163067,
          "actual": -1.04,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-12-01",
          "pred": 2.652659242055161,
          "actual": -1.61,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2008-03-01",
          "pred": 0.1734069489763467,
          "actual": -1.17,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2008-06-01",
          "pred": 0.5581473061450417,
          "actual": -0.44,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-09-01",
          "pred": -0.20937412578021508,
          "actual": -0.28,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-12-01",
          "pred": -1.6754360293545112,
          "actual": -0.9,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2009-03-01",
          "pred": -1.7502062719493052,
          "actual": -0.72,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2009-06-01",
          "pred": -0.7951791732913616,
          "actual": 0.49,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-09-01",
          "pred": 0.006225896721173463,
          "actual": 0.68,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-12-01",
          "pred": -0.9840192229438425,
          "actual": 1.81,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2010-03-01",
          "pred": -0.2857501338828201,
          "actual": 1.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2010-06-01",
          "pred": 0.2727007249601266,
          "actual": -0.62,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-09-01",
          "pred": -0.8574903931978891,
          "actual": -1.56,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-12-01",
          "pred": -0.4295164604227071,
          "actual": -1.63,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2011-03-01",
          "pred": -0.14550391904964433,
          "actual": -0.98,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2011-06-01",
          "pred": -1.547092623003487,
          "actual": -0.25,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-09-01",
          "pred": -1.7570377059962787,
          "actual": -0.76,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-12-01",
          "pred": -3.026575176854136,
          "actual": -1.05,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2012-03-01",
          "pred": -3.017778698760763,
          "actual": -0.48,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2012-06-01",
          "pred": -1.593335610550093,
          "actual": 0.14,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-09-01",
          "pred": -2.737337859239897,
          "actual": 0.44,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-12-01",
          "pred": -1.5086615291205445,
          "actual": -0.13,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2013-03-01",
          "pred": -0.3790887890346367,
          "actual": -0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2013-06-01",
          "pred": -0.9934574211756521,
          "actual": -0.33,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-09-01",
          "pred": -1.6298888696933895,
          "actual": -0.09,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-12-01",
          "pred": -1.4875957555307666,
          "actual": -0.09,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2014-03-01",
          "pred": -2.0759482626621546,
          "actual": -0.07,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2014-06-01",
          "pred": -1.4680565274269513,
          "actual": 0.48,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-09-01",
          "pred": -0.3878099934926629,
          "actual": 0.37,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-12-01",
          "pred": 0.5681304537732956,
          "actual": 0.77,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2015-03-01",
          "pred": 0.38202911124442474,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2015-06-01",
          "pred": -0.6710437043726387,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-09-01",
          "pred": -1.2446721758790096,
          "actual": 2.01,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-12-01",
          "pred": -1.653085849010293,
          "actual": 2.56,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2016-03-01",
          "pred": -1.0863407255239674,
          "actual": 1.6,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2016-06-01",
          "pred": -0.404366290476756,
          "actual": 0.06,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-09-01",
          "pred": 0.6097212158765251,
          "actual": -0.46,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-12-01",
          "pred": 0.10702163416869448,
          "actual": -0.51,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2017-03-01",
          "pred": -0.36212527954885054,
          "actual": -0.09,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2017-06-01",
          "pred": -1.5557507724409507,
          "actual": 0.22,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-09-01",
          "pred": -1.5680852450179783,
          "actual": -0.56,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-12-01",
          "pred": -1.8966481803165014,
          "actual": -0.85,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2018-03-01",
          "pred": -0.4565719557847674,
          "actual": -0.73,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2018-06-01",
          "pred": 1.7987944683522064,
          "actual": 0.12,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-09-01",
          "pred": 1.9815534918881186,
          "actual": 0.3,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-12-01",
          "pred": 1.0230898078528297,
          "actual": 0.97,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2019-03-01",
          "pred": 0.7473772365014302,
          "actual": 0.81,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2019-06-01",
          "pred": 1.4262540836376019,
          "actual": 0.66,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-09-01",
          "pred": 0.36291020060450885,
          "actual": 0.11,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-12-01",
          "pred": 0.4700225826692664,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2020-03-01",
          "pred": 0.9408266399111225,
          "actual": 0.36,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2020-06-01",
          "pred": 1.8852796721376017,
          "actual": -0.21,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-09-01",
          "pred": 0.9103991941500806,
          "actual": -0.66,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-12-01",
          "pred": 0.6044383265414269,
          "actual": -0.98,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2021-03-01",
          "pred": 1.4054507788363084,
          "actual": -0.72,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2021-06-01",
          "pred": 1.0444636081310203,
          "actual": -0.06,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-09-01",
          "pred": 1.7034105902885117,
          "actual": -0.5,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-12-01",
          "pred": 0.6062904858795441,
          "actual": -1.07,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2022-03-01",
          "pred": 0.11101062986242716,
          "actual": -0.84,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2022-06-01",
          "pred": 0.5469474764594129,
          "actual": -0.77,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-09-01",
          "pred": 0.10898479431939545,
          "actual": -1.06,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-12-01",
          "pred": -0.7940923974228993,
          "actual": -0.86,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2023-03-01",
          "pred": -1.1806587229964918,
          "actual": -0.13,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2023-06-01",
          "pred": -1.4245507860850584,
          "actual": 0.95,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-09-01",
          "pred": -1.5178132204931352,
          "actual": 1.65,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-12-01",
          "pred": -1.5023235400495845,
          "actual": 1.81,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2024-03-01",
          "pred": -1.511132776439183,
          "actual": 1.1,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2024-06-01",
          "pred": -0.6650033630827943,
          "actual": 0.25,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-09-01",
          "pred": -0.11803311994930477,
          "actual": -0.11,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-12-01",
          "pred": -0.3050744911478853,
          "actual": -0.58,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2025-03-01",
          "pred": 0.309843457456362,
          "actual": 0.05,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2025-06-01",
          "pred": 1.6720743750268963,
          "actual": 0.01,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-09-01",
          "pred": -0.013069305196065403,
          "actual": -0.3,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-12-01",
          "pred": -1.4715375500144217,
          "actual": -0.49,
          "persistence": -0.58
        }
      ],
      "24": [
        {
          "origin": "2006-09-01",
          "date": "2008-09-01",
          "pred": 2.0902143887772295,
          "actual": -0.28,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2008-12-01",
          "pred": 2.3466640574016404,
          "actual": -0.9,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2009-03-01",
          "pred": 0.19323345441128123,
          "actual": -0.72,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2009-06-01",
          "pred": 0.5078297872746851,
          "actual": 0.49,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2009-09-01",
          "pred": -0.6827145989634009,
          "actual": 0.68,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2009-12-01",
          "pred": -1.4456699005109084,
          "actual": 1.81,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2010-03-01",
          "pred": -3.225459445465871,
          "actual": 1.07,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2010-06-01",
          "pred": -2.9522730758216236,
          "actual": -0.62,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2010-09-01",
          "pred": -0.7877910801901183,
          "actual": -1.56,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2010-12-01",
          "pred": -2.5181905481187554,
          "actual": -1.63,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2011-03-01",
          "pred": -2.8413480045071804,
          "actual": -0.98,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2011-06-01",
          "pred": -0.7704511452174516,
          "actual": -0.25,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2011-09-01",
          "pred": -0.5930286744760666,
          "actual": -0.76,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2011-12-01",
          "pred": -0.09343770050494715,
          "actual": -1.05,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2012-03-01",
          "pred": -0.5196618653252822,
          "actual": -0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2012-06-01",
          "pred": 0.8392446165838147,
          "actual": 0.14,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2012-09-01",
          "pred": -0.24749522993369233,
          "actual": 0.44,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2012-12-01",
          "pred": -0.3677621763682941,
          "actual": -0.13,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2013-03-01",
          "pred": -1.3524679918168787,
          "actual": -0.14,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2013-06-01",
          "pred": -1.8317552336314977,
          "actual": -0.33,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2013-09-01",
          "pred": -2.2634230320059983,
          "actual": -0.09,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2013-12-01",
          "pred": -1.3008990907853584,
          "actual": -0.09,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2014-03-01",
          "pred": -0.629128197552141,
          "actual": -0.07,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2014-06-01",
          "pred": -1.0819667636330017,
          "actual": 0.48,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2014-09-01",
          "pred": 0.20159789991305144,
          "actual": 0.37,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2014-12-01",
          "pred": 0.105902860645392,
          "actual": 0.77,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2015-03-01",
          "pred": 0.5467599498691724,
          "actual": 0.48,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2015-06-01",
          "pred": 1.534716452027113,
          "actual": 1.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2015-09-01",
          "pred": 0.6103322914505253,
          "actual": 2.01,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2015-12-01",
          "pred": 1.4761262876979486,
          "actual": 2.56,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2016-03-01",
          "pred": 0.38832424917832625,
          "actual": 1.6,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2016-06-01",
          "pred": 0.4668702036857697,
          "actual": 0.06,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2016-09-01",
          "pred": -1.8388914027835614,
          "actual": -0.46,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2016-12-01",
          "pred": -0.8773280494547531,
          "actual": -0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2017-03-01",
          "pred": -1.1126407780557641,
          "actual": -0.09,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2017-06-01",
          "pred": -0.2098588257660141,
          "actual": 0.22,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2017-09-01",
          "pred": -0.6993278950246111,
          "actual": -0.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2017-12-01",
          "pred": 0.40678455284562887,
          "actual": -0.85,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2018-03-01",
          "pred": 0.28922166728170806,
          "actual": -0.73,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2018-06-01",
          "pred": 0.2009776304469666,
          "actual": 0.12,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2018-09-01",
          "pred": 0.9508054980555822,
          "actual": 0.3,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2018-12-01",
          "pred": -0.4289840642874399,
          "actual": 0.97,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2019-03-01",
          "pred": -0.2425407294215032,
          "actual": 0.81,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2019-06-01",
          "pred": -0.13805959557175182,
          "actual": 0.66,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2019-09-01",
          "pred": 0.06927322642041356,
          "actual": 0.11,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2019-12-01",
          "pred": 0.4833475426996737,
          "actual": 0.51,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2020-03-01",
          "pred": -0.5316151473872096,
          "actual": 0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2020-06-01",
          "pred": 0.2627993540309783,
          "actual": -0.21,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2020-09-01",
          "pred": -0.07470110876651687,
          "actual": -0.66,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2020-12-01",
          "pred": 0.4825478915624081,
          "actual": -0.98,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2021-03-01",
          "pred": 0.9581857170318555,
          "actual": -0.72,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2021-06-01",
          "pred": 1.1402376744084939,
          "actual": -0.06,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2021-09-01",
          "pred": 1.2855104084294988,
          "actual": -0.5,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2021-12-01",
          "pred": 0.527347250089224,
          "actual": -1.07,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2022-03-01",
          "pred": -0.8598294012888016,
          "actual": -0.84,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2022-06-01",
          "pred": -1.3353869696127203,
          "actual": -0.77,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2022-09-01",
          "pred": -2.282533252436205,
          "actual": -1.06,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2022-12-01",
          "pred": -2.3880201935149774,
          "actual": -0.86,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2023-03-01",
          "pred": -2.794664971268314,
          "actual": -0.13,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2023-06-01",
          "pred": -2.7575463530167608,
          "actual": 0.95,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2023-09-01",
          "pred": -3.166526700822493,
          "actual": 1.65,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2023-12-01",
          "pred": -4.813569050797408,
          "actual": 1.81,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2024-03-01",
          "pred": -3.7920459409527023,
          "actual": 1.1,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2024-06-01",
          "pred": -2.8986688472393487,
          "actual": 0.25,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2024-09-01",
          "pred": -2.951431691207256,
          "actual": -0.11,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2024-12-01",
          "pred": -0.8640087742650471,
          "actual": -0.58,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2025-03-01",
          "pred": -0.33178837497192554,
          "actual": 0.05,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2025-06-01",
          "pred": 1.832784711836255,
          "actual": 0.01,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2025-09-01",
          "pred": 2.9962314599696667,
          "actual": -0.3,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2025-12-01",
          "pred": 1.4872840421472069,
          "actual": -0.49,
          "persistence": 1.81
        }
      ],
      "60": [
        {
          "origin": "2006-09-01",
          "date": "2011-09-01",
          "pred": -0.4227899214834113,
          "actual": -0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2011-12-01",
          "pred": -0.035160861602679505,
          "actual": -1.05,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2012-03-01",
          "pred": -1.1274616641383994,
          "actual": -0.48,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2012-06-01",
          "pred": -0.9550319882957176,
          "actual": 0.14,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2012-09-01",
          "pred": -1.0709201466857996,
          "actual": 0.44,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2012-12-01",
          "pred": -1.7866200574430995,
          "actual": -0.13,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2013-03-01",
          "pred": -1.3223186276048433,
          "actual": -0.14,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2013-06-01",
          "pred": -0.1250641567565165,
          "actual": -0.33,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2013-09-01",
          "pred": -0.2083809026367006,
          "actual": -0.09,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2013-12-01",
          "pred": -1.606379612903011,
          "actual": -0.09,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2014-03-01",
          "pred": -0.3629524439530376,
          "actual": -0.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2014-06-01",
          "pred": 0.9014780419944862,
          "actual": 0.48,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2014-09-01",
          "pred": 0.30766637284493137,
          "actual": 0.37,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2014-12-01",
          "pred": 1.7571297327501472,
          "actual": 0.77,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2015-03-01",
          "pred": 1.1055913745490644,
          "actual": 0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2015-06-01",
          "pred": 0.018631631453349562,
          "actual": 1.28,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2015-09-01",
          "pred": -0.4039739723322564,
          "actual": 2.01,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2015-12-01",
          "pred": -0.712375039080267,
          "actual": 2.56,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2016-03-01",
          "pred": -0.3664888157497481,
          "actual": 1.6,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2016-06-01",
          "pred": 0.46293694521520745,
          "actual": 0.06,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2016-09-01",
          "pred": -0.3762014707031196,
          "actual": -0.46,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2016-12-01",
          "pred": 0.20291237247639526,
          "actual": -0.51,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2017-03-01",
          "pred": 0.5470427060786966,
          "actual": -0.09,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2017-06-01",
          "pred": 0.3792343129101599,
          "actual": 0.22,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2017-09-01",
          "pred": -0.34844450736610194,
          "actual": -0.56,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2017-12-01",
          "pred": -1.1406892650697342,
          "actual": -0.85,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2018-03-01",
          "pred": -0.9352792228863661,
          "actual": -0.73,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2018-06-01",
          "pred": -1.2453735411697693,
          "actual": 0.12,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2018-09-01",
          "pred": -0.4120389574305009,
          "actual": 0.3,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2018-12-01",
          "pred": 0.07149455884217981,
          "actual": 0.97,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2019-03-01",
          "pred": -1.3627908642657685,
          "actual": 0.81,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2019-06-01",
          "pred": -1.4080930150333524,
          "actual": 0.66,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2019-09-01",
          "pred": -0.6609774157505376,
          "actual": 0.11,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2019-12-01",
          "pred": -0.37332222127176595,
          "actual": 0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2020-03-01",
          "pred": -0.465604994375036,
          "actual": 0.36,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2020-06-01",
          "pred": 1.44061115821559,
          "actual": -0.21,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2020-09-01",
          "pred": 1.5488377579788581,
          "actual": -0.66,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2020-12-01",
          "pred": 1.492474184139491,
          "actual": -0.98,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2021-03-01",
          "pred": 1.3579030221915378,
          "actual": -0.72,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2021-06-01",
          "pred": 1.5977073826196249,
          "actual": -0.06,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2021-09-01",
          "pred": 1.7090969203221005,
          "actual": -0.5,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2021-12-01",
          "pred": 0.589694873538614,
          "actual": -1.07,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2022-03-01",
          "pred": -1.3183681770295639,
          "actual": -0.84,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2022-06-01",
          "pred": 0.2949747898743722,
          "actual": -0.77,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2022-09-01",
          "pred": 0.12780761659098694,
          "actual": -1.06,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2022-12-01",
          "pred": 0.4244019335047965,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2023-03-01",
          "pred": 0.3945368779773246,
          "actual": -0.13,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2023-06-01",
          "pred": 1.4052503018736027,
          "actual": 0.95,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2023-09-01",
          "pred": 1.4662990533402447,
          "actual": 1.65,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2023-12-01",
          "pred": 2.258679138077864,
          "actual": 1.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2024-03-01",
          "pred": 3.5996345177360674,
          "actual": 1.1,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2024-06-01",
          "pred": 4.019662616946333,
          "actual": 0.25,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2024-09-01",
          "pred": 4.302745022864346,
          "actual": -0.11,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2024-12-01",
          "pred": 4.686830272311672,
          "actual": -0.58,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2025-03-01",
          "pred": 4.27539894278656,
          "actual": 0.05,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2025-06-01",
          "pred": 3.0356878462779586,
          "actual": 0.01,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2025-09-01",
          "pred": 2.254484352040752,
          "actual": -0.3,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2025-12-01",
          "pred": 2.1873050288212856,
          "actual": -0.49,
          "persistence": -0.98
        }
      ]
    },
    "lag_ridge": {
      "1": [
        {
          "origin": "2006-09-01",
          "date": "2006-10-01",
          "pred": 0.7270414677165788,
          "actual": 0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-01-01",
          "pred": 1.1169480825115772,
          "actual": 0.59,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-04-01",
          "pred": -0.3451115148375633,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-07-01",
          "pred": -0.11754217596323363,
          "actual": -0.37,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-10-01",
          "pred": -1.1687989445397946,
          "actual": -1.41,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-01-01",
          "pred": -1.560146790864992,
          "actual": -1.79,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-04-01",
          "pred": -0.8753795428753439,
          "actual": -0.89,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-07-01",
          "pred": -0.25010421924035076,
          "actual": -0.04,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-10-01",
          "pred": -0.3008962018118343,
          "actual": -0.3,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-01-01",
          "pred": -1.0476586851733871,
          "actual": -1.0,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-04-01",
          "pred": -0.6419936342155298,
          "actual": -0.25,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-07-01",
          "pred": 0.6800903711441104,
          "actual": 0.69,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-10-01",
          "pred": 0.6483023702598263,
          "actual": 0.96,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-01-01",
          "pred": 1.8948874891150747,
          "actual": 1.43,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-04-01",
          "pred": 0.8897787828360099,
          "actual": 0.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-07-01",
          "pred": -0.9185823715606809,
          "actual": -0.89,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-10-01",
          "pred": -1.6297914359626886,
          "actual": -1.65,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-01-01",
          "pred": -1.5237517340180078,
          "actual": -1.7,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-04-01",
          "pred": -0.723218137770804,
          "actual": -0.74,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-07-01",
          "pred": -0.04374426308827484,
          "actual": -0.23,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-10-01",
          "pred": -0.7860451091941288,
          "actual": -0.93,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-01-01",
          "pred": -0.9911678767791495,
          "actual": -0.93,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-04-01",
          "pred": -0.33396388646974695,
          "actual": -0.29,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-07-01",
          "pred": 0.2956024049761672,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-10-01",
          "pred": 0.357799456421054,
          "actual": 0.23,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-01-01",
          "pred": -0.339784968060708,
          "actual": -0.42,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-04-01",
          "pred": -0.05187615850079698,
          "actual": -0.08,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-07-01",
          "pred": -0.3468972117046027,
          "actual": -0.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-10-01",
          "pred": 0.0019612436677369643,
          "actual": -0.24,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-01-01",
          "pred": -0.11132773618432441,
          "actual": -0.42,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-04-01",
          "pred": 0.05304249538000312,
          "actual": 0.28,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-07-01",
          "pred": 0.4962492153023924,
          "actual": 0.13,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-10-01",
          "pred": 0.40129641945267425,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-01-01",
          "pred": 0.6869146612231525,
          "actual": 0.59,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-04-01",
          "pred": 0.37440390338157087,
          "actual": 0.9,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-07-01",
          "pred": 1.3089109983536173,
          "actual": 1.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-10-01",
          "pred": 1.9651705799870476,
          "actual": 2.21,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-01-01",
          "pred": 2.424891988788761,
          "actual": 2.56,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-04-01",
          "pred": 1.2055811578926323,
          "actual": 1.05,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-07-01",
          "pred": -0.2504794613300505,
          "actual": -0.25,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-10-01",
          "pred": -0.477738739138683,
          "actual": -0.75,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-01-01",
          "pred": -0.4231083380114269,
          "actual": -0.34,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-04-01",
          "pred": -0.052867532108278464,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-07-01",
          "pred": 0.2106341903034701,
          "actual": 0.22,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-10-01",
          "pred": -0.7314557016568128,
          "actual": -0.52,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-01-01",
          "pred": -0.8259994811847773,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-04-01",
          "pred": -0.6558074886588897,
          "actual": -0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-07-01",
          "pred": 0.2859104070218946,
          "actual": 0.27,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-10-01",
          "pred": 0.3725414907571503,
          "actual": 0.84,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-01-01",
          "pred": 0.9450136622375405,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-04-01",
          "pred": 0.7955438505223638,
          "actual": 0.67,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-07-01",
          "pred": 0.602224803704603,
          "actual": 0.41,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-10-01",
          "pred": 0.015890411071752555,
          "actual": 0.55,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-01-01",
          "pred": 0.4249652973532023,
          "actual": 0.64,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-04-01",
          "pred": 0.2854768736302108,
          "actual": 0.49,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-07-01",
          "pred": -0.2779798181553052,
          "actual": -0.04,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-10-01",
          "pred": -0.7261024754665408,
          "actual": -1.19,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-01-01",
          "pred": -0.9198882914598231,
          "actual": -1.04,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-04-01",
          "pred": -0.5604133714256148,
          "actual": -0.55,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-07-01",
          "pred": 0.13037329188740757,
          "actual": -0.2,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-10-01",
          "pred": -0.5349917499995788,
          "actual": -0.78,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-01-01",
          "pred": -1.1102891382488458,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-04-01",
          "pred": -0.7983550848400066,
          "actual": -0.9,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-07-01",
          "pred": -0.6179441856988357,
          "actual": -0.56,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-10-01",
          "pred": -1.0310798470546627,
          "actual": -0.99,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-01-01",
          "pred": -0.8103165530060921,
          "actual": -0.78,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-04-01",
          "pred": 0.10071930688102093,
          "actual": 0.24,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-07-01",
          "pred": 1.1335275802359963,
          "actual": 1.2,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-10-01",
          "pred": 1.6190403612234339,
          "actual": 1.59,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-01-01",
          "pred": 1.6155986339414958,
          "actual": 1.71,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-04-01",
          "pred": 0.8136531549613066,
          "actual": 0.93,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-07-01",
          "pred": 0.07235665410436712,
          "actual": 0.2,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-10-01",
          "pred": -0.1839045297262751,
          "actual": -0.24,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-01-01",
          "pred": -0.7311466776758073,
          "actual": -0.76,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-04-01",
          "pred": 0.2375234601897655,
          "actual": -0.08,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-07-01",
          "pred": 0.04200984395442131,
          "actual": -0.03,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-10-01",
          "pred": -0.36411198790415117,
          "actual": -0.5,
          "persistence": -0.3
        }
      ],
      "3": [
        {
          "origin": "2006-09-01",
          "date": "2006-12-01",
          "pred": 0.770847647972299,
          "actual": 1.1,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-03-01",
          "pred": 1.008761670110288,
          "actual": -0.15,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-06-01",
          "pred": -0.5480592310329772,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-09-01",
          "pred": -0.03883476911312718,
          "actual": -1.04,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-12-01",
          "pred": -1.1968195071620025,
          "actual": -1.61,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-03-01",
          "pred": -1.2840086957995769,
          "actual": -1.17,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-06-01",
          "pred": -0.35625488976623054,
          "actual": -0.44,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-09-01",
          "pred": 0.05416910779051548,
          "actual": -0.28,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-12-01",
          "pred": -0.27893010488978126,
          "actual": -0.9,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-03-01",
          "pred": -1.0797707879782297,
          "actual": -0.72,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-06-01",
          "pred": -0.45098387796793904,
          "actual": 0.49,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-09-01",
          "pred": 0.7944982156691591,
          "actual": 0.68,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-12-01",
          "pred": 0.4899916479521044,
          "actual": 1.81,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-03-01",
          "pred": 1.7486267246106846,
          "actual": 1.07,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-06-01",
          "pred": 0.5479737861879236,
          "actual": -0.62,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-09-01",
          "pred": -1.1789560385501643,
          "actual": -1.56,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-12-01",
          "pred": -1.4984086930648761,
          "actual": -1.63,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-03-01",
          "pred": -1.1611304387939532,
          "actual": -0.98,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-06-01",
          "pred": -0.24788128825322708,
          "actual": -0.25,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-09-01",
          "pred": 0.2536073995306267,
          "actual": -0.76,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-12-01",
          "pred": -0.7107604377564832,
          "actual": -1.05,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-03-01",
          "pred": -0.7621698903521394,
          "actual": -0.48,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-06-01",
          "pred": -0.08565099122759312,
          "actual": 0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-09-01",
          "pred": 0.4316481369204294,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-12-01",
          "pred": 0.1957335256344134,
          "actual": -0.13,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-03-01",
          "pred": -0.5300882921028074,
          "actual": -0.14,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-06-01",
          "pred": 0.0821849400017155,
          "actual": -0.33,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-09-01",
          "pred": -0.3625766035008265,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-12-01",
          "pred": 0.081449350668022,
          "actual": -0.09,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-03-01",
          "pred": -0.10603946606846212,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-06-01",
          "pred": 0.1891138583870383,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-09-01",
          "pred": 0.4316603644727079,
          "actual": 0.37,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-12-01",
          "pred": 0.3527863686068125,
          "actual": 0.77,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-03-01",
          "pred": 0.4974775724749895,
          "actual": 0.48,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-06-01",
          "pred": 0.17253611251065148,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-09-01",
          "pred": 1.0869705902807214,
          "actual": 2.01,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-12-01",
          "pred": 1.5827248157962308,
          "actual": 2.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-03-01",
          "pred": 1.8790100001009966,
          "actual": 1.6,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-06-01",
          "pred": 0.5213294885281643,
          "actual": 0.06,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-09-01",
          "pred": -0.6465455947958314,
          "actual": -0.46,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-12-01",
          "pred": -0.48155043062763,
          "actual": -0.51,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-03-01",
          "pred": -0.27844832816490417,
          "actual": -0.09,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-06-01",
          "pred": -0.003937865055417891,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-09-01",
          "pred": 0.1594875016602936,
          "actual": -0.56,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-12-01",
          "pred": -0.8590198454980789,
          "actual": -0.85,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-03-01",
          "pred": -0.6859649193675271,
          "actual": -0.73,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-06-01",
          "pred": -0.45587749230072694,
          "actual": 0.12,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-09-01",
          "pred": 0.4438068400156242,
          "actual": 0.3,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-12-01",
          "pred": 0.38732117590239235,
          "actual": 0.97,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-03-01",
          "pred": 0.770727070076805,
          "actual": 0.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-06-01",
          "pred": 0.6668879923490552,
          "actual": 0.66,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-09-01",
          "pred": 0.4357066692942658,
          "actual": 0.11,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-12-01",
          "pred": -0.12006796208133656,
          "actual": 0.51,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-03-01",
          "pred": 0.2780988333193766,
          "actual": 0.36,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-06-01",
          "pred": 0.12220738400661119,
          "actual": -0.21,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-09-01",
          "pred": -0.38123281982894774,
          "actual": -0.66,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-12-01",
          "pred": -0.7398629649050559,
          "actual": -0.98,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-03-01",
          "pred": -0.6908251076363794,
          "actual": -0.72,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-06-01",
          "pred": -0.27072900690368046,
          "actual": -0.06,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-09-01",
          "pred": 0.3527756667183637,
          "actual": -0.5,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-12-01",
          "pred": -0.5153748318716828,
          "actual": -1.07,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-03-01",
          "pred": -0.9698689718899753,
          "actual": -0.84,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-06-01",
          "pred": -0.6061883711482454,
          "actual": -0.77,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-09-01",
          "pred": -0.36478954409624414,
          "actual": -1.06,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-12-01",
          "pred": -0.890035228233567,
          "actual": -0.86,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-03-01",
          "pred": -0.5885988044032315,
          "actual": -0.13,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-06-01",
          "pred": 0.37032091653246324,
          "actual": 0.95,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-09-01",
          "pred": 1.1884527583970317,
          "actual": 1.65,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-12-01",
          "pred": 1.3643009252812677,
          "actual": 1.81,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-03-01",
          "pred": 1.1809078837401032,
          "actual": 1.1,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-06-01",
          "pred": 0.3193438155439102,
          "actual": 0.25,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-09-01",
          "pred": -0.2107668141775731,
          "actual": -0.11,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-12-01",
          "pred": -0.2823534723160108,
          "actual": -0.58,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-03-01",
          "pred": -0.8323558770522372,
          "actual": 0.05,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-06-01",
          "pred": 0.468478320000927,
          "actual": 0.01,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-09-01",
          "pred": 0.045696938963615805,
          "actual": -0.3,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-12-01",
          "pred": -0.3955238700958017,
          "actual": -0.49,
          "persistence": -0.3
        }
      ],
      "6": [
        {
          "origin": "2006-09-01",
          "date": "2007-03-01",
          "pred": 0.5317166932742271,
          "actual": -0.15,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-06-01",
          "pred": 0.6475752727114341,
          "actual": -0.16,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-09-01",
          "pred": -0.5763724958794686,
          "actual": -1.04,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-12-01",
          "pred": 0.18680313930172474,
          "actual": -1.61,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-03-01",
          "pred": -0.9333743770376001,
          "actual": -1.17,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-06-01",
          "pred": -0.7014942091975018,
          "actual": -0.44,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-09-01",
          "pred": 0.14298579164419523,
          "actual": -0.28,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-12-01",
          "pred": 0.2445518121138172,
          "actual": -0.9,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-03-01",
          "pred": -0.1845553782665566,
          "actual": -0.72,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-06-01",
          "pred": -0.7712346728652192,
          "actual": 0.49,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-09-01",
          "pred": -0.1252309958620793,
          "actual": 0.68,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-12-01",
          "pred": 0.6281983364257984,
          "actual": 1.81,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-03-01",
          "pred": 0.17052586060843844,
          "actual": 1.07,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-06-01",
          "pred": 1.1373479933129211,
          "actual": -0.62,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-09-01",
          "pred": 0.027606505455298747,
          "actual": -1.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-12-01",
          "pred": -1.0075858551681933,
          "actual": -1.63,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-03-01",
          "pred": -0.8582972610776729,
          "actual": -0.98,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-06-01",
          "pred": -0.5330069281606191,
          "actual": -0.25,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-09-01",
          "pred": 0.1377322702025805,
          "actual": -0.76,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-12-01",
          "pred": 0.3595351478556723,
          "actual": -1.05,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-03-01",
          "pred": -0.4385988943655733,
          "actual": -0.48,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-06-01",
          "pred": -0.23726065774611893,
          "actual": 0.14,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-09-01",
          "pred": 0.1617876366178186,
          "actual": 0.44,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-12-01",
          "pred": 0.3089771567386629,
          "actual": -0.13,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-03-01",
          "pred": -0.020233061236916317,
          "actual": -0.14,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-06-01",
          "pred": -0.478844486502693,
          "actual": -0.33,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-09-01",
          "pred": 0.18704088702691013,
          "actual": -0.09,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-12-01",
          "pred": -0.3002997136812408,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-03-01",
          "pred": 0.053918939770675606,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-06-01",
          "pred": -0.1376884713109789,
          "actual": 0.48,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-09-01",
          "pred": 0.17514029333112277,
          "actual": 0.37,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-12-01",
          "pred": 0.2333433649598994,
          "actual": 0.77,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-03-01",
          "pred": 0.09836519565429508,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-06-01",
          "pred": 0.2139570825182413,
          "actual": 1.28,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-09-01",
          "pred": -0.10809212055858997,
          "actual": 2.01,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-12-01",
          "pred": 0.6109851135970868,
          "actual": 2.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-03-01",
          "pred": 0.6960934876819873,
          "actual": 1.6,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-06-01",
          "pred": 0.7935226659954666,
          "actual": 0.06,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-09-01",
          "pred": -0.1854424746722454,
          "actual": -0.46,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-12-01",
          "pred": -0.6698088317041329,
          "actual": -0.51,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-03-01",
          "pred": -0.2943164209614615,
          "actual": -0.09,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-06-01",
          "pred": -0.27791670760631226,
          "actual": 0.22,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-09-01",
          "pred": -0.11808430738413486,
          "actual": -0.56,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-12-01",
          "pred": 0.015825400307528714,
          "actual": -0.85,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-03-01",
          "pred": -0.7149114122007042,
          "actual": -0.73,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-06-01",
          "pred": -0.22441302906281524,
          "actual": 0.12,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-09-01",
          "pred": -0.15505997064056465,
          "actual": 0.3,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-12-01",
          "pred": 0.3665201769058344,
          "actual": 0.97,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-03-01",
          "pred": 0.16865123040136934,
          "actual": 0.81,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-06-01",
          "pred": 0.5025332959937969,
          "actual": 0.66,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-09-01",
          "pred": 0.3558733464063891,
          "actual": 0.11,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-12-01",
          "pred": 0.23776561559844445,
          "actual": 0.51,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-03-01",
          "pred": -0.1710526346388151,
          "actual": 0.36,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-06-01",
          "pred": 0.13199217679649644,
          "actual": -0.21,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-09-01",
          "pred": -0.16976058026344631,
          "actual": -0.66,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-12-01",
          "pred": -0.3741033705607551,
          "actual": -0.98,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-03-01",
          "pred": -0.4417468061252138,
          "actual": -0.72,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-06-01",
          "pred": -0.3173738672258054,
          "actual": -0.06,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-09-01",
          "pred": 0.0056696615686301355,
          "actual": -0.5,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-12-01",
          "pred": 0.36911750419998074,
          "actual": -1.07,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-03-01",
          "pred": -0.4290799570279958,
          "actual": -0.84,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-06-01",
          "pred": -0.4373090293801264,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-09-01",
          "pred": -0.15376680686529198,
          "actual": -1.06,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-12-01",
          "pred": -0.16652673017532404,
          "actual": -0.86,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-03-01",
          "pred": -0.5529050815978412,
          "actual": -0.13,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-06-01",
          "pred": -0.17310793546621417,
          "actual": 0.95,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-09-01",
          "pred": 0.47097419236127624,
          "actual": 1.65,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-12-01",
          "pred": 0.8357280983815443,
          "actual": 1.81,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-03-01",
          "pred": 0.7254822918196158,
          "actual": 1.1,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-06-01",
          "pred": 0.5429428738336741,
          "actual": 0.25,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-09-01",
          "pred": -0.10329457550732046,
          "actual": -0.11,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-12-01",
          "pred": -0.29707042441790055,
          "actual": -0.58,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-03-01",
          "pred": -0.2999535274481288,
          "actual": 0.05,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-06-01",
          "pred": -0.8373691857477998,
          "actual": 0.01,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-09-01",
          "pred": 0.47935767504377275,
          "actual": -0.3,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-12-01",
          "pred": -0.10685348851558513,
          "actual": -0.49,
          "persistence": 0.01
        }
      ],
      "12": [
        {
          "origin": "2006-09-01",
          "date": "2007-09-01",
          "pred": 0.0446855052070253,
          "actual": -1.04,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-12-01",
          "pred": 0.18628401858365762,
          "actual": -1.61,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2008-03-01",
          "pred": 0.05619230786120413,
          "actual": -1.17,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2008-06-01",
          "pred": 0.12030994121278557,
          "actual": -0.44,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-09-01",
          "pred": -0.17058174146843308,
          "actual": -0.28,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-12-01",
          "pred": -0.06983239842552802,
          "actual": -0.9,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2009-03-01",
          "pred": 0.39401048211296974,
          "actual": -0.72,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2009-06-01",
          "pred": 0.08522027802893734,
          "actual": 0.49,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-09-01",
          "pred": 0.05032623336365505,
          "actual": 0.68,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-12-01",
          "pred": 0.21696068062331164,
          "actual": 1.81,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2010-03-01",
          "pred": 0.37469168100828854,
          "actual": 1.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2010-06-01",
          "pred": 0.11403487406745416,
          "actual": -0.62,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-09-01",
          "pred": -0.14454854689565755,
          "actual": -1.56,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-12-01",
          "pred": 0.14022462152229132,
          "actual": -1.63,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2011-03-01",
          "pred": -0.06991044713844241,
          "actual": -0.98,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2011-06-01",
          "pred": -0.2524595719833009,
          "actual": -0.25,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-09-01",
          "pred": -0.013303025438978766,
          "actual": -0.76,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-12-01",
          "pred": -0.29022562493053106,
          "actual": -1.05,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2012-03-01",
          "pred": -0.10733310489256176,
          "actual": -0.48,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2012-06-01",
          "pred": 0.11548562418022851,
          "actual": 0.14,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-09-01",
          "pred": 0.32054990179372256,
          "actual": 0.44,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-12-01",
          "pred": 0.5515715649825352,
          "actual": -0.13,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2013-03-01",
          "pred": 0.3260949373884704,
          "actual": -0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2013-06-01",
          "pred": -0.06763207950577413,
          "actual": -0.33,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-09-01",
          "pred": -0.02151519544188979,
          "actual": -0.09,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-12-01",
          "pred": 0.15190314458342913,
          "actual": -0.09,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2014-03-01",
          "pred": 0.07705822801900153,
          "actual": -0.07,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2014-06-01",
          "pred": -0.16612830338323895,
          "actual": 0.48,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-09-01",
          "pred": -0.22998194032094632,
          "actual": 0.37,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-12-01",
          "pred": -0.08127023528784968,
          "actual": 0.77,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2015-03-01",
          "pred": -0.053137758904005024,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2015-06-01",
          "pred": -0.11796522171524237,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-09-01",
          "pred": -0.16404090107493063,
          "actual": 2.01,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-12-01",
          "pred": -0.19031378668627752,
          "actual": 2.56,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2016-03-01",
          "pred": -0.20891017295297432,
          "actual": 1.6,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2016-06-01",
          "pred": -0.3744758899369329,
          "actual": 0.06,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-09-01",
          "pred": -0.45400631826103277,
          "actual": -0.46,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-12-01",
          "pred": -0.5597110404198644,
          "actual": -0.51,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2017-03-01",
          "pred": -0.4568027616609833,
          "actual": -0.09,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2017-06-01",
          "pred": -0.44328122340737347,
          "actual": 0.22,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-09-01",
          "pred": -0.466624517586823,
          "actual": -0.56,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-12-01",
          "pred": -0.60772721644199,
          "actual": -0.85,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2018-03-01",
          "pred": -0.4124339195274508,
          "actual": -0.73,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2018-06-01",
          "pred": -0.08131218686111993,
          "actual": 0.12,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-09-01",
          "pred": 0.04632249074475603,
          "actual": 0.3,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-12-01",
          "pred": 0.18024249114336766,
          "actual": 0.97,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2019-03-01",
          "pred": 0.07323273826348131,
          "actual": 0.81,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2019-06-01",
          "pred": -0.08294611047861936,
          "actual": 0.66,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-09-01",
          "pred": 0.05779332714812138,
          "actual": 0.11,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-12-01",
          "pred": 0.12872491353404825,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2020-03-01",
          "pred": 0.17541808769812917,
          "actual": 0.36,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2020-06-01",
          "pred": -0.03970634858867972,
          "actual": -0.21,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-09-01",
          "pred": -0.07928463095510886,
          "actual": -0.66,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-12-01",
          "pred": -0.2891983853392778,
          "actual": -0.98,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2021-03-01",
          "pred": -0.3015480115918444,
          "actual": -0.72,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2021-06-01",
          "pred": -0.22546770255581278,
          "actual": -0.06,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-09-01",
          "pred": -0.010632182051202643,
          "actual": -0.5,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-12-01",
          "pred": -0.006532850505657106,
          "actual": -1.07,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2022-03-01",
          "pred": -0.009192584711078533,
          "actual": -0.84,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2022-06-01",
          "pred": 0.0778017841303284,
          "actual": -0.77,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-09-01",
          "pred": 0.1625481688461461,
          "actual": -1.06,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-12-01",
          "pred": 0.3752512021555725,
          "actual": -0.86,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2023-03-01",
          "pred": 0.26723231513379686,
          "actual": -0.13,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2023-06-01",
          "pred": 0.018490502302212386,
          "actual": 0.95,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-09-01",
          "pred": 0.09701216937860857,
          "actual": 1.65,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-12-01",
          "pred": 0.3352954818722974,
          "actual": 1.81,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2024-03-01",
          "pred": 0.22003665263940492,
          "actual": 1.1,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2024-06-01",
          "pred": 0.1328162834531783,
          "actual": 0.25,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-09-01",
          "pred": 0.16576578333904135,
          "actual": -0.11,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-12-01",
          "pred": 0.11098876781929867,
          "actual": -0.58,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2025-03-01",
          "pred": -0.11303645750693136,
          "actual": 0.05,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2025-06-01",
          "pred": -0.34649584302697944,
          "actual": 0.01,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-09-01",
          "pred": -0.5006252249794085,
          "actual": -0.3,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-12-01",
          "pred": -0.5616309982108205,
          "actual": -0.49,
          "persistence": -0.58
        }
      ],
      "24": [
        {
          "origin": "2006-09-01",
          "date": "2008-09-01",
          "pred": -0.19003233327863145,
          "actual": -0.28,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2008-12-01",
          "pred": -0.2835932522999114,
          "actual": -0.9,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2009-03-01",
          "pred": -0.0021586206269300356,
          "actual": -0.72,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2009-06-01",
          "pred": -0.021453377992625727,
          "actual": 0.49,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2009-09-01",
          "pred": 0.19813934243156672,
          "actual": 0.68,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2009-12-01",
          "pred": 0.30136526138008235,
          "actual": 1.81,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2010-03-01",
          "pred": 0.2650452686338607,
          "actual": 1.07,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2010-06-01",
          "pred": 0.06365182999360869,
          "actual": -0.62,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2010-09-01",
          "pred": 0.03769712117378615,
          "actual": -1.56,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2010-12-01",
          "pred": 0.1936132144998325,
          "actual": -1.63,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2011-03-01",
          "pred": 0.16647018481216302,
          "actual": -0.98,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2011-06-01",
          "pred": -0.09726117668382617,
          "actual": -0.25,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2011-09-01",
          "pred": -0.3038574354363499,
          "actual": -0.76,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2011-12-01",
          "pred": -0.4415132305113656,
          "actual": -1.05,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2012-03-01",
          "pred": -0.4377742650845291,
          "actual": -0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2012-06-01",
          "pred": -0.042955855082521865,
          "actual": 0.14,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2012-09-01",
          "pred": 0.3858881388463691,
          "actual": 0.44,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2012-12-01",
          "pred": 0.413027641178374,
          "actual": -0.13,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2013-03-01",
          "pred": 0.3281743469846057,
          "actual": -0.14,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2013-06-01",
          "pred": -0.1124750722633176,
          "actual": -0.33,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2013-09-01",
          "pred": -0.2541109606898383,
          "actual": -0.09,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2013-12-01",
          "pred": -0.045129946362949536,
          "actual": -0.09,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2014-03-01",
          "pred": -0.056619636384426686,
          "actual": -0.07,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2014-06-01",
          "pred": -0.20588923322526664,
          "actual": 0.48,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2014-09-01",
          "pred": -0.3904090265928583,
          "actual": 0.37,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2014-12-01",
          "pred": -0.26553351783059187,
          "actual": 0.77,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2015-03-01",
          "pred": -0.08543781432657443,
          "actual": 0.48,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2015-06-01",
          "pred": -0.12114345809031482,
          "actual": 1.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2015-09-01",
          "pred": -0.09791061850745608,
          "actual": 2.01,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2015-12-01",
          "pred": -0.14648852433766757,
          "actual": 2.56,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2016-03-01",
          "pred": -0.1298863945128564,
          "actual": 1.6,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2016-06-01",
          "pred": -0.3052650802027018,
          "actual": 0.06,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2016-09-01",
          "pred": -0.24643493405844263,
          "actual": -0.46,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2016-12-01",
          "pred": -0.29695437046407336,
          "actual": -0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2017-03-01",
          "pred": -0.26169234023929766,
          "actual": -0.09,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2017-06-01",
          "pred": -0.36342448716207065,
          "actual": 0.22,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2017-09-01",
          "pred": -0.5670084180240931,
          "actual": -0.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2017-12-01",
          "pred": -0.6160509851679485,
          "actual": -0.85,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2018-03-01",
          "pred": -0.48252305557891795,
          "actual": -0.73,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2018-06-01",
          "pred": 0.01343250849792002,
          "actual": 0.12,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2018-09-01",
          "pred": 0.2798297169165001,
          "actual": 0.3,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2018-12-01",
          "pred": 0.33424352144036085,
          "actual": 0.97,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2019-03-01",
          "pred": 0.12544559477479086,
          "actual": 0.81,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2019-06-01",
          "pred": -0.12287041936447049,
          "actual": 0.66,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2019-09-01",
          "pred": -0.040890663985941544,
          "actual": 0.11,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2019-12-01",
          "pred": 0.11413139990634924,
          "actual": 0.51,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2020-03-01",
          "pred": 0.15739842581556174,
          "actual": 0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2020-06-01",
          "pred": -0.027224610080113648,
          "actual": -0.21,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2020-09-01",
          "pred": -0.20428727090203186,
          "actual": -0.66,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2020-12-01",
          "pred": -0.37113999079903737,
          "actual": -0.98,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2021-03-01",
          "pred": -0.27478226916568693,
          "actual": -0.72,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2021-06-01",
          "pred": -0.173777153809472,
          "actual": -0.06,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2021-09-01",
          "pred": -0.04263066636269504,
          "actual": -0.5,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2021-12-01",
          "pred": -0.04730153395505177,
          "actual": -1.07,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2022-03-01",
          "pred": -0.06650552997459708,
          "actual": -0.84,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2022-06-01",
          "pred": 0.02402260216387328,
          "actual": -0.77,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2022-09-01",
          "pred": 0.10123475078778987,
          "actual": -1.06,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2022-12-01",
          "pred": 0.3564177534804063,
          "actual": -0.86,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2023-03-01",
          "pred": 0.26004469693594867,
          "actual": -0.13,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2023-06-01",
          "pred": -0.0008861123116523859,
          "actual": 0.95,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2023-09-01",
          "pred": -0.023535208038472477,
          "actual": 1.65,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2023-12-01",
          "pred": 0.14039651616401017,
          "actual": 1.81,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2024-03-01",
          "pred": 0.113467960442175,
          "actual": 1.1,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2024-06-01",
          "pred": 0.18146183227699897,
          "actual": 0.25,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2024-09-01",
          "pred": 0.12829533114095093,
          "actual": -0.11,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2024-12-01",
          "pred": 0.09324737623528911,
          "actual": -0.58,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2025-03-01",
          "pred": -0.02988948634223562,
          "actual": 0.05,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2025-06-01",
          "pred": -0.3218858495598347,
          "actual": 0.01,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2025-09-01",
          "pred": -0.5614172004508537,
          "actual": -0.3,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2025-12-01",
          "pred": -0.6193864665253246,
          "actual": -0.49,
          "persistence": 1.81
        }
      ],
      "60": [
        {
          "origin": "2006-09-01",
          "date": "2011-09-01",
          "pred": -0.03450008941603566,
          "actual": -0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2011-12-01",
          "pred": -0.06319615066836604,
          "actual": -1.05,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2012-03-01",
          "pred": -0.19307710941062683,
          "actual": -0.48,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2012-06-01",
          "pred": -0.4148069196990266,
          "actual": 0.14,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2012-09-01",
          "pred": -0.20134798433615497,
          "actual": 0.44,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2012-12-01",
          "pred": -0.3231074000700207,
          "actual": -0.13,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2013-03-01",
          "pred": -0.10171200513297851,
          "actual": -0.14,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2013-06-01",
          "pred": -0.024269608045957125,
          "actual": -0.33,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2013-09-01",
          "pred": -0.07932845711475342,
          "actual": -0.09,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2013-12-01",
          "pred": -0.10799916752534511,
          "actual": -0.09,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2014-03-01",
          "pred": -0.045699340015195045,
          "actual": -0.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2014-06-01",
          "pred": -0.09132726447498496,
          "actual": 0.48,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2014-09-01",
          "pred": -0.264254328130049,
          "actual": 0.37,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2014-12-01",
          "pred": -0.0869542398108809,
          "actual": 0.77,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2015-03-01",
          "pred": -0.25080678103351794,
          "actual": 0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2015-06-01",
          "pred": -0.4674248177035353,
          "actual": 1.28,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2015-09-01",
          "pred": -0.41444567582842784,
          "actual": 2.01,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2015-12-01",
          "pred": -0.3468303208202619,
          "actual": 2.56,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2016-03-01",
          "pred": -0.14750318410327634,
          "actual": 1.6,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2016-06-01",
          "pred": 0.004061886264103753,
          "actual": 0.06,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2016-09-01",
          "pred": -0.12622941405173027,
          "actual": -0.46,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2016-12-01",
          "pred": -0.11389536366766095,
          "actual": -0.51,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2017-03-01",
          "pred": -0.07089600174787675,
          "actual": -0.09,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2017-06-01",
          "pred": -0.13852604875311508,
          "actual": 0.22,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2017-09-01",
          "pred": -0.1498215613768315,
          "actual": -0.56,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2017-12-01",
          "pred": -0.17678190060596016,
          "actual": -0.85,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2018-03-01",
          "pred": -0.20909265470198443,
          "actual": -0.73,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2018-06-01",
          "pred": -0.2823529802644956,
          "actual": 0.12,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2018-09-01",
          "pred": -0.2727240616665717,
          "actual": 0.3,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2018-12-01",
          "pred": -0.20041067637351717,
          "actual": 0.97,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2019-03-01",
          "pred": -0.23781949626983223,
          "actual": 0.81,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2019-06-01",
          "pred": -0.18739083783206512,
          "actual": 0.66,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2019-09-01",
          "pred": -0.24821311226124732,
          "actual": 0.11,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2019-12-01",
          "pred": -0.19097597039023007,
          "actual": 0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2020-03-01",
          "pred": -0.24381886017146037,
          "actual": 0.36,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2020-06-01",
          "pred": -0.20106622450358635,
          "actual": -0.21,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2020-09-01",
          "pred": -0.20445672065948184,
          "actual": -0.66,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2020-12-01",
          "pred": -0.3216344782338294,
          "actual": -0.98,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2021-03-01",
          "pred": -0.40251268975349674,
          "actual": -0.72,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2021-06-01",
          "pred": -0.2036720884956243,
          "actual": -0.06,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2021-09-01",
          "pred": 0.03560278909894765,
          "actual": -0.5,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2021-12-01",
          "pred": 0.1311206348856263,
          "actual": -1.07,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2022-03-01",
          "pred": 0.07107108355264702,
          "actual": -0.84,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2022-06-01",
          "pred": -0.11662083299711909,
          "actual": -0.77,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2022-09-01",
          "pred": -0.18294756942550822,
          "actual": -1.06,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2022-12-01",
          "pred": -0.06600835060794252,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2023-03-01",
          "pred": 0.017757766999868196,
          "actual": -0.13,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2023-06-01",
          "pred": -0.007357197530228954,
          "actual": 0.95,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2023-09-01",
          "pred": -0.22171774810830797,
          "actual": 1.65,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2023-12-01",
          "pred": -0.24349547341358746,
          "actual": 1.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2024-03-01",
          "pred": -0.2798116900426133,
          "actual": 1.1,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2024-06-01",
          "pred": -0.18710303455222632,
          "actual": 0.25,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2024-09-01",
          "pred": -0.15417287184469292,
          "actual": -0.11,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2024-12-01",
          "pred": -0.0014019142795480555,
          "actual": -0.58,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2025-03-01",
          "pred": -0.08914060763384257,
          "actual": 0.05,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2025-06-01",
          "pred": -0.10967132155780229,
          "actual": 0.01,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2025-09-01",
          "pred": -0.0654061066835051,
          "actual": -0.3,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2025-12-01",
          "pred": 0.11856464409019907,
          "actual": -0.49,
          "persistence": -0.98
        }
      ]
    },
    "oracle_actual_future_geometry_decoder": {
      "1": [
        {
          "origin": "2006-09-01",
          "date": "2006-10-01",
          "pred": 0.28952001687647017,
          "actual": 0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-01-01",
          "pred": 1.055460348390362,
          "actual": 0.59,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-04-01",
          "pred": -0.15193882793367158,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-07-01",
          "pred": -0.0780089555774004,
          "actual": -0.37,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-10-01",
          "pred": -0.5116155801792506,
          "actual": -1.41,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-01-01",
          "pred": -0.9821035010053872,
          "actual": -1.79,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-04-01",
          "pred": -0.8271123233170087,
          "actual": -0.89,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-07-01",
          "pred": -0.9684731773684742,
          "actual": -0.04,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-10-01",
          "pred": 0.039903722310745376,
          "actual": -0.3,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-01-01",
          "pred": -0.4808716040051271,
          "actual": -1.0,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-04-01",
          "pred": -0.9812817269617312,
          "actual": -0.25,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-07-01",
          "pred": 1.0922852739540136,
          "actual": 0.69,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-10-01",
          "pred": 0.7167458142866096,
          "actual": 0.96,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-01-01",
          "pred": 1.9704781900059625,
          "actual": 1.43,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-04-01",
          "pred": 0.3413888857205821,
          "actual": 0.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-07-01",
          "pred": -0.6964029644253763,
          "actual": -0.89,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-10-01",
          "pred": -1.5218413510196314,
          "actual": -1.65,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-01-01",
          "pred": -0.9192213902205592,
          "actual": -1.7,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-04-01",
          "pred": -0.9099200891574656,
          "actual": -0.74,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-07-01",
          "pred": -0.394294413112468,
          "actual": -0.23,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-10-01",
          "pred": -0.8188128613675772,
          "actual": -0.93,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-01-01",
          "pred": -1.3011333427352838,
          "actual": -0.93,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-04-01",
          "pred": -0.445761239976736,
          "actual": -0.29,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-07-01",
          "pred": 0.21250214112499383,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-10-01",
          "pred": 0.5661610144956998,
          "actual": 0.23,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-01-01",
          "pred": 0.36969335112172286,
          "actual": -0.42,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-04-01",
          "pred": -0.6365443744457162,
          "actual": -0.08,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-07-01",
          "pred": -0.5248217621495992,
          "actual": -0.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-10-01",
          "pred": 0.08179349540574148,
          "actual": -0.24,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-01-01",
          "pred": -0.41620347780029643,
          "actual": -0.42,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-04-01",
          "pred": 0.12067793947302194,
          "actual": 0.28,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-07-01",
          "pred": 0.6853552977334204,
          "actual": 0.13,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-10-01",
          "pred": 0.4776375519714136,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-01-01",
          "pred": 0.705001077490574,
          "actual": 0.59,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-04-01",
          "pred": 0.5413194190290023,
          "actual": 0.9,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-07-01",
          "pred": 1.0154164848386926,
          "actual": 1.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-10-01",
          "pred": 2.3666239824179005,
          "actual": 2.21,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-01-01",
          "pred": 2.5318635617176155,
          "actual": 2.56,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-04-01",
          "pred": 1.4860478789455462,
          "actual": 1.05,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-07-01",
          "pred": 0.037750376569179456,
          "actual": -0.25,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-10-01",
          "pred": -0.8392689707066393,
          "actual": -0.75,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-01-01",
          "pred": -0.13941665304558565,
          "actual": -0.34,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-04-01",
          "pred": -0.007695457929526552,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-07-01",
          "pred": 0.0038334281283471583,
          "actual": 0.22,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-10-01",
          "pred": -0.5521408409257014,
          "actual": -0.52,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-01-01",
          "pred": -0.8550067658176056,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-04-01",
          "pred": 0.009210898412263559,
          "actual": -0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-07-01",
          "pred": 0.018019564380893832,
          "actual": 0.27,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-10-01",
          "pred": 0.26475541785194046,
          "actual": 0.84,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-01-01",
          "pred": 0.6658342826710272,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-04-01",
          "pred": -0.052716492320573516,
          "actual": 0.67,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-07-01",
          "pred": 0.4533718188466723,
          "actual": 0.41,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-10-01",
          "pred": 0.24772364302247765,
          "actual": 0.55,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-01-01",
          "pred": 0.5273754448558277,
          "actual": 0.64,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-04-01",
          "pred": 0.6156233822804699,
          "actual": 0.49,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-07-01",
          "pred": -0.2047859543350292,
          "actual": -0.04,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-10-01",
          "pred": -0.6785751815246017,
          "actual": -1.19,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-01-01",
          "pred": -0.9246573720462641,
          "actual": -1.04,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-04-01",
          "pred": 0.23714794426705998,
          "actual": -0.55,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-07-01",
          "pred": -0.26962780735789627,
          "actual": -0.2,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-10-01",
          "pred": -0.18184462817916816,
          "actual": -0.78,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-01-01",
          "pred": -0.23998773442504429,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-04-01",
          "pred": -0.43365644009894083,
          "actual": -0.9,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-07-01",
          "pred": -0.5735479743673844,
          "actual": -0.56,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-10-01",
          "pred": -0.6547188049775032,
          "actual": -0.99,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-01-01",
          "pred": -0.46298227792255486,
          "actual": -0.78,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-04-01",
          "pred": -0.099238082985011,
          "actual": 0.24,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-07-01",
          "pred": 0.5782826798511504,
          "actual": 1.2,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-10-01",
          "pred": 1.2058470205102134,
          "actual": 1.59,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-01-01",
          "pred": 1.4922461200134458,
          "actual": 1.71,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-04-01",
          "pred": 0.8464002983461594,
          "actual": 0.93,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-07-01",
          "pred": -0.16992858468131383,
          "actual": 0.2,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-10-01",
          "pred": 0.023909717395396313,
          "actual": -0.24,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-01-01",
          "pred": 0.402950912657876,
          "actual": -0.76,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-04-01",
          "pred": 0.43079721234943436,
          "actual": -0.08,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-07-01",
          "pred": -0.47363707468282257,
          "actual": -0.03,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-10-01",
          "pred": -0.7866945386676752,
          "actual": -0.5,
          "persistence": -0.3
        }
      ],
      "3": [
        {
          "origin": "2006-09-01",
          "date": "2006-12-01",
          "pred": 0.7425575253078013,
          "actual": 1.1,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-03-01",
          "pred": 0.6695540285337781,
          "actual": -0.15,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-06-01",
          "pred": -0.09679203754906292,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-09-01",
          "pred": 0.014837552351834102,
          "actual": -1.04,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-12-01",
          "pred": -0.523435553831615,
          "actual": -1.61,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-03-01",
          "pred": -0.15796278651327816,
          "actual": -1.17,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-06-01",
          "pred": -0.8720377107391303,
          "actual": -0.44,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-09-01",
          "pred": -1.3736647065092256,
          "actual": -0.28,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-12-01",
          "pred": 0.1890214359460987,
          "actual": -0.9,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-03-01",
          "pred": -0.35713177239818594,
          "actual": -0.72,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-06-01",
          "pred": -0.07672479939399712,
          "actual": 0.49,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-09-01",
          "pred": 1.0868218148089928,
          "actual": 0.68,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-12-01",
          "pred": 1.815272643787771,
          "actual": 1.81,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-03-01",
          "pred": 1.0732122921840408,
          "actual": 1.07,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-06-01",
          "pred": -0.4544556152619006,
          "actual": -0.62,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-09-01",
          "pred": -1.16368500848372,
          "actual": -1.56,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-12-01",
          "pred": -1.2717203639822487,
          "actual": -1.63,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-03-01",
          "pred": -0.9261550250931809,
          "actual": -0.98,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-06-01",
          "pred": -0.9027842026186133,
          "actual": -0.25,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-09-01",
          "pred": -0.21271120758326667,
          "actual": -0.76,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-12-01",
          "pred": -1.368679705155373,
          "actual": -1.05,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-03-01",
          "pred": -0.8271833432872581,
          "actual": -0.48,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-06-01",
          "pred": 0.08095659325947638,
          "actual": 0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-09-01",
          "pred": 0.6943363507790941,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-12-01",
          "pred": 0.2980365811828284,
          "actual": -0.13,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-03-01",
          "pred": -0.0904980600114921,
          "actual": -0.14,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-06-01",
          "pred": -0.7159101597225517,
          "actual": -0.33,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-09-01",
          "pred": -0.21338049207408483,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-12-01",
          "pred": -0.3860798475762358,
          "actual": -0.09,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-03-01",
          "pred": -0.26074448039325443,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-06-01",
          "pred": 0.6171387872062599,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-09-01",
          "pred": 0.9324754258357321,
          "actual": 0.37,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-12-01",
          "pred": 0.9096322131685126,
          "actual": 0.77,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-03-01",
          "pred": 0.4104709952831964,
          "actual": 0.48,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-06-01",
          "pred": 0.7836281837434107,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-09-01",
          "pred": 1.7939781820593248,
          "actual": 2.01,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-12-01",
          "pred": 2.422561076991932,
          "actual": 2.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-03-01",
          "pred": 2.232452564027106,
          "actual": 1.6,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-06-01",
          "pred": 0.754113357061262,
          "actual": 0.06,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-09-01",
          "pred": -0.5536961131080097,
          "actual": -0.46,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-12-01",
          "pred": -0.45395369290020166,
          "actual": -0.51,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-03-01",
          "pred": -0.014626995038483283,
          "actual": -0.09,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-06-01",
          "pred": -0.12918108389127259,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-09-01",
          "pred": -0.24389407188518417,
          "actual": -0.56,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-12-01",
          "pred": -0.5820990727318636,
          "actual": -0.85,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-03-01",
          "pred": -0.023981488727062114,
          "actual": -0.73,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-06-01",
          "pred": 0.07457293703849621,
          "actual": 0.12,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-09-01",
          "pred": 0.0829816991004797,
          "actual": 0.3,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-12-01",
          "pred": 0.555977262711412,
          "actual": 0.97,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-03-01",
          "pred": 0.11202077192115853,
          "actual": 0.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-06-01",
          "pred": -0.0025930180393174424,
          "actual": 0.66,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-09-01",
          "pred": 0.1228204996220002,
          "actual": 0.11,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-12-01",
          "pred": 0.33257412910952605,
          "actual": 0.51,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-03-01",
          "pred": 0.27548822574876564,
          "actual": 0.36,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-06-01",
          "pred": 0.2367827953595926,
          "actual": -0.21,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-09-01",
          "pred": -0.3732279172270215,
          "actual": -0.66,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-12-01",
          "pred": -0.635054704169351,
          "actual": -0.98,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-03-01",
          "pred": -0.1342683037831754,
          "actual": -0.72,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-06-01",
          "pred": 0.43790018113357176,
          "actual": -0.06,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-09-01",
          "pred": -0.4206530094752961,
          "actual": -0.5,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-12-01",
          "pred": -0.22967309036790343,
          "actual": -1.07,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-03-01",
          "pred": -0.3181781307076927,
          "actual": -0.84,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-06-01",
          "pred": -0.42125156147968884,
          "actual": -0.77,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-09-01",
          "pred": -0.1812369401268859,
          "actual": -1.06,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-12-01",
          "pred": -0.9030013318985418,
          "actual": -0.86,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-03-01",
          "pred": -0.4967567140559883,
          "actual": -0.13,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-06-01",
          "pred": 0.1526998454990308,
          "actual": 0.95,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-09-01",
          "pred": 0.5596765658409892,
          "actual": 1.65,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-12-01",
          "pred": 1.4333775411482093,
          "actual": 1.81,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-03-01",
          "pred": 0.9754178057880135,
          "actual": 1.1,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-06-01",
          "pred": -0.17735222797432382,
          "actual": 0.25,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-09-01",
          "pred": -0.3945454859846701,
          "actual": -0.11,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-12-01",
          "pred": 0.4085299235446779,
          "actual": -0.58,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-03-01",
          "pred": 0.8566467633550366,
          "actual": 0.05,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-06-01",
          "pred": 0.30302577667221914,
          "actual": 0.01,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-09-01",
          "pred": -0.7426339183354944,
          "actual": -0.3,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-12-01",
          "pred": -1.249445389239205,
          "actual": -0.49,
          "persistence": -0.3
        }
      ],
      "6": [
        {
          "origin": "2006-09-01",
          "date": "2007-03-01",
          "pred": 0.5095662210633258,
          "actual": -0.15,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-06-01",
          "pred": 0.1371926205734271,
          "actual": -0.16,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-09-01",
          "pred": -0.0061964313043802455,
          "actual": -1.04,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-12-01",
          "pred": -0.32507679346158247,
          "actual": -1.61,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-03-01",
          "pred": 0.2908440261823979,
          "actual": -1.17,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-06-01",
          "pred": -0.21209158816976112,
          "actual": -0.44,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-09-01",
          "pred": -1.4488408709032348,
          "actual": -0.28,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-12-01",
          "pred": -1.0763487623245276,
          "actual": -0.9,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-03-01",
          "pred": -0.10102052531251737,
          "actual": -0.72,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-06-01",
          "pred": 0.21827951159201797,
          "actual": 0.49,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-09-01",
          "pred": 0.5538194016480821,
          "actual": 0.68,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-12-01",
          "pred": 2.2001545572734114,
          "actual": 1.81,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-03-01",
          "pred": 1.0256424176331793,
          "actual": 1.07,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-06-01",
          "pred": -0.3517833426048457,
          "actual": -0.62,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-09-01",
          "pred": -1.196515866546939,
          "actual": -1.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-12-01",
          "pred": -1.0979400356029185,
          "actual": -1.63,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-03-01",
          "pred": -0.8149118496388463,
          "actual": -0.98,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-06-01",
          "pred": -0.581459436242949,
          "actual": -0.25,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-09-01",
          "pred": -0.47001326468800986,
          "actual": -0.76,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-12-01",
          "pred": -1.2498947033362104,
          "actual": -1.05,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-03-01",
          "pred": -0.81778646551257,
          "actual": -0.48,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-06-01",
          "pred": -0.17016516996570746,
          "actual": 0.14,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-09-01",
          "pred": 0.6977423097396052,
          "actual": 0.44,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-12-01",
          "pred": 0.20320280084234071,
          "actual": -0.13,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-03-01",
          "pred": 0.033616527596772375,
          "actual": -0.14,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-06-01",
          "pred": -0.26883596549028077,
          "actual": -0.33,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-09-01",
          "pred": -0.4438536154819577,
          "actual": -0.09,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-12-01",
          "pred": -0.4919846231412386,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-03-01",
          "pred": -0.20554981879323267,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-06-01",
          "pred": 0.65911565662239,
          "actual": 0.48,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-09-01",
          "pred": 0.88883147764031,
          "actual": 0.37,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-12-01",
          "pred": 1.3112663806203941,
          "actual": 0.77,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-03-01",
          "pred": 0.40391577659078853,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-06-01",
          "pred": 0.8128597530324998,
          "actual": 1.28,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-09-01",
          "pred": 1.5348768303420792,
          "actual": 2.01,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-12-01",
          "pred": 2.100878522702479,
          "actual": 2.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-03-01",
          "pred": 2.096611494722835,
          "actual": 1.6,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-06-01",
          "pred": 0.9829554048315188,
          "actual": 0.06,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-09-01",
          "pred": -0.12106133189879043,
          "actual": -0.46,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-12-01",
          "pred": -0.26139701291657147,
          "actual": -0.51,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-03-01",
          "pred": -0.11404632650384038,
          "actual": -0.09,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-06-01",
          "pred": -0.13076944300028964,
          "actual": 0.22,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-09-01",
          "pred": -0.47707454544906525,
          "actual": -0.56,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-12-01",
          "pred": -0.6056135663463924,
          "actual": -0.85,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-03-01",
          "pred": 0.06564785333064865,
          "actual": -0.73,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-06-01",
          "pred": 0.2002374770856384,
          "actual": 0.12,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-09-01",
          "pred": 0.2964625617040271,
          "actual": 0.3,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-12-01",
          "pred": 0.3964310280385701,
          "actual": 0.97,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-03-01",
          "pred": -0.23231065195969747,
          "actual": 0.81,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-06-01",
          "pred": -0.12566849842547648,
          "actual": 0.66,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-09-01",
          "pred": -0.3401286273553347,
          "actual": 0.11,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-12-01",
          "pred": 0.3510981864461334,
          "actual": 0.51,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-03-01",
          "pred": 0.044078539079578274,
          "actual": 0.36,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-06-01",
          "pred": 0.11297037756481279,
          "actual": -0.21,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-09-01",
          "pred": -0.09977369053285008,
          "actual": -0.66,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-12-01",
          "pred": -0.6122584265590836,
          "actual": -0.98,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-03-01",
          "pred": 0.044709203252456725,
          "actual": -0.72,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-06-01",
          "pred": 0.49348174092176017,
          "actual": -0.06,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-09-01",
          "pred": 0.21692961853679787,
          "actual": -0.5,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-12-01",
          "pred": -0.3089421435355193,
          "actual": -1.07,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-03-01",
          "pred": 0.010001457707968658,
          "actual": -0.84,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-06-01",
          "pred": -0.19924028862054594,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-09-01",
          "pred": 0.024386023984061922,
          "actual": -1.06,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-12-01",
          "pred": -0.6283656825212885,
          "actual": -0.86,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-03-01",
          "pred": -0.6239631358408424,
          "actual": -0.13,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-06-01",
          "pred": 0.19900703384476887,
          "actual": 0.95,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-09-01",
          "pred": 0.3796048441114463,
          "actual": 1.65,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-12-01",
          "pred": 0.949769503724332,
          "actual": 1.81,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-03-01",
          "pred": 0.6693211673398818,
          "actual": 1.1,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-06-01",
          "pred": -0.3070301310125315,
          "actual": 0.25,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-09-01",
          "pred": -0.43126967630359925,
          "actual": -0.11,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-12-01",
          "pred": 0.2504575329968231,
          "actual": -0.58,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-03-01",
          "pred": 1.0374182680580981,
          "actual": 0.05,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-06-01",
          "pred": 0.8927484586834464,
          "actual": 0.01,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-09-01",
          "pred": -0.568199273302723,
          "actual": -0.3,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-12-01",
          "pred": -1.4449078904010775,
          "actual": -0.49,
          "persistence": 0.01
        }
      ],
      "12": [
        {
          "origin": "2006-09-01",
          "date": "2007-09-01",
          "pred": -0.048834227985130506,
          "actual": -1.04,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-12-01",
          "pred": -0.07337661935907983,
          "actual": -1.61,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2008-03-01",
          "pred": 0.5909883580243787,
          "actual": -1.17,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2008-06-01",
          "pred": 0.6037388355402625,
          "actual": -0.44,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-09-01",
          "pred": -0.4787801167270694,
          "actual": -0.28,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-12-01",
          "pred": -0.7841043367522097,
          "actual": -0.9,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2009-03-01",
          "pred": -1.3520096318764903,
          "actual": -0.72,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2009-06-01",
          "pred": -0.604813277510003,
          "actual": 0.49,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-09-01",
          "pred": 0.8911458743015828,
          "actual": 0.68,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-12-01",
          "pred": 1.814665063207235,
          "actual": 1.81,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2010-03-01",
          "pred": 1.041716924536072,
          "actual": 1.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2010-06-01",
          "pred": -0.16568014116271457,
          "actual": -0.62,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-09-01",
          "pred": -1.141737646877837,
          "actual": -1.56,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-12-01",
          "pred": -1.0255992262605007,
          "actual": -1.63,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2011-03-01",
          "pred": -0.6871474659081155,
          "actual": -0.98,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2011-06-01",
          "pred": -0.3314543772924965,
          "actual": -0.25,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-09-01",
          "pred": -0.019692551478028456,
          "actual": -0.76,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-12-01",
          "pred": -1.0904441076079026,
          "actual": -1.05,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2012-03-01",
          "pred": -0.8938568268746393,
          "actual": -0.48,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2012-06-01",
          "pred": 0.01392477182622913,
          "actual": 0.14,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-09-01",
          "pred": 0.4978152020571595,
          "actual": 0.44,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-12-01",
          "pred": -0.07916050711529947,
          "actual": -0.13,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2013-03-01",
          "pred": -0.054072399453960265,
          "actual": -0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2013-06-01",
          "pred": -0.22907484150191348,
          "actual": -0.33,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-09-01",
          "pred": -0.0021381546616131147,
          "actual": -0.09,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-12-01",
          "pred": -0.4499170463526852,
          "actual": -0.09,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2014-03-01",
          "pred": -0.417015986233468,
          "actual": -0.07,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2014-06-01",
          "pred": 0.590922553880999,
          "actual": 0.48,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-09-01",
          "pred": 1.024533418331982,
          "actual": 0.37,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-12-01",
          "pred": 1.3813566780831663,
          "actual": 0.77,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2015-03-01",
          "pred": 0.7055055976820154,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2015-06-01",
          "pred": 1.0710787034570823,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-09-01",
          "pred": 1.526469312969932,
          "actual": 2.01,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-12-01",
          "pred": 1.8567567060562573,
          "actual": 2.56,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2016-03-01",
          "pred": 1.5796396208447234,
          "actual": 1.6,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2016-06-01",
          "pred": 0.5322581361402805,
          "actual": 0.06,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-09-01",
          "pred": -0.00905844740096906,
          "actual": -0.46,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-12-01",
          "pred": 0.28164438085817867,
          "actual": -0.51,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2017-03-01",
          "pred": 0.41889372203738384,
          "actual": -0.09,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2017-06-01",
          "pred": -0.08214907037284386,
          "actual": 0.22,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-09-01",
          "pred": -0.6266793334394137,
          "actual": -0.56,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-12-01",
          "pred": -0.8435239672532111,
          "actual": -0.85,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2018-03-01",
          "pred": -0.1116690432817337,
          "actual": -0.73,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2018-06-01",
          "pred": 0.2579453920686405,
          "actual": 0.12,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-09-01",
          "pred": 0.5114196288404033,
          "actual": 0.3,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-12-01",
          "pred": 0.8116053352188066,
          "actual": 0.97,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2019-03-01",
          "pred": -0.21347174516092585,
          "actual": 0.81,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2019-06-01",
          "pred": -0.6808314598908574,
          "actual": 0.66,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-09-01",
          "pred": -0.9045219001239784,
          "actual": 0.11,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-12-01",
          "pred": -0.14179852798875542,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2020-03-01",
          "pred": -0.3258475077349998,
          "actual": 0.36,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2020-06-01",
          "pred": -0.11408260941805837,
          "actual": -0.21,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-09-01",
          "pred": -0.43625916997939657,
          "actual": -0.66,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-12-01",
          "pred": -0.44602528440627554,
          "actual": -0.98,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2021-03-01",
          "pred": 0.30508271345970656,
          "actual": -0.72,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2021-06-01",
          "pred": 0.709567193232406,
          "actual": -0.06,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-09-01",
          "pred": 0.4165037912452124,
          "actual": -0.5,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-12-01",
          "pred": 0.343452253237297,
          "actual": -1.07,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2022-03-01",
          "pred": 0.45869015399808716,
          "actual": -0.84,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2022-06-01",
          "pred": -0.045322519283282396,
          "actual": -0.77,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-09-01",
          "pred": 0.4452304526063688,
          "actual": -1.06,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-12-01",
          "pred": -0.2407638973215786,
          "actual": -0.86,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2023-03-01",
          "pred": -0.17319130164887891,
          "actual": -0.13,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2023-06-01",
          "pred": 0.29678559799792376,
          "actual": 0.95,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-09-01",
          "pred": 0.30271979890774764,
          "actual": 1.65,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-12-01",
          "pred": 0.7798517966330443,
          "actual": 1.81,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2024-03-01",
          "pred": 0.07464604477636991,
          "actual": 1.1,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2024-06-01",
          "pred": -0.9627018456352389,
          "actual": 0.25,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-09-01",
          "pred": -0.7771947839656703,
          "actual": -0.11,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-12-01",
          "pred": 0.12003008068656315,
          "actual": -0.58,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2025-03-01",
          "pred": 0.873321407561161,
          "actual": 0.05,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2025-06-01",
          "pred": 0.9249889091996967,
          "actual": 0.01,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-09-01",
          "pred": 0.10315939912069594,
          "actual": -0.3,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-12-01",
          "pred": -0.6869341009296581,
          "actual": -0.49,
          "persistence": -0.58
        }
      ],
      "24": [
        {
          "origin": "2006-09-01",
          "date": "2008-09-01",
          "pred": -0.07231367260200987,
          "actual": -0.28,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2008-12-01",
          "pred": 0.4360827284780729,
          "actual": -0.9,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2009-03-01",
          "pred": 0.08471569424317363,
          "actual": -0.72,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2009-06-01",
          "pred": 1.1178977750413677,
          "actual": 0.49,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2009-09-01",
          "pred": 1.0965002438817788,
          "actual": 0.68,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2009-12-01",
          "pred": 1.5712962092213745,
          "actual": 1.81,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2010-03-01",
          "pred": 0.7914930999274951,
          "actual": 1.07,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2010-06-01",
          "pred": -0.837900845981771,
          "actual": -0.62,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2010-09-01",
          "pred": -1.0377185687263923,
          "actual": -1.56,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2010-12-01",
          "pred": -1.0602298182263343,
          "actual": -1.63,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2011-03-01",
          "pred": -0.5489450266312457,
          "actual": -0.98,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2011-06-01",
          "pred": -0.018185446201877335,
          "actual": -0.25,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2011-09-01",
          "pred": 0.1836879453723977,
          "actual": -0.76,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2011-12-01",
          "pred": -0.7799666740820892,
          "actual": -1.05,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2012-03-01",
          "pred": -0.2759078465942473,
          "actual": -0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2012-06-01",
          "pred": 0.3867184571364096,
          "actual": 0.14,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2012-09-01",
          "pred": 0.8543513311302169,
          "actual": 0.44,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2012-12-01",
          "pred": 0.1833177887183777,
          "actual": -0.13,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2013-03-01",
          "pred": -0.3000701521850825,
          "actual": -0.14,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2013-06-01",
          "pred": -0.47671961531999824,
          "actual": -0.33,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2013-09-01",
          "pred": -0.20542545360898312,
          "actual": -0.09,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2013-12-01",
          "pred": -0.5586765276059072,
          "actual": -0.09,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2014-03-01",
          "pred": -0.11224366729613931,
          "actual": -0.07,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2014-06-01",
          "pred": 0.46206650027488855,
          "actual": 0.48,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2014-09-01",
          "pred": 0.937431761904004,
          "actual": 0.37,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2014-12-01",
          "pred": 1.3067267953238502,
          "actual": 0.77,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2015-03-01",
          "pred": 0.6170260588321628,
          "actual": 0.48,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2015-06-01",
          "pred": 1.0247463751730377,
          "actual": 1.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2015-09-01",
          "pred": 1.7751648608197894,
          "actual": 2.01,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2015-12-01",
          "pred": 2.019476413587144,
          "actual": 2.56,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2016-03-01",
          "pred": 1.635855731153125,
          "actual": 1.6,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2016-06-01",
          "pred": 0.5511314704666325,
          "actual": 0.06,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2016-09-01",
          "pred": -0.4364649584708073,
          "actual": -0.46,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2016-12-01",
          "pred": -0.07900947882308898,
          "actual": -0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2017-03-01",
          "pred": 0.2600326042323192,
          "actual": -0.09,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2017-06-01",
          "pred": 0.19136401078096044,
          "actual": 0.22,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2017-09-01",
          "pred": -0.1651166563224774,
          "actual": -0.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2017-12-01",
          "pred": -0.4604121131051716,
          "actual": -0.85,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2018-03-01",
          "pred": 0.07033583224616519,
          "actual": -0.73,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2018-06-01",
          "pred": 0.04829828119664524,
          "actual": 0.12,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2018-09-01",
          "pred": 0.1663899662135936,
          "actual": 0.3,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2018-12-01",
          "pred": 0.729569595628957,
          "actual": 0.97,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2019-03-01",
          "pred": -0.1722891331600598,
          "actual": 0.81,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2019-06-01",
          "pred": -0.2828856866831491,
          "actual": 0.66,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2019-09-01",
          "pred": -0.6144169842100485,
          "actual": 0.11,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2019-12-01",
          "pred": -0.30285075105685866,
          "actual": 0.51,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2020-03-01",
          "pred": -0.9195163580982916,
          "actual": 0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2020-06-01",
          "pred": -1.3672689514355172,
          "actual": -0.21,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2020-09-01",
          "pred": -1.3975276346386123,
          "actual": -0.66,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2020-12-01",
          "pred": -1.089278361028069,
          "actual": -0.98,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2021-03-01",
          "pred": -0.37564974487048775,
          "actual": -0.72,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2021-06-01",
          "pred": 0.6667215487742337,
          "actual": -0.06,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2021-09-01",
          "pred": 0.3650123031521946,
          "actual": -0.5,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2021-12-01",
          "pred": 0.6628536902499409,
          "actual": -1.07,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2022-03-01",
          "pred": 0.8787756306254997,
          "actual": -0.84,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2022-06-01",
          "pred": 0.6870706606311188,
          "actual": -0.77,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2022-09-01",
          "pred": 1.0838162924090775,
          "actual": -1.06,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2022-12-01",
          "pred": 0.412960354790035,
          "actual": -0.86,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2023-03-01",
          "pred": 0.617384226620793,
          "actual": -0.13,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2023-06-01",
          "pred": 0.7041343166191338,
          "actual": 0.95,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2023-09-01",
          "pred": 0.9153262907710414,
          "actual": 1.65,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2023-12-01",
          "pred": 1.017533853971514,
          "actual": 1.81,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2024-03-01",
          "pred": 0.16436336471359347,
          "actual": 1.1,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2024-06-01",
          "pred": -0.9691478419201408,
          "actual": 0.25,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2024-09-01",
          "pred": -1.2919451218355893,
          "actual": -0.11,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2024-12-01",
          "pred": -0.6014179448377558,
          "actual": -0.58,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2025-03-01",
          "pred": 0.021942485488121548,
          "actual": 0.05,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2025-06-01",
          "pred": 0.2257466012754436,
          "actual": 0.01,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2025-09-01",
          "pred": -0.30310907390559444,
          "actual": -0.3,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2025-12-01",
          "pred": -0.678711394954728,
          "actual": -0.49,
          "persistence": 1.81
        }
      ],
      "60": [
        {
          "origin": "2006-09-01",
          "date": "2011-09-01",
          "pred": 0.0988243151694689,
          "actual": -0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2011-12-01",
          "pred": -0.7411714516368224,
          "actual": -1.05,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2012-03-01",
          "pred": -0.020095026621316597,
          "actual": -0.48,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2012-06-01",
          "pred": 0.5165360122334267,
          "actual": 0.14,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2012-09-01",
          "pred": 1.1246461047420062,
          "actual": 0.44,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2012-12-01",
          "pred": 0.4736297867004493,
          "actual": -0.13,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2013-03-01",
          "pred": 0.27660969140878167,
          "actual": -0.14,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2013-06-01",
          "pred": 0.1550072224773594,
          "actual": -0.33,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2013-09-01",
          "pred": 0.2626613490399001,
          "actual": -0.09,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2013-12-01",
          "pred": 0.006578912725089439,
          "actual": -0.09,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2014-03-01",
          "pred": 0.0878636336501489,
          "actual": -0.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2014-06-01",
          "pred": 1.1604048178243243,
          "actual": 0.48,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2014-09-01",
          "pred": 1.2927611316621785,
          "actual": 0.37,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2014-12-01",
          "pred": 1.5462158286476668,
          "actual": 0.77,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2015-03-01",
          "pred": 0.9923231280805027,
          "actual": 0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2015-06-01",
          "pred": 1.2640512953023433,
          "actual": 1.28,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2015-09-01",
          "pred": 1.7055730804432645,
          "actual": 2.01,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2015-12-01",
          "pred": 2.149694308616288,
          "actual": 2.56,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2016-03-01",
          "pred": 1.5787985436187164,
          "actual": 1.6,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2016-06-01",
          "pred": 0.2866074442593762,
          "actual": 0.06,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2016-09-01",
          "pred": -0.7303041882773273,
          "actual": -0.46,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2016-12-01",
          "pred": -0.30962965819575555,
          "actual": -0.51,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2017-03-01",
          "pred": 0.3515554809212813,
          "actual": -0.09,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2017-06-01",
          "pred": -0.029063463324711783,
          "actual": 0.22,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2017-09-01",
          "pred": -0.4291288263880988,
          "actual": -0.56,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2017-12-01",
          "pred": -0.8222993976515192,
          "actual": -0.85,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2018-03-01",
          "pred": -0.3928774183508727,
          "actual": -0.73,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2018-06-01",
          "pred": -0.12758907661972113,
          "actual": 0.12,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2018-09-01",
          "pred": 0.22001014355721815,
          "actual": 0.3,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2018-12-01",
          "pred": 0.4299970992680194,
          "actual": 0.97,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2019-03-01",
          "pred": -0.3821495259112171,
          "actual": 0.81,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2019-06-01",
          "pred": -0.5785390087859663,
          "actual": 0.66,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2019-09-01",
          "pred": -1.0667820456753148,
          "actual": 0.11,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2019-12-01",
          "pred": -0.7952775956550111,
          "actual": 0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2020-03-01",
          "pred": -1.1336777758521026,
          "actual": 0.36,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2020-06-01",
          "pred": -1.2601432953387035,
          "actual": -0.21,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2020-09-01",
          "pred": -1.2386352068766953,
          "actual": -0.66,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2020-12-01",
          "pred": -1.3496205284895473,
          "actual": -0.98,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2021-03-01",
          "pred": -0.8863478185618882,
          "actual": -0.72,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2021-06-01",
          "pred": -0.1901869164379763,
          "actual": -0.06,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2021-09-01",
          "pred": -0.34352849820001535,
          "actual": -0.5,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2021-12-01",
          "pred": -0.16236395262917344,
          "actual": -1.07,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2022-03-01",
          "pred": 0.0671751146036795,
          "actual": -0.84,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2022-06-01",
          "pred": 0.12315646717832068,
          "actual": -0.77,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2022-09-01",
          "pred": 0.5063773404671378,
          "actual": -1.06,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2022-12-01",
          "pred": -0.4033723713166544,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2023-03-01",
          "pred": -0.24603914399208032,
          "actual": -0.13,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2023-06-01",
          "pred": 0.34221914680778354,
          "actual": 0.95,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2023-09-01",
          "pred": 0.6473662760930582,
          "actual": 1.65,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2023-12-01",
          "pred": 1.3160565916215734,
          "actual": 1.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2024-03-01",
          "pred": 0.7389073428757031,
          "actual": 1.1,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2024-06-01",
          "pred": -0.015950221563601163,
          "actual": 0.25,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2024-09-01",
          "pred": -0.36129557060881806,
          "actual": -0.11,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2024-12-01",
          "pred": 0.09940031670708419,
          "actual": -0.58,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2025-03-01",
          "pred": 0.7422267624297602,
          "actual": 0.05,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2025-06-01",
          "pred": 0.8867163035748201,
          "actual": 0.01,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2025-09-01",
          "pred": 0.2114388688121252,
          "actual": -0.3,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2025-12-01",
          "pred": -0.2041467945111618,
          "actual": -0.49,
          "persistence": -0.98
        }
      ]
    }
  },
  "elapsed_seconds": 254.128
};
