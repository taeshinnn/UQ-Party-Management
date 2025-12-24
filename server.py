from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import json
import os
import webbrowser
import threading
from queue_manager import QueueManager
from file_watcher import FileWatcher


app = Flask(__name__, static_folder='static', template_folder='static')
app.config['SECRET_KEY'] = 'party-queue-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

queue_manager = None
file_watcher = None
config = {}


def load_config():
    global config
    config_path = 'config.json'
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {
            "log_file_path": "mock_game.log",
            "server_port": 5000,
            "party_size": 4,
            "parties_needed": 2,
            "auto_open_browser": True,
            "sound_notification": True
        }


def notify_clients(event_type: str, data: dict):
    socketio.emit(event_type, data)


def on_log_event(event: dict):
    notify_clients('queue_update', event['data'])


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        "party_size": config.get("party_size", 4),
        "parties_needed": config.get("parties_needed", 2),
        "max_players": config.get("party_size", 4) * config.get("parties_needed", 2),
        "sound_notification": config.get("sound_notification", True)
    })


@app.route('/api/queue', methods=['GET'])
def get_queue():
    return jsonify(queue_manager.get_queue_status())


@app.route('/api/queue/add', methods=['POST'])
def add_to_queue():
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({"success": False, "message": "Name is required"}), 400
    
    result = queue_manager.add_player(name, source="manual")
    notify_clients('queue_update', result)
    
    return jsonify(result)


@app.route('/api/queue/add-multiple', methods=['POST'])
def add_multiple_to_queue():
    data = request.json
    names = data.get('names', [])
    
    if not names:
        return jsonify({"success": False, "message": "Names are required"}), 400
    
    result = queue_manager.add_multiple_players(names, source="manual")
    notify_clients('queue_update', result)
    
    return jsonify(result)


@app.route('/api/queue/remove', methods=['DELETE'])
def remove_from_queue():
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({"success": False, "message": "Name is required"}), 400
    
    result = queue_manager.remove_player(name)
    notify_clients('queue_update', result)
    
    return jsonify(result)


@app.route('/api/queue/clear', methods=['DELETE'])
def clear_queue():
    result = queue_manager.clear_queue()
    notify_clients('queue_update', result)
    
    return jsonify(result)


@app.route('/api/parties/finalize', methods=['POST'])
def finalize_parties():
    result = queue_manager.finalize_parties()
    
    if result['success']:
        notify_clients('parties_formed', result)
    
    return jsonify(result)


@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(queue_manager.get_history())


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('queue_update', queue_manager.get_queue_status())


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


def open_browser(port):
    url = f'http://localhost:{port}'
    print(f'🚀 Opening browser to {url}')
    webbrowser.open(url)


def start_server(log_file_path: str = None, port: int = None):
    global queue_manager, file_watcher, config
    
    load_config()
    
    if port:
        config['server_port'] = port
    if log_file_path:
        config['log_file_path'] = log_file_path
    
    party_size = config.get('party_size', 4)
    parties_needed = config.get('parties_needed', 2)
    queue_manager = QueueManager(party_size=party_size, parties_needed=parties_needed)
    
    log_path = config.get('log_file_path')
    if log_path and os.path.exists(log_path):
        file_watcher = FileWatcher(log_path, queue_manager, on_log_event)
        file_watcher.start()
    else:
        print(f"ℹ️  Log file not found: {log_path}")
        print("   Running in manual mode only")
    
    server_port = config.get('server_port', 5000)
    
    print("🎮 Party Queue Manager Starting...")
    print(f"🌐 Server running at http://localhost:{server_port}")
    
    if config.get('auto_open_browser', True):
        threading.Timer(1.5, lambda: open_browser(server_port)).start()
    
    try:
        socketio.run(app, host='0.0.0.0', port=server_port, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        if file_watcher:
            file_watcher.stop()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Party Queue Manager Server')
    parser.add_argument('--log', type=str, help='Path to game log file')
    parser.add_argument('--port', type=int, help='Server port (default: 5000)')
    
    args = parser.parse_args()
    
    start_server(log_file_path=args.log, port=args.port)

