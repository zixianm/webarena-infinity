// ============================================================
// Linear Issue Management — Seed Data
// ============================================================

const SEED_DATA_VERSION = 1;

// ── Priority constants ──────────────────────────────────────
const PRIORITIES = [
    { value: 0, name: 'No priority', label: 'No priority', icon: '—', color: '#8b8b8b' },
    { value: 1, name: 'Urgent',      label: 'Urgent',      icon: '!!!', color: '#f76565' },
    { value: 2, name: 'High',        label: 'High',        icon: '!!',  color: '#f59e0b' },
    { value: 3, name: 'Medium',      label: 'Medium',      icon: '!',   color: '#3b82f6' },
    { value: 4, name: 'Low',         label: 'Low',         icon: '↓',   color: '#68b684' },
];

function getPriorityByName(name) {
    return PRIORITIES.find(p => p.name === name) || PRIORITIES[0];
}
function getPriorityByValue(value) {
    return PRIORITIES.find(p => p.value === value) || PRIORITIES[0];
}

// ── Estimate scales ─────────────────────────────────────────
const ESTIMATE_SCALES = {
    Exponential: [1, 2, 4, 8, 16],
    Fibonacci:   [1, 2, 3, 5, 8, 13],
    Linear:      [1, 2, 3, 4, 5],
    'T-Shirt':   ['XS', 'S', 'M', 'L', 'XL'],
};

// ── Relation types ──────────────────────────────────────────
const RELATION_TYPES = ['related', 'blocks', 'blocked', 'duplicate'];

// ── Reserved label names ────────────────────────────────────
const RESERVED_LABEL_NAMES = [
    'assignee', 'cycle', 'effort', 'estimate', 'hours',
    'priority', 'project', 'state', 'status',
];

// ── Status category constants ───────────────────────────────
const STATUS_CATEGORIES = ['backlog', 'unstarted', 'started', 'completed', 'canceled'];

// ── Users (10) ──────────────────────────────────────────────
const USERS = [
    { id: 'user-1',  name: 'Alex Morgan',     email: 'alex.morgan@company.com',     avatar: null, avatarColor: '#6366f1', role: 'Admin' },
    { id: 'user-2',  name: 'James Chen',      email: 'james.chen@company.com',      avatar: null, avatarColor: '#ec4899', role: 'Member' },
    { id: 'user-3',  name: 'Emma Wilson',     email: 'emma.wilson@company.com',     avatar: null, avatarColor: '#14b8a6', role: 'Member' },
    { id: 'user-4',  name: 'Priya Sharma',    email: 'priya.sharma@company.com',    avatar: null, avatarColor: '#f59e0b', role: 'Member' },
    { id: 'user-5',  name: 'Liam O\'Brien',   email: 'liam.obrien@company.com',     avatar: null, avatarColor: '#8b5cf6', role: 'Member' },
    { id: 'user-6',  name: 'Sofia Rodriguez', email: 'sofia.rodriguez@company.com', avatar: null, avatarColor: '#06b6d4', role: 'Member' },
    { id: 'user-7',  name: 'Yuki Tanaka',     email: 'yuki.tanaka@company.com',     avatar: null, avatarColor: '#f43f5e', role: 'Member' },
    { id: 'user-8',  name: 'Omar Hassan',     email: 'omar.hassan@company.com',     avatar: null, avatarColor: '#22c55e', role: 'Member' },
    { id: 'user-9',  name: 'Maya Patel',      email: 'maya.patel@company.com',      avatar: null, avatarColor: '#a855f7', role: 'Member' },
    { id: 'user-10', name: 'Carlos Reyes',    email: 'carlos.reyes@company.com',    avatar: null, avatarColor: '#ef4444', role: 'Member' },
];

const CURRENT_USER = USERS[0]; // Alex Morgan

// ── Helper: build default statuses for a team ───────────────
function buildStatuses(teamId) {
    return [
        { id: `${teamId}-status-1`, name: 'Backlog',     category: 'backlog',   color: '#8b8b8b', position: 0 },
        { id: `${teamId}-status-2`, name: 'Todo',        category: 'unstarted', color: '#e2e2e2', position: 1 },
        { id: `${teamId}-status-3`, name: 'In Progress', category: 'started',   color: '#f59e0b', position: 2 },
        { id: `${teamId}-status-4`, name: 'In Review',   category: 'started',   color: '#3b82f6', position: 3 },
        { id: `${teamId}-status-5`, name: 'Done',        category: 'completed', color: '#22c55e', position: 4 },
        { id: `${teamId}-status-6`, name: 'Canceled',    category: 'canceled',  color: '#95a2b3', position: 5 },
    ];
}

