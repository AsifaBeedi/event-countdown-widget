import json
from typing import Dict, List

class ThemeManager:
    """Manage themes and visual customization"""
    
    DEFAULT_THEMES = {
        "light": {
            "name": "Light",
            "bg_color": "#f5f5dc",
            "text_color": "#013220",
            "accent_color": "#4a90e2",
            "button_color": "#ffffff",
            "button_text_color": "#013220",
            "window_bg": "#ffffff",
            "frame_bg": "#f0f0f0"
        },
        "dark": {
            "name": "Dark",
            "bg_color": "#2b2b2b",
            "text_color": "#ffffff",
            "accent_color": "#ff6b35",
            "button_color": "#404040",
            "button_text_color": "#ffffff",
            "window_bg": "#1e1e1e",
            "frame_bg": "#333333"
        },
        "blue": {
            "name": "Ocean Blue",
            "bg_color": "#e3f2fd",
            "text_color": "#0d47a1",
            "accent_color": "#2196f3",
            "button_color": "#bbdefb",
            "button_text_color": "#0d47a1",
            "window_bg": "#f3e5f5",
            "frame_bg": "#e1bee7"
        },
        "green": {
            "name": "Forest Green",
            "bg_color": "#e8f5e8",
            "text_color": "#1b5e20",
            "accent_color": "#4caf50",
            "button_color": "#c8e6c9",
            "button_text_color": "#1b5e20",
            "window_bg": "#f1f8e9",
            "frame_bg": "#dcedc8"
        },
        "purple": {
            "name": "Royal Purple",
            "bg_color": "#f3e5f5",
            "text_color": "#4a148c",
            "accent_color": "#9c27b0",
            "button_color": "#e1bee7",
            "button_text_color": "#4a148c",
            "window_bg": "#fce4ec",
            "frame_bg": "#f8bbd9"
        },
        "sunset": {
            "name": "Sunset",
            "bg_color": "#fff3e0",
            "text_color": "#e65100",
            "accent_color": "#ff9800",
            "button_color": "#ffcc02",
            "button_text_color": "#e65100",
            "window_bg": "#fff8e1",
            "frame_bg": "#ffecb3"
        }
    }
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_theme = self.load_current_theme()
    
    def load_current_theme(self) -> Dict:
        """Load the current theme from database or default"""
        theme_name = self.db_manager.get_setting("current_theme", "light")
        
        # Try to load custom theme first
        custom_theme = self.load_custom_theme(theme_name)
        if custom_theme:
            return custom_theme
        
        # Fall back to default themes
        return self.DEFAULT_THEMES.get(theme_name, self.DEFAULT_THEMES["light"])
    
    def load_custom_theme(self, theme_name: str) -> Dict:
        """Load a custom theme from database"""
        theme_data = self.db_manager.get_setting(f"custom_theme_{theme_name}")
        if theme_data:
            try:
                return json.loads(theme_data)
            except json.JSONDecodeError:
                return None
        return None
    
    def save_custom_theme(self, theme_name: str, theme_data: Dict) -> bool:
        """Save a custom theme to database"""
        try:
            theme_json = json.dumps(theme_data)
            return self.db_manager.set_setting(f"custom_theme_{theme_name}", theme_json)
        except Exception:
            return False
    
    def set_current_theme(self, theme_name: str) -> bool:
        """Set the current active theme"""
        # Check if theme exists
        if theme_name in self.DEFAULT_THEMES or self.load_custom_theme(theme_name):
            self.db_manager.set_setting("current_theme", theme_name)
            self.current_theme = self.load_current_theme()
            return True
        return False
    
    def get_available_themes(self) -> List[Dict]:
        """Get list of all available themes"""
        themes = []
        
        # Add default themes
        for theme_id, theme_data in self.DEFAULT_THEMES.items():
            themes.append({
                "id": theme_id,
                "name": theme_data["name"],
                "type": "default",
                "preview_colors": {
                    "bg": theme_data["bg_color"],
                    "text": theme_data["text_color"],
                    "accent": theme_data["accent_color"]
                }
            })
        
        # Add custom themes (this would query the database for custom themes)
        # For now, we'll just return default themes
        
        return themes
    
    def get_current_theme(self) -> Dict:
        """Get the current active theme"""
        return self.current_theme
    
    def create_theme_from_base(self, base_theme: str, customizations: Dict) -> Dict:
        """Create a new theme based on an existing one with customizations"""
        if base_theme in self.DEFAULT_THEMES:
            theme = self.DEFAULT_THEMES[base_theme].copy()
            theme.update(customizations)
            return theme
        return self.DEFAULT_THEMES["light"]
    
    def validate_theme(self, theme_data: Dict) -> bool:
        """Validate theme data structure"""
        required_keys = [
            "bg_color", "text_color", "accent_color", 
            "button_color", "button_text_color", "window_bg", "frame_bg"
        ]
        
        return all(key in theme_data for key in required_keys)
    
    def get_theme_preview(self, theme_name: str) -> Dict:
        """Get theme preview data for UI"""
        if theme_name in self.DEFAULT_THEMES:
            theme = self.DEFAULT_THEMES[theme_name]
        else:
            theme = self.load_custom_theme(theme_name)
        
        if not theme:
            return None
        
        return {
            "name": theme.get("name", theme_name),
            "colors": {
                "primary": theme["bg_color"],
                "secondary": theme["text_color"],
                "accent": theme["accent_color"]
            }
        }

class PriorityColorManager:
    """Manage priority-based color coding for events"""
    
    PRIORITY_COLORS = {
        1: "#28a745",  # Low - Green
        2: "#ffc107",  # Medium - Yellow
        3: "#fd7e14",  # High - Orange
        4: "#dc3545",  # Critical - Red
        5: "#6f42c1"   # Urgent - Purple
    }
    
    PRIORITY_NAMES = {
        1: "Low",
        2: "Medium", 
        3: "High",
        4: "Critical",
        5: "Urgent"
    }
    
    @classmethod
    def get_priority_color(cls, priority: int) -> str:
        """Get color for a given priority level"""
        return cls.PRIORITY_COLORS.get(priority, cls.PRIORITY_COLORS[1])
    
    @classmethod
    def get_priority_name(cls, priority: int) -> str:
        """Get name for a given priority level"""
        return cls.PRIORITY_NAMES.get(priority, "Low")
    
    @classmethod
    def get_all_priorities(cls) -> List[Dict]:
        """Get all priority levels with their colors and names"""
        return [
            {
                "level": level,
                "name": name,
                "color": cls.PRIORITY_COLORS[level]
            }
            for level, name in cls.PRIORITY_NAMES.items()
        ]
    
    @classmethod
    def get_days_remaining_color(cls, days: int, priority: int = 1) -> str:
        """Get color based on days remaining and priority"""
        base_color = cls.get_priority_color(priority)
        
        # Modify intensity based on days remaining
        if days < 0:
            return "#6c757d"  # Gray for past events
        elif days == 0:
            return "#dc3545"  # Red for today
        elif days <= 3:
            return "#fd7e14"  # Orange for urgent
        elif days <= 7:
            return "#ffc107"  # Yellow for soon
        else:
            return base_color  # Priority color for future events
