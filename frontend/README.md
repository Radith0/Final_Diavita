# Diabetes Detection AI - Frontend

Beautiful, medical-inspired React frontend for multimodal diabetes detection and prevention.

## Design Philosophy

### Aesthetic Choices

**Typography:**
- **Display**: Space Grotesk - Modern, distinctive, geometric sans-serif
- **Body**: Crimson Pro - Elegant serif for readability and warmth
- **Mono**: IBM Plex Mono - Technical precision for data display

**Color Palette:** Medical Blue-Green (inspired by surgical scrubs and diagnostic imaging)
- **Primary Deep**: #0A3D62 (Trust, medical authority)
- **Primary Main**: #1B6B93 (Medical blue)
- **Accent Warm**: #E85D75 (Vitality, blood flow imagery)
- **Accent Success**: #2ECC71 (Health, improvement)

**Visual Elements:**
- Diagnostic grid patterns (medical chart aesthetic)
- Scan line animations (retinal imaging simulation)
- Glass morphism for depth
- ECG-inspired progress indicators
- Circular risk visualization (medical monitor style)

## Features

✨ **Staggered Page Load Animations** - Orchestrated reveals using Framer Motion
🎨 **Medical-Inspired UI** - Unique aesthetic avoiding generic AI patterns
📊 **Interactive Risk Visualization** - Circular progress with ECG styling
🔬 **What-If Simulations** - Clinical projection displays
📱 **Responsive Design** - Works on all devices
♿ **Accessible** - WCAG compliant with focus management
🔄 **Multimodal Fusion** - Optimized weighted combination of retinal and lifestyle predictions
🧠 **LLM-Powered Advice** - Personalized recommendations using Groq AI

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **Framer Motion** - Animation library
- **React Router** - Navigation
- **Lucide Icons** - Icon library
- **Axios** - HTTP client

## Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Configure API Endpoint

Create `.env` file:
```
VITE_API_URL=http://localhost:5000/api
```

### Run Development Server

```bash
npm run dev
```

Frontend runs on: **http://localhost:3000**

### Build for Production

```bash
npm run build
```

Output in `dist/` folder

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── assets/             # Images, fonts
│   ├── components/         # Reusable components
│   ├── pages/              # Page components
│   │   ├── HomePage.jsx    # Landing page
│   │   ├── AnalysisPage.jsx # Upload & data entry
│   │   ├── ResultsPage.jsx # Risk results
│   │   └── SimulationPage.jsx # What-if scenarios
│   ├── services/           # API service
│   │   └── api.js          # Backend integration
│   ├── styles/             # Global styles
│   │   └── globals.css     # Design system
│   ├── App.jsx             # Root component
│   └── main.jsx            # Entry point
├── index.html
├── vite.config.js
└── package.json
```

## Pages

### 1. Home Page
- Hero with atmospheric background
- Feature cards with hover effects
- Medical grid patterns
- Staggered animations on load

### 2. Analysis Page
- 3-step wizard (Image → Lifestyle → Review)
- Drag-and-drop image upload
- Form with medical UI styling
- Progress indicator

### 3. Results Page
- Circular risk score display (ECG-style)
- Component breakdowns (retinal + lifestyle with optimized fusion weights)
- Detailed findings cards
- LLM-generated recommendations
- Fusion weights displayed: Retinal (10.3%) + Lifestyle (89.7%)

### 4. Simulation Page
- What-if scenario cards
- Risk reduction visualizations
- Action plan checklists
- Recommended intervention pathway

## Design System

### CSS Variables (see globals.css)

```css
--primary-deep: #0A3D62
--primary-main: #1B6B93
--accent-warm: #E85D75
--accent-success: #2ECC71

--font-display: 'Space Grotesk'
--font-body: 'Crimson Pro'
--font-mono: 'IBM Plex Mono'

--shadow-md: 0 4px 16px rgba(10, 61, 98, 0.12)
--transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1)
```

### Animation Patterns

- **Page Load**: Staggered fade-in-up (0.1s delays)
- **Hover States**: Lift effect (-4px to -8px)
- **Progress**: Smooth circular fills
- **Micro-interactions**: Subtle scale/color transitions

## API Integration

All API calls in `src/services/api.js`:

```javascript
import { analyzeComplete } from './services/api'

// Complete analysis
const result = await analyzeComplete(imageFile, lifestyleData)
```

## Customization

### Change Color Theme

Edit CSS variables in `src/styles/globals.css`:

```css
:root {
  --primary-main: #YOUR_COLOR;
  --accent-warm: #YOUR_ACCENT;
}
```

### Add New Page

1. Create page in `src/pages/YourPage.jsx`
2. Create styles in `src/pages/YourPage.css`
3. Add route in `src/App.jsx`

### Modify Animations

Edit Framer Motion configs:

```javascript
initial={{ opacity: 0, y: 40 }}
animate={{ opacity: 1, y: 0 }}
transition={{ duration: 0.8 }}
```

## Backend Integration

The frontend connects to a Flask backend that uses:
- **Optimized Multimodal Fusion**: Cross-validated weights (Retinal: 10.3%, Lifestyle: 89.7%)
- **CNN Model**: For diabetic retinopathy detection from retinal images
- **Gradient Boosting Model**: For lifestyle-based risk prediction
- **Groq LLM**: For personalized advice generation
- **Agentic Architecture**: Multiple AI agents working in coordination

## Performance

- Code splitting with React Router
- Lazy loading for images
- CSS-only animations where possible
- Framer Motion for complex orchestrations
- Backend response time: <2s for complete analysis

## Accessibility

- Semantic HTML
- ARIA labels on interactive elements
- Keyboard navigation support
- Focus management
- Screen reader friendly

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

This is a research project. For questions or improvements, contact the author.

## License

Research Project - Informatics Institute of Technology

---

**Author**: L.M. Radith Dinusitha
**Supervisor**: Mrs. Sulochana Rupasinghe
**Project**: Multimodal AI Framework for Early Diabetes Detection
