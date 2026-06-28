import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_DIR = os.path.join(BASE_DIR, "rules")

# ================================================================
# PYTHON DEFAULT FALLBACKS
# ================================================================

DEFAULT_ACADEMIC_SYNONYMS = {
    # -- Verbs --
    "show":        ["demonstrate", "illustrate", "reveal"],
    "shows":       ["demonstrates", "illustrates", "reveals"],
    "shown":       ["demonstrated", "illustrated", "established"],
    "showing":     ["demonstrating", "illustrating", "revealing"],
    "use":         ["employ", "utilize", "apply"],
    "uses":        ["employs", "utilizes", "applies"],
    "used":        ["employed", "utilized", "applied"],
    "using":       ["employing", "utilizing", "applying"],
    "describe":    ["characterize", "outline", "delineate"],
    "describes":   ["characterizes", "outlines", "delineates"],
    "described":   ["characterized", "outlined", "delineated"],
    "describing":  ["characterizing", "outlining", "delineating"],
    "derive":      ["obtain", "establish", "formulate"],
    "derives":     ["obtains", "establishes", "formulates"],
    "derived":     ["obtained", "established", "formulated"],
    "deriving":    ["obtaining", "establishing", "formulating"],
    "consider":    ["examine", "investigate", "analyze"],
    "considers":   ["examines", "investigates", "analyzes"],
    "considered":  ["examined", "investigated", "analyzed"],
    "considering": ["examining", "investigating", "analyzing"],
    "obtain":      ["derive", "acquire", "determine"],
    "obtains":     ["derives", "acquires", "determines"],
    "obtained":    ["derived", "acquired", "determined"],
    "solve":       ["resolve", "address", "tackle"],
    "solves":      ["resolves", "addresses", "tackles"],
    "solved":      ["resolved", "addressed", "tackled"],
    "solving":     ["resolving", "addressing", "tackling"],
    "assume":      ["suppose", "postulate", "presume"],
    "assumes":     ["supposes", "postulates", "presumes"],
    "assumed":     ["supposed", "postulated", "presumed"],
    "define":      ["specify", "designate", "characterize"],
    "defined":     ["specified", "designated", "characterized"],
    "present":     ["introduce", "provide", "put forward"],
    "presents":    ["introduces", "provides", "puts forward"],
    "presented":   ["introduced", "provided", "put forward"],
    "discuss":     ["examine", "explore", "address"],
    "discusses":   ["examines", "explores", "addresses"],
    "discussed":   ["examined", "explored", "addressed"],
    "note":        ["observe", "recognize", "highlight"],
    "noted":       ["observed", "recognized", "highlighted"],
    "represent":   ["denote", "express", "capture"],
    "represents":  ["denotes", "expresses", "captures"],
    "apply":       ["employ", "implement", "adopt"],
    "applies":     ["employs", "implements", "adopts"],
    "applied":     ["employed", "implemented", "adopted"],
    "provide":     ["furnish", "supply", "offer"],
    "provides":    ["furnishes", "supplies", "offers"],
    "provided":    ["furnished", "supplied", "offered"],
    "require":     ["necessitate", "demand", "call for"],
    "requires":    ["necessitates", "demands", "calls for"],
    "required":    ["necessitated", "demanded", "called for"],
    "propose":     ["suggest", "put forward", "advance"],
    "proposes":    ["suggests", "puts forward", "advances"],
    "proposed":    ["suggested", "put forward", "advanced"],
    "investigate": ["examine", "explore", "study"],
    "investigates":["examines", "explores", "studies"],
    "investigated":["examined", "explored", "studied"],
    "focus":       ["concentrate", "center", "emphasize"],
    "focuses":     ["concentrates", "centers", "emphasizes"],
    "focused":     ["concentrated", "centered", "emphasized"],
    "develop":     ["formulate", "construct", "devise"],
    "develops":    ["formulates", "constructs", "devises"],
    "developed":   ["formulated", "constructed", "devised"],
    "determine":   ["ascertain", "compute", "evaluate"],
    "determines":  ["ascertains", "computes", "evaluates"],
    "determined":  ["ascertained", "computed", "evaluated"],
    "analyze":     ["examine", "evaluate", "assess"],
    "analyzes":    ["examines", "evaluates", "assesses"],
    "analyzed":    ["examined", "evaluated", "assessed"],
    "evaluate":    ["assess", "appraise", "gauge"],
    "evaluates":   ["assesses", "appraises", "gauges"],
    "evaluated":   ["assessed", "appraised", "gauged"],
    "confirm":     ["verify", "validate", "corroborate"],
    "confirms":    ["verifies", "validates", "corroborates"],
    "confirmed":   ["verified", "validated", "corroborated"],
    "yield":       ["produce", "generate", "give rise to"],
    "yields":      ["produces", "generates", "gives rise to"],
    "extend":      ["generalize", "broaden", "expand"],
    "extends":     ["generalizes", "broadens", "expands"],
    "extended":    ["generalized", "broadened", "expanded"],
    "reduce":      ["decrease", "diminish", "lower"],
    "reduces":     ["decreases", "diminishes", "lowers"],
    "involve":     ["entail", "encompass", "comprise"],
    "involves":    ["entails", "encompasses", "comprises"],
    "involved":    ["entailed", "encompassed", "comprised"],
    "ensure":      ["guarantee", "ascertain", "secure"],
    "ensures":     ["guarantees", "ascertains", "secures"],
    "occur":       ["arise", "emerge", "take place"],
    "occurs":      ["arises", "emerges", "takes place"],
    "lead":        ["give rise", "result", "contribute"],
    "leads":       ["gives rise", "results", "contributes"],
    "perform":     ["carry out", "execute", "conduct"],
    "performs":    ["carries out", "executes", "conducts"],
    "compute":     ["calculate", "evaluate", "determine"],
    "computes":    ["calculates", "evaluates", "determines"],
    "computed":    ["calculated", "evaluated", "determined"],
    "approximate": ["estimate", "approach"],
    "approximates":["estimates", "approaches"],
    "approximated":["estimated", "approached"],
    "indicate":    ["suggest", "imply", "signal"],
    "indicates":   ["suggests", "implies", "signals"],
    "indicated":   ["suggested", "implied", "signaled"],
    "depend":      ["rely", "hinge", "rest"],
    "depends":     ["relies", "hinges", "rests"],
    "satisfy":     ["fulfill", "meet", "comply with"],
    "satisfies":   ["fulfills", "meets", "complies with"],
    "construct":   ["build", "formulate", "assemble"],
    "constructs":  ["builds", "formulates", "assembles"],
    "arises":      ["emerges", "originates", "results"],
    "arising":     ["emerging", "originating", "resulting"],
    "hold":        ["remain valid", "persist", "be satisfied"],
    "holds":       ["remains valid", "persists", "is satisfied"],
    "denote":      ["represent", "signify", "designate"],
    "denotes":     ["represents", "signifies", "designates"],
    "denoted":     ["represented", "signified", "designated"],
    "express":     ["formulate", "state", "articulate"],
    "expressed":   ["formulated", "stated", "articulated"],
    "establish":   ["demonstrate", "set up", "prove"],
    "establishes": ["demonstrates", "sets up", "proves"],
    "established": ["demonstrated", "set up", "proven"],
    "measure":     ["quantify", "gauge", "assess"],
    "measures":    ["quantifies", "gauges", "assesses"],
    "observe":     ["notice", "note", "detect"],
    "observes":    ["notices", "notes", "detects"],
    "observed":    ["noticed", "noted", "detected"],

    # -- Nouns --
    "method":         ["approach", "technique", "scheme"],
    "methods":        ["approaches", "techniques", "schemes"],
    "approach":       ["method", "strategy", "framework"],
    "approaches":     ["methods", "strategies", "frameworks"],
    "technique":      ["method", "procedure", "scheme"],
    "techniques":     ["methods", "procedures", "schemes"],
    "problem":        ["challenge", "issue", "question"],
    "problems":       ["challenges", "issues", "questions"],
    "solution":       ["resolution", "result", "outcome"],
    "solutions":      ["resolutions", "results", "outcomes"],
    "result":         ["outcome", "finding", "consequence"],
    "results":        ["outcomes", "findings", "consequences"],
    "analysis":       ["examination", "investigation", "assessment"],
    "behavior":       ["behaviour", "characteristics", "dynamics"],
    "property":       ["characteristic", "attribute", "feature"],
    "properties":     ["characteristics", "attributes", "features"],
    "application":    ["implementation", "utilization", "usage"],
    "applications":   ["implementations", "utilizations", "usages"],
    "framework":      ["structure", "paradigm", "architecture"],
    "model":          ["representation", "formulation", "construct"],
    "models":         ["representations", "formulations", "constructs"],
    "system":         ["framework", "configuration", "arrangement"],
    "systems":        ["frameworks", "configurations", "arrangements"],
    "accuracy":       ["precision", "fidelity", "exactness"],
    "error":          ["deviation", "discrepancy", "residual"],
    "errors":         ["deviations", "discrepancies", "residuals"],
    "condition":      ["criterion", "requirement", "constraint"],
    "conditions":     ["criteria", "requirements", "constraints"],
    "domain":         ["region", "area", "zone"],
    "investigation":  ["study", "examination", "inquiry"],
    "investigations": ["studies", "examinations", "inquiries"],
    "research":       ["study", "investigation", "inquiry"],
    "concept":        ["notion", "idea", "construct"],
    "concepts":       ["notions", "ideas", "constructs"],
    "aspect":         ["facet", "dimension", "component"],
    "aspects":        ["facets", "dimensions", "components"],
    "process":        ["procedure", "mechanism", "operation"],
    "processes":      ["procedures", "mechanisms", "operations"],
    "phenomenon":     ["effect", "occurrence", "event"],
    "phenomena":      ["effects", "occurrences", "events"],
    "structure":      ["architecture", "arrangement", "organization"],
    "context":        ["setting", "framework", "scope"],
    "feature":        ["characteristic", "attribute", "trait"],
    "features":       ["characteristics", "attributes", "traits"],
    "tool":           ["instrument", "utility", "resource"],
    "tools":          ["instruments", "utilities", "resources"],
    "insight":        ["understanding", "perspective", "viewpoint"],
    "insights":       ["understandings", "perspectives", "viewpoints"],
    "constraint":     ["restriction", "limitation", "bound"],
    "constraints":    ["restrictions", "limitations", "bounds"],
    "formulation":    ["expression", "representation", "statement"],
    "formulations":   ["expressions", "representations", "statements"],
    "component":      ["element", "constituent", "part"],
    "components":     ["elements", "constituents", "parts"],
    "scheme":         ["approach", "method", "strategy"],
    "schemes":        ["approaches", "methods", "strategies"],
    "procedure":      ["protocol", "process", "method"],
    "procedures":     ["protocols", "processes", "methods"],
    "assumption":     ["hypothesis", "premise", "supposition"],
    "assumptions":    ["hypotheses", "premises", "suppositions"],
    "derivation":     ["development", "formulation", "construction"],
    "derivations":    ["developments", "formulations", "constructions"],
    "principle":      ["law", "axiom", "tenet"],
    "principles":     ["laws", "axioms", "tenets"],
    "limitation":     ["restriction", "shortcoming", "drawback"],
    "limitations":    ["restrictions", "shortcomings", "drawbacks"],

    # -- Adjectives --
    "important":     ["significant", "crucial", "essential"],
    "significant":   ["substantial", "considerable", "notable"],
    "fundamental":   ["essential", "core", "primary"],
    "basic":         ["foundational", "elementary", "rudimentary"],
    "complex":       ["intricate", "sophisticated", "involved"],
    "simple":        ["straightforward", "elementary", "uncomplicated"],
    "classical":     ["traditional", "conventional", "standard"],
    "common":        ["prevalent", "widespread", "typical"],
    "various":       ["diverse", "several", "multiple"],
    "different":     ["distinct", "diverse", "alternative"],
    "general":       ["broad", "comprehensive", "overarching"],
    "specific":      ["particular", "precise", "definite"],
    "numerical":     ["computational", "discrete", "quantitative"],
    "practical":     ["pragmatic", "applied", "concrete"],
    "appropriate":   ["suitable", "fitting", "proper"],
    "sufficient":    ["adequate", "ample", "satisfactory"],
    "necessary":     ["essential", "required", "indispensable"],
    "similar":       ["analogous", "comparable", "akin"],
    "main":          ["principal", "primary", "central"],
    "key":           ["pivotal", "central", "critical"],
    "wide":          ["broad", "extensive", "expansive"],
    "useful":        ["valuable", "beneficial", "advantageous"],
    "detailed":      ["comprehensive", "thorough", "in-depth"],
    "standard":      ["conventional", "established", "canonical"],
    "typical":       ["characteristic", "representative", "standard"],
    "well-known":    ["widely recognized", "established", "celebrated"],
    "well known":    ["widely recognized", "established", "celebrated"],
    "corresponding": ["associated", "related", "matching"],
    "suitable":      ["appropriate", "fitting", "apt"],
    "certain":       ["specific", "particular", "given"],
    "notable":       ["remarkable", "noteworthy", "prominent"],
    "relevant":      ["pertinent", "applicable", "germane"],
    "extensive":     ["comprehensive", "thorough", "wide-ranging"],
    "underlying":    ["foundational", "fundamental", "core"],
    "crucial":       ["vital", "critical", "indispensable"],
    "essential":     ["indispensable", "vital", "fundamental"],
    "rigorous":      ["systematic", "meticulous", "thorough"],

    # -- Adverbs --
    "typically":     ["generally", "commonly", "ordinarily"],
    "particularly":  ["especially", "notably", "specifically"],
    "commonly":      ["frequently", "often", "routinely"],
    "usually":       ["generally", "typically", "ordinarily"],
    "therefore":     ["consequently", "thus", "hence"],
    "however":       ["nevertheless", "nonetheless", "yet"],
    "moreover":      ["furthermore", "additionally", "besides"],
    "furthermore":   ["moreover", "additionally", "in addition"],
    "directly":      ["immediately", "straightforwardly", "explicitly"],
    "especially":    ["particularly", "notably", "chiefly"],
    "essentially":   ["fundamentally", "basically", "inherently"],
    "significantly": ["substantially", "considerably", "markedly"],
    "approximately": ["roughly", "nearly", "about"],
    "precisely":     ["exactly", "accurately", "rigorously"],
    "clearly":       ["evidently", "obviously", "manifestly"],
    "primarily":     ["mainly", "chiefly", "principally"],
    "subsequently":  ["afterward", "later", "then"],
    "effectively":   ["efficiently", "successfully", "competently"],
    "readily":       ["easily", "promptly", "swiftly"],
    "widely":        ["extensively", "broadly", "generally"],
    "briefly":       ["concisely", "succinctly", "in short"],
    "similarly":     ["likewise", "analogously", "in a comparable manner"],
    "consequently":  ["therefore", "thus", "as a result"],
    "alternatively": ["conversely", "on the other hand", "instead"],
}

