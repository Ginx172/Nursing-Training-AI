import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system';
import NetInfo from '@react-native-community/netinfo';

/**
 * Offline Service for Nursing Training AI
 * Enables offline access to questions and user progress
 */

interface OfflineQuestion {
  id: string;
  sector: string;
  specialty: string;
  band: string;
  bankNumber: number;
  questions: any[];
  lastSynced: string;
}

interface OfflineProgress {
  userId: string;
  questionsCompleted: number;
  answers: any[];
  lastSynced: string;
  pendingSync: boolean;
}

export class OfflineService {
  private static instance: OfflineService;
  private isOnline: boolean = true;
  private questionCache: Map<string, OfflineQuestion> = new Map();

  private constructor() {
    this.initializeNetworkListener();
  }

  public static getInstance(): OfflineService {
    if (!OfflineService.instance) {
      OfflineService.instance = new OfflineService();
    }
    return OfflineService.instance;
  }

  /**
   * Initialize network status listener
   */
  private initializeNetworkListener() {
    NetInfo.addEventListener(state => {
      const wasOffline = !this.isOnline;
      this.isOnline = state.isConnected ?? false;
      
      // If we just came back online, sync pending data
      if (wasOffline && this.isOnline) {
        this.syncPendingData();
      }
    });
  }

  /**
   * Check if device is online
   */
  public async isDeviceOnline(): Promise<boolean> {
    const netInfo = await NetInfo.fetch();
    this.isOnline = netInfo.isConnected ?? false;
    return this.isOnline;
  }

  /**
   * Download question banks for offline use
   */
  public async downloadQuestionBank(
    sector: string,
    specialty: string,
    band: string,
    bankNumber: number
  ): Promise<void> {
    try {
      const cacheKey = `${sector}_${specialty}_${band}_${bankNumber}`;
      
      // Check if already cached
      if (this.questionCache.has(cacheKey)) {
        console.log('Question bank already cached');
        return;
      }

      // Download from backend
      const response = await fetch(
        `YOUR_API_URL/questions/${sector}/${specialty}/${band}/${bankNumber}`
      );
      const questionBank = await response.json();

      // Save to AsyncStorage
      const offlineQuestion: OfflineQuestion = {
        id: cacheKey,
        sector,
        specialty,
        band,
        bankNumber,
        questions: questionBank.questions,
        lastSynced: new Date().toISOString()
      };

      await AsyncStorage.setItem(
        `question_bank_${cacheKey}`,
        JSON.stringify(offlineQuestion)
      );

      this.questionCache.set(cacheKey, offlineQuestion);
      
      console.log(`Downloaded question bank: ${cacheKey}`);
    } catch (error) {
      console.error('Error downloading question bank:', error);
      throw error;
    }
  }

  /**
   * Get cached question bank (offline mode)
   */
  public async getCachedQuestionBank(
    sector: string,
    specialty: string,
    band: string,
    bankNumber: number
  ): Promise<OfflineQuestion | null> {
    try {
      const cacheKey = `${sector}_${specialty}_${band}_${bankNumber}`;
      
      // Check in-memory cache first
      if (this.questionCache.has(cacheKey)) {
        return this.questionCache.get(cacheKey) || null;
      }

      // Check AsyncStorage
      const cached = await AsyncStorage.getItem(`question_bank_${cacheKey}`);
      
      if (cached) {
        const questionBank = JSON.parse(cached);
        this.questionCache.set(cacheKey, questionBank);
        return questionBank;
      }

      return null;
    } catch (error) {
      console.error('Error getting cached question bank:', error);
      return null;
    }
  }

  /**
   * Save user progress offline
   */
  public async saveProgressOffline(
    userId: string,
    questionId: string,
    answer: any,
    score: number
  ): Promise<void> {
    try {
      // Load existing offline progress
      const existingProgress = await this.getOfflineProgress(userId);
      
      const progress: OfflineProgress = existingProgress || {
        userId,
        questionsCompleted: 0,
        answers: [],
        lastSynced: new Date().toISOString(),
        pendingSync: false
      };

      // Add new answer
      progress.answers.push({
        questionId,
        answer,
        score,
        timestamp: new Date().toISOString()
      });
      progress.questionsCompleted++;
      progress.pendingSync = true;

      // Save to AsyncStorage
      await AsyncStorage.setItem(
        `progress_${userId}`,
        JSON.stringify(progress)
      );

      console.log('Progress saved offline');
    } catch (error) {
      console.error('Error saving progress offline:', error);
      throw error;
    }
  }

