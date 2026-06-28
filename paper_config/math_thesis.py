import os
from collections import OrderedDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Project Information
PROJECT_NAME = "math_thesis"

# Input paths
INPUT_DIR = os.path.join(BASE_DIR, "paper_input", "Mathematics-thesis")
TEX_FILE = os.path.join(INPUT_DIR, "main.tex")
BIB_FILE = os.path.join(INPUT_DIR, "references.bib")

# Output path (separate folder)
OUTPUT_DIR = os.path.join(BASE_DIR, "Mathematics-thesis-modified")

# Execution configurations
SYNONYM_AGGRESSIVENESS = 0.55
RANDOM_SEED = 42
MIN_SENTENCE_LENGTH_FOR_CITE = 60

# Topic-based citation mapping for this mathematics thesis
# Format: (tuple of keywords) -> {"key": bibkey, "topic": human_readable_topic}
TOPIC_CITATIONS = OrderedDict([
    (("heat equation", "thermal", "conduction", "fourier", "diffusion equation", "temperature"),
     {"key": "ref_thermal_modeling", "topic": "Heat Conduction and Thermal Diffusion Modeling"}),

    (("wave equation", "vibration", "membrane", "propagation", "elastic", "wave motion"),
     {"key": "ref_wave_propagation", "topic": "Wave Propagation and Vibration Analysis"}),

    (("black-scholes", "black--scholes", "option pricing", "financial derivative", "stochastic"),
     {"key": "ref_option_pricing", "topic": "Option Pricing and Financial Derivative Models"}),

    (("laplace equation", "steady state", "steady-state", "harmonic", "potential"),
     {"key": "ref_laplace_harmonic", "topic": "Laplace Equation and Harmonic Analysis"}),

    (("finite difference", "discretization", "grid", "mesh", "fdm", "difference scheme"),
     {"key": "ref_fdm_schemes", "topic": "Finite Difference Discretization Schemes"}),

    (("stability", "von neumann", "stable", "unstable", "cfl"),
     {"key": "ref_numerical_stability", "topic": "Numerical Stability Analysis of Difference Schemes"}),

    (("convergence", "truncation error", "consistency", "lax equivalence"),
     {"key": "ref_convergence_analysis", "topic": "Convergence and Consistency of Numerical Methods"}),

    (("crank-nicolson", "crank--nicolson", "implicit scheme", "implicit method"),
     {"key": "ref_crank_nicolson", "topic": "Crank--Nicolson Implicit Discretization"}),

    (("explicit method", "explicit scheme", "ftcs", "forward time"),
     {"key": "ref_explicit_methods", "topic": "Explicit Time-Stepping Methods for PDEs"}),

    (("lax method", "lax scheme", "lax-wendroff"),
     {"key": "ref_lax_methods", "topic": "Lax-Type Finite Difference Schemes"}),

    (("leapfrog", "staggered", "leap-frog"),
     {"key": "ref_leapfrog_scheme", "topic": "Leapfrog and Staggered Grid Methods"}),

    (("advection", "transport equation", "convection"),
     {"key": "ref_advection_transport", "topic": "Advection and Transport Equation Methods"}),

    (("partial differential equation", "pde", "second order", "second-order", "classification"),
     {"key": "ref_pde_theory", "topic": "Theory and Classification of Partial Differential Equations"}),

    (("ordinary differential equation", "ode", "first order", "initial value"),
     {"key": "ref_ode_fundamentals", "topic": "Fundamentals of Ordinary Differential Equations"}),

    (("elliptic", "parabolic", "hyperbolic", "discriminant"),
     {"key": "ref_pde_classification", "topic": "Classification of Second-Order PDEs"}),

    (("taylor series", "taylor expansion", "taylor"),
     {"key": "ref_taylor_approx", "topic": "Taylor Series Approximation Methods"}),

    (("boundary value", "dirichlet", "neumann", "boundary condition"),
     {"key": "ref_boundary_problems", "topic": "Boundary Value Problems for Differential Equations"}),

    (("newton", "leibniz", "calculus", "history"),
     {"key": "ref_calculus_history", "topic": "Historical Development of Calculus and Differential Equations"}),

    (("stochastic calculus", "ito", "brownian motion", "wiener process"),
     {"key": "ref_stochastic_calc", "topic": "Stochastic Calculus and Its Lemma"}),

    (("matrix", "tridiagonal", "linear system", "linear algebra"),
     {"key": "ref_linear_algebra", "topic": "Matrix Methods for Linear Systems"}),

    (("numerical simulation", "computational", "algorithm", "implementation"),
     {"key": "ref_computational_methods", "topic": "Computational Methods and Algorithm Implementation"}),

    (("engineering", "applied mathematics", "mathematical modeling", "physical"),
     {"key": "ref_applied_math", "topic": "Applied Mathematics in Engineering and Physical Sciences"}),

    (("quantitative finance", "financial mathematics", "risk", "portfolio"),
     {"key": "ref_quant_finance", "topic": "Quantitative Finance and Mathematical Risk Modeling"}),

    (("conservation", "energy balance", "conservation law"),
     {"key": "ref_conservation_laws", "topic": "Conservation Laws and Energy Balance Principles"}),

    (("payoff", "call option", "put option", "european option", "american option"),
     {"key": "ref_option_payoffs", "topic": "Option Payoff Structures and Strategies"}),

    (("volatility", "drift", "diffusion coefficient"),
     {"key": "ref_volatility_models", "topic": "Volatility and Diffusion Coefficient Modeling"}),
])
