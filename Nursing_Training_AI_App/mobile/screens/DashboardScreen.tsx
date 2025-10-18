import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import * as Animatable from 'react-native-animatable';

const { width } = Dimensions.get('window');

interface DashboardScreenProps {
  navigation: any;
}

export default function DashboardScreen({ navigation }: DashboardScreenProps) {
  const [userStats, setUserStats] = useState({
    userName: 'John Smith',
    currentBand: 'Band 5',
    sector: 'NHS',
    specialty: 'AMU/MAU',
    questionsCompleted: 247,
    accuracy: 82,
    streak: 7,
    nextBand: 'Band 6',
    progressToNextBand: 65,
    recentActivity: [
      { date: '2025-10-17', questions: 15, score: 87 },
      { date: '2025-10-16', questions: 12, score: 78 },
      { date: '2025-10-15', questions: 18, score: 92 }
    ]
  });

  const quickActions = [
    { id: '1', title: 'Continue Training', icon: '📚', color: '#0066CC', screen: 'Questions' },
    { id: '2', title: 'My Progress', icon: '📊', color: '#00A651', screen: 'Progress' },
    { id: '3', title: 'Specialties', icon: '🏥', color: '#FF6B6B', screen: 'Specialties' },
    { id: '4', title: 'Profile', icon: '👤', color: '#9B59B6', screen: 'Profile' }
  ];

  const achievements = [
    { id: '1', title: '7 Day Streak', icon: '🔥', earned: true },
    { id: '2', title: '100 Questions', icon: '💯', earned: true },
    { id: '3', title: '80% Accuracy', icon: '🎯', earned: true },
    { id: '4', title: 'Fast Learner', icon: '⚡', earned: false }
  ];

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <View>
            <Text style={styles.greeting}>Good morning,</Text>
            <Text style={styles.userName}>{userStats.userName}</Text>
            <Text style={styles.userInfo}>
              {userStats.currentBand} • {userStats.sector} • {userStats.specialty}
            </Text>
          </View>
          <TouchableOpacity style={styles.notificationButton}>
            <Text style={styles.notificationIcon}>🔔</Text>
            <View style={styles.notificationBadge}>
              <Text style={styles.notificationBadgeText}>3</Text>
            </View>
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Stats Cards */}
        <Animatable.View animation="fadeInUp" delay={200} style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{userStats.questionsCompleted}</Text>
            <Text style={styles.statLabel}>Questions</Text>
            <Text style={styles.statLabel}>Completed</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{userStats.accuracy}%</Text>
            <Text style={styles.statLabel}>Overall</Text>
            <Text style={styles.statLabel}>Accuracy</Text>
          </View>
          <View style={[styles.statCard, styles.streakCard]}>
            <Text style={styles.statValue}>🔥 {userStats.streak}</Text>
            <Text style={styles.statLabel}>Day</Text>
            <Text style={styles.statLabel}>Streak</Text>
          </View>
        </Animatable.View>

        {/* Progress to Next Band */}
        <Animatable.View animation="fadeInUp" delay={400} style={styles.progressCard}>
          <View style={styles.progressHeader}>
            <Text style={styles.progressTitle}>Progress to {userStats.nextBand}</Text>
            <Text style={styles.progressPercentage}>{userStats.progressToNextBand}%</Text>
          </View>
          <View style={styles.progressBarContainer}>
            <View 
              style={[
                styles.progressBar, 
                { width: `${userStats.progressToNextBand}%` }
              ]} 
            />
          </View>
          <Text style={styles.progressSubtext}>
            Keep going! You're making excellent progress towards Band 6
          </Text>
        </Animatable.View>

        {/* Quick Actions */}
        <Animatable.View animation="fadeInUp" delay={600}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.quickActionsGrid}>
            {quickActions.map((action) => (
              <TouchableOpacity 
                key={action.id}
                style={[styles.quickActionCard, { backgroundColor: action.color }]}
                onPress={() => navigation.navigate(action.screen)}
                activeOpacity={0.8}
              >
                <Text style={styles.quickActionIcon}>{action.icon}</Text>
                <Text style={styles.quickActionTitle}>{action.title}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </Animatable.View>

        {/* Recent Activity */}
        <Animatable.View animation="fadeInUp" delay={800}>
          <Text style={styles.sectionTitle}>Recent Activity</Text>
          {userStats.recentActivity.map((activity, index) => (
            <View key={index} style={styles.activityCard}>
              <View style={styles.activityDate}>
                <Text style={styles.activityDateText}>
                  {new Date(activity.date).toLocaleDateString('en-GB', { 
                    day: 'numeric', 
                    month: 'short' 
                  })}
                </Text>
              </View>
              <View style={styles.activityDetails}>
                <Text style={styles.activityQuestions}>{activity.questions} questions</Text>
                <Text style={styles.activityScore}>Score: {activity.score}%</Text>
              </View>
              <View style={[
                styles.activityBadge,
                { backgroundColor: activity.score >= 80 ? '#00A651' : '#FFA500' }
              ]}>
                <Text style={styles.activityBadgeText}>
                  {activity.score >= 80 ? '✓' : '!'}
                </Text>
              </View>
            </View>
          ))}
        </Animatable.View>

        {/* Achievements */}
        <Animatable.View animation="fadeInUp" delay={1000}>
          <Text style={styles.sectionTitle}>Achievements</Text>
          <View style={styles.achievementsGrid}>
            {achievements.map((achievement) => (
              <View 
                key={achievement.id}
                style={[
                  styles.achievementCard,
                  !achievement.earned && styles.achievementCardLocked
                ]}
              >
                <Text style={styles.achievementIcon}>{achievement.icon}</Text>
                <Text style={[
                  styles.achievementTitle,
                  !achievement.earned && styles.achievementTitleLocked
                ]}>
                  {achievement.title}
                </Text>
              </View>
            ))}
          </View>
        </Animatable.View>

        {/* Recommended Training */}
        <Animatable.View animation="fadeInUp" delay={1200} style={styles.recommendedCard}>
          <Text style={styles.recommendedTitle}>Recommended for You</Text>
          <Text style={styles.recommendedSubtext}>Based on your recent performance</Text>
          <TouchableOpacity 
            style={styles.recommendedButton}
            onPress={() => navigation.navigate('Questions', { 
              specialty: 'amu', 
              band: 'band_5',
              type: 'leadership'
            })}
          >
            <View style={styles.recommendedContent}>
              <Text style={styles.recommendedIcon}>👥</Text>
              <View style={styles.recommendedText}>
                <Text style={styles.recommendedTopicTitle}>Leadership Skills</Text>
                <Text style={styles.recommendedTopicSubtext}>
                  Strengthen your leadership competencies for Band 6
                </Text>
              </View>
            </View>
            <Text style={styles.recommendedArrow}>→</Text>
          </TouchableOpacity>
        </Animatable.View>

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
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
    elevation: 8,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingHorizontal: 20,
  },
  greeting: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginTop: 4,
  },
  userInfo: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.7)',
    marginTop: 4,
  },
  notificationButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  notificationIcon: {
    fontSize: 20,
  },
  notificationBadge: {
    position: 'absolute',
    top: -5,
    right: -5,
    backgroundColor: '#FF4444',
    borderRadius: 10,
    width: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  notificationBadgeText: {
    color: 'white',
    fontSize: 10,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingTop: 20,
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  streakCard: {
    backgroundColor: '#FFF3E0',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 11,
    color: '#666',
    textAlign: 'center',
  },
  progressCard: {
    marginHorizontal: 16,
    marginTop: 20,
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  progressTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
  },
  progressPercentage: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#0066CC',
  },
  progressBarContainer: {
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#0066CC',
    borderRadius: 4,
  },
  progressSubtext: {
    fontSize: 12,
    color: '#666',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginHorizontal: 16,
    marginTop: 24,
    marginBottom: 12,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    gap: 12,
  },
  quickActionCard: {
    width: (width - 44) / 2,
    height: 100,
    borderRadius: 16,
    padding: 16,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  quickActionIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  quickActionTitle: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
  activityCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    marginHorizontal: 16,
    marginBottom: 12,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  activityDate: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  activityDateText: {
    fontSize: 11,
    color: '#666',
    textAlign: 'center',
  },
  activityDetails: {
    flex: 1,
  },
  activityQuestions: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1a1a1a',
  },
  activityScore: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  activityBadge: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  activityBadgeText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  achievementsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    gap: 12,
  },
  achievementCard: {
    width: (width - 44) / 2,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#0066CC',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  achievementCardLocked: {
    borderColor: '#e0e0e0',
    opacity: 0.5,
  },
  achievementIcon: {
    fontSize: 36,
    marginBottom: 8,
  },
  achievementTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1a1a1a',
    textAlign: 'center',
  },
  achievementTitleLocked: {
    color: '#999',
  },
  recommendedCard: {
    marginHorizontal: 16,
    marginTop: 24,
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  recommendedTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  recommendedSubtext: {
    fontSize: 12,
    color: '#666',
    marginBottom: 16,
  },
  recommendedButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#f9f9f9',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  recommendedContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  recommendedIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  recommendedText: {
    flex: 1,
  },
  recommendedTopicTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  recommendedTopicSubtext: {
    fontSize: 12,
    color: '#666',
  },
  recommendedArrow: {
    fontSize: 20,
    color: '#0066CC',
    fontWeight: 'bold',
  },
  bottomPadding: {
    height: 40,
  },
});

