import * as Speech from 'expo-speech';
import Voice from '@react-native-voice/voice';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * Audio Service for Nursing Training AI - ENTERPRISE EDITION
 * Premium voices using ElevenLabs, Azure Neural TTS, and Google WaveNet
 */

interface VoicePreferences {
  provider?: 'elevenlabs' | 'azure_neural' | 'google_wavenet' | 'expo_speech';
  gender?: 'male' | 'female';
  accent?: 'rp' | 'scottish' | 'welsh' | 'northern';
  age?: 'young' | 'mature';
  speakingRate?: number;
}

export class AudioService {
  private static instance: AudioService;
  private isListening: boolean = false;
  private isSpeaking: boolean = false;
  private currentSound: Audio.Sound | null = null;
  private apiUrl: string = 'https://api.nursingtrainingai.com';
  private apiKey: string = '';

  private constructor() {
    this.initializeVoice();
    this.loadApiKey();
  }

  public static getInstance(): AudioService {
    if (!AudioService.instance) {
      AudioService.instance = new AudioService();
    }
    return AudioService.instance;
  }

  private async loadApiKey() {
    try {
      const key = await AsyncStorage.getItem('api_key');
      if (key) {
        this.apiKey = key;
      }
    } catch (error) {
      console.error('Error loading API key:', error);
    }
  }

  /**
   * Initialize Voice Recognition
   */
  private async initializeVoice() {
    try {
      Voice.onSpeechStart = this.onSpeechStart.bind(this);
      Voice.onSpeechEnd = this.onSpeechEnd.bind(this);
      Voice.onSpeechResults = this.onSpeechResults.bind(this);
      Voice.onSpeechError = this.onSpeechError.bind(this);
    } catch (error) {
      console.error('Error initializing voice:', error);
    }
  }

  /**
   * TEXT-TO-SPEECH: Read question aloud with PREMIUM VOICES
   * Uses cloud TTS for ultra-realistic voices (Professional/Enterprise)
   * Falls back to device TTS for Demo/Basic plans
   */
  public async speakQuestion(
    questionText: string, 
    preferences?: VoicePreferences,
    usePremiumVoice: boolean = true
  ): Promise<void> {
    try {
      // Stop any current speech
      if (this.isSpeaking) {
        await this.stopSpeaking();
      }

      this.isSpeaking = true;

      // Use premium cloud voices if available (Professional/Enterprise plans)
      if (usePremiumVoice && this.apiKey) {
        try {
          await this.speakWithCloudTTS(questionText, preferences);
          return;
        } catch (error) {
          console.warn('Cloud TTS failed, falling back to device TTS:', error);
          // Fall through to device TTS
        }
      }

      // Fallback: Use device TTS (Expo Speech)
      await this.speakWithDeviceTTS(questionText, preferences);

    } catch (error) {
      console.error('Error speaking question:', error);
      this.isSpeaking = false;
      throw error;
    }
  }

