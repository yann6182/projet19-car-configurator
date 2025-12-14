import os
import asyncpg
import json
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

# --- IMPORT DE TON MODULE IA ---
from ai_model import analyze_argument, solve_debate, generate_suggestions

# Load environment variables
load_dotenv()

# --- Database Setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db/debatai")
if not DATABASE_URL:
    print(" WARNING: DATABASE_URL n'est pas définie dans le .env")
pool = None

async def get_pool():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(DATABASE_URL)
    return pool

# --- Pydantic Models ---
class User(BaseModel):
    id: int
    username: str

class Debate(BaseModel):
    id: int
    topic: str

class Message(BaseModel):
    id: int
    content: str
    user_id: int
    debate_id: int
    username: str # Joined from users table
    created_at: Any = None # Pour gérer le timestamp

    # Nouveaux champs IA (Optionnels pour éviter les bugs si null)
    arg_type: Optional[str] = "claim"
    relation_type: Optional[str] = "none"
    target_id: Optional[int] = None
    feedback: Optional[str] = None
    # Champ spécial pour envoyer les gagnants au Frontend
    current_winners: Optional[List[str]] = []
    session_id: Optional[str] = None

class MessageIn(BaseModel):
    content: str
    username: str
    session_id: str # We'll use username to find/create user

# --- WebSocket Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, debate_id: int):
        await websocket.accept()
        if debate_id not in self.active_connections:
            self.active_connections[debate_id] = []
        self.active_connections[debate_id].append(websocket)

    def disconnect(self, websocket: WebSocket, debate_id: int):
        if debate_id in self.active_connections:
            self.active_connections[debate_id].remove(websocket)

    async def broadcast(self, message: dict, debate_id: int):
        if debate_id in self.active_connections:
            for connection in self.active_connections[debate_id]:
                await connection.send_text(json.dumps(message, default=str))

manager = ConnectionManager()

# --- FastAPI App ---
app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup():
    await get_pool()

@app.on_event("shutdown")
async def shutdown():
    global pool
    if pool:
        await pool.close()

# --- API Endpoints ---
@app.get("/api/debates", response_model=List[Debate])
async def get_debates():
    db_pool = await get_pool()
    async with db_pool.acquire() as connection:
        rows = await connection.fetch("SELECT id, topic FROM debates ORDER BY created_at DESC")
        return [Debate(id=row['id'], topic=row['topic']) for row in rows]

@app.get("/api/debates/{debate_id}/messages", response_model=List[Message])
async def get_messages(debate_id: int, session_id: str):
    db_pool = await get_pool()
    async with db_pool.acquire() as connection:
        # 1. On récupère les messages de la session
        rows = await connection.fetch(
            """
            SELECT m.id, m.content, m.user_id, m.debate_id, m.created_at, 
                   m.arg_type, m.relation_type, m.target_id, m.feedback, m.session_id, u.username
            FROM messages m
            JOIN users u ON m.user_id = u.id
            WHERE m.debate_id = $1 AND m.session_id = $2
            ORDER BY m.created_at ASC
            """,
            debate_id, session_id
        )
        
        # Astuce : On convertit les résultats SQL en dictionnaires Python modifiables
        results = [dict(row) for row in rows]

        # 2. SI on a des messages, on doit recalculer les gagnants TOUT DE SUITE
        if results:
            # On prépare les données pour Tweety
            debate_data = [
                {
                    "id": r["id"], 
                    "arg_type": r["arg_type"], 
                    "relation": r["relation_type"], 
                    "target_id": r["target_id"]
                } 
                for r in results
            ]
            
            # On appelle Java
            winning_ids = solve_debate(debate_data)
            
            # On injecte la liste des gagnants dans CHAQUE message renvoyé
            # (Comme ça le frontend pourra lire l'info sur n'importe quel message)
            for msg in results:
                msg['current_winners'] = winning_ids

        return [Message(**row) for row in results]