// ── Teams (4) ───────────────────────────────────────────────
const TEAMS = [
    {
        id: 'team-1', name: 'Engineering', identifier: 'ENG', color: '#6366f1', icon: '⚙️',
        isPrivate: false,
        memberIds: ['user-1', 'user-2', 'user-4', 'user-5', 'user-7', 'user-8'],
        statuses: buildStatuses('team-1'),
        settings: { estimatesEnabled: true, estimateScale: 'Fibonacci', autoClosePeriod: 3, autoArchivePeriod: 6, timezone: 'America/Los_Angeles' },
        issueCounter: 40,
    },
    {
        id: 'team-2', name: 'Design', identifier: 'DES', color: '#ec4899', icon: '🎨',
        isPrivate: false,
        memberIds: ['user-1', 'user-3', 'user-6', 'user-9'],
        statuses: buildStatuses('team-2'),
        settings: { estimatesEnabled: false, estimateScale: 'Linear', autoClosePeriod: 3, autoArchivePeriod: 6, timezone: 'America/New_York' },
        issueCounter: 14,
    },
    {
        id: 'team-3', name: 'Product', identifier: 'PRD', color: '#14b8a6', icon: '📦',
        isPrivate: false,
        memberIds: ['user-1', 'user-3', 'user-5', 'user-9', 'user-10'],
        statuses: buildStatuses('team-3'),
        settings: { estimatesEnabled: false, estimateScale: 'Linear', autoClosePeriod: 3, autoArchivePeriod: 6, timezone: 'America/Chicago' },
        issueCounter: 10,
    },
    {
        id: 'team-4', name: 'Customer Success', identifier: 'CS', color: '#f59e0b', icon: '🤝',
        isPrivate: false,
        memberIds: ['user-1', 'user-6', 'user-8', 'user-10'],
        statuses: buildStatuses('team-4'),
        settings: { estimatesEnabled: false, estimateScale: 'Linear', autoClosePeriod: 6, autoArchivePeriod: 12, timezone: 'America/New_York' },
        issueCounter: 22,
    },
];

// ── Label Groups (3) ────────────────────────────────────────
const LABEL_GROUPS = [
    { id: 'lg-1', name: 'Type',     scope: 'workspace', teamId: null, color: '#6366f1' },
    { id: 'lg-2', name: 'Platform', scope: 'workspace', teamId: null, color: '#14b8a6' },
    { id: 'lg-3', name: 'Area',     scope: 'workspace', teamId: null, color: '#f59e0b' },
];

// ── Labels (18) ─────────────────────────────────────────────
const LABELS = [
    // Type group
    { id: 'label-1',  name: 'Bug',         color: '#ef4444', description: 'Something is broken',            scope: 'workspace', teamId: null, groupId: 'lg-1', archived: false },
    { id: 'label-2',  name: 'Feature',     color: '#3b82f6', description: 'New functionality',              scope: 'workspace', teamId: null, groupId: 'lg-1', archived: false },
    { id: 'label-3',  name: 'Improvement', color: '#8b5cf6', description: 'Enhancement to existing feature', scope: 'workspace', teamId: null, groupId: 'lg-1', archived: false },
    { id: 'label-4',  name: 'Chore',       color: '#6b7280', description: 'Maintenance or housekeeping',    scope: 'workspace', teamId: null, groupId: 'lg-1', archived: false },
    // Platform group
    { id: 'label-5',  name: 'iOS',     color: '#000000', description: 'Apple iOS platform',     scope: 'workspace', teamId: null, groupId: 'lg-2', archived: false },
    { id: 'label-6',  name: 'Android', color: '#22c55e', description: 'Google Android platform', scope: 'workspace', teamId: null, groupId: 'lg-2', archived: false },
    { id: 'label-7',  name: 'Web',     color: '#3b82f6', description: 'Web platform',            scope: 'workspace', teamId: null, groupId: 'lg-2', archived: false },
    // Area group
    { id: 'label-8',  name: 'Frontend',       color: '#ec4899', description: 'UI and client-side',        scope: 'workspace', teamId: null, groupId: 'lg-3', archived: false },
    { id: 'label-9',  name: 'Backend',        color: '#6366f1', description: 'Server-side and APIs',      scope: 'workspace', teamId: null, groupId: 'lg-3', archived: false },
    { id: 'label-10', name: 'Infrastructure', color: '#f59e0b', description: 'DevOps and infrastructure', scope: 'workspace', teamId: null, groupId: 'lg-3', archived: false },
    // Standalone workspace labels
    { id: 'label-11', name: 'Design',        color: '#ec4899', description: 'Design-related work',        scope: 'workspace', teamId: null, groupId: null, archived: false },
    { id: 'label-12', name: 'Performance',   color: '#f97316', description: 'Performance optimization',   scope: 'workspace', teamId: null, groupId: null, archived: false },
    { id: 'label-13', name: 'Security',      color: '#dc2626', description: 'Security-related issues',    scope: 'workspace', teamId: null, groupId: null, archived: false },
    { id: 'label-14', name: 'Accessibility', color: '#2563eb', description: 'Accessibility improvements', scope: 'workspace', teamId: null, groupId: null, archived: false },
    { id: 'label-15', name: 'UX',            color: '#a855f7', description: 'User experience',            scope: 'workspace', teamId: null, groupId: null, archived: false },
    { id: 'label-16', name: 'Testing',       color: '#0ea5e9', description: 'Testing and QA',             scope: 'workspace', teamId: null, groupId: null, archived: false },
    // Team-specific labels
    { id: 'label-17', name: 'Tech Debt',     color: '#78716c', description: 'Technical debt',             scope: 'team', teamId: 'team-1', groupId: null, archived: false },
    { id: 'label-18', name: 'Onboarding',    color: '#f59e0b', description: 'Customer onboarding tasks',  scope: 'team', teamId: 'team-4', groupId: null, archived: false },
];

