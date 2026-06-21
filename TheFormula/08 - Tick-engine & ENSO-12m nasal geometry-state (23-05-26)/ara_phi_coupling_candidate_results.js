window.ARA_PHI_COUPLING_RESULTS = {
  "description": "Phi-coupling candidate tests: solar hemispheres, heart/respiration, tides.",
  "phi": 1.618033988749895,
  "leakage_summary": [
    "Data are cached before analysis; cache contents are not used for fitting decisions.",
    "Thresholds/lags/models are fitted on train windows only.",
    "All reported model metrics are held-out later windows.",
    "Event rules use thresholds chosen on train only."
  ],
  "tests": {
    "solar_north_south": {
      "name": "solar_north_south",
      "status": "ok",
      "source": {
        "north_col": 4,
        "south_col": 5,
        "source": "SILSO extended monthly hemispheric Catalogue B",
        "source_path": "F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\TheFormula\\data_cache\\Catalogue_B.txt",
        "source_kind": "cache"
      },
      "n_months": 1758,
      "date_range": [
        "1874-05",
        "2020-10"
      ],
      "horizon_months": 24,
      "leakage_guard": "Thresholds/model trained on first 60% of valid windows; evaluated only on later windows.",
      "cycles": {
        "north": [
          {
            "start": 55,
            "peak": 89,
            "end": 181,
            "ara": 2.7058823529411766
          },
          {
            "start": 181,
            "peak": 246,
            "end": 328,
            "ara": 1.2615384615384615
          },
          {
            "start": 328,
            "peak": 380,
            "end": 459,
            "ara": 1.5192307692307692
          },
          {
            "start": 459,
            "peak": 520,
            "end": 588,
            "ara": 1.1147540983606556
          },
          {
            "start": 588,
            "peak": 651,
            "end": 716,
            "ara": 1.0317460317460319
          },
          {
            "start": 716,
            "peak": 758,
            "end": 841,
            "ara": 1.9761904761904763
          },
          {
            "start": 841,
            "peak": 903,
            "end": 959,
            "ara": 0.9032258064516129
          },
          {
            "start": 959,
            "peak": 1018,
            "end": 1084,
            "ara": 1.11864406779661
          },
          {
            "start": 1084,
            "peak": 1135,
            "end": 1225,
            "ara": 1.7647058823529411
          },
          {
            "start": 1225,
            "peak": 1264,
            "end": 1339,
            "ara": 1.9230769230769231
          },
          {
            "start": 1339,
            "peak": 1382,
            "end": 1467,
            "ara": 1.9767441860465116
          },
          {
            "start": 1467,
            "peak": 1517,
            "end": 1605,
            "ara": 1.76
          }
        ],
        "south": [
          {
            "start": 53,
            "peak": 114,
            "end": 191,
            "ara": 1.2622950819672132
          },
          {
            "start": 191,
            "peak": 231,
            "end": 329,
            "ara": 2.45
          },
          {
            "start": 329,
            "peak": 397,
            "end": 471,
            "ara": 1.088235294117647
          },
          {
            "start": 471,
            "peak": 521,
            "end": 589,
            "ara": 1.36
          },
          {
            "start": 589,
            "peak": 642,
            "end": 708,
            "ara": 1.2452830188679245
          },
          {
            "start": 708,
            "peak": 771,
            "end": 833,
            "ara": 0.9841269841269841
          },
          {
            "start": 833,
            "peak": 878,
            "end": 960,
            "ara": 1.8222222222222222
          },
          {
            "start": 960,
            "peak": 998,
            "end": 1087,
            "ara": 2.3421052631578947
          },
          {
            "start": 1087,
            "peak": 1147,
            "end": 1216,
            "ara": 1.15
          },
          {
            "start": 1216,
            "peak": 1271,
            "end": 1346,
            "ara": 1.3636363636363635
          },
          {
            "start": 1346,
            "peak": 1405,
            "end": 1464,
            "ara": 1.0
          },
          {
            "start": 1464,
            "peak": 1534,
            "end": 1617,
            "ara": 1.1857142857142857
          }
        ],
        "north_ara": {
          "n": 12,
          "mean": 1.5879782546443477,
          "std": 0.5048479590947906,
          "p25": 1.1176715754376214,
          "p50": 1.6396153846153845,
          "p75": 1.9363553113553114
        },
        "south_ara": {
          "n": 12,
          "mean": 1.4378015428175448,
          "std": 0.47745634350153165,
          "p25": 1.1345588235294117,
          "p50": 1.2537890504175688,
          "p75": 1.4782828282828282
        }
      },
      "heldout_model": {
        "n": 621,
        "mae": 0.3062131311716559,
        "baseline_mae": 0.3762869673751188,
        "mae_lift_vs_baseline": 0.07007383620346291,
        "corr": 0.3586017515180699
      },
      "event_rule": {
        "coupling_delta_threshold_train_q75": 0.08140017215586812,
        "phi_score_threshold_train_q50": 0.3445214908826011,
        "event_change_future_minus_current": {
          "n": 66,
          "mean": -0.05042830467963021,
          "std": 0.35809822073977465,
          "p25": -0.21385428975837645,
          "p50": -0.022645451942569672,
          "p75": 0.17354315156602224
        },
        "nonevent_change_future_minus_current": {
          "n": 555,
          "mean": 0.02634188960216338,
          "std": 0.5337931312678591,
          "p25": -0.2021769200348797,
          "p50": 0.06817081263662617,
          "p75": 0.32948656446392366
        },
        "supports_relative_damping": true,
        "supports_absolute_relaxation": true,
        "supports_relaxation": true
      },
      "speed_metrics": {
        "kind": "balance_relaxation",
        "horizon_ticks": 24.0,
        "cycle_period_ticks": 128.0,
        "time_rung_phi": 10.082940632887894,
        "event_current_metric_scale_median_abs": 0.16611747784307274,
        "signed_toward_balance_per_tick": 0.0021011793616512587,
        "signed_toward_balance_per_cycle": 0.2689509582913611,
        "fractional_toward_balance_per_cycle": 1.6190407041059987,
        "rung_density_signed": 0.026673861136711843,
        "rung_density_fractional": 0.16057227380920153,
        "relative_damping_per_tick": 0.0031987580950747327,
        "relative_damping_per_cycle": 0.4094410361695658
      },
      "sample_rows": [
        {
          "t": 985,
          "date": "1956-06",
          "current_error": 0.1204774647206704,
          "future_error": 0.13509718638014054,
          "coupling": 0.9395203336760193,
          "coupling_delta": 0.14828527997391305,
          "phi_score": 0.2568144785320326,
          "ara_n": 1.11864406779661,
          "ara_s": 2.3421052631578947
        },
        {
          "t": 986,
          "date": "1956-07",
          "current_error": 0.05245236423787578,
          "future_error": 0.1435888469037132,
          "coupling": 0.9736504490231243,
          "coupling_delta": 0.16382459388262882,
          "phi_score": 0.2568144785320326,
          "ara_n": 1.11864406779661,
          "ara_s": 2.3421052631578947
        },
        {
          "t": 987,
          "date": "1956-08",
          "current_error": 0.014815085785140474,
          "future_error": 0.16226274067694957,
          "coupling": 0.9925577013613164,
          "coupling_delta": 0.16215126474880226,
          "phi_score": 0.2568144785320326,
          "ara_n": 1.11864406779661,
          "ara_s": 2.3421052631578947
        },
        {
          "t": 988,
          "date": "1956-09",
          "current_error": 0.08062178001585146,
          "future_error": 0.19786482287634155,
          "coupling": 0.9595281306671529,
          "coupling_delta": 0.10767337440798497,
          "phi_score": 0.2568144785320326,
          "ara_n": 1.11864406779661,
          "ara_s": 2.3421052631578947
        },
        {
          "t": 989,
          "date": "1956-10",
          "current_error": 0.14247052530905757,
          "future_error": 0.25203579540030174,
          "coupling": 0.9285714285673343,
          "coupling_delta": 0.058888982661955525,
          "phi_score": 0.2568144785320326,
          "ara_n": 1.11864406779661,
          "ara_s": 2.3421052631578947
        },
        {
          "t": 990,
          "date": "1956-11",
          "current_error": 0.1975471570800152,
          "future_error": 0.3266418690409714,
          "coupling": 0.9011216565966301,
          "coupling_delta": 0.017227901167078175,
          "phi_score": 0.2568144785320326,
          "ara_n": 1.11864406779661,
          "ara_s": 2.3421052631578947
        },
        {
          "t": 991,
          "date": "1956-12",
          "current_error": 0.24199945708135037,
          "future_error": 0.42123810016899427,
          "coupling": 0.8790760869527894,
          "coupling_delta": -0.015650977258816035,
          "phi_score": 0.2568144785320326,
          "ara_n": 1.11864406779661,
          "ara_s": 2.3421052631578947
        },
        {
          "t": 992,
          "date": "1957-01",
          "current_error": 0.26773104331784436,
          "future_error": 0.5299389199993111,
          "coupling": 0.8663702709467899,
          "coupling_delta": -0.03616267560511266,
          "phi_score": 0.2568144785320326,
          "ara_n": 1.11864406779661,
          "ara_s": 2.3421052631578947
        }
      ]
    },
    "heart_respiration": {
      "name": "heart_respiration_bidmc01",
      "status": "ok",
      "source": {
        "columns": [
          "Time [s]",
          "RESP",
          "PLETH",
          "V",
          "AVR",
          "II"
        ],
        "time_col": "Time [s]",
        "ecg_col": "V",
        "resp_col": "RESP",
        "source": "PhysioNet BIDMC PPG and Respiration Dataset, record 01 signals CSV",
        "source_path": "F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\TheFormula\\data_cache\\bidmc_01_Signals.csv",
        "source_kind": "cache"
      },
      "fs_hz": 100.00000000009095,
      "duration_s": 480.0,
      "n_r_peaks": 763,
      "n_resp_cycles": 169,
      "horizon_s": 30.0,
      "leakage_guard": "Thresholds/model trained on first 60% of rolling windows; evaluated only on later windows.",
      "ara_resp": {
        "n": 169,
        "mean": 1.2987600427993553,
        "std": 0.14717390248528495,
        "p25": 1.251497005988024,
        "p50": 1.305732484076433,
        "p75": 1.3734177215189873
      },
      "ara_heart_by_breath": {
        "n": 125,
        "mean": 2.6590777503438328,
        "std": 2.7093597210684783,
        "p25": 0.7783251231527094,
        "p50": 1.9487179487179487,
        "p75": 3.4923076923076923
      },
      "heldout_model": {
        "n": 22,
        "mae": 0.16673914139123963,
        "baseline_mae": 0.1989725945617421,
        "mae_lift_vs_baseline": 0.03223345317050247,
        "corr": -0.04126524758646
      },
      "event_rule": {
        "coupling_delta_threshold_train_q75": 0.005348034118054117,
        "phi_score_threshold_train_q50": 0.4768687388803387,
        "event_change_future_minus_current": {
          "n": 9,
          "mean": 0.10032223600319971,
          "std": 0.2069610098030233,
          "p25": -0.07544736007086789,
          "p50": 0.0043764326587279745,
          "p75": 0.28622178093797407
        },
        "nonevent_change_future_minus_current": {
          "n": 13,
          "mean": 0.1277148355314716,
          "std": 0.257266239131746,
          "p25": -0.02981936833671711,
          "p50": 0.06375870256404836,
          "p75": 0.26463709556785636
        },
        "supports_relative_damping": true,
        "supports_absolute_relaxation": false,
        "supports_relaxation": false
      },
      "speed_metrics": {
        "kind": "balance_relaxation",
        "horizon_ticks": 30.0,
        "cycle_period_ticks": 3.5499999999967713,
        "time_rung_phi": 2.6328272446951804,
        "event_current_metric_scale_median_abs": 0.2404470179148524,
        "signed_toward_balance_per_tick": -0.0033440745334399904,
        "signed_toward_balance_per_cycle": -0.011871464593701168,
        "fractional_toward_balance_per_cycle": -0.04937247588533253,
        "rung_density_signed": -0.00450901767961445,
        "rung_density_fractional": -0.01875264546308989,
        "relative_damping_per_tick": 0.0009130866509423958,
        "relative_damping_per_cycle": 0.003241457610842557
      },
      "sample_rows": [
        {
          "time_s": 255.0,
          "gap": 0.051809423431266134,
          "coupling": 0.05827548718965101,
          "ara_resp": 1.3,
          "ara_heart": 1.3691275167785235,
          "phi_score": 0.5326270356520112,
          "future_gap": 0.3164465189991225,
          "coupling_delta": 0.0015617808041200124
        },
        {
          "time_s": 260.0,
          "gap": 0.26200558440625676,
          "coupling": 0.04083761473338149,
          "ara_resp": 1.3,
          "ara_heart": 1.6893939393939394,
          "phi_score": 0.6487810835521954,
          "future_gap": 0.46779081692775454,
          "coupling_delta": -0.017437872456269522
        },
        {
          "time_s": 265.0,
          "gap": 0.26084076190996386,
          "coupling": 0.0490414016651304,
          "ara_resp": 1.3015151515151515,
          "ara_heart": 1.6893939393939394,
          "phi_score": 0.6498742274952334,
          "future_gap": 0.31309178797714926,
          "coupling_delta": 0.008203786931748912
        },
        {
          "time_s": 270.0,
          "gap": 0.027656479749788524,
          "coupling": 0.059868200570055714,
          "ara_resp": 1.3,
          "ara_heart": 1.3364552114552115,
          "phi_score": 0.5136380693864323,
          "future_gap": 0.3138782606877626,
          "coupling_delta": 0.010826798904925314
        },
        {
          "time_s": 275.0,
          "gap": 0.2596772946466658,
          "coupling": 0.04441284663852545,
          "ara_resp": 1.303030303030303,
          "ara_heart": 1.6893939393939394,
          "phi_score": 0.6509692132978917,
          "future_gap": 0.2544749628887499,
          "coupling_delta": -0.015455353931530268
        },
        {
          "time_s": 280.0,
          "gap": 0.030216336591111833,
          "coupling": 0.025142174630500586,
          "ara_resp": 1.2966764418377321,
          "ara_heart": 1.3364552114552115,
          "phi_score": 0.5117447829001371,
          "future_gap": 0.23989518159292375,
          "coupling_delta": -0.01927067200802486
        },
        {
          "time_s": 285.0,
          "gap": 0.3164465189991225,
          "coupling": 0.03409120746196787,
          "ara_resp": 1.2861635220125787,
          "ara_heart": 1.7649286987522281,
          "phi_score": 0.5874516657051205,
          "future_gap": 0.24099915892825463,
          "coupling_delta": 0.008949032831467287
        },
        {
          "time_s": 290.0,
          "gap": 0.46779081692775454,
          "coupling": 0.05350089238546306,
          "ara_resp": 1.2893081761006289,
          "ara_heart": 2.058333333333333,
          "phi_score": 0.42550763100392847,
          "future_gap": 0.2404470179148524,
          "coupling_delta": 0.019409684923495187
        }
      ]
    },
    "tides": {
      "name": "tide_lunar_solar_triangle_gate",
      "status": "ok",
      "source": {
        "source": "NOAA CO-OPS hourly water level, station 9414290, 2024-07-25 00:00 to 2024-12-31 23:00",
        "requested": "2024-01-01 to 2024-12-31",
        "source_path": "F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\TheFormula\\data_cache\\noaa_9414290_hourly_2024.json",
        "source_kind": "cache",
        "synthetic": false
      },
      "n_hours": 3840,
      "date_range": [
        "2024-07-25 00:00",
        "2024-12-31 23:00"
      ],
      "leakage_guard": "Best lag and scale fitted on first 60%; held-out test is later data only.",
      "best_lag_hours_train_only": -48,
      "train_gate_range_corr_at_best_lag": 0.34193688346210344,
      "heldout_model": {
        "n": 1488,
        "mae": 0.2616362412924005,
        "baseline_mae": 0.1505779569892473,
        "mae_lift_vs_baseline": -0.11105828430315318,
        "corr": 0.7789581214274786
      },
      "amplitude_breathing": {
        "high_gate_threshold_train_q80": 0.9248445421438594,
        "low_gate_threshold_train_q20": 0.13247568717502778,
        "heldout_high_gate_range": {
          "n": 301,
          "mean": 2.263906976744186,
          "std": 0.2876137787012878,
          "p25": 1.953,
          "p50": 2.1710000000000003,
          "p75": 2.552
        },
        "heldout_low_gate_range": {
          "n": 259,
          "mean": 1.411903474903475,
          "std": 0.13695418994088937,
          "p25": 1.3079999999999998,
          "p50": 1.4040000000000001,
          "p75": 1.532
        },
        "supports_amplitude_breathing": true
      },
      "speed_metrics": {
        "kind": "amplitude_breathing",
        "carrier_period_hours": 12.4206012,
        "cycle_period_hours": 354.36705600000005,
        "half_cycle_hours": 177.18352800000002,
        "time_rung_phi_carrier_to_modulation": 6.9636210119183355,
        "high_low_range_difference_m": 0.852003501840711,
        "fractional_range_difference": 0.46357314287454915,
        "fractional_speed_per_hour": 0.0026163444655789283,
        "fractional_per_spring_neap_cycle": 0.9271462857490983,
        "rung_density_fractional": 0.13314140504807404
      },
      "sample_rows": [
        {
          "t": 2304,
          "date": "2024-10-29 00:00",
          "range": 1.384,
          "gate": 0.26387904126543854,
          "persistence": 1.4000000000000001
        },
        {
          "t": 2305,
          "date": "2024-10-29 01:00",
          "range": 1.384,
          "gate": 0.27249783738604644,
          "persistence": 1.4000000000000001
        },
        {
          "t": 2306,
          "date": "2024-10-29 02:00",
          "range": 1.384,
          "gate": 0.28115650970367106,
          "persistence": 1.4000000000000001
        },
        {
          "t": 2307,
          "date": "2024-10-29 03:00",
          "range": 1.384,
          "gate": 0.28985119527057185,
          "persistence": 1.4000000000000001
        },
        {
          "t": 2308,
          "date": "2024-10-29 04:00",
          "range": 1.384,
          "gate": 0.29857814030301344,
          "persistence": 1.4000000000000001
        },
        {
          "t": 2309,
          "date": "2024-10-29 05:00",
          "range": 1.384,
          "gate": 0.3073336971480213,
          "persistence": 1.4000000000000001
        },
        {
          "t": 2310,
          "date": "2024-10-29 06:00",
          "range": 1.384,
          "gate": 0.3161143212289353,
          "persistence": 1.4000000000000001
        },
        {
          "t": 2311,
          "date": "2024-10-29 07:00",
          "range": 1.384,
          "gate": 0.32491656798618035,
          "persistence": 1.4000000000000001
        }
      ]
    }
  }
};
