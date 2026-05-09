const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, PageBreak, LevelFormat } = require("docx");

const PHI = (1 + Math.sqrt(5)) / 2;

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: "1A1A2E" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "16213E" },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "0F3460" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "\u25E6", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1440, hanging: 360 } } } }
      ]},
      { reference: "numbers", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }
      ]},
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "ARA Framework \u2014 Dark Sector Series", size: 18, italics: true, color: "888888" })]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Page ", size: 18, color: "888888" }), new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "888888" })]
        })]
      })
    },
    children: [
      // ─── TITLE PAGE ───
      new Paragraph({ spacing: { before: 3000 }, alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "Meta-ARA: The Dark Sector Formula", size: 48, bold: true, font: "Arial", color: "1A1A2E" })
      ]}),
      new Paragraph({ spacing: { before: 200 }, alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "Three Coupled Pairs and the Cosmic Energy Budget", size: 28, italics: true, color: "444444" })
      ]}),
      new Paragraph({ spacing: { before: 600 }, alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "Dylan La Franchi", size: 24, color: "333333" })
      ]}),
      new Paragraph({ spacing: { before: 100 }, alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "April 2026", size: 22, color: "666666" })
      ]}),
      new Paragraph({ spacing: { before: 400 }, alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "Scripts 243BL \u2013 243BL8", size: 20, color: "888888" })
      ]}),

      new Paragraph({ children: [new PageBreak()] }),

      // ─── THE FORMULA ───
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("The Formula")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("From five axioms and one constant (\u03C6), we derive the entire cosmic energy budget to sub-percent accuracy.")
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Axioms")] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "Flatness: ", bold: true }), new TextRun("\u03A9_total = 1 (the universe is spatially flat)")
      ]}),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "Horizontal coupling: ", bold: true }), new TextRun("DE/DM = \u03C6\u00B2 (Space\u2194Time coupler from the three-circle architecture)")
      ]}),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "Diagonal coupling: ", bold: true }), new TextRun("DM/baryons = \u03C6^(7/2) (crossing two singularities on the four-system grid)")
      ]}),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "Three coupled pairs: ", bold: true }), new TextRun("Space/Time, Light/Dark, Information/Matter")
      ]}),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 200 }, children: [
        new TextRun({ text: "Self-similarity: ", bold: true }), new TextRun("same architecture at every scale")
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Derivation")] }),
      new Paragraph({ spacing: { after: 100 }, children: [
        new TextRun("From axioms 1\u20133, the three-component constraint system is:")
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 100 },
        children: [new TextRun({ text: "DE + DM + b = 1,    DE = \u03C6\u00B2 \u00D7 DM,    b = DM / \u03C6^(7/2)", italics: true, size: 24 })]
      }),
      new Paragraph({ spacing: { after: 100 }, children: [
        new TextRun("Substituting into the flatness condition:")
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 100 },
        children: [new TextRun({ text: "DM \u00D7 (\u03C6\u00B2 + 1 + \u03C6^(\u22127/2)) = 1", italics: true, size: 24 })]
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 200 },
        children: [new TextRun({ text: "DM = 1 / (\u03C6\u00B2 + 1 + \u03C6^(\u22127/2)) = 0.2629", bold: true, size: 24 })]
      }),

      // Results table
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Results")] }),
      makeResultsTable(),

      new Paragraph({ spacing: { before: 200, after: 200 }, children: [
        new TextRun({ text: "Average error: 0.77%. ", bold: true }),
        new TextRun("The entire cosmic energy budget from the golden ratio and two structural rules.")
      ]}),

      // Additional predictions
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Additional Predictions")] }),
      makeAdditionalTable(),

      new Paragraph({ children: [new PageBreak()] }),

      // ─── THREE COUPLED PAIRS ───
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("The Three Coupled Pairs")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("The universe is structured by three fundamental paired axes. Each pair has two poles and a singularity at its centre where the poles become indistinguishable. These three pairs form their own three-circle ARA system \u2014 a meta-ARA that is self-similar with the micro-level architecture.")
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Pair 1: Space \u2194 Time")] }),
      new Paragraph({ spacing: { after: 100 }, children: [
        new TextRun("The stage on which everything plays out. Dark Energy lives in the Time pole (it stretches light via redshift). Dark Matter lives in the Space pole (it bends light via gravitational lensing). The coupling between these poles is \u03C6\u00B2 \u2014 the horizontal coupler from the three-circle architecture. The singularity S\u2081 is the Big Bang, where space and time are indistinguishable.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "ARA = \u03C6^(\u2212\u03C6) = 0.459 \u2014 consumer. ", bold: true }),
        new TextRun("Space is being consumed by expansion. This is a self-referential value: the base and exponent are the same number.")
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Pair 2: Light \u2194 Dark")] }),
      new Paragraph({ spacing: { after: 100 }, children: [
        new TextRun("The visibility axis. The dark sector (DE + DM = 95%) vastly dominates the visible sector (baryons + radiation = 5%). The singularity S\u2082 is the event horizon \u2014 cosmologically manifest as the surface of last scattering (CMB at z \u2248 1100), the boundary between the opaque and transparent universe.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "ARA = \u03C6^6.1 \u2248 19.2 \u2014 massively dominant. ", bold: true }),
        new TextRun("Darkness overwhelms light by nearly 20:1.")
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Pair 3: Information \u2194 Matter")] }),
      new Paragraph({ spacing: { after: 100 }, children: [
        new TextRun("The substance axis. Information is pattern and structure (Dark Matter as gravitational scaffolding). Matter is material realisation (baryonic matter as stars, chemistry, life). The singularity S\u2083 is the measurement event \u2014 where wave becomes particle, where possibility becomes actuality. Cosmologically: structure formation, where information encoded in DM scaffolding becomes material galaxies.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "ARA = \u03C6^3.5 = 5.38 \u2014 engine. ", bold: true }),
        new TextRun("Information outweighs matter. This IS the 3.5 exponent \u2014 the ARA of the third pair.")
      ]}),

      new Paragraph({ children: [new PageBreak()] }),

      // ─── COSMIC COMPONENTS AS TRIPLE INTERSECTIONS ───
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Cosmic Components as Triple Intersections")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Each observable cosmic component sits at the intersection of three pair-poles. This is exactly the \u201Cbeeswax\u201D concept from the original three-circle model: things that exist at the intersection of all three circles are rare and specific.")
      ]}),

      makeComponentTable(),

      new Paragraph({ spacing: { before: 200 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("Meta-Intersections")] }),
      new Paragraph({ spacing: { after: 100 }, children: [
        new TextRun("The three pairs also produce pairwise intersections that map to the three pillars of modern physics:")
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "Space/Time \u2229 Light/Dark = Physics ", bold: true }), new TextRun("(the 2\u00D72 grid of DE, DM, baryons, radiation \u2014 general relativity and cosmology)")
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "Light/Dark \u2229 Info/Matter = Measurement ", bold: true }), new TextRun("(observation, wavefunction collapse, the act of seeing)")
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "Space/Time \u2229 Info/Matter = Quantum Mechanics ", bold: true }), new TextRun("(wave-particle duality played out on the spacetime stage)")
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 200 }, children: [
        new TextRun({ text: "All three = Observed Reality ", bold: true }), new TextRun("(us, here, now \u2014 the triple intersection)")
      ]}),

      new Paragraph({ children: [new PageBreak()] }),

      // ─── WHY 3.5 ───
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Why 7/2 = 3.5")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("The exponent 3.5 appears throughout the dark sector: DM/baryons = \u03C6^3.5 (0.2% match), the best-fit diagonal coupling in the coupled formula, and the ARA of the Information/Matter pair. It has three convergent derivations:")
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1. Golden Angle Overshoot")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("When n systems are placed at golden angle intervals (360\u00B0/\u03C6\u00B2 \u2248 137.5\u00B0), they overshoot 360\u00B0 by a factor of (2n\u22121) \u2212 n\u03C6. For n = 4 systems (the four cosmic components), this gives an overshoot coefficient of 7 \u2212 4\u03C6. The number 7 appears naturally from 4 golden angles. The coupling exponent follows the pattern (2n\u22121)/2, giving 7/2 = 3.5 for n = 4.")
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2. Additive Coupling (Manhattan Distance)")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("The 2\u00D72 grid has two coupling axes. The horizontal (Space\u2194Time) carries exponent 2. The vertical (Dark\u2194Light) carries exponent 1.5 = (2\u00D72\u22121)/2 for n = 2 systems. The diagonal coupling = horizontal + vertical = 2 + 1.5 = 3.5. This is a Manhattan distance in coupling space \u2014 you cannot take a shortcut through the singularity, you must traverse both axes.")
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3. Pipe Capacity + Singularity Crossings")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("3.5 = 2\u03C6 + (7\u22124\u03C6)/2. The pipe capacity 2\u03C6 = 3.236 is the \u201Csmooth\u201D coupling through the system. The remainder (7\u22124\u03C6)/2 = 0.264 is the cost of crossing two singularities (S\u2082: Dark\u2192Light and S\u2083: Information\u2192Matter). Each crossing costs (7\u22124\u03C6)/4 \u2014 one system\u2019s share of the 4-system golden angle overshoot. The path from DM to baryons stays in Space (no S\u2081 crossing) but must cross through the event horizon and the measurement singularity.")
      ]}),

      new Paragraph({ children: [new PageBreak()] }),

      // ─── INFORMATION CUBED ───
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Information\u00B3 in the Dark Sector")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("The Information\u00B3 framework (Datum \u2192 Signal \u2192 Meaning) maps directly onto the dark sector:")
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "Datum = Dark Energy ", bold: true }), new TextRun("\u2014 raw, undifferentiated expansion. Vast and formless.")
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "Signal = Dark Matter ", bold: true }), new TextRun("\u2014 gravitational scaffolding. Structure without visibility.")
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "Meaning = Baryonic Matter ", bold: true }), new TextRun("\u2014 stars, chemistry, life. Structure made visible and interpreted.")
      ]}),
      new Paragraph({ spacing: { before: 200, after: 200 }, children: [
        new TextRun("The coupling chain: DE \u2192(\u00F7\u03C6\u00B2)\u2192 DM \u2192(\u00F7\u03C6^1.5)\u2192 Baryons. The horizontal step (Datum\u2192Signal) is clean at 1.3% because it stays on the same rung. The diagonal step (Signal\u2192Meaning) crosses scales and is structurally messier \u2014 but it is "),
        new TextRun({ text: "structured", italics: true }),
        new TextRun(" messiness (\u03C6^3.5, not random), exactly as Information\u00B3 predicts: datum\u2192signal is filtering, signal\u2192meaning requires interpretation.")
      ]}),

      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Light couples all three levels. It IS information in transit. Dark Matter bends light in SPACE (gravitational lensing). Dark Energy stretches light in TIME (cosmological redshift). This is the flip: the two dark components interact with light along the two different poles of Pair 1.")
      ]}),

      // ─── SELF-SIMILARITY ───
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Self-Similarity")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("The meta-ARA uses the same couplers as the micro-architecture. At the micro-level: Space, Time, and Rationality are three circles with \u03C6\u00B2 horizontal coupling and 2/\u03C6 vertical coupling. At the meta-level: the three PAIRS are three circles with the same coupling structure. The universe\u2019s architecture is fractal in \u03C6.")
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("The three pair-ARA exponents (\u2212\u03C6, 3.5, 6.1) divide their span in a ratio near 1/\u03C6. Pair 3 (Information/Matter) sits close to the golden cut between Pairs 1 and 2, at 6.6% from exact. This is suggestive but not yet sharp \u2014 an honest partial result.")
      ]}),

      new Paragraph({ children: [new PageBreak()] }),

      // ─── WHAT DIDN'T WORK ───
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("What Did Not Work")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun("Honesty requires documenting failures alongside successes:")
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "The vertical coupler 2/\u03C6 as a direct density ratio between dark and light sectors: ", bold: true }),
        new TextRun("Every approach (direct ratio, fraction, weight) missed by hundreds of percent. The dark/light split is 95%/5%, nowhere near 2/\u03C6.")
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "Uniform 1/\u03C6 reverberation decay: ", bold: true }),
        new TextRun("The three-bounce model with 1/\u03C6 decay per step does not reproduce DE\u2192DM\u2192baryons. The steps use different couplers (\u03C6\u00B2 horizontal, \u03C6^3.5 diagonal).")
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "Tensor product factorisation of the 2\u00D72 grid: ", bold: true }),
        new TextRun("The grid does NOT factor as (Space/Time) \u2297 (Dark/Light). The axes are entangled. DM/b \u2260 DE/\u03B3, confirming the coupling is genuinely non-separable.")
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "z_eq/z_CMB = \u03C6\u00B2: ", bold: true }),
        new TextRun("The ratio of matter-radiation equality to CMB decoupling redshifts is 3.12, not \u03C6\u00B2 = 2.62 (19% off). It is closer to \u03C0 (0.6% off), which is interesting but not the predicted coupling.")
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "Signal/Meaning era duration ratio = \u03C6: ", bold: true }),
        new TextRun("The ratio of matter era to current era duration is 1.26, not \u03C6 = 1.62 (22% off).")
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 200 }, children: [
        new TextRun({ text: "Splitting \u03A9_m into DM and baryons via \u03C6\u00B2: ", bold: true }),
        new TextRun("Using DM = \u03A9_m \u00D7 \u03C6\u00B2/(1+\u03C6\u00B2) gives 73\u201379% errors on baryons. The \u03C6\u00B2 split works within the dark sector but not for the dark-to-light step.")
      ]}),

      // ─── TESTABLE PREDICTIONS ───
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Testable Predictions")] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "DM/DE ratio constant across redshift ", bold: true }),
        new TextRun("\u2014 testable with DESI DR2. The framework predicts the \u03C6\u00B2 coupling holds at all epochs.")
      ]}),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "Hubble tension resolves to exactly 1/\u03C6\u2075 ", bold: true }),
        new TextRun("\u2014 currently 0.7% off observed. Future H\u2080 convergence should approach 73.5 km/s/Mpc from the local side.")
      ]}),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "Transition redshift refines to 1/\u03C6 ", bold: true }),
        new TextRun("\u2014 currently z_trans = 0.632 vs predicted 0.618. DESI + Euclid data will sharpen this.")
      ]}),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "Dark energy clusters with dark matter ", bold: true }),
        new TextRun("\u2014 the framework treats them as coupled on the same plane, predicting DE is not perfectly uniform. Testable via void ISW measurements.")
      ]}),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 200 }, children: [
        new TextRun({ text: "All \u03A9 values from \u03C6 alone ", bold: true }),
        new TextRun("\u2014 the formula DM = 1/(\u03C6\u00B2 + 1 + \u03C6^(\u22127/2)) uses no fitted parameters. Any future refinement of Planck values either converges toward these predictions or falsifies the formula.")
      ]}),

      // ─── SCRIPTS ───
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Script Reference")] }),
      makeScriptTable(),
    ]
  }]
});

