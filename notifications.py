import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List
from plyer import notification
import customtkinter as ctk
from tkinter import messagebox

class NotificationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.running = False
        self.notification_thread = None
        
    def start_monitoring(self):
        """Start the notification monitoring thread"""
        if not self.running:
            self.running = True
            self.notification_thread = threading.Thread(target=self._monitor_events, daemon=True)
            self.notification_thread.start()
    
    def stop_monitoring(self):
        """Stop the notification monitoring"""
        self.running = False
        if self.notification_thread:
            self.notification_thread.join(timeout=1)
    
    def _monitor_events(self):
        """Background thread to monitor events and send notifications"""
        while self.running:
            try:
                events = self.db_manager.get_all_events()
                current_date = datetime.now().date()
                
                for event in events:
                    if not event['notification_enabled']:
                        continue
                    
                    event_date = datetime.strptime(event['event_date'], "%Y-%m-%d").date()
                    days_until = (event_date - current_date).days
                    
                    # Check if we should send a notification
                    if days_until == event['notification_days_before']:
                        self._send_notification(event, days_until)
                    elif days_until == 0:
                        self._send_event_today_notification(event)
                    elif days_until < 0 and days_until == -1:
                        self._send_event_passed_notification(event)
                
                # Sleep for 1 hour before checking again
                time.sleep(3600)
                
            except Exception as e:
                print(f"Error in notification monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _send_notification(self, event: Dict, days_until: int):
        """Send a countdown notification"""
        title = f"Countdown Reminder: {event['name']}"
        message = f"{days_until} days remaining until {event['name']}!"
        
        if days_until == 1:
            message = f"Tomorrow is {event['name']}!"
        elif days_until == 0:
            message = f"Today is {event['name']}!"
        
        self._show_system_notification(title, message)
    
    def _send_event_today_notification(self, event: Dict):
        """Send notification when event is today"""
        title = f"🎉 Event Today!"
        message = f"Today is {event['name']}!"
        self._show_system_notification(title, message)
    
    def _send_event_passed_notification(self, event: Dict):
        """Send notification when event has passed"""
        title = f"Event Completed"
        message = f"{event['name']} was yesterday. Hope it went well!"
        self._show_system_notification(title, message)
    
    def _show_system_notification(self, title: str, message: str):
        """Show system notification"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Countdown Widget",
                timeout=10
            )
        except Exception as e:
            print(f"Failed to show notification: {e}")
    
    def send_test_notification(self):
        """Send a test notification"""
        self._show_system_notification(
            "Countdown Widget Test",
            "Notifications are working correctly!"
        )

class CustomNotificationDialog:
    """Custom notification dialog for in-app notifications"""
    
    @staticmethod
    def show_countdown_alert(parent, event_name: str, days_remaining: int):
        """Show a custom countdown alert dialog"""
        dialog = ctk.CTkToplevel(parent)
        dialog.title("Countdown Alert")
        dialog.geometry("350x200")
        dialog.resizable(False, False)
        dialog.configure(fg_color="#f0f8ff")
        
        # Center the dialog on parent
        dialog.transient(parent)
        dialog.grab_set()
        
        # Alert icon and message
        if days_remaining > 0:
            icon = "⏰"
            message = f"{icon} {days_remaining} days remaining\nuntil {event_name}!"
            color = "#ff6b35" if days_remaining <= 3 else "#4a90e2"
        else:
            icon = "🎉"
            message = f"{icon} {event_name}\nis here!"
            color = "#28a745"
        
        # Main message
        label = ctk.CTkLabel(
            dialog,
            text=message,
            font=("Arial", 18, "bold"),
            text_color=color,
            justify="center"
        )
        label.pack(pady=30)
        
        # Action buttons frame
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # OK button
        ok_button = ctk.CTkButton(
            button_frame,
            text="OK",
            command=dialog.destroy,
            width=80,
            fg_color=color,
            hover_color=color
        )
        ok_button.pack(side="left", padx=5)
        
        # Snooze button (for future notifications)
        snooze_button = ctk.CTkButton(
            button_frame,
            text="Remind Later",
            command=lambda: CustomNotificationDialog._snooze_notification(dialog),
            width=100,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        snooze_button.pack(side="left", padx=5)
        
        # Auto-close after 10 seconds
        dialog.after(10000, dialog.destroy)
        
        return dialog
    
    @staticmethod
    def _snooze_notification(dialog):
        """Handle snooze functionality"""
        dialog.destroy()
        # In a full implementation, this would reschedule the notification
