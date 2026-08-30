---
version: alpha
name: "AI School Guardian"
description: "A Thai school-safety evidence console shaped by recorded footage, human review, and calm operational clarity."
colors:
  background: "#07111D"
  surface: "#0D1B2A"
  surfaceRaised: "#122437"
  border: "#24384C"
  primary: "#39D5C3"
  text: "#ECF4F8"
  muted: "#8FA5B8"
  warning: "#FFB454"
  danger: "#FF6470"
  info: "#6FA8FF"
typography:
  display:
    fontFamily: "IBM Plex Sans, Leelawadee UI, Noto Sans Thai, sans-serif"
  body:
    fontFamily: "IBM Plex Sans, Leelawadee UI, Noto Sans Thai, sans-serif"
  utility:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
rounded:
  DEFAULT: "0.625rem"
  sm: "0.375rem"
  md: "0.625rem"
  lg: "0.875rem"
spacing:
  control: "0.75rem"
  panel: "1.25rem"
  section: "1.5rem"
components:
  navigation: { }
  button: { }
  card: { }
  field: { }
  table: { }
  dialog: { }
---

# AI School Guardian Design System

## Overview

### Creative North Star

The interface should feel like a school incident-control desk assembled from a building plan, an evidence log, and a reliable video recorder. It is operational rather than cinematic: footage leads, timestamps stay precise, and safety status is legible at a glance.

### Product context and register

- **Audience and primary job:** Thai school staff review AI-generated candidates from recorded MP4, verify alerts, define monitored zones, and evaluate detection quality.
- **Target market(s) and evidence:** Thai school demonstration/project context, evidenced by Thai UI copy and the maintained project brief in `README.md`.
- **Locale(s) and language policy:** Thai-first explanatory copy with concise English technical vocabulary where it matches the model and evaluation domain.
- **Usage scene:** Desktop-first control room or school office, with occasional narrow-screen access on the same LAN; medium-to-high information density.
- **Register:** Product dashboard on every current route.
- **Memorable signature:** A restrained campus-map grid and cyan evidence rail frame key video/status surfaces.
- **Restraint:** Forms, event tables, review actions, and safety disclaimers remain quiet and conventional.
- **Anti-references:** No hacker-terminal neon, consumer surveillance theatrics, glossy crypto cards, or decorative threat imagery. The AI never visually claims certainty beyond its data.
- **Token ownership/runtime mapping:** Model B. Runtime CSS variables in `frontend/app/globals.css` and aliases in `frontend/tailwind.config.ts` are canonical; this file mirrors accepted values. Shared consumers are `AppShell`, `StatCard`, route cards, fields, tables, and dialogs.

## Colors

`background` is the application canvas; `surface` and `surfaceRaised` provide the only two content elevations. `primary` identifies navigation, focus, safe primary actions, and analyzed evidence. `warning` means review/caution, `danger` means alerts or irreversible actions, and `info` supports neutral system context. Text hierarchy uses `text` and `muted`; borders use `border`. Risk is never communicated by color alone.

## Typography

IBM Plex Sans carries headings and Latin UI; the Thai-capable Leelawadee UI/Noto Sans Thai fallbacks protect Thai legibility. IBM Plex Mono is reserved for timestamps, counts, model state, and evidence identifiers. Uppercase utility labels are short and Latin-only; Thai explanatory text uses normal sentence casing and generous line height.

## Layout

Desktop uses a 264px evidence-navigation rail and a fluid content canvas capped at 1600px. Pages follow a 20–28px outer gutter and 24px section rhythm. Dense evidence tables scroll horizontally on narrow screens; video cards preserve 16:9 geometry. Mobile converts the rail into a compact brand header plus horizontal route strip without hiding destinations.

## Elevation & Depth

Hierarchy comes from tonal surfaces, crisp 1px borders, and one soft shadow on floating navigation/dialog layers. Static data cards stay mostly flat. The campus-grid background is low contrast and must never reduce text or video legibility.

## Shapes

Controls and small chips use 6px; cards use 10px; major media/dialog surfaces use 14px. Camera/evidence corners may use clipped or bracket-like accents, while fields and tables stay rectangular and familiar.

## Components

### Foundational visual states

Interactive controls have visible hover, active, focus-visible, disabled, and busy states. Focus uses a high-contrast cyan ring. Loading occupies stable space; reduced motion removes transforms and stagger.

### Buttons and actions

Primary solid cyan is for one safe action per decision area. Neutral actions use outline/ghost treatments. Warning is used for recoverable review decisions; danger is reserved for deletion or alert severity. Busy labels retain button dimensions.

### Navigation and data display

The active route carries a cyan leading rail, filled surface, icon, and `aria-current`. Cards separate label, value, and context. Tables keep semantic markup, visible horizontal overflow, stable headers, and status badges with text.

### Forms and overlays

Fields use raised dark surfaces, visible labels, 44px target height, and app-owned validation. Native selects are accepted because the product does not require authored popup geometry. Destructive removal uses the shared app dialog rather than browser confirmation. Uploads keep a visible native picker and state accepted types before selection.

### Iconography

Use simple 1.7px rounded-stroke line icons at 18–20px. Icons support labels and never replace safety-critical wording.

### Motion

Use one 220ms entrance for page content and 150–200ms hover/state transitions. Motion communicates selection or state only. Under reduced motion, transforms and repeating ambient animation are disabled.

### Content and data visualization

Voice is concise, factual, and human-review-first. Counts use tabular numerals. Alerts say “candidate” or “potential risk” until a person confirms them. Charts use primary, info, warning, and danger in semantic order and retain text values.

## Do's and Don'ts

- **Do:** Let footage, timestamps, and review status carry the visual hierarchy.
- **Do:** Keep human-verification language visible wherever AI risk candidates appear.
- **Don't:** Use neon green everywhere or make the system resemble a fictional hacking dashboard.
- **Don't:** imply that an AI candidate is a confirmed weapon or confirmed harmful act.
