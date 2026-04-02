"""
REST API wrapper for IIITH Mess MCP Server
Bridge between MCP server and Siri Shortcuts / external integrations

Usage:
    python api_wrapper.py

Then from Siri Shortcut, make HTTP requests to http://localhost:5000/api/...
"""

import os
import asyncio
from typing import Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import MCP tools
from iiith_mess_mcp.server import (
    mess_get_registrations,
    mess_create_registration,
    mess_cancel_registration,
    mess_get_menus,
    mess_get_info,
    mess_get_me,
    mess_login_msit,
    GetRegistrationsInput,
    CreateRegistrationInput,
    MealDateTypeInput,
    MsitLoginInput,
)

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests (needed for Siri Shortcuts)

# Store active session for current user
current_session = {}

# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────

def run_async(coro):
    """Run async MCP function in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def get_auth_context():
    """Get auth_key from env or session from current_session"""
    auth_key = os.environ.get("MESS_AUTH_KEY")
    session = current_session.get("session")
    return {"auth_key": auth_key, "session": session}


# ─────────────────────────────────────────────
# Authentication Endpoints
# ─────────────────────────────────────────────

@app.route("/api/auth/login", methods=["POST"])
def login_msit():
    """
    Login with MSIT credentials
    
    Request body:
    {
        "user": "email@msitprogram.net",
        "password": "your_password"
    }
    
    Response: User info + session cookie
    """
    try:
        data = request.get_json()
        user = data.get("user")
        password = data.get("password")
        
        if not user or not password:
            return jsonify({"error": "Missing user or password"}), 400
        
        params = MsitLoginInput(user=user, password=password)
        result = run_async(mess_login_msit(params))
        
        # Store session if successful
        if isinstance(result, dict) and "session_hint" in result:
            current_session["session"] = result["session_hint"]["session"]
            return jsonify({
                "success": True,
                "message": f"Logged in as {result.get('name', user)}",
                "user": result
            }), 200
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    """Clear stored session"""
    current_session.clear()
    return jsonify({"success": True, "message": "Logged out"}), 200


@app.route("/api/me", methods=["GET"])
def get_me():
    """Get current user profile"""
    try:
        auth = get_auth_context()
        result = run_async(mess_get_me(auth))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# Meal Registration Endpoints
# ─────────────────────────────────────────────

@app.route("/api/meal/register", methods=["POST"])
def register_meal():
    """
    Register for a meal
    
    Request body:
    {
        "date": "2026-04-04",
        "meal": "lunch",
        "mess": "kadamba-nonveg"
    }
    
    Response: Success message or error
    """
    try:
        data = request.get_json()
        date = data.get("meal_date") or data.get("date")
        meal = data.get("meal_type") or data.get("meal")
        mess = data.get("mess_id") or data.get("mess")
        guests = data.get("guests")
        
        if not all([date, meal, mess]):
            return jsonify({
                "error": "Missing required fields: date, meal, mess",
                "example": {
                    "meal_date": "2026-04-04",
                    "meal_type": "lunch",
                    "meal_mess": "kadamba-nonveg",
                    "guests": 0
                }
            }), 400
        
        auth = get_auth_context()
        params = CreateRegistrationInput(
            meal_date=date,
            meal_type=meal,
            meal_mess=mess,
            guests=guests,
            **auth
        )
        result = run_async(mess_create_registration(params))
        
        if isinstance(result, dict) and "error" not in result:
            return jsonify({
                "success": True,
                "message": f"Registered for {meal.capitalize()} on {date}",
                "data": result
            }), 200
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/meal/cancel", methods=["POST"])
def cancel_meal():
    """
    Cancel a meal registration
    
    Request body:
    {
        "date": "2026-04-04",
        "meal": "lunch",
        "mess": "kadamba-nonveg"
    }
    """
    try:
        data = request.get_json()
        date = data.get("meal_date") or data.get("date")
        meal = data.get("meal_type") or data.get("meal")
        mess = data.get("mess_id") or data.get("mess")
        
        if not all([date, meal, mess]):
            return jsonify({"error": "Missing required: date, meal, mess"}), 400
        
        auth = get_auth_context()
        params = MealDateTypeInput(
            meal_date=date,
            meal_type=meal,
            **auth
        )
        result = run_async(mess_cancel_registration(params))
        
        if isinstance(result, dict) and "error" not in result:
            return jsonify({
                "success": True,
                "message": f"Cancelled {meal} on {date}",
                "data": result
            }), 200
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/meals/registrations", methods=["GET"])
def get_registrations():
    """
    Get user's meal registrations
    
    Query params:
        from_date (optional): YYYY-MM-DD
        to_date (optional): YYYY-MM-DD
    """
    try:
        from_date = request.args.get("from_date") or request.args.get("from")
        to_date = request.args.get("to_date") or request.args.get("to")
        
        # Default to today and 7 days ahead if not specified
        from datetime import datetime, timedelta
        if not from_date:
            from_date = datetime.now().strftime("%Y-%m-%d")
        if not to_date:
            to_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        auth = get_auth_context()
        params = GetRegistrationsInput(from_date=from_date, to_date=to_date, **auth)
        result = run_async(mess_get_registrations(params))
        
        return jsonify({
            "success": True,
            "registrations": result
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# Menu & Info Endpoints
# ─────────────────────────────────────────────

@app.route("/api/menus", methods=["GET"])
def get_menus():
    """
    Get menus for a date
    
    Query params:
        date (optional): YYYY-MM-DD, defaults to today
    """
    try:
        date = request.args.get("date")
        from iiith_mess_mcp.server import mess_get_menus, MessMenuInput
        
        result = run_async(mess_get_menus(MessMenuInput(on=date)))
        
        # Format response for voice
        if isinstance(result, dict):
            return jsonify({
                "success": True,
                "date": date or "today",
                "menus": result
            }), 200
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/messes", methods=["GET"])
def get_messes():
    """Get all available messes"""
    try:
        result = run_async(mess_get_info())
        
        messes = []
        if isinstance(result, list):
            for mess in result:
                messes.append({
                    "name": mess.get("name"),
                    "id": mess.get("short_name"),
                    "tags": mess.get("tags", [])
                })
        
        return jsonify({
            "success": True,
            "messes": messes
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# Health & Debug Endpoints
# ─────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "authenticated": bool(current_session.get("session") or os.environ.get("MESS_AUTH_KEY"))
    }), 200


@app.route("/api/help", methods=["GET"])
def help_endpoint():
    """Get API documentation"""
    return jsonify({
        "endpoints": {
            "Authentication": {
                "POST /api/auth/login": "Login with MSIT credentials",
                "POST /api/auth/logout": "Clear session",
                "GET /api/me": "Get current user"
            },
            "Registrations": {
                "POST /api/meal/register": "Register for a meal",
                "POST /api/meal/cancel": "Cancel a meal",
                "GET /api/meals/registrations": "Get your registrations"
            },
            "Info": {
                "GET /api/menus": "Get today's menus",
                "GET /api/messes": "Get all messes"
            }
        }
    }), 200


@app.route("/", methods=["GET"])
def index():
    """Root endpoint with API info"""
    return jsonify({
        "name": "IIITH Mess MCP - Siri Integration API",
        "version": "1.0.0",
        "info": "REST API wrapper for IIITH Mess management",
        "docs": "Visit /api/help for endpoint documentation"
    }), 200


# ─────────────────────────────────────────────
# Error Handlers
# ─────────────────────────────────────────────

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found", "available": "/api/help"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("=" * 60)
    print("IIITH Mess MCP - Siri Integration API")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("API Documentation: http://localhost:5000/api/help")
    print("\nMake sure MESS_AUTH_KEY is set in .env or login first!")
    print("=" * 60)
    
    app.run(debug=True, host="0.0.0.0", port=5500)
