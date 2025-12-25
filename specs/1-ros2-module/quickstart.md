# Quickstart Guide: Module 1 — The Robotic Nervous System (ROS 2)

## Prerequisites
- Node.js 18+ installed
- Basic command line knowledge
- Git installed for version control

## Setup Docusaurus Project

1. **Install Docusaurus globally**:
   ```bash
   npm install -g @docusaurus/init
   ```

2. **Initialize a new Docusaurus project**:
   ```bash
   npx @docusaurus/init@latest init humanoid-robotics-ai-book classic
   cd humanoid-robotics-ai-book
   ```

3. **Install dependencies**:
   ```bash
   npm install
   ```

4. **Start the development server**:
   ```bash
   npm start
   ```

## Configure for Book Authoring

1. **Update docusaurus.config.js** to include your book settings:
   ```javascript
   // docusaurus.config.js
   module.exports = {
     title: 'Physical AI & Humanoid Robotics',
     tagline: 'A comprehensive guide to embodied AI systems',
     url: 'https://your-github-username.github.io',
     baseUrl: '/humanoid-robotics-ai-book/',
     organizationName: 'your-github-username',
     projectName: 'humanoid-robotics-ai-book',
     onBrokenLinks: 'throw',
     onBrokenMarkdownLinks: 'warn',
     // ... other configuration
   };
   ```

## Add Module 1 Content

1. **Create the module directory**:
   ```bash
   mkdir docs/module-1
   ```

2. **Add the three chapter files**:
   ```bash
   touch docs/module-1/chapter-1-ros2-foundations.md
   touch docs/module-1/chapter-2-ros2-middleware.md
   touch docs/module-1/chapter-3-digital-vs-physical-ai.md
   ```

3. **Create a category file for navigation**:
   ```bash
   # docs/module-1/_category_.json
   {
     "label": "Module 1: The Robotic Nervous System (ROS 2)",
     "position": 2,
     "link": {
       "type": "generated-index",
       "description": "Introduction to ROS 2 as the nervous system of humanoid robots"
     }
   }
   ```

## Writing Content

1. **Add frontmatter to each chapter**:
   ```markdown
   ---
   sidebar_position: 1
   title: Chapter 1 - ROS 2 Foundations
   ---

   # Chapter 1: ROS 2 as the Robotic Nervous System

   ## What is ROS 2?

   [Your content here...]
   ```

## Build and Deploy

1. **Build the static site**:
   ```bash
   npm run build
   ```

2. **Deploy to GitHub Pages**:
   ```bash
   npm run deploy
   ```

## Verify Setup

1. **Check that all chapters are accessible**:
   - Chapter 1: ROS 2 Foundations
   - Chapter 2: ROS 2 Middleware for Physical AI
   - Chapter 3: Digital vs Physical AI Systems

2. **Test navigation**:
   - Ensure sidebar navigation works
   - Verify chapter progression flows logically
   - Check that content is readable and accessible

## Next Steps

- Write content for each chapter following the data model
- Add code examples and diagrams where appropriate
- Implement any interactive components if needed
- Test the build process and deployment