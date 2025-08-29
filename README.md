# 🍽️ Cal-Track Mobile App
A powerful, intelligent, and intuitive **Calorie & Nutrition Tracker** built with **Python**, **TypeScript**, **JavaScript**, and **PWA Technology**.  
This app helps you analyze Indian meals using AI to provide comprehensive nutritional information, making it an essential tool for health-conscious individuals.

<div align="center">
  <img src="https://skillicons.dev/icons?i=python,typescript,javascript,html,css,react,nodejs,git" alt="Tech Stack" />
</div>

---

##  Try it out
### 🔗 [Cal-Track PWA (Live App)](https://github.com/Prajwal-koundinya/Cal-track-mobile-app)

---

## 🗂️ Project Structure
```
Cal-track-mobile-app/
├── backend/
│   ├── models/              # AI/ML models for food recognition
│   ├── utils/               # Utility functions & helpers
│   ├── api/                 # API endpoints and routes
│   ├── app.py              # Main Flask/FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── services/        # API services and utilities
│   │   ├── types/           # TypeScript type definitions
│   │   ├── pages/           # Application pages/screens
│   │   ├── hooks/           # Custom React hooks
│   │   └── utils/           # Frontend utilities
│   ├── public/
│   │   ├── manifest.json    # PWA manifest file
│   │   └── sw.js           # Service worker for offline functionality
│   ├── package.json         # Frontend dependencies
│   └── vite.config.js      # Vite configuration
├── tests/
│   ├── backend_test.py     # Backend API tests
│   └── test_result.md      # Test results documentation
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md              # Project documentation
```

## ✨ Features
✅ **AI-Powered Food Recognition** - Advanced computer vision for Indian cuisine  
✅ **Instant Nutritional Analysis** - Calories, proteins, carbs, fats, and fiber breakdown  
✅ **Progressive Web App** - Works offline, installable, cross-platform  
✅ **Portion Estimation** - AI-driven meal quantity approximation  
✅ **Daily Target Tracking** - Personalized protein and calorie goals  
✅ **Indian Cuisine Specialized** - Optimized for traditional Indian meals  
✅ **Photo-to-Report** - Simply snap and get detailed nutrition insights

---

## 📸 Screenshots
| AI Food Analysis | Home Screen | Nutrition Report |
|------------------|-------------|------------------|
| ![Analysis](generated_image:24) | ![Home](generated_image:25) | ![Report](image:22) |

---

## 🚀 Getting Started

### 🔧 Installation

Clone the repository:
```bash
git clone https://github.com/Prajwal-koundinya/Cal-track-mobile-app.git
cd Cal-track-mobile-app
```

### Backend Setup
Navigate to backend directory and install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup  
Navigate to frontend directory and install Node.js dependencies:
```bash
cd frontend
npm install
# or
yarn install
```

### ⚙️ Setup Environment Variables
```bash
cp .env.example .env
# Add your API keys and configuration
```

### Run the Application

Start the backend server:
```bash
cd backend
python app.py
```

Start the frontend development server:
```bash
cd frontend
npm run dev
# or
yarn dev
```

```
The app will be running at:
👉 Backend: http://localhost:5000
👉 Frontend: http://localhost:3000
```

### 🛠️ Build for Production
```bash
cd frontend
npm run build
# or
yarn build
```

## 🚀 Project Overview

### ⚙️ Technologies Used
| **Technology**   | **Logo** | **Purpose** |
| ---------------- | -------- | ----------- |
| **Python** | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) | Backend AI/ML processing |
| **TypeScript** | ![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white) | Type-safe frontend development |
| **JavaScript** | ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) | Dynamic web functionality |
| **React** | ![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB) | UI component library |
| **PWA** | ![PWA](https://img.shields.io/badge/PWA-5A0FC8?style=for-the-badge&logo=pwa&logoColor=white) | Progressive web app features |
| **Flask/FastAPI** | ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) | Python web framework |
| **HTML5** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) | Markup language |
| **CSS3** | ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) | Styling and animations |
| **Git** | ![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white) | Version control |

---

### 🧩 Scripts
| **Command** | **Description** |
| ----------- | --------------- |
| `npm run dev` | Start frontend development server |
| `npm run build` | Build frontend for production |
| `npm run preview` | Preview production build |
| `python app.py` | Start backend server |
| `pytest` | Run backend tests |
| `npm run lint` | Run ESLint checks |

---

### 📝 Folder Highlights
| **Folder** | **Purpose** |
| ---------- | ----------- |
| `backend/models/` | AI/ML models for food recognition |
| `backend/utils/` | Backend utility functions |
| `frontend/components/` | Reusable React UI components |
| `frontend/services/` | API communication services |
| `frontend/types/` | TypeScript type definitions |
| `tests/` | Comprehensive test suites |

