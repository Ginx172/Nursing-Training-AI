import React from 'react';
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

interface ResultsScreenProps {
  navigation: any;
  route: any;
}

export default function ResultsScreen({ navigation, route }: ResultsScreenProps) {
  const { score, sector, specialty, band } = route.params || {};
  
  const percentage = score?.total > 0 ? Math.round((score.correct / score.total) * 100) : 0;
  
  const getPerformanceLevel = (percentage: number) => {
    if (percentage >= 90) return { level: 'Excellent', icon: '🌟', color: '#00A651' };
    if (percentage >= 80) return { level: 'Very Good', icon: '⭐', color: '#0066CC' };
    if (percentage >= 70) return { level: 'Good', icon: '👍', color: '#FFA500' };
    if (percentage >= 60) return { level: 'Pass', icon: '✓', color: '#F39C12' };
    return { level: 'Needs Improvement', icon: '📚', color: '#E74C3C' };
  };

  const performance = getPerformanceLevel(percentage);

  const strengths = [
    'Clinical Assessment',
    'Patient Safety',
    'Emergency Response'
  ];

  const areasToImprove = [
    'Leadership Skills',
    'Governance Knowledge'
  ];

  const recommendations = [
    {
      id: '1',
      title: 'Practice Leadership Questions',
      description: 'Focus on Band 6 leadership scenarios',
      icon: '👥',
      color: '#9B59B6',
      estimatedTime: '30 mins'
    },
    {
      id: '2',
      title: 'Review NICE Guidelines',
      description: 'Read latest sepsis management guidelines',
      icon: '📚',
      color: '#3498DB',
      estimatedTime: '45 mins'
    },
    {
      id: '3',
      title: 'Drug Calculations Practice',
      description: 'Strengthen calculation accuracy',
      icon: '🔢',
      color: '#00A651',
      estimatedTime: '20 mins'
    }
  ];

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header */}
      <View style={[styles.header, { backgroundColor: performance.color }]}>
        <Animatable.View animation="bounceIn" delay={200}>
          <Text style={styles.performanceIcon}>{performance.icon}</Text>
        </Animatable.View>
        <Animatable.Text animation="fadeIn" delay={400} style={styles.performanceLevel}>
          {performance.level}
        </Animatable.Text>
        <Animatable.Text animation="fadeIn" delay={600} style={styles.percentageText}>
          {percentage}%
        </Animatable.Text>
        <Text style={styles.scoreText}>
          {score?.correct} out of {score?.total} correct
        </Text>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Performance Breakdown */}
        <Animatable.View animation="fadeInUp" delay={800} style={styles.breakdownCard}>
          <Text style={styles.cardTitle}>Performance Breakdown</Text>
          
          <View style={styles.statRow}>
            <Text style={styles.statLabel}>Correct Answers</Text>
            <Text style={styles.statValue}>{score?.correct}</Text>
          </View>
          
          <View style={styles.statRow}>
            <Text style={styles.statLabel}>Incorrect Answers</Text>
            <Text style={styles.statValue}>{score?.total - score?.correct}</Text>
          </View>
          
          <View style={styles.statRow}>
            <Text style={styles.statLabel}>Accuracy</Text>
            <Text style={[styles.statValue, { color: performance.color }]}>
              {percentage}%
            </Text>
          </View>

          <View style={styles.divider} />

          <View style={styles.statRow}>
            <Text style={styles.statLabel}>Specialty</Text>
            <Text style={styles.statValue}>{specialty}</Text>
          </View>
          
          <View style={styles.statRow}>
            <Text style={styles.statLabel}>Band Level</Text>
            <Text style={styles.statValue}>{band?.replace('_', ' ').toUpperCase()}</Text>
          </View>
        </Animatable.View>

        {/* Strengths */}
        <Animatable.View animation="fadeInUp" delay={1000} style={styles.strengthsCard}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Your Strengths</Text>
            <Text style={styles.strengthIcon}>💪</Text>
          </View>
          {strengths.map((strength, index) => (
            <View key={index} style={styles.strengthItem}>
              <Text style={styles.checkIcon}>✓</Text>
              <Text style={styles.strengthText}>{strength}</Text>
            </View>
          ))}
        </Animatable.View>

        {/* Areas to Improve */}
        <Animatable.View animation="fadeInUp" delay={1200} style={styles.improvementCard}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Areas to Improve</Text>
            <Text style={styles.targetIcon}>🎯</Text>
          </View>
          {areasToImprove.map((area, index) => (
            <View key={index} style={styles.improvementItem}>
              <Text style={styles.bulletIcon}>•</Text>
              <Text style={styles.improvementText}>{area}</Text>
            </View>
          ))}
        </Animatable.View>

        {/* Recommendations */}
        <Animatable.View animation="fadeInUp" delay={1400}>
          <Text style={styles.sectionTitle}>Recommended Next Steps</Text>
          {recommendations.map((rec, index) => (
            <Animatable.View
              key={rec.id}
              animation="fadeInRight"
              delay={1600 + (index * 200)}
            >
              <TouchableOpacity 
                style={styles.recommendationCard}
                activeOpacity={0.7}
              >
                <View style={[styles.recIcon, { backgroundColor: rec.color }]}>
                  <Text style={styles.recIconText}>{rec.icon}</Text>
                </View>
                <View style={styles.recContent}>
                  <Text style={styles.recTitle}>{rec.title}</Text>
                  <Text style={styles.recDescription}>{rec.description}</Text>
                  <Text style={styles.recTime}>⏱️ {rec.estimatedTime}</Text>
                </View>
                <Text style={styles.recArrow}>→</Text>
              </TouchableOpacity>
            </Animatable.View>
          ))}
        </Animatable.View>

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          <TouchableOpacity 
            style={styles.reviewButton}
            onPress={() => navigation.navigate('Review')}
          >
            <Text style={styles.reviewButtonText}>Review Answers</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.retryButton}
            onPress={() => navigation.navigate('Questions', { sector, specialty, band })}
          >
            <Text style={styles.retryButtonText}>Try Again</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.dashboardButton}
            onPress={() => navigation.navigate('Dashboard')}
          >
            <Text style={styles.dashboardButtonText}>Back to Dashboard</Text>
          </TouchableOpacity>
        </View>

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
    paddingTop: 60,
    paddingBottom: 40,
    alignItems: 'center',
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
  },
  performanceIcon: {
    fontSize: 80,
    marginBottom: 16,
  },
  performanceLevel: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  percentageText: {
    fontSize: 48,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  scoreText: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.9)',
  },
  content: {
    flex: 1,
  },
  breakdownCard: {
    margin: 16,
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
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 16,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
  },
  statValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1a1a1a',
  },
  divider: {
    height: 1,
    backgroundColor: '#e0e0e0',
    marginVertical: 12,
  },
  strengthsCard: {
    margin: 16,
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#00A651',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  improvementCard: {
    margin: 16,
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#FFA500',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  strengthIcon: {
    fontSize: 24,
  },
  targetIcon: {
    fontSize: 24,
  },
  strengthItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  checkIcon: {
    fontSize: 16,
    color: '#00A651',
    marginRight: 8,
    fontWeight: 'bold',
  },
  strengthText: {
    fontSize: 14,
    color: '#333',
  },
  improvementItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  bulletIcon: {
    fontSize: 16,
    color: '#FFA500',
    marginRight: 8,
    fontWeight: 'bold',
  },
  improvementText: {
    fontSize: 14,
    color: '#333',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginHorizontal: 16,
    marginBottom: 12,
  },
  recommendationCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    marginHorizontal: 16,
    marginBottom: 12,
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  recIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  recIconText: {
    fontSize: 24,
  },
  recContent: {
    flex: 1,
  },
  recTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  recDescription: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  recTime: {
    fontSize: 11,
    color: '#999',
  },
  recArrow: {
    fontSize: 20,
    color: '#0066CC',
    fontWeight: 'bold',
  },
  actionButtons: {
    paddingHorizontal: 16,
    marginTop: 24,
    gap: 12,
  },
  reviewButton: {
    backgroundColor: '#0066CC',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  reviewButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  retryButton: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#0066CC',
  },
  retryButtonText: {
    color: '#0066CC',
    fontSize: 16,
    fontWeight: 'bold',
  },
  dashboardButton: {
    backgroundColor: '#f9f9f9',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  dashboardButtonText: {
    color: '#666',
    fontSize: 16,
    fontWeight: '600',
  },
  bottomPadding: {
    height: 40,
  },
});