DEFAULT_PHRASE_REWRITES = [
    # -- Common academic openers --
    ["\\bthis research paper\\b", "the present work"],
    ["\\bthis research\\b", "the current study"],
    ["\\bthis study\\b", "the present investigation"],
    ["\\bthis paper\\b", "the present work"],
    ["\\bthis work\\b", "the current investigation"],
    ["\\bin this paper\\b", "in the present work"],
    ["\\bin this study\\b", "in this investigation"],
    ["\\bin this chapter\\b", "within this chapter"],
    ["\\bin this section\\b", "within the current section"],
    ["\\bthe purpose of this\\b", "the objective of the present"],
    ["\\bthe aim of this\\b", "the goal of the current"],

    # -- Definitional phrases --
    ["\\bis defined as\\b", "is characterized as"],
    ["\\bis said to be\\b", "is classified as"],
    ["\\bis called\\b", "is referred to as"],
    ["\\bis known as\\b", "is recognized as"],
    ["\\bis given by\\b", "is expressed through"],
    ["\\bcan be written as\\b", "may be expressed as"],
    ["\\bcan be expressed as\\b", "may be stated as"],
    ["\\btakes the form\\b", "assumes the form"],
    ["\\bhas the form\\b", "assumes the structure"],
    ["\\bof the form\\b", "having the structure"],
    ["\\bin the form of\\b", "structured as"],

    # -- Causal / logical connectors --
    ["\\bin order to\\b", "so as to"],
    ["\\bdue to the fact that\\b", "because"],
    ["\\bdue to\\b", "owing to"],
    ["\\bbecause of\\b", "on account of"],
    ["\\bas a result of\\b", "as a consequence of"],
    ["\\bas a result\\b", "consequently"],
    ["\\bfor this reason\\b", "on this account"],
    ["\\bon the other hand\\b", "conversely"],
    ["\\bin contrast\\b", "by comparison"],
    ["\\bin addition to\\b", "alongside"],
    ["\\bin addition\\b", "additionally"],
    ["\\bas well as\\b", "together with"],
    ["\\bin terms of\\b", "with respect to"],
    ["\\bwith respect to\\b", "relative to"],
    ["\\baccording to\\b", "as stated by"],
    ["\\bbased on\\b", "grounded in"],

    # -- Importance / role phrases --
    ["\\bplays an important role\\b", "serves a pivotal function"],
    ["\\bplays a key role\\b", "fulfills a central function"],
    ["\\bplays a significant role\\b", "occupies a prominent position"],
    ["\\bplays a crucial role\\b", "holds a critical position"],
    ["\\bis of great importance\\b", "carries considerable significance"],
    ["\\bwidely used\\b", "extensively employed"],
    ["\\bwidely studied\\b", "the subject of extensive research"],
    ["\\bhas been widely\\b", "has been extensively"],
    ["\\bhas been extensively\\b", "has received substantial"],
    ["\\bhas attracted\\b", "has drawn"],

    # -- Descriptive phrases --
    ["\\ba large number of\\b", "numerous"],
    ["\\ba number of\\b", "several"],
    ["\\ba wide range of\\b", "a broad spectrum of"],
    ["\\ba wide variety of\\b", "a diverse assortment of"],
    ["\\bthe majority of\\b", "most of"],
    ["\\bin many cases\\b", "frequently"],
    ["\\bin most cases\\b", "predominantly"],
    ["\\bin some cases\\b", "occasionally"],
    ["\\bin the case of\\b", "for"],
    ["\\bin the context of\\b", "within the scope of"],
    ["\\bin the literature\\b", "in published research"],
    ["\\bin recent years\\b", "in the recent period"],

    # -- Process / method phrases --
    ["\\bfinite difference method\\b", "finite difference scheme"],
    ["\\bfinite difference methods\\b", "finite difference schemes"],
    ["\\bnumerical solution\\b", "computational solution"],
    ["\\bnumerical solutions\\b", "computational solutions"],
    ["\\bnumerical method\\b", "computational technique"],
    ["\\bnumerical methods\\b", "computational techniques"],
    ["\\bnumerical scheme\\b", "computational scheme"],
    ["\\bnumerical approximation\\b", "computational approximation"],
    ["\\bboundary conditions\\b", "boundary constraints"],
    ["\\binitial conditions\\b", "initial constraints"],
    ["\\bboundary value problem\\b", "boundary-constrained problem"],
    ["\\binitial value problem\\b", "initial-state problem"],

    # -- Result / conclusion phrases --
    ["\\bthe results show that\\b", "the findings indicate that"],
    ["\\bthe results indicate\\b", "the outcomes suggest"],
    ["\\bthe results demonstrate\\b", "the findings reveal"],
    ["\\bit can be seen that\\b", "it is evident that"],
    ["\\bit is clear that\\b", "it is apparent that"],
    ["\\bit is worth noting\\b", "it merits attention"],
    ["\\bit should be noted that\\b", "one should recognize that"],
    ["\\bit is important to note\\b", "it bears emphasis"],
    ["\\bit is well known that\\b", "it is widely acknowledged that"],
    ["\\bit has been shown that\\b", "it has been demonstrated that"],
    ["\\bit follows that\b", "one may infer that"],
    ["\\bwe can see that\\b", "one observes that"],
    ["\\bwe observe that\\b", "it is observed that"],
    ["\\bwe note that\\b", "it is noteworthy that"],
    ["\\bwe have\\b", "one has"],
    ["\\bwe get\\b", "one obtains"],
    ["\\bwe obtain\\b", "one derives"],
    ["\\bwe consider\\b", "one examines"],
    ["\\bwe need\\b", "it is necessary"],
    ["\\bwe assume\\b", "it is assumed"],

    # -- Transition phrases --
    ["\\bin the following\\b", "in what follows"],
    ["\\bas follows\\b", "in the following manner"],
    ["\\bas mentioned above\\b", "as previously noted"],
    ["\\bas discussed\\b", "as examined"],
    ["\\bas shown\\b", "as demonstrated"],
    ["\\bfor example\\b", "as an illustration"],
    ["\\bfor instance\\b", "to illustrate"],
    ["\\bthat is\\b", "namely"],
    ["\\bin other words\\b", "stated differently"],
    ["\\bon the basis of\\b", "drawing upon"],
    ["\\bfrom the above\\b", "from the preceding discussion"],
    ["\\bin the above\\b", "in the preceding"],
]

