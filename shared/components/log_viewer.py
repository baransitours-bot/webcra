"""
Log Viewer Component
Reusable live log display
"""

import streamlit as st

class LogViewer:
    """Manages live log display with auto-scrolling"""

    def __init__(self, max_lines: int = 50, expanded: bool = True):
        self.logs = []
        self.max_lines = max_lines
        self.container = st.expander("📋 Live Logs", expanded=expanded)
        self.log_area = self.container.empty()

    def add(self, message: str):
        """Add a log message"""
        self.logs.append(message)
        self._update_display()

    def add_info(self, message: str):
        """Add info log"""
        self.add(f"[INFO] {message}")

    def add_success(self, message: str):
        """Add success log"""
        self.add(f"[SUCCESS] ✅ {message}")

    def add_warning(self, message: str):
        """Add warning log"""
        self.add(f"[WARNING] ⚠️ {message}")

    def add_error(self, message: str):
        """Add error log"""
        self.add(f"[ERROR] ❌ {message}")

    def clear(self):
        """Clear all logs"""
        self.logs = []
        self._update_display()

    def _update_display(self):
        """Update the display with latest logs"""
        # Show only last N lines
        visible_logs = self.logs[-self.max_lines:]
        self.log_area.code('\n'.join(visible_logs))

    def get_logs(self):
        """Get all logs as list"""
        return self.logs.copy()
