"""Mobile application scaffolding team — Software Development."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="mobile_app",
    description="Designs and scaffolds a mobile application with UX, architecture, API design, and native vs cross-platform debate.",
    category="Software Development",
    tags=["mobile", "ios", "android", "react-native", "flutter", "ux", "scaffold"],
    agents=[
        AgentSpec(
            name="UX Designer",
            role="Mobile UX and information architecture specialist",
            instructions=(
                "You are a senior mobile UX designer. Produce: "
                "user personas (2-3), core user journeys (3-5 with step-by-step flows), "
                "information architecture (screen inventory with navigation structure), "
                "wireframe descriptions for 5 key screens (describe layout, components, interactions), "
                "gesture and interaction patterns, "
                "onboarding flow design (max 3 screens), "
                "and mobile-specific UX considerations (thumb zones, haptics, offline states, permissions flow)."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Mobile Architect",
            role="Cross-platform or native architecture specialist",
            instructions=(
                "You are a senior mobile architect. Based on the app requirements, produce: "
                "platform choice justification (React Native vs Flutter vs native iOS+Android), "
                "app architecture pattern (MVVM, Clean Architecture, BLoC), "
                "state management approach, "
                "navigation library selection, "
                "offline-first data strategy (SQLite, Realm, AsyncStorage), "
                "push notification architecture, "
                "deep linking setup, "
                "and app performance optimization strategies (bundle splitting, image optimization, list virtualization)."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="API Designer",
            role="Mobile-optimized backend API specialist",
            instructions=(
                "You are an API designer specializing in mobile backends. Produce: "
                "mobile-optimized API endpoints (with pagination, field filtering, and response shaping), "
                "authentication flow (JWT + refresh tokens, biometric integration), "
                "real-time features design (WebSockets or SSE for chat/notifications), "
                "offline sync protocol (conflict resolution strategy), "
                "API versioning strategy, "
                "bandwidth optimization (compression, minimal payloads), "
                "and a BFF (Backend for Frontend) layer recommendation if needed."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="QA & Release Engineer",
            role="Mobile testing and app store release specialist",
            instructions=(
                "You are a mobile QA and release engineer. Produce: "
                "device test matrix (iOS versions, Android versions, screen sizes to cover), "
                "critical test scenarios (auth, payments, offline, background state, permissions), "
                "automated testing strategy (Detox, Maestro, or Appium — with justification), "
                "crash reporting and analytics setup (Sentry, Firebase Crashlytics), "
                "App Store and Google Play release checklist, "
                "beta testing workflow (TestFlight / Firebase App Distribution), "
                "and app store optimization (ASO) guidelines."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "Should this app be built natively or with a cross-platform framework?",
        "React Native (large ecosystem, web developers can contribute, OTA updates)",
        "Flutter (consistent UI, high performance, single codebase, growing ecosystem)",
        "Native Swift + Kotlin (best performance and platform integration, but double the work)",
    ],
    expected_outputs=[
        "User personas and core journey maps",
        "Screen inventory and navigation architecture",
        "Wireframe descriptions for 5 key screens",
        "Platform and framework decision document",
        "App architecture pattern and project structure",
        "Mobile-optimized API endpoint design",
        "Offline sync strategy",
        "Device test matrix and QA plan",
        "App store release checklist",
    ],
))
