# 🎮 UQ Party Queue Manager

A real-time web-based party queue management system for online games. Automatically organizes players into parties by monitoring game chat logs.

## Features

- ✅ **Automatic Detection**: Monitors game log file for "+" commands
- ✅ **Real-time Updates**: WebSocket-based live interface
- ✅ **Smart Grouping**: Automatically forms parties when enough players join
- ✅ **Manual Control**: Add/remove players manually if needed
- ✅ **Party History**: Track recently formed parties
- ✅ **Beautiful UI**: Modern, responsive web interface
- ✅ **Cross-platform**: Works on Windows, macOS, and Linux

## How It Works

### Game Log Format

The tool monitors a log file with the following format:

```
{timestamp YYYY-mm-ddThh.mm.ss} {increment} {chat_type} {player_name} {message}
```

Example:
```
2025-12-24T10:30:15 1 public Alice +
2025-12-24T10:31:22 2 public Bob +2 Dave, Emma
```

### Supported Commands in Game Chat

- `+` - Add yourself to queue (1 player)
- `+2 Name1, Name2` - Add 2 players with names
- `+3 Name1, Name2, Name3` - Add 3 players with names

### Configuration

Default settings (2 parties of 4 players = 8 total):
- **Party Size**: 4 players per party
- **Parties Needed**: 2 parties
- **Total Players**: 8 players for a full quest group

Edit `config.json` to customize:

```json
{
  "log_file_path": "mock_game.log",
  "server_port": 5000,
  "party_size": 4,
  "parties_needed": 2,
  "auto_open_browser": true,
  "sound_notification": true
}
```

## Installation

### Requirements

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download this project**

```bash
cd /Users/troch/Repositories/Misc/UQ-Party-Management
```

2. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

Or with a virtual environment (recommended):

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure the log file path**

Edit `config.json` and set the path to your game's log file:

```json
{
  "log_file_path": "/path/to/your/game/chat.log"
}
```

Or pass it as a command-line argument (see Usage below).

## Usage

### Basic Usage

```bash
python server.py
```

This will:
- Start the server on port 5000
- Monitor the log file specified in `config.json`
- Automatically open your browser to `http://localhost:5000`

### Command Line Options

```bash
# Specify log file
python server.py --log="/path/to/game/chat.log"

# Specify port
python server.py --port=8080

# Both
python server.py --log="/path/to/game/chat.log" --port=8080
```

### Testing with Mock Data

A mock log file is included for testing:

```bash
python server.py --log="mock_game.log"
```

Then manually append lines to `mock_game.log` to simulate game chat:

```bash
echo "2025-12-24T10:40:00 7 public TestPlayer +" >> mock_game.log
```

## Web Interface

Once running, open `http://localhost:5000` in your browser.

### Manual Controls

- **Add Player**: Type a name and click "Add +1"
- **Add Multiple**: 
  - Type base name and click "+2" or "+3" (adds Name_1, Name_2, etc.)
  - Or paste multiple names in the text area (one per line or comma-separated)
- **Remove Player**: Click the "✕" button next to their name
- **Clear Queue**: Clear all players from queue
- **Start New Queue**: Finalize current parties and start fresh

### Automatic Detection

When the tool monitors your game log:
- Players typing `+` in game are automatically added
- The queue updates in real-time
- When 8 players join, parties are automatically formed
- You'll see a notification and can copy/paste the party list

## Project Structure

```
UQ-Party-Management/
├── server.py              # Main Flask server
├── queue_manager.py       # Queue logic and log parsing
├── file_watcher.py        # Log file monitoring
├── config.json            # Configuration
├── requirements.txt       # Python dependencies
├── mock_game.log          # Test data
├── static/
│   ├── index.html         # Web interface
│   ├── style.css          # Styling
│   └── app.js             # Frontend logic
└── README.md              # This file
```

## Troubleshooting

### "Log file not found"

- Check the path in `config.json` or `--log` argument
- Make sure the game is running and writing to the log file
- Try using an absolute path instead of relative path

### "Not detecting new messages"

- Make sure the log format matches exactly
- Check that the game flushes writes to the log file
- Try appending a test line manually to verify the watcher works

### "Port already in use"

```bash
# Use a different port
python server.py --port=8080
```

### "Module not found"

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## Customization

### Change Party Size

Edit `config.json`:

```json
{
  "party_size": 5,
  "parties_needed": 2
}
```

This would create 2 parties of 5 (10 players total).

### Disable Auto Browser Open

```json
{
  "auto_open_browser": false
}
```

### Disable Sound Notifications

```json
{
  "sound_notification": false
}
```

### Custom Log Format

If your game uses a different log format, edit the regex pattern in `queue_manager.py`:

```python
@staticmethod
def parse_log_line(line: str) -> Optional[Tuple[str, str, int, List[str]]]:
    # Modify this pattern to match your log format
    pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}\.\d{2}\.\d{2})\s+(\d+)\s+(\w+)\s+(.+?)\s+(.+)$'
    # ... rest of the code
```

## Development

### Running in Debug Mode

Edit `server.py` and change:

```python
socketio.run(app, host='0.0.0.0', port=server_port, debug=True)
```

### Adding Features

The codebase is modular:
- `queue_manager.py` - Queue logic (add/remove/form parties)
- `file_watcher.py` - Log file monitoring
- `server.py` - API endpoints and WebSocket events
- `static/app.js` - Frontend behavior

## License

This is a personal tool. Feel free to modify and use as needed.

## Support

For issues or questions, check:
1. Make sure Python 3.8+ is installed
2. All dependencies are installed (`pip install -r requirements.txt`)
3. Log file path is correct
4. Port is not in use

## Future Enhancements

Potential features to add:
- [ ] Role-based queuing (Tank, Healer, DPS)
- [ ] Priority queue system
- [ ] Discord webhook integration
- [ ] Multiple queue support
- [ ] Player statistics and history
- [ ] Admin authentication
- [ ] Database persistence (SQLite/PostgreSQL)
