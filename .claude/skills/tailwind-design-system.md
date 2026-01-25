# Tailwind Design System

**Description**: Comprehensive design system using Tailwind CSS with predefined tokens, components, and styling patterns for consistent UI development

---

## Skill Purpose

Provide a reusable, accessible design system with standardized color palettes, typography, spacing, and component patterns to ensure visual consistency across the Todo Chatbot application.

---

## Design Tokens

### 1. Color Palette

#### Primary Colors (Brand Identity)
```javascript
// Tailwind config extension
colors: {
  primary: {
    50: '#eff6ff',   // Lightest blue
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',  // Base primary
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',  // Darkest blue
  }
}
```

**Usage:**
- `bg-primary-500` - Primary buttons, active states
- `text-primary-600` - Links, interactive text
- `border-primary-300` - Input focus borders
- `hover:bg-primary-600` - Button hover states

#### Secondary Colors (Accents)
```javascript
secondary: {
  50: '#faf5ff',
  100: '#f3e8ff',
  200: '#e9d5ff',
  300: '#d8b4fe',
  400: '#c084fc',
  500: '#a855f7',  // Base secondary (purple)
  600: '#9333ea',
  700: '#7e22ce',
  800: '#6b21a8',
  900: '#581c87',
}
```

**Usage:**
- `bg-secondary-500` - Secondary actions, badges
- `text-secondary-600` - Accent text
- `border-secondary-300` - Decorative borders

#### Neutral Colors (Text & Backgrounds)
```javascript
neutral: {
  50: '#f9fafb',   // Lightest gray
  100: '#f3f4f6',
  200: '#e5e7eb',
  300: '#d1d5db',
  400: '#9ca3af',
  500: '#6b7280',  // Base gray
  600: '#4b5563',
  700: '#374151',
  800: '#1f2937',
  900: '#111827',  // Darkest gray
}
```

**Usage:**
- `bg-neutral-50` - Page backgrounds
- `bg-neutral-100` - Card backgrounds
- `text-neutral-900` - Primary text
- `text-neutral-600` - Secondary text
- `border-neutral-200` - Dividers, borders

#### Semantic Colors
```javascript
semantic: {
  success: {
    light: '#d1fae5',
    DEFAULT: '#10b981',
    dark: '#065f46',
  },
  error: {
    light: '#fee2e2',
    DEFAULT: '#ef4444',
    dark: '#991b1b',
  },
  warning: {
    light: '#fef3c7',
    DEFAULT: '#f59e0b',
    dark: '#92400e',
  },
  info: {
    light: '#dbeafe',
    DEFAULT: '#3b82f6',
    dark: '#1e40af',
  }
}
```

**Usage:**
- `bg-semantic-success` - Success messages, completed tasks
- `text-semantic-error` - Error messages
- `bg-semantic-warning-light` - Warning alerts
- `border-semantic-info` - Info notifications

---

### 2. Typography Scale

#### Heading Hierarchy
```
h1: text-4xl font-bold leading-tight tracking-tight
h2: text-3xl font-bold leading-tight
h3: text-2xl font-semibold leading-snug
h4: text-xl font-semibold leading-snug
h5: text-lg font-medium leading-normal
h6: text-base font-medium leading-normal
```

#### Body Text
```
body-lg: text-lg leading-relaxed
body: text-base leading-normal
body-sm: text-sm leading-normal
caption: text-xs leading-tight
```

#### Font Weights
```
font-light: 300
font-regular: 400
font-medium: 500
font-semibold: 600
font-bold: 700
```

**Example Usage:**
```jsx
<h1 className="text-4xl font-bold leading-tight tracking-tight text-neutral-900">
  Todo Chatbot
</h1>
<p className="text-base leading-normal text-neutral-600">
  Manage your tasks with AI assistance
</p>
```

---

### 3. Spacing System

