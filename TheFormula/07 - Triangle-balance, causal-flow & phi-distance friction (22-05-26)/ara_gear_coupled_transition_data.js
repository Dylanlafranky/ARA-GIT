window.ARA_GEAR_COUPLED_TRANSITION = {
  "date": "2026-05-22",
  "method": "strict-causal ARA gear-coupled geometry transition ENSO test",
  "leakage_guard": "At origin t, decoder training uses only geometry anchors a<t. Lag baseline uses only s+h<t. Deterministic projections use only geometry at origin.",
  "gear_rule": "cross-system incoming_phase = (2 * release_fraction(target_ara) - source_phase) mod 1",
  "system": "ENSO",
  "target": "NINO3.4 anomaly",
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
  "min_train_examples": 96,
  "origin_stride_months": 3,
  "models": {
    "natural_advance_decoder": "Advance phases naturally, then decode geometry.",
    "sync_event_cascade_decoder": "Existing event cascade: cross-system incoming phase is copied from source.",
    "gear_event_cascade_decoder": "Gear event cascade: cross-system phase is mirrored around the target ARA release gate.",
    "same_rung_sync_pair_decoder": "Same-rung cross-system pair coupling with copied source phase.",
    "same_rung_gear_pair_decoder": "Same-rung cross-system pair coupling with mirrored gear phase around the target ARA release gate.",
    "lag_ridge": "Control: causal target lags and slopes.",
    "oracle_actual_future_geometry_decoder": "Diagnostic only: decode actual future geometry."
  },
  "scores": {
    "natural_advance_decoder": {
      "1": {
        "n": 77,
        "mae": 0.39934443106966483,
        "rmse": 0.5019049345141732,
        "corr": 0.830228294748296,
        "direction": 0.4155844155844156,
        "persistence_mae": 0.2149350649350649,
        "mae_lift_vs_persistence": -0.18440936613459993,
        "r2_vs_persistence": -2.7503063307563833,
        "pred_delta_std": 0.41611768433613555,
        "truth_delta_std": 0.2590805908826503
      },
      "3": {
        "n": 77,
        "mae": 0.6876639555423958,
        "rmse": 0.8415745766243276,
        "corr": 0.5736534711575607,
        "direction": 0.5194805194805194,
        "persistence_mae": 0.49103896103896105,
        "mae_lift_vs_persistence": -0.19662499450343474,
        "r2_vs_persistence": -0.9392939158700067,
        "pred_delta_std": 0.6857934123349356,
        "truth_delta_std": 0.6041533595330312
      },
      "6": {
        "n": 76,
        "mae": 0.8971730772883842,
        "rmse": 1.1066523388113123,
        "corr": 0.33916125351152804,
        "direction": 0.5921052631578947,
        "persistence_mae": 0.7817105263157895,
        "mae_lift_vs_persistence": -0.11546255097259472,
        "r2_vs_persistence": -0.2812587749795592,
        "pred_delta_std": 1.0255722901043047,
        "truth_delta_std": 0.9771131213626487
      },
      "12": {
        "n": 74,
        "mae": 1.1182255969749801,
        "rmse": 1.4163071748788065,
        "corr": -0.0004968640211284133,
        "direction": 0.6351351351351351,
        "persistence_mae": 1.005135135135135,
        "mae_lift_vs_persistence": -0.11309046183984517,
        "r2_vs_persistence": -0.1925225187458286,
        "pred_delta_std": 1.1229945001153026,
        "truth_delta_std": 1.2966303184080832
      },
      "24": {
        "n": 70,
        "mae": 1.1567824748354194,
        "rmse": 1.377248019704325,
        "corr": 0.12776712617181052,
        "direction": 0.7142857142857143,
        "persistence_mae": 1.1871428571428573,
        "mae_lift_vs_persistence": 0.030360382307437872,
        "r2_vs_persistence": 0.08652899231969957,
        "pred_delta_std": 1.4162963481124962,
        "truth_delta_std": 1.44045525683333
      },
      "60": {
        "n": 58,
        "mae": 1.2769424135806609,
        "rmse": 1.525148674775879,
        "corr": -0.008601404957503389,
        "direction": 0.4827586206896552,
        "persistence_mae": 0.8901724137931035,
        "mae_lift_vs_persistence": -0.38676999978755733,
        "r2_vs_persistence": -0.4158086920875932,
        "pred_delta_std": 1.2776319032227927,
        "truth_delta_std": 1.279847096712392
      }
    },
    "sync_event_cascade_decoder": {
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
    "gear_event_cascade_decoder": {
      "1": {
        "n": 77,
        "mae": 0.3991444131283192,
        "rmse": 0.5013399763436066,
        "corr": 0.8301557922116576,
        "direction": 0.4155844155844156,
        "persistence_mae": 0.2149350649350649,
        "mae_lift_vs_persistence": -0.18420934819325432,
        "r2_vs_persistence": -2.741868184059863,
        "pred_delta_std": 0.41585492909162447,
        "truth_delta_std": 0.2590805908826503
      },
      "3": {
        "n": 77,
        "mae": 0.6832144532499119,
        "rmse": 0.8384626013644101,
        "corr": 0.5728603537213038,
        "direction": 0.5194805194805194,
        "persistence_mae": 0.49103896103896105,
        "mae_lift_vs_persistence": -0.19217549221095087,
        "r2_vs_persistence": -0.9249781875275711,
        "pred_delta_std": 0.682697590613052,
        "truth_delta_std": 0.6041533595330312
      },
      "6": {
        "n": 76,
        "mae": 0.8881998450542585,
        "rmse": 1.098157060184506,
        "corr": 0.3389021413685119,
        "direction": 0.6052631578947368,
        "persistence_mae": 0.7817105263157895,
        "mae_lift_vs_persistence": -0.10648931873846901,
        "r2_vs_persistence": -0.2616629695172459,
        "pred_delta_std": 1.023876842881376,
        "truth_delta_std": 0.9771131213626487
      },
      "12": {
        "n": 74,
        "mae": 1.1136993564230573,
        "rmse": 1.4143489230165331,
        "corr": 0.014421420566222535,
        "direction": 0.6351351351351351,
        "persistence_mae": 1.005135135135135,
        "mae_lift_vs_persistence": -0.10856422128792231,
        "r2_vs_persistence": -0.18922712482899318,
        "pred_delta_std": 1.1502541547890193,
        "truth_delta_std": 1.2966303184080832
      },
      "24": {
        "n": 70,
        "mae": 1.1627999909455575,
        "rmse": 1.3723563676779744,
        "corr": 0.14684622065935918,
        "direction": 0.7142857142857143,
        "persistence_mae": 1.1871428571428573,
        "mae_lift_vs_persistence": 0.02434286619729975,
        "r2_vs_persistence": 0.0930063252837563,
        "pred_delta_std": 1.4449475446240612,
        "truth_delta_std": 1.44045525683333
      },
      "60": {
        "n": 58,
        "mae": 1.1489554040339418,
        "rmse": 1.441971780096998,
        "corr": 0.002650014176386378,
        "direction": 0.5344827586206896,
        "persistence_mae": 0.8901724137931035,
        "mae_lift_vs_persistence": -0.2587829902408383,
        "r2_vs_persistence": -0.26559203575790247,
        "pred_delta_std": 1.2024659980788377,
        "truth_delta_std": 1.279847096712392
      }
    },
    "same_rung_sync_pair_decoder": {
      "1": {
        "n": 77,
        "mae": 0.3998624718084092,
        "rmse": 0.5022871078167902,
        "corr": 0.829780806295937,
        "direction": 0.4155844155844156,
        "persistence_mae": 0.2149350649350649,
        "mae_lift_vs_persistence": -0.18492740687334433,
        "r2_vs_persistence": -2.7560198136694187,
        "pred_delta_std": 0.4164876943593628,
        "truth_delta_std": 0.2590805908826503
      },
      "3": {
        "n": 77,
        "mae": 0.686624626700267,
        "rmse": 0.841250095803076,
        "corr": 0.5718667108980656,
        "direction": 0.5194805194805194,
        "persistence_mae": 0.49103896103896105,
        "mae_lift_vs_persistence": -0.19558566566130597,
        "r2_vs_persistence": -0.9377987605046998,
        "pred_delta_std": 0.6854381396981619,
        "truth_delta_std": 0.6041533595330312
      },
      "6": {
        "n": 76,
        "mae": 0.9033897031832772,
        "rmse": 1.1110916471592849,
        "corr": 0.33061357528223945,
        "direction": 0.6052631578947368,
        "persistence_mae": 0.7817105263157895,
        "mae_lift_vs_persistence": -0.12167917686748764,
        "r2_vs_persistence": -0.2915588683622723,
        "pred_delta_std": 1.0265157361046704,
        "truth_delta_std": 0.9771131213626487
      },
      "12": {
        "n": 74,
        "mae": 1.1149399205732369,
        "rmse": 1.4187714892229777,
        "corr": -0.006771163593163022,
        "direction": 0.6351351351351351,
        "persistence_mae": 1.005135135135135,
        "mae_lift_vs_persistence": -0.1098047854381019,
        "r2_vs_persistence": -0.1966760061407562,
        "pred_delta_std": 1.1276064865753777,
        "truth_delta_std": 1.2966303184080832
      },
      "24": {
        "n": 70,
        "mae": 1.1508749188513039,
        "rmse": 1.368329582335897,
        "corr": 0.1308095508403899,
        "direction": 0.7285714285714285,
        "persistence_mae": 1.1871428571428573,
        "mae_lift_vs_persistence": 0.03626793829155339,
        "r2_vs_persistence": 0.09832114095989575,
        "pred_delta_std": 1.4212912155802224,
        "truth_delta_std": 1.44045525683333
      },
      "60": {
        "n": 58,
        "mae": 1.2359150969437822,
        "rmse": 1.5064649605775888,
        "corr": -0.004450500287515782,
        "direction": 0.5,
        "persistence_mae": 0.8901724137931035,
        "mae_lift_vs_persistence": -0.3457426831506787,
        "r2_vs_persistence": -0.381332659866934,
        "pred_delta_std": 1.291678164858839,
        "truth_delta_std": 1.279847096712392
      }
    },
    "same_rung_gear_pair_decoder": {
      "1": {
        "n": 77,
        "mae": 0.3995420409735446,
        "rmse": 0.502560576953704,
        "corr": 0.8296974340979935,
        "direction": 0.4155844155844156,
        "persistence_mae": 0.2149350649350649,
        "mae_lift_vs_persistence": -0.18460697603847973,
        "r2_vs_persistence": -2.7601108408807002,
        "pred_delta_std": 0.41626714176730556,
        "truth_delta_std": 0.2590805908826503
      },
      "3": {
        "n": 77,
        "mae": 0.6881170459542072,
        "rmse": 0.8433705271477114,
        "corr": 0.569970329947726,
        "direction": 0.5064935064935064,
        "persistence_mae": 0.49103896103896105,
        "mae_lift_vs_persistence": -0.19707808491524614,
        "r2_vs_persistence": -0.9475797940595665,
        "pred_delta_std": 0.6877661555759074,
        "truth_delta_std": 0.6041533595330312
      },
      "6": {
        "n": 76,
        "mae": 0.8957296746114153,
        "rmse": 1.1118455449295022,
        "corr": 0.3285698441343856,
        "direction": 0.6052631578947368,
        "persistence_mae": 0.7817105263157895,
        "mae_lift_vs_persistence": -0.11401914829562576,
        "r2_vs_persistence": -0.29331215971675806,
        "pred_delta_std": 1.0260185259205992,
        "truth_delta_std": 0.9771131213626487
      },
      "12": {
        "n": 74,
        "mae": 1.1224425880770987,
        "rmse": 1.4243325347219709,
        "corr": -0.01985058034761224,
        "direction": 0.6216216216216216,
        "persistence_mae": 1.005135135135135,
        "mae_lift_vs_persistence": -0.11730745294196376,
        "r2_vs_persistence": -0.20607542226028852,
        "pred_delta_std": 1.1222455802853826,
        "truth_delta_std": 1.2966303184080832
      },
      "24": {
        "n": 70,
        "mae": 1.166947309256296,
        "rmse": 1.3728108101888208,
        "corr": 0.10145487132909534,
        "direction": 0.7285714285714285,
        "persistence_mae": 1.1871428571428573,
        "mae_lift_vs_persistence": 0.020195547886561194,
        "r2_vs_persistence": 0.0924055414980095,
        "pred_delta_std": 1.3749537025332634,
        "truth_delta_std": 1.44045525683333
      },
      "60": {
        "n": 58,
        "mae": 1.183532209188175,
        "rmse": 1.4609031387168072,
        "corr": 0.0066720287967871285,
        "direction": 0.5,
        "persistence_mae": 0.8901724137931035,
        "mae_lift_vs_persistence": -0.2933597953950715,
        "r2_vs_persistence": -0.299041588594533,
        "pred_delta_std": 1.278980867866625,
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
    "natural_advance_decoder": {
      "1": [
        {
          "origin": "2006-09-01",
          "date": "2006-10-01",
          "pred": 0.48542007626870975,
          "actual": 0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-01-01",
          "pred": 1.2251740218959606,
          "actual": 0.59,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-04-01",
          "pred": 0.38797591090544825,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-07-01",
          "pred": -0.12732877864102368,
          "actual": -0.37,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-10-01",
          "pred": -0.4000318362314258,
          "actual": -1.41,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-01-01",
          "pred": -0.6054636912114995,
          "actual": -1.79,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-04-01",
          "pred": -0.9801465354724512,
          "actual": -0.89,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-07-01",
          "pred": -0.9226158384108236,
          "actual": -0.04,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-10-01",
          "pred": -0.36389522744168135,
          "actual": -0.3,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-01-01",
          "pred": -0.002942624826745073,
          "actual": -1.0,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-04-01",
          "pred": -0.811753034726048,
          "actual": -0.25,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-07-01",
          "pred": 0.6638634289713209,
          "actual": 0.69,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-10-01",
          "pred": 1.112275098392798,
          "actual": 0.96,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-01-01",
          "pred": 1.8487993034945005,
          "actual": 1.43,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-04-01",
          "pred": 0.11535552975694413,
          "actual": 0.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-07-01",
          "pred": -0.5841748211598838,
          "actual": -0.89,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-10-01",
          "pred": -1.3388438705968606,
          "actual": -1.65,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-01-01",
          "pred": -1.0956981725219002,
          "actual": -1.7,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-04-01",
          "pred": -1.2612840472385183,
          "actual": -0.74,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-07-01",
          "pred": -0.9467871156686491,
          "actual": -0.23,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-10-01",
          "pred": -0.580965503574453,
          "actual": -0.93,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-01-01",
          "pred": -1.3057764360143755,
          "actual": -0.93,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-04-01",
          "pred": -0.8698799261063046,
          "actual": -0.29,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-07-01",
          "pred": 0.2906210194430536,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-10-01",
          "pred": 0.8526962355538226,
          "actual": 0.23,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-01-01",
          "pred": -0.04468828898004003,
          "actual": -0.42,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-04-01",
          "pred": -0.7377215621402824,
          "actual": -0.08,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-07-01",
          "pred": -0.5603718659751841,
          "actual": -0.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-10-01",
          "pred": -0.26584686554035425,
          "actual": -0.24,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-01-01",
          "pred": -0.29036713218159005,
          "actual": -0.42,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-04-01",
          "pred": -0.19822116615144988,
          "actual": 0.28,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-07-01",
          "pred": 0.951390488074913,
          "actual": 0.13,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-10-01",
          "pred": 0.5931372714315486,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-01-01",
          "pred": 1.0937194591353845,
          "actual": 0.59,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-04-01",
          "pred": 0.47269455413778344,
          "actual": 0.9,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-07-01",
          "pred": 0.6201873197816035,
          "actual": 1.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-10-01",
          "pred": 2.2014021061061944,
          "actual": 2.21,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-01-01",
          "pred": 2.5104180234364017,
          "actual": 2.56,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-04-01",
          "pred": 1.9048420010292073,
          "actual": 1.05,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-07-01",
          "pred": 0.3924917859962549,
          "actual": -0.25,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-10-01",
          "pred": -1.2761852714733972,
          "actual": -0.75,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-01-01",
          "pred": -0.18543836046226075,
          "actual": -0.34,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-04-01",
          "pred": 0.05195568958134647,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-07-01",
          "pred": -0.012443128796518554,
          "actual": 0.22,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-10-01",
          "pred": -0.5088309932236416,
          "actual": -0.52,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-01-01",
          "pred": -0.6584978948957855,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-04-01",
          "pred": 0.21512829679809437,
          "actual": -0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-07-01",
          "pred": 0.2415442093682506,
          "actual": 0.27,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-10-01",
          "pred": 0.2528200229604778,
          "actual": 0.84,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-01-01",
          "pred": 1.054390946317232,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-04-01",
          "pred": -0.1686464980113656,
          "actual": 0.67,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-07-01",
          "pred": 0.386688606200105,
          "actual": 0.41,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-10-01",
          "pred": 0.1950526716149838,
          "actual": 0.55,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-01-01",
          "pred": 0.5633495837133107,
          "actual": 0.64,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-04-01",
          "pred": 0.5270458065513497,
          "actual": 0.49,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-07-01",
          "pred": -0.07225044908766114,
          "actual": -0.04,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-10-01",
          "pred": -0.5309405397058068,
          "actual": -1.19,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-01-01",
          "pred": -0.8034771589769829,
          "actual": -1.04,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-04-01",
          "pred": -0.011541241040331583,
          "actual": -0.55,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-07-01",
          "pred": -0.37529210970823546,
          "actual": -0.2,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-10-01",
          "pred": -0.058057101281209125,
          "actual": -0.78,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-01-01",
          "pred": -0.4171193039612353,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-04-01",
          "pred": -0.5976565975811351,
          "actual": -0.9,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-07-01",
          "pred": -0.5028167294388881,
          "actual": -0.56,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-10-01",
          "pred": -0.5758840188569669,
          "actual": -0.99,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-01-01",
          "pred": -0.806957948040015,
          "actual": -0.78,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-04-01",
          "pred": -0.5042713804133818,
          "actual": 0.24,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-07-01",
          "pred": 0.657931723389972,
          "actual": 1.2,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-10-01",
          "pred": 1.2999314461852887,
          "actual": 1.59,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-01-01",
          "pred": 1.7231613928046279,
          "actual": 1.71,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-04-01",
          "pred": 1.1647002285526282,
          "actual": 0.93,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-07-01",
          "pred": -0.030219614506470496,
          "actual": 0.2,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-10-01",
          "pred": -0.0759711476246322,
          "actual": -0.24,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-01-01",
          "pred": 0.5968378302825097,
          "actual": -0.76,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-04-01",
          "pred": 0.43738651436214715,
          "actual": -0.08,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-07-01",
          "pred": 0.07036445808785864,
          "actual": -0.03,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-10-01",
          "pred": -0.8034099396647769,
          "actual": -0.5,
          "persistence": -0.3
        }
      ],
      "3": [
        {
          "origin": "2006-09-01",
          "date": "2006-12-01",
          "pred": 0.39347330162473015,
          "actual": 1.1,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-03-01",
          "pred": 1.4132848317702245,
          "actual": -0.15,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-06-01",
          "pred": 0.4682063890263452,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-09-01",
          "pred": 0.2316896510900121,
          "actual": -1.04,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-12-01",
          "pred": -0.25203266663523394,
          "actual": -1.61,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-03-01",
          "pred": 0.020729211365853494,
          "actual": -1.17,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-06-01",
          "pred": -0.972978801507712,
          "actual": -0.44,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-09-01",
          "pred": -1.3866666823738858,
          "actual": -0.28,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-12-01",
          "pred": -0.05355160977333074,
          "actual": -0.9,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-03-01",
          "pred": -0.06914431718474648,
          "actual": -0.72,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-06-01",
          "pred": -1.1961271173565742,
          "actual": 0.49,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-09-01",
          "pred": 0.776190837486317,
          "actual": 0.68,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-12-01",
          "pred": 1.875721592895761,
          "actual": 1.81,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-03-01",
          "pred": 0.6429418652108297,
          "actual": 1.07,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-06-01",
          "pred": -0.27105293590426105,
          "actual": -0.62,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-09-01",
          "pred": -0.04584504132311318,
          "actual": -1.56,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-12-01",
          "pred": -1.2180246334249458,
          "actual": -1.63,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-03-01",
          "pred": -0.6044140263165086,
          "actual": -0.98,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-06-01",
          "pred": -0.9422173855676976,
          "actual": -0.25,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-09-01",
          "pred": -1.6001201898126998,
          "actual": -0.76,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-12-01",
          "pred": -0.8413164646356699,
          "actual": -1.05,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-03-01",
          "pred": -1.2887540577216599,
          "actual": -0.48,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-06-01",
          "pred": -0.7863529831005258,
          "actual": 0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-09-01",
          "pred": 1.2123112205627908,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-12-01",
          "pred": 0.8880489591159204,
          "actual": -0.13,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-03-01",
          "pred": -0.5619172707327837,
          "actual": -0.14,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-06-01",
          "pred": -1.2326859182858245,
          "actual": -0.33,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-09-01",
          "pred": -0.7628336945268073,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-12-01",
          "pred": -0.30861491048276835,
          "actual": -0.09,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-03-01",
          "pred": -0.1807830615767978,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-06-01",
          "pred": 0.152373858977135,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-09-01",
          "pred": 1.086863290803254,
          "actual": 0.37,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-12-01",
          "pred": 0.8127452255175975,
          "actual": 0.77,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-03-01",
          "pred": 0.999236070897326,
          "actual": 0.48,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-06-01",
          "pred": 0.8220596799698707,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-09-01",
          "pred": 0.17199444672367545,
          "actual": 2.01,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-12-01",
          "pred": 2.091970501061861,
          "actual": 2.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-03-01",
          "pred": 2.5969441863101363,
          "actual": 1.6,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-06-01",
          "pred": 1.7643636076541824,
          "actual": 0.06,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-09-01",
          "pred": 0.8203412682843741,
          "actual": -0.46,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-12-01",
          "pred": -1.5537788198078066,
          "actual": -0.51,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-03-01",
          "pred": 0.1589072356510588,
          "actual": -0.09,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-06-01",
          "pred": -0.24976793947797138,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-09-01",
          "pred": -0.3481936155399883,
          "actual": -0.56,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-12-01",
          "pred": -0.7099427011808285,
          "actual": -0.85,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-03-01",
          "pred": -1.0371693838175506,
          "actual": -0.73,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-06-01",
          "pred": 0.6885593213627491,
          "actual": 0.12,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-09-01",
          "pred": 0.4388106479026749,
          "actual": 0.3,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-12-01",
          "pred": 0.6660327543293905,
          "actual": 0.97,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-03-01",
          "pred": 0.2766208100678212,
          "actual": 0.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-06-01",
          "pred": -0.6643008761215549,
          "actual": 0.66,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-09-01",
          "pred": -0.3457381043200181,
          "actual": 0.11,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-12-01",
          "pred": 0.31301367725876017,
          "actual": 0.51,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-03-01",
          "pred": 0.39122844793897116,
          "actual": 0.36,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-06-01",
          "pred": 1.1398024286218729,
          "actual": -0.21,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-09-01",
          "pred": 0.008963316999819785,
          "actual": -0.66,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-12-01",
          "pred": -0.38971471563096727,
          "actual": -0.98,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-03-01",
          "pred": -0.9150381993541067,
          "actual": -0.72,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-06-01",
          "pred": -0.1312301006599751,
          "actual": -0.06,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-09-01",
          "pred": -0.8524841514794359,
          "actual": -0.5,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-12-01",
          "pred": 0.37264839090731544,
          "actual": -1.07,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-03-01",
          "pred": -0.29630360278635476,
          "actual": -0.84,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-06-01",
          "pred": -0.6891376940312076,
          "actual": -0.77,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-09-01",
          "pred": -0.4123279511458144,
          "actual": -1.06,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-12-01",
          "pred": -0.8177682527784207,
          "actual": -0.86,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-03-01",
          "pred": -1.3487603010971079,
          "actual": -0.13,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-06-01",
          "pred": -0.8254157772639802,
          "actual": 0.95,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-09-01",
          "pred": 0.3093916787670229,
          "actual": 1.65,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-12-01",
          "pred": 1.6662951348709714,
          "actual": 1.81,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-03-01",
          "pred": 2.009053809724828,
          "actual": 1.1,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-06-01",
          "pred": 1.5813548627356486,
          "actual": 0.25,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-09-01",
          "pred": 0.41930110916665325,
          "actual": -0.11,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-12-01",
          "pred": 0.32107960566487975,
          "actual": -0.58,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-03-01",
          "pred": 1.2679453491590165,
          "actual": 0.05,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-06-01",
          "pred": 0.4666230934321297,
          "actual": 0.01,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-09-01",
          "pred": -0.4442314779884562,
          "actual": -0.3,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-12-01",
          "pred": -0.7861413474365241,
          "actual": -0.49,
          "persistence": -0.3
        }
      ],
      "6": [
        {
          "origin": "2006-09-01",
          "date": "2007-03-01",
          "pred": 0.34760188831352795,
          "actual": -0.15,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-06-01",
          "pred": 0.5354705071812935,
          "actual": -0.16,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-09-01",
          "pred": 0.8257823076970462,
          "actual": -1.04,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-12-01",
          "pred": 0.7648528741788297,
          "actual": -1.61,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-03-01",
          "pred": 0.9030458068768006,
          "actual": -1.17,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-06-01",
          "pred": -0.33481872088846576,
          "actual": -0.44,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-09-01",
          "pred": -1.1387554056519424,
          "actual": -0.28,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-12-01",
          "pred": -1.5211386779584328,
          "actual": -0.9,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-03-01",
          "pred": -0.9074561468438725,
          "actual": -0.72,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-06-01",
          "pred": -0.9033054087150579,
          "actual": 0.49,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-09-01",
          "pred": 0.07826918220423826,
          "actual": 0.68,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-12-01",
          "pred": 1.8545806901343211,
          "actual": 1.81,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-03-01",
          "pred": 0.657710585365866,
          "actual": 1.07,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-06-01",
          "pred": -1.0552269580732112,
          "actual": -0.62,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-09-01",
          "pred": -0.31614965701374353,
          "actual": -1.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-12-01",
          "pred": 0.2466843150705751,
          "actual": -1.63,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-03-01",
          "pred": -0.017761833058854926,
          "actual": -0.98,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-06-01",
          "pred": 0.7251671203344865,
          "actual": -0.25,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-09-01",
          "pred": -1.331121874835686,
          "actual": -0.76,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-12-01",
          "pred": -1.8286369983593511,
          "actual": -1.05,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-03-01",
          "pred": -1.5601321391228224,
          "actual": -0.48,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-06-01",
          "pred": -1.148869919470206,
          "actual": 0.14,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-09-01",
          "pred": 0.8016542581035264,
          "actual": 0.44,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-12-01",
          "pred": 1.8220671631030785,
          "actual": -0.13,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-03-01",
          "pred": 0.24210225643990607,
          "actual": -0.14,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-06-01",
          "pred": -1.2863197729575508,
          "actual": -0.33,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-09-01",
          "pred": -1.1918967540483698,
          "actual": -0.09,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-12-01",
          "pred": -0.422968985631143,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-03-01",
          "pred": -0.2361488190845314,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-06-01",
          "pred": -0.534512575849092,
          "actual": 0.48,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-09-01",
          "pred": 0.518032520997605,
          "actual": 0.37,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-12-01",
          "pred": 1.4271155920621856,
          "actual": 0.77,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-03-01",
          "pred": 0.9391235011781072,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-06-01",
          "pred": 1.2011986479358687,
          "actual": 1.28,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-09-01",
          "pred": 1.6762033938631304,
          "actual": 2.01,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-12-01",
          "pred": 0.8715810065978971,
          "actual": 2.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-03-01",
          "pred": 2.1464205837319,
          "actual": 1.6,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-06-01",
          "pred": 2.0703886084795142,
          "actual": 0.06,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-09-01",
          "pred": 0.9525272786890959,
          "actual": -0.46,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-12-01",
          "pred": 0.6555745029200183,
          "actual": -0.51,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-03-01",
          "pred": 0.01838262313550488,
          "actual": -0.09,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-06-01",
          "pred": 1.3117332276913223,
          "actual": 0.22,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-09-01",
          "pred": -0.8171906678838836,
          "actual": -0.56,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-12-01",
          "pred": -1.068007331468313,
          "actual": -0.85,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-03-01",
          "pred": -0.4930660563954796,
          "actual": -0.73,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-06-01",
          "pred": 0.07985147835848401,
          "actual": 0.12,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-09-01",
          "pred": 1.5478556171464333,
          "actual": 0.3,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-12-01",
          "pred": 0.661106133412963,
          "actual": 0.97,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-03-01",
          "pred": -0.1599667292279029,
          "actual": 0.81,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-06-01",
          "pred": -0.8322629686837674,
          "actual": 0.66,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-09-01",
          "pred": -0.9924185907407692,
          "actual": 0.11,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-12-01",
          "pred": -0.33061962333321543,
          "actual": 0.51,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-03-01",
          "pred": 0.3325247240263758,
          "actual": 0.36,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-06-01",
          "pred": 0.6936989344670973,
          "actual": -0.21,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-09-01",
          "pred": 1.075268401244313,
          "actual": -0.66,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-12-01",
          "pred": -0.16350776771487593,
          "actual": -0.98,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-03-01",
          "pred": 0.02712404229434657,
          "actual": -0.72,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-06-01",
          "pred": -0.4032683716717248,
          "actual": -0.06,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-09-01",
          "pred": -0.017101089911816702,
          "actual": -0.5,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-12-01",
          "pred": -0.6743340353558085,
          "actual": -1.07,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-03-01",
          "pred": -0.4192214424091877,
          "actual": -0.84,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-06-01",
          "pred": -0.42270011535168417,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-09-01",
          "pred": 0.19702029731426418,
          "actual": -1.06,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-12-01",
          "pred": -0.40819052155715896,
          "actual": -0.86,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-03-01",
          "pred": -0.8574801878129461,
          "actual": -0.13,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-06-01",
          "pred": -1.869008945782032,
          "actual": 0.95,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-09-01",
          "pred": -0.8134074046201218,
          "actual": 1.65,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-12-01",
          "pred": 0.4891094017098448,
          "actual": 1.81,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-03-01",
          "pred": 1.5469531318375842,
          "actual": 1.1,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-06-01",
          "pred": 1.7120726389255585,
          "actual": 0.25,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-09-01",
          "pred": 1.8999123990560514,
          "actual": -0.11,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-12-01",
          "pred": 0.6591598276663977,
          "actual": -0.58,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-03-01",
          "pred": 1.5859393771345642,
          "actual": 0.05,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-06-01",
          "pred": 1.7222570341911327,
          "actual": 0.01,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-09-01",
          "pred": -0.6419987977312942,
          "actual": -0.3,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-12-01",
          "pred": -1.041870283895321,
          "actual": -0.49,
          "persistence": 0.01
        }
      ],
      "12": [
        {
          "origin": "2006-09-01",
          "date": "2007-09-01",
          "pred": 1.3206745458359743,
          "actual": -1.04,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-12-01",
          "pred": 1.9428212412703143,
          "actual": -1.61,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2008-03-01",
          "pred": 1.1915125174864525,
          "actual": -1.17,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2008-06-01",
          "pred": -0.3439310642090955,
          "actual": -0.44,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-09-01",
          "pred": -0.8043202358129581,
          "actual": -0.28,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-12-01",
          "pred": -0.6909987167866734,
          "actual": -0.9,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2009-03-01",
          "pred": -0.7681752424107832,
          "actual": -0.72,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2009-06-01",
          "pred": -1.5741587810501538,
          "actual": 0.49,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-09-01",
          "pred": -0.41192911959706013,
          "actual": 0.68,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-12-01",
          "pred": 1.112493800046979,
          "actual": 1.81,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2010-03-01",
          "pred": -0.5918118263207103,
          "actual": 1.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2010-06-01",
          "pred": -0.9901595502002489,
          "actual": -0.62,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-09-01",
          "pred": -1.090343238798629,
          "actual": -1.56,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-12-01",
          "pred": 0.6028871672367888,
          "actual": -1.63,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2011-03-01",
          "pred": 0.8330720815993334,
          "actual": -0.98,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2011-06-01",
          "pred": 0.23664213229998032,
          "actual": -0.25,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-09-01",
          "pred": 0.0316434973907109,
          "actual": -0.76,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-12-01",
          "pred": -0.3722818403569776,
          "actual": -1.05,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2012-03-01",
          "pred": -0.9311955837549009,
          "actual": -0.48,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2012-06-01",
          "pred": -0.5860294345285921,
          "actual": 0.14,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-09-01",
          "pred": 0.636487001672397,
          "actual": 0.44,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-12-01",
          "pred": 0.973170983968968,
          "actual": -0.13,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2013-03-01",
          "pred": -0.34276736412994235,
          "actual": -0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2013-06-01",
          "pred": -1.795077941141815,
          "actual": -0.33,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-09-01",
          "pred": -1.6879654880602235,
          "actual": -0.09,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-12-01",
          "pred": -0.09428359754566538,
          "actual": -0.09,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2014-03-01",
          "pred": -0.81925431749605,
          "actual": -0.07,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2014-06-01",
          "pred": -1.0141372995146072,
          "actual": 0.48,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-09-01",
          "pred": 0.0766957022887348,
          "actual": 0.37,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-12-01",
          "pred": 0.8868829648496582,
          "actual": 0.77,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2015-03-01",
          "pred": 1.9939051417752771,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2015-06-01",
          "pred": 1.2247628325684277,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-09-01",
          "pred": 1.8706036262124275,
          "actual": 2.01,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-12-01",
          "pred": 1.7013056781975069,
          "actual": 2.56,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2016-03-01",
          "pred": 1.664441967967102,
          "actual": 1.6,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2016-06-01",
          "pred": -0.48716661007412815,
          "actual": 0.06,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-09-01",
          "pred": 1.0495641779175544,
          "actual": -0.46,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-12-01",
          "pred": 1.6136118444744723,
          "actual": -0.51,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2017-03-01",
          "pred": 1.4406361603234463,
          "actual": -0.09,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2017-06-01",
          "pred": 0.43296383914315356,
          "actual": 0.22,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-09-01",
          "pred": -0.4003417578210511,
          "actual": -0.56,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-12-01",
          "pred": -0.0843978081841544,
          "actual": -0.85,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2018-03-01",
          "pred": 0.14006113231448603,
          "actual": -0.73,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2018-06-01",
          "pred": 0.9631181494672685,
          "actual": 0.12,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-09-01",
          "pred": 2.0995147444730535,
          "actual": 0.3,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-12-01",
          "pred": 0.8649395116710743,
          "actual": 0.97,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2019-03-01",
          "pred": -1.2029063005942813,
          "actual": 0.81,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2019-06-01",
          "pred": -1.959228863660559,
          "actual": 0.66,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-09-01",
          "pred": -1.8995186241404538,
          "actual": 0.11,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-12-01",
          "pred": 0.26029841182385777,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2020-03-01",
          "pred": 0.0590464628737118,
          "actual": 0.36,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2020-06-01",
          "pred": -0.0912063558395747,
          "actual": -0.21,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-09-01",
          "pred": -0.32882931970373197,
          "actual": -0.66,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-12-01",
          "pred": -0.013279673855684947,
          "actual": -0.98,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2021-03-01",
          "pred": 1.1640030237325425,
          "actual": -0.72,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2021-06-01",
          "pred": 1.5513871099659957,
          "actual": -0.06,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-09-01",
          "pred": 1.427530568530075,
          "actual": -0.5,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-12-01",
          "pred": 0.49176872023379214,
          "actual": -1.07,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2022-03-01",
          "pred": -0.0397652633286454,
          "actual": -0.84,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2022-06-01",
          "pred": 0.19880007514597028,
          "actual": -0.77,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-09-01",
          "pred": 0.32787221418045503,
          "actual": -1.06,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-12-01",
          "pred": 0.36781277537028306,
          "actual": -0.86,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2023-03-01",
          "pred": -1.0114599177326788,
          "actual": -0.13,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2023-06-01",
          "pred": -2.3004770017190643,
          "actual": 0.95,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-09-01",
          "pred": -1.9333856188250425,
          "actual": 1.65,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-12-01",
          "pred": 0.05054750188406162,
          "actual": 1.81,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2024-03-01",
          "pred": -0.5054661691310076,
          "actual": 1.1,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2024-06-01",
          "pred": 0.5951464205853435,
          "actual": 0.25,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-09-01",
          "pred": 1.8065550500983625,
          "actual": -0.11,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-12-01",
          "pred": 1.9726736448417994,
          "actual": -0.58,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2025-03-01",
          "pred": 0.7377228909545793,
          "actual": 0.05,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2025-06-01",
          "pred": 0.3875842096119179,
          "actual": 0.01,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-09-01",
          "pred": 1.202854970837357,
          "actual": -0.3,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-12-01",
          "pred": 0.8085648896037444,
          "actual": -0.49,
          "persistence": -0.58
        }
      ],
      "24": [
        {
          "origin": "2006-09-01",
          "date": "2008-09-01",
          "pred": -0.21429153338879875,
          "actual": -0.28,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2008-12-01",
          "pred": -0.3455363995457943,
          "actual": -0.9,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2009-03-01",
          "pred": 1.1983664225148167,
          "actual": -0.72,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2009-06-01",
          "pred": 1.6226160022652696,
          "actual": 0.49,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2009-09-01",
          "pred": 1.447713878334624,
          "actual": 0.68,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2009-12-01",
          "pred": -0.12116608553707087,
          "actual": 1.81,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2010-03-01",
          "pred": -0.62245912579478,
          "actual": 1.07,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2010-06-01",
          "pred": -1.523376492496262,
          "actual": -0.62,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2010-09-01",
          "pred": -2.660978093403851,
          "actual": -1.56,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2010-12-01",
          "pred": -1.8548281760570087,
          "actual": -1.63,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2011-03-01",
          "pred": 0.5928097119780246,
          "actual": -0.98,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2011-06-01",
          "pred": 1.0182605737918942,
          "actual": -0.25,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2011-09-01",
          "pred": -0.27812791261599407,
          "actual": -0.76,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2011-12-01",
          "pred": 0.6485266437085028,
          "actual": -1.05,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2012-03-01",
          "pred": 0.8780100785878111,
          "actual": -0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2012-06-01",
          "pred": 1.902831786318208,
          "actual": 0.14,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2012-09-01",
          "pred": 1.6834928994736502,
          "actual": 0.44,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2012-12-01",
          "pred": 0.545654613073765,
          "actual": -0.13,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2013-03-01",
          "pred": -1.8591873814389799,
          "actual": -0.14,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2013-06-01",
          "pred": -2.187926817634184,
          "actual": -0.33,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2013-09-01",
          "pred": -2.6977073211647062,
          "actual": -0.09,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2013-12-01",
          "pred": -1.4901517189870446,
          "actual": -0.09,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2014-03-01",
          "pred": 0.46050319259544426,
          "actual": -0.07,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2014-06-01",
          "pred": -0.551730588945485,
          "actual": 0.48,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2014-09-01",
          "pred": 0.36702798408427667,
          "actual": 0.37,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2014-12-01",
          "pred": 0.8325986393817674,
          "actual": 0.77,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2015-03-01",
          "pred": 1.9223463441757915,
          "actual": 0.48,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2015-06-01",
          "pred": 2.0574855335187947,
          "actual": 1.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2015-09-01",
          "pred": 1.5934383107704346,
          "actual": 2.01,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2015-12-01",
          "pred": 0.6138063294695211,
          "actual": 2.56,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2016-03-01",
          "pred": -0.453536494146002,
          "actual": 1.6,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2016-06-01",
          "pred": -0.18564656097812948,
          "actual": 0.06,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2016-09-01",
          "pred": -0.7820592983645442,
          "actual": -0.46,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2016-12-01",
          "pred": -0.45298281569476545,
          "actual": -0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2017-03-01",
          "pred": -0.4384866589384948,
          "actual": -0.09,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2017-06-01",
          "pred": 2.119917111386483,
          "actual": 0.22,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2017-09-01",
          "pred": 0.06345975780874952,
          "actual": -0.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2017-12-01",
          "pred": -0.20650321895891727,
          "actual": -0.85,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2018-03-01",
          "pred": 0.977217273279715,
          "actual": -0.73,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2018-06-01",
          "pred": 1.6182240849193186,
          "actual": 0.12,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2018-09-01",
          "pred": 1.5315355979419787,
          "actual": 0.3,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2018-12-01",
          "pred": 1.1084849608010654,
          "actual": 0.97,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2019-03-01",
          "pred": -0.9988512443693037,
          "actual": 0.81,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2019-06-01",
          "pred": -1.4367322241893017,
          "actual": 0.66,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2019-09-01",
          "pred": -1.2988129007604958,
          "actual": 0.11,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2019-12-01",
          "pred": -0.2882302460175712,
          "actual": 0.51,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2020-03-01",
          "pred": 0.18834512680287183,
          "actual": 0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2020-06-01",
          "pred": -1.5807887535856184,
          "actual": -0.21,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2020-09-01",
          "pred": -0.9066241406106057,
          "actual": -0.66,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2020-12-01",
          "pred": -0.7663906280825489,
          "actual": -0.98,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2021-03-01",
          "pred": 0.878967212261957,
          "actual": -0.72,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2021-06-01",
          "pred": 1.541502195549201,
          "actual": -0.06,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2021-09-01",
          "pred": 1.7395405353052633,
          "actual": -0.5,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2021-12-01",
          "pred": 1.5881203973645581,
          "actual": -1.07,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2022-03-01",
          "pred": 0.3560295628480266,
          "actual": -0.84,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2022-06-01",
          "pred": 0.3563876392439649,
          "actual": -0.77,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2022-09-01",
          "pred": 0.48562080975507405,
          "actual": -1.06,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2022-12-01",
          "pred": 0.2153048251691823,
          "actual": -0.86,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2023-03-01",
          "pred": 0.05990226706904832,
          "actual": -0.13,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2023-06-01",
          "pred": -1.190906266336622,
          "actual": 0.95,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2023-09-01",
          "pred": -1.4608133775861276,
          "actual": 1.65,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2023-12-01",
          "pred": -0.5704128967909412,
          "actual": 1.81,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2024-03-01",
          "pred": 0.32840072547682647,
          "actual": 1.1,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2024-06-01",
          "pred": 0.3814869699155662,
          "actual": 0.25,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2024-09-01",
          "pred": 0.6932269912270667,
          "actual": -0.11,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2024-12-01",
          "pred": 1.0873337533240035,
          "actual": -0.58,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2025-03-01",
          "pred": 1.6203780155405942,
          "actual": 0.05,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2025-06-01",
          "pred": -0.3670196909977075,
          "actual": 0.01,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2025-09-01",
          "pred": -0.3409891254368262,
          "actual": -0.3,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2025-12-01",
          "pred": 1.2263462623732684,
          "actual": -0.49,
          "persistence": 1.81
        }
      ],
      "60": [
        {
          "origin": "2006-09-01",
          "date": "2011-09-01",
          "pred": -1.2255855214926579,
          "actual": -0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2011-12-01",
          "pred": -0.4257327894416311,
          "actual": -1.05,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2012-03-01",
          "pred": 0.674398942279046,
          "actual": -0.48,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2012-06-01",
          "pred": -0.3986401347913413,
          "actual": 0.14,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2012-09-01",
          "pred": -0.5727496509127954,
          "actual": 0.44,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2012-12-01",
          "pred": -0.8856100991520895,
          "actual": -0.13,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2013-03-01",
          "pred": -1.148972182310781,
          "actual": -0.14,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2013-06-01",
          "pred": -1.9461648571752423,
          "actual": -0.33,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2013-09-01",
          "pred": -0.5650093500832157,
          "actual": -0.09,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2013-12-01",
          "pred": 1.5526428365513305,
          "actual": -0.09,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2014-03-01",
          "pred": 0.35878885369403635,
          "actual": -0.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2014-06-01",
          "pred": -0.12450553719456915,
          "actual": 0.48,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2014-09-01",
          "pred": 0.8216682508027371,
          "actual": 0.37,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2014-12-01",
          "pred": 2.2861357511869027,
          "actual": 0.77,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2015-03-01",
          "pred": 2.946613319591557,
          "actual": 0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2015-06-01",
          "pred": 1.9728703357531705,
          "actual": 1.28,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2015-09-01",
          "pred": 0.13349454182601872,
          "actual": 2.01,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2015-12-01",
          "pred": -1.2881358686519022,
          "actual": 2.56,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2016-03-01",
          "pred": -1.9031221873922242,
          "actual": 1.6,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2016-06-01",
          "pred": -1.765734516819227,
          "actual": 0.06,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2016-09-01",
          "pred": -0.8588524516414909,
          "actual": -0.46,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2016-12-01",
          "pred": 0.45779566961024887,
          "actual": -0.51,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2017-03-01",
          "pred": -0.39250102534049136,
          "actual": -0.09,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2017-06-01",
          "pred": -1.5491173250944659,
          "actual": 0.22,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2017-09-01",
          "pred": 0.1300221114107532,
          "actual": -0.56,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2017-12-01",
          "pred": 1.7635460710729631,
          "actual": -0.85,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2018-03-01",
          "pred": 0.4812102895102142,
          "actual": -0.73,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2018-06-01",
          "pred": -0.6187025960824487,
          "actual": 0.12,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2018-09-01",
          "pred": -0.16103123310400064,
          "actual": 0.3,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2018-12-01",
          "pred": -0.7791777586198082,
          "actual": 0.97,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2019-03-01",
          "pred": -0.9254647946411774,
          "actual": 0.81,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2019-06-01",
          "pred": -1.5341773831292116,
          "actual": 0.66,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2019-09-01",
          "pred": -0.18248630111817182,
          "actual": 0.11,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2019-12-01",
          "pred": -0.34161718565494664,
          "actual": 0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2020-03-01",
          "pred": -0.1833222954147529,
          "actual": 0.36,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2020-06-01",
          "pred": 0.20293730197154047,
          "actual": -0.21,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2020-09-01",
          "pred": -0.32932022865072896,
          "actual": -0.66,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2020-12-01",
          "pred": 0.7834431526112763,
          "actual": -0.98,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2021-03-01",
          "pred": 1.98364330338181,
          "actual": -0.72,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2021-06-01",
          "pred": 0.6910523476502465,
          "actual": -0.06,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2021-09-01",
          "pred": -1.5648858516315507,
          "actual": -0.5,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2021-12-01",
          "pred": -1.6957842486608357,
          "actual": -1.07,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2022-03-01",
          "pred": -2.0820664652295666,
          "actual": -0.84,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2022-06-01",
          "pred": -1.5493618939787452,
          "actual": -0.77,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2022-09-01",
          "pred": -0.35777401241724605,
          "actual": -1.06,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2022-12-01",
          "pred": -0.47221291559632056,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2023-03-01",
          "pred": -1.932264180879714,
          "actual": -0.13,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2023-06-01",
          "pred": -2.440898560099628,
          "actual": 0.95,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2023-09-01",
          "pred": -0.8832770550095839,
          "actual": 1.65,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2023-12-01",
          "pred": 0.3693908380160166,
          "actual": 1.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2024-03-01",
          "pred": 2.0978718135182244,
          "actual": 1.1,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2024-06-01",
          "pred": 2.0729312620964153,
          "actual": 0.25,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2024-09-01",
          "pred": 1.6032044069594085,
          "actual": -0.11,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2024-12-01",
          "pred": 1.2286916785778772,
          "actual": -0.58,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2025-03-01",
          "pred": 1.002291939902519,
          "actual": 0.05,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2025-06-01",
          "pred": 1.4601900593673613,
          "actual": 0.01,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2025-09-01",
          "pred": 0.8609671352349062,
          "actual": -0.3,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2025-12-01",
          "pred": 0.7084499695850989,
          "actual": -0.49,
          "persistence": -0.98
        }
      ]
    },
    "sync_event_cascade_decoder": {
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
    "gear_event_cascade_decoder": {
      "1": [
        {
          "origin": "2006-09-01",
          "date": "2006-10-01",
          "pred": 0.4854512991748387,
          "actual": 0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-01-01",
          "pred": 1.2188073440181637,
          "actual": 0.59,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-04-01",
          "pred": 0.3871734331775279,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-07-01",
          "pred": -0.12376821025515686,
          "actual": -0.37,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-10-01",
          "pred": -0.39997503352482705,
          "actual": -1.41,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-01-01",
          "pred": -0.6082922713692139,
          "actual": -1.79,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-04-01",
          "pred": -0.9846911091862272,
          "actual": -0.89,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-07-01",
          "pred": -0.9257062627699042,
          "actual": -0.04,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-10-01",
          "pred": -0.36264113681508714,
          "actual": -0.3,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-01-01",
          "pred": -0.003176463782711171,
          "actual": -1.0,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-04-01",
          "pred": -0.8118620543056932,
          "actual": -0.25,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-07-01",
          "pred": 0.6566435660041966,
          "actual": 0.69,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-10-01",
          "pred": 1.1033964111312669,
          "actual": 0.96,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-01-01",
          "pred": 1.8434919509448753,
          "actual": 1.43,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-04-01",
          "pred": 0.10953096737513887,
          "actual": 0.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-07-01",
          "pred": -0.588723485457938,
          "actual": -0.89,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-10-01",
          "pred": -1.3472579669045395,
          "actual": -1.65,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-01-01",
          "pred": -1.103378163904343,
          "actual": -1.7,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-04-01",
          "pred": -1.2593534465172254,
          "actual": -0.74,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-07-01",
          "pred": -0.9453942890664734,
          "actual": -0.23,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-10-01",
          "pred": -0.5793322118786213,
          "actual": -0.93,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-01-01",
          "pred": -1.3067638627227085,
          "actual": -0.93,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-04-01",
          "pred": -0.8703651327893906,
          "actual": -0.29,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-07-01",
          "pred": 0.2845094218997359,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-10-01",
          "pred": 0.8480451895619563,
          "actual": 0.23,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-01-01",
          "pred": -0.04579798091022565,
          "actual": -0.42,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-04-01",
          "pred": -0.742007861063736,
          "actual": -0.08,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-07-01",
          "pred": -0.5643443313972188,
          "actual": -0.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-10-01",
          "pred": -0.26834850860312337,
          "actual": -0.24,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-01-01",
          "pred": -0.2843343250150798,
          "actual": -0.42,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-04-01",
          "pred": -0.1935914802742356,
          "actual": 0.28,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-07-01",
          "pred": 0.9558135812447349,
          "actual": 0.13,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-10-01",
          "pred": 0.5850688058585294,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-01-01",
          "pred": 1.0879721810913399,
          "actual": 0.59,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-04-01",
          "pred": 0.4706531571074581,
          "actual": 0.9,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-07-01",
          "pred": 0.6116631119787577,
          "actual": 1.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-10-01",
          "pred": 2.1938793784658572,
          "actual": 2.21,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-01-01",
          "pred": 2.5045385127624153,
          "actual": 2.56,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-04-01",
          "pred": 1.8983655121194465,
          "actual": 1.05,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-07-01",
          "pred": 0.3855800701363858,
          "actual": -0.25,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-10-01",
          "pred": -1.2852558326396326,
          "actual": -0.75,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-01-01",
          "pred": -0.19481982067035553,
          "actual": -0.34,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-04-01",
          "pred": 0.039271049629776164,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-07-01",
          "pred": -0.02047170580664663,
          "actual": 0.22,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-10-01",
          "pred": -0.5129170049948417,
          "actual": -0.52,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-01-01",
          "pred": -0.6622227949943077,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-04-01",
          "pred": 0.21013577503939582,
          "actual": -0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-07-01",
          "pred": 0.23525422571258314,
          "actual": 0.27,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-10-01",
          "pred": 0.24614708856071493,
          "actual": 0.84,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-01-01",
          "pred": 1.0470711444307788,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-04-01",
          "pred": -0.17542737603812134,
          "actual": 0.67,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-07-01",
          "pred": 0.37855648529852964,
          "actual": 0.41,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-10-01",
          "pred": 0.18374700143605333,
          "actual": 0.55,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-01-01",
          "pred": 0.5543672109270382,
          "actual": 0.64,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-04-01",
          "pred": 0.5163907171322151,
          "actual": 0.49,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-07-01",
          "pred": -0.08635921226128541,
          "actual": -0.04,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-10-01",
          "pred": -0.545036699861233,
          "actual": -1.19,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-01-01",
          "pred": -0.8073285834085637,
          "actual": -1.04,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-04-01",
          "pred": -0.012841532617012461,
          "actual": -0.55,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-07-01",
          "pred": -0.376407655827678,
          "actual": -0.2,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-10-01",
          "pred": -0.05711313900275146,
          "actual": -0.78,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-01-01",
          "pred": -0.422687876111558,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-04-01",
          "pred": -0.5997753682379349,
          "actual": -0.9,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-07-01",
          "pred": -0.504046518855157,
          "actual": -0.56,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-10-01",
          "pred": -0.5772838099464205,
          "actual": -0.99,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-01-01",
          "pred": -0.8056854210535863,
          "actual": -0.78,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-04-01",
          "pred": -0.5035790453138747,
          "actual": 0.24,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-07-01",
          "pred": 0.6585256749893783,
          "actual": 1.2,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-10-01",
          "pred": 1.301267451895672,
          "actual": 1.59,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-01-01",
          "pred": 1.7204356633347253,
          "actual": 1.71,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-04-01",
          "pred": 1.1684743087683518,
          "actual": 0.93,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-07-01",
          "pred": -0.024196357904573206,
          "actual": 0.2,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-10-01",
          "pred": -0.07994255898583595,
          "actual": -0.24,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-01-01",
          "pred": 0.595307067878285,
          "actual": -0.76,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-04-01",
          "pred": 0.43116716266208754,
          "actual": -0.08,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-07-01",
          "pred": 0.06179300265391359,
          "actual": -0.03,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-10-01",
          "pred": -0.801235831246948,
          "actual": -0.5,
          "persistence": -0.3
        }
      ],
      "3": [
        {
          "origin": "2006-09-01",
          "date": "2006-12-01",
          "pred": 0.38549215522115016,
          "actual": 1.1,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-03-01",
          "pred": 1.416475298136546,
          "actual": -0.15,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-06-01",
          "pred": 0.47101066435609334,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-09-01",
          "pred": 0.24578158223201876,
          "actual": -1.04,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-12-01",
          "pred": -0.2591166264902596,
          "actual": -1.61,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-03-01",
          "pred": 0.025217579740389223,
          "actual": -1.17,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-06-01",
          "pred": -0.977053123305421,
          "actual": -0.44,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-09-01",
          "pred": -1.3944638938753537,
          "actual": -0.28,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-12-01",
          "pred": -0.056756162679651015,
          "actual": -0.9,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-03-01",
          "pred": -0.11348048245799541,
          "actual": -0.72,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-06-01",
          "pred": -1.1970622740358206,
          "actual": 0.49,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-09-01",
          "pred": 0.7494952707558195,
          "actual": 0.68,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-12-01",
          "pred": 1.8150817866909288,
          "actual": 1.81,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-03-01",
          "pred": 0.6188662633425539,
          "actual": 1.07,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-06-01",
          "pred": -0.294802263091293,
          "actual": -0.62,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-09-01",
          "pred": -0.05735520899088736,
          "actual": -1.56,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-12-01",
          "pred": -1.203713774731066,
          "actual": -1.63,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-03-01",
          "pred": -0.6289820794411172,
          "actual": -0.98,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-06-01",
          "pred": -0.9659428742138112,
          "actual": -0.25,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-09-01",
          "pred": -1.5866122534952942,
          "actual": -0.76,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-12-01",
          "pred": -0.8381492882115679,
          "actual": -1.05,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-03-01",
          "pred": -1.2977490051742,
          "actual": -0.48,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-06-01",
          "pred": -0.7906075952043423,
          "actual": 0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-09-01",
          "pred": 1.1239881418384092,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-12-01",
          "pred": 0.8710681594344098,
          "actual": -0.13,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-03-01",
          "pred": -0.5821279693748644,
          "actual": -0.14,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-06-01",
          "pred": -1.2403867535042987,
          "actual": -0.33,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-09-01",
          "pred": -0.7652441927850114,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-12-01",
          "pred": -0.30206566289690157,
          "actual": -0.09,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-03-01",
          "pred": -0.16053505030334894,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-06-01",
          "pred": 0.1389280469599836,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-09-01",
          "pred": 1.0824243361081227,
          "actual": 0.37,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-12-01",
          "pred": 0.7970079016094903,
          "actual": 0.77,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-03-01",
          "pred": 0.9831083356828674,
          "actual": 0.48,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-06-01",
          "pred": 0.8087302204760568,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-09-01",
          "pred": 0.16913445862276483,
          "actual": 2.01,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-12-01",
          "pred": 2.0649102332333835,
          "actual": 2.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-03-01",
          "pred": 2.572728267801452,
          "actual": 1.6,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-06-01",
          "pred": 1.738359850631373,
          "actual": 0.06,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-09-01",
          "pred": 0.8078047027257461,
          "actual": -0.46,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-12-01",
          "pred": -1.5669030538062354,
          "actual": -0.51,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-03-01",
          "pred": 0.13258760675298698,
          "actual": -0.09,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-06-01",
          "pred": -0.2695274976634279,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-09-01",
          "pred": -0.36819191860030376,
          "actual": -0.56,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-12-01",
          "pred": -0.7269577050870957,
          "actual": -0.85,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-03-01",
          "pred": -1.0451875957469818,
          "actual": -0.73,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-06-01",
          "pred": 0.6726008700230222,
          "actual": 0.12,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-09-01",
          "pred": 0.4217755795786548,
          "actual": 0.3,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-12-01",
          "pred": 0.6528871462132297,
          "actual": 0.97,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-03-01",
          "pred": 0.2452752622152431,
          "actual": 0.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-06-01",
          "pred": -0.6843264251585188,
          "actual": 0.66,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-09-01",
          "pred": -0.36939630544670715,
          "actual": 0.11,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-12-01",
          "pred": 0.2814615734507205,
          "actual": 0.51,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-03-01",
          "pred": 0.3711897476050505,
          "actual": 0.36,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-06-01",
          "pred": 1.1169901506279578,
          "actual": -0.21,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-09-01",
          "pred": -0.026749365406407617,
          "actual": -0.66,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-12-01",
          "pred": -0.4220668662904953,
          "actual": -0.98,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-03-01",
          "pred": -0.9284165114686791,
          "actual": -0.72,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-06-01",
          "pred": -0.13715567444648896,
          "actual": -0.06,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-09-01",
          "pred": -0.8661113389005389,
          "actual": -0.5,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-12-01",
          "pred": 0.372287975358965,
          "actual": -1.07,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-03-01",
          "pred": -0.32954097205008515,
          "actual": -0.84,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-06-01",
          "pred": -0.7037947219506988,
          "actual": -0.77,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-09-01",
          "pred": -0.42163763064063836,
          "actual": -1.06,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-12-01",
          "pred": -0.817729213064856,
          "actual": -0.86,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-03-01",
          "pred": -1.3486539137428268,
          "actual": -0.13,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-06-01",
          "pred": -0.819923714387689,
          "actual": 0.95,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-09-01",
          "pred": 0.31223177889524517,
          "actual": 1.65,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-12-01",
          "pred": 1.6606877231326405,
          "actual": 1.81,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-03-01",
          "pred": 1.9931487031532678,
          "actual": 1.1,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-06-01",
          "pred": 1.583994317444857,
          "actual": 0.25,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-09-01",
          "pred": 0.42608741915497594,
          "actual": -0.11,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-12-01",
          "pred": 0.3091835967776421,
          "actual": -0.58,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-03-01",
          "pred": 1.2577921448668545,
          "actual": 0.05,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-06-01",
          "pred": 0.44835695510362966,
          "actual": 0.01,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-09-01",
          "pred": -0.45258722460039613,
          "actual": -0.3,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-12-01",
          "pred": -0.791555193461916,
          "actual": -0.49,
          "persistence": -0.3
        }
      ],
      "6": [
        {
          "origin": "2006-09-01",
          "date": "2007-03-01",
          "pred": 0.3859177886364858,
          "actual": -0.15,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-06-01",
          "pred": 0.55607706504784,
          "actual": -0.16,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-09-01",
          "pred": 0.8820032501083125,
          "actual": -1.04,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-12-01",
          "pred": 0.7797883286272907,
          "actual": -1.61,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-03-01",
          "pred": 0.9316730879516913,
          "actual": -1.17,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-06-01",
          "pred": -0.31649102371010096,
          "actual": -0.44,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-09-01",
          "pred": -1.1598407289326786,
          "actual": -0.28,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-12-01",
          "pred": -1.5067229215668976,
          "actual": -0.9,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-03-01",
          "pred": -0.9107869277341506,
          "actual": -0.72,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-06-01",
          "pred": -0.9073911471653109,
          "actual": 0.49,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-09-01",
          "pred": 0.08106097569668572,
          "actual": 0.68,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-12-01",
          "pred": 1.7676470253518144,
          "actual": 1.81,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-03-01",
          "pred": 0.5924204108557559,
          "actual": 1.07,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-06-01",
          "pred": -1.113579876686109,
          "actual": -0.62,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-09-01",
          "pred": -0.35281475400757556,
          "actual": -1.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-12-01",
          "pred": 0.29930585103397944,
          "actual": -1.63,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-03-01",
          "pred": -0.02251559074740146,
          "actual": -0.98,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-06-01",
          "pred": 0.6727840335905054,
          "actual": -0.25,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-09-01",
          "pred": -1.3689684197245706,
          "actual": -0.76,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-12-01",
          "pred": -1.7923875909659208,
          "actual": -1.05,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-03-01",
          "pred": -1.5670217258462185,
          "actual": -0.48,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-06-01",
          "pred": -1.1083072291671208,
          "actual": 0.14,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-09-01",
          "pred": 0.8035195192154387,
          "actual": 0.44,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-12-01",
          "pred": 1.7448296143507065,
          "actual": -0.13,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-03-01",
          "pred": 0.1947208608581858,
          "actual": -0.14,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-06-01",
          "pred": -1.2826372561833104,
          "actual": -0.33,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-09-01",
          "pred": -1.1810229690860592,
          "actual": -0.09,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-12-01",
          "pred": -0.40255295980157485,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-03-01",
          "pred": -0.1567816600757474,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-06-01",
          "pred": -0.45994243079934755,
          "actual": 0.48,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-09-01",
          "pred": 0.5084159170953496,
          "actual": 0.37,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-12-01",
          "pred": 1.4250849769884866,
          "actual": 0.77,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-03-01",
          "pred": 0.9304347399909343,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-06-01",
          "pred": 1.1834882991672002,
          "actual": 1.28,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-09-01",
          "pred": 1.73193509946171,
          "actual": 2.01,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-12-01",
          "pred": 0.8676799011673115,
          "actual": 2.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-03-01",
          "pred": 2.108464959461385,
          "actual": 1.6,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-06-01",
          "pred": 2.025977792940335,
          "actual": 0.06,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-09-01",
          "pred": 0.9017642661742318,
          "actual": -0.46,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-12-01",
          "pred": 0.6261003857737638,
          "actual": -0.51,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-03-01",
          "pred": 0.00044101317442911576,
          "actual": -0.09,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-06-01",
          "pred": 1.2579375757872164,
          "actual": 0.22,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-09-01",
          "pred": -0.803690411269634,
          "actual": -0.56,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-12-01",
          "pred": -1.107813839902648,
          "actual": -0.85,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-03-01",
          "pred": -0.4947508933849918,
          "actual": -0.73,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-06-01",
          "pred": 0.06292079606278991,
          "actual": 0.12,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-09-01",
          "pred": 1.4691312578820162,
          "actual": 0.3,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-12-01",
          "pred": 0.589454137169122,
          "actual": 0.97,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-03-01",
          "pred": -0.20902281808342923,
          "actual": 0.81,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-06-01",
          "pred": -0.8734744877013485,
          "actual": 0.66,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-09-01",
          "pred": -1.0348077421646091,
          "actual": 0.11,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-12-01",
          "pred": -0.3712668064991823,
          "actual": 0.51,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-03-01",
          "pred": 0.2979854288991595,
          "actual": 0.36,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-06-01",
          "pred": 0.6121277963951745,
          "actual": -0.21,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-09-01",
          "pred": 1.0488202477260176,
          "actual": -0.66,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-12-01",
          "pred": -0.2528717668205043,
          "actual": -0.98,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-03-01",
          "pred": -0.01292693481581779,
          "actual": -0.72,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-06-01",
          "pred": -0.4334460025006574,
          "actual": -0.06,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-09-01",
          "pred": -0.04508344209734409,
          "actual": -0.5,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-12-01",
          "pred": -0.707153798091255,
          "actual": -1.07,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-03-01",
          "pred": -0.46601325935690263,
          "actual": -0.84,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-06-01",
          "pred": -0.44250249739873565,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-09-01",
          "pred": 0.18954631763028085,
          "actual": -1.06,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-12-01",
          "pred": -0.4208169933718396,
          "actual": -0.86,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-03-01",
          "pred": -0.8533491640560366,
          "actual": -0.13,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-06-01",
          "pred": -1.8568219165475843,
          "actual": 0.95,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-09-01",
          "pred": -0.8208768637249992,
          "actual": 1.65,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-12-01",
          "pred": 0.5063784463730793,
          "actual": 1.81,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-03-01",
          "pred": 1.5123568784033778,
          "actual": 1.1,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-06-01",
          "pred": 1.6333547684036362,
          "actual": 0.25,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-09-01",
          "pred": 1.8998121738964175,
          "actual": -0.11,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-12-01",
          "pred": 0.6493559028012965,
          "actual": -0.58,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-03-01",
          "pred": 1.546758188998967,
          "actual": 0.05,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-06-01",
          "pred": 1.7014623588967877,
          "actual": 0.01,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-09-01",
          "pred": -0.6658079915174897,
          "actual": -0.3,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-12-01",
          "pred": -1.0218108925875657,
          "actual": -0.49,
          "persistence": 0.01
        }
      ],
      "12": [
        {
          "origin": "2006-09-01",
          "date": "2007-09-01",
          "pred": 1.4413082585299053,
          "actual": -1.04,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-12-01",
          "pred": 2.040353316085164,
          "actual": -1.61,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2008-03-01",
          "pred": 1.3134233278393779,
          "actual": -1.17,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2008-06-01",
          "pred": -0.22974747953284105,
          "actual": -0.44,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-09-01",
          "pred": -0.7819913166106726,
          "actual": -0.28,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-12-01",
          "pred": -0.5904833855643914,
          "actual": -0.9,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2009-03-01",
          "pred": -0.799766871379584,
          "actual": -0.72,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2009-06-01",
          "pred": -1.5611822551729402,
          "actual": 0.49,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-09-01",
          "pred": -0.4076295700778163,
          "actual": 0.68,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-12-01",
          "pred": 1.1863394502279774,
          "actual": 1.81,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2010-03-01",
          "pred": -0.6645239990940119,
          "actual": 1.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2010-06-01",
          "pred": -1.0968312498377901,
          "actual": -0.62,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-09-01",
          "pred": -1.1648144281085464,
          "actual": -1.56,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-12-01",
          "pred": 0.49763361062862044,
          "actual": -1.63,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2011-03-01",
          "pred": 0.6805908426216086,
          "actual": -0.98,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2011-06-01",
          "pred": 0.14539053985253203,
          "actual": -0.25,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-09-01",
          "pred": 0.0793381164457368,
          "actual": -0.76,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-12-01",
          "pred": -0.24414779156071448,
          "actual": -1.05,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2012-03-01",
          "pred": -0.8640192089974787,
          "actual": -0.48,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2012-06-01",
          "pred": -0.5072276841451433,
          "actual": 0.14,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-09-01",
          "pred": 0.7692561632284273,
          "actual": 0.44,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-12-01",
          "pred": 0.9864341834586461,
          "actual": -0.13,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2013-03-01",
          "pred": -0.40041833550165196,
          "actual": -0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2013-06-01",
          "pred": -1.7267284437786588,
          "actual": -0.33,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-09-01",
          "pred": -1.657252144475968,
          "actual": -0.09,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-12-01",
          "pred": 0.18998934861008782,
          "actual": -0.09,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2014-03-01",
          "pred": -0.7042280824082818,
          "actual": -0.07,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2014-06-01",
          "pred": -0.9424384008007295,
          "actual": 0.48,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-09-01",
          "pred": 0.21604064034892306,
          "actual": 0.37,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-12-01",
          "pred": 1.0997941678038705,
          "actual": 0.77,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2015-03-01",
          "pred": 2.0518449035190667,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2015-06-01",
          "pred": 1.3143132869701972,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-09-01",
          "pred": 2.1027435266769565,
          "actual": 2.01,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-12-01",
          "pred": 1.6980074105944243,
          "actual": 2.56,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2016-03-01",
          "pred": 1.6424077236417036,
          "actual": 1.6,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2016-06-01",
          "pred": -0.5228378131422896,
          "actual": 0.06,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-09-01",
          "pred": 0.95059643223105,
          "actual": -0.46,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-12-01",
          "pred": 1.4837908686496988,
          "actual": -0.51,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2017-03-01",
          "pred": 1.4998596133524502,
          "actual": -0.09,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2017-06-01",
          "pred": 0.35593846465162216,
          "actual": 0.22,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-09-01",
          "pred": -0.3964488496909801,
          "actual": -0.56,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-12-01",
          "pred": -0.13409673268306987,
          "actual": -0.85,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2018-03-01",
          "pred": 0.0406547520595962,
          "actual": -0.73,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2018-06-01",
          "pred": 0.9165552427089907,
          "actual": 0.12,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-09-01",
          "pred": 2.069864810656871,
          "actual": 0.3,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-12-01",
          "pred": 0.8359824275447905,
          "actual": 0.97,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2019-03-01",
          "pred": -1.2885800316378275,
          "actual": 0.81,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2019-06-01",
          "pred": -2.06134683362713,
          "actual": 0.66,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-09-01",
          "pred": -1.9811891590955824,
          "actual": 0.11,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-12-01",
          "pred": 0.2207803202461086,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2020-03-01",
          "pred": -0.019068767151765847,
          "actual": 0.36,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2020-06-01",
          "pred": -0.17542820747833573,
          "actual": -0.21,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-09-01",
          "pred": -0.4383875847564419,
          "actual": -0.66,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-12-01",
          "pred": -0.05702854207424634,
          "actual": -0.98,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2021-03-01",
          "pred": 1.073412481239901,
          "actual": -0.72,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2021-06-01",
          "pred": 1.5086796740526358,
          "actual": -0.06,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-09-01",
          "pred": 1.4055958441918892,
          "actual": -0.5,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-12-01",
          "pred": 0.44935860851582693,
          "actual": -1.07,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2022-03-01",
          "pred": -0.12218130657587738,
          "actual": -0.84,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2022-06-01",
          "pred": 0.16272046566411547,
          "actual": -0.77,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-09-01",
          "pred": 0.2098571039564193,
          "actual": -1.06,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-12-01",
          "pred": 0.2253983744570942,
          "actual": -0.86,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2023-03-01",
          "pred": -1.0753573906765426,
          "actual": -0.13,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2023-06-01",
          "pred": -2.3794691942774016,
          "actual": 0.95,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-09-01",
          "pred": -1.9811338703892656,
          "actual": 1.65,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-12-01",
          "pred": 0.02749738549535167,
          "actual": 1.81,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2024-03-01",
          "pred": -0.543356959123138,
          "actual": 1.1,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2024-06-01",
          "pred": 0.6081781776397306,
          "actual": 0.25,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-09-01",
          "pred": 1.686296648136797,
          "actual": -0.11,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-12-01",
          "pred": 1.8817118354430775,
          "actual": -0.58,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2025-03-01",
          "pred": 0.7176566515368067,
          "actual": 0.05,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2025-06-01",
          "pred": 0.3879175012452817,
          "actual": 0.01,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-09-01",
          "pred": 1.1618892869350674,
          "actual": -0.3,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-12-01",
          "pred": 0.813832583150767,
          "actual": -0.49,
          "persistence": -0.58
        }
      ],
      "24": [
        {
          "origin": "2006-09-01",
          "date": "2008-09-01",
          "pred": 0.07197455854424113,
          "actual": -0.28,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2008-12-01",
          "pred": -0.14453125822527235,
          "actual": -0.9,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2009-03-01",
          "pred": 1.5125028946523555,
          "actual": -0.72,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2009-06-01",
          "pred": 1.7749678794875086,
          "actual": 0.49,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2009-09-01",
          "pred": 1.6372697020372302,
          "actual": 0.68,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2009-12-01",
          "pred": -0.007639235873169648,
          "actual": 1.81,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2010-03-01",
          "pred": -0.46656956301256775,
          "actual": 1.07,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2010-06-01",
          "pred": -1.506607987962254,
          "actual": -0.62,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2010-09-01",
          "pred": -2.682209985859902,
          "actual": -1.56,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2010-12-01",
          "pred": -1.8336140008749724,
          "actual": -1.63,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2011-03-01",
          "pred": 0.6899363312217669,
          "actual": -0.98,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2011-06-01",
          "pred": 0.6655683964434597,
          "actual": -0.25,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2011-09-01",
          "pred": -0.20932585646677315,
          "actual": -0.76,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2011-12-01",
          "pred": 0.5489987145456339,
          "actual": -1.05,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2012-03-01",
          "pred": 0.8156887522670973,
          "actual": -0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2012-06-01",
          "pred": 1.8014063263789994,
          "actual": 0.14,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2012-09-01",
          "pred": 1.6508261558979276,
          "actual": 0.44,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2012-12-01",
          "pred": 0.5437422914605226,
          "actual": -0.13,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2013-03-01",
          "pred": -1.9410079909899856,
          "actual": -0.14,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2013-06-01",
          "pred": -2.211262573846025,
          "actual": -0.33,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2013-09-01",
          "pred": -2.57510553519222,
          "actual": -0.09,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2013-12-01",
          "pred": -1.3752806221080949,
          "actual": -0.09,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2014-03-01",
          "pred": 0.5835887049412671,
          "actual": -0.07,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2014-06-01",
          "pred": -0.4376406367675334,
          "actual": 0.48,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2014-09-01",
          "pred": 0.5982603764503736,
          "actual": 0.37,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2014-12-01",
          "pred": 1.0382831088678541,
          "actual": 0.77,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2015-03-01",
          "pred": 2.0505083358753504,
          "actual": 0.48,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2015-06-01",
          "pred": 2.2389478220083365,
          "actual": 1.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2015-09-01",
          "pred": 1.7107371256474737,
          "actual": 2.01,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2015-12-01",
          "pred": 0.6284194770546618,
          "actual": 2.56,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2016-03-01",
          "pred": -0.3728141024355566,
          "actual": 1.6,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2016-06-01",
          "pred": -0.14393628292254596,
          "actual": 0.06,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2016-09-01",
          "pred": -1.0355685413461477,
          "actual": -0.46,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2016-12-01",
          "pred": -0.5321814950094009,
          "actual": -0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2017-03-01",
          "pred": -0.5194890022581812,
          "actual": -0.09,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2017-06-01",
          "pred": 2.0611630261935323,
          "actual": 0.22,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2017-09-01",
          "pred": -0.06663552990037253,
          "actual": -0.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2017-12-01",
          "pred": -0.21658533245114614,
          "actual": -0.85,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2018-03-01",
          "pred": 0.7346581957586156,
          "actual": -0.73,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2018-06-01",
          "pred": 1.6019135517612264,
          "actual": 0.12,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2018-09-01",
          "pred": 1.5279351292852414,
          "actual": 0.3,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2018-12-01",
          "pred": 1.1099164332189861,
          "actual": 0.97,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2019-03-01",
          "pred": -1.1350949350771953,
          "actual": 0.81,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2019-06-01",
          "pred": -1.7316464566297287,
          "actual": 0.66,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2019-09-01",
          "pred": -1.4403921072998744,
          "actual": 0.11,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2019-12-01",
          "pred": -0.2619213157718368,
          "actual": 0.51,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2020-03-01",
          "pred": -0.04422076596584335,
          "actual": 0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2020-06-01",
          "pred": -1.760747459822666,
          "actual": -0.21,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2020-09-01",
          "pred": -0.5627262755440261,
          "actual": -0.66,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2020-12-01",
          "pred": -0.5922833668488768,
          "actual": -0.98,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2021-03-01",
          "pred": 0.5857416423631586,
          "actual": -0.72,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2021-06-01",
          "pred": 1.4893652905846715,
          "actual": -0.06,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2021-09-01",
          "pred": 1.5902122750934617,
          "actual": -0.5,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2021-12-01",
          "pred": 1.49967784450738,
          "actual": -1.07,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2022-03-01",
          "pred": 0.30176606732262146,
          "actual": -0.84,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2022-06-01",
          "pred": 0.30717644927457355,
          "actual": -0.77,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2022-09-01",
          "pred": 0.18810444446859867,
          "actual": -1.06,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2022-12-01",
          "pred": 0.0395097831039188,
          "actual": -0.86,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2023-03-01",
          "pred": -0.03180655415677036,
          "actual": -0.13,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2023-06-01",
          "pred": -1.3800170989024396,
          "actual": 0.95,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2023-09-01",
          "pred": -1.6074474423913405,
          "actual": 1.65,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2023-12-01",
          "pred": -0.5791810082109217,
          "actual": 1.81,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2024-03-01",
          "pred": 0.3395543535394874,
          "actual": 1.1,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2024-06-01",
          "pred": 0.1798538984458387,
          "actual": 0.25,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2024-09-01",
          "pred": 0.5271728255205551,
          "actual": -0.11,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2024-12-01",
          "pred": 1.0894593901229552,
          "actual": -0.58,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2025-03-01",
          "pred": 1.5833174010143707,
          "actual": 0.05,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2025-06-01",
          "pred": -0.43109830294713397,
          "actual": 0.01,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2025-09-01",
          "pred": -0.5758719716480172,
          "actual": -0.3,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2025-12-01",
          "pred": 0.970331872670396,
          "actual": -0.49,
          "persistence": 1.81
        }
      ],
      "60": [
        {
          "origin": "2006-09-01",
          "date": "2011-09-01",
          "pred": 0.13928896127152499,
          "actual": -0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2011-12-01",
          "pred": 0.375937799146089,
          "actual": -1.05,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2012-03-01",
          "pred": 1.529926510755196,
          "actual": -0.48,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2012-06-01",
          "pred": 0.6124151335963297,
          "actual": 0.14,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2012-09-01",
          "pred": -0.0076478892508723625,
          "actual": 0.44,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2012-12-01",
          "pred": 0.0735331991247333,
          "actual": -0.13,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2013-03-01",
          "pred": -1.0260752739325387,
          "actual": -0.14,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2013-06-01",
          "pred": -0.77922258655097,
          "actual": -0.33,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2013-09-01",
          "pred": -0.24352902640361818,
          "actual": -0.09,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2013-12-01",
          "pred": 1.0310346866310902,
          "actual": -0.09,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2014-03-01",
          "pred": 0.7730320353726133,
          "actual": -0.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2014-06-01",
          "pred": -0.46558753521875434,
          "actual": 0.48,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2014-09-01",
          "pred": 0.38736923656941835,
          "actual": 0.37,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2014-12-01",
          "pred": 2.127140075945825,
          "actual": 0.77,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2015-03-01",
          "pred": 2.3618326677662393,
          "actual": 0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2015-06-01",
          "pred": 1.525721564185344,
          "actual": 1.28,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2015-09-01",
          "pred": -0.06567290177210823,
          "actual": 2.01,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2015-12-01",
          "pred": -1.4756011989630182,
          "actual": 2.56,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2016-03-01",
          "pred": -1.8743121991209268,
          "actual": 1.6,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2016-06-01",
          "pred": -1.5966990068337843,
          "actual": 0.06,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2016-09-01",
          "pred": -0.1865699557894694,
          "actual": -0.46,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2016-12-01",
          "pred": 0.27898535845053773,
          "actual": -0.51,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2017-03-01",
          "pred": -0.5839225384699636,
          "actual": -0.09,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2017-06-01",
          "pred": -0.7340170973788344,
          "actual": 0.22,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2017-09-01",
          "pred": 0.8597290073757944,
          "actual": -0.56,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2017-12-01",
          "pred": 1.6759693233868858,
          "actual": -0.85,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2018-03-01",
          "pred": 0.6880786073347356,
          "actual": -0.73,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2018-06-01",
          "pred": -0.5405840623428797,
          "actual": 0.12,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2018-09-01",
          "pred": 0.6375612768015246,
          "actual": 0.3,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2018-12-01",
          "pred": 0.5120154521165471,
          "actual": 0.97,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2019-03-01",
          "pred": 0.3017930983621906,
          "actual": 0.81,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2019-06-01",
          "pred": -0.16107562588529006,
          "actual": 0.66,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2019-09-01",
          "pred": 0.9595003206867314,
          "actual": 0.11,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2019-12-01",
          "pred": 0.7974045245288792,
          "actual": 0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2020-03-01",
          "pred": 0.7493522576842018,
          "actual": 0.36,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2020-06-01",
          "pred": 0.7149521023517322,
          "actual": -0.21,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2020-09-01",
          "pred": -0.4762127493521455,
          "actual": -0.66,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2020-12-01",
          "pred": 0.15207810797906068,
          "actual": -0.98,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2021-03-01",
          "pred": 1.7252108756866658,
          "actual": -0.72,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2021-06-01",
          "pred": 0.3640516717326226,
          "actual": -0.06,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2021-09-01",
          "pred": -1.1160771548166295,
          "actual": -0.5,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2021-12-01",
          "pred": -2.093832658485256,
          "actual": -1.07,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2022-03-01",
          "pred": -2.518600042919652,
          "actual": -0.84,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2022-06-01",
          "pred": -1.4438564701534868,
          "actual": -0.77,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2022-09-01",
          "pred": -0.25311702603142455,
          "actual": -1.06,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2022-12-01",
          "pred": -0.9837353046757691,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2023-03-01",
          "pred": -2.472903697240171,
          "actual": -0.13,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2023-06-01",
          "pred": -2.6466471393923046,
          "actual": 0.95,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2023-09-01",
          "pred": -0.7551868711610159,
          "actual": 1.65,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2023-12-01",
          "pred": 0.6880092884041722,
          "actual": 1.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2024-03-01",
          "pred": 1.9108871261450886,
          "actual": 1.1,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2024-06-01",
          "pred": 2.004894192815297,
          "actual": 0.25,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2024-09-01",
          "pred": 1.5547962511768896,
          "actual": -0.11,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2024-12-01",
          "pred": 0.993855138570822,
          "actual": -0.58,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2025-03-01",
          "pred": 0.7688693928776495,
          "actual": 0.05,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2025-06-01",
          "pred": 1.4784051541601169,
          "actual": 0.01,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2025-09-01",
          "pred": 0.9492416026083889,
          "actual": -0.3,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2025-12-01",
          "pred": 0.6212905603386993,
          "actual": -0.49,
          "persistence": -0.98
        }
      ]
    },
    "same_rung_sync_pair_decoder": {
      "1": [
        {
          "origin": "2006-09-01",
          "date": "2006-10-01",
          "pred": 0.4939085199637434,
          "actual": 0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-01-01",
          "pred": 1.2333294714938707,
          "actual": 0.59,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-04-01",
          "pred": 0.39210489314277486,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-07-01",
          "pred": -0.12111133216411299,
          "actual": -0.37,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-10-01",
          "pred": -0.39565930272824074,
          "actual": -1.41,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-01-01",
          "pred": -0.603698892588963,
          "actual": -1.79,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-04-01",
          "pred": -0.9835476674980299,
          "actual": -0.89,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-07-01",
          "pred": -0.9221555063588652,
          "actual": -0.04,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-10-01",
          "pred": -0.3637407444017132,
          "actual": -0.3,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-01-01",
          "pred": -0.0018669895571466408,
          "actual": -1.0,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-04-01",
          "pred": -0.8124228222044909,
          "actual": -0.25,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-07-01",
          "pred": 0.6623318201324485,
          "actual": 0.69,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-10-01",
          "pred": 1.1108883127164821,
          "actual": 0.96,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-01-01",
          "pred": 1.8484043511648205,
          "actual": 1.43,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-04-01",
          "pred": 0.11208707361489545,
          "actual": 0.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-07-01",
          "pred": -0.5830794244003824,
          "actual": -0.89,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-10-01",
          "pred": -1.3364356464953329,
          "actual": -1.65,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-01-01",
          "pred": -1.0952709742655968,
          "actual": -1.7,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-04-01",
          "pred": -1.2610162118257533,
          "actual": -0.74,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-07-01",
          "pred": -0.9470157694984359,
          "actual": -0.23,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-10-01",
          "pred": -0.5834961447366573,
          "actual": -0.93,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-01-01",
          "pred": -1.3070845048658322,
          "actual": -0.93,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-04-01",
          "pred": -0.8704679377113826,
          "actual": -0.29,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-07-01",
          "pred": 0.2902135363387413,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-10-01",
          "pred": 0.8494609615939297,
          "actual": 0.23,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-01-01",
          "pred": -0.04606644135332942,
          "actual": -0.42,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-04-01",
          "pred": -0.7403241846978941,
          "actual": -0.08,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-07-01",
          "pred": -0.5628090576107496,
          "actual": -0.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-10-01",
          "pred": -0.26430131713151944,
          "actual": -0.24,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-01-01",
          "pred": -0.28874892563774507,
          "actual": -0.42,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-04-01",
          "pred": -0.20333938821018888,
          "actual": 0.28,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-07-01",
          "pred": 0.9521445307596391,
          "actual": 0.13,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-10-01",
          "pred": 0.5941764465659543,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-01-01",
          "pred": 1.094775313260871,
          "actual": 0.59,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-04-01",
          "pred": 0.47241076356240613,
          "actual": 0.9,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-07-01",
          "pred": 0.6176746175802867,
          "actual": 1.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-10-01",
          "pred": 2.197494218631465,
          "actual": 2.21,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-01-01",
          "pred": 2.5055099424977345,
          "actual": 2.56,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-04-01",
          "pred": 1.8990750445529516,
          "actual": 1.05,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-07-01",
          "pred": 0.39062172478115265,
          "actual": -0.25,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-10-01",
          "pred": -1.2786009592235088,
          "actual": -0.75,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-01-01",
          "pred": -0.1834865348549154,
          "actual": -0.34,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-04-01",
          "pred": 0.05144887565388233,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-07-01",
          "pred": -0.014729202390732644,
          "actual": 0.22,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-10-01",
          "pred": -0.5076474434430966,
          "actual": -0.52,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-01-01",
          "pred": -0.6591350923340258,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-04-01",
          "pred": 0.21331599877278953,
          "actual": -0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-07-01",
          "pred": 0.23475435304126008,
          "actual": 0.27,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-10-01",
          "pred": 0.24831489190195044,
          "actual": 0.84,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-01-01",
          "pred": 1.0479799883253171,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-04-01",
          "pred": -0.17493299775458462,
          "actual": 0.67,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-07-01",
          "pred": 0.38282218477350044,
          "actual": 0.41,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-10-01",
          "pred": 0.18990117679870477,
          "actual": 0.55,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-01-01",
          "pred": 0.5615828561603243,
          "actual": 0.64,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-04-01",
          "pred": 0.5257086024155848,
          "actual": 0.49,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-07-01",
          "pred": -0.07138878771442099,
          "actual": -0.04,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-10-01",
          "pred": -0.5325433338600175,
          "actual": -1.19,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-01-01",
          "pred": -0.8037275348749765,
          "actual": -1.04,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-04-01",
          "pred": -0.011391368916714713,
          "actual": -0.55,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-07-01",
          "pred": -0.3754979863111625,
          "actual": -0.2,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-10-01",
          "pred": -0.05976230717108902,
          "actual": -0.78,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-01-01",
          "pred": -0.42121002662654855,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-04-01",
          "pred": -0.6004238728291271,
          "actual": -0.9,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-07-01",
          "pred": -0.5056813240991662,
          "actual": -0.56,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-10-01",
          "pred": -0.5803647726505611,
          "actual": -0.99,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-01-01",
          "pred": -0.8085109869722424,
          "actual": -0.78,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-04-01",
          "pred": -0.5057887679247491,
          "actual": 0.24,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-07-01",
          "pred": 0.6562932916653177,
          "actual": 1.2,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-10-01",
          "pred": 1.2968240548488497,
          "actual": 1.59,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-01-01",
          "pred": 1.7207771964679315,
          "actual": 1.71,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-04-01",
          "pred": 1.160603203997266,
          "actual": 0.93,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-07-01",
          "pred": -0.0310111261997585,
          "actual": 0.2,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-10-01",
          "pred": -0.07798271480716976,
          "actual": -0.24,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-01-01",
          "pred": 0.5933007221246251,
          "actual": -0.76,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-04-01",
          "pred": 0.4375996365901809,
          "actual": -0.08,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-07-01",
          "pred": 0.06870578187098289,
          "actual": -0.03,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-10-01",
          "pred": -0.8001147997047923,
          "actual": -0.5,
          "persistence": -0.3
        }
      ],
      "3": [
        {
          "origin": "2006-09-01",
          "date": "2006-12-01",
          "pred": 0.41568229208701263,
          "actual": 1.1,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-03-01",
          "pred": 1.4345844614343157,
          "actual": -0.15,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-06-01",
          "pred": 0.4815186776255829,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-09-01",
          "pred": 0.2525927530116269,
          "actual": -1.04,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-12-01",
          "pred": -0.23488870356758546,
          "actual": -1.61,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-03-01",
          "pred": 0.028156367481772606,
          "actual": -1.17,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-06-01",
          "pred": -0.9813188797350442,
          "actual": -0.44,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-09-01",
          "pred": -1.3861122089165252,
          "actual": -0.28,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-12-01",
          "pred": -0.04914211112934094,
          "actual": -0.9,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-03-01",
          "pred": -0.06722106150716253,
          "actual": -0.72,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-06-01",
          "pred": -1.200660619360338,
          "actual": 0.49,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-09-01",
          "pred": 0.77062760691456,
          "actual": 0.68,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-12-01",
          "pred": 1.8689573771632062,
          "actual": 1.81,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-03-01",
          "pred": 0.6472962815092099,
          "actual": 1.07,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-06-01",
          "pred": -0.2794556194897072,
          "actual": -0.62,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-09-01",
          "pred": -0.04355856922923759,
          "actual": -1.56,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-12-01",
          "pred": -1.2116343934595535,
          "actual": -1.63,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-03-01",
          "pred": -0.6058325319009532,
          "actual": -0.98,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-06-01",
          "pred": -0.9401082104593679,
          "actual": -0.25,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-09-01",
          "pred": -1.599770207735499,
          "actual": -0.76,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-12-01",
          "pred": -0.8422324289709546,
          "actual": -1.05,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-03-01",
          "pred": -1.245530726352359,
          "actual": -0.48,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-06-01",
          "pred": -0.7842226529885509,
          "actual": 0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-09-01",
          "pred": 1.1402324562434947,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-12-01",
          "pred": 0.8802531422057651,
          "actual": -0.13,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-03-01",
          "pred": -0.5625976294866287,
          "actual": -0.14,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-06-01",
          "pred": -1.2385650547436553,
          "actual": -0.33,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-09-01",
          "pred": -0.7707377926816309,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-12-01",
          "pred": -0.3050847828645897,
          "actual": -0.09,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-03-01",
          "pred": -0.18415352781939293,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-06-01",
          "pred": 0.1385410316722145,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-09-01",
          "pred": 1.0884361888717589,
          "actual": 0.37,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-12-01",
          "pred": 0.8151407156311241,
          "actual": 0.77,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-03-01",
          "pred": 0.9987913443736014,
          "actual": 0.48,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-06-01",
          "pred": 0.8210494219190098,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-09-01",
          "pred": 0.16364039763409946,
          "actual": 2.01,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-12-01",
          "pred": 2.076416112345117,
          "actual": 2.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-03-01",
          "pred": 2.58255506735547,
          "actual": 1.6,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-06-01",
          "pred": 1.747495441574412,
          "actual": 0.06,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-09-01",
          "pred": 0.8156196260046747,
          "actual": -0.46,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-12-01",
          "pred": -1.5610390300410368,
          "actual": -0.51,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-03-01",
          "pred": 0.1622705835733281,
          "actual": -0.09,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-06-01",
          "pred": -0.24595615082817718,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-09-01",
          "pred": -0.3543813383188026,
          "actual": -0.56,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-12-01",
          "pred": -0.7074611354908806,
          "actual": -0.85,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-03-01",
          "pred": -1.0439312539347196,
          "actual": -0.73,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-06-01",
          "pred": 0.686004624640252,
          "actual": 0.12,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-09-01",
          "pred": 0.42202132719533897,
          "actual": 0.3,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-12-01",
          "pred": 0.6531121438767746,
          "actual": 0.97,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-03-01",
          "pred": 0.25401876250209104,
          "actual": 0.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-06-01",
          "pred": -0.6832745836443821,
          "actual": 0.66,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-09-01",
          "pred": -0.35925359250484895,
          "actual": 0.11,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-12-01",
          "pred": 0.3007268415539282,
          "actual": 0.51,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-03-01",
          "pred": 0.3858285342120916,
          "actual": 0.36,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-06-01",
          "pred": 1.1331543040134673,
          "actual": -0.21,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-09-01",
          "pred": 0.013122960258694482,
          "actual": -0.66,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-12-01",
          "pred": -0.3931599439478468,
          "actual": -0.98,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-03-01",
          "pred": -0.9156251281441345,
          "actual": -0.72,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-06-01",
          "pred": -0.13010355746084112,
          "actual": -0.06,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-09-01",
          "pred": -0.8526473453891492,
          "actual": -0.5,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-12-01",
          "pred": 0.36174439086472887,
          "actual": -1.07,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-03-01",
          "pred": -0.304467226058229,
          "actual": -0.84,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-06-01",
          "pred": -0.6982014576431681,
          "actual": -0.77,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-09-01",
          "pred": -0.4212685824475167,
          "actual": -1.06,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-12-01",
          "pred": -0.8285873294647783,
          "actual": -0.86,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-03-01",
          "pred": -1.3527009031167512,
          "actual": -0.13,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-06-01",
          "pred": -0.8309540658905615,
          "actual": 0.95,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-09-01",
          "pred": 0.30693011813716625,
          "actual": 1.65,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-12-01",
          "pred": 1.6567500944931932,
          "actual": 1.81,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-03-01",
          "pred": 2.001795374590561,
          "actual": 1.1,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-06-01",
          "pred": 1.569573451766543,
          "actual": 0.25,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-09-01",
          "pred": 0.41033878286724407,
          "actual": -0.11,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-12-01",
          "pred": 0.3098289027466586,
          "actual": -0.58,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-03-01",
          "pred": 1.25690419089253,
          "actual": 0.05,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-06-01",
          "pred": 0.4662981269842995,
          "actual": 0.01,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-09-01",
          "pred": -0.4392982059316462,
          "actual": -0.3,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-12-01",
          "pred": -0.7782592957491614,
          "actual": -0.49,
          "persistence": -0.3
        }
      ],
      "6": [
        {
          "origin": "2006-09-01",
          "date": "2007-03-01",
          "pred": 0.40128915128081755,
          "actual": -0.15,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-06-01",
          "pred": 0.5633368342990143,
          "actual": -0.16,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-09-01",
          "pred": 0.8605662090976,
          "actual": -1.04,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-12-01",
          "pred": 0.8043601331589203,
          "actual": -1.61,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-03-01",
          "pred": 0.9369211401780128,
          "actual": -1.17,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-06-01",
          "pred": -0.32209893594276606,
          "actual": -0.44,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-09-01",
          "pred": -1.1461372698609198,
          "actual": -0.28,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-12-01",
          "pred": -1.5240760452203508,
          "actual": -0.9,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-03-01",
          "pred": -0.8963546589028034,
          "actual": -0.72,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-06-01",
          "pred": -0.8999589237395831,
          "actual": 0.49,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-09-01",
          "pred": 0.06267358328253445,
          "actual": 0.68,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-12-01",
          "pred": 1.8386293935638591,
          "actual": 1.81,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-03-01",
          "pred": 0.6509386559573911,
          "actual": 1.07,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-06-01",
          "pred": -1.0480752257536463,
          "actual": -0.62,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-09-01",
          "pred": -0.3240337677265692,
          "actual": -1.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-12-01",
          "pred": 0.261241316505428,
          "actual": -1.63,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-03-01",
          "pred": -0.015275634137683158,
          "actual": -0.98,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-06-01",
          "pred": 0.7233111274693602,
          "actual": -0.25,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-09-01",
          "pred": -1.3277833159036283,
          "actual": -0.76,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-12-01",
          "pred": -1.8322538219087439,
          "actual": -1.05,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-03-01",
          "pred": -1.5414283837277836,
          "actual": -0.48,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-06-01",
          "pred": -1.1409981396551514,
          "actual": 0.14,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-09-01",
          "pred": 0.8169079459329021,
          "actual": 0.44,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-12-01",
          "pred": 1.7974395302565631,
          "actual": -0.13,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-03-01",
          "pred": 0.23065785179332782,
          "actual": -0.14,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-06-01",
          "pred": -1.2904203703568733,
          "actual": -0.33,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-09-01",
          "pred": -1.2139613634432902,
          "actual": -0.09,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-12-01",
          "pred": -0.43734626772420665,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-03-01",
          "pred": -0.24627186851162247,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-06-01",
          "pred": -0.5459844637546942,
          "actual": 0.48,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-09-01",
          "pred": 0.49923051472008273,
          "actual": 0.37,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-12-01",
          "pred": 1.4179163673013973,
          "actual": 0.77,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-03-01",
          "pred": 0.9425340639709938,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-06-01",
          "pred": 1.2050788988549102,
          "actual": 1.28,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-09-01",
          "pred": 1.6760164479028932,
          "actual": 2.01,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-12-01",
          "pred": 0.8596740048688263,
          "actual": 2.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-03-01",
          "pred": 2.116146897644652,
          "actual": 1.6,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-06-01",
          "pred": 2.0541024205517657,
          "actual": 0.06,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-09-01",
          "pred": 0.9271231893223125,
          "actual": -0.46,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-12-01",
          "pred": 0.6531011907750403,
          "actual": -0.51,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-03-01",
          "pred": 0.005680828829780682,
          "actual": -0.09,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-06-01",
          "pred": 1.3233209425221204,
          "actual": 0.22,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-09-01",
          "pred": -0.808999608709106,
          "actual": -0.56,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-12-01",
          "pred": -1.0691226330485908,
          "actual": -0.85,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-03-01",
          "pred": -0.5018051331559917,
          "actual": -0.73,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-06-01",
          "pred": 0.06340367254822765,
          "actual": 0.12,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-09-01",
          "pred": 1.5391707567245674,
          "actual": 0.3,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-12-01",
          "pred": 0.6303624472252508,
          "actual": 0.97,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-03-01",
          "pred": -0.1870135411785576,
          "actual": 0.81,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-06-01",
          "pred": -0.8697814967103289,
          "actual": 0.66,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-09-01",
          "pred": -1.0317275880240913,
          "actual": 0.11,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-12-01",
          "pred": -0.3644085159493168,
          "actual": 0.51,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-03-01",
          "pred": 0.3018171699401915,
          "actual": 0.36,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-06-01",
          "pred": 0.6839509226767985,
          "actual": -0.21,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-09-01",
          "pred": 1.0729997676190977,
          "actual": -0.66,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-12-01",
          "pred": -0.13450559700701595,
          "actual": -0.98,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-03-01",
          "pred": 0.03891758232734818,
          "actual": -0.72,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-06-01",
          "pred": -0.4183603728200792,
          "actual": -0.06,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-09-01",
          "pred": -0.015336530341048791,
          "actual": -0.5,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-12-01",
          "pred": -0.5645072019678083,
          "actual": -1.07,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-03-01",
          "pred": -0.3136499141890931,
          "actual": -0.84,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-06-01",
          "pred": -0.43893049705483234,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-09-01",
          "pred": 0.18039456352466027,
          "actual": -1.06,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-12-01",
          "pred": -0.42530076049378307,
          "actual": -0.86,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-03-01",
          "pred": -0.8846215542100763,
          "actual": -0.13,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-06-01",
          "pred": -1.8695865384123915,
          "actual": 0.95,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-09-01",
          "pred": -0.8079538538920261,
          "actual": 1.65,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-12-01",
          "pred": 0.48713830809239794,
          "actual": 1.81,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-03-01",
          "pred": 1.5365237069464905,
          "actual": 1.1,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-06-01",
          "pred": 1.6861763796210798,
          "actual": 0.25,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-09-01",
          "pred": 1.8785464959255778,
          "actual": -0.11,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-12-01",
          "pred": 0.7088572936087995,
          "actual": -0.58,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-03-01",
          "pred": 1.5526757869708054,
          "actual": 0.05,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-06-01",
          "pred": 1.7139011582323926,
          "actual": 0.01,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-09-01",
          "pred": -0.619653315327147,
          "actual": -0.3,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-12-01",
          "pred": -1.0319540025216853,
          "actual": -0.49,
          "persistence": 0.01
        }
      ],
      "12": [
        {
          "origin": "2006-09-01",
          "date": "2007-09-01",
          "pred": 1.4278311582081142,
          "actual": -1.04,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-12-01",
          "pred": 2.03883852619175,
          "actual": -1.61,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2008-03-01",
          "pred": 1.2716526947700897,
          "actual": -1.17,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2008-06-01",
          "pred": -0.2577386694383834,
          "actual": -0.44,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-09-01",
          "pred": -0.7023567946531689,
          "actual": -0.28,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-12-01",
          "pred": -0.650914665073355,
          "actual": -0.9,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2009-03-01",
          "pred": -0.8183917647109977,
          "actual": -0.72,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2009-06-01",
          "pred": -1.5583563181457931,
          "actual": 0.49,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-09-01",
          "pred": -0.4427041962190873,
          "actual": 0.68,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-12-01",
          "pred": 1.1346796178437506,
          "actual": 1.81,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2010-03-01",
          "pred": -0.5960717141593962,
          "actual": 1.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2010-06-01",
          "pred": -0.9972860972881824,
          "actual": -0.62,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-09-01",
          "pred": -1.088198681242682,
          "actual": -1.56,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-12-01",
          "pred": 0.6116929847766519,
          "actual": -1.63,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2011-03-01",
          "pred": 0.8214997816463137,
          "actual": -0.98,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2011-06-01",
          "pred": 0.23064655171761173,
          "actual": -0.25,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-09-01",
          "pred": 0.034956944917806945,
          "actual": -0.76,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-12-01",
          "pred": -0.38016101485196124,
          "actual": -1.05,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2012-03-01",
          "pred": -0.9067117073547961,
          "actual": -0.48,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2012-06-01",
          "pred": -0.5738381135800853,
          "actual": 0.14,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-09-01",
          "pred": 0.6302585104363947,
          "actual": 0.44,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-12-01",
          "pred": 0.9930512855266156,
          "actual": -0.13,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2013-03-01",
          "pred": -0.306666812555747,
          "actual": -0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2013-06-01",
          "pred": -1.8092536587039723,
          "actual": -0.33,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-09-01",
          "pred": -1.73015718933952,
          "actual": -0.09,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-12-01",
          "pred": -0.11117647601577084,
          "actual": -0.09,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2014-03-01",
          "pred": -0.8620238625097034,
          "actual": -0.07,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2014-06-01",
          "pred": -1.0359111127553784,
          "actual": 0.48,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-09-01",
          "pred": 0.05912635025943526,
          "actual": 0.37,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-12-01",
          "pred": 0.8182383864531274,
          "actual": 0.77,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2015-03-01",
          "pred": 1.9432543280961232,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2015-06-01",
          "pred": 1.192433002448701,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-09-01",
          "pred": 1.8589269666009274,
          "actual": 2.01,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-12-01",
          "pred": 1.6896251033244505,
          "actual": 2.56,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2016-03-01",
          "pred": 1.6592139034024522,
          "actual": 1.6,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2016-06-01",
          "pred": -0.4880710749996855,
          "actual": 0.06,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-09-01",
          "pred": 1.0355883366976297,
          "actual": -0.46,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-12-01",
          "pred": 1.5782320570069273,
          "actual": -0.51,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2017-03-01",
          "pred": 1.3584490660554533,
          "actual": -0.09,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2017-06-01",
          "pred": 0.4252152766282296,
          "actual": 0.22,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-09-01",
          "pred": -0.418289868571829,
          "actual": -0.56,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-12-01",
          "pred": -0.08725280792225196,
          "actual": -0.85,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2018-03-01",
          "pred": 0.11743953564248368,
          "actual": -0.73,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2018-06-01",
          "pred": 0.9019758752847795,
          "actual": 0.12,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-09-01",
          "pred": 2.0774396482709085,
          "actual": 0.3,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-12-01",
          "pred": 0.829932828469897,
          "actual": 0.97,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2019-03-01",
          "pred": -1.2604237536670901,
          "actual": 0.81,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2019-06-01",
          "pred": -2.017347806281532,
          "actual": 0.66,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-09-01",
          "pred": -1.9228634645431515,
          "actual": 0.11,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-12-01",
          "pred": 0.21076355962893506,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2020-03-01",
          "pred": -0.0010815630005369479,
          "actual": 0.36,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2020-06-01",
          "pred": -0.14425581693308961,
          "actual": -0.21,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-09-01",
          "pred": -0.38857638387898036,
          "actual": -0.66,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-12-01",
          "pred": -0.13483541649244618,
          "actual": -0.98,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2021-03-01",
          "pred": 1.1032906227287353,
          "actual": -0.72,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2021-06-01",
          "pred": 1.5162717568362818,
          "actual": -0.06,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-09-01",
          "pred": 1.3704056691212867,
          "actual": -0.5,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-12-01",
          "pred": 0.45728501520711606,
          "actual": -1.07,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2022-03-01",
          "pred": -0.05552351864224994,
          "actual": -0.84,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2022-06-01",
          "pred": 0.17897515158502122,
          "actual": -0.77,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-09-01",
          "pred": 0.2922202372462199,
          "actual": -1.06,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-12-01",
          "pred": 0.2834232703185197,
          "actual": -0.86,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2023-03-01",
          "pred": -1.0370007794598741,
          "actual": -0.13,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2023-06-01",
          "pred": -2.32553777139185,
          "actual": 0.95,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-09-01",
          "pred": -1.9772758369349233,
          "actual": 1.65,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-12-01",
          "pred": 0.026887253058148784,
          "actual": 1.81,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2024-03-01",
          "pred": -0.5169543562280791,
          "actual": 1.1,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2024-06-01",
          "pred": 0.5952132532063662,
          "actual": 0.25,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-09-01",
          "pred": 1.7780308595806078,
          "actual": -0.11,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-12-01",
          "pred": 1.923658007603646,
          "actual": -0.58,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2025-03-01",
          "pred": 0.7035387625273508,
          "actual": 0.05,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2025-06-01",
          "pred": 0.3736543428792703,
          "actual": 0.01,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-09-01",
          "pred": 1.1783713363111736,
          "actual": -0.3,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-12-01",
          "pred": 0.7664002857216312,
          "actual": -0.49,
          "persistence": -0.58
        }
      ],
      "24": [
        {
          "origin": "2006-09-01",
          "date": "2008-09-01",
          "pred": -0.003106588092932637,
          "actual": -0.28,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2008-12-01",
          "pred": -0.14468050688892295,
          "actual": -0.9,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2009-03-01",
          "pred": 1.346805602057099,
          "actual": -0.72,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2009-06-01",
          "pred": 1.7105587071231494,
          "actual": 0.49,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2009-09-01",
          "pred": 1.5446488002693146,
          "actual": 0.68,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2009-12-01",
          "pred": -0.10617178629253277,
          "actual": 1.81,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2010-03-01",
          "pred": -0.6865624452937136,
          "actual": 1.07,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2010-06-01",
          "pred": -1.5354475372396115,
          "actual": -0.62,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2010-09-01",
          "pred": -2.6270059504698087,
          "actual": -1.56,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2010-12-01",
          "pred": -1.8748759721451316,
          "actual": -1.63,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2011-03-01",
          "pred": 0.38859933506576605,
          "actual": -0.98,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2011-06-01",
          "pred": 0.9792598804503052,
          "actual": -0.25,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2011-09-01",
          "pred": -0.26729532181187204,
          "actual": -0.76,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2011-12-01",
          "pred": 0.7706197741466645,
          "actual": -1.05,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2012-03-01",
          "pred": 0.8908006863617385,
          "actual": -0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2012-06-01",
          "pred": 1.8819211697871163,
          "actual": 0.14,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2012-09-01",
          "pred": 1.8136044414448718,
          "actual": 0.44,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2012-12-01",
          "pred": 0.6492553170221381,
          "actual": -0.13,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2013-03-01",
          "pred": -1.829319691333626,
          "actual": -0.14,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2013-06-01",
          "pred": -2.243321891483424,
          "actual": -0.33,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2013-09-01",
          "pred": -2.6132391104367123,
          "actual": -0.09,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2013-12-01",
          "pred": -1.4538057399277422,
          "actual": -0.09,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2014-03-01",
          "pred": 0.496778343008232,
          "actual": -0.07,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2014-06-01",
          "pred": -0.64473382371581,
          "actual": 0.48,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2014-09-01",
          "pred": 0.27758693669983553,
          "actual": 0.37,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2014-12-01",
          "pred": 0.7352617860880771,
          "actual": 0.77,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2015-03-01",
          "pred": 1.8303833864717929,
          "actual": 0.48,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2015-06-01",
          "pred": 2.0208090019361973,
          "actual": 1.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2015-09-01",
          "pred": 1.6359161343771964,
          "actual": 2.01,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2015-12-01",
          "pred": 0.49529745059656555,
          "actual": 2.56,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2016-03-01",
          "pred": -0.4895940745244579,
          "actual": 1.6,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2016-06-01",
          "pred": -0.2990995647002923,
          "actual": 0.06,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2016-09-01",
          "pred": -0.8139458078814429,
          "actual": -0.46,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2016-12-01",
          "pred": -0.4327894570219471,
          "actual": -0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2017-03-01",
          "pred": -0.43475697941116176,
          "actual": -0.09,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2017-06-01",
          "pred": 2.067600735075398,
          "actual": 0.22,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2017-09-01",
          "pred": -0.011544099934772713,
          "actual": -0.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2017-12-01",
          "pred": -0.32459073109582304,
          "actual": -0.85,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2018-03-01",
          "pred": 0.8180481264163424,
          "actual": -0.73,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2018-06-01",
          "pred": 1.5794566526707357,
          "actual": 0.12,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2018-09-01",
          "pred": 1.4177776140423688,
          "actual": 0.3,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2018-12-01",
          "pred": 1.153650032664626,
          "actual": 0.97,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2019-03-01",
          "pred": -1.045195558350984,
          "actual": 0.81,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2019-06-01",
          "pred": -1.528907823890634,
          "actual": 0.66,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2019-09-01",
          "pred": -1.3352961287145142,
          "actual": 0.11,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2019-12-01",
          "pred": -0.31831088282663456,
          "actual": 0.51,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2020-03-01",
          "pred": 0.14180277121052295,
          "actual": 0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2020-06-01",
          "pred": -1.7133502633376319,
          "actual": -0.21,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2020-09-01",
          "pred": -0.7439998912388375,
          "actual": -0.66,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2020-12-01",
          "pred": -0.8476943092344907,
          "actual": -0.98,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2021-03-01",
          "pred": 0.569406167759463,
          "actual": -0.72,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2021-06-01",
          "pred": 1.4296610541320913,
          "actual": -0.06,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2021-09-01",
          "pred": 1.5781975206330678,
          "actual": -0.5,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2021-12-01",
          "pred": 1.4367653610760642,
          "actual": -1.07,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2022-03-01",
          "pred": 0.2540037423692183,
          "actual": -0.84,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2022-06-01",
          "pred": 0.20123030884193507,
          "actual": -0.77,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2022-09-01",
          "pred": 0.31971475664164395,
          "actual": -1.06,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2022-12-01",
          "pred": 0.15214874830709246,
          "actual": -0.86,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2023-03-01",
          "pred": 0.0017374172333823844,
          "actual": -0.13,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2023-06-01",
          "pred": -1.2304109832399528,
          "actual": 0.95,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2023-09-01",
          "pred": -1.6191587752193757,
          "actual": 1.65,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2023-12-01",
          "pred": -0.5592862794263481,
          "actual": 1.81,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2024-03-01",
          "pred": 0.2942720455631812,
          "actual": 1.1,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2024-06-01",
          "pred": 0.31833809364539944,
          "actual": 0.25,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2024-09-01",
          "pred": 0.5395231084838579,
          "actual": -0.11,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2024-12-01",
          "pred": 1.0406837789912267,
          "actual": -0.58,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2025-03-01",
          "pred": 1.6351697890668189,
          "actual": 0.05,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2025-06-01",
          "pred": -0.3827475728353342,
          "actual": 0.01,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2025-09-01",
          "pred": -0.5054901858614613,
          "actual": -0.3,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2025-12-01",
          "pred": 1.161890285215119,
          "actual": -0.49,
          "persistence": 1.81
        }
      ],
      "60": [
        {
          "origin": "2006-09-01",
          "date": "2011-09-01",
          "pred": -0.8027785455755435,
          "actual": -0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2011-12-01",
          "pred": -0.05713685256352012,
          "actual": -1.05,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2012-03-01",
          "pred": 0.9706288376603052,
          "actual": -0.48,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2012-06-01",
          "pred": -0.09015437810006471,
          "actual": 0.14,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2012-09-01",
          "pred": -0.28432933291239043,
          "actual": 0.44,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2012-12-01",
          "pred": -0.7606262194645522,
          "actual": -0.13,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2013-03-01",
          "pred": -1.2927920150149073,
          "actual": -0.14,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2013-06-01",
          "pred": -1.7297718007465361,
          "actual": -0.33,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2013-09-01",
          "pred": -0.5177599751322876,
          "actual": -0.09,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2013-12-01",
          "pred": 1.652316377892827,
          "actual": -0.09,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2014-03-01",
          "pred": 0.3875482574260538,
          "actual": -0.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2014-06-01",
          "pred": 0.028142009748801475,
          "actual": 0.48,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2014-09-01",
          "pred": 0.8792189237243048,
          "actual": 0.37,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2014-12-01",
          "pred": 2.365560724728093,
          "actual": 0.77,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2015-03-01",
          "pred": 2.8800256486805464,
          "actual": 0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2015-06-01",
          "pred": 2.011180877315654,
          "actual": 1.28,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2015-09-01",
          "pred": 0.30365544258088645,
          "actual": 2.01,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2015-12-01",
          "pred": -1.0707233508043832,
          "actual": 2.56,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2016-03-01",
          "pred": -1.8252311948275535,
          "actual": 1.6,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2016-06-01",
          "pred": -1.6602060641120886,
          "actual": 0.06,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2016-09-01",
          "pred": -0.8074301138109732,
          "actual": -0.46,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2016-12-01",
          "pred": 0.4498435954913911,
          "actual": -0.51,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2017-03-01",
          "pred": -0.41023111845164595,
          "actual": -0.09,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2017-06-01",
          "pred": -1.7125118267057884,
          "actual": 0.22,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2017-09-01",
          "pred": -0.02651986596813455,
          "actual": -0.56,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2017-12-01",
          "pred": 1.7367775960304945,
          "actual": -0.85,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2018-03-01",
          "pred": 0.3005702774054974,
          "actual": -0.73,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2018-06-01",
          "pred": -0.7574981782022824,
          "actual": 0.12,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2018-09-01",
          "pred": 0.011695663461826378,
          "actual": 0.3,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2018-12-01",
          "pred": -0.7313901646277668,
          "actual": 0.97,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2019-03-01",
          "pred": -1.0734824855931802,
          "actual": 0.81,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2019-06-01",
          "pred": -1.6374684803068522,
          "actual": 0.66,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2019-09-01",
          "pred": -0.06736490804240974,
          "actual": 0.11,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2019-12-01",
          "pred": -0.32118291403272853,
          "actual": 0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2020-03-01",
          "pred": -0.13965527515527257,
          "actual": 0.36,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2020-06-01",
          "pred": 0.14773164817548465,
          "actual": -0.21,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2020-09-01",
          "pred": -0.49751607763217887,
          "actual": -0.66,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2020-12-01",
          "pred": 0.5003498714143206,
          "actual": -0.98,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2021-03-01",
          "pred": 1.7915945325267746,
          "actual": -0.72,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2021-06-01",
          "pred": 0.6065983270940566,
          "actual": -0.06,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2021-09-01",
          "pred": -1.64527854056017,
          "actual": -0.5,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2021-12-01",
          "pred": -1.7455973830743012,
          "actual": -1.07,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2022-03-01",
          "pred": -2.161608980377599,
          "actual": -0.84,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2022-06-01",
          "pred": -1.8152709768968243,
          "actual": -0.77,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2022-09-01",
          "pred": -0.41858693445429035,
          "actual": -1.06,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2022-12-01",
          "pred": -0.5614201229634084,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2023-03-01",
          "pred": -2.027605717213501,
          "actual": -0.13,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2023-06-01",
          "pred": -2.6745931062104416,
          "actual": 0.95,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2023-09-01",
          "pred": -1.1639955761024876,
          "actual": 1.65,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2023-12-01",
          "pred": 0.06226849972921364,
          "actual": 1.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2024-03-01",
          "pred": 1.7592231499531261,
          "actual": 1.1,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2024-06-01",
          "pred": 1.8420634495701864,
          "actual": 0.25,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2024-09-01",
          "pred": 1.3505043193671404,
          "actual": -0.11,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2024-12-01",
          "pred": 1.0177171750779244,
          "actual": -0.58,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2025-03-01",
          "pred": 0.8742319114527672,
          "actual": 0.05,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2025-06-01",
          "pred": 1.2762237530713945,
          "actual": 0.01,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2025-09-01",
          "pred": 0.7374231959057378,
          "actual": -0.3,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2025-12-01",
          "pred": 0.6761460198230379,
          "actual": -0.49,
          "persistence": -0.98
        }
      ]
    },
    "same_rung_gear_pair_decoder": {
      "1": [
        {
          "origin": "2006-09-01",
          "date": "2006-10-01",
          "pred": 0.5003343547587141,
          "actual": 0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-01-01",
          "pred": 1.2413064338042137,
          "actual": 0.59,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-04-01",
          "pred": 0.4024390543011697,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-07-01",
          "pred": -0.11097535793120972,
          "actual": -0.37,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-10-01",
          "pred": -0.3844789913649103,
          "actual": -1.41,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-01-01",
          "pred": -0.596926007585543,
          "actual": -1.79,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-04-01",
          "pred": -0.96934006766867,
          "actual": -0.89,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-07-01",
          "pred": -0.9093351945864407,
          "actual": -0.04,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-10-01",
          "pred": -0.3569160377665954,
          "actual": -0.3,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-01-01",
          "pred": 0.005250648000650553,
          "actual": -1.0,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-04-01",
          "pred": -0.798609178694958,
          "actual": -0.25,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-07-01",
          "pred": 0.6630503373829669,
          "actual": 0.69,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-10-01",
          "pred": 1.1142095170941162,
          "actual": 0.96,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-01-01",
          "pred": 1.844853611392378,
          "actual": 1.43,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-04-01",
          "pred": 0.11179089254772559,
          "actual": 0.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-07-01",
          "pred": -0.582447682560979,
          "actual": -0.89,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-10-01",
          "pred": -1.334223827778187,
          "actual": -1.65,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-01-01",
          "pred": -1.0881163244554362,
          "actual": -1.7,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-04-01",
          "pred": -1.2551871039724933,
          "actual": -0.74,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-07-01",
          "pred": -0.9383648631942587,
          "actual": -0.23,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-10-01",
          "pred": -0.5764546287892403,
          "actual": -0.93,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-01-01",
          "pred": -1.2996150026351574,
          "actual": -0.93,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-04-01",
          "pred": -0.8632769450928721,
          "actual": -0.29,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-07-01",
          "pred": 0.29887328489426207,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-10-01",
          "pred": 0.860931523089713,
          "actual": 0.23,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-01-01",
          "pred": -0.03455197671238171,
          "actual": -0.42,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-04-01",
          "pred": -0.7304580157844327,
          "actual": -0.08,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-07-01",
          "pred": -0.5478590053957422,
          "actual": -0.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-10-01",
          "pred": -0.2600545736268153,
          "actual": -0.24,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-01-01",
          "pred": -0.2792136420102543,
          "actual": -0.42,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-04-01",
          "pred": -0.1872362705663449,
          "actual": 0.28,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-07-01",
          "pred": 0.9580829527528117,
          "actual": 0.13,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-10-01",
          "pred": 0.5951787738171561,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-01-01",
          "pred": 1.0929553283633093,
          "actual": 0.59,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-04-01",
          "pred": 0.47207579992552734,
          "actual": 0.9,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-07-01",
          "pred": 0.6160274806973298,
          "actual": 1.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-10-01",
          "pred": 2.1941954914140167,
          "actual": 2.21,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-01-01",
          "pred": 2.5045900748116767,
          "actual": 2.56,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-04-01",
          "pred": 1.9003061184668224,
          "actual": 1.05,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-07-01",
          "pred": 0.39205839850498636,
          "actual": -0.25,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-10-01",
          "pred": -1.278630672212601,
          "actual": -0.75,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-01-01",
          "pred": -0.19180728594655466,
          "actual": -0.34,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-04-01",
          "pred": 0.04894926496061634,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-07-01",
          "pred": -0.0146651465493947,
          "actual": 0.22,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-10-01",
          "pred": -0.5056364138004226,
          "actual": -0.52,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-01-01",
          "pred": -0.6577435128010873,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-04-01",
          "pred": 0.21305194696074614,
          "actual": -0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-07-01",
          "pred": 0.23967338301184943,
          "actual": 0.27,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-10-01",
          "pred": 0.2509589827138416,
          "actual": 0.84,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-01-01",
          "pred": 1.053851570573964,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-04-01",
          "pred": -0.17124194676034454,
          "actual": 0.67,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-07-01",
          "pred": 0.38513741541327084,
          "actual": 0.41,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-10-01",
          "pred": 0.19477075347568235,
          "actual": 0.55,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-01-01",
          "pred": 0.5666830058732217,
          "actual": 0.64,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-04-01",
          "pred": 0.5322155837140476,
          "actual": 0.49,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-07-01",
          "pred": -0.06869316155418052,
          "actual": -0.04,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-10-01",
          "pred": -0.5283604069268452,
          "actual": -1.19,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-01-01",
          "pred": -0.8071530974707003,
          "actual": -1.04,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-04-01",
          "pred": -0.018637516857561754,
          "actual": -0.55,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-07-01",
          "pred": -0.37948538771616247,
          "actual": -0.2,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-10-01",
          "pred": -0.06365442137955882,
          "actual": -0.78,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-01-01",
          "pred": -0.42261503487961244,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-04-01",
          "pred": -0.6021584329316082,
          "actual": -0.9,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-07-01",
          "pred": -0.5071792280738393,
          "actual": -0.56,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-10-01",
          "pred": -0.5775231250765994,
          "actual": -0.99,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-01-01",
          "pred": -0.8087001292003355,
          "actual": -0.78,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-04-01",
          "pred": -0.5045993506638484,
          "actual": 0.24,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-07-01",
          "pred": 0.6531949059225216,
          "actual": 1.2,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-10-01",
          "pred": 1.2907402532411163,
          "actual": 1.59,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-01-01",
          "pred": 1.7189951620418402,
          "actual": 1.71,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-04-01",
          "pred": 1.165921570754795,
          "actual": 0.93,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-07-01",
          "pred": -0.025861687423013837,
          "actual": 0.2,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-10-01",
          "pred": -0.07302430486397232,
          "actual": -0.24,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-01-01",
          "pred": 0.5969492171285442,
          "actual": -0.76,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-04-01",
          "pred": 0.4389608146481951,
          "actual": -0.08,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-07-01",
          "pred": 0.07478436825880519,
          "actual": -0.03,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-10-01",
          "pred": -0.7982317214708514,
          "actual": -0.5,
          "persistence": -0.3
        }
      ],
      "3": [
        {
          "origin": "2006-09-01",
          "date": "2006-12-01",
          "pred": 0.440552083913433,
          "actual": 1.1,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-03-01",
          "pred": 1.4586534168888023,
          "actual": -0.15,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-06-01",
          "pred": 0.5102507653201446,
          "actual": -0.16,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-09-01",
          "pred": 0.27425443919906833,
          "actual": -1.04,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2007-12-01",
          "pred": -0.21567224714209288,
          "actual": -1.61,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-03-01",
          "pred": 0.06290695425111245,
          "actual": -1.17,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-06-01",
          "pred": -0.9400904028513494,
          "actual": -0.44,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-09-01",
          "pred": -1.351893176697542,
          "actual": -0.28,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2008-12-01",
          "pred": -0.04687507819899738,
          "actual": -0.9,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-03-01",
          "pred": -0.046836502434924814,
          "actual": -0.72,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-06-01",
          "pred": -1.1585801947226306,
          "actual": 0.49,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-09-01",
          "pred": 0.7684103832336263,
          "actual": 0.68,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2009-12-01",
          "pred": 1.8614821675935793,
          "actual": 1.81,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-03-01",
          "pred": 0.6357481595842402,
          "actual": 1.07,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-06-01",
          "pred": -0.2814282870581649,
          "actual": -0.62,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-09-01",
          "pred": -0.03242993796067384,
          "actual": -1.56,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2010-12-01",
          "pred": -1.1982222396069067,
          "actual": -1.63,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-03-01",
          "pred": -0.5829092162704043,
          "actual": -0.98,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-06-01",
          "pred": -0.9160167488815127,
          "actual": -0.25,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-09-01",
          "pred": -1.5863901409870942,
          "actual": -0.76,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2011-12-01",
          "pred": -0.8305874735022377,
          "actual": -1.05,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-03-01",
          "pred": -1.2778430244006411,
          "actual": -0.48,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-06-01",
          "pred": -0.7490028170673245,
          "actual": 0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-09-01",
          "pred": 1.264169200119228,
          "actual": 0.44,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2012-12-01",
          "pred": 0.9107367948746532,
          "actual": -0.13,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-03-01",
          "pred": -0.5322949922635822,
          "actual": -0.14,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-06-01",
          "pred": -1.2053592366577182,
          "actual": -0.33,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-09-01",
          "pred": -0.7494345608634607,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2013-12-01",
          "pred": -0.2948194976807427,
          "actual": -0.09,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-03-01",
          "pred": -0.15690065794562208,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-06-01",
          "pred": 0.17631220346004972,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-09-01",
          "pred": 1.1005120132651594,
          "actual": 0.37,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2014-12-01",
          "pred": 0.8105862385573787,
          "actual": 0.77,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-03-01",
          "pred": 0.9919011268474727,
          "actual": 0.48,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-06-01",
          "pred": 0.8097484788674614,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-09-01",
          "pred": 0.1628615963893246,
          "actual": 2.01,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2015-12-01",
          "pred": 2.0669326061020246,
          "actual": 2.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-03-01",
          "pred": 2.5751004732458638,
          "actual": 1.6,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-06-01",
          "pred": 1.7555795215719232,
          "actual": 0.06,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-09-01",
          "pred": 0.8174764335888894,
          "actual": -0.46,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2016-12-01",
          "pred": -1.5606058117112525,
          "actual": -0.51,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-03-01",
          "pred": 0.15189718551903758,
          "actual": -0.09,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-06-01",
          "pred": -0.26022863765624754,
          "actual": 0.22,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-09-01",
          "pred": -0.335828482034289,
          "actual": -0.56,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2017-12-01",
          "pred": -0.7130172830683105,
          "actual": -0.85,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-03-01",
          "pred": -1.0358291683483598,
          "actual": -0.73,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-06-01",
          "pred": 0.6899006653700579,
          "actual": 0.12,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-09-01",
          "pred": 0.4335648470380302,
          "actual": 0.3,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2018-12-01",
          "pred": 0.6584338121041196,
          "actual": 0.97,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-03-01",
          "pred": 0.2689357019662506,
          "actual": 0.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-06-01",
          "pred": -0.6663315017125913,
          "actual": 0.66,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-09-01",
          "pred": -0.3448166159633459,
          "actual": 0.11,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2019-12-01",
          "pred": 0.3109032695801742,
          "actual": 0.51,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-03-01",
          "pred": 0.4031780044225787,
          "actual": 0.36,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-06-01",
          "pred": 1.144585749615925,
          "actual": -0.21,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-09-01",
          "pred": 0.01538198294295753,
          "actual": -0.66,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2020-12-01",
          "pred": -0.38354435198188586,
          "actual": -0.98,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-03-01",
          "pred": -0.9246375015204706,
          "actual": -0.72,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-06-01",
          "pred": -0.14761742889846358,
          "actual": -0.06,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-09-01",
          "pred": -0.8687252467380865,
          "actual": -0.5,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2021-12-01",
          "pred": 0.3437574089798876,
          "actual": -1.07,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-03-01",
          "pred": -0.31548703938709505,
          "actual": -0.84,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-06-01",
          "pred": -0.7064219224362412,
          "actual": -0.77,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-09-01",
          "pred": -0.4361095583739548,
          "actual": -1.06,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2022-12-01",
          "pred": -0.8192126194248749,
          "actual": -0.86,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-03-01",
          "pred": -1.3518441455505772,
          "actual": -0.13,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-06-01",
          "pred": -0.8273131312953131,
          "actual": 0.95,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-09-01",
          "pred": 0.2905379141407779,
          "actual": 1.65,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2023-12-01",
          "pred": 1.6405192650449398,
          "actual": 1.81,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-03-01",
          "pred": 2.000712895983869,
          "actual": 1.1,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-06-01",
          "pred": 1.5835883883915913,
          "actual": 0.25,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-09-01",
          "pred": 0.4315648252136191,
          "actual": -0.11,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2024-12-01",
          "pred": 0.3109304802636026,
          "actual": -0.58,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-03-01",
          "pred": 1.2791558366867641,
          "actual": 0.05,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-06-01",
          "pred": 0.4795429554077187,
          "actual": 0.01,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-09-01",
          "pred": -0.4178609152845535,
          "actual": -0.3,
          "persistence": 0.01
        },
        {
          "origin": "2025-09-01",
          "date": "2025-12-01",
          "pred": -0.7668631584167719,
          "actual": -0.49,
          "persistence": -0.3
        }
      ],
      "6": [
        {
          "origin": "2006-09-01",
          "date": "2007-03-01",
          "pred": 0.4422004442961418,
          "actual": -0.15,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-06-01",
          "pred": 0.6272346713592093,
          "actual": -0.16,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2007-09-01",
          "pred": 0.9066298551676386,
          "actual": -1.04,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2007-12-01",
          "pred": 0.8371459289923047,
          "actual": -1.61,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-03-01",
          "pred": 0.9896746918827708,
          "actual": -1.17,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-06-01",
          "pred": -0.2689980242357046,
          "actual": -0.44,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2008-09-01",
          "pred": -1.0786009892724555,
          "actual": -0.28,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2008-12-01",
          "pred": -1.4482198632430445,
          "actual": -0.9,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-03-01",
          "pred": -0.8808354531697943,
          "actual": -0.72,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-06-01",
          "pred": -0.8617967965434463,
          "actual": 0.49,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2009-09-01",
          "pred": 0.07980938295166723,
          "actual": 0.68,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2009-12-01",
          "pred": 1.8223740502051666,
          "actual": 1.81,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-03-01",
          "pred": 0.6164016021697418,
          "actual": 1.07,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-06-01",
          "pred": -1.0796709221357257,
          "actual": -0.62,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2010-09-01",
          "pred": -0.31128156908614,
          "actual": -1.56,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2010-12-01",
          "pred": 0.2558827865375956,
          "actual": -1.63,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-03-01",
          "pred": 0.03950631651589799,
          "actual": -0.98,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-06-01",
          "pred": 0.7688720119057416,
          "actual": -0.25,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2011-09-01",
          "pred": -1.2717399194636303,
          "actual": -0.76,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2011-12-01",
          "pred": -1.767606255212137,
          "actual": -1.05,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-03-01",
          "pred": -1.53958281780291,
          "actual": -0.48,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-06-01",
          "pred": -1.061427276562146,
          "actual": 0.14,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2012-09-01",
          "pred": 0.8674249185602838,
          "actual": 0.44,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2012-12-01",
          "pred": 1.876927078530539,
          "actual": -0.13,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-03-01",
          "pred": 0.2620046354755822,
          "actual": -0.14,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-06-01",
          "pred": -1.2125010121028175,
          "actual": -0.33,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2013-09-01",
          "pred": -1.1552688534500803,
          "actual": -0.09,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2013-12-01",
          "pred": -0.3987715035690202,
          "actual": -0.09,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-03-01",
          "pred": -0.1845303905020519,
          "actual": -0.07,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-06-01",
          "pred": -0.49538066404252157,
          "actual": 0.48,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2014-09-01",
          "pred": 0.5354842158979245,
          "actual": 0.37,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2014-12-01",
          "pred": 1.4288063831342548,
          "actual": 0.77,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-03-01",
          "pred": 0.9264229369513812,
          "actual": 0.48,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-06-01",
          "pred": 1.1783432638694034,
          "actual": 1.28,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2015-09-01",
          "pred": 1.6590165064077005,
          "actual": 2.01,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2015-12-01",
          "pred": 0.847739505499195,
          "actual": 2.56,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-03-01",
          "pred": 2.098659365737673,
          "actual": 1.6,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-06-01",
          "pred": 2.0568147825859926,
          "actual": 0.06,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2016-09-01",
          "pred": 0.969761875100562,
          "actual": -0.46,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2016-12-01",
          "pred": 0.6478486949366181,
          "actual": -0.51,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-03-01",
          "pred": 0.01111023866385793,
          "actual": -0.09,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-06-01",
          "pred": 1.302101242960179,
          "actual": 0.22,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2017-09-01",
          "pred": -0.7843923535505183,
          "actual": -0.56,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2017-12-01",
          "pred": -1.0457226448464694,
          "actual": -0.85,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-03-01",
          "pred": -0.4976313597160151,
          "actual": -0.73,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-06-01",
          "pred": 0.07629666351675049,
          "actual": 0.12,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2018-09-01",
          "pred": 1.546933758238573,
          "actual": 0.3,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2018-12-01",
          "pred": 0.6381398554501642,
          "actual": 0.97,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-03-01",
          "pred": -0.17419224016688664,
          "actual": 0.81,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-06-01",
          "pred": -0.8246511776288948,
          "actual": 0.66,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2019-09-01",
          "pred": -0.9804331054967761,
          "actual": 0.11,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2019-12-01",
          "pred": -0.3490530782675847,
          "actual": 0.51,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-03-01",
          "pred": 0.336679187503429,
          "actual": 0.36,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-06-01",
          "pred": 0.7051633996895905,
          "actual": -0.21,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2020-09-01",
          "pred": 1.0797679693356668,
          "actual": -0.66,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2020-12-01",
          "pred": -0.1256147513851615,
          "actual": -0.98,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-03-01",
          "pred": 0.00679487153919163,
          "actual": -0.72,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-06-01",
          "pred": -0.42849648767559306,
          "actual": -0.06,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2021-09-01",
          "pred": -0.05065058775891462,
          "actual": -0.5,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2021-12-01",
          "pred": -0.7117707253327509,
          "actual": -1.07,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-03-01",
          "pred": -0.4583930241667716,
          "actual": -0.84,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-06-01",
          "pred": -0.4893920497602174,
          "actual": -0.77,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2022-09-01",
          "pred": 0.13630917433606454,
          "actual": -1.06,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2022-12-01",
          "pred": -0.43694562341379073,
          "actual": -0.86,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-03-01",
          "pred": -0.8763574763248733,
          "actual": -0.13,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-06-01",
          "pred": -1.8826883213003713,
          "actual": 0.95,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2023-09-01",
          "pred": -0.8219645573034196,
          "actual": 1.65,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2023-12-01",
          "pred": 0.4675252299711273,
          "actual": 1.81,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-03-01",
          "pred": 1.515815887225983,
          "actual": 1.1,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-06-01",
          "pred": 1.716272283121835,
          "actual": 0.25,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2024-09-01",
          "pred": 1.8966231359861783,
          "actual": -0.11,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2024-12-01",
          "pred": 0.6661028940447792,
          "actual": -0.58,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-03-01",
          "pred": 1.5958014648205268,
          "actual": 0.05,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-06-01",
          "pred": 1.758798302358777,
          "actual": 0.01,
          "persistence": -0.58
        },
        {
          "origin": "2025-03-01",
          "date": "2025-09-01",
          "pred": -0.5804132894066474,
          "actual": -0.3,
          "persistence": 0.05
        },
        {
          "origin": "2025-06-01",
          "date": "2025-12-01",
          "pred": -1.0145164675278997,
          "actual": -0.49,
          "persistence": 0.01
        }
      ],
      "12": [
        {
          "origin": "2006-09-01",
          "date": "2007-09-01",
          "pred": 1.493823559664131,
          "actual": -1.04,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2007-12-01",
          "pred": 2.104108387053783,
          "actual": -1.61,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2008-03-01",
          "pred": 1.3910870020735038,
          "actual": -1.17,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2008-06-01",
          "pred": -0.10771729450212325,
          "actual": -0.44,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2008-09-01",
          "pred": -0.5202578906028452,
          "actual": -0.28,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2008-12-01",
          "pred": -0.5100035233639189,
          "actual": -0.9,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2009-03-01",
          "pred": -0.7426984196026486,
          "actual": -0.72,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2009-06-01",
          "pred": -1.5288711653332938,
          "actual": 0.49,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2009-09-01",
          "pred": -0.3933740439837815,
          "actual": 0.68,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2009-12-01",
          "pred": 1.1933021021412937,
          "actual": 1.81,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2010-03-01",
          "pred": -0.6229765823010908,
          "actual": 1.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2010-06-01",
          "pred": -0.9983133736506531,
          "actual": -0.62,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2010-09-01",
          "pred": -1.0931469902861672,
          "actual": -1.56,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2010-12-01",
          "pred": 0.603553874856112,
          "actual": -1.63,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2011-03-01",
          "pred": 0.8186847843735229,
          "actual": -0.98,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2011-06-01",
          "pred": 0.35678845612534765,
          "actual": -0.25,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2011-09-01",
          "pred": 0.16509583378573142,
          "actual": -0.76,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2011-12-01",
          "pred": -0.2836366794355182,
          "actual": -1.05,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2012-03-01",
          "pred": -0.8084978495485025,
          "actual": -0.48,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2012-06-01",
          "pred": -0.5464882487667891,
          "actual": 0.14,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2012-09-01",
          "pred": 0.7304001743808768,
          "actual": 0.44,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2012-12-01",
          "pred": 1.0513102017510119,
          "actual": -0.13,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2013-03-01",
          "pred": -0.28436062864359274,
          "actual": -0.14,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2013-06-01",
          "pred": -1.688908111935813,
          "actual": -0.33,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2013-09-01",
          "pred": -1.6123400472274378,
          "actual": -0.09,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2013-12-01",
          "pred": 0.023769595269094376,
          "actual": -0.09,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2014-03-01",
          "pred": -0.7299315510684148,
          "actual": -0.07,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2014-06-01",
          "pred": -0.8825290456828475,
          "actual": 0.48,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2014-09-01",
          "pred": 0.12900673141854324,
          "actual": 0.37,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2014-12-01",
          "pred": 0.7130428661499547,
          "actual": 0.77,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2015-03-01",
          "pred": 1.9570940628641265,
          "actual": 0.48,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2015-06-01",
          "pred": 1.1838136385368414,
          "actual": 1.28,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2015-09-01",
          "pred": 1.813191280264116,
          "actual": 2.01,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2015-12-01",
          "pred": 1.6225132442192023,
          "actual": 2.56,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2016-03-01",
          "pred": 1.5872722045025032,
          "actual": 1.6,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2016-06-01",
          "pred": -0.5240736186876123,
          "actual": 0.06,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2016-09-01",
          "pred": 1.037322002293201,
          "actual": -0.46,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2016-12-01",
          "pred": 1.6864557499024122,
          "actual": -0.51,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2017-03-01",
          "pred": 1.4503882109062345,
          "actual": -0.09,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2017-06-01",
          "pred": 0.49249450707544323,
          "actual": 0.22,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2017-09-01",
          "pred": -0.3985196339086819,
          "actual": -0.56,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2017-12-01",
          "pred": -0.06590150444963566,
          "actual": -0.85,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2018-03-01",
          "pred": 0.09955986763863141,
          "actual": -0.73,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2018-06-01",
          "pred": 0.9204654142686893,
          "actual": 0.12,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2018-09-01",
          "pred": 2.099388068766684,
          "actual": 0.3,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2018-12-01",
          "pred": 0.8168184552834509,
          "actual": 0.97,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2019-03-01",
          "pred": -1.2007629403271838,
          "actual": 0.81,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2019-06-01",
          "pred": -1.9420049312639955,
          "actual": 0.66,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2019-09-01",
          "pred": -1.9025242050623528,
          "actual": 0.11,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2019-12-01",
          "pred": 0.24163557285424453,
          "actual": 0.51,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2020-03-01",
          "pred": 0.01566662656213391,
          "actual": 0.36,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2020-06-01",
          "pred": -0.11549109866195026,
          "actual": -0.21,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2020-09-01",
          "pred": -0.3421420903155213,
          "actual": -0.66,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2020-12-01",
          "pred": -0.013358502386157644,
          "actual": -0.98,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2021-03-01",
          "pred": 1.0610310975139259,
          "actual": -0.72,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2021-06-01",
          "pred": 1.465211713830259,
          "actual": -0.06,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2021-09-01",
          "pred": 1.3206969155162267,
          "actual": -0.5,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2021-12-01",
          "pred": 0.4019423221122999,
          "actual": -1.07,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2022-03-01",
          "pred": -0.14486117085483025,
          "actual": -0.84,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2022-06-01",
          "pred": 0.12029382794447435,
          "actual": -0.77,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2022-09-01",
          "pred": 0.24324126968054904,
          "actual": -1.06,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2022-12-01",
          "pred": 0.32071890517574614,
          "actual": -0.86,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2023-03-01",
          "pred": -1.054362405853252,
          "actual": -0.13,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2023-06-01",
          "pred": -2.331219341005776,
          "actual": 0.95,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2023-09-01",
          "pred": -1.9676334091069323,
          "actual": 1.65,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2023-12-01",
          "pred": 0.05569043940429876,
          "actual": 1.81,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2024-03-01",
          "pred": -0.4692042313272241,
          "actual": 1.1,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2024-06-01",
          "pred": 0.6254502439023931,
          "actual": 0.25,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2024-09-01",
          "pred": 1.8189045170068106,
          "actual": -0.11,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2024-12-01",
          "pred": 2.0132857322790145,
          "actual": -0.58,
          "persistence": 1.81
        },
        {
          "origin": "2024-03-01",
          "date": "2025-03-01",
          "pred": 0.7473839675837347,
          "actual": 0.05,
          "persistence": 1.1
        },
        {
          "origin": "2024-06-01",
          "date": "2025-06-01",
          "pred": 0.415916927527941,
          "actual": 0.01,
          "persistence": 0.25
        },
        {
          "origin": "2024-09-01",
          "date": "2025-09-01",
          "pred": 1.2585316221274576,
          "actual": -0.3,
          "persistence": -0.11
        },
        {
          "origin": "2024-12-01",
          "date": "2025-12-01",
          "pred": 0.9217523109749823,
          "actual": -0.49,
          "persistence": -0.58
        }
      ],
      "24": [
        {
          "origin": "2006-09-01",
          "date": "2008-09-01",
          "pred": 0.12975917090958267,
          "actual": -0.28,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2008-12-01",
          "pred": 0.0063880162414540025,
          "actual": -0.9,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2009-03-01",
          "pred": 1.5052183972481203,
          "actual": -0.72,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2009-06-01",
          "pred": 1.8371278327254377,
          "actual": 0.49,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2009-09-01",
          "pred": 1.5718357464358284,
          "actual": 0.68,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2009-12-01",
          "pred": 0.005766304305640396,
          "actual": 1.81,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2010-03-01",
          "pred": -0.6805864483938534,
          "actual": 1.07,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2010-06-01",
          "pred": -1.410008659436367,
          "actual": -0.62,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2010-09-01",
          "pred": -2.6667084794836944,
          "actual": -1.56,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2010-12-01",
          "pred": -1.7491514697570159,
          "actual": -1.63,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2011-03-01",
          "pred": 0.759946751322199,
          "actual": -0.98,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2011-06-01",
          "pred": 1.136179592229091,
          "actual": -0.25,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2011-09-01",
          "pred": -0.205798777455309,
          "actual": -0.76,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2011-12-01",
          "pred": 0.6791110720748458,
          "actual": -1.05,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2012-03-01",
          "pred": 0.8681392878904997,
          "actual": -0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2012-06-01",
          "pred": 1.9642774101897043,
          "actual": 0.14,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2012-09-01",
          "pred": 1.8487379492668519,
          "actual": 0.44,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2012-12-01",
          "pred": 0.4800831500596829,
          "actual": -0.13,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2013-03-01",
          "pred": -1.7031101397238964,
          "actual": -0.14,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2013-06-01",
          "pred": -2.023331047419524,
          "actual": -0.33,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2013-09-01",
          "pred": -2.259552471992634,
          "actual": -0.09,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2013-12-01",
          "pred": -1.2980326613486466,
          "actual": -0.09,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2014-03-01",
          "pred": 0.6469291491820769,
          "actual": -0.07,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2014-06-01",
          "pred": -0.4460167995643269,
          "actual": 0.48,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2014-09-01",
          "pred": 0.29862242522265786,
          "actual": 0.37,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2014-12-01",
          "pred": 0.5820297970200955,
          "actual": 0.77,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2015-03-01",
          "pred": 1.7794753995613861,
          "actual": 0.48,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2015-06-01",
          "pred": 1.9563341852983676,
          "actual": 1.28,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2015-09-01",
          "pred": 1.5046879158675928,
          "actual": 2.01,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2015-12-01",
          "pred": 0.5725758133645734,
          "actual": 2.56,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2016-03-01",
          "pred": -0.47942998696607914,
          "actual": 1.6,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2016-06-01",
          "pred": -0.17155715238452382,
          "actual": 0.06,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2016-09-01",
          "pred": -0.6906269697394967,
          "actual": -0.46,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2016-12-01",
          "pred": -0.30739738723786414,
          "actual": -0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2017-03-01",
          "pred": -0.27366055762079816,
          "actual": -0.09,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2017-06-01",
          "pred": 2.359516604250018,
          "actual": 0.22,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2017-09-01",
          "pred": 0.16920759604698551,
          "actual": -0.56,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2017-12-01",
          "pred": 0.12993585404884006,
          "actual": -0.85,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2018-03-01",
          "pred": 1.1950352630847065,
          "actual": -0.73,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2018-06-01",
          "pred": 1.7553526663109373,
          "actual": 0.12,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2018-09-01",
          "pred": 1.3676053720253523,
          "actual": 0.3,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2018-12-01",
          "pred": 1.084867556676485,
          "actual": 0.97,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2019-03-01",
          "pred": -1.017372072839232,
          "actual": 0.81,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2019-06-01",
          "pred": -1.3207343250574948,
          "actual": 0.66,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2019-09-01",
          "pred": -1.2610171577544738,
          "actual": 0.11,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2019-12-01",
          "pred": -0.33972668684321894,
          "actual": 0.51,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2020-03-01",
          "pred": 0.1444271036646654,
          "actual": 0.36,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2020-06-01",
          "pred": -1.6319368678403299,
          "actual": -0.21,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2020-09-01",
          "pred": -0.7578099858452214,
          "actual": -0.66,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2020-12-01",
          "pred": -0.6263615400131741,
          "actual": -0.98,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2021-03-01",
          "pred": 0.7877176942089205,
          "actual": -0.72,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2021-06-01",
          "pred": 1.3675254475760412,
          "actual": -0.06,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2021-09-01",
          "pred": 1.338270396525838,
          "actual": -0.5,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2021-12-01",
          "pred": 1.427833027911063,
          "actual": -1.07,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2022-03-01",
          "pred": 0.16272942447865388,
          "actual": -0.84,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2022-06-01",
          "pred": 0.26259210447579034,
          "actual": -0.77,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2022-09-01",
          "pred": 0.39466077161150925,
          "actual": -1.06,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2022-12-01",
          "pred": 0.17571581916686552,
          "actual": -0.86,
          "persistence": -0.98
        },
        {
          "origin": "2021-03-01",
          "date": "2023-03-01",
          "pred": 0.05198890628756683,
          "actual": -0.13,
          "persistence": -0.72
        },
        {
          "origin": "2021-06-01",
          "date": "2023-06-01",
          "pred": -1.132992669281231,
          "actual": 0.95,
          "persistence": -0.06
        },
        {
          "origin": "2021-09-01",
          "date": "2023-09-01",
          "pred": -1.5781418727051935,
          "actual": 1.65,
          "persistence": -0.5
        },
        {
          "origin": "2021-12-01",
          "date": "2023-12-01",
          "pred": -0.6584721670989861,
          "actual": 1.81,
          "persistence": -1.07
        },
        {
          "origin": "2022-03-01",
          "date": "2024-03-01",
          "pred": 0.17166376556851237,
          "actual": 1.1,
          "persistence": -0.84
        },
        {
          "origin": "2022-06-01",
          "date": "2024-06-01",
          "pred": 0.3441102286026153,
          "actual": 0.25,
          "persistence": -0.77
        },
        {
          "origin": "2022-09-01",
          "date": "2024-09-01",
          "pred": 0.7689132103820444,
          "actual": -0.11,
          "persistence": -1.06
        },
        {
          "origin": "2022-12-01",
          "date": "2024-12-01",
          "pred": 1.1580452997902904,
          "actual": -0.58,
          "persistence": -0.86
        },
        {
          "origin": "2023-03-01",
          "date": "2025-03-01",
          "pred": 1.6310560885061527,
          "actual": 0.05,
          "persistence": -0.13
        },
        {
          "origin": "2023-06-01",
          "date": "2025-06-01",
          "pred": -0.45625225432083977,
          "actual": 0.01,
          "persistence": 0.95
        },
        {
          "origin": "2023-09-01",
          "date": "2025-09-01",
          "pred": -0.3454956481654794,
          "actual": -0.3,
          "persistence": 1.65
        },
        {
          "origin": "2023-12-01",
          "date": "2025-12-01",
          "pred": 1.1116954834764508,
          "actual": -0.49,
          "persistence": 1.81
        }
      ],
      "60": [
        {
          "origin": "2006-09-01",
          "date": "2011-09-01",
          "pred": -0.6543351794577947,
          "actual": -0.76,
          "persistence": 0.62
        },
        {
          "origin": "2006-12-01",
          "date": "2011-12-01",
          "pred": 0.2831920412110664,
          "actual": -1.05,
          "persistence": 1.1
        },
        {
          "origin": "2007-03-01",
          "date": "2012-03-01",
          "pred": 1.2996819822328889,
          "actual": -0.48,
          "persistence": -0.15
        },
        {
          "origin": "2007-06-01",
          "date": "2012-06-01",
          "pred": 0.4736201947015886,
          "actual": 0.14,
          "persistence": -0.16
        },
        {
          "origin": "2007-09-01",
          "date": "2012-09-01",
          "pred": 0.20308771163645334,
          "actual": 0.44,
          "persistence": -1.04
        },
        {
          "origin": "2007-12-01",
          "date": "2012-12-01",
          "pred": -0.15299855541756624,
          "actual": -0.13,
          "persistence": -1.61
        },
        {
          "origin": "2008-03-01",
          "date": "2013-03-01",
          "pred": -0.6945161549497708,
          "actual": -0.14,
          "persistence": -1.17
        },
        {
          "origin": "2008-06-01",
          "date": "2013-06-01",
          "pred": -1.4056399828265218,
          "actual": -0.33,
          "persistence": -0.44
        },
        {
          "origin": "2008-09-01",
          "date": "2013-09-01",
          "pred": -0.05386244633373076,
          "actual": -0.09,
          "persistence": -0.28
        },
        {
          "origin": "2008-12-01",
          "date": "2013-12-01",
          "pred": 1.9818978043304696,
          "actual": -0.09,
          "persistence": -0.9
        },
        {
          "origin": "2009-03-01",
          "date": "2014-03-01",
          "pred": 0.9064437811197625,
          "actual": -0.07,
          "persistence": -0.72
        },
        {
          "origin": "2009-06-01",
          "date": "2014-06-01",
          "pred": 0.318133179460612,
          "actual": 0.48,
          "persistence": 0.49
        },
        {
          "origin": "2009-09-01",
          "date": "2014-09-01",
          "pred": 1.158766464756174,
          "actual": 0.37,
          "persistence": 0.68
        },
        {
          "origin": "2009-12-01",
          "date": "2014-12-01",
          "pred": 2.5047329584778546,
          "actual": 0.77,
          "persistence": 1.81
        },
        {
          "origin": "2010-03-01",
          "date": "2015-03-01",
          "pred": 2.813192283564575,
          "actual": 0.48,
          "persistence": 1.07
        },
        {
          "origin": "2010-06-01",
          "date": "2015-06-01",
          "pred": 1.9313127004756094,
          "actual": 1.28,
          "persistence": -0.62
        },
        {
          "origin": "2010-09-01",
          "date": "2015-09-01",
          "pred": 0.07788594953524451,
          "actual": 2.01,
          "persistence": -1.56
        },
        {
          "origin": "2010-12-01",
          "date": "2015-12-01",
          "pred": -1.1351001519865478,
          "actual": 2.56,
          "persistence": -1.63
        },
        {
          "origin": "2011-03-01",
          "date": "2016-03-01",
          "pred": -1.5466485313304408,
          "actual": 1.6,
          "persistence": -0.98
        },
        {
          "origin": "2011-06-01",
          "date": "2016-06-01",
          "pred": -1.4259670830423579,
          "actual": 0.06,
          "persistence": -0.25
        },
        {
          "origin": "2011-09-01",
          "date": "2016-09-01",
          "pred": -0.8802641027600452,
          "actual": -0.46,
          "persistence": -0.76
        },
        {
          "origin": "2011-12-01",
          "date": "2016-12-01",
          "pred": 0.6362291087426374,
          "actual": -0.51,
          "persistence": -1.05
        },
        {
          "origin": "2012-03-01",
          "date": "2017-03-01",
          "pred": -0.3774408881385707,
          "actual": -0.09,
          "persistence": -0.48
        },
        {
          "origin": "2012-06-01",
          "date": "2017-06-01",
          "pred": -1.6211737788930336,
          "actual": 0.22,
          "persistence": 0.14
        },
        {
          "origin": "2012-09-01",
          "date": "2017-09-01",
          "pred": 0.607101798706521,
          "actual": -0.56,
          "persistence": 0.44
        },
        {
          "origin": "2012-12-01",
          "date": "2017-12-01",
          "pred": 2.363969667860226,
          "actual": -0.85,
          "persistence": -0.13
        },
        {
          "origin": "2013-03-01",
          "date": "2018-03-01",
          "pred": 0.7627765923288152,
          "actual": -0.73,
          "persistence": -0.14
        },
        {
          "origin": "2013-06-01",
          "date": "2018-06-01",
          "pred": -0.2498395357861773,
          "actual": 0.12,
          "persistence": -0.33
        },
        {
          "origin": "2013-09-01",
          "date": "2018-09-01",
          "pred": 0.017547192341512585,
          "actual": 0.3,
          "persistence": -0.09
        },
        {
          "origin": "2013-12-01",
          "date": "2018-12-01",
          "pred": -0.1749585173535414,
          "actual": 0.97,
          "persistence": -0.09
        },
        {
          "origin": "2014-03-01",
          "date": "2019-03-01",
          "pred": -0.5451752305236626,
          "actual": 0.81,
          "persistence": -0.07
        },
        {
          "origin": "2014-06-01",
          "date": "2019-06-01",
          "pred": -1.1147096608128888,
          "actual": 0.66,
          "persistence": 0.48
        },
        {
          "origin": "2014-09-01",
          "date": "2019-09-01",
          "pred": 0.4469657885864368,
          "actual": 0.11,
          "persistence": 0.37
        },
        {
          "origin": "2014-12-01",
          "date": "2019-12-01",
          "pred": 0.1026264857452333,
          "actual": 0.51,
          "persistence": 0.77
        },
        {
          "origin": "2015-03-01",
          "date": "2020-03-01",
          "pred": 0.5039853245872816,
          "actual": 0.36,
          "persistence": 0.48
        },
        {
          "origin": "2015-06-01",
          "date": "2020-06-01",
          "pred": 0.35778481512137306,
          "actual": -0.21,
          "persistence": 1.28
        },
        {
          "origin": "2015-09-01",
          "date": "2020-09-01",
          "pred": -0.40602030206637085,
          "actual": -0.66,
          "persistence": 2.01
        },
        {
          "origin": "2015-12-01",
          "date": "2020-12-01",
          "pred": 0.3938932415047388,
          "actual": -0.98,
          "persistence": 2.56
        },
        {
          "origin": "2016-03-01",
          "date": "2021-03-01",
          "pred": 1.6291310213633827,
          "actual": -0.72,
          "persistence": 1.6
        },
        {
          "origin": "2016-06-01",
          "date": "2021-06-01",
          "pred": 0.48455073630650614,
          "actual": -0.06,
          "persistence": 0.06
        },
        {
          "origin": "2016-09-01",
          "date": "2021-09-01",
          "pred": -1.4431888789528255,
          "actual": -0.5,
          "persistence": -0.46
        },
        {
          "origin": "2016-12-01",
          "date": "2021-12-01",
          "pred": -1.75273513091387,
          "actual": -1.07,
          "persistence": -0.51
        },
        {
          "origin": "2017-03-01",
          "date": "2022-03-01",
          "pred": -2.0738148529098717,
          "actual": -0.84,
          "persistence": -0.09
        },
        {
          "origin": "2017-06-01",
          "date": "2022-06-01",
          "pred": -1.710465161055338,
          "actual": -0.77,
          "persistence": 0.22
        },
        {
          "origin": "2017-09-01",
          "date": "2022-09-01",
          "pred": -0.4431326020111692,
          "actual": -1.06,
          "persistence": -0.56
        },
        {
          "origin": "2017-12-01",
          "date": "2022-12-01",
          "pred": -0.64654498603791,
          "actual": -0.86,
          "persistence": -0.85
        },
        {
          "origin": "2018-03-01",
          "date": "2023-03-01",
          "pred": -1.8545625891510298,
          "actual": -0.13,
          "persistence": -0.73
        },
        {
          "origin": "2018-06-01",
          "date": "2023-06-01",
          "pred": -2.217497500318665,
          "actual": 0.95,
          "persistence": 0.12
        },
        {
          "origin": "2018-09-01",
          "date": "2023-09-01",
          "pred": -0.7297495270540244,
          "actual": 1.65,
          "persistence": 0.3
        },
        {
          "origin": "2018-12-01",
          "date": "2023-12-01",
          "pred": 0.34254014263097976,
          "actual": 1.81,
          "persistence": 0.97
        },
        {
          "origin": "2019-03-01",
          "date": "2024-03-01",
          "pred": 1.93362243295689,
          "actual": 1.1,
          "persistence": 0.81
        },
        {
          "origin": "2019-06-01",
          "date": "2024-06-01",
          "pred": 1.9231082591071549,
          "actual": 0.25,
          "persistence": 0.66
        },
        {
          "origin": "2019-09-01",
          "date": "2024-09-01",
          "pred": 1.3313298042020998,
          "actual": -0.11,
          "persistence": 0.11
        },
        {
          "origin": "2019-12-01",
          "date": "2024-12-01",
          "pred": 0.86335542760748,
          "actual": -0.58,
          "persistence": 0.51
        },
        {
          "origin": "2020-03-01",
          "date": "2025-03-01",
          "pred": 0.7949386756108527,
          "actual": 0.05,
          "persistence": 0.36
        },
        {
          "origin": "2020-06-01",
          "date": "2025-06-01",
          "pred": 1.4892716773193442,
          "actual": 0.01,
          "persistence": -0.21
        },
        {
          "origin": "2020-09-01",
          "date": "2025-09-01",
          "pred": 1.006792374647867,
          "actual": -0.3,
          "persistence": -0.66
        },
        {
          "origin": "2020-12-01",
          "date": "2025-12-01",
          "pred": 0.9324915385648298,
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
  "elapsed_seconds": 88.818
};
