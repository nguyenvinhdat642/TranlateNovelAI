"""
Custom dialogs và notifications cho TranslateNovelAI
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import threading
import time

class ModernMessageBox:
    """Custom MessageBox với giao diện hiện đại"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.result = None
        
    def show_success(self, title="Thành công", message="Thao tác đã hoàn thành!", details=None):
        """Hiển thị dialog thành công"""
        return self._show_dialog("success", title, message, details)
    
    def show_error(self, title="Lỗi", message="Đã xảy ra lỗi!", details=None):
        """Hiển thị dialog lỗi"""
        return self._show_dialog("error", title, message, details)
    
    def show_warning(self, title="Cảnh báo", message="Vui lòng kiểm tra!", details=None):
        """Hiển thị dialog cảnh báo"""
        return self._show_dialog("warning", title, message, details)
    
    def show_question(self, title="Xác nhận", message="Bạn có chắc chắn?", details=None):
        """Hiển thị dialog hỏi yes/no"""
        return self._show_dialog("question", title, message, details, show_cancel=True)
    
    def _show_dialog(self, dialog_type, title, message, details=None, show_cancel=False):
        """Hiển thị dialog tùy chỉnh"""
        
        # Tạo cửa sổ
        dialog = ctk.CTkToplevel(self.parent) if self.parent else ctk.CTk()
        dialog.title(title)
        dialog.geometry("450x300")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.parent) if self.parent else None
        dialog.grab_set()
        
        # Configure window
        if self.parent:
            # Center relative to parent
            dialog.geometry(f"+{self.parent.winfo_x() + 50}+{self.parent.winfo_y() + 50}")
        else:
            # Center on screen
            dialog.geometry(f"+{dialog.winfo_screenwidth()//2 - 225}+{dialog.winfo_screenheight()//2 - 150}")
        
        # Main frame
        main_frame = ctk.CTkFrame(dialog, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header frame with icon and title
        header_frame = ctk.CTkFrame(main_frame, height=80)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Icon
        icon_colors = {
            "success": ("#28a745", "✅"),
            "error": ("#dc3545", "❌"), 
            "warning": ("#ffc107", "⚠️"),
            "question": ("#007bff", "❓")
        }
        
        color, emoji = icon_colors.get(dialog_type, ("#6c757d", "ℹ️"))
        
        icon_label = ctk.CTkLabel(
            header_frame,
            text=emoji,
            font=ctk.CTkFont(size=32),
            width=50
        )
        icon_label.pack(side="left", padx=(20, 10), pady=15)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True, pady=15, padx=(0, 20))
        
        # Message frame
        message_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        message_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Main message
        message_label = ctk.CTkLabel(
            message_frame,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=400,
            justify="left",
            anchor="nw"
        )
        message_label.pack(fill="x", pady=(0, 10))
        
        # Details (nếu có)
        if details:
            details_frame = ctk.CTkFrame(message_frame)
            details_frame.pack(fill="both", expand=True, pady=(0, 10))
            
            details_label = ctk.CTkLabel(
                details_frame,
                text="Chi tiết:",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            details_label.pack(anchor="w", padx=15, pady=(10, 5))
            
            details_text = ctk.CTkTextbox(
                details_frame,
                height=60,
                font=ctk.CTkFont(family="Consolas", size=10)
            )
            details_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
            details_text.insert("0.0", details)
            details_text.configure(state="disabled")
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def on_ok():
            self.result = True
            dialog.destroy()
        
        def on_cancel():
            self.result = False
            dialog.destroy()
        
        if show_cancel:
            # Yes/No buttons
            cancel_btn = ctk.CTkButton(
                buttons_frame,
                text="Không",
                command=on_cancel,
                width=100,
                height=35,
                fg_color=("gray70", "gray25"),
                hover_color=("gray65", "gray30")
            )
            cancel_btn.pack(side="right", padx=(10, 0))
            
            ok_btn = ctk.CTkButton(
                buttons_frame,
                text="Có",
                command=on_ok,
                width=100,
                height=35,
                fg_color=color,
                hover_color=color
            )
            ok_btn.pack(side="right")
        else:
            # OK button only
            ok_btn = ctk.CTkButton(
                buttons_frame,
                text="OK",
                command=on_ok,
                width=120,
                height=40,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=color,
                hover_color=color
            )
            ok_btn.pack(side="right")
        
        # Focus và bind keys
        dialog.focus_set()
        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel() if show_cancel else on_ok())
        
        # Wait for result
        self.result = None
        dialog.wait_window()
        
        return self.result

