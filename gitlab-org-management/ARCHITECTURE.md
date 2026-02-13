# Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [File Structure](#file-structure)
3. [Data Model](#data-model)
4. [State Management & Persistence](#state-management--persistence)
5. [Routing](#routing)
6. [UI Component System](#ui-component-system)
7. [Task Workflows](#task-workflows)
8. [Membership & Access Model](#membership--access-model)
9. [Verifying Operations via the Backend](#verifying-operations-via-the-backend)
10. [Data Relationships Reference](#data-relationships-reference)

---

## Overview

This is a single-page application (SPA) that replicates GitLab's organization management functionality. It is built with **pure HTML, CSS, and JavaScript** (no frameworks, no build step). All data is stored **in-memory** in a centralized `AppState` object and **persisted to `localStorage`** across page reloads.

### How to Run

```bash
# From the project root:
python3 -m http.server 8000
# Then open http://localhost:8000 in a browser
```

Any static file server works. The app is entirely client-side.

### Technology Constraints

- No frameworks (React, Vue, etc.)
- No native OS UI elements (`<select>`, `alert()`, `<input type="date">`, etc.)
- All dropdowns, modals, toasts, and date inputs are custom HTML/CSS/JS
- All data lives in the browser (localStorage + in-memory)

---

## File Structure

```
index.html              App shell (sidebar, topbar, modal, toast containers)
css/styles.css          All styles (~30KB, GitLab-inspired theme)
js/data.js              Seed data constants (users, groups, projects, memberships, roles)
js/state.js             Centralized AppState with mutations, queries, persistence
js/components.js        Reusable UI components (dropdowns, modals, toasts, badges, forms)
js/views.js             All view renderers and modal/action helpers
js/app.js               Hash-based router and event handler attachment
DESIGN.md               Project specification and implementation rules
gitlab-doc/             Source documentation files used as specification
```

### Load Order

Scripts are loaded synchronously in `index.html` in this order:

1. **`data.js`** - Defines all constant seed data (`ROLES`, `USERS`, `GROUPS`, `PROJECTS`, etc.)
2. **`state.js`** - Creates `AppState` using persisted data (from localStorage) or seed data
3. **`components.js`** - Defines the `Components` utility object
4. **`views.js`** - Defines the `Views` object (depends on `AppState` and `Components`)
5. **`app.js`** - Defines the `Router` and calls `initApp()` on DOMContentLoaded

Each script tag uses a `?v=2` cache-busting query parameter to prevent stale caching.

---

## Data Model

### Entities

| Entity | Key Fields | Stored In |
|--------|-----------|-----------|
| **User** | `id`, `username`, `name`, `email`, `avatarColor`, `twoFactorEnabled` | `AppState.users[]` |
| **Organization** | `id`, `name`, `path`, `visibility`, `ownerId` | `AppState.organizations[]` |
| **Group** | `id`, `name`, `path`, `fullPath`, `parentId`, `organizationId`, `visibility`, `archived` | `AppState.groups[]` |
| **Project** | `id`, `name`, `path`, `fullPath`, `groupId`, `visibility`, `archived`, `stars`, `forks` | `AppState.projects[]` |
| **Current User** | Same fields as User, plus `secondaryEmails`, `status`, `bio`, etc. | `AppState.currentUser` |

### Relationship Tables

| Relationship | Key Fields | Stored In |
|-------------|-----------|-----------|
| **Group Membership** | `groupId`, `userId`, `role`, `membershipType`, `expiresAt`, `addedBy`, `addedAt` | `AppState.groupMemberships[]` |
| **Project Membership** | `projectId`, `userId`, `role`, `membershipType`, `expiresAt`, `addedBy`, `addedAt` | `AppState.projectMemberships[]` |
| **Group Share** | `sourceGroupId`, `targetGroupId`, `maxRole`, `expiresAt`, `addedBy`, `addedAt` | `AppState.groupShares[]` |
| **Project Share** | `sourceGroupId`, `targetProjectId`, `maxRole`, `expiresAt`, `addedBy`, `addedAt` | `AppState.projectShares[]` |

### Roles

Roles are plain objects with a numeric `level` used for comparison:

| Role | Level | Constant |
|------|-------|----------|
| Minimal Access | 5 | `ROLES.MINIMAL_ACCESS` |
| Guest | 10 | `ROLES.GUEST` |
| Planner | 15 | `ROLES.PLANNER` |
| Reporter | 20 | `ROLES.REPORTER` |
| Developer | 30 | `ROLES.DEVELOPER` |
| Maintainer | 40 | `ROLES.MAINTAINER` |
| Owner | 50 | `ROLES.OWNER` |

**Important**: After JSON round-tripping (persistence), roles are compared by `.level` value, **not** by object reference. For example, `m.role.level >= ROLES.OWNER.level`, not `m.role === ROLES.OWNER`.

### Group Hierarchy

Groups form a tree via `parentId`:
- `parentId: null` = top-level group (belongs directly to an organization)
- Maximum depth: 20 levels (enforced by GitLab.com, stored in `GITLAB_COM_LIMITS.misc.maxSubgroupDepth`)
- `organizationId` links a group to its organization (inherited from parent on creation)
- `fullPath` is the complete slash-separated path, e.g., `acme-corp/platform-engineering/infrastructure`

### Visibility Cascade

Visibility levels have an order: `private (0) < internal (1) < public (2)`.

A subgroup or project **cannot** have a visibility level higher than its parent group. This is enforced by:
- `AppState.isVisibilityAllowed(visibility, parentGroupId)` - checks if a visibility level is allowed
- `AppState.getMaxVisibility(parentGroupId)` - returns the maximum allowed visibility
- The create group/project modals dynamically filter visibility options based on the parent

---

## State Management & Persistence

### AppState Object (`state.js`)

`AppState` is a single global object that holds all application data. It follows an observer pattern for reactivity.

#### Lifecycle

```
Page Load
   │
   ├─ _loadPersistedData()  ─── reads from localStorage('gitlabOrgAppState')
   │   │
   │   ├─ Found? → Parse JSON, return data
   │   └─ Not found / error? → return null
   │
   ├─ _loadSeedData()  ─── deep-clones all constants from data.js
   │
   └─ AppState initialized from persisted data OR seed data
```

#### Mutation Flow

Every mutation method follows this pattern:

```
User action (click, form submit)
    │
    ├─ Calls AppState mutation method (e.g., createGroup, addGroupMember)
    │     │
    │     ├─ Modifies in-memory arrays
    │     └─ Calls this.notify()
    │            │
    │            ├─ Notifies all subscribers (listeners)
    │            └─ Calls this._persist()
    │                   │
    │                   └─ Serializes persistable state to localStorage
    │
    └─ UI update (toast, router refresh/navigate)
```

#### What Is Persisted

Persisted to `localStorage` under key `gitlabOrgAppState`:
- `currentUser`, `users`, `organizations`, `groups`, `projects`
- `groupMemberships`, `projectMemberships`, `groupShares`, `projectShares`
- `_nextUserId`, `_nextGroupId`, `_nextProjectId`, `_nextOrgId`

**Not** persisted (transient UI state):
- `currentRoute`, `routeParams`, `sidebarOpen`, `modalOpen`, `validationErrors`, `toasts`, `_listeners`

#### Reset Mechanism

`AppState.resetToSeedData()`:
1. Removes the localStorage key
2. Deep-clones all seed data from `data.js`
3. Replaces all AppState collections
4. Notifies listeners (but does NOT persist, since we just cleared storage)

Available in the UI via Settings > "Reset all data to defaults".

### Subscription

```javascript
const unsubscribe = AppState.subscribe((state) => {
    // Called after every notify()
});
unsubscribe(); // Stop listening
```

Currently, the app uses `Router.refresh()` for re-rendering rather than fine-grained subscriptions.

---

## Routing

### Hash-Based Router (`app.js`)

The app uses hash-based routing. URLs look like `http://localhost:8000/#/groups/5?tab=members`.

#### Route Table

| Pattern | Handler | Description |
|---------|---------|-------------|
| `/` | `Views.home()` | Dashboard |
| `/organizations` | `Views.organizations()` | Organization list |
| `/organizations/:id` | `Views.organizationDetail(id)` | Organization detail |
| `/groups` | `Views.groups()` | Group tree view |
| `/groups/:id` | `Views.groupDetail(id)` | Group detail (tabbed) |
| `/projects` | `Views.projects()` | Project list |
| `/projects/:id` | `Views.projectDetail(id)` | Project detail (tabbed) |
| `/members` | `Views.members()` | Global member list |
| `/namespaces` | `Views.namespaces()` | Namespace list |
| `/profile` | `Views.profile()` | Current user profile |
| `/profile/:username` | `Views.profile(username)` | User profile by username |
| `/import` | `Views.importPage()` | Import sources |
| `/settings` | `Views.settings()` | GitLab.com settings/limits |

#### Route Matching

`Router.matchRoute(pattern, path)` splits both by `/` and matches segment-by-segment. Segments starting with `:` are captured as params. Query string parameters (after `?`) are parsed into `AppState.routeParams`.

#### Rendering Cycle

```
Router.navigate(path)
    │
    ├─ Parse path and query params
    ├─ Update AppState.currentRoute and AppState.routeParams
    ├─ Push to browser history (unless skipHistory=true)
    └─ Router.render()
         │
         ├─ Match route pattern → call view handler → get HTML string
         ├─ Set contentWrapper.innerHTML = html
         ├─ Update sidebar active state
         └─ Router.attachHandlers()  (bind event listeners to new DOM elements)
```

#### Event Handler Attachment

After each render, `Router.attachHandlers()` scans the DOM for interactive elements and binds event listeners. Each element is flagged (e.g., `el._routeHandlerAttached = true`) to prevent duplicate bindings. This includes:

- Route links (`[data-route]`)
- Tab items (`.tab-item`)
- Search inputs (`#groupSearch`, `#projectSearch`, `#memberSearch`, etc.)
- Filter dropdowns (`#groupVisFilter`, `#projectVisFilter`, `#memberTypeFilter`)
- Action buttons (`#createGroupBtn`, `#saveGroupSettingsBtn`, `#resetDataBtn`, etc.)

---

## UI Component System

### Components Object (`components.js`)

All reusable UI elements are methods on the global `Components` object. They return HTML strings (not DOM nodes) for embedding in view templates.

#### Key Components

| Component | Method | Description |
|-----------|--------|-------------|
| Avatar | `Components.avatar(user, size)` | Circular avatar with initials |
| Group Avatar | `Components.groupAvatar(entity, size)` | Square avatar with initials |
| Custom Dropdown | `Components.dropdown(id, options, selectedValue, opts)` | Custom div-based dropdown with optional search |
| Modal | `Components.showModal(title, body, footer)` | Opens the global modal overlay |
| Toast | `Components.showToast(message, type, duration)` | Timed notification popup |
| Confirm Dialog | `Components.confirm(title, msg, onConfirm, opts)` | Modal with cancel/confirm buttons |
| Tabs | `Components.tabs(id, items, activeTab)` | Tab bar rendering |
| Badges | `Components.badge()`, `roleBadge()`, `visibilityBadge()`, `membershipBadge()` | Various badge types |
| Form Fields | `Components.formField()`, `textInput()`, `textarea()`, `checkbox()`, `dateInput()` | Form building blocks |
| Info Boxes | `Components.infoBox()`, `warningBox()`, `errorBox()`, `successBox()` | Alert boxes |
| Utilities | `Components.escapeHtml()`, `escapeAttr()`, `formatDate()`, `timeAgo()` | HTML escaping, date formatting |

#### Custom Dropdown Behavior

Dropdowns fire a custom `change` event with `detail.value` when an item is selected. Global event delegation (at bottom of `components.js`) handles:
- Opening/closing on trigger click
- Item selection (updates `data-value` attribute and trigger text)
- Click-outside-to-close
- Search filtering within dropdown menus

#### Modal System

There is a single global modal container in `index.html`:
```
#modalOverlay > #modalContainer > (#modalHeader + #modalBody + #modalFooter)
```
`Components.showModal()` populates these elements and adds the `.active` class. `Components.closeModal()` removes it. The `Components.confirm()` method is a convenience wrapper.

---

## Task Workflows

This section documents every major user-facing operation, the code path it follows, and which data collections it modifies.

### 1. Create Group

**UI Path**: Groups page > "New group" button, OR Group detail > Overview > "New subgroup" button

**Code Flow**:
1. `Views._showCreateGroupModal(parentId, orgId)` opens the modal
2. Name input auto-generates the URL slug in `pathInput`
3. Real-time validation via `Views._validateCreateGroupForm()` → calls `AppState.validateName()` and `AppState.validatePath()`
4. Submit button calls `AppState.createGroup(data)`

**State Changes** (`AppState.createGroup` at `state.js:409`):
- Increments `_nextGroupId`
- Pushes new group object to `AppState.groups[]`
- Pushes a membership record to `AppState.groupMemberships[]` (current user as Owner)
- Calls `notify()` → persists

**Validation Rules**:
- Name: 2-255 chars, starts/ends with alphanumeric, no consecutive special chars, not `.git`/`.atom`, not a reserved name
- Path: same rules, URL-safe characters only
- Visibility: cannot exceed parent group's visibility

### 2. Create Project

**UI Path**: Projects page > "New project", OR Group detail > Overview > "New project"

**Code Flow**:
1. `Views._showCreateProjectModal(groupId)` opens the modal
2. Group selector dropdown (with search) determines which group owns the project
3. When the selected group changes, the visibility dropdown is constrained
4. Submit calls `AppState.createProject(data)`

**State Changes** (`AppState.createProject` at `state.js:479`):
- Increments `_nextProjectId`
- Pushes new project to `AppState.projects[]`
- Calls `notify()` → persists

**Note**: Unlike group creation, creating a project does **not** add a direct project membership for the current user. The current user gains access through their group membership (inherited).

### 3. Delete Group

**UI Path**: Group detail page header > "Delete group" button (Owner only)

**Code Flow**:
1. `Views._confirmDeleteGroup(groupId)` shows a confirm dialog listing affected subgroups and projects
2. On confirm, calls `AppState.deleteGroup(groupId)`

**State Changes** (`AppState.deleteGroup` at `state.js:460`):
- Collects all descendant group IDs via `getDescendantGroups()`
- Removes all projects belonging to those groups from `AppState.projects[]`
- Removes all groups from `AppState.groups[]`
- Removes all related `groupMemberships[]`, `projectMemberships[]`, `groupShares[]`, `projectShares[]`
- Calls `notify()` → persists

**Cascade**: Deleting a group removes its entire subtree (all descendants, their projects, and all associated memberships and shares).

### 4. Delete Project

**UI Path**: Project detail header > "Delete project" (Owner only)

**State Changes** (`AppState.deleteProject` at `state.js:501`):
- Removes project from `AppState.projects[]`
- Removes related `projectMemberships[]` and `projectShares[]`

### 5. Update Group Settings

**UI Path**: Group detail > Settings tab > form fields > "Save settings"

**Code Flow**:
1. Handler in `app.js:257` reads form values (`groupName`, `groupPath`, `groupDesc`, `groupVisibility`, etc.)
2. Validates name via `AppState.validateName()`
3. Calls `AppState.updateGroup(groupId, data)` which uses `Object.assign()`
4. Calls `Views._rebuildGroupPaths(groupId)` to recursively update `fullPath` on the group, its descendants, and their projects

**State Changes**: Mutates the group object in-place within `AppState.groups[]`.

### 6. Add Member to Group

**UI Path**: Group detail > Members tab > "Add member" (Maintainer+)

**Code Flow**:
1. `Views._showAddMemberModal('group', groupId)` shows a modal with user selector, role selector, and expiry date
2. Filters out users who are already members
3. On submit, calls `AppState.addGroupMember(groupId, userId, role, expiresAt)`

**State Changes** (`AppState.addGroupMember` at `state.js:341`):
- If the user already has a direct membership → updates role and expiresAt
- Otherwise → pushes new record to `groupMemberships[]` with `membershipType: 'direct'`

### 7. Edit Member Role/Expiration

**UI Path**: Group detail > Members tab > "Edit" button on a direct member row

**Code Flow**:
1. `Views._showEditMemberModal('group', groupId, userId)` opens edit modal
2. Computes minimum role level from inherited membership (cannot go lower)
3. On submit, calls `AppState.updateGroupMemberRole()` and `AppState.updateGroupMemberExpiration()`

### 8. Remove Member from Group

**UI Path**: Group detail > Members tab > "Remove" button

**Code Flow**: `Views._confirmRemoveMember('group', groupId, userId)` → confirm dialog → `AppState.removeGroupMember(groupId, userId)`

**State Changes**: Filters out the matching direct membership from `groupMemberships[]`.

**Important**: Removing a direct member does not remove inherited memberships. If the user has access through a parent group, they retain that inherited access.

### 9. Add/Remove Project Members

Same pattern as group members, but operates on `AppState.projectMemberships[]` via `addProjectMember()` / `removeProjectMember()`.

### 10. Share Group with Group (Group-to-Group Invitation)

**UI Path**: Group detail > Sharing tab > "Invite a group"

**Code Flow**:
1. `Views._showShareGroupModal(targetGroupId)` shows modal with group selector, max role, and expiry
2. On submit, calls `AppState.addGroupShare(sourceGroupId, targetGroupId, maxRole, expiresAt)`

**State Changes** (`AppState.addGroupShare` at `state.js:508`):
- If share already exists → updates maxRole and expiresAt
- Otherwise → pushes new record to `groupShares[]`

**Effect**: All direct members of `sourceGroupId` gain access to `targetGroupId` with their role capped at `maxRole`.

### 11. Share Project with Group (Group-to-Project Invitation)

Same pattern as group sharing, but operates on `AppState.projectShares[]` via `addProjectShare()`.

### 12. Transfer Group

**UI Path**: Group detail > Settings tab > "Transfer group"

**Code Flow**:
1. `Views._showTransferGroupModal(groupId)` shows modal with target dropdown (excludes self and descendants)
2. On submit, updates `parentId`, may reduce visibility if new parent is more restrictive
3. Calls `Views._rebuildGroupPaths(groupId)` to recursively fix all `fullPath` values

### 13. Archive/Unarchive Group

**UI Path**: Group detail > Settings tab > "Archive this group" / "Unarchive this group"

**State Changes**: Sets `group.archived = true/false` via `AppState.updateGroup()`.

**Effect**: Archived groups hide most action buttons (create subgroup, create project, add member, etc.).

### 14. Update Profile

**UI Path**: Profile page > Edit tab > form fields > "Save profile"

**Code Flow** (`app.js:346`):
1. Reads all profile form fields
2. Updates `AppState.currentUser` properties
3. Syncs to `AppState.users[]` via `Object.assign(u, user)`
4. Calls `AppState.notify()` → persists

### 15. Change Username

**UI Path**: Profile > Account tab > username field > "Change username"

**Code Flow** (`app.js:377`):
1. Validates with `AppState.validateName()`
2. Checks uniqueness against `AppState.users[]`
3. Shows confirm dialog
4. Updates `currentUser.username` and syncs to users array

### 16. Add/Remove Secondary Emails

**UI Path**: Profile > Emails tab

**State Changes**: Modifies `AppState.currentUser.secondaryEmails[]` and syncs to users array.

### 17. Toggle Two-Factor Authentication

**UI Path**: Profile > Account tab > "Enable/Disable 2FA"

**State Changes**: Toggles `currentUser.twoFactorEnabled` and syncs.

### 18. Reset All Data

**UI Path**: Settings page > "Reset all data to defaults"

**Code Flow** (`app.js:242`):
1. Shows danger confirm dialog
2. Calls `AppState.resetToSeedData()` which clears localStorage and restores seed data
3. Navigates to home

---

## Membership & Access Model

The membership system implements GitLab's inheritance model with three membership sources:

### Membership Types

| Type | Source | Description |
|------|--------|-------------|
| **Direct** | Explicit assignment | User was directly added to the group/project |
| **Inherited** | Parent group chain | User has a direct membership in an ancestor group |
| **Shared** | Group invitation | User belongs to a group that was invited to this group/project |

### Computation Methods

#### Group Members

- **`getDirectGroupMembers(groupId)`**: Filters `groupMemberships[]` for matching `groupId` and `membershipType === 'direct'`
- **`getInheritedGroupMembers(groupId)`**: Walks up the ancestor chain via `getGroupAncestors()`. For each ancestor, collects its direct members. Skips users who already have a direct membership in the current group (direct takes precedence).
- **`getSharedGroupMembers(groupId)`**: Looks up `groupShares[]` where `targetGroupId` matches. For each share, gets direct members of the source group. Applies the `maxRole` cap: `effectiveRole = min(memberRole, share.maxRole)` (compared by `.level`).
- **`getAllGroupMembers(groupId)`**: Returns `[...direct, ...inherited, ...shared]`

#### Project Members

- **`getDirectProjectMembers(projectId)`**: Filters `projectMemberships[]`
- **`getInheritedProjectMembers(projectId)`**: Gets the project's group, then calls `getAllGroupMembers(group.id)`. Group members who don't have a direct project membership appear as inherited project members.
- **`getSharedProjectMembers(projectId)`**: Same pattern as group shares but from `projectShares[]`
- **`getAllProjectMembers(projectId)`**: Combines all three

#### Current User's Role

- **`getCurrentUserGroupRole(groupId)`**: Gets all group members, filters to current user, returns the highest `.role.level`
- **`getCurrentUserProjectRole(projectId)`**: Same for projects

### Role Precedence

When a user appears in multiple membership sources, the **highest role** wins. This is computed at display time, not stored.

### Role Constraints on Editing

When editing a member's role in a group:
- The minimum role is the user's **inherited** role level (you cannot set a direct role lower than what they inherit)
- The Owner role can only be assigned by other Owners

---

## Verifying Operations via the Backend

Since all data lives in `localStorage` and the in-memory `AppState`, you can inspect and verify operations using browser DevTools or automated tools (e.g., Playwright).

### Accessing AppState in the Console

Open the browser console and access the global `AppState` object directly:

```javascript
// All data is accessible:
AppState.groups
AppState.projects
AppState.users
AppState.groupMemberships
AppState.projectMemberships
AppState.groupShares
AppState.projectShares
AppState.currentUser
```

### Verifying Group Creation

After creating a group:

```javascript
// Check the group was added
AppState.groups.find(g => g.name === 'My New Group')
// → { id: 15, name: 'My New Group', path: 'my-new-group', fullPath: '...', ... }

// Verify the creator was added as Owner
AppState.groupMemberships.filter(m => m.groupId === 15)
// → [{ groupId: 15, userId: 1, role: { name: 'Owner', level: 50 }, membershipType: 'direct', ... }]

// Check the auto-increment counter advanced
AppState._nextGroupId
// → 16
```

### Verifying Project Creation

```javascript
// Find the project
AppState.projects.find(p => p.name === 'my-project')
// → { id: 21, name: 'my-project', groupId: 6, fullPath: 'acme-corp/.../my-project', ... }

// Note: no direct projectMembership is created; access is inherited from the group
AppState.projectMemberships.filter(m => m.projectId === 21)
// → [] (empty, unless members were explicitly added)
```

### Verifying Membership Operations

```javascript
// Check direct group members
AppState.groupMemberships.filter(m => m.groupId === 1 && m.membershipType === 'direct')

// Check all members (including inherited and shared) — uses computed method
AppState.getAllGroupMembers(1)
// Each entry has: { userId, role: { name, level }, membershipType, source, expiresAt, ... }

// Check a specific user's effective role
AppState.getCurrentUserGroupRole(1)
// → { name: 'Owner', level: 50, ... }

// Verify inherited members of a subgroup
AppState.getInheritedGroupMembers(6)
// Returns members inherited from group 1 (Platform Engineering)
```

### Verifying Sharing

```javascript
// Check group-to-group shares
AppState.groupShares
// → [{ sourceGroupId: 4, targetGroupId: 1, maxRole: { name: 'Reporter', level: 20 }, ... }, ...]

// Check shared members of a group (computed)
AppState.getSharedGroupMembers(1)
// Returns members from sourceGroupId=4 (Security) with roles capped at Reporter

// Check project shares
AppState.projectShares
// → [{ sourceGroupId: 3, targetProjectId: 6, maxRole: { ... }, ... }, ...]
```

### Verifying Deletion

```javascript
// After deleting group 6 (Infrastructure):
AppState.groups.find(g => g.id === 6)
// → undefined

// Its subgroups (id:12 Terraform Modules) should also be gone
AppState.groups.find(g => g.id === 12)
// → undefined

// Projects in those groups should be gone
AppState.projects.filter(p => p.groupId === 6 || p.groupId === 12)
// → []

// Memberships should be cleaned up
AppState.groupMemberships.filter(m => m.groupId === 6 || m.groupId === 12)
// → []
```

### Verifying Profile Updates

```javascript
// Check current user
AppState.currentUser.name
AppState.currentUser.username
AppState.currentUser.bio
AppState.currentUser.twoFactorEnabled
AppState.currentUser.secondaryEmails

// Verify sync to users array
AppState.getUserById(1).name === AppState.currentUser.name
// → true (they should always match)
```

### Verifying Persistence (localStorage)

```javascript
// Read raw persisted data
JSON.parse(localStorage.getItem('gitlabOrgAppState'))

// Check specific collections
const stored = JSON.parse(localStorage.getItem('gitlabOrgAppState'));
stored.groups.length     // number of groups
stored.projects.length   // number of projects
stored._nextGroupId      // next auto-increment ID

// Verify persistence matches in-memory state
stored.groups.length === AppState.groups.length
// → true (should always match after any mutation)

// Clear persistence (will revert to seed data on reload)
localStorage.removeItem('gitlabOrgAppState')
```

### Verifying Visibility Constraints

```javascript
// Check if 'public' is allowed for a subgroup under a 'private' parent
AppState.isVisibilityAllowed('public', 1)
// → false (group 1 is private)

AppState.isVisibilityAllowed('private', 1)
// → true

AppState.getMaxVisibility(1)
// → 'private'
```

### Verifying Name Validation

```javascript
AppState.validateName('a')
// → ['Must be at least 2 characters']

AppState.validateName('admin')
// → ['"admin" is a reserved name']

AppState.validateName('My Valid Group')
// → [] (empty = valid)

AppState.validatePath('my-group')
// → [] (empty = valid)

AppState.validatePath('a')
// → ['Must be at least 2 characters']
```

### Using Playwright or Automated Tests

Since the app uses `data-testid` attributes throughout, you can locate elements reliably:

```javascript
// Playwright examples:
await page.getByTestId('create-group-btn').click();
await page.getByTestId('newGroupName').fill('Test Group');
await page.getByTestId('submit-create-group').click();
await page.getByTestId('toast');  // verify success toast

// Read AppState from within the page context:
const groupCount = await page.evaluate(() => AppState.groups.length);
const newGroup = await page.evaluate(() => AppState.groups.find(g => g.name === 'Test Group'));
```

Key `data-testid` values:

| Element | Test ID |
|---------|---------|
| Create group button | `create-group-btn` |
| Create group form | `create-group-form` |
| Submit create group | `submit-create-group` |
| Create project button | `create-project-btn` |
| Submit create project | `submit-create-project` |
| Add member button | `add-member-btn` |
| Submit add member | `submit-add-member` |
| Delete group button | `delete-group-btn` |
| Delete project button | `delete-project-btn` |
| Group tree | `group-tree` |
| Member list | `member-list` |
| Modal confirm | `modal-confirm` |
| Modal cancel | `modal-cancel` |
| Toast notification | `toast` |
| Sidebar toggle | `sidebar-toggle` |
| User menu | `user-menu` |
| Specific group tree item | `group-tree-item-{id}` |
| Specific member edit button | `edit-member-{username}` |
| Specific member remove button | `remove-member-{username}` |

---

## Data Relationships Reference

```
Organization (1)
 └── Group (many, top-level: parentId=null, organizationId=org.id)
      ├── Group (subgroup: parentId=parent.id)
      │    ├── Group (sub-subgroup, up to 20 levels)
      │    └── Project (groupId=group.id)
      └── Project (groupId=group.id)

GroupMembership
  groupId → Group.id
  userId  → User.id
  role    → { name, level } (plain object, compared by .level)

ProjectMembership
  projectId → Project.id
  userId    → User.id
  role      → { name, level }

GroupShare (group invited to group)
  sourceGroupId → Group.id (the group being invited)
  targetGroupId → Group.id (the group receiving access)
  maxRole       → { name, level } (caps the effective role)

ProjectShare (group invited to project)
  sourceGroupId    → Group.id
  targetProjectId  → Project.id
  maxRole          → { name, level }
```

### Seed Data Summary

| Collection | Count | ID Range |
|-----------|-------|----------|
| Users | 12 | 1-12 |
| Organizations | 2 | 1-2 |
| Groups | 14 | 1-14 |
| Projects | 20 | 1-20 |
| Group Memberships | 22 | (no ID, keyed by groupId+userId) |
| Project Memberships | 5 | (no ID, keyed by projectId+userId) |
| Group Shares | 2 | (keyed by sourceGroupId+targetGroupId) |
| Project Shares | 2 | (keyed by sourceGroupId+targetProjectId) |

Auto-increment counters start after the last seed ID:
- `_nextUserId: 13`
- `_nextGroupId: 15`
- `_nextProjectId: 21`
- `_nextOrgId: 3`