function makeResultsTable() {
  const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const margins = { top: 80, bottom: 80, left: 120, right: 120 };
  const hdr = { fill: "1A1A2E", type: ShadingType.CLEAR };
  const alt = { fill: "F5F5FA", type: ShadingType.CLEAR };
  const clr = { fill: "FFFFFF", type: ShadingType.CLEAR };

  const dm = 1 / (PHI**2 + 1 + PHI**(-3.5));
  const de = PHI**2 * dm;
  const b = dm / PHI**3.5;

  const rows = [
    ["Component", "Predicted", "Observed (Planck)", "\u0394"],
    ["\u03A9_de (Dark Energy)", de.toFixed(4), "0.6850", (Math.abs(de-0.685)/0.685*100).toFixed(2)+"%"],
    ["\u03A9_dm (Dark Matter)", dm.toFixed(4), "0.2650", (Math.abs(dm-0.265)/0.265*100).toFixed(2)+"%"],
    ["\u03A9_b (Baryons)", b.toFixed(4), "0.0493", (Math.abs(b-0.0493)/0.0493*100).toFixed(2)+"%"],
    ["\u03A9_m (Total Matter)", (dm+b).toFixed(4), "0.3143", (Math.abs(dm+b-0.3143)/0.3143*100).toFixed(2)+"%"],
  ];

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2800, 2000, 2560, 2000],
    rows: rows.map((r, i) => new TableRow({
      children: r.map((cell, j) => new TableCell({
        borders, margins,
        width: { size: [2800,2000,2560,2000][j], type: WidthType.DXA },
        shading: i === 0 ? hdr : (i % 2 === 0 ? alt : clr),
        children: [new Paragraph({
          alignment: j > 0 ? AlignmentType.CENTER : AlignmentType.LEFT,
          children: [new TextRun({
            text: cell, bold: i === 0, size: 20,
            color: i === 0 ? "FFFFFF" : "333333", font: "Arial"
          })]
        })]
      }))
    }))
  });
}