// ── Projects (4) ────────────────────────────────────────────
const PROJECTS = [
    { id: 'project-1', name: 'Q1 Launch',              description: 'Q1 product launch milestones',           color: '#6366f1', status: 'started',   leadId: 'user-1',  teamIds: ['team-1', 'team-2', 'team-3'], startDate: '2025-01-06', targetDate: '2025-03-31', createdAt: '2024-12-15T10:00:00Z' },
    { id: 'project-2', name: 'Mobile App Redesign',     description: 'Complete redesign of mobile application', color: '#ec4899', status: 'planned',   leadId: 'user-3',  teamIds: ['team-2', 'team-1'],           startDate: '2025-02-01', targetDate: '2025-05-30', createdAt: '2025-01-05T09:00:00Z' },
    { id: 'project-3', name: 'Infrastructure Upgrade',  description: 'Migrate to new cloud infrastructure',    color: '#f59e0b', status: 'started',   leadId: 'user-4',  teamIds: ['team-1'],                     startDate: '2025-01-13', targetDate: '2025-04-15', createdAt: '2025-01-02T14:00:00Z' },
    { id: 'project-4', name: 'Customer Portal',         description: 'Self-service customer portal',           color: '#22c55e', status: 'planned',   leadId: 'user-6',  teamIds: ['team-4', 'team-1'],           startDate: '2025-03-01', targetDate: '2025-06-30', createdAt: '2025-01-10T11:00:00Z' },
];

// ── Cycles (9) ──────────────────────────────────────────────
const CYCLES = [
    // Engineering
    { id: 'cycle-1', name: 'Sprint 11', teamId: 'team-1', startDate: '2025-01-06', endDate: '2025-01-19', status: 'completed' },
    { id: 'cycle-2', name: 'Sprint 12', teamId: 'team-1', startDate: '2025-01-20', endDate: '2025-02-02', status: 'active' },
    { id: 'cycle-3', name: 'Sprint 13', teamId: 'team-1', startDate: '2025-02-03', endDate: '2025-02-16', status: 'upcoming' },
    // Design
    { id: 'cycle-4', name: 'Sprint 8',  teamId: 'team-2', startDate: '2025-01-06', endDate: '2025-01-19', status: 'completed' },
    { id: 'cycle-5', name: 'Sprint 9',  teamId: 'team-2', startDate: '2025-01-20', endDate: '2025-02-02', status: 'active' },
    { id: 'cycle-6', name: 'Sprint 10', teamId: 'team-2', startDate: '2025-02-03', endDate: '2025-02-16', status: 'upcoming' },
    // Product
    { id: 'cycle-7', name: 'Sprint 5',  teamId: 'team-3', startDate: '2025-01-13', endDate: '2025-01-26', status: 'completed' },
    { id: 'cycle-8', name: 'Sprint 6',  teamId: 'team-3', startDate: '2025-01-27', endDate: '2025-02-09', status: 'active' },
    // Customer Success
    { id: 'cycle-9', name: 'Sprint 3',  teamId: 'team-4', startDate: '2025-01-20', endDate: '2025-02-02', status: 'active' },
];

