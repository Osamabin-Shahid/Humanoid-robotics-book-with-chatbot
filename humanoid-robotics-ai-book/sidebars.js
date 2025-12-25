/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

module.exports = {
  docs: [
    'intro',
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      items: [
        'module-1/intro',
        'module-1/chapter-1-ros2-foundations',
        'module-1/chapter-2-ros2-middleware',
        'module-1/chapter-3-digital-vs-physical-ai'
      ],
    },
    {
      type: 'category',
      label: 'Module 2: The Digital Twin (Gazebo & Unity)',
      items: [
        'module-2/intro',
        'module-2/gazebo-physics',
        'module-2/unity-visualization',
        'module-2/sensor-simulation'
      ],
    },
    {
      type: 'category',
      label: 'Module 3: The AI-Robot Brain (NVIDIA Isaac™)',
      items: [
        'module-3/intro',
        'module-3/isaac-sim',
        'module-3/isaac-ros',
        'module-3/nav2-navigation'
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action (VLA) – The Cognitive Humanoid',
      items: [
        'module-4/intro',
        'module-4/voice-to-action',
        'module-4/cognitive-planning',
        'module-4/autonomous-humanoid'
      ],
    },
  ],
};
