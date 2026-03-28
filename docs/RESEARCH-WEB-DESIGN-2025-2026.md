# Cutting-Edge Web Design Techniques & Trends 2025-2026
## Comprehensive Research Report for Vibe Coding Syllabus Page

> Target: Single HTML file with inline CSS & JS. No build tools. Futuristic, stunning look.

---

## 1. CSS-Only Animations & Effects (No External Libraries)

### 1.1 CSS Scroll-Driven Animations

**Browser Support (Feb 2026):** Chrome 115+, Edge 115+, Safari 26+, Firefox (flag)

Two core timeline types:

#### Scroll Progress Timeline - `scroll()`
Ties animation progress to scroll position of a container.

```css
@keyframes slideIn {
  from { opacity: 0; transform: translateX(-100px); }
  to   { opacity: 1; transform: translateX(0); }
}

.animated-element {
  animation: slideIn linear;
  animation-timeline: scroll();        /* tied to nearest scroll container */
  animation-range: entry 0% entry 100%; /* animate while entering viewport */
}
```

#### View Progress Timeline - `view()`
Animates based on element visibility within the scrollport.

```css
.reveal-card {
  animation: fadeScale linear both;
  animation-timeline: view();
  animation-range: entry 10% cover 40%;
}

@keyframes fadeScale {
  from { opacity: 0; transform: scale(0.8); }
  to   { opacity: 1; transform: scale(1); }
}
```

#### Scroll-Triggered Animations (Chrome 145+, 2026)
Time-based animations that trigger when crossing scroll offsets:

```css
.element {
  animation: popIn 0.6s ease-out both;
  animation-trigger: view();  /* NEW in 2026 */
  animation-trigger-range: entry 20%;
}
```

#### Parallax with Pure CSS Scroll-Driven Animations
```css
.parallax-bg {
  animation: parallax linear;
  animation-timeline: scroll();
}

@keyframes parallax {
  from { transform: translateY(0); }
  to   { transform: translateY(-30%); }
}
```

**Key Resources:**
- [MDN: CSS Scroll-Driven Animations](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations)
- [Chrome: Scroll-Driven Animations](https://developer.chrome.com/docs/css-ui/scroll-driven-animations)
- [CSS-Tricks: Bringing Back Parallax](https://css-tricks.com/bringing-back-parallax-with-scroll-driven-css-animations/)
- [Scroll-Driven Animations Demos](https://scroll-driven-animations.style/)

---

### 1.2 CSS `@property` and Custom Properties for Animations

`@property` registers custom properties with a type, so the browser can interpolate and animate them.

#### Animating Gradients (Impossible Without @property)
```css
@property --gradient-angle {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}

@property --color-1 {
  syntax: '<color>';
  initial-value: #6366f1;
  inherits: false;
}

@property --color-2 {
  syntax: '<color>';
  initial-value: #ec4899;
  inherits: false;
}

.aurora-bg {
  --gradient-angle: 0deg;
  --color-1: #6366f1;
  --color-2: #ec4899;
  background: linear-gradient(var(--gradient-angle), var(--color-1), var(--color-2));
  animation: auroraShift 8s ease-in-out infinite alternate;
}

@keyframes auroraShift {
  0%   { --gradient-angle: 0deg;   --color-1: #6366f1; --color-2: #ec4899; }
  33%  { --gradient-angle: 120deg; --color-1: #06b6d4; --color-2: #8b5cf6; }
  66%  { --gradient-angle: 240deg; --color-1: #f59e0b; --color-2: #10b981; }
  100% { --gradient-angle: 360deg; --color-1: #6366f1; --color-2: #ec4899; }
}
```

#### Coordinated Multi-Property Animation from Single Token
```css
@property --reveal-progress {
  syntax: '<number>';
  initial-value: 0;
  inherits: false;
}

.reveal-element {
  --reveal-progress: 0;
  opacity: var(--reveal-progress);
  transform: translateY(calc((1 - var(--reveal-progress)) * 40px));
  clip-path: inset(calc((1 - var(--reveal-progress)) * 100%) 0 0 0);
  transition: --reveal-progress 0.8s ease-out;
}

.reveal-element.visible {
  --reveal-progress: 1;
}
```

#### Animated Conic Gradient Border
```css
@property --border-angle {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}

.glow-card {
  --border-angle: 0deg;
  border: 2px solid transparent;
  background:
    linear-gradient(#0a0a1a, #0a0a1a) padding-box,
    conic-gradient(from var(--border-angle), #6366f1, #ec4899, #06b6d4, #6366f1) border-box;
  animation: rotateBorder 3s linear infinite;
}

@keyframes rotateBorder {
  to { --border-angle: 360deg; }
}
```

**Key Resources:**
- [CSS-Tricks: Exploring @property](https://css-tricks.com/exploring-property-and-its-animating-powers/)
- [Smashing Magazine: Custom @property](https://www.smashingmagazine.com/2024/05/times-need-custom-property-instead-css-variable/)
- [Egghead: Animate Custom Properties](https://egghead.io/lessons/css-use-css-property-to-animate-and-transition-custom-properties)

---

### 1.3 CSS Container Queries

Container queries adapt components to their container size, not the viewport. Production-ready in all major browsers.

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 400px) {
  .card-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }
}

@container card (max-width: 399px) {
  .card-content {
    display: flex;
    flex-direction: column;
  }
}
```

#### Container Units (cqw, cqh, cqi, cqb)
```css
.adaptive-text {
  font-size: clamp(0.875rem, 3cqi, 1.5rem);
  padding: 2cqi;
}
```

**Key Resources:**
- [CSS Container Queries in 2025](https://caisy.io/blog/css-container-queries)
- [Medium: CSS 2025 Container Queries](https://medium.com/@vyakymenko/css-2025-container-queries-and-style-queries-in-real-projects-c38af5a13aa2)

---

### 1.4 View Transitions API

Enables native morphing/crossfade transitions between DOM states without frameworks.

```javascript
// Basic same-document transition
function switchSection(newContent) {
  if (!document.startViewTransition) {
    updateDOM(newContent);
    return;
  }

  document.startViewTransition(() => {
    updateDOM(newContent);
  });
}
```

```css
/* Customize the transition */
::view-transition-old(root) {
  animation: fadeOut 0.3s ease-out;
}
::view-transition-new(root) {
  animation: fadeIn 0.3s ease-in;
}

/* Named element morphing */
.hero-image {
  view-transition-name: hero;
}

::view-transition-group(hero) {
  animation-duration: 0.5s;
  animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
```

#### Morph Between Sections
```css
/* The browser interpolates position, size, and transform */
.section-heading {
  view-transition-name: heading;
}

/* New in 2025: auto-naming */
.list-item {
  view-transition-name: match-element; /* auto-unique per element */
}
```

**Key Resources:**
- [Chrome: View Transitions](https://developer.chrome.com/docs/web-platform/view-transitions)
- [Chrome: View Transitions 2025 Update](https://developer.chrome.com/blog/view-transitions-in-2025)
- [MDN: View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API)

---

### 1.5 New CSS Features for 2026

- **`sibling-index()`** - Stagger animations based on element position
- **`::scroll-button` / `::scroll-marker`** - Native carousel navigation
- **CSS Anchor Positioning** - Tether elements to each other with pure CSS
- **Interest Invoker API** - Handle hover interactions at browser level
- **`@starting-style`** - Define where an element came from for entry animations

```css
/* Stagger with sibling-index() - 2026 */
.stagger-item {
  transition-delay: calc(sibling-index() * 0.08s);
  opacity: 0;
  transform: translateY(20px);
}

.stagger-item.visible {
  opacity: 1;
  transform: translateY(0);
}
```

**Key Resources:**
- [LogRocket: CSS in 2026](https://blog.logrocket.com/css-in-2026/)
- [Nerdy.dev: 4 CSS Features for 2026](https://nerdy.dev/4-css-features-every-front-end-developer-should-know-in-2026)
- [Medium: Most Awaited CSS Features of 2026](https://medium.com/@onix_react/most-awaited-css-features-of-2026-886d76d666b2)

---

## 2. Cutting-Edge Visual Effects (Pure HTML/CSS/JS)

### 2.1 Glass Morphism & Liquid Glass

Apple's WWDC 2025 "Liquid Glass" effect popularized this trend.

#### Basic Glassmorphism
```css
.glass-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}
```

#### Advanced Liquid Glass with SVG Filters
```html
<svg style="position:absolute;width:0;height:0">
  <filter id="liquid-glass">
    <feTurbulence type="fractalNoise" baseFrequency="0.015" numOctaves="3" result="noise" seed="1"/>
    <feDisplacementMap in="SourceGraphic" in2="noise" scale="12" xChannelSelector="R" yChannelSelector="G"/>
    <feSpecularLighting surfaceScale="2" specularConstant="1" specularExponent="20" result="specular">
      <fePointLight x="-100" y="-200" z="300"/>
    </feSpecularLighting>
    <feComposite in="SourceGraphic" in2="specular" operator="arithmetic" k1="0" k2="1" k3="0.5" k4="0"/>
  </filter>
</svg>

<div style="filter: url(#liquid-glass);" class="glass-panel">
  Content here
</div>
```

#### Animated Liquid Glass (JS for turbulence animation)
```javascript
const turbulence = document.querySelector('#liquid-glass feTurbulence');
let seed = 1;
function animateTurbulence() {
  seed += 0.005;
  turbulence.setAttribute('seed', seed);
  requestAnimationFrame(animateTurbulence);
}
animateTurbulence();
```

**Key Resources:**
- [FreeFrontend: CSS Liquid Glass](https://freefrontend.com/css-liquid-glass/)
- [Mitkov: CSS Liquid Glass How-To](https://www.mitkov-systems.de/en/blog/css-liquid-glass-how-to)
- [WWDC 2025 Liquid Glass](https://www.liquidglassresources.com/development/liquid-glass-effect-css-svg/)
- [Glass CSS Generator](https://css.glass/)

---

### 2.2 3D CSS Transforms & Perspective

```css
.scene {
  perspective: 1000px;
  perspective-origin: 50% 50%;
}

.card-3d {
  transform-style: preserve-3d;
  transition: transform 0.6s cubic-bezier(0.23, 1, 0.32, 1);
}

.card-3d:hover {
  transform: rotateY(15deg) rotateX(-5deg) translateZ(30px);
}

/* Dynamic tilt with JavaScript */
```

```javascript
document.querySelectorAll('.tilt-card').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = (y - centerY) / centerY * -10;  // max 10deg
    const rotateY = (x - centerX) / centerX * 10;

    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
  });

  card.addEventListener('mouseleave', () => {
    card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0)';
    card.style.transition = 'transform 0.5s ease-out';
  });

  card.addEventListener('mouseenter', () => {
    card.style.transition = 'none';
  });
});
```

**Key Resources:**
- [Frontend.fyi: CSS 3D Perspective Animations](https://www.frontend.fyi/tutorials/css-3d-perspective-animations)
- [LetsBuildUI: 3D Hover Effect](https://www.letsbuildui.dev/articles/a-3d-hover-effect-using-css-transforms/)
- [FreeFrontend: 65 CSS 3D Transforms](https://freefrontend.com/css-3d-transforms/)

---

### 2.3 Chromatic Aberration / Holographic / Iridescent Effects

#### Holographic Card Effect (Pure CSS)
```css
.holographic {
  position: relative;
  overflow: hidden;
}

