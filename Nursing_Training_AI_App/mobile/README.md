# 📱 Nursing Training AI - Mobile App

Complete mobile application for UK healthcare professional training with AI-powered question generation and personalized learning paths.

## ✨ Features

### 🎯 Core Functionality
- **Multi-Sector Support**: NHS, Private Healthcare, Care Homes, Community, Primary Care
- **All NHS Bands**: Band 2 through Band 8d (8a, 8b, 8c, 8d)
- **9 NHS Specialties**: AMU, Emergency, ICU, Maternity, Mental Health, Pediatrics, Cardiology, Neurology, Oncology
- **2,140+ Question Banks**: Over 42,000 questions total

### 📚 Question Types
- **Multiple Choice**: Test clinical knowledge
- **Scenarios**: Real-world clinical situations  
- **Calculations**: Drug dosages, vital signs
- **Case Studies**: Complex patient management
- **Leadership**: Team management scenarios
- **Governance**: Quality improvement and audit

### 🎤 Audio Features
- **Text-to-Speech**: Questions read aloud in British English
- **Speech-to-Text**: Voice answers for scenario questions
- **Adjustable Speed**: Normal, slow, fast, clear modes
- **Voice Selection**: Multiple British English voices

### 📴 Offline Mode
- Download question banks for offline practice
- Automatic sync when back online
- Progress saved locally
- Essential content caching

### 🔔 Smart Notifications
- Daily training reminders
- Streak notifications
- Achievement alerts
- Weekly progress reports
- Customizable timing

### 🎨 Modern UI/UX
- **Dark Mode**: System-aware or manual toggle
- **Smooth Animations**: Using react-native-animatable
- **NHS Themed**: Professional blue color scheme
- **Responsive Design**: Works on all screen sizes
- **Accessibility**: Screen reader support

### 📊 Progress Tracking
- Real-time performance stats
- Accuracy tracking by competency
- Streak counter
- Band progression monitoring
- Personalized recommendations

## 🛠 Technical Stack

### Framework
- **React Native** 0.72.6
- **Expo** ~49.0.15
- **TypeScript** 5.1.3

### Navigation
- **@react-navigation/native** 6.1.9
- **@react-navigation/stack** 6.3.20
- **@react-navigation/bottom-tabs** 6.5.11

### State Management
- **Context API**: Global app state
- **Secure Store**: Encrypted user data
- **AsyncStorage**: Offline data persistence

### Audio
- **expo-speech**: Text-to-Speech
- **react-native-voice**: Speech-to-Text
- **expo-av**: Audio playback

### Notifications
- **expo-notifications**: Push notifications
- **expo-device**: Device information

### Other Libraries
- **axios**: API communication
- **react-query**: Data fetching and caching
- **react-hook-form**: Form management
- **zod**: Schema validation
- **react-native-animatable**: Animations
- **react-native-paper**: UI components

## 📁 Project Structure

```
mobile/
├── App.tsx                      # Main app entry with navigation
├── package.json                 # Dependencies
├── app.json                     # Expo configuration
│
├── screens/                     # All app screens
│   ├── LoginScreen.tsx          # Authentication
│   ├── RegisterScreen.tsx       # User registration
│   ├── DashboardScreen.tsx      # Main dashboard
│   ├── SpecialtiesScreen.tsx    # Specialty selection
│   ├── QuestionsScreen.tsx      # Question interface
│   ├── ResultsScreen.tsx        # Performance results
│   └── ProfileScreen.tsx        # User profile & settings
│
├── context/                     # State management
│   ├── AppContext.tsx           # Global app state
│   └── ThemeContext.tsx         # Dark mode theme
│
├── services/                    # Business logic
│   ├── AudioService.ts          # Speech features
│   ├── OfflineService.ts        # Offline functionality
│   └── NotificationService.ts   # Push notifications
│
├── components/                  # Reusable components
├── utils/                       # Utility functions
└── assets/                      # Images, fonts, icons
```

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ installed
- Expo CLI installed (`npm install -g expo-cli`)
- iOS Simulator (Mac) or Android Emulator
- Physical device for testing (recommended)

### Installation

```bash
cd Nursing_Training_AI_App/mobile
npm install
```

### Running the App

```bash
# Start Expo development server
npm start

# Run on iOS
npm run ios

# Run on Android
npm run android

# Run on web
npm run web
```

### Building for Production

```bash
# Build for Android
npm run build:android

# Build for iOS  
npm run build:ios
```

## 📝 Configuration

### API Endpoint
Update API URL in services:
- `services/AudioService.ts`
- `services/OfflineService.ts`
- `context/AppContext.tsx`

### Expo Project ID
Update in:
- `app.json` → `extra.eas.projectId`
- `services/NotificationService.ts`

## 🎯 User Flow

1. **Login/Register** → Choose sector, band, specialty
2. **Dashboard** → View progress, stats, recommendations
3. **Select Specialty** → Choose from available specialties
4. **Answer Questions** → Multi-type questions with audio support
5. **View Results** → Performance feedback and recommendations
6. **Profile** → Manage settings, view achievements

## 🔐 Security

- User credentials stored in Expo SecureStore (encrypted)
- JWT tokens for API authentication
- Secure offline data storage
- No sensitive data in AsyncStorage

## 🌐 Supported Platforms

- ✅ iOS 13+
- ✅ Android 6.0+
- ✅ Web (Progressive Web App)

## 📊 Performance

- Optimized bundle size
- Lazy loading for screens
- Image optimization
- Efficient caching strategy
- Minimal re-renders with Context API

## 🎓 Target Users

### NHS
- Healthcare Assistants (Band 2-3)
- Staff Nurses (Band 4-5)
- Senior Nurses (Band 6)
- Advanced Practitioners (Band 7)
- Managers & Directors (Band 8a-8d)

### Private Healthcare
- Theatre Nurses
- Recovery Nurses
- Ward Nurses
- Endoscopy Nurses
- Cosmetic Practitioners

### Care Homes
- Care Assistants
- Senior Care Assistants
- Care Home Nurses
- Deputy Managers
- Care Home Managers

### Community
- District Nurses
- Health Visitors
- Community Mental Health Nurses
- School Nurses
- Community Matrons

### Primary Care
- Practice Nurses
- Advanced Nurse Practitioners
- Healthcare Assistants
- Chronic Disease Specialists

## 📈 Future Enhancements

- [ ] Camera integration for document scanning
- [ ] Peer-to-peer study groups
- [ ] Leaderboards and competitions
- [ ] Video tutorials
- [ ] AR/VR clinical scenarios
- [ ] Integration with e-portfolio systems
- [ ] Multi-language support

## 🐛 Known Issues

- Voice recognition requires physical device
- Some features require internet connection
- iOS voice quality better than Android

## 📞 Support

For support, email: support@nursingtrainingai.com

## 📄 License

Proprietary - All rights reserved

---

Built with ❤️ for UK Healthcare Professionals

