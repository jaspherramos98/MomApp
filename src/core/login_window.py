import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
import sys
import os

# Add the parent directory to the Python path to import auth module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import authentication module
try:
    from src.core.auth import authenticate_user, register_user, hash_password
except ImportError:
    # Fallback if auth module structure is different
    try:
        from core.auth import authenticate_user, register_user, hash_password
    except ImportError:
        print("Warning: Auth module not found. Using demo mode.")
        # Demo mode functions
        def authenticate_user(username, password):
            return username == "demo" and password == "demo"
        def register_user(username, password, **kwargs):
            return True
        def hash_password(password):
            return password

class ModernMomApp:
    def __init__(self, parent_app=None):
        self.parent_app = parent_app  # Reference to main application
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        self.current_tab = "login"
        self.login_successful = False  # Track if login was successful
        
        # For window dragging
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._dragging = False
        
        # For window resizing
        self._resize_edge = None
        self._resize_start_x = 0
        self._resize_start_y = 0
        self._resize_start_width = 0
        self._resize_start_height = 0
        self.edge_size = 8  # Pixels from edge to trigger resize
        
        # Track login status
        self.login_successful = False
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # Notification system
        self.notification_frame = None
        self.notification_label = None
        
    def setup_window(self):
        self.root.title("Mom App - Login")
        self.root.geometry("450x700")  # Increased height from 640 to 700
        self.root.minsize(350, 600)  # Increased min height from 500 to 600
        self.root.resizable(True, True)  # Make window resizable
        
        # Remove window decorations (borderless window)
        self.root.overrideredirect(True)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)  # Updated with new height
        self.root.geometry(f"450x700+{x}+{y}")
        
        # Dark mode color scheme
        self.colors = {
            'bg': '#1a1a1a',           # Dark background
            'card_bg': '#2d2d2d',      # Card background
            'primary': '#667eea',       # Primary accent
            'primary_hover': '#5a6fd8', # Primary hover
            'secondary': '#764ba2',     # Secondary accent
            'text': '#ffffff',          # White text
            'text_light': '#b0b0b0',   # Light gray text
            'text_muted': '#808080',   # Muted text
            'border': '#404040',       # Border color
            'input_bg': '#3a3a3a',     # Input background
            'success': '#48bb78',      # Success green
            'error': '#f56565',        # Error red
            'warning': '#ed8936',      # Warning orange
            'info': '#4299e1',         # Info blue
            'title_bar': '#1a1a1a',    # Title bar background
            'close_hover': '#dc3545',  # Close button hover
            'minimize_hover': '#ffc107' # Minimize button hover
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Set window to stay on top initially (optional)
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        
    def setup_styles(self):
        # Custom fonts
        self.fonts = {
            'title': tkFont.Font(family='Segoe UI', size=24, weight='normal'),
            'subtitle': tkFont.Font(family='Segoe UI', size=10),
            'heading': tkFont.Font(family='Segoe UI', size=12, weight='bold'),
            'body': tkFont.Font(family='Segoe UI', size=10),
            'button': tkFont.Font(family='Segoe UI', size=11, weight='bold'),
            'title_bar': tkFont.Font(family='Segoe UI', size=9),
            'notification': tkFont.Font(family='Segoe UI', size=9)
        }
        
    def create_widgets(self):
        # Create custom title bar
        self.create_title_bar()
        
        # Main container with resize handle
        self.main_container = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_container.pack(fill='both', expand=True)
        
        # Create notification area (initially hidden)
        self.create_notification_area()
        
        # Bind resize events to main container edges
        self.setup_resize_bindings()
        
        # Main content frame
        main_frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=40, pady=(0, 40))
        
        # Card container with subtle border
        self.card = tk.Frame(main_frame, 
                            bg=self.colors['card_bg'],
                            relief='solid',
                            bd=1,
                            highlightbackground=self.colors['border'],
                            highlightthickness=1)
        self.card.pack(fill='both', expand=True)
        
        # Title section
        self.create_title_section()
        
        # Tab section
        self.create_tab_section()
        
        # Form sections
        self.create_login_form()
        self.create_register_form()
        
        # Show login form by default
        self.show_login_form()
        
    def create_notification_area(self):
        """Create the notification area that slides down from the top"""
        try:
            self.notification_frame = tk.Frame(self.main_container, 
                                             bg=self.colors['info'],
                                             height=40)
            
            self.notification_label = tk.Label(self.notification_frame,
                                             text="",
                                             font=self.fonts['notification'],
                                             fg='white',
                                             bg=self.colors['info'])
            self.notification_label.pack(expand=True, fill='both', padx=10, pady=8)
            
            # Don't pack initially - will be shown when needed
        except Exception as e:
            print(f"Error creating notification area: {e}")
            self.notification_frame = None
            self.notification_label = None
        
    def show_notification(self, message, type='info', duration=3000):
        """Show a notification at the top of the window"""
        # Check if notification area exists
        if not self.notification_frame or not self.notification_label:
            print(f"Notification: [{type}] {message}")
            return
            
        # Set the background color based on type
        bg_color = {
            'success': self.colors['success'],
            'error': self.colors['error'],
            'warning': self.colors['warning'],
            'info': self.colors['info']
        }.get(type, self.colors['info'])
        
        self.notification_frame.configure(bg=bg_color)
        self.notification_label.configure(bg=bg_color, text=message)
        
        # Show the notification
        self.notification_frame.pack(fill='x', before=self.main_container.winfo_children()[0])
        
        # Auto-hide after duration
        self.root.after(duration, self.hide_notification)
        
    def hide_notification(self):
        """Hide the notification"""
        self.notification_frame.pack_forget()
        
    def create_title_bar(self):
        # Custom title bar
        self.title_bar = tk.Frame(self.root, bg=self.colors['title_bar'], height=32)
        self.title_bar.pack(fill='x')
        self.title_bar.pack_propagate(False)
        
        # Title bar content frame
        title_content = tk.Frame(self.title_bar, bg=self.colors['title_bar'])
        title_content.pack(fill='both', expand=True)
        
        # App icon and title
        title_frame = tk.Frame(title_content, bg=self.colors['title_bar'])
        title_frame.pack(side='left', padx=10)
        
        # Icon (using a simple text icon)
        icon_label = tk.Label(title_frame,
                             text="👨‍👩‍👧‍👦",
                             font=('Segoe UI', 12),
                             bg=self.colors['title_bar'])
        icon_label.pack(side='left', padx=(0, 8))
        
        title_label = tk.Label(title_frame,
                              text="Mom App - Login",
                              font=self.fonts['title_bar'],
                              fg=self.colors['text_light'],
                              bg=self.colors['title_bar'])
        title_label.pack(side='left')
        
        # Window controls frame
        controls_frame = tk.Frame(title_content, bg=self.colors['title_bar'])
        controls_frame.pack(side='right')
        
        # Close button
        close_btn = tk.Button(controls_frame,
                             text="✕",
                             font=('Segoe UI', 10),
                             fg=self.colors['text_light'],
                             bg=self.colors['title_bar'],
                             activebackground=self.colors['close_hover'],
                             activeforeground='white',
                             bd=0,
                             padx=12,
                             pady=4,
                             cursor='hand2',
                             command=self.on_window_close)
        close_btn.pack(side='right')
        
        # Minimize button
        minimize_btn = tk.Button(controls_frame,
                               text="—",
                               font=('Segoe UI', 10),
                               fg=self.colors['text_light'],
                               bg=self.colors['title_bar'],
                               activebackground=self.colors['minimize_hover'],
                               activeforeground='black',
                               bd=0,
                               padx=12,
                               pady=4,
                               cursor='hand2',
                               command=self.minimize_window)
        minimize_btn.pack(side='right')
        
        # Hover effects for buttons
        def on_close_enter(e):
            close_btn.configure(bg=self.colors['close_hover'], fg='white')
        def on_close_leave(e):
            close_btn.configure(bg=self.colors['title_bar'], fg=self.colors['text_light'])
            
        def on_minimize_enter(e):
            minimize_btn.configure(bg=self.colors['minimize_hover'], fg='black')
        def on_minimize_leave(e):
            minimize_btn.configure(bg=self.colors['title_bar'], fg=self.colors['text_light'])
        
        close_btn.bind('<Enter>', on_close_enter)
        close_btn.bind('<Leave>', on_close_leave)
        minimize_btn.bind('<Enter>', on_minimize_enter)
        minimize_btn.bind('<Leave>', on_minimize_leave)
        
        # Make ENTIRE title bar draggable (except buttons)
        self.title_bar.bind('<Button-1>', self.start_drag)
        self.title_bar.bind('<B1-Motion>', self.drag_window)
        self.title_bar.bind('<ButtonRelease-1>', self.stop_drag)
        title_content.bind('<Button-1>', self.start_drag)
        title_content.bind('<B1-Motion>', self.drag_window)
        title_content.bind('<ButtonRelease-1>', self.stop_drag)
        title_frame.bind('<Button-1>', self.start_drag)
        title_frame.bind('<B1-Motion>', self.drag_window)
        title_frame.bind('<ButtonRelease-1>', self.stop_drag)
        title_label.bind('<Button-1>', self.start_drag)
        title_label.bind('<B1-Motion>', self.drag_window)
        title_label.bind('<ButtonRelease-1>', self.stop_drag)
        icon_label.bind('<Button-1>', self.start_drag)
        icon_label.bind('<B1-Motion>', self.drag_window)
        icon_label.bind('<ButtonRelease-1>', self.stop_drag)
        
    def start_drag(self, event):
        self._dragging = True
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        
    def drag_window(self, event):
        if self._dragging:
            x = self.root.winfo_x() - self._drag_start_x + event.x
            y = self.root.winfo_y() - self._drag_start_y + event.y
            self.root.geometry(f"+{x}+{y}")
        
    def stop_drag(self, event):
        self._dragging = False
        
    def minimize_window(self):
        self.root.iconify()
        
    def setup_resize_bindings(self):
        """Setup edge detection and resize bindings"""
        # Bind mouse events for resize detection
        self.root.bind('<Motion>', self.check_resize_cursor)
        self.root.bind('<Button-1>', self.start_resize)
        self.root.bind('<B1-Motion>', self.do_resize)
        self.root.bind('<ButtonRelease-1>', self.stop_resize)
        
        # Create invisible resize grip in bottom right corner
        resize_grip = tk.Label(self.root, text="◢", 
                              font=('Segoe UI', 12),
                              fg=self.colors['text_muted'],
                              bg=self.colors['bg'],
                              cursor='size_nw_se')
        resize_grip.place(relx=1.0, rely=1.0, anchor='se')
        
    def check_resize_cursor(self, event):
        """Change cursor when near window edges"""
        if hasattr(self, '_resizing') and self._resizing:
            return
            
        x, y = event.x, event.y
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # Determine which edge we're near
        edge = self.get_edge(x, y, width, height)
        
        # Set appropriate cursor
        cursors = {
            'top': 'size_ns',
            'bottom': 'size_ns',
            'left': 'size_we',
            'right': 'size_we',
            'top-left': 'size_nw_se',
            'top-right': 'size_ne_sw',
            'bottom-left': 'size_ne_sw',
            'bottom-right': 'size_nw_se'
        }
        
        if edge:
            self.root.configure(cursor=cursors.get(edge, ''))
        else:
            self.root.configure(cursor='')
            
    def get_edge(self, x, y, width, height):
        """Determine which edge the cursor is near"""
        edge = ''
        if x < self.edge_size:
            edge = 'left'
        elif x > width - self.edge_size:
            edge = 'right'
            
        if y < self.edge_size:
            edge = 'top' if not edge else f'top-{edge}'
        elif y > height - self.edge_size:
            edge = 'bottom' if not edge else f'bottom-{edge}'
            
        return edge
        
    def start_resize(self, event):
        """Start resizing if on edge"""
        x, y = event.x, event.y
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        self._resize_edge = self.get_edge(x, y, width, height)
        
        if self._resize_edge:
            self._resizing = True
            self._resize_start_x = self.root.winfo_pointerx()
            self._resize_start_y = self.root.winfo_pointery()
            self._resize_start_width = width
            self._resize_start_height = height
            self._resize_start_root_x = self.root.winfo_x()
            self._resize_start_root_y = self.root.winfo_y()
            
    def do_resize(self, event):
        """Handle window resizing"""
        if hasattr(self, '_resizing') and self._resizing and self._resize_edge:
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            
            dx = x - self._resize_start_x
            dy = y - self._resize_start_y
            
            new_width = self._resize_start_width
            new_height = self._resize_start_height
            new_x = self._resize_start_root_x
            new_y = self._resize_start_root_y
            
            # Calculate new dimensions based on edge
            if 'right' in self._resize_edge:
                new_width = max(self.root.minsize()[0], self._resize_start_width + dx)
            if 'left' in self._resize_edge:
                new_width = max(self.root.minsize()[0], self._resize_start_width - dx)
                new_x = self._resize_start_root_x + (self._resize_start_width - new_width)
            if 'bottom' in self._resize_edge:
                new_height = max(self.root.minsize()[1], self._resize_start_height + dy)
            if 'top' in self._resize_edge:
                new_height = max(self.root.minsize()[1], self._resize_start_height - dy)
                new_y = self._resize_start_root_y + (self._resize_start_height - new_height)
                
            self.root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
            
    def stop_resize(self, event):
        """Stop resizing"""
        self._resizing = False
        self._resize_edge = None
        
    def create_title_section(self):
        title_frame = tk.Frame(self.card, bg=self.colors['card_bg'])
        title_frame.pack(pady=(30, 20))
        
        # Main title
        title_label = tk.Label(title_frame,
                              text="Mom App",
                              font=self.fonts['title'],
                              fg=self.colors['primary'],
                              bg=self.colors['card_bg'])
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(title_frame,
                                 text="Your family's digital companion",
                                 font=self.fonts['subtitle'],
                                 fg=self.colors['text_light'],
                                 bg=self.colors['card_bg'])
        subtitle_label.pack(pady=(5, 0))
        
    def create_tab_section(self):
        tab_frame = tk.Frame(self.card, bg=self.colors['card_bg'])
        tab_frame.pack(pady=(0, 30), padx=30, fill='x')
        
        # Tab container with background
        tab_container = tk.Frame(tab_frame, bg=self.colors['border'], relief='flat', bd=0)
        tab_container.pack(fill='x')
        
        # Tab buttons
        self.login_tab_btn = tk.Button(tab_container,
                                      text="Login",
                                      font=self.fonts['body'],
                                      fg=self.colors['primary'],
                                      bg=self.colors['card_bg'],
                                      activebackground=self.colors['card_bg'],
                                      activeforeground=self.colors['primary'],
                                      relief='flat',
                                      bd=0,
                                      cursor='hand2',
                                      command=lambda: self.switch_tab('login'))
        self.login_tab_btn.pack(side='left', fill='x', expand=True, padx=2, pady=2, ipady=8)
        
        self.register_tab_btn = tk.Button(tab_container,
                                         text="Register",
                                         font=self.fonts['body'],
                                         fg=self.colors['text_light'],
                                         bg=self.colors['border'],
                                         activebackground=self.colors['border'],
                                         activeforeground=self.colors['text_light'],
                                         relief='flat',
                                         bd=0,
                                         cursor='hand2',
                                         command=lambda: self.switch_tab('register'))
        self.register_tab_btn.pack(side='right', fill='x', expand=True, padx=2, pady=2, ipady=8)
        
    def create_login_form(self):
        self.login_frame = tk.Frame(self.card, bg=self.colors['card_bg'])
        
        # Username field
        self.create_input_field(self.login_frame, "Username", "login_username", show=None)
        
        # Password field
        self.create_input_field(self.login_frame, "Password", "login_password", show="*")
        
        # Login button
        login_btn = tk.Button(self.login_frame,
                             text="Sign In",
                             font=self.fonts['button'],
                             fg='white',
                             bg=self.colors['primary'],
                             activebackground=self.colors['primary_hover'],
                             activeforeground='white',
                             relief='flat',
                             bd=0,
                             cursor='hand2',
                             command=self.handle_login)
        login_btn.pack(pady=(20, 10), padx=30, fill='x', ipady=12)
        
        # Add hover effects
        login_btn.bind('<Enter>', lambda e: login_btn.configure(bg=self.colors['primary_hover']))
        login_btn.bind('<Leave>', lambda e: login_btn.configure(bg=self.colors['primary']))
        
        # Forgot password link
        forgot_btn = tk.Button(self.login_frame,
                              text="Forgot your password?",
                              font=self.fonts['body'],
                              fg=self.colors['primary'],
                              bg=self.colors['card_bg'],
                              activebackground=self.colors['card_bg'],
                              activeforeground=self.colors['primary_hover'],
                              relief='flat',
                              bd=0,
                              cursor='hand2',
                              command=self.forgot_password)
        forgot_btn.pack(pady=(10, 0))
        
    def create_register_form(self):
        self.register_frame = tk.Frame(self.card, bg=self.colors['card_bg'])
        
        # Username field
        self.create_input_field(self.register_frame, "Username", "reg_username", show=None)
        
        # Password field
        self.create_input_field(self.register_frame, "Password", "reg_password", show="*")
        
        # Confirm password field
        self.create_input_field(self.register_frame, "Confirm Password", "confirm_password", show="*")
        
        # Age field
        age_frame = tk.Frame(self.register_frame, bg=self.colors['card_bg'])
        age_frame.pack(fill='x', padx=30, pady=(0, 15))
        
        age_label = tk.Label(age_frame,
                            text="Age",
                            font=self.fonts['body'],
                            fg=self.colors['text'],
                            bg=self.colors['card_bg'])
        age_label.pack(anchor='w', pady=(0, 5))
        
        self.age_entry = tk.Entry(age_frame,
                                 font=self.fonts['body'],
                                 relief='solid',
                                 bd=1,
                                 bg=self.colors['input_bg'],
                                 fg=self.colors['text'],
                                 insertbackground=self.colors['text'],
                                 highlightbackground=self.colors['border'],
                                 highlightcolor=self.colors['primary'],
                                 width=10)
        self.age_entry.pack(anchor='w', ipady=8, ipadx=10)
        
        # Register button
        register_btn = tk.Button(self.register_frame,
                                text="Create Account",
                                font=self.fonts['button'],
                                fg='white',
                                bg=self.colors['primary'],
                                activebackground=self.colors['primary_hover'],
                                activeforeground='white',
                                relief='flat',
                                bd=0,
                                cursor='hand2',
                                command=self.handle_register)
        register_btn.pack(pady=(20, 10), padx=30, fill='x', ipady=12)
        
        # Add hover effects
        register_btn.bind('<Enter>', lambda e: register_btn.configure(bg=self.colors['primary_hover']))
        register_btn.bind('<Leave>', lambda e: register_btn.configure(bg=self.colors['primary']))
        
    def create_input_field(self, parent, label_text, var_name, show=None):
        field_frame = tk.Frame(parent, bg=self.colors['card_bg'])
        field_frame.pack(fill='x', padx=30, pady=(0, 15))
        
        # Label
        label = tk.Label(field_frame,
                        text=label_text,
                        font=self.fonts['body'],
                        fg=self.colors['text'],
                        bg=self.colors['card_bg'])
        label.pack(anchor='w', pady=(0, 5))
        
        # Entry with dark theme
        entry = tk.Entry(field_frame,
                        font=self.fonts['body'],
                        relief='solid',
                        bd=1,
                        bg=self.colors['input_bg'],
                        fg=self.colors['text'],
                        insertbackground=self.colors['text'],
                        highlightbackground=self.colors['border'],
                        highlightcolor=self.colors['primary'],
                        show=show)
        entry.pack(fill='x', ipady=10, ipadx=15)
        
        # Store reference to entry widget
        setattr(self, f"{var_name}_entry", entry)
        
        # Bind focus events for visual feedback
        entry.bind('<FocusIn>', lambda e: self.on_entry_focus(e, True))
        entry.bind('<FocusOut>', lambda e: self.on_entry_focus(e, False))
        
    def on_entry_focus(self, event, focused):
        if focused:
            event.widget.configure(highlightbackground=self.colors['primary'],
                                 highlightcolor=self.colors['primary'],
                                 highlightthickness=2)
        else:
            event.widget.configure(highlightbackground=self.colors['border'],
                                 highlightthickness=1)
            
    def switch_tab(self, tab):
        self.current_tab = tab
        
        if tab == 'login':
            # Active login tab
            self.login_tab_btn.configure(
                fg=self.colors['primary'],
                bg=self.colors['card_bg']
            )
            # Inactive register tab
            self.register_tab_btn.configure(
                fg=self.colors['text_light'],
                bg=self.colors['border']
            )
            self.show_login_form()
        else:
            # Inactive login tab
            self.login_tab_btn.configure(
                fg=self.colors['text_light'],
                bg=self.colors['border']
            )
            # Active register tab
            self.register_tab_btn.configure(
                fg=self.colors['primary'],
                bg=self.colors['card_bg']
            )
            self.show_register_form()
            
    def show_login_form(self):
        self.register_frame.pack_forget()
        self.login_frame.pack(fill='x', pady=(0, 30))
        
    def show_register_form(self):
        self.login_frame.pack_forget()
        self.register_frame.pack(fill='x', pady=(0, 30))
        
    def handle_login(self):
        username = self.login_username_entry.get().strip()
        password = self.login_password_entry.get().strip()
        
        if not username or not password:
            self.show_notification("Please fill in all fields", 'error')
            return
        
        try:
            # Use the auth module to authenticate
            if authenticate_user(username, password):
                self.show_notification(f"Welcome back, {username}! 👋", 'success')
                
                # Set login success flag
                self.login_successful = True
                
                # Store username for parent app
                self.logged_in_username = username
                
                # Wait a moment for notification to be seen, then close
                self.root.after(1500, self.close_and_proceed)
                
            else:
                self.show_notification("Invalid username or password", 'error')
                # Clear password field for security
                self.login_password_entry.delete(0, tk.END)
                
        except Exception as e:
            self.show_notification(f"Authentication error: {str(e)}", 'error')
            print(f"Login error: {e}")
    
    def close_and_proceed(self):
        """Close login window and proceed to main app"""
        self.root.destroy()
        
        # If integrated with main app, you can call:
        if self.parent_app:
            self.parent_app.on_login_success(self.logged_in_username)
        
    def handle_register(self):
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        age = self.age_entry.get().strip()
        
        if not all([username, password, confirm_password, age]):
            self.show_notification("Please fill in all fields", 'error')
            return
            
        if password != confirm_password:
            self.show_notification("Passwords do not match", 'error')
            return
            
        try:
            age_int = int(age)
            if age_int < 13 or age_int > 120:
                self.show_notification("Please enter a valid age (13-120)", 'error')
                return
        except ValueError:
            self.show_notification("Please enter a valid age", 'error')
            return
        
        try:
            # Use the auth module to register user
            if register_user(username, password, age=age_int):
                self.show_notification(f"Account created successfully! 🎉", 'success')
                
                # Wait a bit then switch to login tab
                self.root.after(1500, lambda: self.switch_tab('login'))
                self.root.after(1600, self.clear_register_form)
                
                # Auto-fill username in login form
                self.root.after(1700, lambda: self.login_username_entry.insert(0, username))
            else:
                self.show_notification("Username already exists", 'error')
                
        except Exception as e:
            self.show_notification(f"Registration error: {str(e)}", 'error')
            print(f"Registration error: {e}")
        
    def clear_register_form(self):
        self.reg_username_entry.delete(0, tk.END)
        self.reg_password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        
    def forgot_password(self):
        self.show_notification("Password recovery coming soon!", 'info')
        
    def on_window_close(self):
        """Handle window close event - properly exit the application"""
        # If login wasn't successful and parent app exists, exit the entire application
        if not self.login_successful and self.parent_app:
            # Call the parent app's emergency shutdown or exit method
            if hasattr(self.parent_app, 'emergency_shutdown'):
                self.parent_app.emergency_shutdown()
            elif hasattr(self.parent_app, 'app'):
                # Quit the Qt application
                self.parent_app.app.quit()
        
        # Destroy the tkinter window
        self.root.destroy()
        
        # Exit the application if no login occurred
        if not self.login_successful:
            import sys
            sys.exit(0)
        
    def run(self):
        self.root.mainloop()

# For standalone testing
if __name__ == "__main__":
    app = ModernMomApp()
    app.run()