  /**
   * Get offline progress
   */
  private async getOfflineProgress(userId: string): Promise<OfflineProgress | null> {
    try {
      const cached = await AsyncStorage.getItem(`progress_${userId}`);
      return cached ? JSON.parse(cached) : null;
    } catch (error) {
      console.error('Error getting offline progress:', error);
      return null;
    }
  }

  /**
   * Sync pending data when online
   */
  public async syncPendingData(): Promise<void> {
    try {
      if (!this.isOnline) {
        console.log('Device is offline, cannot sync');
        return;
      }

      // Get all progress items with pending sync
      const keys = await AsyncStorage.getAllKeys();
      const progressKeys = keys.filter(key => key.startsWith('progress_'));

      for (const key of progressKeys) {
        const cached = await AsyncStorage.getItem(key);
        if (!cached) continue;

        const progress: OfflineProgress = JSON.parse(cached);
        
        if (progress.pendingSync) {
          // Sync with backend
          await this.syncProgressToBackend(progress);
          
          // Mark as synced
          progress.pendingSync = false;
          progress.lastSynced = new Date().toISOString();
          
          await AsyncStorage.setItem(key, JSON.stringify(progress));
        }
      }

      console.log('Sync completed successfully');
    } catch (error) {
      console.error('Error syncing data:', error);
    }
  }

  /**
   * Sync progress to backend
   */
  private async syncProgressToBackend(progress: OfflineProgress): Promise<void> {
    try {
      const response = await fetch(`YOUR_API_URL/progress/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(progress)
      });

      if (!response.ok) {
        throw new Error('Sync failed');
      }

      console.log('Progress synced to backend');
    } catch (error) {
      console.error('Error syncing to backend:', error);
      throw error;
    }
  }

  /**
   * Download essential content for offline use
   */
  public async downloadEssentialContent(
    userId: string,
    userPreferences: {
      sector: string;
      specialty: string;
      band: string;
    }
  ): Promise<void> {
    try {
      // Download first 3 question banks for user's specialty and band
      for (let i = 1; i <= 3; i++) {
        await this.downloadQuestionBank(
          userPreferences.sector,
          userPreferences.specialty,
          userPreferences.band,
          i
        );
      }

      // Mark as downloaded
      await AsyncStorage.setItem(
        `offline_ready_${userId}`,
        JSON.stringify({
          ready: true,
          downloadedAt: new Date().toISOString(),
          preferences: userPreferences
        })
      );

      console.log('Essential content downloaded for offline use');
    } catch (error) {
      console.error('Error downloading essential content:', error);
      throw error;
    }
  }

  /**
   * Check if offline content is ready
   */
  public async isOfflineReady(userId: string): Promise<boolean> {
    try {
      const cached = await AsyncStorage.getItem(`offline_ready_${userId}`);
      if (!cached) return false;

      const offlineData = JSON.parse(cached);
      return offlineData.ready === true;
    } catch (error) {
      console.error('Error checking offline ready:', error);
      return false;
    }
  }

  /**
   * Clear offline cache
   */
  public async clearOfflineCache(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => 
        key.startsWith('question_bank_') || key.startsWith('offline_ready_')
      );

      await AsyncStorage.multiRemove(cacheKeys);
      this.questionCache.clear();

      console.log('Offline cache cleared');
    } catch (error) {
      console.error('Error clearing cache:', error);
      throw error;
    }
  }

  /**
   * Get cache statistics
   */
  public async getCacheStats(): Promise<{
    totalBanks: number;
    totalSize: string;
    lastSync: string;
  }> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => key.startsWith('question_bank_'));
      
      let totalSize = 0;
      let lastSync = '';

      for (const key of cacheKeys) {
        const item = await AsyncStorage.getItem(key);
        if (item) {
          totalSize += item.length;
          const data = JSON.parse(item);
          if (data.lastSynced > lastSync) {
            lastSync = data.lastSynced;
          }
        }
      }

      return {
        totalBanks: cacheKeys.length,
        totalSize: `${(totalSize / 1024 / 1024).toFixed(2)} MB`,
        lastSync
      };
    } catch (error) {
      console.error('Error getting cache stats:', error);
      return { totalBanks: 0, totalSize: '0 MB', lastSync: '' };
    }
  }
}

// Export singleton instance
export default OfflineService.getInstance();

