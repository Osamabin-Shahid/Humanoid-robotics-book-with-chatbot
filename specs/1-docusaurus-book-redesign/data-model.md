# Data Model: Docusaurus Book Cleanup & Neural-Themed UI

## Overview
This project is a UI/UX redesign that doesn't introduce new data models. It works with the existing book content structure.

## Existing Content Structure

### Book Module
- id: string (unique identifier)
- title: string (module title)
- position: number (ordering)
- chapters: Chapter[] (list of chapters in the module)

### Chapter
- id: string (unique identifier)
- title: string (chapter title)
- position: number (ordering within module)
- content: string (path to markdown file)
- sidebar_position: number (position in sidebar navigation)

## Navigation Structure
- items: NavigationItem[] (list of navigation items)
- type: "category" | "doc" | "link" (navigation item type)
- label: string (display text)
- to: string (destination path)

## UI Components (Configuration)
### Homepage Card
- title: string (card title)
- description: string (card description)
- to: string (destination path)
- icon: string (icon identifier)
- color: string (theme color for the card)

### Theme Configuration
- primaryColor: string (main theme color)
- secondaryColor: string (secondary theme color)
- gradientStart: string (gradient start color)
- gradientEnd: string (gradient end color)
- fontFamily: string (font family for the site)
- animationEnabled: boolean (whether animations are enabled)

## CSS Variables (Custom Properties)
- --ifm-color-primary: string (primary color)
- --ifm-color-secondary: string (secondary color)
- --ifm-navbar-background-color: string (navbar background)
- --ifm-footer-background-color: string (footer background)
- --ifm-card-background-color: string (card background)
- --ifm-animation-duration: string (animation duration)