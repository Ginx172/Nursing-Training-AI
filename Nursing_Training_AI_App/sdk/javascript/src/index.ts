/**
 * Nursing Training AI - JavaScript/TypeScript SDK
 * Official client library for Enterprise API integration
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// ========================================
// INTERFACES
// ========================================

export interface User {
  id: string;
  email: string;
  name: string;
  nmcNumber?: string;
  currentBand: string;
  sector: string;
  specialty: string;
  subscriptionTier: string;
}

export interface Question {
  id: string;
  sector: string;
  specialty: string;
  band: string;
  questionType: string;
  questionText: string;
  difficulty: string;
  competencies: string[];
}

export interface Analytics {
  userId: string;
  questionsCompleted: number;
  accuracyPercentage: number;
  timeSpentMinutes: number;
}

export interface NursingAIConfig {
  apiKey?: string;
  baseUrl?: string;
  timeout?: number;
}

// ========================================
// EXCEPTIONS
// ========================================

export class NursingAIError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NursingAIError';
  }
}

export class AuthenticationError extends NursingAIError {
  constructor(message: string = 'Authentication failed') {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class RateLimitError extends NursingAIError {
  constructor(message: string = 'Rate limit exceeded') {
    super(message);
    this.name = 'RateLimitError';
  }
}

// ========================================
// MAIN CLIENT
// ========================================

export class NursingAIClient {
  private client: AxiosInstance;
  
  public users: UserResource;
  public questions: QuestionResource;
  public analytics: AnalyticsResource;
  
  constructor(config: NursingAIConfig = {}) {
    const {
      apiKey,
      baseUrl = 'https://api.nursingtrainingai.com',
      timeout = 30000
    } = config;
    
    this.client = axios.create({
      baseURL: baseUrl,
      timeout,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'NursingAI-JS-SDK/1.0.0',
        ...(apiKey && { 'X-API-Key': apiKey })
      }
    });
    
    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      response => response,
      this.handleError
    );
    
    // Initialize resources
    this.users = new UserResource(this.client);
    this.questions = new QuestionResource(this.client);
    this.analytics = new AnalyticsResource(this.client);
  }
  
  private handleError(error: AxiosError): Promise<never> {
    if (error.response) {
      const status = error.response.status;
      
      if (status === 401 || status === 403) {
        throw new AuthenticationError('Invalid API key or unauthorized');
      } else if (status === 429) {
        throw new RateLimitError();
      }
    }
    
    throw new NursingAIError(error.message);
  }
}

// ========================================
// RESOURCE CLASSES
// ========================================

class UserResource {
  constructor(private client: AxiosInstance) {}
  
  async get(userId: string): Promise<User> {
    const response = await this.client.get(`/api/users/${userId}`);
    return response.data.user;
  }
  
  async list(limit: number = 50, offset: number = 0): Promise<User[]> {
    const response = await this.client.get('/api/admin/users/search', {
      params: { limit, offset }
    });
    return response.data.users;
  }
}

class QuestionResource {
  constructor(private client: AxiosInstance) {}
  
  async getBank(
    sector: string,
    specialty: string,
    band: string,
    bankNumber: number
  ): Promise<any> {
    const response = await this.client.get(
      `/api/questions/${sector}/${specialty}/${band}/${bankNumber}`
    );
    return response.data;
  }
}

class AnalyticsResource {
  constructor(private client: AxiosInstance) {}
  
  async getUserAnalytics(
    userId: string,
    dateFrom?: Date,
    dateTo?: Date
  ): Promise<Analytics> {
    const params: any = {};
    if (dateFrom) params.date_from = dateFrom.toISOString();
    if (dateTo) params.date_to = dateTo.toISOString();
    
    const response = await this.client.get(`/api/analytics/user/${userId}`, { params });
    return response.data.analytics;
  }
}

// Export everything
export default NursingAIClient;