// ── Issues (38 total) ───────────────────────────────────────
const ISSUES = [
    // ── Engineering (ENG-1 through ENG-40, sparse) ──
    { id: 'issue-eng-1',  identifier: 'ENG-1',  title: 'Set up CI/CD pipeline',             description: 'Configure GitHub Actions for automated builds and deployments.',   teamId: 'team-1', statusId: 'team-1-status-5', priority: getPriorityByName('High'),   assigneeId: 'user-4', creatorId: 'user-1', labelIds: ['label-10'], projectId: 'project-3', cycleId: 'cycle-1', parentIssueId: null, estimate: 8, dueDate: null,         sortOrder: 1, createdAt: '2025-01-06T09:00:00Z', updatedAt: '2025-01-15T16:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-eng-2',  identifier: 'ENG-2',  title: 'Database schema migration',         description: 'Migrate user tables to new schema with proper indexing.',          teamId: 'team-1', statusId: 'team-1-status-5', priority: getPriorityByName('High'),   assigneeId: 'user-2', creatorId: 'user-1', labelIds: ['label-9'],  projectId: 'project-3', cycleId: 'cycle-1', parentIssueId: null, estimate: 13, dueDate: null,        sortOrder: 2, createdAt: '2025-01-06T09:30:00Z', updatedAt: '2025-01-18T14:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-eng-3',  identifier: 'ENG-3',  title: 'Implement rate limiting',           description: 'Add rate limiting middleware to all API endpoints.',               teamId: 'team-1', statusId: 'team-1-status-5', priority: getPriorityByName('Medium'), assigneeId: 'user-7', creatorId: 'user-4', labelIds: ['label-9', 'label-13'], projectId: null, cycleId: 'cycle-1', parentIssueId: null, estimate: 5, dueDate: null, sortOrder: 3, createdAt: '2025-01-07T10:00:00Z', updatedAt: '2025-01-16T11:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-eng-4',  identifier: 'ENG-4',  title: 'Add monitoring dashboards',         description: 'Create Grafana dashboards for key system metrics.',                teamId: 'team-1', statusId: 'team-1-status-4', priority: getPriorityByName('Medium'), assigneeId: 'user-8', creatorId: 'user-1', labelIds: ['label-10'], projectId: 'project-3', cycleId: 'cycle-2', parentIssueId: null, estimate: 3, dueDate: null,        sortOrder: 4, createdAt: '2025-01-08T08:30:00Z', updatedAt: '2025-01-25T15:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-eng-5',  identifier: 'ENG-5',  title: 'Refactor authentication module',    description: 'Break down monolithic auth into microservice.',                    teamId: 'team-1', statusId: 'team-1-status-3', priority: getPriorityByName('High'),   assigneeId: 'user-1', creatorId: 'user-1', labelIds: ['label-9', 'label-17'], projectId: 'project-1', cycleId: 'cycle-2', parentIssueId: null, estimate: 8, dueDate: '2025-02-15', sortOrder: 5, createdAt: '2025-01-10T09:00:00Z', updatedAt: '2025-01-26T10:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-eng-34', identifier: 'ENG-34', title: 'API response caching layer',        description: 'Implement Redis-based caching for frequently accessed API endpoints.', teamId: 'team-1', statusId: 'team-1-status-3', priority: getPriorityByName('High'),   assigneeId: 'user-1', creatorId: 'user-4', labelIds: ['label-9', 'label-12'], projectId: 'project-1', cycleId: 'cycle-2', parentIssueId: null, estimate: 5, dueDate: '2025-02-10', sortOrder: 6, createdAt: '2025-01-20T09:00:00Z', updatedAt: '2025-01-27T14:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-eng-35', identifier: 'ENG-35', title: 'Fix memory leak in worker process', description: 'Worker process memory usage grows unbounded after 24h.',            teamId: 'team-1', statusId: 'team-1-status-3', priority: getPriorityByName('Urgent'), assigneeId: null,     creatorId: 'user-2', labelIds: ['label-1'],  projectId: null,       cycleId: 'cycle-2', parentIssueId: null, estimate: 3, dueDate: '2025-01-30', sortOrder: 7, createdAt: '2025-01-21T11:00:00Z', updatedAt: '2025-01-22T09:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-eng-36', identifier: 'ENG-36', title: 'WebSocket connection drops',        description: 'Users report intermittent WebSocket disconnections under load.',    teamId: 'team-1', statusId: 'team-1-status-2', priority: getPriorityByName('High'),   assigneeId: 'user-7', creatorId: 'user-5', labelIds: [],           projectId: null,       cycleId: null,      parentIssueId: null, estimate: null, dueDate: null,     sortOrder: 8, createdAt: '2025-01-22T14:00:00Z', updatedAt: '2025-01-22T14:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-eng-37', identifier: 'ENG-37', title: 'Optimize database queries',         description: 'Several N+1 queries identified in the dashboard endpoint.',         teamId: 'team-1', statusId: 'team-1-status-2', priority: getPriorityByName('Medium'), assigneeId: 'user-2', creatorId: 'user-1', labelIds: ['label-9', 'label-12'], projectId: null, cycleId: 'cycle-2', parentIssueId: null, estimate: null, dueDate: null, sortOrder: 9, createdAt: '2025-01-23T08:00:00Z', updatedAt: '2025-01-23T08:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-eng-38', identifier: 'ENG-38', title: 'Upgrade Node.js to v20 LTS',        description: 'Current Node 18 EOL approaching. Upgrade all services.',            teamId: 'team-1', statusId: 'team-1-status-2', priority: getPriorityByName('Medium'), assigneeId: 'user-5', creatorId: 'user-4', labelIds: ['label-10'], projectId: 'project-3', cycleId: null, parentIssueId: null, estimate: 3, dueDate: '2025-03-01', sortOrder: 10, createdAt: '2025-01-24T10:00:00Z', updatedAt: '2025-01-24T10:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-eng-39', identifier: 'ENG-39', title: 'Add end-to-end test suite',         description: 'Set up Playwright tests for critical user flows.',                  teamId: 'team-1', statusId: 'team-1-status-1', priority: getPriorityByName('Low'),    assigneeId: 'user-7', creatorId: 'user-1', labelIds: ['label-16'], projectId: null,       cycleId: null, parentIssueId: null, estimate: 8, dueDate: null,         sortOrder: 11, createdAt: '2025-01-25T09:00:00Z', updatedAt: '2025-01-25T09:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-eng-40', identifier: 'ENG-40', title: 'Implement feature flags system',    description: 'Build a feature flag service for gradual rollouts.',                teamId: 'team-1', statusId: 'team-1-status-1', priority: getPriorityByName('Medium'), assigneeId: 'user-1', creatorId: 'user-1', labelIds: ['label-2', 'label-9'], projectId: 'project-1', cycleId: null, parentIssueId: null, estimate: 5, dueDate: null, sortOrder: 12, createdAt: '2025-01-26T11:00:00Z', updatedAt: '2025-01-26T11:00:00Z', archivedAt: null, deletedAt: null },

    // ── Design (DES-1 through DES-14, sparse) ──
    { id: 'issue-des-1',  identifier: 'DES-1',  title: 'Design system component library',   description: 'Create a comprehensive design system with reusable components.',    teamId: 'team-2', statusId: 'team-2-status-3', priority: getPriorityByName('High'),   assigneeId: 'user-3', creatorId: 'user-1', labelIds: ['label-11'], projectId: 'project-2', cycleId: 'cycle-5', parentIssueId: null, estimate: null, dueDate: null,     sortOrder: 1, createdAt: '2025-01-06T10:00:00Z', updatedAt: '2025-01-20T12:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-des-2',  identifier: 'DES-2',  title: 'Mobile navigation redesign',        description: 'Redesign the mobile app navigation for better usability.',          teamId: 'team-2', statusId: 'team-2-status-3', priority: getPriorityByName('High'),   assigneeId: 'user-6', creatorId: 'user-3', labelIds: ['label-15'], projectId: 'project-2', cycleId: 'cycle-5', parentIssueId: null, estimate: null, dueDate: '2025-02-14', sortOrder: 2, createdAt: '2025-01-07T09:00:00Z', updatedAt: '2025-01-22T15:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-des-3',  identifier: 'DES-3',  title: 'Dashboard wireframes',              description: 'Create wireframes for the new analytics dashboard.',                teamId: 'team-2', statusId: 'team-2-status-5', priority: getPriorityByName('Medium'), assigneeId: 'user-9', creatorId: 'user-3', labelIds: ['label-15'], projectId: null,       cycleId: 'cycle-4', parentIssueId: null, estimate: null, dueDate: null,     sortOrder: 3, createdAt: '2025-01-08T11:00:00Z', updatedAt: '2025-01-15T16:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-des-4',  identifier: 'DES-4',  title: 'Accessibility audit',               description: 'Run WCAG 2.1 AA audit across all pages and create remediation plan.', teamId: 'team-2', statusId: 'team-2-status-2', priority: getPriorityByName('Medium'), assigneeId: 'user-3', creatorId: 'user-1', labelIds: ['label-14'], projectId: null,       cycleId: 'cycle-5', parentIssueId: null, estimate: null, dueDate: '2025-02-28', sortOrder: 4, createdAt: '2025-01-10T10:00:00Z', updatedAt: '2025-01-21T09:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-des-5',  identifier: 'DES-5',  title: 'Dark mode color palette',           description: 'Define complete color palette for dark mode implementation.',        teamId: 'team-2', statusId: 'team-2-status-4', priority: getPriorityByName('Low'),    assigneeId: 'user-6', creatorId: 'user-3', labelIds: ['label-11'], projectId: 'project-2', cycleId: 'cycle-5', parentIssueId: null, estimate: null, dueDate: null,     sortOrder: 5, createdAt: '2025-01-12T13:00:00Z', updatedAt: '2025-01-24T11:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-des-12', identifier: 'DES-12', title: 'Onboarding flow illustrations',     description: 'Design custom illustrations for the user onboarding experience.',   teamId: 'team-2', statusId: 'team-2-status-3', priority: getPriorityByName('Medium'), assigneeId: 'user-9', creatorId: 'user-3', labelIds: ['label-15'], projectId: 'project-2', cycleId: 'cycle-5', parentIssueId: null, estimate: null, dueDate: null,     sortOrder: 6, createdAt: '2025-01-20T10:00:00Z', updatedAt: '2025-01-25T14:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-des-13', identifier: 'DES-13', title: 'Email template designs',            description: 'Design responsive email templates for transactional emails.',       teamId: 'team-2', statusId: 'team-2-status-1', priority: getPriorityByName('Low'),    assigneeId: null,     creatorId: 'user-3', labelIds: ['label-11'], projectId: null,       cycleId: null,      parentIssueId: null, estimate: null, dueDate: null,     sortOrder: 7, createdAt: '2025-01-22T09:00:00Z', updatedAt: '2025-01-22T09:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-des-14', identifier: 'DES-14', title: 'Settings page UI overhaul',         description: 'Modernize the settings page with new design patterns.',             teamId: 'team-2', statusId: 'team-2-status-3', priority: getPriorityByName('High'),   assigneeId: 'user-3', creatorId: 'user-1', labelIds: ['label-15', 'label-3'], projectId: 'project-1', cycleId: 'cycle-5', parentIssueId: null, estimate: null, dueDate: '2025-02-20', sortOrder: 8, createdAt: '2025-01-24T08:00:00Z', updatedAt: '2025-01-26T10:00:00Z', archivedAt: null, deletedAt: null },

    // ── Product (PRD-1 through PRD-10, sparse) ──
    { id: 'issue-prd-1',  identifier: 'PRD-1',  title: 'Competitive analysis report',       description: 'Analyze top 5 competitors and identify feature gaps.',              teamId: 'team-3', statusId: 'team-3-status-5', priority: getPriorityByName('High'),   assigneeId: 'user-9', creatorId: 'user-1', labelIds: [],           projectId: null,       cycleId: 'cycle-7', parentIssueId: null, estimate: null, dueDate: null,     sortOrder: 1, createdAt: '2025-01-06T09:00:00Z', updatedAt: '2025-01-20T16:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-prd-2',  identifier: 'PRD-2',  title: 'Q1 roadmap planning',               description: 'Define and prioritize Q1 product roadmap initiatives.',             teamId: 'team-3', statusId: 'team-3-status-5', priority: getPriorityByName('Urgent'), assigneeId: 'user-1', creatorId: 'user-1', labelIds: [],           projectId: 'project-1', cycleId: 'cycle-7', parentIssueId: null, estimate: null, dueDate: '2025-01-15', sortOrder: 2, createdAt: '2025-01-06T10:00:00Z', updatedAt: '2025-01-14T18:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-prd-3',  identifier: 'PRD-3',  title: 'User interview synthesis',          description: 'Compile and analyze findings from 20 user interviews.',             teamId: 'team-3', statusId: 'team-3-status-4', priority: getPriorityByName('Medium'), assigneeId: 'user-10', creatorId: 'user-9', labelIds: ['label-15'], projectId: null,       cycleId: 'cycle-8', parentIssueId: null, estimate: null, dueDate: null,    sortOrder: 3, createdAt: '2025-01-13T11:00:00Z', updatedAt: '2025-01-25T14:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-prd-4',  identifier: 'PRD-4',  title: 'Feature specification: Search',     description: 'Write detailed spec for enhanced search functionality.',             teamId: 'team-3', statusId: 'team-3-status-3', priority: getPriorityByName('High'),   assigneeId: 'user-5', creatorId: 'user-1', labelIds: ['label-2'],  projectId: 'project-1', cycleId: 'cycle-8', parentIssueId: null, estimate: null, dueDate: '2025-02-07', sortOrder: 4, createdAt: '2025-01-15T09:00:00Z', updatedAt: '2025-01-27T11:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-prd-5',  identifier: 'PRD-5',  title: 'Pricing page A/B test plan',        description: 'Design A/B test for new pricing page layout.',                      teamId: 'team-3', statusId: 'team-3-status-2', priority: getPriorityByName('Medium'), assigneeId: 'user-3', creatorId: 'user-9', labelIds: [],           projectId: null,       cycleId: 'cycle-8', parentIssueId: null, estimate: null, dueDate: null,     sortOrder: 5, createdAt: '2025-01-20T10:00:00Z', updatedAt: '2025-01-20T10:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-prd-10', identifier: 'PRD-10', title: 'Analytics dashboard requirements',  description: 'Define requirements for new analytics dashboard v2.',               teamId: 'team-3', statusId: 'team-3-status-2', priority: getPriorityByName('Low'),    assigneeId: 'user-9', creatorId: 'user-1', labelIds: ['label-2'],  projectId: 'project-1', cycleId: null, parentIssueId: null, estimate: null, dueDate: null, sortOrder: 6, createdAt: '2025-01-26T09:00:00Z', updatedAt: '2025-01-26T09:00:00Z', archivedAt: null, deletedAt: null },

    // ── Customer Success (CS-1 through CS-22, sparse) ──
    { id: 'issue-cs-1',  identifier: 'CS-1',  title: 'Acme Corp onboarding',               description: 'Complete onboarding process for Acme Corp enterprise account.',     teamId: 'team-4', statusId: 'team-4-status-5', priority: getPriorityByName('High'),   assigneeId: 'user-6', creatorId: 'user-1', labelIds: ['label-18'], projectId: 'project-4', cycleId: null, parentIssueId: null, estimate: null, dueDate: null,         sortOrder: 1, createdAt: '2025-01-06T09:00:00Z', updatedAt: '2025-01-18T16:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-cs-2',  identifier: 'CS-2',  title: 'TechStart integration support',      description: 'Help TechStart set up API integration with their CRM.',             teamId: 'team-4', statusId: 'team-4-status-3', priority: getPriorityByName('Medium'), assigneeId: 'user-8', creatorId: 'user-6', labelIds: [],           projectId: null,       cycleId: 'cycle-9', parentIssueId: null, estimate: null, dueDate: '2025-02-05', sortOrder: 2, createdAt: '2025-01-10T10:00:00Z', updatedAt: '2025-01-25T11:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-cs-3',  identifier: 'CS-3',  title: 'Quarterly business review prep',     description: 'Prepare QBR materials for top 10 enterprise accounts.',             teamId: 'team-4', statusId: 'team-4-status-3', priority: getPriorityByName('High'),   assigneeId: 'user-10', creatorId: 'user-1', labelIds: [],          projectId: null,       cycleId: 'cycle-9', parentIssueId: null, estimate: null, dueDate: '2025-02-15', sortOrder: 3, createdAt: '2025-01-12T09:00:00Z', updatedAt: '2025-01-26T14:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-cs-4',  identifier: 'CS-4',  title: 'Knowledge base article updates',     description: 'Update 15 outdated knowledge base articles with new UI screenshots.', teamId: 'team-4', statusId: 'team-4-status-2', priority: getPriorityByName('Low'),  assigneeId: 'user-6', creatorId: 'user-8', labelIds: [],           projectId: null,       cycleId: null,      parentIssueId: null, estimate: null, dueDate: null,        sortOrder: 4, createdAt: '2025-01-15T11:00:00Z', updatedAt: '2025-01-15T11:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-cs-20', identifier: 'CS-20', title: 'Legacy CRM data cleanup',            description: 'Remove deprecated fields from legacy CRM integration data.',        teamId: 'team-4', statusId: 'team-4-status-1', priority: getPriorityByName('Low'),    assigneeId: 'user-10', creatorId: 'user-6', labelIds: ['label-4'], projectId: null,       cycleId: null, parentIssueId: null, estimate: null, dueDate: null, sortOrder: 5, createdAt: '2025-01-24T10:00:00Z', updatedAt: '2025-01-24T10:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-cs-21', identifier: 'CS-21', title: 'Customer feedback survey analysis',  description: 'Analyze Q4 customer satisfaction survey results.',                   teamId: 'team-4', statusId: 'team-4-status-2', priority: getPriorityByName('Medium'), assigneeId: 'user-8', creatorId: 'user-1', labelIds: [],           projectId: null,       cycleId: 'cycle-9', parentIssueId: null, estimate: null, dueDate: '2025-02-10', sortOrder: 6, createdAt: '2025-01-25T09:00:00Z', updatedAt: '2025-01-25T09:00:00Z', archivedAt: null, deletedAt: null },
    { id: 'issue-cs-22', identifier: 'CS-22', title: 'Renewal process documentation',      description: 'Document the customer renewal workflow for the team handbook.',      teamId: 'team-4', statusId: 'team-4-status-2', priority: getPriorityByName('Medium'), assigneeId: 'user-6', creatorId: 'user-10', labelIds: [],          projectId: null,       cycleId: null, parentIssueId: null, estimate: null, dueDate: null, sortOrder: 7, createdAt: '2025-01-26T08:00:00Z', updatedAt: '2025-01-26T08:00:00Z', archivedAt: null, deletedAt: null },
];

