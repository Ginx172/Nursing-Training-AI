import * as Speech from 'expo-speech';
import Voice from '@react-native-voice/voice';
import { Audio } from 'expo-av';

/**
 * Audio Service for Nursing Training AI
 * Handles Speech-to-Text and Text-to-Speech functionality
 */

export class AudioService {
  private static instance: AudioService;
  private isListening: boolean = false;
  private isSpeaking: boolean = false;

  private constructor() {
    this.initializeVoice();
  }

  public static getInstance(): AudioService {
    if (!AudioService.instance) {
      AudioService.instance = new AudioService();
    }
    return AudioService.instance;
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
   * TEXT-TO-SPEECH: Read question aloud
   */
  public async speakQuestion(questionText: string, options?: Speech.SpeechOptions): Promise<void> {
    try {
      // Stop any current speech
      if (this.isSpeaking) {
        await this.stopSpeaking();
      }

      // Set default options
      const defaultOptions: Speech.SpeechOptions = {
        language: 'en-GB', // British English
        pitch: 1.0,
        rate: 0.85, // Slightly slower for clarity
        voice: 'com.apple.ttsbundle.Serena-compact', // Female British voice (iOS)
        ...options
      };

      this.isSpeaking = true;
      
      // Speak the question
      await Speech.speak(questionText, {
        ...defaultOptions,
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
      });

    } catch (error) {
      console.error('Error speaking question:', error);
      this.isSpeaking = false;
      throw error;
    }
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

