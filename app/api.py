from flask import Flask, request, jsonify
from app.main import build_graph    
from app.state.state import initial_state, InitialState