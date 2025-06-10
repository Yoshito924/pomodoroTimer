# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a Loop-based Pomodoro Timer desktop application built with Python and Tkinter. It continuously cycles between 25-minute work sessions and 5-minute breaks without user intervention.

## Commands

### Running the Application
```bash
python main.py
```

### Installing Dependencies
The project requires Windows-specific audio libraries:
```bash
pip install pycaw comtypes
```

Note: `pygame` is mentioned in the readme but not actually used in the code.

## Architecture

### Core Components
1. **main.py** - Main application entry point with `PomodoroTimer` class that manages:
   - Timer state (work/break cycles)
   - Tkinter GUI components
   - CSV logging to `log/` directory
   - Integration with other modules

2. **config.py** - Centralized configuration management:
   - Loads/saves settings to `settings.json`
   - Merges user settings with defaults
   - Uses temporary files for safe writes

3. **sound_manager.py** - Windows-specific audio handling:
   - System beep sounds via `winsound`
   - WAV file playback from `sounds/` directory
   - System volume control via `pycaw`

4. **timer_settings.py** - Modal settings dialog for configuring:
   - Work/break durations
   - Reminder notification frequency
   - System volume

### Key Design Patterns
- **State Management**: Timer maintains clear work/break states with automatic transitions
- **Configuration Persistence**: All settings saved to JSON and restored on startup
- **Logging**: Activities logged to daily CSV files with Shift-JIS encoding (Japanese locale)
- **Error Handling**: Comprehensive try-except blocks with fallback behavior

### Platform Limitations
This project is **Windows-only** due to its sound implementation using `winsound` and `pycaw`. Cross-platform support would require refactoring the sound manager.

### Data Flow
1. Startup: Load config → Initialize UI → Restore window state
2. Timer Loop: Work (25min) → Reminder sounds → Break (5min) → Increment counter → Repeat
3. Settings Changes: Update config → Save to JSON → Apply immediately
4. Logging: Every timer event → Write to `log/YYYY-MM-DD.csv`

### Directory Structure
- `sounds/` - WAV files for notifications (auto-created)
- `log/` - Daily CSV activity logs (auto-created)
- `__pycache__/` - Python bytecode cache (gitignored)