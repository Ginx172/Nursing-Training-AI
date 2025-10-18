import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Alert
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import * as Animatable from 'react-native-animatable';

const { width } = Dimensions.get('window');

interface SubscriptionScreenProps {
  navigation: any;
}

export default function SubscriptionScreen({ navigation }: SubscriptionScreenProps) {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');
  const [selectedPlan, setSelectedPlan] = useState<string>('professional');

  const plans = [
    {
      id: 'demo',
      name: 'Demo',
      price: { monthly: 0, annual: 0 },
      description: 'Try before you buy',
      features: [
        '10 question banks',
        '20 questions/day',
        'AMU specialty only',
        'NHS sector only',
        'Bands 2-5 only',
        'Basic analytics',
        '14-day trial'
      ],
      limitations: [
        'Limited access',
        'No audio features',
        'No offline mode'
      ],
      color: '#95A5A6',
      buttonText: 'Start Free Trial'
    },
    {
      id: 'basic',
      name: 'Basic',
      price: { monthly: 9.99, annual: 99.00 },
      description: 'For individual professionals',
      features: [
        '500 question banks',
        '100 questions/day',
        '5 NHS specialties',
        'NHS + Care Homes',
        'Bands 2-6',
        '✅ Audio features',
        '✅ Offline mode (5 banks)',
        'AI feedback',
        'Personalized recommendations'
      ],
      color: '#3498DB',
      buttonText: 'Choose Basic'
    },
    {
      id: 'professional',
      name: 'Professional',
      price: { monthly: 19.99, annual: 199.00 },
      description: 'Most Popular - Advance your career',
      features: [
        '✅ UNLIMITED question banks',
        '✅ UNLIMITED questions/day',
        '✅ ALL 9 specialties',
        '✅ ALL 5 sectors',
        '✅ ALL bands (2-8d)',
        '✅ Audio features',
        '✅ Offline mode (20 banks)',
        '✅ Advanced analytics',
        '✅ CPD certificates',
        '✅ Study groups',
        '✅ Priority support'
      ],
      popular: true,
      color: '#0066CC',
      buttonText: 'Choose Professional'
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: { monthly: 199.00, annual: 1999.00 },
      description: 'For organizations & training departments',
      features: [
        '🏢 Everything in Professional',
        '✅ 50 user licenses',
        '✅ Unlimited offline banks',
        '✅ Team analytics',
        '✅ Custom question banks',
        '✅ API access',
        '✅ White-label option',
        '✅ Dedicated manager',
        '✅ Phone support',
        '✅ SSO integration',
        '+ £5/user/month for additional users'
      ],
      color: '#9B59B6',
      buttonText: 'Contact Sales'
    }
  ];

  const handleSelectPlan = async (planId: string) => {
    if (planId === 'enterprise') {
      Alert.alert(
        'Enterprise Plan',
        'Contact our sales team for Enterprise pricing and features.',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Contact Sales', onPress: () => {/* Open contact form */} }
        ]
      );
      return;
    }

    if (planId === 'demo') {
      // Start free trial
      Alert.alert(
        '14-Day Free Trial',
        'Start your free trial now? No credit card required.',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Start Trial', onPress: () => {/* Activate trial */} }
        ]
      );
      return;
    }

    // Navigate to checkout
    navigation.navigate('Checkout', {
      planId,
      billingCycle
    });
  };

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
        <Text style={styles.headerTitle}>Choose Your Plan</Text>
        <View style={styles.placeholder} />
      </View>

      {/* Billing Cycle Toggle */}
      <View style={styles.billingToggleContainer}>
        <TouchableOpacity
          style={[
            styles.billingToggleButton,
            billingCycle === 'monthly' && styles.billingToggleButtonActive
          ]}
          onPress={() => setBillingCycle('monthly')}
        >
          <Text style={[
            styles.billingToggleText,
            billingCycle === 'monthly' && styles.billingToggleTextActive
          ]}>
            Monthly
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[
            styles.billingToggleButton,
            billingCycle === 'annual' && styles.billingToggleButtonActive
          ]}
          onPress={() => setBillingCycle('annual')}
        >
          <Text style={[
            styles.billingToggleText,
            billingCycle === 'annual' && styles.billingToggleTextActive
          ]}>
            Annual
          </Text>
          <View style={styles.savingsBadge}>
            <Text style={styles.savingsBadgeText}>Save 17%</Text>
          </View>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Plans */}
        {plans.map((plan, index) => (
          <Animatable.View
            key={plan.id}
            animation="fadeInUp"
            delay={index * 200}
          >
            <TouchableOpacity
              style={[
                styles.planCard,
                plan.popular && styles.planCardPopular,
                { borderLeftColor: plan.color }
              ]}
              onPress={() => handleSelectPlan(plan.id)}
              activeOpacity={0.9}
            >
              {plan.popular && (
                <View style={styles.popularBadge}>
                  <Text style={styles.popularBadgeText}>⭐ MOST POPULAR</Text>
                </View>
              )}

              <View style={styles.planHeader}>
                <View>
                  <Text style={styles.planName}>{plan.name}</Text>
                  <Text style={styles.planDescription}>{plan.description}</Text>
                </View>
                
                <View style={styles.planPricing}>
                  <Text style={styles.planPrice}>
                    {plan.price[billingCycle] === 0 
                      ? 'FREE' 
                      : `£${plan.price[billingCycle]}`
                    }
                  </Text>
                  {plan.price[billingCycle] > 0 && (
                    <Text style={styles.planPeriod}>
                      /{billingCycle === 'monthly' ? 'month' : 'year'}
                    </Text>
                  )}
                </View>
              </View>

              <View style={styles.planFeatures}>
                {plan.features.map((feature, idx) => (
                  <View key={idx} style={styles.featureItem}>
                    <Text style={styles.featureCheck}>
                      {feature.startsWith('✅') || feature.startsWith('🏢') ? '' : '•'}
                    </Text>
                    <Text style={styles.featureText}>{feature}</Text>
                  </View>
                ))}
              </View>

              {plan.limitations && (
                <View style={styles.limitationsContainer}>
                  {plan.limitations.map((limit, idx) => (
                    <Text key={idx} style={styles.limitationText}>
                      ⚠️ {limit}
                    </Text>
                  ))}
                </View>
              )}

              <TouchableOpacity
                style={[
                  styles.planButton,
                  { backgroundColor: plan.color }
                ]}
                onPress={() => handleSelectPlan(plan.id)}
              >
                <Text style={styles.planButtonText}>{plan.buttonText}</Text>
              </TouchableOpacity>
            </TouchableOpacity>
          </Animatable.View>
        ))}

        {/* Money Back Guarantee */}
        <Animatable.View animation="fadeIn" delay={1000} style={styles.guaranteeCard}>
          <Text style={styles.guaranteeIcon}>💯</Text>
          <Text style={styles.guaranteeTitle}>14-Day Money-Back Guarantee</Text>
          <Text style={styles.guaranteeText}>
            Not satisfied? Get a full refund within 14 days, no questions asked.
          </Text>
        </Animatable.View>

        {/* FAQ */}
        <View style={styles.faqSection}>
          <Text style={styles.sectionTitle}>Frequently Asked Questions</Text>
          
          <View style={styles.faqItem}>
            <Text style={styles.faqQuestion}>Can I cancel anytime?</Text>
            <Text style={styles.faqAnswer}>
              Yes! You can cancel your subscription at any time. Your access will continue until the end of your billing period.
            </Text>
          </View>

          <View style={styles.faqItem}>
            <Text style={styles.faqQuestion}>Do you offer refunds?</Text>
            <Text style={styles.faqAnswer}>
              Yes, we offer a 14-day money-back guarantee on all paid plans.
            </Text>
          </View>

          <View style={styles.faqItem}>
            <Text style={styles.faqQuestion}>Can I upgrade or downgrade?</Text>
            <Text style={styles.faqAnswer}>
              Absolutely! You can change your plan at any time. Upgrades are prorated, and downgrades take effect at the next billing cycle.
            </Text>
          </View>
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
  billingToggleContainer: {
    flexDirection: 'row',
    backgroundColor: 'white',
    margin: 16,
    borderRadius: 12,
    padding: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  billingToggleButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    position: 'relative',
  },
  billingToggleButtonActive: {
    backgroundColor: '#0066CC',
  },
  billingToggleText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  billingToggleTextActive: {
    color: 'white',
  },
  savingsBadge: {
    position: 'absolute',
    top: -8,
    right: 8,
    backgroundColor: '#00A651',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
  },
  savingsBadgeText: {
    fontSize: 9,
    fontWeight: 'bold',
    color: 'white',
  },
  content: {
    flex: 1,
  },
  planCard: {
    backgroundColor: 'white',
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 20,
    padding: 20,
    borderLeftWidth: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 5,
  },
  planCardPopular: {
    borderWidth: 3,
    borderColor: '#0066CC',
    transform: [{ scale: 1.02 }],
  },
  popularBadge: {
    position: 'absolute',
    top: -12,
    left: 20,
    backgroundColor: '#0066CC',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 16,
    shadowColor: '#0066CC',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  popularBadgeText: {
    color: 'white',
    fontSize: 11,
    fontWeight: 'bold',
  },
  planHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 20,
  },
  planName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  planDescription: {
    fontSize: 13,
    color: '#666',
  },
  planPricing: {
    alignItems: 'flex-end',
  },
  planPrice: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#0066CC',
  },
  planPeriod: {
    fontSize: 12,
    color: '#999',
  },
  planFeatures: {
    marginBottom: 16,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  featureCheck: {
    fontSize: 14,
    color: '#00A651',
    marginRight: 8,
    fontWeight: 'bold',
  },
  featureText: {
    flex: 1,
    fontSize: 13,
    color: '#333',
    lineHeight: 20,
  },
  limitationsContainer: {
    backgroundColor: '#FFF3E0',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  limitationText: {
    fontSize: 11,
    color: '#F39C12',
    marginBottom: 4,
  },
  planButton: {
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  planButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  guaranteeCard: {
    backgroundColor: 'white',
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  guaranteeIcon: {
    fontSize: 40,
    marginBottom: 12,
  },
  guaranteeTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 8,
    textAlign: 'center',
  },
  guaranteeText: {
    fontSize: 13,
    color: '#666',
    textAlign: 'center',
    lineHeight: 20,
  },
  faqSection: {
    marginHorizontal: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 16,
  },
  faqItem: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  faqQuestion: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  faqAnswer: {
    fontSize: 13,
    color: '#666',
    lineHeight: 20,
  },
  bottomPadding: {
    height: 40,
  },
});

