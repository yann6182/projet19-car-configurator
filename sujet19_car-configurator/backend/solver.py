from typing import Dict, List, Tuple, Optional, Set
from ortools.sat.python import cp_model


# -----------------------
# Définition du domaine
# -----------------------

VARIABLES = {
    "model": ["compact", "suv", "sport_gt", "luxury_sedan"],
    "engine": ["petrol_1_6", "petrol_2_0t", "diesel_2_0", "hybrid_2_0", "electric_lr"],
    "transmission": ["manual", "auto8"],
    "drivetrain": ["fwd", "rwd", "awd"],
    "color": ["white", "black", "red", "blue", "silver"],
    "interior": ["cloth", "leather", "alcantara"],
    "pack": ["none", "tech", "premium", "offroad", "performance"],
}

# Description lisible pour l'UI
LABELS = {
    "model": {
        "compact": "Compact Urbain",
        "suv": "SUV Trail",
        "sport_gt": "Coupé GT",
        "luxury_sedan": "Berline Luxe",
    },
    "engine": {
        "petrol_1_6": "Essence 1.6L",
        "petrol_2_0t": "Essence 2.0L Turbo",
        "diesel_2_0": "Diesel 2.0L",
        "hybrid_2_0": "Hybride 2.0L",
        "electric_lr": "Électrique Long Range",
    },
    "transmission": {
        "manual": "Manuelle 6 rapports",
        "auto8": "Auto 8 rapports",
    },
    "drivetrain": {
        "fwd": "Traction (FWD)",
        "rwd": "Propulsion (RWD)",
        "awd": "Transmission intégrale (AWD)",
    },
    "color": {
        "white": "Blanc Nacré",
        "black": "Noir Onyx",
        "red": "Rouge Carmin",
        "blue": "Bleu Horizon",
        "silver": "Gris Argent",
    },
    "interior": {
        "cloth": "Tissu",
        "leather": "Cuir",
        "alcantara": "Alcantara",
    },
    "pack": {
        "none": "Aucun pack",
        "tech": "Pack Tech",
        "premium": "Pack Premium",
        "offroad": "Pack Offroad",
        "performance": "Pack Performance",
    },
}


def build_index_maps():
    idx = {}
    for var, values in VARIABLES.items():
        idx[var] = {v: i for i, v in enumerate(values)}
    return idx


INDEX = build_index_maps()