.holographic::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(255,0,0,0.1) 0%,
    rgba(255,127,0,0.1) 14%,
    rgba(255,255,0,0.1) 28%,
    rgba(0,255,0,0.1) 42%,
    rgba(0,0,255,0.1) 57%,
    rgba(75,0,130,0.1) 71%,
    rgba(148,0,211,0.1) 85%,
    rgba(255,0,0,0.1) 100%
  );
  background-size: 200% 200%;
  animation: holographicShift 5s ease-in-out infinite;
  mix-blend-mode: color-dodge;
  pointer-events: none;
}

@keyframes holographicShift {
  0%   { background-position: 0% 0%; }
  50%  { background-position: 100% 100%; }
  100% { background-position: 0% 0%; }
}
```

#### Chromatic Aberration (Text)
```css
.chromatic-text {
  color: white;
  text-shadow:
    -2px 0 rgba(255, 0, 0, 0.5),
     2px 0 rgba(0, 255, 255, 0.5);
  animation: chromaticPulse 3s ease-in-out infinite;
}

@keyframes chromaticPulse {
  0%, 100% {
    text-shadow:
      -2px 0 rgba(255, 0, 0, 0.5),
       2px 0 rgba(0, 255, 255, 0.5);
  }
  50% {
    text-shadow:
      -4px 0 rgba(255, 0, 0, 0.7),
       4px 0 rgba(0, 255, 255, 0.7);
  }
}
```

#### Iridescent Surface
```css
@property --iridescent-hue {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}

.iridescent {
  background: linear-gradient(
    45deg,
    hsl(calc(var(--iridescent-hue) + 0deg)   70% 60%),
    hsl(calc(var(--iridescent-hue) + 60deg)  70% 60%),
    hsl(calc(var(--iridescent-hue) + 120deg) 70% 60%),
    hsl(calc(var(--iridescent-hue) + 180deg) 70% 60%)
  );
  animation: iridescentShift 6s linear infinite;
}

@keyframes iridescentShift {
  to { --iridescent-hue: 360deg; }
}
```

**Key Resources:**
- [CSS3.com: Holographic CSS Effect Guide](https://css3.com/how-to-get-the-holographic-css-effect-a-complete-guide/)
- [Robb Owen: CSS Blend Mode Shaders](https://robbowen.digital/wrote-about/css-blend-mode-shaders/)
- [GitHub: Liquid CSS - Chromatic Aberration](https://github.com/electrikmilk/liquid-css)

---

### 2.4 Gradient Mesh Animations

```css
@property --mesh-x {
  syntax: '<percentage>';
  initial-value: 30%;
  inherits: false;
}
@property --mesh-y {
  syntax: '<percentage>';
  initial-value: 20%;
  inherits: false;
}

