import math
from flask import Flask, request, jsonify
from flask_cors import CORS # Pour autoriser les requêtes depuis votre HTML local

# --- Initialisation de Flask ---
app = Flask(__name__)
CORS(app) # Active CORS pour toutes les routes

# --- Logique de jeu (copiée de votre code) ---
SCORES = {
    'IA': 10,
    'HUMAIN': -10,
    'NUL': 0
}
HUMAIN = 'X'
IA = 'O'

# --- Fonctions utilitaires (inchangées) ---

def get_cases_vides(board):
    cases = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                cases.append((i, j))
    return cases

def est_victoire(board, joueur):
    for i in range(3):
        if all(board[i][j] == joueur for j in range(3)):
            return True
    for j in range(3):
        if all(board[i][j] == joueur for i in range(3)):
            return True
    if board[0][0] == joueur and board[1][1] == joueur and board[2][2] == joueur:
        return True
    if board[0][2] == joueur and board[1][1] == joueur and board[2][0] == joueur:
        return True
    return False

def est_match_nul(board):
    return not est_victoire(board, HUMAIN) and not est_victoire(board, IA) and len(get_cases_vides(board)) == 0

def verifier_etat_jeu(board):
    if est_victoire(board, IA):
        return 'IA'
    elif est_victoire(board, HUMAIN):
        return 'HUMAIN'
    elif est_match_nul(board):
        return 'NUL'
    else:
        return None

# --- L'IA (Algorithme Minimax, inchangé) ---

def minimax(board, profondeur, est_tour_maximiseur):
    etat = verifier_etat_jeu(board)
    if etat is not None:
        return SCORES[etat]

    if est_tour_maximiseur:
        meilleur_score = -math.inf
        for (ligne, col) in get_cases_vides(board):
            board[ligne][col] = IA
            score = minimax(board, profondeur + 1, False)
            board[ligne][col] = ' '
            meilleur_score = max(score, meilleur_score)
        return meilleur_score
    else:
        meilleur_score = math.inf
        for (ligne, col) in get_cases_vides(board):
            board[ligne][col] = HUMAIN
            score = minimax(board, profondeur + 1, True)
            board[ligne][col] = ' '
            meilleur_score = min(score, meilleur_score)
        return meilleur_score

def trouver_meilleur_coup(board):
    meilleur_score = -math.inf
    meilleur_coup = None

    for (ligne, col) in get_cases_vides(board):
        board[ligne][col] = IA
        score_du_coup = minimax(board, 0, False)
        board[ligne][col] = ' '
        
        if score_du_coup > meilleur_score:
            meilleur_score = score_du_coup
            meilleur_coup = (ligne, col)
            
    return meilleur_coup

# --- La route API (le "modèle" que le site web va appeler) ---

@app.route('/api/play', methods=['POST'])
def api_play():
    try:
        # 1. Recevoir le plateau de jeu actuel depuis le site web
        data = request.json
        board = data.get('board')

        if not board:
            return jsonify({'error': 'Plateau non fourni'}), 400

        # 2. Vérifier si le jeu n'est pas déjà fini (au cas où)
        etat_initial = verifier_etat_jeu(board)
        if etat_initial is not None:
            return jsonify({'status': etat_initial, 'move': None})

        # 3. Demander à l'IA de trouver le meilleur coup
        (ligne, col) = trouver_meilleur_coup(board)
        
        # 4. Appliquer le coup de l'IA
        board[ligne][col] = IA
        
        # 5. Vérifier le nouvel état du jeu
        etat_final = verifier_etat_jeu(board)
        
        # 6. Renvoyer le coup de l'IA et l'état du jeu au site web
        return jsonify({
            'status': etat_final, # 'IA', 'NUL', ou None
            'move': (ligne, col)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Lancement du serveur Flask ---
if __name__ == "__main__":
    app.run(debug=True) # Lance le serveur local (généralement sur http://127.0.0.1:5000)