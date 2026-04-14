# Design System Strategy: The Curated Atelier

## 1. Overview & Creative North Star
The "Creative North Star" for this design system is **The Digital Atelier**. Much like a high-end physical boutique, the digital experience must prioritize negative space, architectural silhouettes, and a sense of "quiet luxury." We are moving away from the loud, cluttered aesthetics of mass-market e-commerce in favor of a bespoke, editorial approach.

This system breaks the "template" look by utilizing **Intentional Asymmetry**. Rather than a rigid 12-column grid that feels mechanical, we utilize "breathing room" offsets where product imagery might bleed off-center, paired with high-contrast typography scales. The goal is to make every page feel like a spread from a premium fashion monograph, where the whitespace is as important as the content itself.

## 2. Colors & Tonal Depth
Our palette is rooted in a sophisticated monochrome base with a "Muted Ochre" (Secondary) accent that mimics the warmth of gold without the cliché of high-gloss metallics.

### The "No-Line" Rule
To maintain a premium, seamless feel, **1px solid borders are strictly prohibited for sectioning.** Do not use lines to separate the header from the hero, or products from the footer. Boundaries must be defined solely through:
- **Background Shifts:** Use `surface-container-low` (#f2f4f4) sections sitting atop a `background` (#f9f9f9) base.
- **Tonal Transitions:** Creating soft zones of focus using subtle shifts in the neutral scale.

### Surface Hierarchy & Nesting
Treat the UI as a physical stack of fine paper.
- **Layer 0 (Base):** `surface` (#f9f9f9)
- **Layer 1 (Cards/Floating Elements):** `surface-container-lowest` (#ffffff) to provide a crisp, clean lift.
- **Layer 2 (In-set Details):** `surface-container-high` (#e4e9ea) for decorative accents or secondary information.

### The "Glass & Signature" Rule
For floating navigation or quick-view modals, use **Glassmorphism**. Apply `surface` at 80% opacity with a `24px` backdrop-blur. This ensures the high-quality lifestyle photography bleeds through the UI, making the interface feel integrated with the brand's visual story. For main CTAs, apply a subtle linear gradient from `primary` (#5f5e5e) to `primary-dim` (#535252) to give the buttons a tactile, "weighted" feel.

## 3. Typography
The typography is a dialogue between the heritage-rich **Noto Serif** (reflecting the HMY logo) and the precision-engineered **Manrope**.

*   **Display & Headlines (Noto Serif):** These are our "editorial" voices. Use `display-lg` (3.5rem) for hero statements with tight letter-spacing (-0.02em) to evoke high-fashion mastheads.
*   **Titles & Body (Manrope):** The "functional" voice. `body-lg` (1rem) is the workhorse for product descriptions, ensuring maximum legibility.
*   **Labels (Manrope):** Small-caps or increased letter-spacing (0.05em) should be applied to `label-md` to denote luxury "tags" or metadata.

The contrast between the sharp serifs and the geometric sans-serif creates a hierarchy of "Expression" vs. "Information."

## 4. Elevation & Depth
In this system, depth is felt, not seen. We reject the heavy "drop shadow" of the 2010s.

*   **The Layering Principle:** Use the color tokens to create a "Soft Lift." A `surface-container-lowest` card placed on a `surface-container-low` background provides enough contrast to imply depth without a single pixel of shadow.
*   **Ambient Shadows:** Where a floating effect is vital (e.g., a cart drawer), use an "Ambient Shadow": `0px 20px 40px rgba(45, 52, 53, 0.06)`. The tint uses the `on-surface` color (#2d3435) at a very low opacity to mimic natural light.
*   **The "Ghost Border" Fallback:** If a border is required for accessibility, use the `outline-variant` (#adb3b4) at **15% opacity**. It should be a suggestion of a line, not a boundary.
*   **The Zero-Radius Rule:** In alignment with the brand's sophisticated architecture, the **Roundedness Scale is 0px across all tokens.** Sharp corners convey authority, precision, and a high-end "tailored" finish.

## 5. Components

### Buttons
*   **Primary:** Solid `primary` (#5f5e5e) background, `on-primary` text. No border. Rectangular (0px radius).
*   **Secondary:** `surface` background with a "Ghost Border" (15% `outline-variant`).
*   **Tertiary:** Text-only in `primary` with a 2px underline that appears on hover, utilizing the Spacing Scale for padding.

### Cards & Product Grids
**Forbid the use of divider lines.** Product cards should sit on the `surface` background. Use vertical whitespace (e.g., 48px or 64px) to separate rows. Product titles should use `title-md` (Manrope) and prices should use `title-sm` to maintain a clean, uncluttered grid.

### Input Fields
Text inputs use a bottom-border only (`outline-variant` at 40% opacity). When focused, the border transitions to `secondary` (Muted Gold #745b3b). This mimics the look of a high-end guest book or a luxury order form.

### Signature Component: The "Lookbook Masonry"
Instead of standard squares, use a masonry layout for lifestyle categories. Mix portrait (2:3) and landscape (3:2) aspect ratios to break the repetition and encourage "visual discovery."

## 6. Do's and Don'ts

### Do:
*   **Use Generous Whitespace:** If you think there is enough space, add 16px more. Whitespace is a luxury commodity in this design system.
*   **Lead with Imagery:** The UI exists only to frame the photography. Ensure the `background` (#f9f9f9) never competes with the product colors.
*   **Maintain Sharpness:** Ensure all icons and edges are pixel-perfect and strictly 0px radius.

### Don't:
*   **Don't use "Pure Black":** Use `on-surface` (#2d3435) for text to maintain a softer, more editorial look.
*   **Don't use Dividers:** Avoid horizontal rules (`<hr>`). Use background color steps (`surface` to `surface-container-low`) to define new sections.
*   **Don't Over-animate:** Transitions should be slow and "weighted" (e.g., 400ms ease-out). Rapid, bouncy animations cheapen the premium feel.