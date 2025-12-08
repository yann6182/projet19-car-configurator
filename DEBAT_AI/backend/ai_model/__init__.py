from .argument_mining import analyze_input as analyze_argument
# Ajout de l'import de la nouvelle fonction
from .argument_mining import generate_suggestions 
from .logic_bridge import solve_debate

__all__ = ["analyze_argument", "solve_debate", "generate_suggestions"]