import subprocess
import os
from pathlib import Path

# On repère où est le dossier Java par rapport à ce script
current_dir = Path(__file__).parent
solver_dir = current_dir / "tweety_solver"
jar_path = solver_dir / "libs" / "tweety.jar"

def solve_debate(arguments_json):
    """
    Reçoit une liste d'arguments (format JSON), génère la string pour Java,
    et retourne les gagnants.
    """
    
    # 1. Convertir le JSON en format compréhensible par notre Java
    # Format : arg(id),arg(id2),att(id2:id1)
    
    java_instructions = []
    
    # D'abord on déclare tous les arguments
    for arg in arguments_json:
        # On nettoie les ID pour éviter les bugs (pas d'espace)
        clean_id = str(arg['id']).replace(" ", "_")
        java_instructions.append(f"arg({clean_id})")
        
    # Ensuite on déclare les attaques
    for arg in arguments_json:
        if arg['relation'] == 'attack' and arg['target_id']:
            attacker = str(arg['id']).replace(" ", "_")
            target = str(arg['target_id']).replace(" ", "_")
            java_instructions.append(f"att({attacker}:{target})")

    # On joint tout par des virgules
    input_string = ",".join(java_instructions)
    
    print(f"DEBUG - Envoi à Java : {input_string}")

    # 2. Appeler Java via subprocess
    # Commande : java -cp "libs/tweety.jar;." DebateSolver "arg(a),..."
    
    # Attention au séparateur de classpath (; pour Windows, : pour Mac/Linux)
    classpath_sep = ";" if os.name == 'nt' else ":"
    classpath = f"{jar_path}{classpath_sep}."

    try:
        result = subprocess.run(
            ["java", "-cp", classpath, "DebateSolver", input_string],
            cwd=solver_dir, # On se place dans le dossier Java pour exécuter
            capture_output=True,
            text=True,
            check=True
        )
        
        # 3. Analyser la réponse de Java
        output = result.stdout.strip()
        print(f"DEBUG - Réponse Java brute : {output}")
        
        # On cherche la ligne qui commence par GAGNANTS:
        for line in output.split("\n"):
            if line.startswith("GAGNANTS:"):
                # GAGNANTS:{arg1, arg2} -> on enlève le préfixe et les accolades
                raw_list = line.replace("GAGNANTS:", "").replace("{", "").replace("}", "")
                
                # On sépare par virgule et on nettoie les espaces
                winners = [w.strip() for w in raw_list.split(",") if w.strip()]
                return winners
                
        return []

    except subprocess.CalledProcessError as e:
        print(f"Erreur Java : {e.stderr}")
        return []

# --- TEST ---
if __name__ == "__main__":
    # Simulation de données que le LLM t'aurait envoyé
    mock_data = [
        {"id": "A", "content": "Il fait beau", "relation": "none", "target_id": None},
        {"id": "B", "content": "Il pleut", "relation": "attack", "target_id": "A"},
        {"id": "C", "content": "Météo France dit soleil", "relation": "attack", "target_id": "B"}
    ]
    
    print("Calcul des gagnants...")
    gagnants = solve_debate(mock_data)
    print(f"✅ Les arguments gagnants sont : {gagnants}")