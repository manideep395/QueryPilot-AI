from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import asyncio
import logging
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_orchestrator import EnhancedOrchestrator
from core.security_manager import security_manager, Permission, UserRole

# Initialize FastAPI app
app = FastAPI(
    title="NeuroSQL API",
    description="Advanced NL-to-SQL with AI Integration",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Data models
class QueryRequest(BaseModel):
    question: str
    database: Optional[str] = "database.db"
    user_id: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str
    role: str

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str

class QueryResponse(BaseModel):
    sql: Optional[str]
    result: Optional[Any]
    explanation: str
    confidence: float
    execution_time: float
    timestamp: str
    performance_metrics: Optional[Dict] = None
    ai_enhancements: Optional[Dict] = None
    security_info: Optional[Dict] = None

class SchemaResponse(BaseModel):
    tables: Dict[str, List[str]]
    relations: List[Dict]

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = WebSocketManager()

# Global orchestrator instance
orchestrator = None

@app.on_event("startup")
async def startup_event():
    global orchestrator
    orchestrator = EnhancedOrchestrator("database.db")
    app.state.orchestrator = orchestrator
    logging.info("Enhanced NeuroSQL API started successfully")

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token and return user info"""
    token = credentials.credentials
    payload = security_manager.verify_jwt_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the web dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NeuroSQL Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
            .query-section { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }
            .input-group { margin-bottom: 20px; }
            input[type="text"] { width: 100%; padding: 15px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 16px; }
            button { background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
            button:hover { background: #5a6fd8; }
            .result-section { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .sql-code { background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px; margin: 15px 0; font-family: 'Courier New', monospace; }
            .table { width: 100%; border-collapse: collapse; margin: 15px 0; }
            .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            .table th { background: #f8f9fa; font-weight: 600; }
            .confidence { display: inline-block; padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }
            .confidence.high { background: #d4edda; color: #155724; }
            .confidence.medium { background: #fff3cd; color: #856404; }
            .confidence.low { background: #f8d7da; color: #721c24; }
            .loading { display: none; text-align: center; padding: 20px; }
            .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 NeuroSQL Dashboard</h1>
                <p>Advanced Natural Language to SQL with AI Integration</p>
            </div>
            
            <div class="query-section">
                <h2>Ask Your Question</h2>
                <div class="input-group">
                    <input type="text" id="queryInput" placeholder="e.g., 'Show me all students with marks greater than 80'" />
                </div>
                <button onclick="executeQuery()">Execute Query</button>
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Processing your query...</p>
                </div>
            </div>
            
            <div class="result-section" id="resultSection" style="display: none;">
                <h2>Results</h2>
                <div id="results"></div>
            </div>
        </div>

        <script>
            async function executeQuery() {
                const query = document.getElementById('queryInput').value;
                if (!query.trim()) {
                    alert('Please enter a question');
                    return;
                }

                const loading = document.getElementById('loading');
                const resultSection = document.getElementById('resultSection');
                const results = document.getElementById('results');
                
                loading.style.display = 'block';
                resultSection.style.display = 'none';

                try {
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ question: query })
                    });

                    const data = await response.json();
                    
                    loading.style.display = 'none';
                    resultSection.style.display = 'block';

                    let html = '';
                    
                    if (data.sql) {
                        html += `<div class="sql-code"><strong>Generated SQL:</strong><br>${data.sql}</div>`;
                    }
                    
                    const confidenceClass = data.confidence > 0.8 ? 'high' : data.confidence > 0.6 ? 'medium' : 'low';
                    html += `<p><strong>Confidence:</strong> <span class="confidence ${confidenceClass}">${(data.confidence * 100).toFixed(1)}%</span></p>`;
                    html += `<p><strong>Explanation:</strong> ${data.explanation}</p>`;
                    html += `<p><strong>Execution Time:</strong> ${data.execution_time}ms</p>`;
                    
                    if (data.result && data.result.length > 0) {
                        html += '<h3>Query Results:</h3>';
                        html += '<table class="table">';
                        
                        // Headers
                        html += '<tr>';
                        Object.keys(data.result[0]).forEach(key => {
                            html += `<th>${key}</th>`;
                        });
                        html += '</tr>';
                        
                        // Data rows
                        data.result.forEach(row => {
                            html += '<tr>';
                            Object.values(row).forEach(value => {
                                html += `<td>${value}</td>`;
                            });
                            html += '</tr>';
                        });
                        
                        html += '</table>';
                    } else if (data.result === null) {
                        html += '<p>No results returned or query was blocked by safety layer.</p>';
                    }
                    
                    results.innerHTML = html;
                    
                } catch (error) {
                    loading.style.display = 'none';
                    results.innerHTML = `<p style="color: red;"><strong>Error:</strong> ${error.message}</p>`;
                    resultSection.style.display = 'block';
                }
            }

            // Allow Enter key to submit
            document.getElementById('queryInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    executeQuery();
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/query", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """Execute natural language query with enhanced features"""
    start_time = datetime.now()
    
    try:
        # Execute query with enhanced orchestrator
        result = orchestrator.handle_query(
            request.question, 
            user_id=current_user.get("user_id"),
            database=request.database
        )
        
        return QueryResponse(
            sql=result.get("sql"),
            result=result.get("result"),
            explanation=result.get("explanation", ""),
            confidence=result.get("confidence", 0.0),
            execution_time=result.get("execution_time", 0.0),
            timestamp=datetime.now().isoformat(),
            performance_metrics=result.get("performance_metrics"),
            ai_enhancements=result.get("ai_enhancements"),
            security_info=result.get("security_info")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )

@app.get("/api/schema", response_model=SchemaResponse)
async def get_schema(
    database: str = "database.db",
    current_user: dict = Depends(get_current_user)
):
    """Get database schema"""
    try:
        if database != "database.db":
            orchestrator.load_database(database)
            
        schema, relations = orchestrator.executor.read_schema(orchestrator.conn)
        
        return SchemaResponse(
            tables=schema,
            relations=relations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get schema: {str(e)}"
        )

@app.get("/api/tables")
async def get_tables(
    database: str = "database.db",
    current_user: dict = Depends(get_current_user)
):
    """Get list of tables"""
    try:
        if database != "database.db":
            orchestrator.load_database(database)
            
        tables = orchestrator.executor.show_tables(orchestrator.conn)
        return {"tables": tables}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tables: {str(e)}"
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process real-time query or updates
            await manager.broadcast({"type": "update", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Authentication endpoints
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token"""
    try:
        token, message = security_manager.authenticate_user(
            request.username, 
            request.password,
            ip_address="api_client",
            user_agent="api"
        )
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=message,
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = security_manager.get_user_by_username(request.username)
        
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            username=user.username,
            role=user.role.value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@app.post("/api/auth/register")
async def register(request: CreateUserRequest):
    """Register new user"""
    try:
        role_map = {
            "admin": UserRole.ADMIN,
            "analyst": UserRole.ANALYST,
            "viewer": UserRole.VIEWER,
            "guest": UserRole.GUEST
        }
        
        success, message = security_manager.create_user(
            request.username,
            request.email,
            request.password,
            role_map[request.role]
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {"message": "User created successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    user = security_manager.get_user(current_user.get("user_id"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "permissions": [p.value for p in user.permissions],
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None
    }

@app.get("/api/system/status")
async def get_system_status(current_user: dict = Depends(get_current_user)):
    """Get system status and information"""
    return orchestrator.get_system_status()

@app.get("/api/performance/report")
async def get_performance_report(current_user: dict = Depends(get_current_user)):
    """Get performance report"""
    from core.performance_optimizer import performance_optimizer
    return performance_optimizer.get_performance_report()

@app.get("/api/performance/suggestions")
async def get_optimization_suggestions(current_user: dict = Depends(get_current_user)):
    """Get optimization suggestions"""
    from core.performance_optimizer import performance_optimizer
    return performance_optimizer.get_optimization_recommendations()

@app.get("/api/security/audit")
async def get_audit_logs(current_user: dict = Depends(get_current_user)):
    """Get security audit logs (admin only)"""
    return security_manager.get_audit_logs(current_user.get("user_id"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
