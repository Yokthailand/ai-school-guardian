# UX Contract

## Product context

- Audience: Authorized Thai school staff and project evaluators.
- Primary jobs: Upload recorded MP4, run analysis, inspect candidates, review events, define zones, and measure model performance.
- Target market(s): Thai school project/demo environment.
- Active locales: Thai-first with stable English technical terms.
- Language/content register and native-review policy: Plain operational Thai; safety claims require human verification.
- Timezone/calendar policy: Browser-local display; video events retain recorded-video seconds separately.
- Accessibility target: WCAG 2.2 AA.

## Business-context sources

| Domain / scope | Authoritative source | Source type | Reviewed date |
|---|---|---|---|
| Recorded-video-only scope | `README.md` | Product brief | 2026-08-30 |
| Human-verification requirement | `README.md`, backend API/model behavior | Product/API contract | 2026-08-30 |
| Video/event lifecycle | Backend FastAPI routes and SQLAlchemy models | API/domain implementation | 2026-08-30 |
| Deletion | `DELETE /api/cameras/{id}` behavior | API contract | 2026-08-30 |

## Visual contract

- Project `DESIGN.md`: `DESIGN.md`
- Token ownership model: Existing runtime canonical (Model B).
- Runtime design-system/token source: `frontend/app/globals.css` and `frontend/tailwind.config.ts`.
- Mapping/export/adapters: CSS variables → Tailwind semantic aliases → shared components/routes.
- Token drift gate: DESIGN.md lint, strict premium audit, build, and browser inspection.
- Supported themes: Dark operational theme.

## Canonical UI Map

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
|---|---|---|---|---|
| Select/Listbox | Native select | This contract | native | keyboard + browser popup |
| Date | Native date input; platform-owned calendar accepted | This contract | native | locale + keyboard + browser popup |
| Form | Native semantic form + shared global field states | This contract | create / edit | browser validation flow |
| Scrollbar | `frontend/app/globals.css` | `DESIGN.md` | stable-gutter exception | computed/browser inspection |
| Dialog | `components/ConfirmDialog.tsx` | This contract | irreversible deletion | keyboard + focus browser check |
| CRUD | Route components + `lib/api.ts` | Backend API | return / stay | full-flow browser check |

## Component behavior

| Component | Default | Hover | Focus | Active | Disabled | Busy | Error |
|---|---|---|---|---|---|---|---|
| Button | Semantic intent | Raised/brightened | Cyan ring | Small translate | Dim, non-interactive | Stable label width | Inline/banner |
| Input | Raised surface | Stronger border | Cyan ring | n/a | Dim | n/a | Danger border + text |
| Table/list | Stable surface | Row tint | Visible target ring | Selected tint | n/a | Reserved loader | Persistent retry message |

## Dataset navigation

- Admin tables: Current backend-bounded render-all behavior; horizontal scroll on narrow screens.
- Exploratory lists: Render all current video sources because the project dataset is intentionally small.
- URL state: Existing filters remain route-local until the API adds paging/query restoration.
- Empty/no-results/error/loading treatment: Distinct stable messages; errors retain retry context.

## Flow ledger

| Operation | Trigger | Pending | Success destination | Success feedback | Failure recovery | Focus outcome | Source ref |
|---|---|---|---|---|---|---|---|
| Upload video/image | Upload / Analyze | Stable busy button | Stay in context | Inline status/result | Preserve selection and show error | Result/status heading | Backend upload APIs |
| Analyze video | Run AI analysis | Busy button + status panel | Stay on video | Result metrics | Persistent error, retry action | Analysis status | Analysis API |
| Delete video | Delete | Dialog action busy | Library | Updated list | Dialog remains with error | Next logical library item | Camera DELETE API |
| Review event | Confirm / False positive | Action disabled while request runs | Event log | Updated row | Persistent page error | Reviewed row action | Event review API |

## Navigation and responsive behavior

- Route document title policy: `{Page} — AI School Guardian`, managed by the application shell.
- Sidebar transformation: Persistent desktop rail; compact header and horizontally scrollable route strip below desktop.
- Responsive table strategy: Horizontal scrolling with visible styled scrollbar.
- Focus restoration: Dialog returns focus to its trigger; sticky UI must not obscure focused targets.

## Overlays and feedback

- Dialog primitive: `ConfirmDialog` with accessible title/description, Escape, cancel-first focus, and trigger restoration.
- Destructive confirmation levels: Camera deletion is irreversible and uses danger intent with explicit consequences.
- Alert/banner scope: Inline for workflow errors; page-level only for conditions affecting the full route.

## Async and resilience

- Mutation default: Pessimistic.
- Idempotency and duplicate-submit policy: Disable action while pending.
- Offline/read-stale/write behavior: Preserve visible content and show request failure.
- Retry behavior: Explicit retry by repeating the same user action.
- Stale-request policy: Ignore work after route/component cleanup when added to changed workflows.

## Validation

- Schema/validation layer: Backend authoritative; lightweight client constraints for file type and required fields.
- Trigger timing: Submit, then inline recovery.
- Server error mapping: Persistent form/page message; never raw browser dialogs.
- `noValidate`: Required on product forms; duplicate submit prevented; entered non-sensitive values preserved.

## Verification

- Required static commands: Next lint, TypeScript/build, strict premium audit, DESIGN.md lint.
- Browser matrix: Desktop, narrow viewport, keyboard focus, loading/empty/error where reachable, reduced motion.
- Accessibility checks: Semantic navigation/actions, visible focus, dialog keyboard behavior, contrast review.
- Canonical sibling flow: Dashboard video evidence cards compared with video library and analysis detail.