// ── Comments (12) ───────────────────────────────────────────
const COMMENTS = [
    { id: 'comment-1',  issueId: 'issue-eng-5',  body: 'I started breaking down the auth module. The session management piece is the most complex.',   userId: 'user-1', parentCommentId: null,       resolved: false, createdAt: '2025-01-20T10:00:00Z', updatedAt: '2025-01-20T10:00:00Z' },
    { id: 'comment-2',  issueId: 'issue-eng-5',  body: 'Should we consider using OAuth2 for the new service? It would simplify third-party integrations.', userId: 'user-4', parentCommentId: 'comment-1', resolved: false, createdAt: '2025-01-20T11:30:00Z', updatedAt: '2025-01-20T11:30:00Z' },
    { id: 'comment-3',  issueId: 'issue-eng-5',  body: 'Good idea. Let me create a spike for that.',                                                    userId: 'user-1', parentCommentId: 'comment-1', resolved: false, createdAt: '2025-01-20T12:00:00Z', updatedAt: '2025-01-20T12:00:00Z' },
    { id: 'comment-4',  issueId: 'issue-eng-34', body: 'Redis cluster is set up. We can use it for session caching too.',                               userId: 'user-4', parentCommentId: null,        resolved: false, createdAt: '2025-01-22T09:00:00Z', updatedAt: '2025-01-22T09:00:00Z' },
    { id: 'comment-5',  issueId: 'issue-eng-34', body: 'Cache invalidation strategy needs to be documented before we proceed.',                          userId: 'user-1', parentCommentId: null,        resolved: false, createdAt: '2025-01-23T14:00:00Z', updatedAt: '2025-01-23T14:00:00Z' },
    { id: 'comment-6',  issueId: 'issue-des-1',  body: 'I\'ve uploaded the initial component inventory to Figma. Please review.',                        userId: 'user-3', parentCommentId: null,        resolved: false, createdAt: '2025-01-15T10:00:00Z', updatedAt: '2025-01-15T10:00:00Z' },
    { id: 'comment-7',  issueId: 'issue-des-2',  body: 'The tab bar approach tested better than the hamburger menu in user testing.',                    userId: 'user-6', parentCommentId: null,        resolved: false, createdAt: '2025-01-18T16:00:00Z', updatedAt: '2025-01-18T16:00:00Z' },
    { id: 'comment-8',  issueId: 'issue-des-14', body: 'Can we align the settings page with the new design system components?',                          userId: 'user-1', parentCommentId: null,        resolved: false, createdAt: '2025-01-25T09:00:00Z', updatedAt: '2025-01-25T09:00:00Z' },
    { id: 'comment-9',  issueId: 'issue-des-14', body: 'Yes, that\'s the plan. I\'ll use the new card and form components from DES-1.',                   userId: 'user-3', parentCommentId: 'comment-8', resolved: false, createdAt: '2025-01-25T10:00:00Z', updatedAt: '2025-01-25T10:00:00Z' },
    { id: 'comment-10', issueId: 'issue-prd-4',  body: 'The search spec should include autocomplete and fuzzy matching requirements.',                    userId: 'user-5', parentCommentId: null,        resolved: false, createdAt: '2025-01-22T11:00:00Z', updatedAt: '2025-01-22T11:00:00Z' },
    { id: 'comment-11', issueId: 'issue-cs-3',   body: 'I\'ve started gathering metrics from the last quarter. Will share the deck by Friday.',           userId: 'user-10', parentCommentId: null,       resolved: false, createdAt: '2025-01-24T14:00:00Z', updatedAt: '2025-01-24T14:00:00Z' },
    { id: 'comment-12', issueId: 'issue-eng-35', body: 'This looks like it might be related to the connection pool not being properly released.',         userId: 'user-2', parentCommentId: null,        resolved: false, createdAt: '2025-01-22T10:00:00Z', updatedAt: '2025-01-22T10:00:00Z' },
];