**Base Unit:** 4px (Tailwind's default)

```
spacing: {
  0: '0px',
  1: '0.25rem',  // 4px
  2: '0.5rem',   // 8px
  3: '0.75rem',  // 12px
  4: '1rem',     // 16px
  5: '1.25rem',  // 20px
  6: '1.5rem',   // 24px
  8: '2rem',     // 32px
  10: '2.5rem',  // 40px
  12: '3rem',    // 48px
  16: '4rem',    // 64px
  20: '5rem',    // 80px
  24: '6rem',    // 96px
}
```

**Common Patterns:**
- Component padding: `p-4` or `p-6`
- Section spacing: `space-y-6` or `space-y-8`
- Button padding: `px-4 py-2` or `px-6 py-3`
- Card padding: `p-6` or `p-8`
- Gap in flex/grid: `gap-4` or `gap-6`

---

## Component Patterns

### 1. Buttons

#### Primary Button
```
bg-primary-500 hover:bg-primary-600 active:bg-primary-700
text-white font-medium
px-4 py-2 rounded-lg
transition-colors duration-200
focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
disabled:opacity-50 disabled:cursor-not-allowed
```

**Example:**
```jsx
<button className="bg-primary-500 hover:bg-primary-600 text-white font-medium px-4 py-2 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
  Add Task
</button>
```

#### Secondary Button
```
bg-neutral-100 hover:bg-neutral-200 active:bg-neutral-300
text-neutral-900 font-medium
px-4 py-2 rounded-lg
transition-colors duration-200
focus:outline-none focus:ring-2 focus:ring-neutral-400 focus:ring-offset-2
```

#### Outline Button
```
border-2 border-primary-500 hover:bg-primary-50
text-primary-600 hover:text-primary-700 font-medium
px-4 py-2 rounded-lg
transition-colors duration-200
focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
```

#### Ghost Button
```
text-neutral-700 hover:bg-neutral-100 active:bg-neutral-200
font-medium px-4 py-2 rounded-lg
transition-colors duration-200
focus:outline-none focus:ring-2 focus:ring-neutral-400 focus:ring-offset-2
```

#### Danger Button
```
bg-semantic-error hover:bg-red-600 active:bg-red-700
text-white font-medium
px-4 py-2 rounded-lg
transition-colors duration-200
focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2
```

---

### 2. Input Fields

#### Text Input
```
w-full px-4 py-2 rounded-lg
border border-neutral-300 focus:border-primary-500
bg-white text-neutral-900 placeholder-neutral-400
transition-colors duration-200
focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1
disabled:bg-neutral-100 disabled:cursor-not-allowed
```

**Example:**
```jsx
<input
  type="text"
  placeholder="Enter task title..."
  className="w-full px-4 py-2 rounded-lg border border-neutral-300 focus:border-primary-500 bg-white text-neutral-900 placeholder-neutral-400 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
/>
```

#### Textarea
```
w-full px-4 py-3 rounded-lg
border border-neutral-300 focus:border-primary-500
bg-white text-neutral-900 placeholder-neutral-400
resize-none min-h-[100px]
transition-colors duration-200
focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1
```

#### Select Dropdown
```
w-full px-4 py-2 rounded-lg
border border-neutral-300 focus:border-primary-500
bg-white text-neutral-900
appearance-none cursor-pointer
transition-colors duration-200
focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1
```

#### Checkbox
```
w-5 h-5 rounded
border-2 border-neutral-300 checked:border-primary-500
text-primary-500 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
cursor-pointer transition-colors duration-200
```

#### Radio Button
```
w-5 h-5 rounded-full
border-2 border-neutral-300 checked:border-primary-500
text-primary-500 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
cursor-pointer transition-colors duration-200
```

---

### 3. Cards & Containers

#### Basic Card
```
bg-white rounded-lg shadow-sm border border-neutral-200
p-6 transition-shadow duration-200
hover:shadow-md
```

#### Elevated Card
```
bg-white rounded-xl shadow-lg
p-6 transition-all duration-200
hover:shadow-xl hover:-translate-y-1
```

#### Chat Message Bubble (User)
```
bg-primary-500 text-white
rounded-2xl rounded-tr-sm
px-4 py-3 max-w-[80%]
shadow-sm
```

#### Chat Message Bubble (AI)
```
bg-neutral-100 text-neutral-900
rounded-2xl rounded-tl-sm
px-4 py-3 max-w-[80%]
shadow-sm
```

---

### 4. Navigation Components

#### Navigation Bar
```
bg-white border-b border-neutral-200
px-6 py-4 flex items-center justify-between
shadow-sm sticky top-0 z-50
```

#### Navigation Link (Active)
```
text-primary-600 font-medium
border-b-2 border-primary-500
px-3 py-2 transition-colors duration-200
```

#### Navigation Link (Inactive)
```
text-neutral-600 hover:text-neutral-900
border-b-2 border-transparent hover:border-neutral-300
px-3 py-2 transition-colors duration-200
```

---

### 5. Alerts & Notifications

#### Success Alert
```
bg-semantic-success-light border-l-4 border-semantic-success
text-semantic-success-dark
px-4 py-3 rounded-r-lg
flex items-start gap-3
```

#### Error Alert
```
bg-semantic-error-light border-l-4 border-semantic-error
text-semantic-error-dark
px-4 py-3 rounded-r-lg
flex items-start gap-3
```

#### Warning Alert
```
bg-semantic-warning-light border-l-4 border-semantic-warning
text-semantic-warning-dark
px-4 py-3 rounded-r-lg
flex items-start gap-3
```

#### Info Alert
```
bg-semantic-info-light border-l-4 border-semantic-info
text-semantic-info-dark
px-4 py-3 rounded-r-lg
flex items-start gap-3
```

#### Toast Notification
```
bg-white shadow-lg rounded-lg border border-neutral-200
px-4 py-3 min-w-[300px] max-w-[400px]
animate-slide-in-right
```

---

### 6. Loading States

#### Spinner
```
animate-spin rounded-full
border-4 border-neutral-200 border-t-primary-500
w-8 h-8
```

**Example:**
```jsx
<div className="flex items-center justify-center p-8">
  <div className="animate-spin rounded-full border-4 border-neutral-200 border-t-primary-500 w-8 h-8" />
</div>
```

#### Skeleton Loader
```
bg-neutral-200 animate-pulse rounded
h-4 w-full
```

#### Button Loading State
```
bg-primary-500 text-white font-medium
px-4 py-2 rounded-lg
opacity-70 cursor-wait
flex items-center gap-2
```

---

### 7. Empty States

```
flex flex-col items-center justify-center
text-center p-12
text-neutral-500
```

**Example:**
```jsx
<div className="flex flex-col items-center justify-center text-center p-12">
  <svg className="w-16 h-16 text-neutral-400 mb-4">...</svg>
  <h3 className="text-lg font-medium text-neutral-900 mb-2">No tasks yet</h3>
  <p className="text-sm text-neutral-500">Create your first task to get started</p>
</div>
```

---

## Layout Utilities

### Container Widths
```
container mx-auto px-4 sm:px-6 lg:px-8
max-w-7xl
```

### Grid Systems
```
// 2-column grid
grid grid-cols-1 md:grid-cols-2 gap-6

// 3-column grid
grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6

// Auto-fit grid
grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-6
```

### Flexbox Patterns
```
// Horizontal center
flex items-center justify-center

// Space between
flex items-center justify-between

// Vertical stack
flex flex-col space-y-4

// Horizontal row
flex items-center space-x-4
```

### Responsive Breakpoints
```
sm: 640px   // Mobile landscape
md: 768px   // Tablet
lg: 1024px  // Desktop
xl: 1280px  // Large desktop
2xl: 1536px // Extra large
```

---

## Effects & Animations

### Shadow Elevation
```
shadow-sm    // Subtle shadow
shadow       // Default shadow
shadow-md    // Medium shadow
shadow-lg    // Large shadow
shadow-xl    // Extra large shadow
shadow-2xl   // Maximum shadow
```

### Border Radius
```
rounded-sm   // 2px
rounded      // 4px
rounded-md   // 6px
rounded-lg   // 8px
rounded-xl   // 12px
rounded-2xl  // 16px
rounded-full // 9999px (circular)
```

### Transitions
```
transition-colors duration-200    // Color transitions
transition-all duration-200       // All properties
transition-transform duration-200 // Transform only
```

### Hover Effects
```
hover:scale-105      // Slight scale up
hover:shadow-lg      // Increase shadow
hover:-translate-y-1 // Lift up
hover:brightness-110 // Brighten
```

### Custom Animations (Add to tailwind.config.js)
```javascript
animation: {
  'slide-in-right': 'slideInRight 0.3s ease-out',
  'fade-in': 'fadeIn 0.2s ease-in',
  'bounce-subtle': 'bounceSubtle 0.5s ease-in-out',
}
keyframes: {
  slideInRight: {
    '0%': { transform: 'translateX(100%)', opacity: '0' },
    '100%': { transform: 'translateX(0)', opacity: '1' },
  },
  fadeIn: {
    '0%': { opacity: '0' },
    '100%': { opacity: '1' },
  },
  bounceSubtle: {
    '0%, 100%': { transform: 'translateY(0)' },
    '50%': { transform: 'translateY(-5px)' },
  },
}
```

---

## Accessibility Patterns

### Focus Indicators
```
focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
```

### Screen Reader Only
```
sr-only
// Visually hidden but accessible to screen readers
```

### ARIA Labels
Always include:
- `aria-label` for icon-only buttons
- `aria-describedby` for form fields with help text
- `role` attributes for custom components
- `aria-live` for dynamic content updates

### Keyboard Navigation
Ensure all interactive elements are keyboard accessible:
```
focus:ring-2 focus:ring-primary-500
tabindex="0"
```

### Color Contrast
- Text on white: Use `text-neutral-900` (AAA compliant)
- Secondary text: Use `text-neutral-600` (AA compliant)
- Links: Use `text-primary-600` with underline on hover

---

## Best Practices

### 1. Utility-First Approach
- Compose utilities instead of writing custom CSS
- Use `@apply` sparingly, only for repeated patterns
- Keep component classes in JSX for better visibility

### 2. Consistent Spacing
- Use spacing scale consistently (4px increments)
- Prefer `space-y-*` and `space-x-*` for child spacing
- Use `gap-*` for flex/grid layouts

### 3. Responsive Design
- Mobile-first approach (base styles, then `md:`, `lg:`)
- Test all breakpoints
- Use responsive utilities: `hidden md:block`, `flex-col md:flex-row`

### 4. Performance
- Avoid arbitrary values when possible: `w-[347px]` → `w-80`
- Use Tailwind's JIT mode for optimal bundle size
- Purge unused styles in production

### 5. Semantic Color Names
- Use semantic names in components: `bg-primary-500` not `bg-blue-500`
- Makes theme changes easier
- Improves code readability

---

## Usage Examples

### Modern Chat Interface
```jsx
<div className="flex flex-col h-screen bg-neutral-50">
  {/* Header */}
  <header className="bg-white border-b border-neutral-200 px-6 py-4 shadow-sm">
    <h1 className="text-2xl font-bold text-neutral-900">Todo Chatbot</h1>
  </header>

  {/* Messages */}
  <div className="flex-1 overflow-y-auto p-6 space-y-4">
    {/* User message */}
    <div className="flex justify-end">
      <div className="bg-primary-500 text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-[80%] shadow-sm">
        Add a task to buy groceries
      </div>
    </div>

    {/* AI message */}
    <div className="flex justify-start">
      <div className="bg-neutral-100 text-neutral-900 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[80%] shadow-sm">
        I've added "Buy groceries" to your task list!
      </div>
    </div>
  </div>

  {/* Input */}
  <div className="bg-white border-t border-neutral-200 p-4">
    <div className="flex gap-2">
      <input
        type="text"
        placeholder="Type a message..."
        className="flex-1 px-4 py-2 rounded-lg border border-neutral-300 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
      />
      <button className="bg-primary-500 hover:bg-primary-600 text-white font-medium px-6 py-2 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
        Send
      </button>
    </div>
  </div>
</div>
```

### Task Card
```jsx
<div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6 hover:shadow-md transition-shadow duration-200">
  <div className="flex items-start justify-between mb-3">
    <h3 className="text-lg font-semibold text-neutral-900">Buy groceries</h3>
    <button className="text-neutral-400 hover:text-neutral-600 transition-colors">
      <svg className="w-5 h-5">...</svg>
    </button>
  </div>
  <p className="text-sm text-neutral-600 mb-4">
    Get milk, eggs, and bread from the store
  </p>
  <div className="flex items-center justify-between">
    <span className="text-xs text-neutral-500">Due: Today</span>
    <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
      Mark complete
    </button>
  </div>
</div>
```

---

## Checklist

- [ ] Color palette defined and consistent
- [ ] Typography scale applied to all text elements
- [ ] Spacing system used consistently (4px increments)
- [ ] All interactive elements have focus states
- [ ] Hover states defined for clickable elements
- [ ] Loading states implemented for async actions
- [ ] Empty states designed for zero-data scenarios
- [ ] Error states handled with clear messaging
- [ ] Responsive breakpoints tested (mobile, tablet, desktop)
- [ ] Color contrast meets WCAG AA standards
- [ ] Keyboard navigation works for all interactions
- [ ] ARIA labels added for accessibility
- [ ] Animations are subtle and purposeful
- [ ] Dark mode variants considered (if applicable)

---

## Usage

**Frontend Development Agent** and **UI/UX Design Agent** use this skill when:

- Creating new UI components
- Styling forms and inputs
- Designing chat interfaces
- Building navigation elements
- Implementing loading and error states
- Ensuring visual consistency
- Improving accessibility
- Optimizing responsive layouts

Always reference the relevant task ID from `tasks.md` when applying design system patterns.
