import React, { useState } from 'react';
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

interface SpecialtiesScreenProps {
  navigation: any;
}

export default function SpecialtiesScreen({ navigation }: SpecialtiesScreenProps) {
  const [selectedSector, setSelectedSector] = useState('nhs');
  const [selectedBand, setSelectedBand] = useState('band_5');

  const sectors = [
    { id: 'nhs', name: 'NHS', icon: '🏥', color: '#0066CC' },
    { id: 'private_healthcare', name: 'Private', icon: '💼', color: '#9B59B6' },
    { id: 'care_homes', name: 'Care Homes', icon: '🏠', color: '#E74C3C' },
    { id: 'community', name: 'Community', icon: '🚑', color: '#00A651' },
    { id: 'primary_care', name: 'Primary Care', icon: '⚕️', color: '#F39C12' }
  ];

  const nhsSpecialties = [
    { id: 'amu', name: 'AMU/MAU', icon: '🏥', questions: 900, color: '#0066CC' },
    { id: 'emergency', name: 'Emergency/A&E', icon: '🚨', questions: 850, color: '#E74C3C' },
    { id: 'icu', name: 'ICU/Critical Care', icon: '💉', questions: 920, color: '#8E44AD' },
    { id: 'maternity', name: 'Maternity', icon: '👶', questions: 780, color: '#FF69B4' },
    { id: 'mental_health', name: 'Mental Health', icon: '🧠', questions: 840, color: '#3498DB' },
    { id: 'pediatrics', name: 'Pediatrics', icon: '🎈', questions: 800, color: '#F39C12' },
    { id: 'cardiology', name: 'Cardiology', icon: '❤️', questions: 760, color: '#E74C3C' },
    { id: 'neurology', name: 'Neurology', icon: '🧬', questions: 720, color: '#9B59B6' },
    { id: 'oncology', name: 'Oncology', icon: '🎗️', questions: 790, color: '#16A085' }
  ];

  const privateSpecialties = [
    { id: 'theatre', name: 'Theatre', icon: '⚕️', questions: 420, color: '#9B59B6' },
    { id: 'recovery', name: 'Recovery', icon: '🛏️', questions: 380, color: '#3498DB' },
    { id: 'ward', name: 'Ward', icon: '🏥', questions: 400, color: '#0066CC' },
    { id: 'endoscopy', name: 'Endoscopy', icon: '🔬', questions: 360, color: '#16A085' },
    { id: 'cosmetic', name: 'Cosmetic', icon: '✨', questions: 340, color: '#FF69B4' },
    { id: 'pre_assessment', name: 'Pre-Assessment', icon: '📋', questions: 320, color: '#F39C12' }
  ];

  const careHomeSpecialties = [
    { id: 'residential_care', name: 'Residential Care', icon: '🏠', questions: 280, color: '#E74C3C' },
    { id: 'nursing_home', name: 'Nursing Home', icon: '🩺', questions: 260, color: '#0066CC' },
    { id: 'dementia_care', name: 'Dementia Care', icon: '🧠', questions: 240, color: '#9B59B6' },
    { id: 'palliative_care', name: 'Palliative Care', icon: '🕊️', questions: 220, color: '#16A085' }
  ];

  const communitySpecialties = [
    { id: 'district_nursing', name: 'District Nursing', icon: '🚑', questions: 250, color: '#00A651' },
    { id: 'health_visiting', name: 'Health Visiting', icon: '👶', questions: 230, color: '#FF69B4' },
    { id: 'community_mental_health', name: 'Community MH', icon: '🧠', questions: 210, color: '#3498DB' },
    { id: 'school_nursing', name: 'School Nursing', icon: '🎒', questions: 190, color: '#F39C12' },
    { id: 'community_matron', name: 'Community Matron', icon: '👩‍⚕️', questions: 200, color: '#9B59B6' }
  ];

  const primaryCareSpecialties = [
    { id: 'practice_nursing', name: 'Practice Nursing', icon: '⚕️', questions: 350, color: '#F39C12' },
    { id: 'advanced_practitioner', name: 'Advanced Practitioner', icon: '👨‍⚕️', questions: 320, color: '#0066CC' },
    { id: 'hca_primary_care', name: 'HCA Primary Care', icon: '🩺', questions: 280, color: '#00A651' },
    { id: 'chronic_disease', name: 'Chronic Disease', icon: '💊', questions: 300, color: '#E74C3C' },
    { id: 'immunizations', name: 'Immunizations', icon: '💉', questions: 260, color: '#3498DB' }
  ];

  const getSpecialtiesForSector = () => {
    switch (selectedSector) {
      case 'nhs': return nhsSpecialties;
      case 'private_healthcare': return privateSpecialties;
      case 'care_homes': return careHomeSpecialties;
      case 'community': return communitySpecialties;
      case 'primary_care': return primaryCareSpecialties;
      default: return nhsSpecialties;
    }
  };

  const handleSpecialtySelect = (specialtyId: string) => {
    navigation.navigate('Questions', {
      sector: selectedSector,
      specialty: specialtyId,
      band: selectedBand
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
        <Text style={styles.headerTitle}>Choose Your Specialty</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Sector Selection */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Healthcare Sector</Text>
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.sectorScroll}
          >
            {sectors.map((sector, index) => (
              <Animatable.View
                key={sector.id}
                animation="fadeInRight"
                delay={index * 100}
              >
                <TouchableOpacity
                  style={[
                    styles.sectorCard,
                    selectedSector === sector.id && styles.sectorCardActive,
                    { borderColor: sector.color }
                  ]}
                  onPress={() => setSelectedSector(sector.id)}
                >
                  <Text style={styles.sectorIcon}>{sector.icon}</Text>
                  <Text style={[
                    styles.sectorName,
                    selectedSector === sector.id && styles.sectorNameActive
                  ]}>
                    {sector.name}
                  </Text>
                </TouchableOpacity>
              </Animatable.View>
            ))}
          </ScrollView>
        </View>

        {/* Band Selection */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Current Band Level</Text>
          <View style={styles.bandGrid}>
            {['band_2', 'band_3', 'band_4', 'band_5', 'band_6', 'band_7', 'band_8a'].map((band, index) => (
              <Animatable.View
                key={band}
                animation="fadeInUp"
                delay={index * 50}
              >
                <TouchableOpacity
                  style={[
                    styles.bandCard,
                    selectedBand === band && styles.bandCardActive
                  ]}
                  onPress={() => setSelectedBand(band)}
                >
                  <Text style={[
                    styles.bandText,
                    selectedBand === band && styles.bandTextActive
                  ]}>
                    {band.replace('_', ' ').toUpperCase()}
                  </Text>
                </TouchableOpacity>
              </Animatable.View>
            ))}
          </View>
        </View>

        {/* Specialties Grid */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            {sectors.find(s => s.id === selectedSector)?.name} Specialties
          </Text>
          <View style={styles.specialtiesGrid}>
            {getSpecialtiesForSector().map((specialty, index) => (
              <Animatable.View
                key={specialty.id}
                animation="zoomIn"
                delay={index * 100}
              >
                <TouchableOpacity
                  style={[styles.specialtyCard, { borderLeftColor: specialty.color }]}
                  onPress={() => handleSpecialtySelect(specialty.id)}
                  activeOpacity={0.7}
                >
                  <View style={styles.specialtyHeader}>
                    <Text style={styles.specialtyIcon}>{specialty.icon}</Text>
                    <View style={styles.specialtyInfo}>
                      <Text style={styles.specialtyName}>{specialty.name}</Text>
                      <Text style={styles.specialtyQuestions}>
                        {specialty.questions} questions available
                      </Text>
                    </View>
                  </View>
                  <Text style={styles.specialtyArrow}>→</Text>
                </TouchableOpacity>
              </Animatable.View>
            ))}
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
  content: {
    flex: 1,
  },
  section: {
    marginTop: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginHorizontal: 16,
    marginBottom: 12,
  },
  sectorScroll: {
    paddingHorizontal: 16,
    gap: 12,
  },
  sectorCard: {
    width: 100,
    height: 100,
    backgroundColor: 'white',
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#e0e0e0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectorCardActive: {
    borderWidth: 3,
    transform: [{ scale: 1.05 }],
  },
  sectorIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  sectorName: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
    textAlign: 'center',
  },
  sectorNameActive: {
    color: '#0066CC',
    fontWeight: 'bold',
  },
  bandGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    gap: 8,
  },
  bandCard: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: 'white',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  bandCardActive: {
    backgroundColor: '#0066CC',
    borderColor: '#0066CC',
  },
  bandText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
  },
  bandTextActive: {
    color: 'white',
  },
  specialtiesGrid: {
    paddingHorizontal: 16,
    gap: 12,
  },
  specialtyCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 16,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  specialtyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  specialtyIcon: {
    fontSize: 32,
    marginRight: 16,
  },
  specialtyInfo: {
    flex: 1,
  },
  specialtyName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  specialtyQuestions: {
    fontSize: 12,
    color: '#666',
  },
  specialtyArrow: {
    fontSize: 20,
    color: '#0066CC',
    fontWeight: 'bold',
    marginLeft: 12,
  },
  bottomPadding: {
    height: 40,
  },
});

