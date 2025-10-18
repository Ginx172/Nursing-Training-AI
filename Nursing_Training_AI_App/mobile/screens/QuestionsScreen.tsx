import React, { useState, useEffect } from 'react';
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

interface QuestionsScreenProps {
  navigation: any;
  route: any;
}

export default function QuestionsScreen({ navigation, route }: QuestionsScreenProps) {
  const { sector, specialty, band } = route.params || {};
  
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [isAudioEnabled, setIsAudioEnabled] = useState(false);

  // Mock questions - TODO: Load from backend
  const questions = [
    {
      id: 1,
      type: 'multiple_choice',
      question: 'A patient presents with acute shortness of breath. What is your FIRST priority?',
      options: [
        'A) Take full medical history',
        'B) Assess airway, breathing, circulation (ABC)',
        'C) Order chest X-ray',
        'D) Call consultant'
      ],
      correctAnswer: 'B',
      explanation: 'ABC assessment is always the priority in acute presentations. This ensures immediate life-threatening issues are identified and managed first.',
      competencies: ['Assessment', 'Patient safety', 'Emergency care'],
      difficulty: 'intermediate'
    },
    {
      id: 2,
      type: 'scenario',
      question: 'Describe your approach to managing a patient with suspected sepsis.',
      expectedPoints: [
        'Recognize signs of sepsis using NEWS2 score',
        'Initiate sepsis six bundle within 1 hour',
        'Obtain blood cultures before antibiotics',
        'Administer broad-spectrum antibiotics',
        'Give IV fluids as prescribed',
        'Monitor vital signs closely',
        'Escalate to senior clinician'
      ],
      competencies: ['Clinical assessment', 'Emergency response', 'Protocol adherence'],
      difficulty: 'intermediate'
    },
    {
      id: 3,
      type: 'calculation',
      question: 'Calculate the required dose: Patient weighs 75kg. Prescribed 15mg/kg of medication. Stock solution is 250mg/5ml. How many ml do you administer?',
      calculation: {
        required_dose: '75kg × 15mg/kg = 1125mg',
        volume: '(1125mg ÷ 250mg) × 5ml = 22.5ml'
      },
      correctAnswer: '22.5ml',
      tolerance: 0.5,
      competencies: ['Drug calculations', 'Safe practice', 'Accuracy'],
      difficulty: 'intermediate'
    }
  ];

  const currentQuestion = questions[currentQuestionIndex];

  useEffect(() => {
    // Timer for question
    const interval = setInterval(() => {
      setTimeElapsed((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [currentQuestionIndex]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerSelect = (answer: string) => {
    if (!isAnswered) {
      setSelectedAnswer(answer);
    }
  };

  const handleSubmitAnswer = () => {
    if (!selectedAnswer) {
      Alert.alert('No Answer Selected', 'Please select an answer before submitting');
      return;
    }

    setIsAnswered(true);
    
    // Check if answer is correct (for multiple choice)
    if (currentQuestion.type === 'multiple_choice') {
      const isCorrect = selectedAnswer.startsWith(currentQuestion.correctAnswer);
      if (isCorrect) {
        setScore({ ...score, correct: score.correct + 1, total: score.total + 1 });
      } else {
        setScore({ ...score, total: score.total + 1 });
      }
    }
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setSelectedAnswer(null);
      setIsAnswered(false);
      setTimeElapsed(0);
    } else {
      // Navigate to Results screen
      navigation.navigate('Results', {
        score: score,
        sector: sector,
        specialty: specialty,
        band: band
      });
    }
  };

  const renderMultipleChoiceQuestion = () => (
    <View style={styles.optionsContainer}>
      {currentQuestion.options?.map((option, index) => {
        const optionLetter = option.charAt(0);
        const isSelected = selectedAnswer === option;
        const isCorrect = optionLetter === currentQuestion.correctAnswer;
        
        let cardStyle = styles.optionCard;
        if (isAnswered) {
          if (isCorrect) {
            cardStyle = styles.optionCardCorrect;
          } else if (isSelected && !isCorrect) {
            cardStyle = styles.optionCardWrong;
          }
        } else if (isSelected) {
          cardStyle = styles.optionCardSelected;
        }

        return (
          <Animatable.View
            key={index}
            animation="fadeInRight"
            delay={index * 100}
          >
            <TouchableOpacity
              style={cardStyle}
              onPress={() => handleAnswerSelect(option)}
              disabled={isAnswered}
            >
              <Text style={styles.optionText}>{option}</Text>
              {isAnswered && isCorrect && (
                <Text style={styles.checkmark}>✓</Text>
              )}
              {isAnswered && isSelected && !isCorrect && (
                <Text style={styles.crossmark}>✗</Text>
              )}
            </TouchableOpacity>
          </Animatable.View>
        );
      })}
    </View>
  );

  const renderScenarioQuestion = () => (
    <View style={styles.scenarioContainer}>
      <Text style={styles.scenarioInstructions}>
        This is a scenario-based question. List the key points you would consider:
      </Text>
      <View style={styles.expectedPointsContainer}>
        <Text style={styles.expectedPointsTitle}>Expected Points:</Text>
        {currentQuestion.expectedPoints?.map((point, index) => (
          <View key={index} style={styles.expectedPoint}>
            <Text style={styles.bulletPoint}>•</Text>
            <Text style={styles.expectedPointText}>{point}</Text>
          </View>
        ))}
      </View>
      <TouchableOpacity style={styles.recordButton}>
        <Text style={styles.recordIcon}>🎤</Text>
        <Text style={styles.recordText}>Record Your Answer</Text>
      </TouchableOpacity>
    </View>
  );

  const renderCalculationQuestion = () => (
    <View style={styles.calculationContainer}>
      <View style={styles.calculationSteps}>
        <Text style={styles.calculationTitle}>Show your working:</Text>
        {Object.entries(currentQuestion.calculation || {}).map(([key, value], index) => (
          <View key={index} style={styles.calculationStep}>
            <Text style={styles.calculationLabel}>{key.replace('_', ' ')}:</Text>
            <Text style={styles.calculationValue}>{value}</Text>
          </View>
        ))}
      </View>
      <TouchableOpacity style={styles.answerInputButton}>
        <Text style={styles.answerInputText}>Enter Your Answer</Text>
      </TouchableOpacity>
    </View>
  );

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
        <View style={styles.headerInfo}>
          <Text style={styles.headerTitle}>
            {specialty?.toUpperCase()} - {band?.replace('_', ' ').toUpperCase()}
          </Text>
          <Text style={styles.headerSubtitle}>
            Question {currentQuestionIndex + 1} of {questions.length}
          </Text>
        </View>
        <TouchableOpacity 
          style={styles.audioButton}
          onPress={() => setIsAudioEnabled(!isAudioEnabled)}
        >
          <Text style={styles.audioIcon}>{isAudioEnabled ? '🔊' : '🔇'}</Text>
        </TouchableOpacity>
      </View>

      {/* Progress Bar */}
      <View style={styles.progressContainer}>
        <View 
          style={[
            styles.progressBar, 
            { width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }
          ]} 
        />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Question Card */}
        <Animatable.View animation="fadeInUp" style={styles.questionCard}>
          <View style={styles.questionHeader}>
            <View style={styles.questionTypeBadge}>
              <Text style={styles.questionTypeText}>
                {currentQuestion.type.replace('_', ' ').toUpperCase()}
              </Text>
            </View>
            <View style={styles.timerContainer}>
              <Text style={styles.timerIcon}>⏱️</Text>
              <Text style={styles.timerText}>{formatTime(timeElapsed)}</Text>
            </View>
          </View>

          <Text style={styles.questionText}>{currentQuestion.question}</Text>

          {/* Competencies */}
          <View style={styles.competenciesContainer}>
            {currentQuestion.competencies.map((comp, index) => (
              <View key={index} style={styles.competencyTag}>
                <Text style={styles.competencyText}>{comp}</Text>
              </View>
            ))}
          </View>
        </Animatable.View>

        {/* Render question type specific content */}
        {currentQuestion.type === 'multiple_choice' && renderMultipleChoiceQuestion()}
        {currentQuestion.type === 'scenario' && renderScenarioQuestion()}
        {currentQuestion.type === 'calculation' && renderCalculationQuestion()}

        {/* Explanation (shown after answer) */}
        {isAnswered && currentQuestion.explanation && (
          <Animatable.View animation="fadeIn" style={styles.explanationCard}>
            <Text style={styles.explanationTitle}>Explanation</Text>
            <Text style={styles.explanationText}>{currentQuestion.explanation}</Text>
          </Animatable.View>
        )}

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          {!isAnswered && currentQuestion.type === 'multiple_choice' && (
            <TouchableOpacity 
              style={styles.submitButton}
              onPress={handleSubmitAnswer}
            >
              <Text style={styles.submitButtonText}>Submit Answer</Text>
            </TouchableOpacity>
          )}
          
          {isAnswered && (
            <TouchableOpacity 
              style={styles.nextButton}
              onPress={handleNextQuestion}
            >
              <Text style={styles.nextButtonText}>
                {currentQuestionIndex < questions.length - 1 ? 'Next Question' : 'View Results'}
              </Text>
            </TouchableOpacity>
          )}
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
    paddingBottom: 16,
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
  headerInfo: {
    flex: 1,
    marginHorizontal: 12,
  },
  headerTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: 'white',
  },
  headerSubtitle: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.8)',
    marginTop: 2,
  },
  audioButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  audioIcon: {
    fontSize: 20,
  },
  progressContainer: {
    height: 4,
    backgroundColor: '#e0e0e0',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#00A651',
  },
  content: {
    flex: 1,
  },
  questionCard: {
    margin: 16,
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  questionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  questionTypeBadge: {
    backgroundColor: '#e6f2ff',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  questionTypeText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#0066CC',
  },
  timerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f9f9f9',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  timerIcon: {
    fontSize: 14,
    marginRight: 4,
  },
  timerText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
  },
  questionText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#1a1a1a',
    marginBottom: 16,
  },
  competenciesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  competencyTag: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  competencyText: {
    fontSize: 10,
    color: '#666',
    fontWeight: '600',
  },
  optionsContainer: {
    paddingHorizontal: 16,
    gap: 12,
  },
  optionCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    borderWidth: 2,
    borderColor: '#e0e0e0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  optionCardSelected: {
    borderColor: '#0066CC',
    backgroundColor: '#e6f2ff',
  },
  optionCardCorrect: {
    borderColor: '#00A651',
    backgroundColor: '#e8f5e9',
  },
  optionCardWrong: {
    borderColor: '#E74C3C',
    backgroundColor: '#ffebee',
  },
  optionText: {
    fontSize: 14,
    color: '#1a1a1a',
    lineHeight: 20,
  },
  checkmark: {
    position: 'absolute',
    top: 16,
    right: 16,
    fontSize: 24,
    color: '#00A651',
  },
  crossmark: {
    position: 'absolute',
    top: 16,
    right: 16,
    fontSize: 24,
    color: '#E74C3C',
  },
  scenarioContainer: {
    paddingHorizontal: 16,
  },
  scenarioInstructions: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
    fontStyle: 'italic',
  },
  expectedPointsContainer: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  expectedPointsTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#0066CC',
    marginBottom: 12,
  },
  expectedPoint: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  bulletPoint: {
    fontSize: 14,
    color: '#0066CC',
    marginRight: 8,
    fontWeight: 'bold',
  },
  expectedPointText: {
    flex: 1,
    fontSize: 13,
    color: '#333',
    lineHeight: 20,
  },
  recordButton: {
    flexDirection: 'row',
    backgroundColor: '#E74C3C',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  recordIcon: {
    fontSize: 24,
    marginRight: 8,
  },
  recordText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  calculationContainer: {
    paddingHorizontal: 16,
  },
  calculationSteps: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  calculationTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#0066CC',
    marginBottom: 12,
  },
  calculationStep: {
    marginBottom: 12,
  },
  calculationLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  calculationValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1a1a1a',
  },
  answerInputButton: {
    backgroundColor: '#0066CC',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  answerInputText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  explanationCard: {
    margin: 16,
    backgroundColor: '#e8f5e9',
    borderRadius: 12,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#00A651',
  },
  explanationTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#00A651',
    marginBottom: 8,
  },
  explanationText: {
    fontSize: 13,
    color: '#333',
    lineHeight: 20,
  },
  actionButtons: {
    paddingHorizontal: 16,
    marginTop: 16,
  },
  submitButton: {
    backgroundColor: '#0066CC',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#0066CC',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 5,
  },
  submitButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  nextButton: {
    backgroundColor: '#00A651',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#00A651',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 5,
  },
  nextButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  bottomPadding: {
    height: 40,
  },
});

