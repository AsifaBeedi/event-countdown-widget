import pystray
from PIL import Image, ImageDraw
import threading
from datetime import datetime

class SystemTrayManager:
    def __init__(self, app_callback, quit_callback):
        self.app_callback = app_callback
        self.quit_callback = quit_callback
        self.icon = None
        self.running = False
        
    def create_icon_image(self, text="CD"):
        """Create a simple icon image with text"""
        # Create a 64x64 image with transparent background
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw a circle background
        draw.ellipse([8, 8, 56, 56], fill=(1, 50, 32, 255), outline=(255, 255, 255, 255), width=2)
        
        # Draw text
        bbox = draw.textbbox((0, 0), text, anchor="mm")
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (64 - text_width) // 2
        y = (64 - text_height) // 2
        draw.text((x, y), text, fill=(255, 255, 255, 255))
        
        return image
    
    def update_icon_with_countdown(self, days_remaining):
        """Update the system tray icon with countdown days"""
        if self.icon and self.running:
            # Limit text length for icon
            if days_remaining > 999:
                text = "999+"
            elif days_remaining < 0:
                text = "END"
            else:
                text = str(days_remaining)
            
            new_image = self.create_icon_image(text)
            self.icon.icon = new_image
    
    def create_menu(self):
        """Create the system tray context menu"""
        return pystray.Menu(
            pystray.MenuItem("Open Countdown Widget", self.show_app),
            pystray.MenuItem("Add New Event", self.add_new_event),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings", self.show_settings),
            pystray.MenuItem("About", self.show_about),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.quit_app)
        )
    
    def show_app(self, icon=None, item=None):
        """Show the main application window"""
        if self.app_callback:
            self.app_callback()
    
    def add_new_event(self, icon=None, item=None):
        """Trigger add new event dialog"""
        # This would be implemented to show the add event dialog
        self.show_app()
    
    def show_settings(self, icon=None, item=None):
        """Show settings dialog"""
        # Placeholder for settings dialog
        pass
    
    def show_about(self, icon=None, item=None):
        """Show about dialog"""
        # Placeholder for about dialog
        pass
    
    def quit_app(self, icon=None, item=None):
        """Quit the application"""
        self.stop()
        if self.quit_callback:
            self.quit_callback()
    
    def start(self):
        """Start the system tray icon"""
        if not self.running:
            self.running = True
            image = self.create_icon_image()
            menu = self.create_menu()
            
            self.icon = pystray.Icon(
                "countdown_widget",
                image,
                "Countdown Widget",
                menu
            )
            
            # Run in separate thread to avoid blocking
            self.tray_thread = threading.Thread(
                target=self.icon.run,
                daemon=True
            )
            self.tray_thread.start()
    
    def stop(self):
        """Stop the system tray icon"""
        if self.icon and self.running:
            self.running = False
            self.icon.stop()

class TrayNotificationManager:
    """Manage notifications through system tray"""
    
    def __init__(self, tray_manager):
        self.tray_manager = tray_manager
    
    def show_balloon_notification(self, title, message):
        """Show a balloon notification from system tray"""
        if self.tray_manager.icon and self.tray_manager.running:
            try:
                self.tray_manager.icon.notify(message, title)
            except Exception as e:
                print(f"Failed to show balloon notification: {e}")
    
    def update_tray_tooltip(self, next_event_info):
        """Update the system tray tooltip with next event info"""
        if self.tray_manager.icon and self.tray_manager.running:
            if next_event_info:
                tooltip = f"Next: {next_event_info['name']} in {next_event_info['days']} days"
            else:
                tooltip = "Countdown Widget - No active events"
            
            self.tray_manager.icon.title = tooltip