  /**
   * PREMIUM: Cloud TTS with ultra-realistic voices
   */
  private async speakWithCloudTTS(
    text: string,
    preferences?: VoicePreferences
  ): Promise<void> {
    try {
      // Check if audio is cached offline
      const cachedAudio = await this.getCachedAudio(text, preferences);
      if (cachedAudio) {
        await this.playAudioFile(cachedAudio);
        return;
      }

      // Request audio from backend
      const response = await fetch(`${this.apiUrl}/api/tts/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': this.apiKey
        },
        body: JSON.stringify({
          text,
          preferences: preferences || {
            provider: 'elevenlabs',
            gender: 'female',
            accent: 'rp',
            age: 'young'
          }
        })
      });

      if (!response.ok) {
        throw new Error('TTS API request failed');
      }

      const audioBlob = await response.blob();
      const audioBase64 = await this.blobToBase64(audioBlob);

      // Save to local storage for offline use
      const audioUri = await this.saveAudioLocally(text, audioBase64, preferences);

      // Play audio
      await this.playAudioFile(audioUri);

    } catch (error) {
      console.error('Cloud TTS error:', error);
      throw error;
    }
  }

  /**
   * FALLBACK: Device TTS (Free, works offline)
   */
  private async speakWithDeviceTTS(
    text: string,
    preferences?: VoicePreferences
  ): Promise<void> {
    const options: Speech.SpeechOptions = {
      language: 'en-GB',
      pitch: 1.0,
      rate: preferences?.speakingRate || 0.90,
      voice: 'com.apple.ttsbundle.Serena-compact',
      onDone: () => {
        this.isSpeaking = false;
      },
      onStopped: () => {
        this.isSpeaking = false;
      },
      onError: (error) => {
        console.error('Speech error:', error);
        this.isSpeaking = false;
      }
    };

    await Speech.speak(text, options);
  }

  /**
   * Play audio file
   */
  private async playAudioFile(uri: string): Promise<void> {
    try {
      // Unload previous sound
      if (this.currentSound) {
        await this.currentSound.unloadAsync();
      }

      // Load and play
      const { sound } = await Audio.Sound.createAsync(
        { uri },
        { shouldPlay: true },
        (status) => {
          if (status.isLoaded && status.didJustFinish) {
            this.isSpeaking = false;
          }
        }
      );

      this.currentSound = sound;
      await sound.playAsync();

    } catch (error) {
      console.error('Error playing audio:', error);
      this.isSpeaking = false;
      throw error;
    }
  }

  /**
   * Cache management
   */
  private async getCachedAudio(
    text: string,
    preferences?: VoicePreferences
  ): Promise<string | null> {
    try {
      const cacheKey = this.generateCacheKey(text, preferences);
      const cacheUri = `${FileSystem.documentDirectory}audio_cache/${cacheKey}.mp3`;
      
      const fileInfo = await FileSystem.getInfoAsync(cacheUri);
      if (fileInfo.exists) {
        return cacheUri;
      }
      
      return null;
    } catch (error) {
      console.error('Error getting cached audio:', error);
      return null;
    }
  }

  private async saveAudioLocally(
    text: string,
    audioBase64: string,
    preferences?: VoicePreferences
  ): Promise<string> {
    try {
      const cacheKey = this.generateCacheKey(text, preferences);
      const cacheDir = `${FileSystem.documentDirectory}audio_cache/`;
      const cacheUri = `${cacheDir}${cacheKey}.mp3`;

      // Create directory if doesn't exist
      const dirInfo = await FileSystem.getInfoAsync(cacheDir);
      if (!dirInfo.exists) {
        await FileSystem.makeDirectoryAsync(cacheDir, { intermediates: true });
      }

      // Save audio file
      await FileSystem.writeAsStringAsync(cacheUri, audioBase64, {
        encoding: FileSystem.EncodingType.Base64
      });

      return cacheUri;
    } catch (error) {
      console.error('Error saving audio:', error);
      throw error;
    }
  }

  private generateCacheKey(text: string, preferences?: VoicePreferences): string {
    const data = `${text}:${JSON.stringify(preferences || {})}`;
    // Simple hash function
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      const char = data.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash).toString(36);
  }

  private async blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = (reader.result as string).split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  /**
   * Stop current speech
   */
  public async stopSpeaking(): Promise<void> {
    try {
      await Speech.stop();
      this.isSpeaking = false;
    } catch (error) {
      console.error('Error stopping speech:', error);
    }
  }

  /**
   * Check if currently speaking
   */
  public isCurrentlySpeaking(): boolean {
    return this.isSpeaking;
  }

  /**
   * Get available voices
   */
  public async getAvailableVoices(): Promise<Speech.Voice[]> {
    try {
      const voices = await Speech.getAvailableVoicesAsync();
      // Filter for British English voices
      return voices.filter(voice => 
        voice.language.startsWith('en-GB') || voice.language.startsWith('en-UK')
      );
    } catch (error) {
      console.error('Error getting voices:', error);
      return [];
    }
  }

  /**
   * SPEECH-TO-TEXT: Start listening for answer
   */
  public async startListening(onResult: (result: string) => void): Promise<void> {
    try {
      // Request audio permission
      const { status } = await Audio.requestPermissionsAsync();
      
      if (status !== 'granted') {
        throw new Error('Audio permission not granted');
      }

      // Check if already listening
      if (this.isListening) {
        await this.stopListening();
      }

      this.isListening = true;

      // Start voice recognition
      await Voice.start('en-GB'); // British English
      
      // Set up result callback
      Voice.onSpeechResults = (e) => {
        if (e.value && e.value.length > 0) {
          onResult(e.value[0]);
        }
      };

    } catch (error) {
      console.error('Error starting voice recognition:', error);
      this.isListening = false;
      throw error;
    }
  }

  /**
   * Stop listening
   */
  public async stopListening(): Promise<void> {
    try {
      await Voice.stop();
      this.isListening = false;
    } catch (error) {
      console.error('Error stopping voice recognition:', error);
    }
  }

  /**
   * Cancel listening
   */
  public async cancelListening(): Promise<void> {
    try {
      await Voice.cancel();
      this.isListening = false;
    } catch (error) {
      console.error('Error canceling voice recognition:', error);
    }
  }

  /**
   * Check if currently listening
   */
  public isCurrentlyListening(): boolean {
    return this.isListening;
  }

  /**
   * Destroy voice recognition
   */
  public async destroy(): Promise<void> {
    try {
      await Voice.destroy();
      Voice.removeAllListeners();
      this.isListening = false;
    } catch (error) {
      console.error('Error destroying voice:', error);
    }
  }

  // Voice recognition event handlers
  private onSpeechStart(e: any) {
    console.log('Speech started:', e);
  }

  private onSpeechEnd(e: any) {
    console.log('Speech ended:', e);
    this.isListening = false;
  }

  private onSpeechResults(e: any) {
    console.log('Speech results:', e.value);
  }

  private onSpeechError(e: any) {
    console.error('Speech error:', e);
    this.isListening = false;
  }

  /**
   * Utility: Speak with specific voice style
   */
  public async speakWithStyle(
    text: string,
    style: 'normal' | 'slow' | 'fast' | 'clear'
  ): Promise<void> {
    const styleOptions: { [key: string]: Speech.SpeechOptions } = {
      normal: { rate: 0.85, pitch: 1.0 },
      slow: { rate: 0.6, pitch: 1.0 },
      fast: { rate: 1.2, pitch: 1.0 },
      clear: { rate: 0.7, pitch: 1.1 }
    };

    await this.speakQuestion(text, styleOptions[style]);
  }

  /**
   * Utility: Spell out text (for NMC numbers, etc.)
   */
  public async spellOut(text: string): Promise<void> {
    const spelled = text.split('').join(' ');
    await this.speakQuestion(spelled, { rate: 0.5 });
  }
}

// Export singleton instance
export default AudioService.getInstance();

