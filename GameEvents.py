# GameEvents.py - Event Handling and Input Detection
# Handles pygame events, keyboard/mouse input, and alert system

import pygame
import sys
from typing import List, Tuple, Optional


class AlertManager:
    """Manages alert messages and their display timers"""
    def __init__(self):
        self.alerts: List[Tuple[str, int]] = []  # List of (message, timer) tuples
    
    def add_alert(self, message: str, duration: int = 120):
        """Add a new alert message with duration in frames"""
        self.alerts.append((message, duration))
    
    def update(self):
        """Update alert timers and remove expired alerts"""
        self.alerts = [(msg, timer - 1) for msg, timer in self.alerts if timer > 1]
    
    def get_active_alerts(self) -> List[str]:
        """Get list of currently active alert messages"""
        return [msg for msg, timer in self.alerts]
    
    def clear(self):
        """Clear all alerts"""
        self.alerts = []