// ── Issue Relations (6) ─────────────────────────────────────
const ISSUE_RELATIONS = [
    { id: 'rel-1', issueId: 'issue-eng-5',  relatedIssueId: 'issue-eng-34', type: 'related' },
    { id: 'rel-2', issueId: 'issue-eng-2',  relatedIssueId: 'issue-eng-38', type: 'blocks' },
    { id: 'rel-3', issueId: 'issue-des-1',  relatedIssueId: 'issue-des-2',  type: 'related' },
    { id: 'rel-4', issueId: 'issue-des-1',  relatedIssueId: 'issue-des-5',  type: 'related' },
    { id: 'rel-5', issueId: 'issue-prd-4',  relatedIssueId: 'issue-eng-5',  type: 'related' },
    { id: 'rel-6', issueId: 'issue-cs-2',   relatedIssueId: 'issue-cs-1',   type: 'related' },
];

// ── Templates (3) ───────────────────────────────────────────
const TEMPLATES = [
    { id: 'template-1', name: 'Bug Report',      description: 'Template for reporting bugs',              teamId: null, defaultPriority: getPriorityByName('High'),        defaultLabelIds: ['label-1'], defaultEstimate: null, templateDescription: '## Steps to Reproduce\n1. \n2. \n3. \n\n## Expected Behavior\n\n## Actual Behavior\n\n## Environment\n- Browser: \n- OS: ', createdAt: '2025-01-01T00:00:00Z' },
    { id: 'template-2', name: 'Feature Request',  description: 'Template for feature requests',            teamId: null, defaultPriority: getPriorityByName('Medium'),      defaultLabelIds: ['label-2'], defaultEstimate: null, templateDescription: '## Problem Statement\n\n## Proposed Solution\n\n## User Stories\n- As a user, I want...\n\n## Acceptance Criteria\n- [ ] \n- [ ] ', createdAt: '2025-01-01T00:00:00Z' },
    { id: 'template-3', name: 'Sprint Task',      description: 'Template for sprint tasks',                teamId: null, defaultPriority: getPriorityByName('No priority'), defaultLabelIds: [],           defaultEstimate: null, templateDescription: '## Task Description\n\n## Requirements\n- [ ] \n\n## Definition of Done\n- [ ] Code written\n- [ ] Tests passing\n- [ ] PR reviewed', createdAt: '2025-01-01T00:00:00Z' },
];