@app.post("/api/debates/{debate_id}/messages", response_model=Message)
async def create_message(debate_id: int, message_in: MessageIn):
    db_pool = await get_pool()
    
    # 1. Récupérer le contexte pour l'IA (Filtré par SESSION_ID)
    # On ne veut pas que l'IA lise les messages d'un autre match (Alice vs Charlie)
    async with db_pool.acquire() as connection:
        history_rows = await connection.fetch("""
            SELECT id, content, arg_type FROM messages 
            WHERE debate_id = $1 AND session_id = $2
            ORDER BY created_at DESC LIMIT 10
        """, debate_id, message_in.session_id)
        
        history_context = [{"id": str(r['id']), "content": r['content'], "type": r['arg_type']} for r in history_rows]

    # 2. Appel à ton module IA (Argument Mining) - Inchangé
    print(f"🤖 Analyse IA du message : {message_in.content}")
    try:
        ai_analysis = analyze_argument(message_in.content, history_context)
    except Exception as e:
        print(f"⚠️ Erreur IA: {e}")
        ai_analysis = {}

    # Extraction des valeurs
    arg_type = ai_analysis.get('type', 'claim')
    relation = ai_analysis.get('relation', 'none')
    target_id = ai_analysis.get('target_id')
    feedback = ai_analysis.get('feedback')

    if not isinstance(target_id, int):
        target_id = None

    async with db_pool.acquire() as connection:
        async with connection.transaction():
            # Gestion User - Inchangé
            user = await connection.fetchrow("SELECT id FROM users WHERE username = $1", message_in.username)
            if user:
                user_id = user['id']
            else:
                user_id = await connection.fetchval("INSERT INTO users (username) VALUES ($1) RETURNING id", message_in.username)

            # 3. Insertion en Base de Données (AVEC SESSION_ID)
            row = await connection.fetchrow(
                """
                INSERT INTO messages (content, user_id, debate_id, arg_type, relation_type, target_id, feedback, session_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id, content, user_id, debate_id, created_at, arg_type, relation_type, target_id, feedback, session_id
                """,
                message_in.content, user_id, debate_id, arg_type, relation, target_id, feedback, message_in.session_id
            )

            # 4. Calcul Logique (Tweety) - Filtré par SESSION_ID
            # On ne veut calculer le graphe que pour ce match spécifique
            all_messages = await connection.fetch("""
                SELECT id, arg_type, relation_type as relation, target_id 
                FROM messages WHERE debate_id = $1 AND session_id = $2
            """, debate_id, message_in.session_id)
            
            debate_data = [dict(m) for m in all_messages]
            
            print("🧠 Calcul des gagnants avec Java...")
            winning_ids = solve_debate(debate_data)
            print(f"🏆 Gagnants actuels : {winning_ids}")

            # 5. Préparation de la réponse
            response_dict = dict(row)
            response_dict['username'] = message_in.username
            response_dict['current_winners'] = winning_ids

            # 6. Diffusion WebSocket
            # Le frontend filtrera les messages qui ne concernent pas sa session
            await manager.broadcast(response_dict, debate_id)
            
            return Message(**response_dict)

@app.websocket("/ws/debates/{debate_id}")
async def websocket_endpoint(websocket: WebSocket, debate_id: int):
    await manager.connect(websocket, debate_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, debate_id)

@app.get("/api/debates/{debate_id}/suggestions/{target_message_id}")
async def get_suggestions(debate_id: int, target_message_id: int):
    """
    Génère 3 idées de contre-arguments pour attaquer un message spécifique.
    """
    db_pool = await get_pool()
    async with db_pool.acquire() as connection:
        # 1. On récupère le message qu'on veut attaquer
        target_msg = await connection.fetchrow(
            "SELECT content FROM messages WHERE id = $1", target_message_id
        )
        if not target_msg:
            return {"error": "Message introuvable"}

        # 2. On récupère un peu de contexte global
        context_rows = await connection.fetch(
            "SELECT content FROM messages WHERE debate_id = $1 ORDER BY created_at DESC LIMIT 5", 
            debate_id
        )
        context_text = "\n".join([r['content'] for r in context_rows])

        # 3. On appelle ton IA
        suggestions = generate_suggestions(target_msg['content'], context_text)
        
        return {"suggestions": suggestions}

@app.get("/")
def read_root():
    return {"status": "Backend is running"}

@app.delete("/api/debates/{debate_id}/messages")
async def reset_debate(debate_id: int, session_id: str): # <-- Besoin du session_id
    db_pool = await get_pool()
    async with db_pool.acquire() as connection:
        # On ne supprime QUE ce match là
        await connection.execute(
            "DELETE FROM messages WHERE debate_id = $1 AND session_id = $2", 
            debate_id, session_id
        )
    return {"status": "Match reset successfully"}