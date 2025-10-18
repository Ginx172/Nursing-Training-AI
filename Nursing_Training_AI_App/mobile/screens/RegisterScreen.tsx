import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Picker } from '@react-native-picker/picker';
import * as Animatable from 'react-native-animatable';

interface RegisterScreenProps {
  navigation: any;
}

export default function RegisterScreen({ navigation }: RegisterScreenProps) {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    nmcNumber: '',
    currentBand: 'band_5',
    sector: 'nhs',
    specialty: 'amu'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const sectors = [
    { label: 'NHS Hospital', value: 'nhs' },
    { label: 'Private Healthcare', value: 'private_healthcare' },
    { label: 'Care Home', value: 'care_homes' },
    { label: 'Community Healthcare', value: 'community' },
    { label: 'Primary Care / GP Surgery', value: 'primary_care' }
  ];

  const bands = [
    { label: 'Band 2 - Healthcare Assistant', value: 'band_2' },
    { label: 'Band 3 - Senior HCA', value: 'band_3' },
    { label: 'Band 4 - Associate Practitioner', value: 'band_4' },
    { label: 'Band 5 - Staff Nurse', value: 'band_5' },
    { label: 'Band 6 - Senior Nurse', value: 'band_6' },
    { label: 'Band 7 - Advanced Practitioner', value: 'band_7' },
    { label: 'Band 8a - Senior Manager', value: 'band_8a' },
    { label: 'Band 8b - Associate Director', value: 'band_8b' },
    { label: 'Band 8c - Director', value: 'band_8c' },
    { label: 'Band 8d - Executive Director', value: 'band_8d' }
  ];

  const specialties = [
    { label: 'AMU/MAU', value: 'amu' },
    { label: 'Emergency/A&E', value: 'emergency' },
    { label: 'ICU/Critical Care', value: 'icu' },
    { label: 'Maternity', value: 'maternity' },
    { label: 'Mental Health', value: 'mental_health' },
    { label: 'Pediatrics', value: 'pediatrics' },
    { label: 'Cardiology', value: 'cardiology' },
    { label: 'Neurology', value: 'neurology' },
    { label: 'Oncology', value: 'oncology' }
  ];

  const handleRegister = async () => {
    // Validation
    if (!formData.fullName || !formData.email || !formData.password) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      Alert.alert('Error', 'Password must be at least 8 characters');
      return;
    }

    setIsLoading(true);
    try {
      // TODO: Integrate with backend API
      setTimeout(() => {
        setIsLoading(false);
        Alert.alert(
          'Registration Successful',
          'Your account has been created. Please sign in.',
          [{ text: 'OK', onPress: () => navigation.navigate('Login') }]
        );
      }, 1000);
      
    } catch (error) {
      setIsLoading(false);
      Alert.alert('Registration Failed', 'Please try again');
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <StatusBar style="light" />
      <ScrollView 
        contentContainerStyle={styles.scrollContainer}
        keyboardShouldPersistTaps="handled"
      >
        {/* Header */}
        <Animatable.View animation="fadeInDown" style={styles.header}>
          <Text style={styles.title}>Create Account</Text>
          <Text style={styles.subtitle}>Join thousands of UK healthcare professionals</Text>
        </Animatable.View>

        {/* Registration Form */}
        <Animatable.View animation="fadeInUp" delay={300} style={styles.formContainer}>
          
          {/* Full Name */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Full Name *</Text>
            <TextInput
              style={styles.input}
              placeholder="John Smith"
              placeholderTextColor="#999"
              value={formData.fullName}
              onChangeText={(text) => setFormData({...formData, fullName: text})}
              autoCapitalize="words"
            />
          </View>

          {/* Email */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Email Address *</Text>
            <TextInput
              style={styles.input}
              placeholder="your.email@nhs.net"
              placeholderTextColor="#999"
              value={formData.email}
              onChangeText={(text) => setFormData({...formData, email: text})}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
            />
          </View>

          {/* NMC Number */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>NMC/PIN Number (Optional)</Text>
            <TextInput
              style={styles.input}
              placeholder="12A3456E"
              placeholderTextColor="#999"
              value={formData.nmcNumber}
              onChangeText={(text) => setFormData({...formData, nmcNumber: text})}
              autoCapitalize="characters"
            />
          </View>

          {/* Sector */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Healthcare Sector *</Text>
            <View style={styles.pickerContainer}>
              <Picker
                selectedValue={formData.sector}
                onValueChange={(value) => setFormData({...formData, sector: value})}
                style={styles.picker}
              >
                {sectors.map((sector) => (
                  <Picker.Item key={sector.value} label={sector.label} value={sector.value} />
                ))}
              </Picker>
            </View>
          </View>

          {/* Current Band */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Current Band *</Text>
            <View style={styles.pickerContainer}>
              <Picker
                selectedValue={formData.currentBand}
                onValueChange={(value) => setFormData({...formData, currentBand: value})}
                style={styles.picker}
              >
                {bands.map((band) => (
                  <Picker.Item key={band.value} label={band.label} value={band.value} />
                ))}
              </Picker>
            </View>
          </View>

          {/* Specialty */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Specialty *</Text>
            <View style={styles.pickerContainer}>
              <Picker
                selectedValue={formData.specialty}
                onValueChange={(value) => setFormData({...formData, specialty: value})}
                style={styles.picker}
              >
                {specialties.map((spec) => (
                  <Picker.Item key={spec.value} label={spec.label} value={spec.value} />
                ))}
              </Picker>
            </View>
          </View>

          {/* Password */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Password *</Text>
            <View style={styles.passwordContainer}>
              <TextInput
                style={[styles.input, styles.passwordInput]}
                placeholder="Minimum 8 characters"
                placeholderTextColor="#999"
                value={formData.password}
                onChangeText={(text) => setFormData({...formData, password: text})}
                secureTextEntry={!showPassword}
                autoCapitalize="none"
                autoCorrect={false}
              />
              <TouchableOpacity 
                style={styles.eyeIcon}
                onPress={() => setShowPassword(!showPassword)}
              >
                <Text style={styles.eyeIconText}>{showPassword ? '👁️' : '👁️‍🗨️'}</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Confirm Password */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Confirm Password *</Text>
            <TextInput
              style={styles.input}
              placeholder="Re-enter your password"
              placeholderTextColor="#999"
              value={formData.confirmPassword}
              onChangeText={(text) => setFormData({...formData, confirmPassword: text})}
              secureTextEntry={!showPassword}
              autoCapitalize="none"
              autoCorrect={false}
            />
          </View>

          {/* Register Button */}
          <TouchableOpacity 
            style={[styles.registerButton, isLoading && styles.registerButtonDisabled]}
            onPress={handleRegister}
            disabled={isLoading}
          >
            <Text style={styles.registerButtonText}>
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </Text>
          </TouchableOpacity>

          {/* Login Link */}
          <View style={styles.loginContainer}>
            <Text style={styles.loginText}>Already have an account? </Text>
            <TouchableOpacity onPress={() => navigation.navigate('Login')}>
              <Text style={styles.loginLink}>Sign In</Text>
            </TouchableOpacity>
          </View>

          {/* Terms */}
          <Text style={styles.termsText}>
            By creating an account, you agree to our Terms of Service and Privacy Policy
          </Text>
        </Animatable.View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0066CC',
  },
  scrollContainer: {
    flexGrow: 1,
  },
  header: {
    paddingTop: 60,
    paddingBottom: 30,
    alignItems: 'center',
    backgroundColor: '#0066CC',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
    paddingHorizontal: 20,
  },
  formContainer: {
    flex: 1,
    backgroundColor: 'white',
    borderTopLeftRadius: 30,
    borderTopRightRadius: 30,
    paddingHorizontal: 24,
    paddingTop: 32,
    paddingBottom: 24,
  },
  inputContainer: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  pickerContainer: {
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    overflow: 'hidden',
  },
  picker: {
    height: 50,
  },
  passwordContainer: {
    position: 'relative',
  },
  passwordInput: {
    paddingRight: 50,
  },
  eyeIcon: {
    position: 'absolute',
    right: 16,
    top: 16,
  },
  eyeIconText: {
    fontSize: 20,
  },
  registerButton: {
    backgroundColor: '#0066CC',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 24,
    shadowColor: '#0066CC',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 5,
  },
  registerButtonDisabled: {
    backgroundColor: '#ccc',
  },
  registerButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 24,
  },
  loginText: {
    color: '#666',
    fontSize: 14,
  },
  loginLink: {
    color: '#0066CC',
    fontSize: 14,
    fontWeight: 'bold',
  },
  termsText: {
    fontSize: 11,
    color: '#999',
    textAlign: 'center',
    marginTop: 16,
    paddingHorizontal: 16,
  },
});

