# Rikat / Larapak CSS Engine - Lightweight In-House Utility-First CSS Framework
# Zero Node.js, Zero External Dependencies, 100% Native Python

import os
import re

class CSSEngine:
    """
    In-house JIT and Utility-First CSS Engine for Larapak & NgapakIn.
    Generates semantic design tokens, Tailwind-compatible utility classes,
    arbitrary value rules (e.g., w-[350px], bg-[#f58220]), and enterprise components.
    """

    def __init__(self, views_dir="resources/views", output_file="public/css/rikat.css"):
        self.views_dir = views_dir
        self.output_file = output_file

    def get_core_tokens(self) -> str:
        """Returns foundational design tokens, variables, reset and theme rules."""
        return """/* ==========================================================================
   Rikat CSS v1.0 - Utility-First CSS Engine for Larapak & NgapakIn
   Aesthetic: OLED Deep Slate, Machined Bezel, Amber Accent, High-End Minimalist
   Zero Node.js Dependency - 100% Native Pure CSS
   ========================================================================== */

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  /* Color Palette - Dark OLED (Default) */
  --bg-base: #06080d;
  --bg-surface: #0d121c;
  --bg-surface-elevated: #131a27;
  --bg-surface-hover: #192233;
  
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-highlight: rgba(255, 255, 255, 0.16);
  --border-accent: rgba(245, 130, 32, 0.4);
  
  --accent-primary: #f58220;
  --accent-hover: #e65100;
  --accent-glow: rgba(245, 130, 32, 0.2);
  --accent-cream: #f4e8d3;
  
  --color-success: #10b981;
  --color-danger: #ef4444;
  --color-warning: #f59e0b;
  --color-info: #3b82f6;

  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --text-accent: #fb923c;
  
  /* Typography & Geometry */
  --font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, monospace;
  
  --radius-none: 0px;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 24px;
  --radius-pill: 9999px;

  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.35);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.45);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.55);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.65);
}

/* Light Theme Mode */
.light, @media (prefers-color-scheme: light) {
  :root {
    --bg-base: #f8fafc;
    --bg-surface: #ffffff;
    --bg-surface-elevated: #f1f5f9;
    --bg-surface-hover: #e2e8f0;
    
    --border-subtle: rgba(0, 0, 0, 0.08);
    --border-highlight: rgba(0, 0, 0, 0.16);
    --border-accent: rgba(245, 130, 32, 0.4);
    
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
  }
}

/* Base Reset */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-family: var(--font-sans);
  background-color: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

body {
  min-height: 100vh;
}
"""

    def get_core_utilities(self) -> str:
        """Generates static full-scale utility classes compatible with Tailwind conventions."""
        css = ["/* ================= Utility Classes ================= */\n"]
        
        # Display
        displays = {
            "block": "display: block;",
            "inline-block": "display: inline-block;",
            "inline": "display: inline;",
            "flex": "display: flex;",
            "inline-flex": "display: inline-flex;",
            "grid": "display: grid;",
            "inline-grid": "display: inline-grid;",
            "hidden": "display: none;",
        }
        for cls, rule in displays.items():
            css.append(f".{cls} {{ {rule} }}")

        # Flexbox utilities
        flex_dirs = {
            "flex-row": "flex-direction: row;",
            "flex-row-reverse": "flex-direction: row-reverse;",
            "flex-col": "flex-direction: column;",
            "flex-col-reverse": "flex-direction: column-reverse;",
            "flex-wrap": "flex-wrap: wrap;",
            "flex-nowrap": "flex-wrap: nowrap;",
            "flex-1": "flex: 1 1 0%;",
            "flex-auto": "flex: 1 1 auto;",
            "flex-none": "flex: none;",
            "grow": "flex-grow: 1;",
            "grow-0": "flex-grow: 0;",
            "shrink": "flex-shrink: 1;",
            "shrink-0": "flex-shrink: 0;",
        }
        for cls, rule in flex_dirs.items():
            css.append(f".{cls} {{ {rule} }}")

        # Alignment & Justification
        align_items = {
            "items-start": "align-items: flex-start;",
            "items-center": "align-items: center;",
            "items-end": "align-items: flex-end;",
            "items-baseline": "align-items: baseline;",
            "items-stretch": "align-items: stretch;",
        }
        for cls, rule in align_items.items():
            css.append(f".{cls} {{ {rule} }}")

        justify_content = {
            "justify-start": "justify-content: flex-start;",
            "justify-center": "justify-content: center;",
            "justify-end": "justify-content: flex-end;",
            "justify-between": "justify-content: space-between;",
            "justify-around": "justify-content: space-around;",
            "justify-evenly": "justify-content: space-evenly;",
        }
        for cls, rule in justify_content.items():
            css.append(f".{cls} {{ {rule} }}")

        # Grid Column Utilities
        for i in range(1, 13):
            css.append(f".grid-cols-{i} {{ grid-template-columns: repeat({i}, minmax(0, 1fr)); }}")
            css.append(f".col-span-{i} {{ grid-column: span {i} / span {i}; }}")
        css.append(".col-span-full { grid-column: 1 / -1; }")

        # Spacing scales (4px standard base)
        # 0:0, 1:4px, 2:8px, 3:12px, 4:16px, 5:20px, 6:24px, 8:32px, 10:40px, 12:48px, 16:64px, 20:80px, 24:96px
        spacing_map = {
            "0": "0px",
            "1": "0.25rem",
            "2": "0.5rem",
            "3": "0.75rem",
            "4": "1rem",
            "5": "1.25rem",
            "6": "1.5rem",
            "8": "2rem",
            "10": "2.5rem",
            "12": "3rem",
            "16": "4rem",
            "20": "5rem",
            "24": "6rem"
        }

        # Gaps
        for k, v in spacing_map.items():
            css.append(f".gap-{k} {{ gap: {v}; }}")
            css.append(f".gap-x-{k} {{ column-gap: {v}; }}")
            css.append(f".gap-y-{k} {{ row-gap: {v}; }}")

        # Padding & Margins
        for k, v in spacing_map.items():
            css.append(f".p-{k} {{ padding: {v}; }}")
            css.append(f".px-{k} {{ padding-left: {v}; padding-right: {v}; }}")
            css.append(f".py-{k} {{ padding-top: {v}; padding-bottom: {v}; }}")
            css.append(f".pt-{k} {{ padding-top: {v}; }}")
            css.append(f".pb-{k} {{ padding-bottom: {v}; }}")
            css.append(f".pl-{k} {{ padding-left: {v}; }}")
            css.append(f".pr-{k} {{ padding-right: {v}; }}")

            css.append(f".m-{k} {{ margin: {v}; }}")
            css.append(f".mx-{k} {{ margin-left: {v}; margin-right: {v}; }}")
            css.append(f".my-{k} {{ margin-top: {v}; margin-bottom: {v}; }}")
            css.append(f".mt-{k} {{ margin-top: {v}; }}")
            css.append(f".mb-{k} {{ margin-bottom: {v}; }}")
            css.append(f".ml-{k} {{ margin-left: {v}; }}")
            css.append(f".mr-{k} {{ margin-right: {v}; }}")

        css.append(".mx-auto { margin-left: auto; margin-right: auto; }")
        css.append(".my-auto { margin-top: auto; margin-bottom: auto; }")
        css.append(".m-auto { margin: auto; }")

        # Sizing
        widths = {
            "w-full": "width: 100%;",
            "w-screen": "width: 100vw;",
            "w-auto": "width: auto;",
            "w-fit": "width: fit-content;",
            "w-1/2": "width: 50%;",
            "w-1/3": "width: 33.333333%;",
            "w-2/3": "width: 66.666667%;",
            "w-1/4": "width: 25%;",
            "w-3/4": "width: 75%;",
        }
        for cls, rule in widths.items():
            css.append(f".{cls} {{ {rule} }}")

        max_widths = {
            "max-w-xs": "max-width: 20rem;",
            "max-w-sm": "max-width: 24rem;",
            "max-w-md": "max-width: 28rem;",
            "max-w-lg": "max-width: 32rem;",
            "max-w-xl": "max-width: 36rem;",
            "max-w-2xl": "max-width: 42rem;",
            "max-w-3xl": "max-width: 48rem;",
            "max-w-4xl": "max-width: 56rem;",
            "max-w-5xl": "max-width: 64rem;",
            "max-w-6xl": "max-width: 72rem;",
            "max-w-7xl": "max-width: 80rem;",
            "max-w-full": "max-width: 100%;",
        }
        for cls, rule in max_widths.items():
            css.append(f".{cls} {{ {rule} }}")

        heights = {
            "h-full": "height: 100%;",
            "h-screen": "height: 100vh;",
            "h-auto": "height: auto;",
            "min-h-screen": "min-height: 100vh;",
            "min-h-full": "min-height: 100%;",
        }
        for cls, rule in heights.items():
            css.append(f".{cls} {{ {rule} }}")

        # Typography
        type_sizes = {
            "text-xs": "font-size: 0.75rem; line-height: 1rem;",
            "text-sm": "font-size: 0.875rem; line-height: 1.25rem;",
            "text-base": "font-size: 1rem; line-height: 1.5rem;",
            "text-lg": "font-size: 1.125rem; line-height: 1.75rem;",
            "text-xl": "font-size: 1.25rem; line-height: 1.75rem;",
            "text-2xl": "font-size: 1.5rem; line-height: 2rem;",
            "text-3xl": "font-size: 1.875rem; line-height: 2.25rem;",
            "text-4xl": "font-size: 2.25rem; line-height: 2.5rem;",
            "text-5xl": "font-size: 3rem; line-height: 1;",
        }
        for cls, rule in type_sizes.items():
            css.append(f".{cls} {{ {rule} }}")

        font_weights = {
            "font-light": "font-weight: 300;",
            "font-normal": "font-weight: 400;",
            "font-medium": "font-weight: 500;",
            "font-semibold": "font-weight: 600;",
            "font-bold": "font-weight: 700;",
            "font-extrabold": "font-weight: 800;",
        }
        for cls, rule in font_weights.items():
            css.append(f".{cls} {{ {rule} }}")

        text_align = {
            "text-left": "text-align: left;",
            "text-center": "text-align: center;",
            "text-right": "text-align: right;",
            "text-justify": "text-align: justify;",
            "truncate": "overflow: hidden; text-overflow: ellipsis; white-space: nowrap;",
        }
        for cls, rule in text_align.items():
            css.append(f".{cls} {{ {rule} }}")

        # Semantic Colors
        colors = {
            "bg-base": "background-color: var(--bg-base);",
            "bg-surface": "background-color: var(--bg-surface);",
            "bg-surface-elevated": "background-color: var(--bg-surface-elevated);",
            "bg-surface-hover": "background-color: var(--bg-surface-hover);",
            "bg-accent": "background-color: var(--accent-primary);",
            "bg-transparent": "background-color: transparent;",
            "bg-success": "background-color: var(--color-success);",
            "bg-danger": "background-color: var(--color-danger);",
            "bg-warning": "background-color: var(--color-warning);",
            "bg-info": "background-color: var(--color-info);",

            "text-primary": "color: var(--text-primary);",
            "text-secondary": "color: var(--text-secondary);",
            "text-muted": "color: var(--text-muted);",
            "text-accent": "color: var(--accent-primary);",
            "text-success": "color: var(--color-success);",
            "text-danger": "color: var(--color-danger);",
            "text-warning": "color: var(--color-warning);",
            "text-info": "color: var(--color-info);",

            "border-subtle": "border-color: var(--border-subtle);",
            "border-highlight": "border-color: var(--border-highlight);",
            "border-accent": "border-color: var(--border-accent);",
            "border-success": "border-color: var(--color-success);",
            "border-danger": "border-color: var(--color-danger);",
        }
        for cls, rule in colors.items():
            css.append(f".{cls} {{ {rule} }}")

        # Border & Radius
        borders = {
            "border": "border-width: 1px; border-style: solid;",
            "border-0": "border-width: 0px;",
            "border-t": "border-top-width: 1px; border-top-style: solid;",
            "border-b": "border-bottom-width: 1px; border-bottom-style: solid;",
            "border-l": "border-left-width: 1px; border-left-style: solid;",
            "border-r": "border-right-width: 1px; border-right-style: solid;",
            
            "rounded-none": "border-radius: var(--radius-none);",
            "rounded-sm": "border-radius: var(--radius-sm);",
            "rounded-md": "border-radius: var(--radius-md);",
            "rounded-lg": "border-radius: var(--radius-lg);",
            "rounded-xl": "border-radius: var(--radius-xl);",
            "rounded-2xl": "border-radius: var(--radius-2xl);",
            "rounded-pill": "border-radius: var(--radius-pill);",
            "rounded-full": "border-radius: 9999px;",
        }
        for cls, rule in borders.items():
            css.append(f".{cls} {{ {rule} }}")

        # Shadows & Transitions
        effects = {
            "shadow-sm": "box-shadow: var(--shadow-sm);",
            "shadow-md": "box-shadow: var(--shadow-md);",
            "shadow-lg": "box-shadow: var(--shadow-lg);",
            "shadow-xl": "box-shadow: var(--shadow-xl);",
            "shadow-none": "box-shadow: none;",
            
            "cursor-pointer": "cursor: pointer;",
            "cursor-not-allowed": "cursor: not-allowed;",
            "select-none": "user-select: none;",
            
            "transition": "transition: all 0.2s ease;",
            "transition-all": "transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);",
            "transition-colors": "transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;",
            "transition-transform": "transition: transform 0.2s ease;",
        }
        for cls, rule in effects.items():
            css.append(f".{cls} {{ {rule} }}")

        # Container
        css.append("""
.container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;
  padding-right: 1rem;
}
@media (min-width: 640px) { .container { max-width: 640px; } }
@media (min-width: 768px) { .container { max-width: 768px; } }
@media (min-width: 1024px) { .container { max-width: 1024px; } }
@media (min-width: 1280px) { .container { max-width: 1280px; } }
""")

        return "\n".join(css)

    def get_smart_components(self) -> str:
        """Generates built-in, cohesive UI components styled for Larapak & Rikat CSS."""
        return """/* ================= Smart Components ================= */

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-family: var(--font-sans);
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.625rem 1.25rem;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  text-decoration: none;
  line-height: 1.25;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  user-select: none;
}
.btn:hover {
  transform: translateY(-1px);
}
.btn:active {
  transform: translateY(0);
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-primary {
  background-color: var(--accent-primary);
  color: #ffffff;
  border-color: var(--accent-primary);
  box-shadow: 0 2px 8px var(--accent-glow);
}
.btn-primary:hover {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
  box-shadow: 0 4px 12px var(--accent-glow);
}

.btn-secondary {
  background-color: var(--bg-surface-elevated);
  color: var(--text-primary);
  border-color: var(--border-subtle);
}
.btn-secondary:hover {
  background-color: var(--bg-surface-hover);
  border-color: var(--border-highlight);
}

.btn-outline {
  background-color: transparent;
  color: var(--accent-primary);
  border-color: var(--accent-primary);
}
.btn-outline:hover {
  background-color: var(--accent-primary);
  color: #ffffff;
}

.btn-danger {
  background-color: var(--color-danger);
  color: #ffffff;
}
.btn-danger:hover {
  filter: brightness(0.9);
}

.btn-sm {
  font-size: 0.75rem;
  padding: 0.4rem 0.8rem;
  border-radius: var(--radius-sm);
}
.btn-lg {
  font-size: 1rem;
  padding: 0.85rem 1.75rem;
  border-radius: var(--radius-lg);
}

/* Cards */
.card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: border-color 0.2s ease, transform 0.2s ease;
}
.card-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
  font-weight: 600;
  color: var(--text-primary);
}
.card-body {
  padding: 1.5rem;
  color: var(--text-secondary);
}
.card-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-subtle);
  background-color: var(--bg-surface-elevated);
}

/* Form Controls */
.input {
  width: 100%;
  font-family: var(--font-sans);
  font-size: 0.875rem;
  background-color: var(--bg-base);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 0.625rem 0.875rem;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.select, .textarea {
  width: 100%;
  font-family: var(--font-sans);
  font-size: 0.875rem;
  background-color: var(--bg-base);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 0.625rem 0.875rem;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.input:focus, .select:focus, .textarea:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-glow);
}
.input::placeholder, .textarea::placeholder {
  color: var(--text-muted);
}

/* Tables */
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  text-align: left;
}
.table th {
  padding: 0.75rem 1rem;
  font-weight: 600;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-subtle);
  text-transform: uppercase;
  font-size: 0.7rem;
  letter-spacing: 0.05em;
}
.table td {
  padding: 0.85rem 1rem;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-subtle);
}
.table-hover tbody tr:hover {
  background-color: var(--bg-surface-hover);
}
.table-striped tbody tr:nth-child(even) {
  background-color: rgba(255, 255, 255, 0.02);
}

/* Badges */
.badge {
  display: inline-flex;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border-subtle);
  background-color: var(--bg-surface-elevated);
  color: var(--text-secondary);
}
.badge-accent {
  background-color: var(--accent-glow);
  color: var(--accent-primary);
  border-color: var(--border-accent);
}
.badge-success {
  background-color: rgba(16, 185, 129, 0.15);
  color: var(--color-success);
  border-color: rgba(16, 185, 129, 0.3);
}
.badge-danger {
  background-color: rgba(239, 68, 68, 0.15);
  color: var(--color-danger);
  border-color: rgba(239, 68, 68, 0.3);
}

/* Alerts */
.alert {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  background-color: var(--bg-surface);
  font-size: 0.875rem;
  margin-bottom: 1rem;
}
.alert-info {
  border-color: rgba(59, 130, 246, 0.3);
  background-color: rgba(59, 130, 246, 0.08);
  color: #93c5fd;
}
.alert-success {
  border-color: rgba(16, 185, 129, 0.3);
  background-color: rgba(16, 185, 129, 0.08);
  color: #6ee7b7;
}
.alert-danger {
  border-color: rgba(239, 68, 68, 0.3);
  background-color: rgba(239, 68, 68, 0.08);
  color: #fca5a5;
}
"""

    def scan_arbitrary_classes(self) -> str:
        """
        Scans views (.nview) and extracts arbitrary value classes like:
        w-[320px], h-[50px], bg-[#f58220], text-[#ff0000], p-[15px], m-[10px],
        and state variants like hover:bg-accent, md:flex, etc.
        """
        if not os.path.isdir(self.views_dir):
            return ""

        classes_found = set()
        class_regex = re.compile(r'class=["\']([^"\']+)["\']')

        for root, _, files in os.walk(self.views_dir):
            for file in files:
                if file.endswith((".nview", ".html")):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                        matches = class_regex.findall(content)
                        for m in matches:
                            for c in m.split():
                                classes_found.add(c.strip())
                    except Exception:
                        pass

        generated_rules = []

        # Arbitrary Values generator
        # e.g., w-[350px], max-w-[500px], h-[100px], bg-[#abc], text-[#fff], p-[20px], m-[12px]
        for c in sorted(classes_found):
            # Escaped selector for CSS (e.g. w-\[350px\])
            escaped = c.replace("[", r"\[").replace("]", r"\]").replace("#", r"\#").replace(":", r"\:")

            # 1. Width arbitrary: w-[...]
            m_w = re.match(r'^w-\[(.+)\]$', c)
            if m_w:
                generated_rules.append(f".{escaped} {{ width: {m_w.group(1)}; }}")
                continue

            # 2. Max Width arbitrary: max-w-[...]
            m_mw = re.match(r'^max-w-\[(.+)\]$', c)
            if m_mw:
                generated_rules.append(f".{escaped} {{ max-width: {m_mw.group(1)}; }}")
                continue

            # 3. Height arbitrary: h-[...]
            m_h = re.match(r'^h-\[(.+)\]$', c)
            if m_h:
                generated_rules.append(f".{escaped} {{ height: {m_h.group(1)}; }}")
                continue

            # 4. Background color arbitrary: bg-[#...]
            m_bg = re.match(r'^bg-\[(.+)\]$', c)
            if m_bg:
                generated_rules.append(f".{escaped} {{ background-color: {m_bg.group(1)}; }}")
                continue

            # 5. Font size arbitrary: text-[18px], text-[1.2rem], text-[14pt]
            m_txtsize = re.match(r'^text-\[(.+px|.+rem|.+em|.+%|.+pt)\]$', c)
            if m_txtsize:
                generated_rules.append(f".{escaped} {{ font-size: {m_txtsize.group(1)}; }}")
                continue

            # 6. Text color arbitrary: text-[#...], text-[rgb(...)]
            m_txt = re.match(r'^text-\[(.+)\]$', c)
            if m_txt:
                generated_rules.append(f".{escaped} {{ color: {m_txt.group(1)}; }}")
                continue

            # 6. Padding arbitrary: p-[...], px-[...], py-[...]
            m_p = re.match(r'^p-\[(.+)\]$', c)
            if m_p:
                generated_rules.append(f".{escaped} {{ padding: {m_p.group(1)}; }}")
                continue
            m_px = re.match(r'^px-\[(.+)\]$', c)
            if m_px:
                generated_rules.append(f".{escaped} {{ padding-left: {m_px.group(1)}; padding-right: {m_px.group(1)}; }}")
                continue
            m_py = re.match(r'^py-\[(.+)\]$', c)
            if m_py:
                generated_rules.append(f".{escaped} {{ padding-top: {m_py.group(1)}; padding-bottom: {m_py.group(1)}; }}")
                continue

            # 7. Margin arbitrary: m-[...], mx-[...], my-[...], mt-[...], mb-[...]
            m_m = re.match(r'^m-\[(.+)\]$', c)
            if m_m:
                generated_rules.append(f".{escaped} {{ margin: {m_m.group(1)}; }}")
                continue
            m_mx = re.match(r'^mx-\[(.+)\]$', c)
            if m_mx:
                generated_rules.append(f".{escaped} {{ margin-left: {m_mx.group(1)}; margin-right: {m_mx.group(1)}; }}")
                continue
            m_my = re.match(r'^my-\[(.+)\]$', c)
            if m_my:
                generated_rules.append(f".{escaped} {{ margin-top: {m_my.group(1)}; margin-bottom: {m_my.group(1)}; }}")
                continue
            m_mt = re.match(r'^mt-\[(.+)\]$', c)
            if m_mt:
                generated_rules.append(f".{escaped} {{ margin-top: {m_mt.group(1)}; }}")
                continue
            m_mb = re.match(r'^mb-\[(.+)\]$', c)
            if m_mb:
                generated_rules.append(f".{escaped} {{ margin-bottom: {m_mb.group(1)}; }}")
                continue

            # 8. Gap, Radius & Z-Index arbitrary
            m_gap = re.match(r'^gap-\[(.+)\]$', c)
            if m_gap:
                generated_rules.append(f".{escaped} {{ gap: {m_gap.group(1)}; }}")
                continue
            m_rnd = re.match(r'^rounded-\[(.+)\]$', c)
            if m_rnd:
                generated_rules.append(f".{escaped} {{ border-radius: {m_rnd.group(1)}; }}")
                continue
            m_z = re.match(r'^z-\[(.+)\]$', c)
            if m_z:
                generated_rules.append(f".{escaped} {{ z-index: {m_z.group(1)}; }}")
                continue

            # 9. Hover variant: hover:cls
            if c.startswith("hover:"):
                base_cls = c[6:]
                # e.g., hover:bg-accent, hover:text-white, hover:opacity-80
                if base_cls == "bg-accent":
                    generated_rules.append(f".{escaped}:hover {{ background-color: var(--accent-primary); }}")
                elif base_cls == "bg-surface-elevated":
                    generated_rules.append(f".{escaped}:hover {{ background-color: var(--bg-surface-elevated); }}")
                elif base_cls == "bg-surface-hover":
                    generated_rules.append(f".{escaped}:hover {{ background-color: var(--bg-surface-hover); }}")
                elif base_cls == "text-accent":
                    generated_rules.append(f".{escaped}:hover {{ color: var(--accent-primary); }}")
                elif base_cls == "text-primary":
                    generated_rules.append(f".{escaped}:hover {{ color: var(--text-primary); }}")
                elif base_cls == "underline":
                    generated_rules.append(f".{escaped}:hover {{ text-decoration: underline; }}")

            # 11. Responsive variants: sm:, md:, lg:, xl:
            breakpoints = {
                "sm:": "640px",
                "md:": "768px",
                "lg:": "1024px",
                "xl:": "1280px"
            }
            for bp_prefix, min_w in breakpoints.items():
                if c.startswith(bp_prefix):
                    base_cls = c[len(bp_prefix):]
                    rule = None
                    if base_cls == "flex": rule = "display: flex;"
                    elif base_cls == "grid": rule = "display: grid;"
                    elif base_cls == "hidden": rule = "display: none;"
                    elif base_cls == "block": rule = "display: block;"
                    elif base_cls == "inline-flex": rule = "display: inline-flex;"
                    elif base_cls.startswith("grid-cols-"):
                        cols = base_cls.split("-")[-1]
                        rule = f"grid-template-columns: repeat({cols}, minmax(0, 1fr));"
                    elif base_cls == "w-full": rule = "width: 100%;"
                    elif base_cls == "w-auto": rule = "width: auto;"
                    elif base_cls.startswith("p-"):
                        p_val = base_cls.split("-")[-1]
                        rule = f"padding: {p_val}rem;" if p_val.isdigit() else None

                    if rule:
                        generated_rules.append(f"@media (min-width: {min_w}) {{ .{escaped} {{ {rule} }} }}")

        if generated_rules:
            return "/* ================= JIT Arbitrary & Scanned Rules ================= */\n" + "\n".join(generated_rules) + "\n"
        return ""

    def compile(self) -> str:
        """Assembles and compiles the full Rikat / Larapak CSS file."""
        tokens = self.get_core_tokens()
        utilities = self.get_core_utilities()
        components = self.get_smart_components()
        jit_rules = self.scan_arbitrary_classes()

        full_css = f"{tokens}\n{utilities}\n{components}\n{jit_rules}"
        
        # Ensure output directory exists
        out_dir = os.path.dirname(self.output_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(full_css)

        # Also write alias larapak.css so both names work interchangeably!
        alias_file = os.path.join(out_dir, "larapak.css") if out_dir else "larapak.css"
        with open(alias_file, "w", encoding="utf-8") as f:
            f.write(full_css)

        return full_css

def compile_rikat_css(views_dir="resources/views", output_file="public/css/rikat.css") -> str:
    """Convenience helper to run CSSEngine compile."""
    engine = CSSEngine(views_dir=views_dir, output_file=output_file)
    return engine.compile()

