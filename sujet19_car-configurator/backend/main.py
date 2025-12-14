from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

from solver import propagate_domains, solve_configuration

app = FastAPI(title="Car Configurator CSP API")

# CORS pour permettre l'accès depuis le front (localhost:5173, 3000, file://, etc.)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "null",  # file:// origin quand on ouvre index.html directement
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConfigRequest(BaseModel):
    assignments: Dict[str, Optional[str]]


class PropagationResponse(BaseModel):
    domains: Dict[str, List[str]]
    valid: bool


class SolveResponse(BaseModel):
    configuration: Optional[Dict[str, str]]
    status: str


@app.get("/")
def root():
    return {"message": "Car Configurator API is running"}


@app.post("/propagate", response_model=PropagationResponse)
def api_propagate(req: ConfigRequest) -> Any:
    """
    Prend des affectations partielles et renvoie,
    pour chaque variable, les valeurs encore possibles.
    """
    domains, is_consistent = propagate_domains(req.assignments)
    return {"domains": domains, "valid": is_consistent}


@app.post("/solve", response_model=SolveResponse)
def api_solve(req: ConfigRequest) -> Any:
    """
    Tente de compléter la configuration à partir des choix partiels.
    """
    config, status = solve_configuration(req.assignments)
    return {"configuration": config, "status": status}


@app.get("/ping")
def ping() -> Dict[str, str]:
    return {"message": "Car Configurator API is running"}