function makeAdditionalTable() {
  const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const margins = { top: 80, bottom: 80, left: 120, right: 120 };
  const hdr = { fill: "1A1A2E", type: ShadingType.CLEAR };
  const alt = { fill: "F5F5FA", type: ShadingType.CLEAR };
  const clr = { fill: "FFFFFF", type: ShadingType.CLEAR };

  const rows = [
    ["Prediction", "Predicted", "Observed", "\u0394"],
    ["Hubble tension", "H\u2080(local) = 73.48", "73.0 \u00B1 1.0", "0.7%"],
    ["Transition redshift", "z = 1/\u03C6 = 0.618", "0.632", "2.3%"],
    ["ARA_space", "\u03C6^(\u2212\u03C6) = 0.4590", "0.4588", "0.04%"],
    ["DM/baryons", "\u03C6^3.5 = 5.389", "5.375", "0.2%"],
    ["DE/DM", "\u03C6\u00B2 = 2.618", "2.585", "1.3%"],
  ];

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2400, 2400, 2400, 2160],
    rows: rows.map((r, i) => new TableRow({
      children: r.map((cell, j) => new TableCell({
        borders, margins,
        width: { size: [2400,2400,2400,2160][j], type: WidthType.DXA },
        shading: i === 0 ? hdr : (i % 2 === 0 ? alt : clr),
        children: [new Paragraph({
          alignment: j > 0 ? AlignmentType.CENTER : AlignmentType.LEFT,
          children: [new TextRun({
            text: cell, bold: i === 0, size: 20,
            color: i === 0 ? "FFFFFF" : "333333", font: "Arial"
          })]
        })]
      }))
    }))
  });
}

