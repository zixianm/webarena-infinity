# Task Design Rationale

## Overview

24 evaluation tasks (8 easy, 8 medium, 8 hard) for testing browser-use agents on the GitLab organization management web app. Each task is paired with a Python verifier that checks `AppState` via `GET /api/state`.

## Design Principles

1. **Natural language instructions** — phrased as a typical user would say them, without revealing internal implementation details.
2. **Trick tasks are allowed** — as long as they reflect realistic user scenarios (e.g., M8 requires understanding share direction).
3. **Workflow coverage** — tasks collectively cover every major workflow in the application.
4. **Difficulty calibration** — based on step count, navigation depth, implicit constraints, and prerequisite knowledge.

## Difficulty Criteria

| Level | Steps | Navigation | Constraints | Description |
|-------|-------|------------|-------------|-------------|
| **Easy** | 1–3 | Direct sidebar link → single page/tab | None | Single-action operations with obvious navigation |
| **Medium** | 3–5 | Navigate to specific sub-entity or nested tab | May require knowing entity relationships | Operations on specific entities requiring targeted navigation |
| **Hard** | 5+ | Deep nesting, cross-page, or cross-org | Multi-step workflows, custom UI components, implicit rules | Either multi-step across pages OR single operations with deep implicit constraints |

### Hard Task Split (50/50)

Hard tasks are evenly split between two categories:

- **Multi-step (H1–H4)**: Require completing two distinct operations in sequence, often on different pages.
- **Deep-constraint (H5–H8)**: A single logical operation that is challenging due to deep navigation, multiple interacting form controls, cross-organization scope, or custom UI components (date pickers, comma-separated inputs).

## Task Definitions

### Easy (E1–E8)

| ID | Instruction | Workflow | Why Easy |
|----|-------------|----------|----------|
| E1 | Create a new group called 'DevOps Team' with public visibility | Group creation | Sidebar → Groups → New group → fill 2 fields → submit |
| E2 | Delete the project 'legacy-monolith' | Project deletion | Navigate to project → Settings → Delete → confirm |
| E3 | Change your bio to 'Full-stack developer with 10 years of experience' | Profile edit | Sidebar → Profile → edit text field → save |
| E4 | Add 'alex.backup@gmail.com' as a secondary email address to your account | Email management | Profile → Emails tab → type email → Add |
| E5 | Turn off two-factor authentication on your account | Account settings | Profile → Account tab → toggle switch |
| E6 | Unarchive the 'Archived Projects' group | Group archive toggle | Find archived group → Settings → Unarchive |
| E7 | Remove your secondary email 'alex.personal@email.com' | Email management | Profile → Emails tab → remove button |
| E8 | Set your current status message to 'On vacation' and mark yourself as busy | Profile status | Profile → edit status fields → save |

### Medium (M1–M8)

| ID | Instruction | Workflow | Why Medium |
|----|-------------|----------|------------|
| M1 | Create a new project called 'monitoring-service' in the 'Observability' group | Project creation | Must navigate to a specific nested group (Platform Eng → Observability), then create project |
| M2 | Add Yuki Tanaka as a Developer to the 'CI/CD' group | Member addition | Navigate to nested group → Members tab → modal with user selector + role dropdown |
| M3 | Change James Chen's role in the 'Terraform Modules' group from Maintainer to Owner | Role change | 3-level deep navigation (Platform Eng → Infrastructure → Terraform Modules) → Members → edit modal |
| M4 | Invite the 'Open Source' group to the 'Product Development' group with a maximum role of Reporter | Group sharing | Navigate to Product Dev → Sharing tab → modal with group selector + role |
| M5 | Remove Maria Rodriguez from the 'Product Development' group | Member removal | Navigate to group → Members tab → find specific member → remove with confirmation |
| M6 | Create a subgroup called 'Performance Testing' under the 'Web Application' group | Subgroup creation | Navigate to Product Dev → Web Application → create subgroup from overview |
| M7 | Update the Platform Engineering group: change its description to 'Core infrastructure and platform services' and enable 'Require two-factor authentication' | Multi-field settings | Navigate to group → Settings → update 2 different form controls → save |
| M8 | Revoke the 'Security' group's access to 'Platform Engineering' | Share revocation | **Trick task**: Agent must understand that Security is shared *into* Platform Engineering (not the reverse) and navigate to Platform Engineering's Sharing tab to remove it |

### Hard — Multi-step (H1–H4)

