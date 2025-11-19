"""
Progress Display Component
Reusable progress bar and status display
"""

import streamlit as st

class ProgressDisplay:
    """Manages progress bar and status text"""

    def __init__(self):
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        self.current_progress = 0

    def update(self, current: int, total: int, message: str = ""):
        """Update progress bar and status"""
        if total > 0:
            self.current_progress = current / total
            self.progress_bar.progress(self.current_progress)

        status_msg = f"{message} ({current}/{total})" if message else f"{current}/{total}"
        self.status_text.text(status_msg)

    def complete(self, message: str = "✅ Completed!"):
        """Mark as complete"""
        self.progress_bar.progress(1.0)
        self.status_text.text(message)

    def error(self, message: str):
        """Show error"""
        self.status_text.error(message)