DEFAULT_PROTECTED_TERMS = [
    "Fourier's Law", "Fourier's law", "Newton's second law",
    "Newton's Second Law", "Taylor series", "Taylor expansion",
    "Taylor's theorem",
    "Black-Scholes", "Black--Scholes", "Black-Scholes-Merton",
    "Crank-Nicolson", "Crank--Nicolson",
    "Von Neumann", "von Neumann", "Von-Neumann",
    "Laplace", "Poisson", "Dirichlet", "Neumann",
    "Euler", "Runge-Kutta", "Gauss",
    "Ito's Lemma", "Ito's lemma",
    "Markov", "Wiener", "Brownian",
    "FTCS", "BTCS", "CFL",
    "MATLAB", "Python",
    "Air University", "Islamabad"
]

# ================================================================
# LOADER IMPLEMENTATION
# ================================================================

def load_rules():
    """
    Loads synonyms, phrase rewrites, and protected terms from rules/ folder.
    Creates default JSON files if they don't exist.
    """
    os.makedirs(RULES_DIR, exist_ok=True)
    
    synonyms_path = os.path.join(RULES_DIR, "synonyms.json")
    phrases_path = os.path.join(RULES_DIR, "phrases.json")
    protected_path = os.path.join(RULES_DIR, "protected_terms.json")

    # 1. Academic Synonyms
    if not os.path.exists(synonyms_path):
        with open(synonyms_path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_ACADEMIC_SYNONYMS, f, indent=2, ensure_ascii=False)
        synonyms = DEFAULT_ACADEMIC_SYNONYMS
    else:
        with open(synonyms_path, 'r', encoding='utf-8') as f:
            synonyms = json.load(f)

    # 2. Phrase Rewrites
    if not os.path.exists(phrases_path):
        with open(phrases_path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_PHRASE_REWRITES, f, indent=2, ensure_ascii=False)
        phrases = DEFAULT_PHRASE_REWRITES
    else:
        with open(phrases_path, 'r', encoding='utf-8') as f:
            phrases = json.load(f)
            
    # Convert list of lists back to list of tuples for regex engine
    phrases = [(item[0], item[1]) for item in phrases]

    # 3. Protected Terms
    if not os.path.exists(protected_path):
        with open(protected_path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_PROTECTED_TERMS, f, indent=2, ensure_ascii=False)
        protected_terms = set(DEFAULT_PROTECTED_TERMS)
    else:
        with open(protected_path, 'r', encoding='utf-8') as f:
            protected_list = json.load(f)
            protected_terms = set(protected_list)

    return synonyms, phrases, protected_terms

# Load them immediately on import
ACADEMIC_SYNONYMS, PHRASE_REWRITES, PROTECTED_TERMS = load_rules()