.gradient-mesh {
  background:
    radial-gradient(ellipse at var(--mesh-x) var(--mesh-y), rgba(99, 102, 241, 0.8) 0%, transparent 50%),
    radial-gradient(ellipse at calc(100% - var(--mesh-x)) calc(100% - var(--mesh-y)), rgba(236, 72, 153, 0.6) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(6, 182, 212, 0.4) 0%, transparent 60%),
    linear-gradient(135deg, #0a0a2e, #1a1a4e);
  animation: meshMove 12s ease-in-out infinite alternate;
}

@keyframes meshMove {
  0%   { --mesh-x: 20%; --mesh-y: 20%; }
  25%  { --mesh-x: 80%; --mesh-y: 30%; }
  50%  { --mesh-x: 60%; --mesh-y: 80%; }
  75%  { --mesh-x: 30%; --mesh-y: 70%; }
  100% { --mesh-x: 20%; --mesh-y: 20%; }
}
```

---

### 2.5 Text Reveal Animations & Kinetic Typography

#### Split Text Reveal (Character by Character)
```html
<h1 class="split-reveal" data-text="Vibe Coding">Vibe Coding</h1>
```

```javascript
document.querySelectorAll('.split-reveal').forEach(el => {
  const text = el.textContent;
  el.innerHTML = text.split('').map((char, i) =>
    `<span style="
      display:inline-block;
      opacity:0;
      transform:translateY(40px) rotateX(-90deg);
      animation:charReveal 0.6s ease-out forwards;
      animation-delay:${i * 0.05}s;
    ">${char === ' ' ? '&nbsp;' : char}</span>`
  ).join('');
});
```

```css
@keyframes charReveal {
  to {
    opacity: 1;
    transform: translateY(0) rotateX(0);
  }
}
```

#### Clip-Path Text Reveal on Scroll
```css
.text-reveal {
  clip-path: inset(0 100% 0 0);  /* RTL: inset(0 0 0 100%) */
  animation: clipReveal linear both;
  animation-timeline: view();
  animation-range: entry 20% cover 50%;
}

@keyframes clipReveal {
  to { clip-path: inset(0 0 0 0); }
}
```

#### Scroll-Driven 3D Cylindrical Text
```css
.cylinder-text {
  transform-style: preserve-3d;
  animation: cylinderRotate linear;
  animation-timeline: scroll();
}

@keyframes cylinderRotate {
  from { transform: rotateX(0); }
  to   { transform: rotateX(360deg); }
}
```

**Key Resources:**
- [FreeFrontend: 96 CSS Text Animations](https://freefrontend.com/css-text-animations/)
- [Codrops: 3D Scroll-Driven Text Animations](https://tympanus.net/codrops/2025/11/04/creating-3d-scroll-driven-text-animations-with-css-and-gsap/)
- [CSS Author: 35+ Text Animation Examples](https://cssauthor.com/css-text-animation-examples/)

---

### 2.6 Particle Systems

#### CSS-Only Particles (No JS)
```css
.particles {
  position: fixed;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  animation: particleFloat var(--duration) var(--delay) linear infinite;
}

@keyframes particleFloat {
  0%   { transform: translateY(100vh) translateX(0) scale(0); opacity: 0; }
  10%  { opacity: 1; }
  90%  { opacity: 1; }
  100% { transform: translateY(-10vh) translateX(var(--drift)) scale(1); opacity: 0; }
}
```

Generate in HTML:
```html
<!-- Generate 30-50 particles with varied custom properties -->
<div class="particles">
  <div class="particle" style="left:5%;--duration:12s;--delay:0s;--drift:20px"></div>
  <div class="particle" style="left:15%;--duration:18s;--delay:2s;--drift:-30px"></div>
  <!-- ... more particles -->
</div>
```

Or generate with JS:
```javascript
const container = document.querySelector('.particles');
for (let i = 0; i < 40; i++) {
  const p = document.createElement('div');
  p.className = 'particle';
  p.style.cssText = `
    left: ${Math.random() * 100}%;
    --duration: ${10 + Math.random() * 20}s;
    --delay: ${Math.random() * 10}s;
    --drift: ${(Math.random() - 0.5) * 100}px;
    width: ${2 + Math.random() * 4}px;
    height: ${2 + Math.random() * 4}px;
    background: rgba(${150 + Math.random()*105}, ${150 + Math.random()*105}, 255, ${0.1 + Math.random()*0.3});
  `;
  container.appendChild(p);
}
```

#### Canvas Particle System (Performant)
```javascript
const canvas = document.createElement('canvas');
canvas.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:0;';
document.body.prepend(canvas);
const ctx = canvas.getContext('2d');

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

const particles = Array.from({length: 80}, () => ({
  x: Math.random() * canvas.width,
  y: Math.random() * canvas.height,
  vx: (Math.random() - 0.5) * 0.5,
  vy: (Math.random() - 0.5) * 0.5,
  size: 1 + Math.random() * 2,
  alpha: 0.1 + Math.random() * 0.4
}));

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw connections
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x;
      const dy = particles[i].y - particles[j].y;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist < 150) {
        ctx.strokeStyle = `rgba(100, 150, 255, ${0.15 * (1 - dist/150)})`;
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        ctx.moveTo(particles[i].x, particles[i].y);
        ctx.lineTo(particles[j].x, particles[j].y);
        ctx.stroke();
      }
    }
  }

  // Draw particles
  particles.forEach(p => {
    p.x += p.vx;
    p.y += p.vy;
    if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
    if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

    ctx.fillStyle = `rgba(130, 170, 255, ${p.alpha})`;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    ctx.fill();
  });

  requestAnimationFrame(draw);
}
draw();
```

---

### 2.7 Aurora / Noise Effects (CSS-Only)

#### Pure CSS Aurora Background
```css
.aurora {
  position: fixed;
  inset: 0;
  z-index: -1;
  overflow: hidden;
  background: #0a0a2e;
}

.aurora::before,
.aurora::after {
  content: '';
  position: absolute;
  width: 200%;
  height: 200%;
  top: -50%;
  left: -50%;
}

