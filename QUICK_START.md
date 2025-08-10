# Enhanced Countdown Widget - Quick Start Guide

## 🚀 Getting Started

### Option 1: Run from Source (Recommended for Development)
1. Open Command Prompt or PowerShell
2. Navigate to the project folder
3. Run: `python enhanced_countdown_app.py`

### Option 2: Use the Launcher Script
1. Double-click `run_enhanced.bat`
2. The application will start automatically

### Option 3: Build Standalone Executable
1. Double-click `build_enhanced.bat`
2. Wait for build to complete
3. Run `dist\CountdownWidget.exe`

## 🎯 Key Features

### ✨ New in Enhanced Version:
- **Multiple Events**: Track unlimited countdown events
- **SQLite Database**: Persistent local storage
- **System Tray**: Minimize to system tray with live updates
- **Priority System**: Color-coded priorities (Low to Urgent)
- **Smart Notifications**: Customizable reminders
- **Modern Themes**: 6 beautiful built-in themes
- **Better UI**: Organized layout with event list and details

### 📱 How to Use:

#### Adding Your First Event
1. Launch the application
2. Click "Add Event" button
3. Fill in:
   - Event name (required)
   - Description (optional)
   - Date in YYYY-MM-DD format (required)
   - Priority level
   - Notification preferences
4. Click "Save Event"

#### Managing Events
- **View Events**: See all events in the left panel
- **Select Event**: Click any event to see detailed countdown
- **Edit Event**: Click "Edit" button in event details
- **Delete Event**: Click "Delete" button (with confirmation)
- **System Tray**: Minimize app to tray for background monitoring

#### Customizing Appearance
- Click "Themes" button to change visual style
- Choose from 6 built-in themes:
  - Light (default)
  - Dark
  - Ocean Blue
  - Forest Green
  - Royal Purple
  - Sunset

#### Setting Up Notifications
- Enable/disable notifications per event
- Choose reminder timing (1-30 days before)
- Test notifications in settings

## 🔧 Troubleshooting

### Common Issues:

**"Module not found" errors:**
```bash
pip install customtkinter pystray pillow plyer python-dotenv
```

**App won't start:**
- Make sure Python 3.10+ is installed
- Check that all dependencies are installed
- Try running `test_enhanced.py` first

**Notifications not working:**
- Check Windows notification settings
- Try the test notification feature
- Make sure app has notification permissions

**Database errors:**
- Delete `countdown_events.db` to reset
- Restart the application

## 📁 Project Files

- `enhanced_countdown_app.py` - Main enhanced application
- `countdown_app.py` - Original simple version
- `database.py` - SQLite database management
- `notifications.py` - Notification system
- `system_tray.py` - System tray integration
- `theme_manager.py` - Theme management
- `test_enhanced.py` - Test script
- `countdown_events.db` - SQLite database file

## 🌟 Tips & Tricks

1. **System Tray**: The app minimizes to system tray instead of closing
2. **Priority Colors**: Events are color-coded by urgency and days remaining
3. **Background Monitoring**: Notifications work even when app is minimized
4. **Data Safety**: All events are stored locally in SQLite database
5. **Keyboard Shortcuts**: Use Tab to navigate between form fields

## 🔄 Migrating from Simple Version

If you were using the original `countdown_app.py`:
1. Your old `event_data.json` file is preserved
2. The enhanced version creates a new `countdown_events.db`
3. You can manually re-enter events or use both versions side-by-side

## 🆘 Getting Help

If you encounter issues:
1. Run `test_enhanced.py` to check system compatibility
2. Check the console output for error messages
3. Verify all dependencies are installed
4. Try resetting the database by deleting `countdown_events.db`

## 🎉 Enjoy Your Enhanced Countdown Widget!

Made with ❤️ for better productivity and time management.
