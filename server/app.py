import sqlite3
import uuid
import json
import hashlib
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import secrets

DATABASE = 'locations.db'
SESSION_SECRET = secrets.token_hex(32)

sessions = {}

def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id TEXT PRIMARY KEY,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            accuracy REAL,
            note TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    admin_exists = conn.execute('SELECT COUNT(*) FROM admin_users').fetchone()[0]
    if admin_exists == 0:
        default_password = hashlib.sha256(b'admin123').hexdigest()
        conn.execute('INSERT INTO admin_users (username, password_hash, created_at) VALUES (?, ?, ?)',
                   ('admin', default_password, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/':
            self.serve_file('public/index.html')
        elif parsed.path == '/api/locations':
            if not self.is_authenticated():
                self.send_unauthorized()
                return
            self.get_locations()
        elif parsed.path.startswith('/api/locations/'):
            self.get_location(parsed.path.split('/')[-1])
        elif parsed.path == '/login.html':
            self.serve_file('public/login.html')
        elif parsed.path == '/dashboard.html':
            if not self.is_authenticated():
                self.send_response(302)
                self.send_header('Location', '/login.html')
                self.end_headers()
                return
            self.serve_file('public/dashboard.html')
        elif parsed.path == '/view.html':
            self.serve_file('public/view.html')
        elif parsed.path == '/api/login':
            self.serve_file('public/login.html')
        elif parsed.path in ['/style.css', '/app.js', '/view.js', '/dashboard.js', '/login.js']:
            self.serve_file('public' + parsed.path)
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/locations':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            
            if 'latitude' not in data or 'longitude' not in data:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Latitude and longitude required"}')
                return
            
            location_id = uuid.uuid4().hex[:8]
            conn = sqlite3.connect(DATABASE)
            conn.execute('''
                INSERT INTO locations (id, latitude, longitude, accuracy, note, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (location_id, data['latitude'], data['longitude'], 
                  data.get('accuracy'), data.get('note'), datetime.now().isoformat()))
            conn.commit()
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'id': location_id, 'link': f'/view.html?id={location_id}'}).encode())
        
        elif self.path == '/api/login':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            
            username = data.get('username', '')
            password = data.get('password', '')
            
            conn = sqlite3.connect(DATABASE)
            user = conn.execute('SELECT * FROM admin_users WHERE username = ?', (username,)).fetchone()
            conn.close()
            
            if user and verify_password(password, user[2]):
                session_id = secrets.token_hex(16)
                sessions[session_id] = {'username': username, 'created': datetime.now().isoformat()}
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Set-Cookie', f'session={session_id}; Path=/; HttpOnly')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'redirect': '/dashboard.html'}).encode())
            else:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid credentials'}).encode())
        
        elif self.path == '/api/logout':
            cookie = self.headers.get('Cookie', '')
            session_id = self.extract_session_id(cookie)
            if session_id and session_id in sessions:
                del sessions[session_id]
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Set-Cookie', 'session=; Path=/; HttpOnly; Max-Age=0')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
    
    def do_DELETE(self):
        if not self.is_authenticated():
            self.send_unauthorized()
            return
        
        if self.path.startswith('/api/locations/'):
            location_id = self.path.split('/')[-1]
            conn = sqlite3.connect(DATABASE)
            cursor = conn.execute('DELETE FROM locations WHERE id = ?', (location_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            
            if deleted:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"success": true}')
            else:
                self.send_response(404)
                self.end_headers()
    
    def serve_file(self, path):
        try:
            with open(path, 'rb') as f:
                content = f.read()
            
            ext = path.split('.')[-1]
            content_type = 'text/html' if ext == 'html' else 'text/css' if ext == 'css' else 'application/javascript'
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except:
            self.send_error(404)
    
    def get_locations(self):
        conn = sqlite3.connect(DATABASE)
        locs = conn.execute('SELECT * FROM locations ORDER BY created_at DESC').fetchall()
        conn.close()
        
        result = json.dumps([{
            'id': loc[0], 'latitude': loc[1], 'longitude': loc[2],
            'accuracy': loc[3], 'note': loc[4], 'created_at': loc[5]
        } for loc in locs])
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(result.encode())
    
    def get_location(self, location_id):
        conn = sqlite3.connect(DATABASE)
        loc = conn.execute('SELECT * FROM locations WHERE id = ?', (location_id,)).fetchone()
        conn.close()
        
        if not loc:
            self.send_response(404)
            self.end_headers()
            return
        
        result = json.dumps({
            'id': loc[0], 'latitude': loc[1], 'longitude': loc[2],
            'accuracy': loc[3], 'note': loc[4], 'created_at': loc[5]
        })
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(result.encode())
    
    def extract_session_id(self, cookie):
        if not cookie:
            return None
        for part in cookie.split(';'):
            if part.strip().startswith('session='):
                return part.split('=')[1]
        return None
    
    def is_authenticated(self):
        cookie = self.headers.get('Cookie', '')
        session_id = self.extract_session_id(cookie)
        return session_id and session_id in sessions
    
    def send_unauthorized(self):
        self.send_response(401)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"error": "Unauthorized"}')

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 3000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'Server running on http://localhost:{port}')
    server.serve_forever()