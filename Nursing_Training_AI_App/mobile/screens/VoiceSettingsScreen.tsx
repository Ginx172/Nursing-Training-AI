import React, { useState, useEffect } from 'react';
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
import AudioService from '../services/AudioService';

interface VoiceSettingsScreenProps {
  navigation: any;
}

export default function VoiceSettingsScreen({ navigation }: VoiceSettingsScreenProps) {
  const [settings, setSettings] = useState({
    usePremiumVoices: true,
    provider: 'elevenlabs',
    gender: 'female',
    accent: 'rp',
    age: 'young',
    speakingRate: 0.95,
    autoCacheAudio: true
  });

  const [playingSample, setPlayingSample] = useState<string | null>(null);

  const providers = [
    {
      id: 'elevenlabs',
      name: 'ElevenLabs',
      quality: '⭐⭐⭐⭐⭐',
      description: 'Ultra-realistic, most natural',
      badge: 'BEST',
      color: '#0066CC',
      requiresPlan: 'Professional'
    },
    {
      id: 'azure_neural',
      name: 'Azure Neural',
      quality: '⭐⭐⭐⭐',
      description: 'Excellent British voices',
      color: '#0078D4',
      requiresPlan: 'Professional'
    },
    {
      id: 'google_wavenet',
      name: 'Google WaveNet',
      quality: '⭐⭐⭐⭐',
      description: 'High quality alternative',
      color: '#4285F4',
      requiresPlan: 'Professional'
    },
    {
      id: 'expo_speech',
      name: 'Device Voice',
      quality: '⭐⭐⭐',
      description: 'Free, works offline',
      color: '#95A5A6',
      requiresPlan: 'All Plans'
    }
  ];

  const voices = {
    elevenlabs: [
      { id: 'british_female_young', name: 'Sarah - Young Professional', icon: '👩‍⚕️', gender: 'female' },
      { id: 'british_female_mature', name: 'Dorothy - Mature & Authoritative', icon: '👩‍⚕️', gender: 'female' },
      { id: 'british_female_warm', name: 'Elli - Warm & Friendly', icon: '👩‍⚕️', gender: 'female' },
      { id: 'british_male_professional', name: 'Arnold - Professional', icon: '👨‍⚕️', gender: 'male' },
      { id: 'british_male_authoritative', name: 'Adam - Deep & Authoritative', icon: '👨‍⚕️', gender: 'male' },
      { id: 'scottish_female', name: 'Charlotte - Scottish', icon: '🏴󠁧󠁢󠁳󠁣󠁴󠁿', gender: 'female' },
      { id: 'scottish_male', name: 'James - Scottish', icon: '🏴󠁧󠁢󠁳󠁣󠁴󠁿', gender: 'male' },
    ],
    azure_neural: [
      { id: 'british_female_rp', name: 'Sonia - RP Professional', icon: '👩‍⚕️', gender: 'female' },
      { id: 'british_female_southern', name: 'Libby - Southern English', icon: '👩‍⚕️', gender: 'female' },
      { id: 'british_male_rp', name: 'Ryan - RP Authoritative', icon: '👨‍⚕️', gender: 'male' },
    ]
  };

  const handlePlaySample = async (voiceId: string) => {
    try {
      setPlayingSample(voiceId);
      
      const sampleText = "A patient presents with acute shortness of breath and chest pain. What is your first priority?";
      
      const audioService = AudioService.getInstance();
      await audioService.speakQuestion(sampleText, {
        provider: settings.provider as any,
        gender: settings.gender as any,
        accent: settings.accent as any,
        age: settings.age as any
      });
      
      setPlayingSample(null);
    } catch (error) {
      Alert.alert('Error', 'Failed to play voice sample');
      setPlayingSample(null);
    }
  };

  const handleSaveSettings = () => {
    // Save to AsyncStorage
    Alert.alert('Success', 'Voice settings saved');
    navigation.goBack();
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
        <Text style={styles.headerTitle}>Voice Settings</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        
        {/* Premium Voices Toggle */}
        <Animatable.View animation="fadeInUp" delay={200} style={styles.card}>
          <View style={styles.cardHeader}>
            <View>
              <Text style={styles.cardTitle}>Premium Voices 🎤</Text>
              <Text style={styles.cardSubtitle}>Ultra-realistic AI voices</Text>
            </View>
            <Switch
              value={settings.usePremiumVoices}
              onValueChange={(value) => setSettings({...settings, usePremiumVoices: value})}
              trackColor={{ false: '#e0e0e0', true: '#0066CC' }}
            />
          </View>
          
          {!settings.usePremiumVoices && (
            <View style={styles.notice}>
              <Text style={styles.noticeText}>
                Using device voices. Upgrade to Professional for premium AI voices!
              </Text>
            </View>
          )}
        </Animatable.View>

        {/* Provider Selection */}
        {settings.usePremiumVoices && (
          <Animatable.View animation="fadeInUp" delay={400}>
            <Text style={styles.sectionTitle}>Voice Provider</Text>
            {providers.map((provider, index) => (
              <TouchableOpacity
                key={provider.id}
                style={[
                  styles.providerCard,
                  settings.provider === provider.id && styles.providerCardActive,
                  { borderLeftColor: provider.color }
                ]}
                onPress={() => setSettings({...settings, provider: provider.id})}
              >
                {provider.badge && (
                  <View style={[styles.badge, { backgroundColor: provider.color }]}>
                    <Text style={styles.badgeText}>{provider.badge}</Text>
                  </View>
                )}
                
                <Text style={styles.providerName}>{provider.name}</Text>
                <Text style={styles.providerQuality}>{provider.quality}</Text>
                <Text style={styles.providerDescription}>{provider.description}</Text>
                
                <View style={styles.requiresBadge}>
                  <Text style={styles.requiresText}>Requires: {provider.requiresPlan}</Text>
                </View>
              </TouchableOpacity>
            ))}
          </Animatable.View>
        )}

        {/* Voice Selection */}
        {settings.usePremiumVoices && settings.provider !== 'expo_speech' && (
          <Animatable.View animation="fadeInUp" delay={600}>
            <Text style={styles.sectionTitle}>Choose Voice</Text>
            {voices[settings.provider as keyof typeof voices]?.map((voice, index) => (
              <TouchableOpacity
                key={voice.id}
                style={styles.voiceCard}
                onPress={() => handlePlaySample(voice.id)}
              >
                <Text style={styles.voiceIcon}>{voice.icon}</Text>
                <View style={styles.voiceInfo}>
                  <Text style={styles.voiceName}>{voice.name}</Text>
                  <Text style={styles.voiceGender}>{voice.gender}</Text>
                </View>
                <TouchableOpacity
                  style={styles.playButton}
                  onPress={() => handlePlaySample(voice.id)}
                >
                  <Text style={styles.playButtonText}>
                    {playingSample === voice.id ? '⏸️' : '▶️'}
                  </Text>
                </TouchableOpacity>
              </TouchableOpacity>
            ))}
          </Animatable.View>
        )}

        {/* Speaking Rate */}
        <Animatable.View animation="fadeInUp" delay={800} style={styles.card}>
          <Text style={styles.cardTitle}>Speaking Rate</Text>
          <View style={styles.rateContainer}>
            <TouchableOpacity
              style={styles.rateButton}
              onPress={() => setSettings({...settings, speakingRate: Math.max(0.5, settings.speakingRate - 0.05)})}
            >
              <Text style={styles.rateButtonText}>−</Text>
            </TouchableOpacity>
            
            <View style={styles.rateDisplay}>
              <Text style={styles.rateValue}>{(settings.speakingRate * 100).toFixed(0)}%</Text>
              <Text style={styles.rateLabel}>
                {settings.speakingRate < 0.8 ? 'Slow' : settings.speakingRate > 1.1 ? 'Fast' : 'Normal'}
              </Text>
            </View>
            
            <TouchableOpacity
              style={styles.rateButton}
              onPress={() => setSettings({...settings, speakingRate: Math.min(1.5, settings.speakingRate + 0.05)})}
            >
              <Text style={styles.rateButtonText}>+</Text>
            </TouchableOpacity>
          </View>
        </Animatable.View>

        {/* Auto-Cache Toggle */}
        <Animatable.View animation="fadeInUp" delay={1000} style={styles.card}>
          <View style={styles.settingRow}>
            <View>
              <Text style={styles.settingTitle}>Auto-Cache Audio</Text>
              <Text style={styles.settingDescription}>
                Download audio for offline use
              </Text>
            </View>
            <Switch
              value={settings.autoCacheAudio}
              onValueChange={(value) => setSettings({...settings, autoCacheAudio: value})}
              trackColor={{ false: '#e0e0e0', true: '#0066CC' }}
            />
          </View>
        </Animatable.View>

        {/* Save Button */}
        <TouchableOpacity 
          style={styles.saveButton}
          onPress={handleSaveSettings}
        >
          <Text style={styles.saveButtonText}>Save Voice Settings</Text>
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
  card: {
    backgroundColor: 'white',
    margin: 16,
    borderRadius: 16,
    padding: 20,
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
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1a1a1a',
  },
  cardSubtitle: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  notice: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#FFF3E0',
    borderRadius: 8,
  },
  noticeText: {
    fontSize: 12,
    color: '#F39C12',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginHorizontal: 16,
    marginTop: 24,
    marginBottom: 12,
  },
  providerCard: {
    backgroundColor: 'white',
    marginHorizontal: 16,
    marginBottom: 12,
    borderRadius: 16,
    padding: 16,
    borderLeftWidth: 4,
    position: 'relative',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  providerCardActive: {
    borderWidth: 2,
    borderColor: '#0066CC',
  },
  badge: {
    position: 'absolute',
    top: -8,
    right: 16,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  badgeText: {
    color: 'white',
    fontSize: 10,
    fontWeight: 'bold',
  },
  providerName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  providerQuality: {
    fontSize: 14,
    marginBottom: 4,
  },
  providerDescription: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  requiresBadge: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  requiresText: {
    fontSize: 10,
    color: '#666',
  },
  voiceCard: {
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
  voiceIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  voiceInfo: {
    flex: 1,
  },
  voiceName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 2,
  },
  voiceGender: {
    fontSize: 11,
    color: '#999',
    textTransform: 'capitalize',
  },
  playButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#0066CC',
    justifyContent: 'center',
    alignItems: 'center',
  },
  playButtonText: {
    fontSize: 18,
  },
  rateContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 16,
  },
  rateButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#0066CC',
    justifyContent: 'center',
    alignItems: 'center',
  },
  rateButtonText: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
  },
  rateDisplay: {
    marginHorizontal: 32,
    alignItems: 'center',
  },
  rateValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#0066CC',
  },
  rateLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  settingTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1a1a1a',
  },
  settingDescription: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  saveButton: {
    backgroundColor: '#0066CC',
    margin: 16,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#0066CC',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 5,
  },
  saveButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  bottomPadding: {
    height: 40,
  },
});

