"""Chrome extension development team — Software Development."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="chrome_extension",
    description="Architects, builds, and prepares a Chrome extension for publication with manifest, UI, background scripts, and store listing.",
    category="Software Development",
    tags=["chrome extension", "browser", "javascript", "manifest v3", "web extension"],
    agents=[
        AgentSpec(
            name="Extension Architect",
            role="Chrome extension architecture and Manifest V3 specialist",
            instructions=(
                "You are a Chrome extension architect. For the given extension concept, produce: "
                "complete manifest.json (Manifest V3) with all permissions justified, "
                "architecture diagram showing communication between popup, background service worker, "
                "content scripts, and options page, "
                "storage strategy (chrome.storage.local vs sync vs session), "
                "message passing patterns between components, "
                "security considerations (CSP, XSS prevention, permission minimization), "
                "and cross-browser compatibility notes (Firefox, Edge)."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="UI Developer",
            role="Extension popup and options page UI specialist",
            instructions=(
                "You are a Chrome extension UI developer. Produce: "
                "popup HTML/CSS/JS scaffold (under 600x800px constraint), "
                "options page structure with settings persistence via chrome.storage, "
                "component design for the 3 main UI states (loading, active, error), "
                "keyboard navigation and accessibility considerations, "
                "dark mode support using prefers-color-scheme, "
                "and a visual design guide (colors, typography, spacing) aligned with Chrome UI patterns."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Background Script Developer",
            role="Service worker and browser API integration specialist",
            instructions=(
                "You are a Manifest V3 service worker specialist. Produce: "
                "service worker lifecycle management (install, activate, fetch), "
                "alarm-based scheduling for background tasks (chrome.alarms API), "
                "context menu integration (chrome.contextMenus), "
                "tab and window management patterns, "
                "external API call patterns with proper error handling and retry logic, "
                "badge and notification management, "
                "and performance optimizations (lazy loading modules, avoiding persistent service workers)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Store Publisher",
            role="Chrome Web Store submission and ASO specialist",
            instructions=(
                "You are a Chrome Web Store publishing specialist. Produce: "
                "store listing title (under 75 chars), "
                "short description (under 132 chars), "
                "long description (persuasive, keyword-rich, under 16000 chars), "
                "5 screenshot descriptions (1280x800 or 640x400) with content guidance, "
                "privacy policy template covering data collection, "
                "promotional tile text (440x280), "
                "category recommendation with rationale, "
                "and a pre-submission compliance checklist against Chrome Web Store policies."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "What permission model minimizes user friction while enabling core functionality?",
        "Minimal permissions (request only what's needed, earn trust gradually)",
        "Broad permissions upfront (better UX, fewer interruptions, but higher barrier to install)",
        "Optional permissions (core works without extras, advanced features unlock with permission grants)",
    ],
    expected_outputs=[
        "Complete manifest.json (Manifest V3)",
        "Extension architecture diagram",
        "Popup and options page scaffold",
        "Service worker implementation guide",
        "Chrome Web Store listing copy",
        "Privacy policy template",
        "Pre-submission compliance checklist",
        "Cross-browser compatibility notes",
    ],
))