.aurora::before {
  background:
    radial-gradient(ellipse at 20% 50%, rgba(99, 102, 241, 0.4) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 50%, rgba(236, 72, 153, 0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 80%, rgba(6, 182, 212, 0.3) 0%, transparent 50%);
  animation: auroraMove1 15s ease-in-out infinite alternate;
  filter: blur(60px);
}

.aurora::after {
  background:
    radial-gradient(ellipse at 70% 30%, rgba(139, 92, 246, 0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 30% 70%, rgba(14, 165, 233, 0.3) 0%, transparent 50%);
  animation: auroraMove2 20s ease-in-out infinite alternate;
  filter: blur(80px);
}

@keyframes auroraMove1 {
  0%   { transform: translate(0, 0) rotate(0deg); }
  100% { transform: translate(-5%, 3%) rotate(5deg); }
}

@keyframes auroraMove2 {
  0%   { transform: translate(0, 0) rotate(0deg) scale(1); }
  100% { transform: translate(3%, -2%) rotate(-3deg) scale(1.1); }
}
```

#### SVG Noise Texture Overlay
```html
<svg style="position:fixed;inset:0;pointer-events:none;z-index:9999;opacity:0.03;mix-blend-mode:overlay;">
  <filter id="noiseFilter">
    <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/>
  </filter>
  <rect width="100%" height="100%" filter="url(#noiseFilter)"/>
</svg>
```

**Key Resources:**
- [Dalton Walsh: Aurora CSS Background](https://daltonwalsh.com/blog/aurora-css-background-effect/)
- [GitHub: Auroral - Animated Gradients](https://github.com/LunarLogic/auroral)
- [Interwebing: Aurora CSS Effect](https://www.interwebing.com/css/cool-css-backgrounds-the-aurora-effect/)

---

## 3. Interactive Experiences for Single-Page Sites

### 3.1 Horizontal Scroll Sections

```css
.horizontal-scroll-container {
  height: 300vh; /* Controls scroll length */
  position: relative;
}

.horizontal-scroll-sticky {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: hidden;
}

.horizontal-scroll-track {
  display: flex;
  gap: 2rem;
  height: 100%;
  width: max-content;
}

.horizontal-panel {
  width: 80vw;
  height: 80vh;
  flex-shrink: 0;
}
```

```javascript
const container = document.querySelector('.horizontal-scroll-container');
const track = document.querySelector('.horizontal-scroll-track');

window.addEventListener('scroll', () => {
  const rect = container.getBoundingClientRect();
  const scrollProgress = -rect.top / (container.offsetHeight - window.innerHeight);
  const maxTranslate = track.scrollWidth - window.innerWidth;
  const translateX = Math.max(0, Math.min(scrollProgress * maxTranslate, maxTranslate));
  track.style.transform = `translateX(-${translateX}px)`;
});
```

### 3.2 Magnetic Cursor Effect

```javascript
document.querySelectorAll('.magnetic').forEach(el => {
  el.addEventListener('mousemove', (e) => {
    const rect = el.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    const strength = 0.3; // 0 to 1

    el.style.transform = `translate(${x * strength}px, ${y * strength}px)`;
  });

  el.addEventListener('mouseleave', () => {
    el.style.transform = 'translate(0, 0)';
    el.style.transition = 'transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
  });

  el.addEventListener('mouseenter', () => {
    el.style.transition = 'none';
  });
});
```

### 3.3 Scroll-Triggered SVG Path Animations

```html
<svg viewBox="0 0 1200 2000" class="timeline-path">
  <path id="mainPath"
    d="M 600 0 C 400 200, 800 400, 600 600 C 400 800, 800 1000, 600 1200 C 400 1400, 800 1600, 600 1800"
    fill="none"
    stroke="url(#pathGradient)"
    stroke-width="3"
    stroke-linecap="round"/>
  <defs>
    <linearGradient id="pathGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#6366f1"/>
      <stop offset="100%" stop-color="#06b6d4"/>
    </linearGradient>
  </defs>
</svg>
```

```javascript
const path = document.getElementById('mainPath');
const pathLength = path.getTotalLength();

path.style.strokeDasharray = pathLength;
path.style.strokeDashoffset = pathLength;

window.addEventListener('scroll', () => {
  const scrollPercent = window.scrollY / (document.body.scrollHeight - window.innerHeight);
  const drawLength = pathLength * scrollPercent;
  path.style.strokeDashoffset = pathLength - drawLength;
});
```

#### CSS-Only SVG Draw on Scroll (Modern)
```css
#mainPath {
  stroke-dasharray: 5000;  /* path length */
  stroke-dashoffset: 5000;
  animation: drawPath linear;
  animation-timeline: scroll();
}

@keyframes drawPath {
  to { stroke-dashoffset: 0; }
}
```

### 3.4 Reveal-on-Scroll with Stagger

```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const children = entry.target.querySelectorAll('.stagger-child');
      children.forEach((child, i) => {
        child.style.transitionDelay = `${i * 0.1}s`;
        child.classList.add('visible');
      });
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.2 });

document.querySelectorAll('.stagger-parent').forEach(el => {
  observer.observe(el);
});
```

```css
.stagger-child {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.stagger-child.visible {
  opacity: 1;
  transform: translateY(0);
}

/* Respect user preferences */
@media (prefers-reduced-motion: reduce) {
  .stagger-child {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
```

**Key Resources:**
- [W3Schools: SVG Draw on Scroll](https://www.w3schools.com/howto/howto_js_scrolldrawing.asp)
- [Codrops: Animate SVG Shapes on Scroll](https://tympanus.net/codrops/2022/06/08/how-to-animate-svg-shapes-on-scroll/)
- [Dennis Kats: Path Scroll Animation](https://denniskats.dev/blog/path_scroll_animation)
- [FreeCodeCamp: Scroll Animations with IntersectionObserver](https://www.freecodecamp.org/news/scroll-animations-with-javascript-intersection-observer-api/)

---

## 4. Roadmap/Timeline Visual Experiences

### 4.1 Journey Path Timeline with SVG Draw-on-Scroll

This creates a winding SVG path connecting nodes, drawn as user scrolls.

```html
<div class="journey-timeline">
  <svg class="journey-svg" viewBox="0 0 800 3000" preserveAspectRatio="xMidYMid meet">
    <!-- Winding path -->
    <path class="journey-path" d="
      M 400 50
      C 200 200, 600 350, 400 500
      C 200 650, 600 800, 400 950
      C 200 1100, 600 1250, 400 1400
      C 200 1550, 600 1700, 400 1850
      C 200 2000, 600 2150, 400 2300
      C 200 2450, 600 2600, 400 2750
    " fill="none" stroke="url(#journeyGrad)" stroke-width="3"/>

    <!-- Glow version of same path -->
    <path class="journey-path-glow" d="..."
      fill="none" stroke="url(#journeyGrad)" stroke-width="8"
      filter="blur(6px)" opacity="0.4"/>

    <!-- Milestone dots at path positions -->
    <circle class="milestone" cx="400" cy="50" r="8" fill="#6366f1"/>
    <circle class="milestone" cx="400" cy="500" r="8" fill="#8b5cf6"/>
    <circle class="milestone" cx="400" cy="950" r="8" fill="#a855f7"/>
    <circle class="milestone" cx="400" cy="1400" r="8" fill="#ec4899"/>
    <!-- ... more milestones -->

    <defs>
      <linearGradient id="journeyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#6366f1"/>
        <stop offset="50%" stop-color="#a855f7"/>
        <stop offset="100%" stop-color="#06b6d4"/>
      </linearGradient>
    </defs>
  </svg>

  <!-- Content cards positioned alongside the path -->
  <div class="milestone-card" style="top: 50px;">
    <h3>Phase 1: Foundation</h3>
    <p>HTML, CSS, JavaScript basics</p>
  </div>
  <!-- ... more cards -->
</div>
```

```css
.journey-timeline {
  position: relative;
  min-height: 3000px;
}

.journey-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.journey-path {
  stroke-dasharray: var(--path-length);
  stroke-dashoffset: var(--path-length);
  animation: drawJourney linear;
  animation-timeline: scroll();
}

@keyframes drawJourney {
  to { stroke-dashoffset: 0; }
}

.milestone {
  opacity: 0;
  transform-origin: center;
  animation: popMilestone 0.3s ease-out forwards;
  animation-timeline: view();
  animation-range: entry 50% entry 100%;
}

@keyframes popMilestone {
  from { opacity: 0; r: 0; }
  to   { opacity: 1; r: 12; }
}

.milestone-card {
  position: absolute;
  width: 300px;
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 1.5rem;
  opacity: 0;
  transform: translateX(30px);
  animation: cardSlideIn linear both;
  animation-timeline: view();
  animation-range: entry 20% cover 40%;
}

@keyframes cardSlideIn {
  to { opacity: 1; transform: translateX(0); }
}
```

### 4.2 Constellation / Node Network Style

```javascript
// Canvas-based constellation that connects milestone nodes
class ConstellationTimeline {
  constructor(canvas, nodes) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.nodes = nodes; // [{x, y, label, active}]
    this.connections = [];
    this.mouseX = 0;
    this.mouseY = 0;

    // Build connections between sequential nodes
    for (let i = 0; i < nodes.length - 1; i++) {
      this.connections.push([i, i + 1]);
    }

    this.animate();
  }

  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw connections with glow
    this.connections.forEach(([a, b]) => {
      const nodeA = this.nodes[a];
      const nodeB = this.nodes[b];

      // Gradient line
      const grad = this.ctx.createLinearGradient(
        nodeA.x, nodeA.y, nodeB.x, nodeB.y
      );
      grad.addColorStop(0, nodeA.active ? 'rgba(99,102,241,0.8)' : 'rgba(99,102,241,0.2)');
      grad.addColorStop(1, nodeB.active ? 'rgba(139,92,246,0.8)' : 'rgba(139,92,246,0.2)');

      this.ctx.strokeStyle = grad;
      this.ctx.lineWidth = 2;
      this.ctx.beginPath();
      this.ctx.moveTo(nodeA.x, nodeA.y);
      this.ctx.lineTo(nodeB.x, nodeB.y);
      this.ctx.stroke();
    });

    // Draw nodes
    this.nodes.forEach(node => {
      // Outer glow
      const glow = this.ctx.createRadialGradient(
        node.x, node.y, 0, node.x, node.y, node.active ? 30 : 15
      );
      glow.addColorStop(0, node.active ? 'rgba(99,102,241,0.4)' : 'rgba(99,102,241,0.1)');
      glow.addColorStop(1, 'transparent');
      this.ctx.fillStyle = glow;
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.active ? 30 : 15, 0, Math.PI * 2);
      this.ctx.fill();

      // Core dot
      this.ctx.fillStyle = node.active ? '#6366f1' : '#4a4a6a';
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.active ? 6 : 4, 0, Math.PI * 2);
      this.ctx.fill();
    });

    requestAnimationFrame(() => this.animate());
  }
}
```

### 4.3 Orbital / Planetary Progression

```css
.orbital-system {
  position: relative;
  width: 600px;
  height: 600px;
  margin: 0 auto;
}

