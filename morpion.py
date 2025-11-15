import math
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

HUMAIN = 'X'
IA = 'O'
SCORES = {'IA': 10, 'HUMAIN': -10, 'NUL': 0}

def get_cases_vides(board):
    return [(i,j) for i in range(3) for j in range(3) if board[i][j] == ' ']

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

def minimax(board, profondeur, est_max):
    etat = verifier_etat_jeu(board)
    if etat is not None:
        return SCORES[etat]
    if est_max:
        meilleur = -math.inf
        for i,j in get_cases_vides(board):
            board[i][j] = IA
            score = minimax(board, profondeur+1, False)
            board[i][j] = ' '
            meilleur = max(score, meilleur)
        return meilleur
    else:
        meilleur = math.inf
        for i,j in get_cases_vides(board):
            board[i][j] = HUMAIN
            score = minimax(board, profondeur+1, True)
            board[i][j] = ' '
            meilleur = min(score, meilleur)
        return meilleur

def trouver_meilleur_coup(board):
    meilleur_score = -math.inf
    meilleur_coup = None
    for i,j in get_cases_vides(board):
        board[i][j] = IA
        score = minimax(board, 0, False)
        board[i][j] = ' '
        if score > meilleur_score:
            meilleur_score = score
            meilleur_coup = (i,j)
    return meilleur_coup

@app.route('/api/play', methods=['POST'])
def api_play():
    try:
        data = request.json
        board = data.get('board')
        if not board:
            return jsonify({'error': 'Plateau non fourni'}), 400

        etat = verifier_etat_jeu(board)
        if etat:
            return jsonify({'status': etat, 'move': None})

        coup = trouver_meilleur_coup(board)
        if coup:
            i,j = coup
            board[i][j] = IA
            etat = verifier_etat_jeu(board)
            return jsonify({'status': etat, 'move': [i,j]})
        else:
            return jsonify({'status': 'NUL', 'move': None})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- Lancement du serveur Flask ---
if __name__ == "__main__":
    app.run(debug=True) # Lance le serveur local (généralement sur http://127.0.0.1:5000)