| ID | Instruction | Workflows Combined | Why Hard |
|----|-------------|-------------------|----------|
| H1 | Create a new public project called 'community-tools' in the 'Open Source' group, then share it with the 'Product Development' group with Developer access | Project creation + project sharing | Two distinct operations: create project, then navigate to new project's Sharing tab for a second operation |
| H2 | Create a new subgroup called 'Threat Intelligence' under the 'Security' group, then add Priya Sharma as a Developer to the new subgroup | Subgroup creation + member addition | Two operations on a newly-created entity; Security has `preventInvitations: true` (info banner only, doesn't block) which may confuse the agent |
| H3 | Remove Liam O'Shea from the 'web-frontend' project and add Sofia Petrov as a Developer to the same project | Member removal + member addition | Two membership operations on same project; must complete removal before addition (modal excludes existing members) |
| H4 | Change your username to 'alex.m' and update your display name to 'Alex M.' | Account tab + Profile edit tab | Operations span two different tabs within Profile; username change requires a confirmation dialog |

### Hard — Deep-constraint (H5–H8)

| ID | Instruction | Why Hard |
|----|-------------|----------|
| H5 | Add Omar Hassan as a member of the 'Terraform Modules' group with the Maintainer role and set the membership to expire on 2027-12-31 | 3 levels deep navigation (Platform Eng → Infrastructure → Terraform Modules) + interacting with custom date picker component (non-native, YYYY-MM-DD format) |
| H6 | In the 'Observability' group, change the name to 'Monitoring & Observability', set subgroup creation to 'Owners only', project creation to 'No one', and enable the 'Disable email mentions' option | 4 different form controls in one save (text input + 2 custom dropdowns + checkbox) in a nested group; agent must correctly operate each control type |
| H7 | Invite the 'Analytics Platform' group to the 'design-system' project with Reporter access and an expiration date of 2027-06-15 | Cross-organization sharing (Analytics Platform is in DataStream GmbH, design-system is in Acme Corp); must locate the project, use sharing modal with group selector + role + date picker |
| H8 | On the 'web-frontend' project, update the settings: change the project name to 'web-app-frontend', set the description to 'Main customer-facing web application', set the topics to 'react', 'vue', 'frontend', and change the visibility to 'private' | 4 field changes in one save; topics are a comma-separated text input that must be edited (existing value: 'react, typescript, frontend' → replace 'typescript' with 'vue'); visibility change from internal to private (valid: more restrictive) |

## Workflow Coverage

| Workflow | Tasks | Count |
|----------|-------|-------|
| Group creation | E1, M6, H2 | 3 |
| Group settings | M7, H6 | 2 |
| Group archive/unarchive | E6 | 1 |
| Group sharing (invite) | M4 | 1 |
| Group share revocation | M8 | 1 |
| Project creation | M1, H1 | 2 |
| Project settings | H8 | 1 |
| Project deletion | E2 | 1 |
| Project sharing (invite) | H1, H7 | 2 |
| Member addition (group) | M2, H2, H5 | 3 |
| Member role change (group) | M3 | 1 |
| Member removal (group) | M5 | 1 |
| Member addition (project) | H3 | 1 |
| Member removal (project) | H3 | 1 |
| Profile editing | E3, E8, H4 | 3 |
| Account settings (username) | H4 | 1 |
| Account settings (2FA) | E5 | 1 |
| Email management | E4, E7 | 2 |
| Cross-org operations | H7 | 1 |
| Deep navigation (3+ levels) | M3, H5 | 2 |
| Custom date picker | H5, H7 | 2 |

## Verifier Design

Each verifier implements `verify(server_url: str) -> tuple[bool, str]` and checks internal `AppState` via `GET /api/state`.

Key verification patterns used across tasks:

| Pattern | Example Tasks | Description |
|---------|---------------|-------------|
| Entity existence (by name) | E1, M1, M6, H1, H2 | Search by name/path, not by ID (IDs are auto-incremented) |
| Entity absence | E2, M5, M8 | Confirm deletion or removal succeeded |
| Property match | E3, E5, E8, M7, H6, H8 | Check specific field values after update |
| Side effect check | E1, E2, M6 | E.g., creating a group also creates an Owner membership |
| Membership with constraints | M2, H5 | Check role, membership type, and optional expiry date |
| Relationship check | M1, M4, M6, H1, H7 | Verify parent-child or share relationships between entities |
| Multi-condition | H3, H4, H6, H8 | Multiple independent checks must all pass |
| State sync | E3, E5, H4 | Verify both `currentUser` and `users[]` array are consistent |
