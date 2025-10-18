import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * Notification Service for Nursing Training AI
 * Handles push notifications and daily reminders
 */

// Configure notification behavior
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export class NotificationService {
  private static instance: NotificationService;
  private expoPushToken: string | null = null;

  private constructor() {}

  public static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  /**
   * Initialize notifications and get push token
   */
  public async initialize(): Promise<string | null> {
    try {
      if (!Device.isDevice) {
        console.log('Must use physical device for push notifications');
        return null;
      }

      // Request permissions
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        console.log('Failed to get push token for push notification!');
        return null;
      }

      // Get the push token
      const token = await Notifications.getExpoPushTokenAsync({
        projectId: 'your-expo-project-id' // TODO: Replace with actual project ID
      });

      this.expoPushToken = token.data;

      // Configure for Android
      if (Platform.OS === 'android') {
        Notifications.setNotificationChannelAsync('default', {
          name: 'default',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#0066CC',
        });
      }

      // Save token to backend
      await this.registerPushToken(token.data);

      console.log('Push token:', token.data);
      return token.data;

    } catch (error) {
      console.error('Error initializing notifications:', error);
      return null;
    }
  }

  /**
   * Register push token with backend
   */
  private async registerPushToken(token: string): Promise<void> {
    try {
      // TODO: Send token to backend
      await AsyncStorage.setItem('push_token', token);
      console.log('Push token registered');
    } catch (error) {
      console.error('Error registering push token:', error);
    }
  }

  /**
   * Schedule daily training reminder
   */
  public async scheduleDailyReminder(hour: number = 18, minute: number = 0): Promise<void> {
    try {
      // Cancel existing reminders
      await this.cancelDailyReminder();

      // Schedule new reminder
      await Notifications.scheduleNotificationAsync({
        content: {
          title: '📚 Time for Training!',
          body: 'Complete today\'s questions to maintain your streak 🔥',
          data: { type: 'daily_reminder' },
          sound: true,
        },
        trigger: {
          hour,
          minute,
          repeats: true,
        },
      });

      console.log('Daily reminder scheduled');
    } catch (error) {
      console.error('Error scheduling daily reminder:', error);
      throw error;
    }
  }

  /**
   * Cancel daily reminder
   */
  public async cancelDailyReminder(): Promise<void> {
    try {
      const notifications = await Notifications.getAllScheduledNotificationsAsync();
      const dailyReminders = notifications.filter(n => 
        n.content.data?.type === 'daily_reminder'
      );

      for (const reminder of dailyReminders) {
        await Notifications.cancelScheduledNotificationAsync(reminder.identifier);
      }

      console.log('Daily reminders cancelled');
    } catch (error) {
      console.error('Error cancelling daily reminder:', error);
    }
  }

  /**
   * Send local notification immediately
   */
  public async sendLocalNotification(
    title: string,
    body: string,
    data?: any
  ): Promise<void> {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data,
          sound: true,
        },
        trigger: null, // Send immediately
      });
    } catch (error) {
      console.error('Error sending local notification:', error);
    }
  }

  /**
   * Schedule streak reminder
   */
  public async scheduleStreakReminder(daysStreak: number): Promise<void> {
    try {
      await this.sendLocalNotification(
        `🔥 ${daysStreak} Day Streak!`,
        `Amazing! You've practiced ${daysStreak} days in a row. Keep it up!`,
        { type: 'streak_achievement', days: daysStreak }
      );
    } catch (error) {
      console.error('Error scheduling streak reminder:', error);
    }
  }

  /**
   * Schedule achievement notification
   */
  public async notifyAchievement(
    achievementTitle: string,
    achievementDescription: string
  ): Promise<void> {
    try {
      await this.sendLocalNotification(
        `🏆 Achievement Unlocked!`,
        `${achievementTitle}: ${achievementDescription}`,
        { type: 'achievement', title: achievementTitle }
      );
    } catch (error) {
      console.error('Error notifying achievement:', error);
    }
  }

  /**
   * Schedule progress report notification
   */
  public async scheduleWeeklyReport(): Promise<void> {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title: '📊 Your Weekly Progress Report',
          body: 'Check your training stats and see how you\'ve improved!',
          data: { type: 'weekly_report' },
          sound: true,
        },
        trigger: {
          weekday: 1, // Monday
          hour: 9,
          minute: 0,
          repeats: true,
        },
      });

      console.log('Weekly report scheduled');
    } catch (error) {
      console.error('Error scheduling weekly report:', error);
    }
  }

  /**
   * Cancel all scheduled notifications
   */
  public async cancelAllNotifications(): Promise<void> {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
      console.log('All notifications cancelled');
    } catch (error) {
      console.error('Error cancelling notifications:', error);
    }
  }

  /**
   * Get all scheduled notifications
   */
  public async getScheduledNotifications(): Promise<Notifications.NotificationRequest[]> {
    try {
      return await Notifications.getAllScheduledNotificationsAsync();
    } catch (error) {
      console.error('Error getting scheduled notifications:', error);
      return [];
    }
  }

  /**
   * Setup notification listeners
   */
  public setupNotificationListeners(
    onNotificationReceived?: (notification: Notifications.Notification) => void,
    onNotificationResponse?: (response: Notifications.NotificationResponse) => void
  ): void {
    // Listener for when notification is received while app is foregrounded
    Notifications.addNotificationReceivedListener(notification => {
      console.log('Notification received:', notification);
      if (onNotificationReceived) {
        onNotificationReceived(notification);
      }
    });

    // Listener for when user taps on notification
    Notifications.addNotificationResponseReceivedListener(response => {
      console.log('Notification response:', response);
      if (onNotificationResponse) {
        onNotificationResponse(response);
      }
    });
  }

  /**
   * Badge management
   */
  public async setBadgeCount(count: number): Promise<void> {
    try {
      await Notifications.setBadgeCountAsync(count);
    } catch (error) {
      console.error('Error setting badge count:', error);
    }
  }

  public async clearBadge(): Promise<void> {
    try {
      await Notifications.setBadgeCountAsync(0);
    } catch (error) {
      console.error('Error clearing badge:', error);
    }
  }
}

// Export singleton instance
export default NotificationService.getInstance();

