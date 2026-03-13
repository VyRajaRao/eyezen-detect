# eyezen-detect: AI-Powered Retinal Disease Detection

A full-stack web application for retinal fundus image analysis and disease detection using machine learning.

## 🏗️ Project Architecture

### Frontend
- **Framework**: React 18 + TypeScript + Vite
- **Styling**: TailwindCSS + Shadcn/UI Components
- **State Management**: TanStack Query
- **Routing**: React Router v6
- **Location**: `/frontend/`

### Backend
- **Framework**: FastAPI (Python)
- **ML/AI**: TensorFlow 2.13 + OpenCV
- **Database**: SQLite + SQLAlchemy ORM
- **Task**: 8-class retinal disease classification
- **Location**: `/backend/`

---

## 📁 Directory Structure

```
eyezen-detect/
│
├── frontend/                         # React + Vite frontend
│   ├── public/                       # Static assets
│   ├── src/
│   │   ├── components/              # Reusable React components
│   │   │   ├── AboutSection.tsx
│   │   │   ├── ChatBot.tsx
│   │   │   ├── DisclaimerSection.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── HeroSection.tsx
│   │   │   ├── ResultsSection.tsx
│   │   │   ├── UploadSection.tsx
│   │   │   └── ui/                 # Shadcn UI components (40+)
│   │   │
│   │   ├── pages/                   # Page components
│   │   │   ├── Index.tsx            # Main landing page
│   │   │   └── NotFound.tsx         # 404 page
│   │   │
│   │   ├── hooks/                   # Custom React hooks
│   │   │   ├── use-mobile.tsx
│   │   │   └── use-toast.ts
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts              # Backend API client
│   │   │   ├── imageValidator.ts   # Image validation logic
│   │   │   └── utils.ts            # Utility functions
│   │   │
│   │   ├── types/
│   │   │   └── index.ts            # TypeScript type definitions
│   │   │
│   │   ├── App.tsx                 # Root component
│   │   ├── App.css                 # Global styles
│   │   ├── index.css               # CSS reset + variables
│   │   ├── main.tsx                # Entry point
│   │   └── vite-env.d.ts           # Vite environment types
│   │
│   ├── index.html                   # HTML template
│   ├── package.json                 # Dependencies & scripts
│   ├── tsconfig.json                # TypeScript config
│   ├── tsconfig.app.json            # App-specific TS config
│   ├── tsconfig.node.json           # Node-specific TS config
│   ├── vite.config.ts              # Vite configuration
│   ├── tailwind.config.ts          # TailwindCSS config
│   ├── postcss.config.js           # PostCSS config
│   ├── eslint.config.js            # ESLint configuration
│   └── components.json             # Shadcn UI config
│
├── backend/                          # Python FastAPI backend
│   ├── app/                         # Main application package
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   │
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   └── database.py         # SQLAlchemy ORM setup
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── disease_classifier.py    # TensorFlow model wrapper
│   │   │   └── db_models.py            # ORM models
│   │   │
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── (future API endpoints)
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── inference.py        # Prediction logic
│   │   │   └── preprocessing.py    # Image preprocessing
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── preprocess.py       # Image preprocessing utilities
│   │       ├── metrics.py          # Model metrics
│   │       ├── train_utils.py      # Training utilities
│   │       └── kaggle_utils.py     # Kaggle dataset handling
│   │
│   ├── training/                    # Training scripts
│   │   ├── train_8class_model.py
│   │   └── train_improved.py
│   │
│   ├── datasets/                    # Raw training datasets (in .gitignore)
│   │   ├── original/
│   │   └── 8class/
│   │
│   ├── model_weights/              # Trained model files (in .gitignore)
│   │   ├── retina_disease_model.h5
│   │   ├── best_model.h5
│   │   ├── best_model_checkpoint.h5
│   │   ├── class_indices.json
│   │   └── training_report.json
│   │
│   ├── storage/
│   │   └── images/                 # Uploaded images from frontend
│   │
│   ├── requirements.txt             # Python dependencies
│   └── sql_app.db                  # SQLite database
│
├── .gitignore                       # Git ignore rules (comprehensive)
├── .env.example                     # Environment variables template
└── README.md                        # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ (for frontend)
- Python 3.8+ (for backend)
- Virtual environment (venv, conda, etc.)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev          # Development server on localhost:8081
npm run build        # Production build
```

**Frontend URLs:**
- Development: `http://localhost:8081`
- API Backend: `http://localhost:5000`

### Backend Setup

```bash
cd backend
python -m venv venv              # Create virtual environment
source venv/Scripts/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

**Backend URLs:**
- API: `http://localhost:5000`
- Health Check: `http://localhost:5000/health`
- Swagger Docs: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

---

## 📚 API Endpoints

### Health Check
```
GET /health
Response: { "status": "healthy", "version": "1.0.0", "models_ready": true }
```

### Disease Prediction
```
POST /predict
Body: { "file": <image_file> }
Response: { "disease": "...", "confidence": 0.95, "all_predictions": {...} }
```

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend:
```env
DATABASE_URL=sqlite:///./sql_app.db
MODEL_PATH=./model_weights/retina_disease_model.h5
API_PORT=5000
DEBUG=False
```

### TensorFlow Model
- **Classes**: Normal, Cataract, Glaucoma, AMD, Diabetes, Hypertension, Myopia, Other (8 classes)
- **Input**: Retinal fundus images (RGB, 224×224)
- **Output**: Disease classification + confidence score

---

## 📦 Dependencies

### Frontend
- React 18
- TypeScript
- Vite 5.4
- TailwindCSS
- Shadcn/UI (40+ components)
- React Router v6
- TanStack Query

### Backend
- FastAPI 0.104
- Uvicorn (ASGI server)
- TensorFlow 2.13
- OpenCV 4.8
- SQLAlchemy 2.0
- Pydantic 2.5

---

## 🎨 Design Features

- **Responsive UI**: Mobile-first design with TailwindCSS
- **Dark Mode Ready**: Shadcn/UI components support theme switching
- **Real-time Updates**: TanStack Query for automatic UI caching
- **Type Safety**: Full TypeScript coverage

---

## 📖 Development Workflow

### Running Both Servers

**Terminal 1 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 2 - Backend:**
```bash
cd backend
source venv/Scripts/activate
python -m uvicorn app.main:app --reload
```

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build        # Creates optimized build in frontend/dist/
```

**Backend:**
```bash
# Run with production ASGI server (Gunicorn)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

---

## 🐳 Docker Support (Optional)

```bash
docker-compose up --build
# Frontend: localhost:3000
# Backend: localhost:5000
```

---

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test
```

### Backend Tests
```bash
cd backend
pytest
```

---

## 📝 Project Status

- ✅ Frontend React app with Shadcn/UI
- ✅ Backend FastAPI with TensorFlow integration
- ✅ Image upload and validation
- ✅ Real-time disease prediction
- ✅ Database persistence (SQLite)
- ⏳ Advanced ML features (confidence thresholds, model versioning)
- ⏳ Comprehensive testing suite
- ⏳ Docker containerization

---

## 📜 License

This project is provided as-is for educational and research purposes.

---

## 📧 Support

For issues or questions, please refer to the documentation or create an issue in the repository.
