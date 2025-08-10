import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import threading
import sys
import os

# Import our custom modules
from database import DatabaseManager
from notifications import NotificationManager, CustomNotificationDialog
from system_tray import SystemTrayManager, TrayNotificationManager
from theme_manager import ThemeManager, PriorityColorManager

# Set dark appearance mode for modern look
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
ctk.set_widget_scaling(1.0)
ctk.set_window_scaling(1.0)

# Modern color palette
COLORS = {
    "primary": "#1f1f1f",      # Dark background
    "secondary": "#2d2d2d",     # Secondary background
    "accent": "#3b82f6",        # Blue accent
    "accent_hover": "#2563eb",  # Darker blue
    "success": "#10b981",       # Green
    "danger": "#ef4444",        # Red
    "warning": "#f59e0b",       # Amber
    "text_primary": "#ffffff",  # White text
    "text_secondary": "#94a3b8", # Gray text
    "border": "#374151",        # Border color
    "card": "#1e293b",          # Card background
    "hover": "#334155"          # Hover state
}

def center_window(window, width: int, height: int):
    """Center a window on the screen with proper positioning"""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

class CountdownApp:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.theme_manager = ThemeManager(self.db_manager)
        self.notification_manager = NotificationManager(self.db_manager)
        
        # Initialize system tray
        self.tray_manager = SystemTrayManager(
            app_callback=self.show_main_window,
            quit_callback=self.quit_application
        )
        self.tray_notification_manager = TrayNotificationManager(self.tray_manager)
        
        # Main window
        self.root = None
        self.current_events = []
        self.selected_event_id = None
        
        # Start background services
        self.notification_manager.start_monitoring()
        self.tray_manager.start()
        
        # Check if this is first run
        if not self.db_manager.get_all_events():
            self.show_welcome_dialog()
        else:
            self.show_main_window()
    
    def show_welcome_dialog(self):
        """Show welcome dialog for first-time users"""
        welcome = ctk.CTk()
        welcome.title("Welcome to Countdown Pro")
        center_window(welcome, 650, 550)
        welcome.configure(fg_color=COLORS["primary"])
        welcome.resizable(False, False)
        
        # Main container with sophisticated styling
        main_container = ctk.CTkFrame(
            welcome, 
            corner_radius=20,
            fg_color=COLORS["secondary"],
            border_width=1,
            border_color=COLORS["border"]
        )
        main_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Header section with gradient-like effect
        header_frame = ctk.CTkFrame(
            main_container,
            corner_radius=15,
            fg_color=COLORS["card"],
            height=120
        )
        header_frame.pack(fill="x", padx=20, pady=(20, 15))
        header_frame.pack_propagate(False)
        
        # Professional title
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚡ Countdown Pro",
            font=("SF Pro Display", 32, "bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(pady=(30, 5))
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Professional Event Management & Countdown System",
            font=("SF Pro Display", 14),
            text_color=COLORS["text_secondary"]
        )
        subtitle_label.pack()
        
        # Features section with modern cards
        features_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        features_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        features = [
            ("📊", "Advanced Analytics", "Track multiple events with priority management"),
            ("⚡", "Real-time Sync", "Cloud synchronization across all devices"),
            ("🎯", "Smart Notifications", "Intelligent alerts and reminders"),
            ("🎨", "Premium Themes", "Beautiful, customizable interface")
        ]
        
        for i, (icon, title, desc) in enumerate(features):
            if i % 2 == 0:
                row_frame = ctk.CTkFrame(features_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=5)
            
            feature_card = ctk.CTkFrame(
                row_frame,
                corner_radius=12,
                fg_color=COLORS["card"],
                border_width=1,
                border_color=COLORS["border"]
            )
            feature_card.pack(side="left", fill="both", expand=True, padx=5)
            
            icon_label = ctk.CTkLabel(
                feature_card,
                text=icon,
                font=("SF Pro Display", 24)
            )
            icon_label.pack(pady=(15, 5))
            
            title_label = ctk.CTkLabel(
                feature_card,
                text=title,
                font=("SF Pro Display", 13, "bold"),
                text_color=COLORS["text_primary"]
            )
            title_label.pack()
            
            desc_label = ctk.CTkLabel(
                feature_card,
                text=desc,
                font=("SF Pro Display", 10),
                text_color=COLORS["text_secondary"],
                wraplength=120
            )
            desc_label.pack(pady=(2, 15))
        
        # Action buttons with modern design
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(pady=(20, 25))
        
        get_started_btn = ctk.CTkButton(
            button_frame,
            text="Get Started",
            command=lambda: (welcome.destroy(), self.show_add_event_dialog()),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            width=180,
            height=48,
            font=("SF Pro Display", 15, "bold"),
            corner_radius=12,
            border_width=0
        )
        get_started_btn.pack(side="left", padx=10)
        
        explore_btn = ctk.CTkButton(
            button_frame,
            text="Explore First",
            command=lambda: (welcome.destroy(), self.show_main_window()),
            fg_color="transparent",
            hover_color=COLORS["hover"],
            border_width=2,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            width=150,
            height=48,
            font=("SF Pro Display", 15),
            corner_radius=12
        )
        explore_btn.pack(side="left", padx=10)
        
        welcome.mainloop()
    
    def show_main_window(self):
        """Show the main application window"""
        if self.root:
            self.root.lift()
            self.root.focus_force()
            return
        
        self.root = ctk.CTk()
        self.root.title("Countdown Pro")
        center_window(self.root, 950, 700)
        self.root.configure(fg_color=COLORS["primary"])
        self.root.minsize(850, 650)
        
        # Apply theme
        self.apply_theme()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main layout
        self.create_main_layout()
        
        # Load and display events
        self.refresh_events()
        
        # Bind close event to minimize to tray instead of closing
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        
        self.root.mainloop()
    
    def create_menu_bar(self):
        """Create application menu bar"""
        # Professional menu frame with modern styling
        menu_frame = ctk.CTkFrame(
            self.root, 
            height=65, 
            corner_radius=15,
            fg_color=COLORS["card"],
            border_width=1,
            border_color=COLORS["border"]
        )
        menu_frame.pack(fill="x", padx=15, pady=(15, 10))
        menu_frame.pack_propagate(False)
        
        # Left section with action buttons
        action_frame = ctk.CTkFrame(menu_frame, fg_color="transparent")
        action_frame.pack(side="left", fill="y", padx=20, pady=15)
        
        add_btn = ctk.CTkButton(
            action_frame,
            text="+ New Event",
            command=self.show_add_event_dialog,
            width=140,
            height=38,
            font=("SF Pro Display", 13, "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            corner_radius=10,
            border_width=0
        )
        add_btn.pack(side="left", padx=8)
        
        refresh_btn = ctk.CTkButton(
            action_frame,
            text="🔄 Refresh",
            command=self.refresh_events,
            width=110,
            height=38,
            font=("SF Pro Display", 13),
            fg_color="transparent",
            hover_color=COLORS["hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            corner_radius=10
        )
        refresh_btn.pack(side="left", padx=8)
        
        # Right section with utility buttons
        utility_frame = ctk.CTkFrame(menu_frame, fg_color="transparent")
        utility_frame.pack(side="right", fill="y", padx=20, pady=15)
        
        # Export button
        export_btn = ctk.CTkButton(
            utility_frame,
            text="📤",
            command=self.export_events,
            width=40,
            height=38,
            font=("SF Pro Display", 16),
            fg_color="transparent",
            hover_color=COLORS["hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            corner_radius=10
        )
        export_btn.pack(side="right", padx=5)
        
        # Import button
        import_btn = ctk.CTkButton(
            utility_frame,
            text="📥",
            command=self.import_events,
            width=40,
            height=38,
            font=("SF Pro Display", 16),
            fg_color="transparent",
            hover_color=COLORS["hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            corner_radius=10
        )
        import_btn.pack(side="right", padx=5)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            utility_frame,
            text="⚙",
            command=self.show_settings_dialog,
            width=40,
            height=38,
            font=("SF Pro Display", 16),
            fg_color="transparent",
            hover_color=COLORS["hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            corner_radius=10
        )
        settings_btn.pack(side="right", padx=5)
        settings_frame = ctk.CTkFrame(menu_frame, fg_color="transparent")
        settings_frame.pack(side="right", fill="y", padx=10)
        
        themes_btn = ctk.CTkButton(
            settings_frame,
            text="🎨 Themes",
            command=self.show_theme_selector,
            width=100,
            height=35,
            font=("Segoe UI", 12),
            fg_color="#6f42c1",
            hover_color="#5a32a3",
            corner_radius=8
        )
        themes_btn.pack(side="right", padx=5, pady=7)
        
        settings_btn = ctk.CTkButton(
            settings_frame,
            text="⚙️ Settings",
            command=self.show_settings_dialog,
            width=100,
            height=35,
            font=("Segoe UI", 12),
            fg_color="#6c757d",
            hover_color="#5a6268",
            corner_radius=8
        )
        settings_btn.pack(side="right", padx=5, pady=7)
    
    def create_main_layout(self):
        """Create the main application layout with modern design"""
        # Main container with sophisticated styling
        main_container = ctk.CTkFrame(
            self.root, 
            corner_radius=20,
            fg_color=COLORS["secondary"],
            border_width=1,
            border_color=COLORS["border"]
        )
        main_container.pack(fill="both", expand=True, padx=15, pady=(10, 15))
        
        # Left panel - Event list with modern design
        left_panel = ctk.CTkFrame(
            main_container, 
            width=380, 
            corner_radius=15,
            fg_color=COLORS["card"],
            border_width=1,
            border_color=COLORS["border"]
        )
        left_panel.pack(side="left", fill="y", padx=(15, 8), pady=15)
        left_panel.pack_propagate(False)
        
        # Event list header with professional styling
        list_header_frame = ctk.CTkFrame(
            left_panel, 
            height=60, 
            corner_radius=12,
            fg_color="transparent"
        )
        list_header_frame.pack(fill="x", padx=15, pady=(15, 10))
        list_header_frame.pack_propagate(False)
        
        list_header = ctk.CTkLabel(
            list_header_frame,
            text="� Active Events",
            font=("SF Pro Display", 20, "bold"),
            text_color=COLORS["text_primary"]
        )
        list_header.pack(pady=18)
        
        # Event list scrollable frame with modern scrollbar
        self.events_scrollable = ctk.CTkScrollableFrame(
            left_panel, 
            corner_radius=12,
            fg_color="transparent",
            scrollbar_fg_color=COLORS["secondary"],
            scrollbar_button_color=COLORS["accent"],
            scrollbar_button_hover_color=COLORS["accent_hover"]
        )
        self.events_scrollable.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        
        # Right panel - Event details and countdown with elegant design
        right_panel = ctk.CTkFrame(
            main_container, 
            corner_radius=15,
            fg_color=COLORS["card"],
            border_width=1,
            border_color=COLORS["border"]
        )
        right_panel.pack(side="right", fill="both", expand=True, padx=(8, 15), pady=15)
        
        # Header for right panel with sophisticated typography
        right_header_frame = ctk.CTkFrame(
            right_panel, 
            height=60, 
            corner_radius=12,
            fg_color="transparent"
        )
        right_header_frame.pack(fill="x", padx=15, pady=(15, 10))
        right_header_frame.pack_propagate(False)
        
        right_header = ctk.CTkLabel(
            right_header_frame,
            text="⏱️ Live Countdown",
            font=("SF Pro Display", 20, "bold"),
            text_color=COLORS["text_primary"]
        )
        right_header.pack(pady=18)
        
        # Countdown display area with premium styling
        self.countdown_frame = ctk.CTkFrame(
            right_panel, 
            corner_radius=15,
            fg_color=COLORS["secondary"],
            border_width=1,
            border_color=COLORS["border"]
        )
        self.countdown_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Default countdown display
        self.show_default_countdown()
    
    def show_default_countdown(self):
        """Show default countdown with professional styling"""
        for widget in self.countdown_frame.winfo_children():
            widget.destroy()
        
        events = self.db_manager.get_all_events()
        
        # Create main container with modern design
        main_container = ctk.CTkFrame(
            self.countdown_frame, 
            corner_radius=15,
            fg_color="transparent"
        )
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        if not events:
            # Professional empty state design
            empty_state_frame = ctk.CTkFrame(
                main_container, 
                corner_radius=15,
                fg_color=COLORS["primary"],
                border_width=2,
                border_color=COLORS["border"]
            )
            empty_state_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Elegant icon with modern styling
            icon_label = ctk.CTkLabel(
                empty_state_frame,
                text="⚡",
                font=("SF Pro Display", 80),
                text_color=COLORS["accent"]
            )
            icon_label.pack(pady=(60, 25))
            
            # Professional typography
            title_label = ctk.CTkLabel(
                empty_state_frame,
                text="Ready to Begin",
                font=("SF Pro Display", 28, "bold"),
                text_color=COLORS["text_primary"]
            )
            title_label.pack(pady=(0, 15))
            
            desc_label = ctk.CTkLabel(
                empty_state_frame,
                text="Create your first countdown event to start\ntracking important dates and deadlines.",
                font=("SF Pro Display", 15),
                text_color=COLORS["text_secondary"],
                justify="center"
            )
            desc_label.pack(pady=(0, 40))
            
            # Call-to-action button with modern design
            cta_button = ctk.CTkButton(
                empty_state_frame,
                text="+ Create Event",
                command=self.show_add_event_dialog,
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                width=200,
                height=50,
                font=("SF Pro Display", 16, "bold"),
                corner_radius=12,
                border_width=0
            )
            cta_button.pack(pady=(0, 60))
            
        else:
            # Show next upcoming event with premium styling
            next_event = self.get_next_upcoming_event(events)
            if next_event:
                # Professional header section
                header_frame = ctk.CTkFrame(
                    main_container, 
                    corner_radius=12, 
                    height=60,
                    fg_color=COLORS["primary"],
                    border_width=1,
                    border_color=COLORS["border"]
                )
                header_frame.pack(fill="x", padx=15, pady=(15, 20))
                header_frame.pack_propagate(False)
                
                header_label = ctk.CTkLabel(
                    header_frame,
                    text="🔥 Next Upcoming Event",
                    font=("Segoe UI", 18, "bold"),
                    text_color=self.theme_manager.current_theme["accent_color"]
                )
                header_label.pack(expand=True)
                
                # Show the event (reuse the existing method but in a contained way)
                self.show_event_countdown(next_event)
            else:
                # All events are past
                past_frame = ctk.CTkFrame(main_container, corner_radius=12)
                past_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                icon_label = ctk.CTkLabel(
                    past_frame,
                    text="🎉",
                    font=("Segoe UI", 60)
                )
                icon_label.pack(pady=(40, 20))
                
                title_label = ctk.CTkLabel(
                    past_frame,
                    text="All Events Complete!",
                    font=("Segoe UI", 24, "bold"),
                    text_color=self.theme_manager.current_theme["accent_color"]
                )
                title_label.pack(pady=(0, 10))
                
                desc_label = ctk.CTkLabel(
                    past_frame,
                    text="Great job! You've completed all your events.\nAdd new events to continue tracking countdowns.",
                    font=("Segoe UI", 14),
                    text_color=self.theme_manager.current_theme["text_color"],
                    justify="center"
                )
                desc_label.pack(pady=(0, 30))
                
                # Add new event button
                new_event_btn = ctk.CTkButton(
                    past_frame,
                    text="➕ Add New Event",
                    command=self.show_add_event_dialog,
                    fg_color="#28a745",
                    hover_color="#218838",
                    width=160,
                    height=40,
                    font=("Segoe UI", 14, "bold"),
                    corner_radius=10
                )
                new_event_btn.pack(pady=(0, 40))
    
    def get_next_upcoming_event(self, events):
        """Get the next upcoming event"""
        today = datetime.now().date()
        upcoming_events = []
        
        for event in events:
            event_date = datetime.strptime(event['event_date'], "%Y-%m-%d").date()
            days_remaining = (event_date - today).days
            
            if days_remaining >= 0:
                event['days_remaining'] = days_remaining
                upcoming_events.append(event)
        
        if upcoming_events:
            # Sort by days remaining, then by priority
            upcoming_events.sort(key=lambda x: (x['days_remaining'], -x['priority']))
            return upcoming_events[0]
        
        return None
    
    def show_event_countdown(self, event):
        """Show countdown for a specific event"""
        for widget in self.countdown_frame.winfo_children():
            widget.destroy()
        
        # Calculate days remaining
        today = datetime.now().date()
        event_date = datetime.strptime(event['event_date'], "%Y-%m-%d").date()
        days_remaining = (event_date - today).days
        
        # Get priority color
        priority_color = PriorityColorManager.get_days_remaining_color(
            days_remaining, event['priority']
        )
        
        # Main content container
        content_container = ctk.CTkFrame(self.countdown_frame, corner_radius=15)
        content_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Event name with enhanced styling
        name_frame = ctk.CTkFrame(content_container, corner_radius=10, height=60)
        name_frame.pack(fill="x", padx=15, pady=(15, 10))
        name_frame.pack_propagate(False)
        
        name_label = ctk.CTkLabel(
            name_frame,
            text=event['name'],
            font=("Segoe UI", 24, "bold"),
            text_color=self.theme_manager.current_theme["text_color"],
            wraplength=400
        )
        name_label.pack(expand=True)
        
        # Countdown display with enhanced visuals
        countdown_container = ctk.CTkFrame(content_container, corner_radius=15)
        countdown_container.pack(fill="x", padx=15, pady=10)
        
        if days_remaining > 0:
            countdown_text = f"{days_remaining}"
            subtitle_text = "days remaining"
            emoji = "⏰"
            bg_gradient = priority_color
        elif days_remaining == 0:
            countdown_text = "TODAY"
            subtitle_text = "is the day!"
            emoji = "🎉"
            bg_gradient = "#dc3545"
        else:
            countdown_text = f"{abs(days_remaining)}"
            subtitle_text = "days ago"
            emoji = "📅"
            bg_gradient = "#6c757d"
        
        # Big countdown display
        countdown_display_frame = ctk.CTkFrame(countdown_container, corner_radius=12, height=120)
        countdown_display_frame.pack(fill="x", padx=15, pady=15)
        countdown_display_frame.pack_propagate(False)
        
        # Emoji and countdown number
        main_display = ctk.CTkLabel(
            countdown_display_frame,
            text=f"{emoji} {countdown_text}",
            font=("Segoe UI", 48, "bold"),
            text_color=bg_gradient
        )
        main_display.pack(expand=True)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            countdown_container,
            text=subtitle_text,
            font=("Segoe UI", 18),
            text_color=self.theme_manager.current_theme["text_color"]
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Event details section
        details_frame = ctk.CTkFrame(content_container, corner_radius=10)
        details_frame.pack(fill="x", padx=15, pady=10)
        
        # Event date
        date_info_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        date_info_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            date_info_frame,
            text="📅 Event Date:",
            font=("Segoe UI", 12, "bold"),
            text_color=self.theme_manager.current_theme["text_color"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            date_info_frame,
            text=event['event_date'],
            font=("Segoe UI", 12),
            text_color=self.theme_manager.current_theme["accent_color"]
        ).pack(side="right")
        
        # Priority info
        priority_info_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        priority_info_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        priority_name = PriorityColorManager.get_priority_name(event['priority'])
        ctk.CTkLabel(
            priority_info_frame,
            text="⭐ Priority:",
            font=("Segoe UI", 12, "bold"),
            text_color=self.theme_manager.current_theme["text_color"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            priority_info_frame,
            text=priority_name,
            font=("Segoe UI", 12, "bold"),
            text_color=priority_color
        ).pack(side="right")
        
        # Description if available
        if event['description']:
            desc_frame = ctk.CTkFrame(details_frame, corner_radius=8)
            desc_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            ctk.CTkLabel(
                desc_frame,
                text="📝 Description:",
                font=("Segoe UI", 12, "bold"),
                text_color=self.theme_manager.current_theme["text_color"]
            ).pack(anchor="w", padx=15, pady=(10, 5))
            
            desc_label = ctk.CTkLabel(
                desc_frame,
                text=event['description'],
                font=("Segoe UI", 11),
                text_color=self.theme_manager.current_theme["text_color"],
                wraplength=400,
                justify="left"
            )
            desc_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Action buttons with enhanced styling
        button_container = ctk.CTkFrame(content_container, fg_color="transparent")
        button_container.pack(fill="x", padx=15, pady=(10, 15))
        
        button_frame = ctk.CTkFrame(button_container, fg_color="transparent")
        button_frame.pack()
        
        edit_btn = ctk.CTkButton(
            button_frame,
            text="✏️ Edit Event",
            command=lambda: self.show_edit_event_dialog(event),
            width=140,
            height=40,
            font=("Segoe UI", 12, "bold"),
            fg_color="#17a2b8",
            hover_color="#138496",
            corner_radius=10
        )
        edit_btn.pack(side="left", padx=8)
        
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Delete",
            command=lambda: self.delete_event(event['id']),
            fg_color="#dc3545",
            hover_color="#c82333",
            width=120,
            height=40,
            font=("Segoe UI", 12, "bold"),
            corner_radius=10
        )
        delete_btn.pack(side="left", padx=8)
        
        # Update system tray
        self.tray_manager.update_icon_with_countdown(days_remaining)
        self.tray_notification_manager.update_tray_tooltip({
            'name': event['name'],
            'days': days_remaining
        })
    
    def refresh_events(self):
        """Refresh the event list"""
        # Clear current event list
        for widget in self.events_scrollable.winfo_children():
            widget.destroy()
        
        # Load events from database
        self.current_events = self.db_manager.get_all_events()
        
        if not self.current_events:
            no_events_label = ctk.CTkLabel(
                self.events_scrollable,
                text="No events yet.\nClick 'Add Event' to get started!",
                font=("Arial", 12),
                text_color=self.theme_manager.current_theme["text_color"]
            )
            no_events_label.pack(pady=20)
        else:
            # Sort events by date
            today = datetime.now().date()
            for event in self.current_events:
                event_date = datetime.strptime(event['event_date'], "%Y-%m-%d").date()
                event['days_remaining'] = (event_date - today).days
            
            # Sort by days remaining (upcoming first), then by priority
            self.current_events.sort(key=lambda x: (x['days_remaining'], -x['priority']))
            
            # Create event cards
            for event in self.current_events:
                self.create_event_card(event)
        
        # Update default countdown display
        self.show_default_countdown()
    
    def create_event_card(self, event):
        """Create a professional card widget for an event"""
        # Enhanced event card with modern styling
        card = ctk.CTkFrame(
            self.events_scrollable, 
            corner_radius=15, 
            height=110,
            fg_color=COLORS["card"],
            border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(fill="x", padx=10, pady=8)
        card.pack_propagate(False)
        
        # Hover effects with modern colors
        def on_enter(e):
            card.configure(
                fg_color=COLORS["hover"],
                border_color=COLORS["accent"]
            )
        
        def on_leave(e):
            card.configure(
                fg_color=COLORS["card"],
                border_color=COLORS["border"]
            )
        
        def on_click(e):
            self.select_event(event)
            
        card.bind("<Button-1>", on_click)
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # Calculate time remaining
        days_remaining = event.get('days_remaining', 0)
        priority_color = PriorityColorManager.get_days_remaining_color(
            days_remaining, event['priority']
        )
        
        # Priority indicator with modern design
        priority_indicator = ctk.CTkFrame(
            card, 
            width=6, 
            corner_radius=3,
            fg_color=priority_color
        )
        priority_indicator.pack(side="left", fill="y", padx=(15, 0), pady=15)
        
        # Main content container
        content_container = ctk.CTkFrame(card, fg_color="transparent")
        content_container.pack(side="left", fill="both", expand=True, padx=20, pady=15)
        
        # Header section with event name and status
        header_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        header_frame.pack(fill="x")
        
        # Event name with professional typography
        event_name = event['name']
        if len(event_name) > 30:
            event_name = event_name[:27] + "..."
            
        name_label = ctk.CTkLabel(
            header_frame,
            text=event_name,
            font=("SF Pro Display", 16, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)
        
        # Status badge with modern styling
        if days_remaining > 0:
            status_text = f"{days_remaining}d"
            badge_color = COLORS["accent"]
        elif days_remaining == 0:
            status_text = "TODAY"
            badge_color = COLORS["warning"]
        else:
            status_text = f"{abs(days_remaining)}d overdue"
            badge_color = COLORS["error"]
        
        status_badge = ctk.CTkLabel(
            header_frame,
            text=status_text,
            font=("SF Pro Display", 11, "bold"),
            text_color="white",
            fg_color=badge_color,
            corner_radius=15,
            width=80,
            height=28
        )
        status_badge.pack(side="right")
        
        # Details section
        details_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        details_frame.pack(fill="x", pady=(8, 0))
        
        # Event date with icon
        event_date = event.get('event_date') or event.get('target_date')
        if isinstance(event_date, str):
            # Parse date string if needed
            from datetime import datetime
            event_date = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
        
        date_str = event_date.strftime("%B %d, %Y")
        date_label = ctk.CTkLabel(
            details_frame,
            text=f"📅 {date_str}",
            font=("SF Pro Display", 12),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        date_label.pack(side="left")
        
        # Priority level with modern indicator
        priority_value = event.get('priority', 'medium')
        
        # Handle both numeric and text priority values
        if isinstance(priority_value, int):
            priority_num_map = {1: "low", 2: "medium", 3: "high", 4: "high", 5: "high"}
            priority_value = priority_num_map.get(priority_value, "medium")
        
        priority_map = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}
        priority_text = priority_map.get(priority_value, str(priority_value))
        
        priority_label = ctk.CTkLabel(
            details_frame,
            text=priority_text,
            font=("SF Pro Display", 11),
            text_color=COLORS["text_secondary"]
        )
        priority_label.pack(side="right")
        
        return card
        
        # Event date
        date_label = ctk.CTkLabel(
            bottom_frame,
            text=f"📅 {event['event_date']}",
            font=("Segoe UI", 11),
            text_color=self.theme_manager.current_theme["text_color"],
            anchor="w"
        )
        date_label.pack(side="left")
        
        # Priority label
        priority_name = PriorityColorManager.get_priority_name(event['priority'])
        priority_label = ctk.CTkLabel(
            bottom_frame,
            text=f"⭐ {priority_name}",
            font=("Segoe UI", 10),
            text_color=priority_color,
            anchor="e"
        )
        priority_label.pack(side="right")
    
    def select_event(self, event):
        """Select an event to show in detail view"""
        self.selected_event_id = event['id']
        self.show_event_countdown(event)
    
    def show_add_event_dialog(self):
        """Show dialog to add new event"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add New Event")
        center_window(dialog, 500, 700)
        dialog.resizable(False, False)
        dialog.configure(fg_color=self.theme_manager.current_theme["window_bg"])
        
        # Center dialog and make it modal
        if self.root:
            dialog.transient(self.root)
            dialog.grab_set()
        
        # Main container with proper padding
        main_container = ctk.CTkFrame(dialog, corner_radius=15)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_container, 
            text="🎯 Create New Event", 
            font=("Segoe UI", 20, "bold"),
            text_color=self.theme_manager.current_theme["accent_color"]
        )
        title_label.pack(pady=(20, 15))
        
        # Form frame with scrollable content - reduced height to leave room for buttons
        form_frame = ctk.CTkScrollableFrame(main_container, height=450)
        form_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Event name section
        name_section = ctk.CTkFrame(form_frame, corner_radius=10)
        name_section.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(name_section, text="📝 Event Name:", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        name_entry = ctk.CTkEntry(
            name_section, 
            width=380, 
            height=40,
            placeholder_text="Enter your event name...",
            font=("Segoe UI", 12),
            corner_radius=8
        )
        name_entry.pack(padx=15, pady=(0, 15))
        
        # Event description section
        desc_section = ctk.CTkFrame(form_frame, corner_radius=10)
        desc_section.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(desc_section, text="📄 Description (Optional):", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        desc_entry = ctk.CTkTextbox(
            desc_section, 
            width=380, 
            height=80,
            font=("Segoe UI", 11),
            corner_radius=8
        )
        desc_entry.pack(padx=15, pady=(0, 15))
        
        # Event date section
        date_section = ctk.CTkFrame(form_frame, corner_radius=10)
        date_section.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(date_section, text="📅 Event Date:", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        # Date input with example
        date_frame = ctk.CTkFrame(date_section, fg_color="transparent")
        date_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        date_entry = ctk.CTkEntry(
            date_frame, 
            width=280, 
            height=40,
            placeholder_text="YYYY-MM-DD",
            font=("Segoe UI", 12),
            corner_radius=8
        )
        date_entry.pack(side="left")
        
        ctk.CTkLabel(date_frame, text="Example: 2025-12-31", font=("Segoe UI", 10), text_color="gray").pack(side="left", padx=(10, 0), pady=10)
        
        # Priority section
        priority_section = ctk.CTkFrame(form_frame, corner_radius=10)
        priority_section.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(priority_section, text="⭐ Priority Level:", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        priority_var = ctk.StringVar(value="Medium")
        priority_menu = ctk.CTkOptionMenu(
            priority_section,
            variable=priority_var,
            values=["Low", "Medium", "High", "Critical", "Urgent"],
            width=380,
            height=40,
            font=("Segoe UI", 12),
            corner_radius=8
        )
        priority_menu.pack(padx=15, pady=(0, 15))
        
        # Notifications section
        notif_section = ctk.CTkFrame(form_frame, corner_radius=10)
        notif_section.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(notif_section, text="🔔 Notification Settings:", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        notification_var = ctk.BooleanVar(value=True)
        notification_check = ctk.CTkCheckBox(
            notif_section,
            text="Enable notifications for this event",
            variable=notification_var,
            font=("Segoe UI", 12),
            corner_radius=6
        )
        notification_check.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Notification timing
        ctk.CTkLabel(notif_section, text="Notify me this many days before:", font=("Segoe UI", 12)).pack(anchor="w", padx=15, pady=(5, 5))
        notify_days_var = ctk.StringVar(value="1")
        notify_days_menu = ctk.CTkOptionMenu(
            notif_section,
            variable=notify_days_var,
            values=["1", "2", "3", "5", "7", "14", "30"],
            width=380,
            height=35,
            font=("Segoe UI", 11),
            corner_radius=8
        )
        notify_days_menu.pack(padx=15, pady=(0, 15))
        
        # FIXED: Action buttons placed outside scrollable frame for visibility
        button_container = ctk.CTkFrame(main_container, fg_color="transparent", height=60)
        button_container.pack(fill="x", pady=(0, 15))
        button_container.pack_propagate(False)
        
        def save_event():
            name = name_entry.get().strip()
            description = desc_entry.get("1.0", "end-1c").strip()
            date_str = date_entry.get().strip()
            
            if not name or not date_str:
                messagebox.showerror("Error", "Please fill in Event Name and Date fields.")
                return
            
            try:
                # Validate date format
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Please use YYYY-MM-DD date format (e.g., 2025-12-31).")
                return
            
            # Convert priority to number
            priority_map = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4, "Urgent": 5}
            priority = priority_map[priority_var.get()]
            
            # Save to database
            self.db_manager.add_event(
                name=name,
                event_date=date_str,
                description=description,
                notification_enabled=notification_var.get(),
                notification_days_before=int(notify_days_var.get()),
                priority=priority
            )
            
            dialog.destroy()
            self.refresh_events()
            messagebox.showinfo("Success", f"Event '{name}' added successfully!")
        
        # Buttons with enhanced styling - now properly visible
        button_frame = ctk.CTkFrame(button_container, fg_color="transparent")
        button_frame.pack(expand=True)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Event",
            command=save_event,
            fg_color="#28a745",
            hover_color="#218838",
            width=160,
            height=45,
            font=("Segoe UI", 14, "bold"),
            corner_radius=10
        )
        save_btn.pack(side="left", padx=10, pady=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            fg_color="#6c757d",
            hover_color="#5a6268",
            width=130,
            height=45,
            font=("Segoe UI", 14),
            corner_radius=10
        )
        cancel_btn.pack(side="left", padx=10, pady=10)
        
        # Focus on name entry and bind Enter key
        name_entry.focus()
        dialog.bind("<Return>", lambda e: save_event())
    
    def show_edit_event_dialog(self, event):
        """Show dialog to edit existing event"""
        # Similar to add event dialog but pre-filled with event data
        # Implementation would be similar to show_add_event_dialog
        # but with fields pre-populated and update instead of create
        pass
    
    def delete_event(self, event_id):
        """Delete an event with confirmation"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this event?"):
            self.db_manager.delete_event(event_id)
            self.refresh_events()
            messagebox.showinfo("Success", "Event deleted successfully!")
    
    def show_theme_selector(self):
        """Show theme selection dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Choose Theme")
        center_window(dialog, 500, 400)
        dialog.resizable(False, False)
        dialog.configure(fg_color=self.theme_manager.current_theme["window_bg"])
        
        if self.root:
            dialog.transient(self.root)
            dialog.grab_set()
        
        # Main container
        main_container = ctk.CTkFrame(dialog, corner_radius=15)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_container,
            text="🎨 Choose Your Theme",
            font=("Segoe UI", 20, "bold"),
            text_color=self.theme_manager.current_theme["accent_color"]
        )
        title_label.pack(pady=(20, 25))
        
        # Theme grid
        themes_frame = ctk.CTkScrollableFrame(main_container, height=250)
        themes_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        available_themes = self.theme_manager.get_available_themes()
        current_theme_id = self.theme_manager.db_manager.get_setting("current_theme", "light")
        
        def apply_theme(theme_id):
            self.theme_manager.set_current_theme(theme_id)
            self.apply_theme()
            self.refresh_events()
            dialog.destroy()
            messagebox.showinfo("Theme Applied", f"Theme '{theme_id}' has been applied successfully!")
        
        # Create theme buttons in a grid
        for i, theme in enumerate(available_themes):
            theme_frame = ctk.CTkFrame(themes_frame, corner_radius=10)
            theme_frame.pack(fill="x", pady=8, padx=5)
            
            # Theme preview colors
            colors_frame = ctk.CTkFrame(theme_frame, height=40, corner_radius=8)
            colors_frame.pack(fill="x", padx=15, pady=(15, 10))
            colors_frame.pack_propagate(False)
            
            # Color preview strips
            for j, color in enumerate([theme['preview_colors']['bg'], 
                                     theme['preview_colors']['text'], 
                                     theme['preview_colors']['accent']]):
                color_strip = ctk.CTkFrame(colors_frame, fg_color=color, width=40)
                color_strip.pack(side="left", fill="y", padx=2, pady=5)
            
            # Theme info
            info_frame = ctk.CTkFrame(theme_frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            # Theme name
            name_label = ctk.CTkLabel(
                info_frame,
                text=theme['name'],
                font=("Segoe UI", 14, "bold"),
                text_color=self.theme_manager.current_theme["text_color"]
            )
            name_label.pack(side="left")
            
            # Current theme indicator
            if theme['id'] == current_theme_id:
                current_label = ctk.CTkLabel(
                    info_frame,
                    text="✓ Current",
                    font=("Segoe UI", 11, "bold"),
                    text_color="#28a745"
                )
                current_label.pack(side="right")
            else:
                # Apply button
                apply_btn = ctk.CTkButton(
                    info_frame,
                    text="Apply",
                    command=lambda t=theme['id']: apply_theme(t),
                    width=80,
                    height=30,
                    font=("Segoe UI", 11),
                    corner_radius=6
                )
                apply_btn.pack(side="right")
        
        # Close button
        close_btn = ctk.CTkButton(
            main_container,
            text="Close",
            command=dialog.destroy,
            width=100,
            height=35,
            font=("Segoe UI", 12),
            fg_color="#6c757d",
            hover_color="#5a6268",
            corner_radius=8
        )
        close_btn.pack(pady=(15, 20))
    
    def show_settings_dialog(self):
        """Show settings dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Settings")
        center_window(dialog, 400, 300)
        dialog.resizable(False, False)
        dialog.configure(fg_color=self.theme_manager.current_theme["window_bg"])
        
        if self.root:
            dialog.transient(self.root)
            dialog.grab_set()
        
        # Main container
        main_container = ctk.CTkFrame(dialog, corner_radius=15)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_container,
            text="⚙️ Settings",
            font=("Segoe UI", 20, "bold"),
            text_color=self.theme_manager.current_theme["accent_color"]
        )
        title_label.pack(pady=(20, 25))
        
        # Settings options
        settings_frame = ctk.CTkFrame(main_container, corner_radius=10)
        settings_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Test notification button
        test_notif_btn = ctk.CTkButton(
            settings_frame,
            text="🔔 Test Notifications",
            command=self.notification_manager.send_test_notification,
            width=200,
            height=40,
            font=("Segoe UI", 12),
            corner_radius=8
        )
        test_notif_btn.pack(pady=20)
        
        # About section
        about_label = ctk.CTkLabel(
            settings_frame,
            text="Enhanced Countdown Widget v2.0\nBuilt with CustomTkinter",
            font=("Segoe UI", 11),
            text_color=self.theme_manager.current_theme["text_color"],
            justify="center"
        )
        about_label.pack(pady=10)
        
        # Close button
        close_btn = ctk.CTkButton(
            main_container,
            text="Close",
            command=dialog.destroy,
            width=100,
            height=35,
            font=("Segoe UI", 12),
            fg_color="#6c757d",
            hover_color="#5a6268",
            corner_radius=8
        )
        close_btn.pack(pady=(15, 20))
    
    def apply_theme(self):
        """Apply current theme to the application"""
        if not self.root:
            return
        
        theme = self.theme_manager.current_theme
        self.root.configure(fg_color=theme["window_bg"])
    
    def minimize_to_tray(self):
        """Minimize application to system tray"""
        if self.root:
            self.root.withdraw()
    
    def quit_application(self):
        """Quit the application completely"""
        self.notification_manager.stop_monitoring()
        self.tray_manager.stop()
        
        if self.root:
            self.root.quit()
        
        sys.exit()
    
    def export_events(self):
        """Export events to JSON file"""
        try:
            from tkinter import filedialog
            import json
            
            events = self.db_manager.get_all_events()
            if not events:
                messagebox.showinfo("Export", "No events to export.")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                # Convert datetime objects to strings for JSON serialization
                export_data = []
                for event in events:
                    event_data = event.copy()
                    if 'target_date' in event_data:
                        event_data['target_date'] = event_data['target_date'].isoformat()
                    export_data.append(event_data)
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                messagebox.showinfo("Export Complete", f"Events exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export events: {str(e)}")
    
    def import_events(self):
        """Import events from JSON file"""
        try:
            from tkinter import filedialog
            import json
            from datetime import datetime
            
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    import_data = json.load(f)
                
                imported_count = 0
                for event_data in import_data:
                    try:
                        # Convert date string back to datetime
                        if 'target_date' in event_data:
                            event_data['target_date'] = datetime.fromisoformat(event_data['target_date'])
                        
                        # Remove ID to create new events
                        if 'id' in event_data:
                            del event_data['id']
                        
                        self.db_manager.add_event(
                            event_data['name'],
                            event_data['target_date'],
                            event_data.get('priority', 'medium'),
                            event_data.get('description', '')
                        )
                        imported_count += 1
                    except Exception as e:
                        print(f"Failed to import event: {e}")
                        continue
                
                self.refresh_events()
                messagebox.showinfo("Import Complete", f"Successfully imported {imported_count} events.")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import events: {str(e)}")

def main():
    """Main application entry point"""
    app = CountdownApp()

if __name__ == "__main__":
    main()