class ToastNotification:
    """Toast notification hiện tại góc màn hình"""
    
    def __init__(self):
        self.notifications = []
        
    def show(self, message, duration=3000, type="info"):
        """Hiển thị toast notification"""
        
        # Tạo cửa sổ toast
        toast = ctk.CTkToplevel()
        toast.title("")
        toast.geometry("350x80")
        toast.resizable(False, False)
        toast.attributes('-topmost', True)
        toast.overrideredirect(True)  # Remove window decorations
        
        # Position ở góc phải dưới màn hình
        screen_width = toast.winfo_screenwidth()
        screen_height = toast.winfo_screenheight()
        
        # Tính toán vị trí y dựa trên số notification hiện tại
        y_offset = len(self.notifications) * 90
        x = screen_width - 370
        y = screen_height - 150 - y_offset
        
        toast.geometry(f"+{x}+{y}")
        
        # Colors theo type
        colors = {
            "success": ("#28a745", "✅"),
            "error": ("#dc3545", "❌"),
            "warning": ("#ffc107", "⚠️"),
            "info": ("#17a2b8", "ℹ️")
        }
        
        color, emoji = colors.get(type, colors["info"])
        
        # Main frame
        main_frame = ctk.CTkFrame(toast, corner_radius=10, fg_color=color)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Content frame
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Icon
        icon_label = ctk.CTkLabel(
            content_frame,
            text=emoji,
            font=ctk.CTkFont(size=20),
            width=30
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        # Message
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=12),
            wraplength=250,
            anchor="w",
            text_color="white"
        )
        message_label.pack(side="left", fill="x", expand=True)
        
        # Close button
        close_btn = ctk.CTkLabel(
            content_frame,
            text="×",
            font=ctk.CTkFont(size=18, weight="bold"),
            width=20,
            cursor="hand2",
            text_color="white"
        )
        close_btn.pack(side="right")
        
        def close_toast():
            try:
                if toast in self.notifications:
                    self.notifications.remove(toast)
                toast.destroy()
                self._reposition_notifications()
            except:
                pass
        
        close_btn.bind("<Button-1>", lambda e: close_toast())
        
        # Add to notifications list
        self.notifications.append(toast)
        
        # Auto close after duration
        toast.after(duration, close_toast)
        
        # Animation: slide in
        self._animate_slide_in(toast, x, y)
        
        return toast
    
    def _animate_slide_in(self, toast, target_x, target_y):
        """Animation slide in từ phải sang"""
        start_x = toast.winfo_screenwidth()
        current_x = start_x
        
        def animate():
            nonlocal current_x
            if current_x > target_x:
                current_x -= 20
                toast.geometry(f"+{current_x}+{target_y}")
                toast.after(10, animate)
            else:
                toast.geometry(f"+{target_x}+{target_y}")
        
        animate()
    
    def _reposition_notifications(self):
        """Sắp xếp lại vị trí các notifications"""
        for i, notification in enumerate(self.notifications):
            try:
                screen_width = notification.winfo_screenwidth()
                screen_height = notification.winfo_screenheight()
                x = screen_width - 370
                y = screen_height - 150 - (i * 90)
                notification.geometry(f"+{x}+{y}")
            except:
                pass

class ProgressDialog:
    """Dialog hiển thị progress với animation"""
    
    def __init__(self, parent=None, title="Đang xử lý..."):
        self.parent = parent
        self.dialog = None
        self.progress_bar = None
        self.status_label = None
        self.is_running = False
        self.title = title
        
    def show(self):
        """Hiển thị progress dialog"""
        if self.dialog:
            return
            
        self.dialog = ctk.CTkToplevel(self.parent) if self.parent else ctk.CTk()
        self.dialog.title(self.title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        
        # Center dialog
        if self.parent:
            self.dialog.transient(self.parent)
            self.dialog.geometry(f"+{self.parent.winfo_x() + 100}+{self.parent.winfo_y() + 100}")
        
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ctk.CTkFrame(self.dialog, corner_radius=0)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=self.title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(main_frame, width=300)
        self.progress_bar.pack(pady=10, padx=20)
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Đang chuẩn bị...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(5, 20))
        
        self.is_running = True
        
    def update_progress(self, value, status=""):
        """Cập nhật progress"""
        if self.progress_bar:
            self.progress_bar.set(value)
        if self.status_label and status:
            self.status_label.configure(text=status)
    
    def close(self):
        """Đóng dialog"""
        if self.dialog:
            self.is_running = False
            self.dialog.destroy()
            self.dialog = None

# Convenience functions
toast = ToastNotification()

def show_success(message, details=None, parent=None):
    """Hiển thị thông báo thành công"""
    msgbox = ModernMessageBox(parent)
    return msgbox.show_success("🎉 Thành công!", message, details)

def show_error(message, details=None, parent=None):
    """Hiển thị thông báo lỗi"""
    msgbox = ModernMessageBox(parent)
    return msgbox.show_error("❌ Lỗi!", message, details)

def show_warning(message, details=None, parent=None):
    """Hiển thị cảnh báo"""
    msgbox = ModernMessageBox(parent)
    return msgbox.show_warning("⚠️ Cảnh báo!", message, details)

def show_question(message, details=None, parent=None):
    """Hiển thị câu hỏi yes/no"""
    msgbox = ModernMessageBox(parent)
    return msgbox.show_question("❓ Xác nhận", message, details)

def show_toast_success(message, duration=3000):
    """Toast thành công"""
    return toast.show(message, duration, "success")

def show_toast_error(message, duration=4000):
    """Toast lỗi"""
    return toast.show(message, duration, "error")

def show_toast_warning(message, duration=3500):
    """Toast cảnh báo"""
    return toast.show(message, duration, "warning")

def show_toast_info(message, duration=3000):
    """Toast thông tin"""
    return toast.show(message, duration, "info") 