def _build_model(assignments: Dict[str, Optional[str]]) -> Tuple[cp_model.CpModel, Dict[str, cp_model.IntVar]]:
    model = cp_model.CpModel()
    vars_int = {}

    # Création des variables CP-SAT (un IntVar par dimension)
    for var_name, domain in VARIABLES.items():
        vars_int[var_name] = model.NewIntVar(0, len(domain) - 1, var_name)

    # Affectations partielles
    for var_name, value in assignments.items():
        if value is None or value == "":
            continue
        if var_name not in VARIABLES:
            continue
        if value not in INDEX[var_name]:
            continue
        model.Add(vars_int[var_name] == INDEX[var_name][value])

    # -------------------------
    # Contraintes métier
    # -------------------------

    m = vars_int["model"]
    e = vars_int["engine"]
    t = vars_int["transmission"]
    d = vars_int["drivetrain"]
    c = vars_int["color"]
    i = vars_int["interior"]
    p = vars_int["pack"]

    # Raccourcis pour indices
    M = INDEX["model"]
    E = INDEX["engine"]
    T = INDEX["transmission"]
    D = INDEX["drivetrain"]
    C = INDEX["color"]
    I = INDEX["interior"]
    P = INDEX["pack"]

    # -------------------------
    # Règles métier réalistes
    # -------------------------

    # Compact : moteur 1.6/2.0t/hybride, pas AWD, pas Alcantara, pas offroad/performance
    model.AddForbiddenAssignments(
        [m, e],
        [
            (M["compact"], E["diesel_2_0"]),
            (M["compact"], E["electric_lr"]),
        ],
    )
    model.AddForbiddenAssignments([m, d], [(M["compact"], D["awd"])])
    model.AddForbiddenAssignments([m, i], [(M["compact"], I["alcantara"])])
    model.AddForbiddenAssignments([m, p], [(M["compact"], P["offroad"]), (M["compact"], P["performance"])])
    # Hybride compact uniquement en auto
    model.AddForbiddenAssignments([m, e, t], [(M["compact"], E["hybrid_2_0"], T["manual"])])

    # SUV : auto obligatoire, moteurs 2.0t / diesel / hybrid, pas performance
    model.AddForbiddenAssignments([m, t], [(M["suv"], T["manual"])])
    model.AddForbiddenAssignments([m, e], [(M["suv"], E["petrol_1_6"])])
    model.AddForbiddenAssignments([m, p], [(M["suv"], P["performance"])])
    # Offroad uniquement pour SUV et nécessite AWD
    model.AddForbiddenAssignments([p, m], [(P["offroad"], M["compact"]), (P["offroad"], M["sport_gt"]), (P["offroad"], M["luxury_sedan"])])
    model.AddForbiddenAssignments([p, d], [(P["offroad"], D["fwd"]), (P["offroad"], D["rwd"])])

    # Sport GT : auto, RWD/AWD, moteurs 2.0t ou électrique, pas cloth, pas offroad, au moins Tech
    model.AddForbiddenAssignments([m, t], [(M["sport_gt"], T["manual"])])
    model.AddForbiddenAssignments([m, d], [(M["sport_gt"], D["fwd"])])
    model.AddForbiddenAssignments([m, i], [(M["sport_gt"], I["cloth"])])
    model.AddForbiddenAssignments([m, p], [(M["sport_gt"], P["none"]), (M["sport_gt"], P["offroad"])])
    model.AddForbiddenAssignments(
        [m, e],
        [
            (M["sport_gt"], E["petrol_1_6"]),
            (M["sport_gt"], E["diesel_2_0"]),
            (M["sport_gt"], E["hybrid_2_0"]),
        ],
    )

    # Luxury Sedan : auto, RWD/AWD, moteurs 2.0t/hybride/électrique, pas cloth, pack >= Tech, pas offroad/performance
    model.AddForbiddenAssignments([m, t], [(M["luxury_sedan"], T["manual"])])
    model.AddForbiddenAssignments([m, d], [(M["luxury_sedan"], D["fwd"])])
    model.AddForbiddenAssignments([m, i], [(M["luxury_sedan"], I["cloth"])])
    model.AddForbiddenAssignments(
        [m, e],
        [
            (M["luxury_sedan"], E["petrol_1_6"]),
            (M["luxury_sedan"], E["diesel_2_0"]),
        ],
    )
    model.AddForbiddenAssignments([m, p], [(M["luxury_sedan"], P["none"]), (M["luxury_sedan"], P["offroad"]), (M["luxury_sedan"], P["performance"])])

    # Electric LR : auto, AWD, pas cloth, pas offroad/performance, seulement GT ou Luxury
    model.AddForbiddenAssignments([e, t], [(E["electric_lr"], T["manual"])])
    model.AddForbiddenAssignments([e, d], [(E["electric_lr"], D["fwd"]), (E["electric_lr"], D["rwd"])])
    model.AddForbiddenAssignments([e, i], [(E["electric_lr"], I["cloth"])])
    model.AddForbiddenAssignments([e, p], [(E["electric_lr"], P["offroad"]), (E["electric_lr"], P["performance"])])
    model.AddForbiddenAssignments(
        [m, e],
        [
            (M["compact"], E["electric_lr"]),
            (M["suv"], E["electric_lr"]),
        ],
    )

    # Petrol 1.6 : uniquement sur compact
    model.AddForbiddenAssignments(
        [m, e],
        [
            (M["suv"], E["petrol_1_6"]),
            (M["sport_gt"], E["petrol_1_6"]),
            (M["luxury_sedan"], E["petrol_1_6"]),
        ],
    )

    # Diesel : pas sur GT ni Luxury
    model.AddForbiddenAssignments([m, e], [(M["sport_gt"], E["diesel_2_0"]), (M["luxury_sedan"], E["diesel_2_0"])])

    # AWD toujours en auto8
    model.AddForbiddenAssignments([d, t], [(D["awd"], T["manual"])])

    # Premium requiert auto8
    model.AddForbiddenAssignments([p, t], [(P["premium"], T["manual"])])

    # Performance uniquement sur Sport GT et auto8
    model.AddForbiddenAssignments([p, m], [(P["performance"], M["compact"]), (P["performance"], M["suv"]), (P["performance"], M["luxury_sedan"])])
    model.AddForbiddenAssignments([p, t], [(P["performance"], T["manual"])])

    # Tech requis pour Sport GT et Luxury
    model.AddForbiddenAssignments([m, p], [(M["sport_gt"], P["none"]), (M["luxury_sedan"], P["none"])])

    # Couleur rouge non disponible pour Luxury
    model.AddForbiddenAssignments([m, c], [(M["luxury_sedan"], C["red"])])

    return model, vars_int


class DomainCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables: Dict[str, cp_model.IntVar]):
        super().__init__()
        self._vars = variables
        self.domains: Dict[str, Set[int]] = {name: set() for name in variables}

    def on_solution_callback(self):
        for name, var in self._vars.items():
            self.domains[name].add(self.Value(var))


def propagate_domains(assignments: Dict[str, Optional[str]]):
    """
    Retourne, pour chaque variable, l'ensemble des valeurs encore possibles
    en tenant compte des contraintes ET des affectations partielles.
    """
    model, vars_int = _build_model(assignments)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0
    solver.parameters.num_search_workers = 8

    # Pour chaque variable et chaque valeur possible, on teste s'il existe
    # au moins une solution complète en ajoutant la contrainte var == value.
    # C'est plus simple et robuste que SearchForAllSolutions pour obtenir
    # les domaines accessibles (taille du problème très réduite ici).
    domains: Dict[str, List[str]] = {name: [] for name in VARIABLES}
    is_consistent = False

    for var_name, values in VARIABLES.items():
        for idx in range(len(values)):
            # Reconstruire un modèle propre pour chaque test
            test_model, test_vars = _build_model(assignments)
            test_model.Add(test_vars[var_name] == idx)

            test_solver = cp_model.CpSolver()
            test_solver.parameters.max_time_in_seconds = 0.5
            test_solver.parameters.num_search_workers = 8

            status = test_solver.Solve(test_model)
            if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                domains[var_name].append(values[idx])
                is_consistent = True

    return domains, is_consistent


def solve_configuration(assignments: Dict[str, Optional[str]]):
    """
    Tente de trouver une configuration complète compatible avec les choix partiels.
    """
    model, vars_int = _build_model(assignments)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, "INFEASIBLE"

    # Récupération d'une solution
    result: Dict[str, str] = {}
    for var_name, var in vars_int.items():
        idx = solver.Value(var)
        result[var_name] = VARIABLES[var_name][idx]

    return result, "FEASIBLE"