// ── Customers (4) ───────────────────────────────────────────
const CUSTOMERS = [
    { id: 'customer-1', name: 'Acme Corp',        domain: 'acme.com',        tier: 'Enterprise', contactName: 'John Smith',       contactEmail: 'john@acme.com',        revenue: 120000, createdAt: '2024-06-15T00:00:00Z' },
    { id: 'customer-2', name: 'TechStart Inc',    domain: 'techstart.io',    tier: 'Business',   contactName: 'Sarah Lee',        contactEmail: 'sarah@techstart.io',   revenue: 45000,  createdAt: '2024-08-20T00:00:00Z' },
    { id: 'customer-3', name: 'GlobalMedia',      domain: 'globalmedia.com', tier: 'Enterprise', contactName: 'Mark Johnson',     contactEmail: 'mark@globalmedia.com', revenue: 200000, createdAt: '2024-03-10T00:00:00Z' },
    { id: 'customer-4', name: 'DataFlow Systems', domain: 'dataflow.dev',    tier: 'Pro',        contactName: 'Lisa Wang',        contactEmail: 'lisa@dataflow.dev',    revenue: 18000,  createdAt: '2024-11-01T00:00:00Z' },
];

// ── Customer Requests (5) ───────────────────────────────────
const CUSTOMER_REQUESTS = [
    { id: 'cr-1', customerId: 'customer-1', issueId: 'issue-eng-5',  title: 'Need SSO integration ASAP',          description: 'Acme requires SAML SSO for their security compliance.',   priority: 'high',   createdAt: '2025-01-10T09:00:00Z' },
    { id: 'cr-2', customerId: 'customer-2', issueId: 'issue-cs-2',   title: 'API rate limits too restrictive',    description: 'TechStart hitting rate limits during peak sync periods.',  priority: 'medium', createdAt: '2025-01-12T14:00:00Z' },
    { id: 'cr-3', customerId: 'customer-3', issueId: 'issue-prd-4',  title: 'Advanced search needed',             description: 'GlobalMedia needs boolean search operators.',             priority: 'high',   createdAt: '2025-01-15T10:00:00Z' },
    { id: 'cr-4', customerId: 'customer-1', issueId: 'issue-eng-34', title: 'API response times degrading',       description: 'Acme reporting slow API responses during business hours.', priority: 'urgent', createdAt: '2025-01-20T08:00:00Z' },
    { id: 'cr-5', customerId: 'customer-4', issueId: 'issue-cs-4',   title: 'Documentation needs updating',       description: 'DataFlow found outdated docs in the knowledge base.',     priority: 'low',    createdAt: '2025-01-22T11:00:00Z' },
];

