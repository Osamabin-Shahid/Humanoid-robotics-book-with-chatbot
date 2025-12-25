# Quickstart Guide: Docusaurus Book Cleanup & Neural-Themed UI

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn package manager
- Git
- Basic knowledge of React and CSS

## Setup

1. **Clone the repository** (if starting fresh):
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm start
   ```
   This will start the development server at `http://localhost:3000`

## Project Structure

```
humanoid-robotics-ai-book/
├── docs/                 # Book content
│   ├── module-1/
│   ├── module-2/
│   ├── module-3/
│   └── module-4/
├── src/
│   ├── components/       # Custom React components
│   ├── pages/            # Custom pages (homepage)
│   └── css/              # Custom CSS
├── static/               # Static assets
├── docusaurus.config.js  # Docusaurus configuration
└── sidebars.js           # Navigation configuration
```

## Key Files to Modify

### 1. Homepage
- **File**: `src/pages/index.js`
- **Purpose**: Custom neural-themed homepage with cards

### 2. Styles
- **File**: `src/css/custom.css`
- **Purpose**: Custom styling for neural theme

### 3. Navigation
- **File**: `sidebars.js`
- **Purpose**: Book-only navigation structure

### 4. Configuration
- **File**: `docusaurus.config.js`
- **Purpose**: Site configuration and theme settings

## Development Workflow

1. **Audit current structure**:
   ```bash
   # Check current navigation
   cat sidebars.js

   # Check current config
   cat docusaurus.config.js
   ```

2. **Clean up default content**:
   - Remove blog directory
   - Remove tutorial content
   - Update sidebar configuration

3. **Create custom homepage**:
   ```bash
   mkdir -p src/pages
   # Create custom homepage with neural theme
   ```

4. **Add custom styles**:
   ```bash
   mkdir -p src/css
   # Add neural-themed CSS
   ```

5. **Test changes**:
   ```bash
   npm start
   ```

6. **Build and verify**:
   ```bash
   npm run build
   npm run serve
   ```

## Custom Components

### Homepage Cards
Create reusable card components for the homepage:

```jsx
// src/components/Card/index.js
import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import './styles.module.css';

export default function Card({title, description, to, icon}) {
  return (
    <Link className="card-link" to={to}>
      <div className="card">
        <div className="card-icon">{icon}</div>
        <h3 className="card-title">{title}</h3>
        <p className="card-description">{description}</p>
      </div>
    </Link>
  );
}
```

### Neural Background
Create a neural network background component:

```jsx
// src/components/NeuralBackground/index.js
import React from 'react';
import './styles.module.css';

export default function NeuralBackground() {
  return (
    <div className="neural-background">
      <div className="neural-node"></div>
      <div className="neural-node"></div>
      <div className="neural-node"></div>
      {/* More nodes as needed */}
    </div>
  );
}
```

## Testing Checklist

- [ ] Homepage displays neural-themed design
- [ ] All default tutorial content removed
- [ ] Blog features disabled
- [ ] Navigation shows only book content
- [ ] Cards link to appropriate sections
- [ ] Hover animations work correctly
- [ ] Site is responsive on mobile
- [ ] All links work correctly
- [ ] Build process completes without errors

## Deployment

1. **Build for production**:
   ```bash
   npm run build
   ```

2. **Serve locally to test**:
   ```bash
   npm run serve
   ```

3. **Deploy** to GitHub Pages or your preferred static hosting service

## Troubleshooting

### Common Issues:

1. **Homepage not loading custom component**:
   - Ensure `src/pages/index.js` exists and is properly formatted
   - Check Docusaurus config for any conflicting settings

2. **CSS not applying**:
   - Verify custom CSS is imported in the right place
   - Check for CSS conflicts with default Docusaurus styles

3. **Navigation not updating**:
   - Verify `sidebars.js` is properly configured
   - Check for cached navigation in development server

4. **Build errors**:
   - Run `npm run clear` to clear Docusaurus cache
   - Check for syntax errors in modified files