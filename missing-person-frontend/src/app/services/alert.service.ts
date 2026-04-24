import { Injectable } from '@angular/core';

export interface AlertNotification {
  id: number;
  type: 'match' | 'warning' | 'error' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  data?: any;
}

@Injectable({
  providedIn: 'root'
})
export class AlertService {
  private alerts: AlertNotification[] = [];
  private alertId = 0;

  // Add new alert
  addAlert(type: AlertNotification['type'], title: string, message: string, data?: any): AlertNotification {
    const alert: AlertNotification = {
      id: ++this.alertId,
      type,
      title,
      message,
      timestamp: new Date(),
      data
    };
    
    this.alerts.unshift(alert);
    
    // Keep only last 20 alerts
    if (this.alerts.length > 20) {
      this.alerts.pop();
    }

    // Show browser notification if permitted
    this.showBrowserNotification(title, message);

    return alert;
  }

  // Show match alert
  showMatchAlert(name: string, confidence: number, personId: number, photo: string): AlertNotification {
    return this.addAlert(
      'match',
      '🎯 MATCH FOUND!',
      `Found ${name} with ${confidence}% confidence`,
      { name, confidence, personId, photo }
    );
  }

  // Show warning alert
  showWarning(title: string, message: string): AlertNotification {
    return this.addAlert('warning', title, message);
  }

  // Show error alert
  showError(title: string, message: string): AlertNotification {
    return this.addAlert('error', title, message);
  }

  // Show info alert
  showInfo(title: string, message: string): AlertNotification {
    return this.addAlert('info', title, message);
  }

  // Remove alert
  removeAlert(id: number): void {
    this.alerts = this.alerts.filter(a => a.id !== id);
  }

  // Clear all alerts
  clearAlerts(): void {
    this.alerts = [];
  }

  // Get all alerts
  getAlerts(): AlertNotification[] {
    return this.alerts;
  }

  // Get unread count (alerts from last 5 minutes)
  getUnreadCount(): number {
    const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
    return this.alerts.filter(a => a.timestamp > fiveMinutesAgo).length;
  }

  // Browser notification
  private showBrowserNotification(title: string, message: string): void {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body: message,
        icon: 'assets/police_logo.png'
      });
    }
  }

  // Request notification permission
  requestNotificationPermission(): void {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }
}