---

## 🔬 How It Works

1. **📸 Capture**: Take a photo of your Indian meal using the PWA camera interface
2. **🤖 AI Processing**: Advanced computer vision analyzes the image for food identification
3. **📊 Analysis**: ML algorithms estimate portions and calculate nutritional content
4. **📈 Report**: Get detailed breakdown of calories, proteins, carbs, fats, and fiber
5. **🎯 Track**: Monitor daily nutrition goals and protein requirements

---

## 🚀 AI Technology Features

### 🧠 Machine Learning Capabilities
- **Computer Vision Models** trained on Indian cuisine datasets
- **Portion Estimation Algorithms** for accurate quantity analysis  
- **Nutritional Database** with 1000+ Indian food profiles
- **Real-time Processing** for instant results

### 📱 Progressive Web App Benefits
- **Offline Functionality** - Works without internet after initial load
- **Cross-Platform** - Runs on iOS, Android, and desktop browsers
- **App-like Experience** - Native feel with push notifications
- **Instant Updates** - No app store downloads required
- **Responsive Design** - Optimized for all screen sizes

---

## 🌟 Key Features in Detail

### Indian Cuisine Specialization
✅ Recognizes traditional dishes (dal, roti, sabzi, rice dishes)  
✅ Handles regional variations and cooking styles  
✅ Supports mixed meals and complex preparations  
✅ Database includes street food and restaurant meals

### Comprehensive Nutrition Analysis
✅ **Calorie Counting** - Accurate caloric content calculation  
✅ **Protein Analysis** - Essential for fitness goals  
✅ **Carbohydrate Breakdown** - Simple and complex carbs  
✅ **Fat Content** - Saturated and unsaturated analysis  
✅ **Fiber Measurement** - Dietary fiber for digestive health  
✅ **Portion Estimation** - AI-driven quantity approximation

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add: AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow TypeScript/JavaScript best practices
- Write comprehensive tests for new features
- Ensure PWA compliance and accessibility
- Document API endpoints and components

---

## 📈 Roadmap & Future Features

### 🚧 Coming Soon
- [ ] **Multi-language Support** (Hindi, Tamil, Bengali)
- [ ] **Barcode Scanning** for packaged foods
- [ ] **Meal Planning** with AI recommendations
- [ ] **Social Features** for sharing meals and progress
- [ ] **Fitness Tracker Integration** (Apple Health, Google Fit)
- [ ] **Restaurant Menu Integration** for dining out
- [ ] **Voice Commands** for hands-free operation

### 🎯 Long-term Vision
- [ ] **Global Cuisine Support** expansion beyond Indian food
- [ ] **Personalized AI Nutritionist** with health recommendations
- [ ] **Integration with Healthcare Providers** for medical tracking
- [ ] **Advanced Analytics** with trend analysis and insights

---

## 🤝 **Acknowledgments**

Special thanks to the nutrition and AI communities for their invaluable resources and datasets.  
Inspired by the need to make nutrition tracking accessible for Indian cuisine lovers worldwide.

**Tech Stack Inspiration**: Modern web development practices with PWA capabilities  
**AI Models**: Built upon state-of-the-art computer vision research

---

## 👨‍💻 Author

**Prajwal Koundinya**
- 🌐 GitHub: [@Prajwal-koundinya](https://github.com/Prajwal-koundinya)
- 💼 LinkedIn: [Connect with me]
- 📧 Email: [Your Email]
- 🌟 Portfolio: [Your Portfolio Website]

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support & Issues

If you encounter any issues or have questions:

1. 🐛 **Bug Reports**: [Create an Issue](https://github.com/Prajwal-koundinya/Cal-track-mobile-app/issues)
2. 💡 **Feature Requests**: [Start a Discussion](https://github.com/Prajwal-koundinya/Cal-track-mobile-app/discussions)
3. 📧 **Direct Contact**: [Email for urgent matters]

---

<div align="center">

### 🔥 *Made with ❤️ for Health-Conscious Developers and Food Enthusiasts*

**Transform Your Nutrition Journey with AI-Powered Indian Meal Analysis** 🥘

[![Stars](https://img.shields.io/github/stars/Prajwal-koundinya/Cal-track-mobile-app?style=social)](https://github.com/Prajwal-koundinya/Cal-track-mobile-app)
[![Forks](https://img.shields.io/github/forks/Prajwal-koundinya/Cal-track-mobile-app?style=social)](https://github.com/Prajwal-koundinya/Cal-track-mobile-app/fork)
[![Issues](https://img.shields.io/github/issues/Prajwal-koundinya/Cal-track-mobile-app)](https://github.com/Prajwal-koundinya/Cal-track-mobile-app/issues)

*If you find this project helpful, don't forget to ⭐ it on GitHub!*

</div>