.orbit-ring {
  position: absolute;
  border: 1px solid rgba(99, 102, 241, 0.15);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.orbit-ring:nth-child(1) { width: 150px; height: 150px; }
.orbit-ring:nth-child(2) { width: 250px; height: 250px; }
.orbit-ring:nth-child(3) { width: 350px; height: 350px; }
.orbit-ring:nth-child(4) { width: 450px; height: 450px; }
.orbit-ring:nth-child(5) { width: 550px; height: 550px; }

.planet {
  position: absolute;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--planet-color, #6366f1);
  box-shadow: 0 0 20px var(--planet-color, #6366f1);
  top: 50%;
  left: 50%;
  transform-origin: 0 0;
  animation: orbit var(--orbit-duration, 10s) linear infinite;
}

@keyframes orbit {
  from {
    transform: rotate(var(--start-angle, 0deg))
               translateX(var(--orbit-radius))
               rotate(calc(-1 * var(--start-angle, 0deg)));
  }
  to {
    transform: rotate(calc(var(--start-angle, 0deg) + 360deg))
               translateX(var(--orbit-radius))
               rotate(calc(-1 * (var(--start-angle, 0deg) + 360deg)));
  }
}

/* Central "sun" = core topic */
.sun {
  position: absolute;
  width: 40px;
  height: 40px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, #f59e0b, #f97316);
  border-radius: 50%;
  box-shadow: 0 0 40px rgba(245, 158, 11, 0.5);
  animation: sunPulse 3s ease-in-out infinite;
}

@keyframes sunPulse {
  0%, 100% { box-shadow: 0 0 40px rgba(245, 158, 11, 0.5); }
  50%      { box-shadow: 0 0 60px rgba(245, 158, 11, 0.8); }
}
```

### 4.4 DNA Helix / Spiral Progression

```javascript
function createHelixTimeline(container, items) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', `0 0 400 ${items.length * 200}`);
  svg.style.width = '100%';

  items.forEach((item, i) => {
    const y = i * 200 + 100;
    const side = i % 2 === 0 ? -1 : 1;
    const x = 200 + side * 80 * Math.sin(i * 0.8);

    // Helix strand paths
    const strand1X = 200 + 60 * Math.sin(i * Math.PI / 2);
    const strand2X = 200 - 60 * Math.sin(i * Math.PI / 2);

    // Connection bar between strands
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', strand1X);
    line.setAttribute('y1', y);
    line.setAttribute('x2', strand2X);
    line.setAttribute('y2', y);
    line.setAttribute('stroke', `hsl(${240 + i * 15}, 70%, 60%)`);
    line.setAttribute('stroke-width', '2');
    line.setAttribute('opacity', '0.3');
    svg.appendChild(line);

    // Node on one strand
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', side > 0 ? strand1X : strand2X);
    circle.setAttribute('cy', y);
    circle.setAttribute('r', '8');
    circle.setAttribute('fill', `hsl(${240 + i * 15}, 70%, 60%)`);
    svg.appendChild(circle);
  });

  container.appendChild(svg);
}
```

**Key Design Philosophy for Timelines:**
- Use scroll-driven animations for progressive reveal
- Combine SVG paths with CSS animations for the "journey" feel
- Place content cards alongside geometric patterns
- Add subtle particle or glow effects for a futuristic atmosphere
- Make nodes interactive (hover reveals details)

---

## 5. Award-Winning Single-Page Web Experiences

### Notable Examples (Awwwards / SOTD Style)

| Site | Key Techniques | Why It's Impressive |
|------|---------------|-------------------|
| **Active Theory** | Kinetic typography, glitch transitions, real-time cursor reactions | Dark futuristic interface, scroll storytelling |
| **Glyphic** | Geometric animations on deep black, crisp typography | High-tech data visualization feel |
| **Vapi.ai** | Gradient-rich near-black bg, glowing code elements | Electric feel, scroll engagement |
| **Evervault** | Glowing technical diagrams, green accents on black | Security metaphor through design |
| **Claude on Mars** (Awwwards 2025) | 3D WebGL, immersive storytelling | Full immersive experience |
| **OCTANE MOUNTAIN** (Awwwards 2025) | Performance-driven animation | Award-winning interaction design |
| **QASE** | Navy + purple/blue glow, space-like feel | Futuristic SaaS landing |

### Common Patterns in Award-Winning Sites
1. **Dark themes with selective glow** -- neon accents against near-black
2. **Scroll storytelling** -- content unfolds cinematically
3. **Micro-interactions everywhere** -- cursor effects, hover states, transitions
4. **Performant animations** -- only transform/opacity, GPU-accelerated
5. **Typography as design element** -- oversized, animated, kinetic
6. **Bento grid layouts** -- modular card arrangements (2026 trend)
7. **Organic/soft shapes** -- moving away from sharp geometric grids
8. **Noise texture overlays** -- subtle grain for depth
9. **Gradient mesh backgrounds** -- multi-layered animated gradients
10. **Custom cursors** -- dot following, magnetic, reactive

**Key Resources:**
- [Awwwards: Best Single Page Websites](https://www.awwwards.com/websites/single-page/)
- [Awwwards: One Page Collection](https://www.awwwards.com/awwwards/collections/one-page/)
- [99designs: Futuristic Websites](https://99designs.com/inspiration/websites/futuristic)
- [FireArt: 20 Best Futuristic Websites](https://fireart.studio/blog/20-best-futuristic-website-examples-to-inspire-you/)

---

## 6. Three.js & WebGL Lightweight Effects

All examples below use Three.js from CDN -- no build tools needed.

### 6.1 Floating Particles / Orbs Background

```html
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<canvas id="bg-canvas"></canvas>

<script>
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({
  canvas: document.getElementById('bg-canvas'),
  alpha: true,
  antialias: true
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

// Particles
const geometry = new THREE.BufferGeometry();
const count = 500;
const positions = new Float32Array(count * 3);
const colors = new Float32Array(count * 3);

for (let i = 0; i < count * 3; i += 3) {
  positions[i]     = (Math.random() - 0.5) * 20;  // x
  positions[i + 1] = (Math.random() - 0.5) * 20;  // y
  positions[i + 2] = (Math.random() - 0.5) * 20;  // z

  colors[i]     = 0.4 + Math.random() * 0.2;  // r
  colors[i + 1] = 0.4 + Math.random() * 0.3;  // g
  colors[i + 2] = 0.8 + Math.random() * 0.2;  // b
}

geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

const material = new THREE.PointsMaterial({
  size: 0.08,
  vertexColors: true,
  transparent: true,
  opacity: 0.6,
  blending: THREE.AdditiveBlending,
  depthWrite: false
});

const particles = new THREE.Points(geometry, material);
scene.add(particles);

// Floating orbs (larger glowing spheres)
const orbGroup = new THREE.Group();
for (let i = 0; i < 5; i++) {
  const orbGeo = new THREE.SphereGeometry(0.3 + Math.random() * 0.4, 16, 16);
  const orbMat = new THREE.MeshBasicMaterial({
    color: new THREE.Color(`hsl(${220 + i * 30}, 70%, 60%)`),
    transparent: true,
    opacity: 0.15
  });
  const orb = new THREE.Mesh(orbGeo, orbMat);
  orb.position.set(
    (Math.random() - 0.5) * 8,
    (Math.random() - 0.5) * 8,
    (Math.random() - 0.5) * 5
  );
  orb.userData = {
    speed: 0.005 + Math.random() * 0.01,
    amplitude: 1 + Math.random() * 2,
    offset: Math.random() * Math.PI * 2
  };
  orbGroup.add(orb);
}
scene.add(orbGroup);

camera.position.z = 5;

// Mouse interaction
let mouseX = 0, mouseY = 0;
document.addEventListener('mousemove', (e) => {
  mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
  mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
});

function animate() {
  requestAnimationFrame(animate);

  const time = Date.now() * 0.001;

  // Slow rotation
  particles.rotation.y += 0.0005;
  particles.rotation.x += 0.0002;

  // Mouse-driven camera movement
  camera.position.x += (mouseX * 0.5 - camera.position.x) * 0.05;
  camera.position.y += (-mouseY * 0.5 - camera.position.y) * 0.05;
  camera.lookAt(scene.position);

  // Animate orbs
  orbGroup.children.forEach(orb => {
    const d = orb.userData;
    orb.position.y += Math.sin(time * d.speed * 10 + d.offset) * 0.003;
    orb.position.x += Math.cos(time * d.speed * 8 + d.offset) * 0.002;
  });

  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>

<style>
#bg-canvas {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
}
</style>
```

### 6.2 Fluid / Liquid Simulation (Lightweight WebGL)

Use the open-source WebGL Fluid Simulation by Pavel Dobryakov:

```html
<!-- Lightweight fluid sim: ~15KB -->
<script src="https://cdn.jsdelivr.net/gh/nicnl31/WebGL-Fluid-Simulation/script.js"></script>

<!-- Or embed the fluid sim from: https://paveldogreat.github.io/WebGL-Fluid-Simulation/ -->
```

Alternative: **Smokey Fluid Cursor** for a lighter touch:
```html
<script src="https://cdn.jsdelivr.net/npm/smokey-fluid-cursor/dist/smokey-fluid-cursor.min.js"></script>
<script>
  new SmokeyFluidCursor({
    canvas: document.getElementById('fluid-canvas'),
    colorPalette: ['#6366f1', '#8b5cf6', '#a855f7', '#06b6d4'],
    pressure: 0.3,
    curl: 20
  });
</script>
```

### 6.3 Noise/Distortion Shader (Inline GLSL)

```javascript
// Minimal noise background with raw WebGL (no Three.js dependency)
const canvas = document.getElementById('noise-canvas');
const gl = canvas.getContext('webgl');

const vertexShader = `
  attribute vec2 position;
  void main() {
    gl_Position = vec4(position, 0.0, 1.0);
  }
`;

const fragmentShader = `
  precision mediump float;
  uniform float time;
  uniform vec2 resolution;

  // Simplex noise
  vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
  vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

  float snoise(vec3 v) {
    const vec2 C = vec2(1.0/6.0, 1.0/3.0);
    const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
    vec3 i = floor(v + dot(v, C.yyy));
    vec3 x0 = v - i + dot(i, C.xxx);
    vec3 g = step(x0.yzx, x0.xyz);
    vec3 l = 1.0 - g;
    vec3 i1 = min(g.xyz, l.zxy);
    vec3 i2 = max(g.xyz, l.zxy);
    vec3 x1 = x0 - i1 + C.xxx;
    vec3 x2 = x0 - i2 + C.yyy;
    vec3 x3 = x0 - D.yyy;
    i = mod289(i);
    vec4 p = permute(permute(permute(
      i.z + vec4(0.0, i1.z, i2.z, 1.0))
      + i.y + vec4(0.0, i1.y, i2.y, 1.0))
      + i.x + vec4(0.0, i1.x, i2.x, 1.0));
    float n_ = 0.142857142857;
    vec3 ns = n_ * D.wyz - D.xzx;
    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
    vec4 x_ = floor(j * ns.z);
    vec4 y_ = floor(j - 7.0 * x_);
    vec4 x = x_ * ns.x + ns.yyyy;
    vec4 y = y_ * ns.x + ns.yyyy;
    vec4 h = 1.0 - abs(x) - abs(y);
    vec4 b0 = vec4(x.xy, y.xy);
    vec4 b1 = vec4(x.zw, y.zw);
    vec4 s0 = floor(b0)*2.0 + 1.0;
    vec4 s1 = floor(b1)*2.0 + 1.0;
    vec4 sh = -step(h, vec4(0.0));
    vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
    vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
    vec3 p0 = vec3(a0.xy, h.x);
    vec3 p1 = vec3(a0.zw, h.y);
    vec3 p2 = vec3(a1.xy, h.z);
    vec3 p3 = vec3(a1.zw, h.w);
    vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
    p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;
    vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
    m = m * m;
    return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
  }

  void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    float n = snoise(vec3(uv * 3.0, time * 0.2));

    vec3 color1 = vec3(0.06, 0.06, 0.18);   // deep blue
    vec3 color2 = vec3(0.25, 0.1, 0.4);     // purple
    vec3 color3 = vec3(0.02, 0.4, 0.5);     // teal

    vec3 color = mix(color1, color2, smoothstep(-0.5, 0.5, n));
    color = mix(color, color3, smoothstep(0.0, 0.8, n * sin(time * 0.1)));

    gl_FragColor = vec4(color, 1.0);
  }
`;

// WebGL setup boilerplate
function createShader(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  return shader;
}

const vs = createShader(gl, gl.VERTEX_SHADER, vertexShader);
const fs = createShader(gl, gl.FRAGMENT_SHADER, fragmentShader);

const program = gl.createProgram();
gl.attachShader(program, vs);
gl.attachShader(program, fs);
gl.linkProgram(program);
gl.useProgram(program);

const buffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);

const posAttr = gl.getAttribLocation(program, 'position');
gl.enableVertexAttribArray(posAttr);
gl.vertexAttribPointer(posAttr, 2, gl.FLOAT, false, 0, 0);

const timeLoc = gl.getUniformLocation(program, 'time');
const resLoc = gl.getUniformLocation(program, 'resolution');

function render(t) {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  gl.viewport(0, 0, canvas.width, canvas.height);
  gl.uniform1f(timeLoc, t * 0.001);
  gl.uniform2f(resLoc, canvas.width, canvas.height);
  gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  requestAnimationFrame(render);
}
requestAnimationFrame(render);
```

**Key Resources:**
- [Three.js Journey: Particles](https://threejs-journey.com/lessons/particles)
- [Codrops: Interactive Particles](https://tympanus.net/codrops/2019/01/17/interactive-particles-with-three-js/)
- [Codrops: Dreamy Particle Effect with GPGPU](https://tympanus.net/codrops/2024/12/19/crafting-a-dreamy-particle-effect-with-three-js-and-gpgpu/)
- [WebGL Fluid Simulation](https://paveldogreat.github.io/WebGL-Fluid-Simulation/)
- [CSS Script: Smokey Fluid Cursor](https://www.cssscript.com/smokey-fluid-cursor/)

---

## 7. Recommended Architecture for Single HTML File

### File Structure
```html
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vibe Coding Syllabus</title>

  <!-- Fonts from Google CDN -->
  <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">

  <!-- Three.js from CDN (optional, for WebGL effects) -->
  <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js" defer></script>

  <style>
    /* All CSS inline - using @property, scroll-driven animations, etc. */
    /* SVG filters defined in HTML body */
    /* Container queries for responsive components */
    /* View transitions for section switching */
    /* Aurora/gradient mesh backgrounds */
  </style>
</head>
<body>
  <!-- SVG Filters (hidden) -->
  <svg style="position:absolute;width:0;height:0">...</svg>

  <!-- Noise Overlay -->
  <svg class="noise-overlay">...</svg>

  <!-- Three.js Canvas (background) -->
  <canvas id="bg-canvas"></canvas>

  <!-- CSS Particles (no-JS fallback) -->
  <div class="particles">...</div>

  <!-- Main Content -->
  <main>
    <section class="hero">...</section>
    <section class="roadmap">
      <!-- SVG Journey Path -->
      <!-- Milestone Cards with scroll-driven animations -->
    </section>
    <section class="modules">...</section>
  </main>

  <script>
    // All JS inline
    // 1. IntersectionObserver for reveal animations
    // 2. Three.js particle background
    // 3. Magnetic cursor effects
    // 4. SVG path drawing on scroll
    // 5. 3D card tilt
    // 6. Horizontal scroll section logic
  </script>
</body>
</html>
```

### Performance Budget for Single File
- **CSS**: ~15-25KB (with all animations)
- **JS**: ~10-20KB (custom code) + ~150KB (Three.js from CDN, cached)
- **SVG filters/paths**: ~5-10KB
- **Total without Three.js**: ~30-55KB (excellent)
- **Total with Three.js CDN**: ~180-210KB (still good, CDN-cached)

### Key Performance Rules
1. Only animate `transform` and `opacity` (GPU-composited)
2. Use `will-change` sparingly on animated elements
3. Use `content-visibility: auto` on off-screen sections
4. Prefer CSS scroll-driven animations over JS scroll listeners
5. Use `requestAnimationFrame` for all JS animations
6. Add `@media (prefers-reduced-motion: reduce)` fallbacks
7. Lazy-initialize Three.js after first paint
8. Use `IntersectionObserver` instead of scroll events for reveals

---

## 8. Recommended Effect Stack for "Vibe Coding" Syllabus Page

### Tier 1: Must-Have (Pure CSS, High Impact)
- [x] Aurora gradient mesh background with @property animations
- [x] Glass morphism cards with backdrop-filter
- [x] Scroll-driven fade/slide reveals using `animation-timeline: view()`
- [x] Animated gradient border on key cards (conic-gradient + @property)
- [x] SVG noise texture overlay for depth
- [x] Staggered reveal animations with IntersectionObserver
- [x] Split-text character animations for headings

### Tier 2: Impressive (CSS + Light JS)
- [x] SVG journey path timeline that draws on scroll
- [x] 3D card tilt on hover (mouse-tracking)
- [x] Magnetic cursor on CTAs
- [x] Constellation/node network for milestone connections
- [x] Holographic/iridescent accents on premium elements
- [x] Horizontal scroll section for module overview

### Tier 3: Stunning (Three.js / WebGL)
- [x] Floating particle + orb background
- [x] Subtle noise shader background
- [x] Scroll-linked camera movement

### Color Palette Suggestion (Futuristic Dark Theme)
```css
:root {
  --bg-deep:    #0a0a1a;
  --bg-surface: #12122a;
  --accent-1:   #6366f1;  /* Indigo */
  --accent-2:   #8b5cf6;  /* Purple */
  --accent-3:   #06b6d4;  /* Cyan */
  --accent-4:   #ec4899;  /* Pink */
  --accent-5:   #f59e0b;  /* Amber (sparingly) */
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --glass-bg:   rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);
  --glow-indigo: 0 0 30px rgba(99, 102, 241, 0.3);
  --glow-cyan:   0 0 30px rgba(6, 182, 212, 0.3);
}
```

---

## Sources

### CSS Scroll-Driven Animations
- [MDN: CSS Scroll-Driven Animations](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations)
- [Chrome: Scroll-Driven Animations](https://developer.chrome.com/docs/css-ui/scroll-driven-animations)
- [CSS-Tricks: Bringing Back Parallax with Scroll-Driven CSS Animations](https://css-tricks.com/bringing-back-parallax-with-scroll-driven-css-animations/)
- [Scroll-Driven Animations Style Demos](https://scroll-driven-animations.style/)
- [Smashing Magazine: Introduction to CSS Scroll-Driven Animations](https://www.smashingmagazine.com/2024/12/introduction-css-scroll-driven-animations/)
- [Chrome: Scroll-Triggered Animations](https://developer.chrome.com/blog/scroll-triggered-animations)
- [FreeFrontend: 25 CSS Scroll-Driven Animations](https://freefrontend.com/css-scroll-driven/)

### CSS @property and Houdini
- [CSS-Tricks: Exploring @property and its Animating Powers](https://css-tricks.com/exploring-property-and-its-animating-powers/)
- [Smashing Magazine: Custom @property vs CSS Variable](https://www.smashingmagazine.com/2024/05/times-need-custom-property-instead-css-variable/)
- [web.dev: Smarter Custom Properties with Houdini](https://web.dev/articles/css-props-and-vals)
- [Egghead: Animate Custom Properties with @property](https://egghead.io/lessons/css-use-css-property-to-animate-and-transition-custom-properties)

### View Transitions API
- [Chrome: View Transitions (Smooth Transitions)](https://developer.chrome.com/docs/web-platform/view-transitions)
- [Chrome: View Transitions 2025 Update](https://developer.chrome.com/blog/view-transitions-in-2025)
- [MDN: View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API)
- [DebugBear: View Transitions SPA Without Framework](https://www.debugbear.com/blog/view-transitions-spa-without-framework)

### Container Queries
- [Caisy: CSS Container Queries in 2025](https://caisy.io/blog/css-container-queries)
- [Medium: CSS 2025 Container Queries in Real Projects](https://medium.com/@vyakymenko/css-2025-container-queries-and-style-queries-in-real-projects-c38af5a13aa2)

### Glass Morphism & Liquid Glass
- [FreeFrontend: CSS Liquid Glass](https://freefrontend.com/css-liquid-glass/)
- [Mitkov Systems: CSS Liquid Glass How-To](https://www.mitkov-systems.de/en/blog/css-liquid-glass-how-to)
- [WWDC 2025 Liquid Glass Resources](https://www.liquidglassresources.com/development/liquid-glass-effect-css-svg/)
- [Glass CSS Generator](https://css.glass/)

### Holographic & Chromatic Effects
- [CSS3.com: Holographic CSS Effect Guide](https://css3.com/how-to-get-the-holographic-css-effect-a-complete-guide/)
- [Robb Owen: CSS Blend Mode Shaders](https://robbowen.digital/wrote-about/css-blend-mode-shaders/)
- [GitHub: Liquid CSS - Chromatic Aberration](https://github.com/electrikmilk/liquid-css)

### Text Animations
- [FreeFrontend: 96 CSS Text Animations](https://freefrontend.com/css-text-animations/)
- [Codrops: 3D Scroll-Driven Text Animations](https://tympanus.net/codrops/2025/11/04/creating-3d-scroll-driven-text-animations-with-css-and-gsap/)
- [IK Agency: Kinetic Typography Guide 2026](https://www.ikagency.com/graphic-design-typography/kinetic-typography/)

### SVG Path & Timeline Animations
- [W3Schools: SVG Draw on Scroll](https://www.w3schools.com/howto/howto_js_scrolldrawing.asp)
- [Codrops: Animate SVG Shapes on Scroll](https://tympanus.net/codrops/2022/06/08/how-to-animate-svg-shapes-on-scroll/)
- [Dennis Kats: Path Scroll Animation with CSS](https://denniskats.dev/blog/path_scroll_animation)
- [GitHub: Scroll SVG Library](https://github.com/DanRDT/scroll-svg)

### Scroll Reveal & IntersectionObserver
- [FreeCodeCamp: Scroll Animations with IntersectionObserver](https://www.freecodecamp.org/news/scroll-animations-with-javascript-intersection-observer-api/)
- [CSS Script: Animate When Visible](https://www.cssscript.com/animate-when-visible/)
- [Liquid Light: Trigger Animations with IntersectionObserver](https://www.liquidlight.co.uk/blog/trigger-animations-with-intersection-observer-api/)

### Three.js & WebGL
- [Three.js Journey: Particles](https://threejs-journey.com/lessons/particles)
- [Codrops: Interactive Particles with Three.js](https://tympanus.net/codrops/2019/01/17/interactive-particles-with-three-js/)
- [Codrops: Dreamy Particle Effect with GPGPU](https://tympanus.net/codrops/2024/12/19/crafting-a-dreamy-particle-effect-with-three-js-and-gpgpu/)
- [WebGL Fluid Simulation](https://paveldogreat.github.io/WebGL-Fluid-Simulation/)
- [CSS Script: Smokey Fluid Cursor](https://www.cssscript.com/smokey-fluid-cursor/)
- [FreeFrontend: 146 Three.js Examples](https://freefrontend.com/three-js/)

### Award-Winning Sites & Inspiration
- [Awwwards: Best Single Page Websites](https://www.awwwards.com/websites/single-page/)
- [Awwwards: One Page Collection](https://www.awwwards.com/awwwards/collections/one-page/)
- [99designs: Futuristic Websites Inspiration](https://99designs.com/inspiration/websites/futuristic)
- [FireArt: 20 Best Futuristic Website Examples](https://fireart.studio/blog/20-best-futuristic-website-examples-to-inspire-you/)
- [Mycodeless: Best Neon Websites 2025](https://mycodelesswebsite.com/neon-websites/)

### 2026 CSS & Web Trends
- [LogRocket: CSS in 2026](https://blog.logrocket.com/css-in-2026/)
- [LogRocket: 8 Trends for Web Development 2026](https://blog.logrocket.com/8-trends-web-dev-2026/)
- [Nerdy.dev: 4 CSS Features for 2026](https://nerdy.dev/4-css-features-every-front-end-developer-should-know-in-2026)
- [Medium: Most Awaited CSS Features of 2026](https://medium.com/@onix_react/most-awaited-css-features-of-2026-886d76d666b2)
- [Webflow: 8 Web Design Trends 2026](https://webflow.com/blog/web-design-trends-2026)
- [Elementor: Web Design Trends 2026](https://elementor.com/blog/web-design-trends-2026/)

### Aurora / Gradient Effects
- [Dalton Walsh: Aurora CSS Background Effect](https://daltonwalsh.com/blog/aurora-css-background-effect/)
- [GitHub: Auroral - Animated Background Gradients](https://github.com/LunarLogic/auroral)
- [ibelick: Animated Gradient Borders with CSS](https://ibelick.com/blog/create-animated-gradient-borders-with-css)

### Parallax & Horizontal Scroll
- [CSS-Tricks: Parallax with Scroll-Driven Animations](https://css-tricks.com/bringing-back-parallax-with-scroll-driven-css-animations/)
- [Memberstack: 14 Best Parallax Scroll Examples 2025](https://www.memberstack.com/blog/14-of-the-best-parallax-scroll-examples-for-2025)
- [Prismic: 50 Interactive CSS Scroll Effects](https://prismic.io/blog/css-scroll-effects)

### 3D Effects & Card Tilt
- [Frontend.fyi: CSS 3D Perspective Animations](https://www.frontend.fyi/tutorials/css-3d-perspective-animations)
- [LetsBuildUI: 3D Hover Effect Using CSS Transforms](https://www.letsbuildui.dev/articles/a-3d-hover-effect-using-css-transforms/)
- [FreeFrontend: 65 CSS 3D Transforms](https://freefrontend.com/css-3d-transforms/)

### Constellation & Node Visualizations
- [CSS Script: Interactive Constellation Effect](https://www.cssscript.com/interactive-constellation-effectas/)
- [GitHub: Constellation - Animated Constellations](https://github.com/thenextweb/constellation)
- [Medium: Constellation Effect with HTML Canvas](https://fleker.medium.com/building-a-constellation-effect-for-the-web-with-html-canvas-fae3d4e0e7d2)
