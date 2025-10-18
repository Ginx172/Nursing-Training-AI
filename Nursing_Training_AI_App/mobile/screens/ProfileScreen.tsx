import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import * as Animatable from 'react-native-animatable';

interface ProfileScreenProps {
  navigation: any;
}

export default function ProfileScreen({ navigation }: ProfileScreenProps) {
  const [settings, setSettings] = useState({
    notifications: true,
    audio: true,
    darkMode: false,
    dailyReminder: true,
    weeklyReport: true
  });

  const userProfile = {
    name: 'John Smith',
    email: 'john.smith@nhs.net',
    nmcNumber: '12A3456E',
    currentBand: 'Band 5',
    sector: 'NHS',
    specialty: 'AMU/MAU',
    joinDate: '2024-01-15',
    questionsCompleted: 247,
    averageScore: 82,
    streak: 7,
    badges: ['🔥 7 Day Streak', '💯 100 Questions', '🎯 80% Accuracy']
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Logout', 
          style: 'destructive',
          onPress: () => navigation.navigate('Login')
        }
      ]
    );
  };

  const menuItems = [
    { id: '1', title: 'Edit Profile', icon: '👤', screen: 'EditProfile' },
    { id: '2', title: 'Subscription', icon: '💳', screen: 'Subscription' },
    { id: '3', title: 'Progress Report', icon: '📊', screen: 'ProgressReport' },
    { id: '4', title: 'Certificates', icon: '🎓', screen: 'Certificates' },
    { id: '5', title: 'Help & Support', icon: '❓', screen: 'Help' },
    { id: '6', title: 'About', icon: 'ℹ️', screen: 'About' }
  ];

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>←</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Profile</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Profile Card */}
        <Animatable.View animation="fadeInUp" delay={200} style={styles.profileCard}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {userProfile.name.split(' ').map(n => n[0]).join('')}
            </Text>
          </View>
          <Text style={styles.profileName}>{userProfile.name}</Text>
          <Text style={styles.profileEmail}>{userProfile.email}</Text>
          
          <View style={styles.profileInfo}>
            <View style={styles.profileInfoItem}>
              <Text style={styles.profileInfoLabel}>NMC Number</Text>
              <Text style={styles.profileInfoValue}>{userProfile.nmcNumber}</Text>
            </View>
            <View style={styles.profileDivider} />
            <View style={styles.profileInfoItem}>
              <Text style={styles.profileInfoLabel}>Band</Text>
              <Text style={styles.profileInfoValue}>{userProfile.currentBand}</Text>
            </View>
            <View style={styles.profileDivider} />
            <View style={styles.profileInfoItem}>
              <Text style={styles.profileInfoLabel}>Sector</Text>
              <Text style={styles.profileInfoValue}>{userProfile.sector}</Text>
            </View>
          </View>

          <View style={styles.badgesContainer}>
            {userProfile.badges.map((badge, index) => (
              <View key={index} style={styles.badge}>
                <Text style={styles.badgeText}>{badge}</Text>
              </View>
            ))}
          </View>
        </Animatable.View>

        {/* Stats Card */}
        <Animatable.View animation="fadeInUp" delay={400} style={styles.statsCard}>
          <Text style={styles.cardTitle}>Your Statistics</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{userProfile.questionsCompleted}</Text>
              <Text style={styles.statLabel}>Questions</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{userProfile.averageScore}%</Text>
              <Text style={styles.statLabel}>Average</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statValue}>🔥 {userProfile.streak}</Text>
              <Text style={styles.statLabel}>Streak</Text>
            </View>
          </View>
        </Animatable.View>

        {/* Settings */}
        <Animatable.View animation="fadeInUp" delay={600} style={styles.settingsCard}>
          <Text style={styles.cardTitle}>Settings</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingTitle}>Push Notifications</Text>
              <Text style={styles.settingDescription}>Receive training reminders</Text>
            </View>
            <Switch
              value={settings.notifications}
              onValueChange={(value) => setSettings({...settings, notifications: value})}
              trackColor={{ false: '#e0e0e0', true: '#0066CC' }}
              thumbColor={settings.notifications ? '#fff' : '#f4f3f4'}
            />
          </View>

          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingTitle}>Audio Mode</Text>
              <Text style={styles.settingDescription}>Enable text-to-speech for questions</Text>
            </View>
            <Switch
              value={settings.audio}
              onValueChange={(value) => setSettings({...settings, audio: value})}
              trackColor={{ false: '#e0e0e0', true: '#0066CC' }}
              thumbColor={settings.audio ? '#fff' : '#f4f3f4'}
            />
          </View>

          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingTitle}>Dark Mode</Text>
              <Text style={styles.settingDescription}>Use dark theme</Text>
            </View>
            <Switch
              value={settings.darkMode}
              onValueChange={(value) => setSettings({...settings, darkMode: value})}
              trackColor={{ false: '#e0e0e0', true: '#0066CC' }}
              thumbColor={settings.darkMode ? '#fff' : '#f4f3f4'}
            />
          </View>

          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingTitle}>Daily Reminder</Text>
              <Text style={styles.settingDescription}>Remind me to practice daily</Text>
            </View>
            <Switch
              value={settings.dailyReminder}
              onValueChange={(value) => setSettings({...settings, dailyReminder: value})}
              trackColor={{ false: '#e0e0e0', true: '#0066CC' }}
              thumbColor={settings.dailyReminder ? '#fff' : '#f4f3f4'}
            />
          </View>

          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingTitle}>Weekly Report</Text>
              <Text style={styles.settingDescription}>Email weekly progress summary</Text>
            </View>
            <Switch
              value={settings.weeklyReport}
              onValueChange={(value) => setSettings({...settings, weeklyReport: value})}
              trackColor={{ false: '#e0e0e0', true: '#0066CC' }}
              thumbColor={settings.weeklyReport ? '#fff' : '#f4f3f4'}
            />
          </View>
        </Animatable.View>

        {/* Menu Items */}
        <Animatable.View animation="fadeInUp" delay={800} style={styles.menuCard}>
          {menuItems.map((item, index) => (
            <TouchableOpacity
              key={item.id}
              style={styles.menuItem}
              onPress={() => navigation.navigate(item.screen)}
            >
              <View style={styles.menuItemLeft}>
                <Text style={styles.menuIcon}>{item.icon}</Text>
                <Text style={styles.menuTitle}>{item.title}</Text>
              </View>
              <Text style={styles.menuArrow}>→</Text>
            </TouchableOpacity>
          ))}
        </Animatable.View>

        {/* Logout Button */}
        <TouchableOpacity 
          style={styles.logoutButton}
          onPress={handleLogout}
        >
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>

        <View style={styles.bottomPadding} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#0066CC',
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  backButtonText: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
  },
  placeholder: {
    width: 40,
  },
  content: {
    flex: 1,
  },
  profileCard: {
    margin: 16,
    marginTop: 24,
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#0066CC',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  avatarText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
  },
  profileName: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  profileEmail: {
    fontSize: 14,
    color: '#666',
    marginBottom: 20,
  },
  profileInfo: {
    flexDirection: 'row',
    width: '100%',
    marginBottom: 20,
  },
  profileInfoItem: {
    flex: 1,
    alignItems: 'center',
  },
  profileInfoLabel: {
    fontSize: 11,
    color: '#999',
    marginBottom: 4,
  },
  profileInfoValue: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1a1a1a',
  },
  profileDivider: {
    width: 1,
    backgroundColor: '#e0e0e0',
  },
  badgesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 8,
  },
  badge: {
    backgroundColor: '#f9f9f9',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  badgeText: {
    fontSize: 11,
    color: '#666',
  },
  statsCard: {
    margin: 16,
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#0066CC',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#e0e0e0',
  },
  settingsCard: {
    margin: 16,
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f5f5f5',
  },
  settingInfo: {
    flex: 1,
    marginRight: 12,
  },
  settingTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 12,
    color: '#999',
  },
  menuCard: {
    margin: 16,
    backgroundColor: 'white',
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  menuItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f5f5f5',
  },
  menuItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  menuIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  menuTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1a1a1a',
  },
  menuArrow: {
    fontSize: 16,
    color: '#ccc',
  },
  logoutButton: {
    margin: 16,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#E74C3C',
  },
  logoutText: {
    color: '#E74C3C',
    fontSize: 16,
    fontWeight: 'bold',
  },
  bottomPadding: {
    height: 40,
  },
});