// ── Build full seed data object ─────────────────────────────
function buildSeedData() {
    return {
        _seedVersion: SEED_DATA_VERSION,
        teams:            JSON.parse(JSON.stringify(TEAMS)),
        users:            JSON.parse(JSON.stringify(USERS)),
        issues:           JSON.parse(JSON.stringify(ISSUES)),
        labels:           JSON.parse(JSON.stringify(LABELS)),
        labelGroups:      JSON.parse(JSON.stringify(LABEL_GROUPS)),
        projects:         JSON.parse(JSON.stringify(PROJECTS)),
        cycles:           JSON.parse(JSON.stringify(CYCLES)),
        comments:         JSON.parse(JSON.stringify(COMMENTS)),
        issueRelations:   JSON.parse(JSON.stringify(ISSUE_RELATIONS)),
        templates:        JSON.parse(JSON.stringify(TEMPLATES)),
        customers:        JSON.parse(JSON.stringify(CUSTOMERS)),
        customerRequests: JSON.parse(JSON.stringify(CUSTOMER_REQUESTS)),
        currentUserId:    CURRENT_USER.id,
        _nextIssueId:     100,
        _nextCommentId:   20,
        _nextRelationId:  10,
        _nextLabelId:     30,
        _nextLabelGroupId: 10,
        _nextTemplateId:  10,
        _nextCustomerId:  10,
        _nextCustomerRequestId: 10,
    };
}