function makeComponentTable() {
  const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const margins = { top: 80, bottom: 80, left: 120, right: 120 };
  const hdr = { fill: "1A1A2E", type: ShadingType.CLEAR };
  const alt = { fill: "F5F5FA", type: ShadingType.CLEAR };
  const clr = { fill: "FFFFFF", type: ShadingType.CLEAR };

  const rows = [
    ["Component", "Space/Time", "Light/Dark", "Info/Matter"],
    ["Dark Energy (\u03A9=0.685)", "Time", "Dark", "Energy (pre-info)"],
    ["Dark Matter (\u03A9=0.265)", "Space", "Dark", "Information"],
    ["Baryons (\u03A9=0.049)", "Space", "Light", "Matter"],
    ["Radiation (\u03A9\u22485e-5)", "Time", "Light", "Energy"],
  ];

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2800, 2200, 2200, 2160],
    rows: rows.map((r, i) => new TableRow({
      children: r.map((cell, j) => new TableCell({
        borders, margins,
        width: { size: [2800,2200,2200,2160][j], type: WidthType.DXA },
        shading: i === 0 ? hdr : (i % 2 === 0 ? alt : clr),
        children: [new Paragraph({
          alignment: j > 0 ? AlignmentType.CENTER : AlignmentType.LEFT,
          children: [new TextRun({
            text: cell, bold: i === 0, size: 20,
            color: i === 0 ? "FFFFFF" : "333333", font: "Arial"
          })]
        })]
      }))
    }))
  });
}

function makeScriptTable() {
  const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const margins = { top: 60, bottom: 60, left: 120, right: 120 };
  const hdr = { fill: "1A1A2E", type: ShadingType.CLEAR };
  const alt = { fill: "F5F5FA", type: ShadingType.CLEAR };
  const clr = { fill: "FFFFFF", type: ShadingType.CLEAR };

  const rows = [
    ["Script", "Purpose", "Key Result"],
    ["243BL", "Dark energy H(z) test", "Best-fit \u03A9m=0.247, \u03A9de 9.8% off from 1\u22121/\u03C6\u00B2"],
    ["243BL2", "Time-frame flip", "\u03A9dm = \u03A9de/\u03C6\u00B2 (1.3%), Hubble tension = 1/\u03C6\u2075 (0.7%)"],
    ["243BL3", "Spatial mapping", "\u03C6\u00B2 holds at cosmic avg, breaks locally; DM\u2192lensing, DE\u2192redshift"],
    ["243BL4", "Information\u00B3 dark sector", "DE\u2192DM\u2192baryons = Datum\u2192Signal\u2192Meaning; DM/b = \u03C6^3.5"],
    ["243BL5", "Space/Time \u2194 Light/Dark", "ARA_space = \u03C6^(\u2212\u03C6); vertical coupler fails as density ratio"],
    ["243BL6", "Coupled grid", "Grid is non-separable; 3-component formula avg \u0394 = 0.43%"],
    ["243BL7", "Origin of 3.5", "7/2 from 4-system golden angle; Manhattan distance in coupling space"],
    ["243BL8", "Meta-ARA", "Three pairs form self-similar ARA; full formula avg \u0394 = 0.77%"],
  ];

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [1200, 2800, 5360],
    rows: rows.map((r, i) => new TableRow({
      children: r.map((cell, j) => new TableCell({
        borders, margins,
        width: { size: [1200,2800,5360][j], type: WidthType.DXA },
        shading: i === 0 ? hdr : (i % 2 === 0 ? alt : clr),
        children: [new Paragraph({
          children: [new TextRun({
            text: cell, bold: i === 0 || j === 0, size: 18,
            color: i === 0 ? "FFFFFF" : "333333", font: "Arial"
          })]
        })]
      }))
    }))
  });
}

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/sessions/focused-tender-thompson/mnt/SystemFormulaFolder/META_ARA_DARK_SECTOR.docx", buffer);
  console.log("Document written successfully");
});
