// ============================================================
// Linear Issue Management — AppState
// ============================================================

const AppState = {
    // ── Data (persisted) ────────────────────────────────────
    teams: [], users: [], issues: [], labels: [], labelGroups: [],
    projects: [], cycles: [], comments: [], issueRelations: [],
    templates: [], customers: [], customerRequests: [],
    currentUserId: null,
    _seedVersion: SEED_DATA_VERSION,
    _nextIssueId: 100, _nextCommentId: 20, _nextRelationId: 10,
    _nextLabelId: 30, _nextLabelGroupId: 10, _nextTemplateId: 10,
    _nextCustomerId: 10, _nextCustomerRequestId: 10,

    // ── UI state (transient) ────────────────────────────────
    currentRoute: '/',
    routeParams: {},
    _listeners: [],

    // ── Init ────────────────────────────────────────────────
    init() {
        const saved = localStorage.getItem('linearAppState');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                if (parsed._seedVersion === SEED_DATA_VERSION) {
                    this._loadFrom(parsed);
                    this._pushToServer();
                    return;
                }
            } catch (e) { /* fall through to seed */ }
            localStorage.removeItem('linearAppState');
        }
        this._loadFrom(buildSeedData());
        this._persist();
    },

    _loadFrom(data) {
        const keys = [
            'teams','users','issues','labels','labelGroups','projects','cycles',
            'comments','issueRelations','templates','customers','customerRequests',
            'currentUserId','_seedVersion',
            '_nextIssueId','_nextCommentId','_nextRelationId','_nextLabelId',
            '_nextLabelGroupId','_nextTemplateId','_nextCustomerId','_nextCustomerRequestId',
        ];
        keys.forEach(k => { if (data[k] !== undefined) this[k] = data[k]; });
    },

    // ── Subscription ────────────────────────────────────────
    subscribe(fn)   { this._listeners.push(fn); },
    notify()        { this._persist(); this._listeners.forEach(fn => fn()); },

    // ── Persistence ─────────────────────────────────────────
    _getPersistable() {
        return {
            _seedVersion: this._seedVersion,
            teams: this.teams, users: this.users, issues: this.issues,
            labels: this.labels, labelGroups: this.labelGroups,
            projects: this.projects, cycles: this.cycles,
            comments: this.comments, issueRelations: this.issueRelations,
            templates: this.templates, customers: this.customers,
            customerRequests: this.customerRequests,
            currentUserId: this.currentUserId,
            _nextIssueId: this._nextIssueId, _nextCommentId: this._nextCommentId,
            _nextRelationId: this._nextRelationId, _nextLabelId: this._nextLabelId,
            _nextLabelGroupId: this._nextLabelGroupId, _nextTemplateId: this._nextTemplateId,
            _nextCustomerId: this._nextCustomerId, _nextCustomerRequestId: this._nextCustomerRequestId,
        };
    },

    _persist() {
        const data = this._getPersistable();
        localStorage.setItem('linearAppState', JSON.stringify(data));
        this._pushToServer();
    },

    _pushToServer() {
        fetch('/api/state', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this._getPersistable()),
        }).catch(() => {});
    },

    resetToSeedData() {
        localStorage.removeItem('linearAppState');
        this._loadFrom(buildSeedData());
        this._persist();
    },

    // ── Lookups ─────────────────────────────────────────────
    getCurrentUser()       { return this.users.find(u => u.id === this.currentUserId); },
    getUserById(id)        { return this.users.find(u => u.id === id); },
    getTeamById(id)        { return this.teams.find(t => t.id === id); },
    getIssueById(id)       { return this.issues.find(i => i.id === id); },
    getIssueByIdentifier(ident) { return this.issues.find(i => i.identifier === ident); },
    getLabelById(id)       { return this.labels.find(l => l.id === id); },
    getLabelGroupById(id)  { return this.labelGroups.find(g => g.id === id); },
    getProjectById(id)     { return this.projects.find(p => p.id === id); },
    getCycleById(id)       { return this.cycles.find(c => c.id === id); },
    getTemplateById(id)    { return this.templates.find(t => t.id === id); },
    getCustomerById(id)    { return this.customers.find(c => c.id === id); },

    // ── Queries ─────────────────────────────────────────────
    getIssuesForTeam(teamId) {
        return this.issues.filter(i => i.teamId === teamId && !i.deletedAt && !i.archivedAt);
    },

    getSubIssues(parentIssueId) {
        return this.issues.filter(i => i.parentIssueId === parentIssueId && !i.deletedAt);
    },

    getIssueRelations(issueId) {
        const direct = this.issueRelations.filter(r => r.issueId === issueId);
        const inverse = this.issueRelations.filter(r => r.relatedIssueId === issueId).map(r => {
            const inverseType = r.type === 'blocks' ? 'blocked' : r.type === 'blocked' ? 'blocks' : r.type;
            return { ...r, issueId: r.relatedIssueId, relatedIssueId: r.issueId, type: inverseType, _inverse: true };
        });
        return [...direct, ...inverse];
    },

    getLabelsForTeam(teamId) {
        return this.labels.filter(l => !l.archived && (l.scope === 'workspace' || l.teamId === teamId));
    },

    getLabelsInGroup(groupId) {
        return this.labels.filter(l => l.groupId === groupId);
    },

    getCommentsForIssue(issueId) {
        return this.comments.filter(c => c.issueId === issueId).sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
    },

    getCyclesForTeam(teamId) {
        return this.cycles.filter(c => c.teamId === teamId);
    },

    getMyIssues() {
        return this.issues.filter(i => i.assigneeId === this.currentUserId && !i.deletedAt && !i.archivedAt);
    },

    getIssuesForProject(projectId) {
        return this.issues.filter(i => i.projectId === projectId && !i.deletedAt && !i.archivedAt);
    },

    getIssuesForCycle(cycleId) {
        return this.issues.filter(i => i.cycleId === cycleId && !i.deletedAt && !i.archivedAt);
    },

    getCustomerRequestsForIssue(issueId) {
        return this.customerRequests.filter(cr => cr.issueId === issueId);
    },

    getCustomerRequestsForCustomer(customerId) {
        return this.customerRequests.filter(cr => cr.customerId === customerId);
    },

    getStatusById(statusId) {
        for (const team of this.teams) {
            const s = team.statuses.find(st => st.id === statusId);
            if (s) return s;
        }
        return null;
    },

    getTeamStatuses(teamId) {
        const team = this.getTeamById(teamId);
        return team ? team.statuses : [];
    },

    // ── Mutations ───────────────────────────────────────────
    createIssue(data) {
        const team = this.getTeamById(data.teamId);
        if (!team) return null;
        team.issueCounter++;
        const identifier = `${team.identifier}-${team.issueCounter}`;
        const now = new Date().toISOString();
        const defaultStatus = team.statuses.find(s => s.category === 'backlog') || team.statuses[0];
        const issue = {
            id: `issue-${this._nextIssueId++}`,
            identifier,
            title: data.title || '',
            description: data.description || '',
            teamId: data.teamId,
            statusId: data.statusId || defaultStatus.id,
            priority: data.priority || getPriorityByName('No priority'),
            assigneeId: data.assigneeId || null,
            creatorId: data.creatorId || this.currentUserId,
            labelIds: data.labelIds || [],
            projectId: data.projectId || null,
            cycleId: data.cycleId || null,
            parentIssueId: data.parentIssueId || null,
            estimate: data.estimate || null,
            dueDate: data.dueDate || null,
            sortOrder: this.issues.length + 1,
            createdAt: now,
            updatedAt: now,
            archivedAt: null,
            deletedAt: null,
        };
        this.issues.push(issue);
        this.notify();
        return issue;
    },

    updateIssue(issueId, data) {
        const issue = this.getIssueById(issueId);
        if (!issue) return null;
        Object.assign(issue, data, { updatedAt: new Date().toISOString() });
        this.notify();
        return issue;
    },

    deleteIssue(issueId) {
        const issue = this.getIssueById(issueId);
        if (!issue) return;
        issue.deletedAt = new Date().toISOString();
        issue.updatedAt = new Date().toISOString();
        this.notify();
    },

    restoreIssue(issueId) {
        const issue = this.getIssueById(issueId);
        if (!issue) return;
        issue.deletedAt = null;
        issue.updatedAt = new Date().toISOString();
        this.notify();
    },

    moveIssueToTeam(issueId, newTeamId) {
        const issue = this.getIssueById(issueId);
        if (!issue) return;
        const oldTeam = this.getTeamById(issue.teamId);
        const newTeam = this.getTeamById(newTeamId);
        if (!oldTeam || !newTeam) return;

        // Generate new identifier
        newTeam.issueCounter++;
        issue.identifier = `${newTeam.identifier}-${newTeam.issueCounter}`;
        issue.teamId = newTeamId;

        // Remap status: match by name first, then category, then fallback
        const oldStatus = this.getStatusById(issue.statusId);
        let newStatus = null;
        if (oldStatus) {
            newStatus = newTeam.statuses.find(s => s.name === oldStatus.name);
            if (!newStatus) newStatus = newTeam.statuses.find(s => s.category === oldStatus.category);
        }
        if (!newStatus) newStatus = newTeam.statuses[0];
        issue.statusId = newStatus.id;

        // Remove cycle (team-specific)
        issue.cycleId = null;
        // Remove team-scoped labels
        issue.labelIds = issue.labelIds.filter(lid => {
            const label = this.getLabelById(lid);
            return label && (label.scope === 'workspace' || label.teamId === newTeamId);
        });
        // Remove project if not associated with new team
        if (issue.projectId) {
            const project = this.getProjectById(issue.projectId);
            if (project && !project.teamIds.includes(newTeamId)) {
                issue.projectId = null;
            }
        }
        issue.updatedAt = new Date().toISOString();
        this.notify();
    },

    addLabelToIssue(issueId, labelId) {
        const issue = this.getIssueById(issueId);
        const label = this.getLabelById(labelId);
        if (!issue || !label) return;
        if (issue.labelIds.includes(labelId)) return;

        // Enforce label group constraint: one label per group
        if (label.groupId) {
            const groupLabels = this.getLabelsInGroup(label.groupId);
            const groupLabelIds = groupLabels.map(l => l.id);
            issue.labelIds = issue.labelIds.filter(id => !groupLabelIds.includes(id));
        }
        issue.labelIds.push(labelId);
        issue.updatedAt = new Date().toISOString();
        this.notify();
    },

    removeLabelFromIssue(issueId, labelId) {
        const issue = this.getIssueById(issueId);
        if (!issue) return;
        issue.labelIds = issue.labelIds.filter(id => id !== labelId);
        issue.updatedAt = new Date().toISOString();
        this.notify();
    },

    addComment(issueId, body, parentCommentId = null) {
        const now = new Date().toISOString();
        const comment = {
            id: `comment-${this._nextCommentId++}`,
            issueId,
            body,
            userId: this.currentUserId,
            parentCommentId: parentCommentId || null,
            resolved: false,
            createdAt: now,
            updatedAt: now,
        };
        this.comments.push(comment);
        this.notify();
        return comment;
    },

    updateComment(commentId, body) {
        const comment = this.comments.find(c => c.id === commentId);
        if (!comment) return;
        comment.body = body;
        comment.updatedAt = new Date().toISOString();
        this.notify();
    },

    deleteComment(commentId) {
        this.comments = this.comments.filter(c => c.id !== commentId);
        this.notify();
    },

    resolveThread(commentId) {
        const comment = this.comments.find(c => c.id === commentId);
        if (!comment) return;
        comment.resolved = !comment.resolved;
        comment.updatedAt = new Date().toISOString();
        this.notify();
    },

    addRelation(issueId, relatedIssueId, type) {
        // Check for existing relation
        const exists = this.issueRelations.some(r =>
            (r.issueId === issueId && r.relatedIssueId === relatedIssueId) ||
            (r.issueId === relatedIssueId && r.relatedIssueId === issueId)
        );
        if (exists) return null;

        const relation = {
            id: `rel-${this._nextRelationId++}`,
            issueId,
            relatedIssueId,
            type,
        };
        this.issueRelations.push(relation);

        // Duplicate side effect: auto-cancel the issue
        if (type === 'duplicate') {
            const issue = this.getIssueById(issueId);
            if (issue) {
                const team = this.getTeamById(issue.teamId);
                if (team) {
                    const canceledStatus = team.statuses.find(s => s.category === 'canceled');
                    if (canceledStatus) {
                        issue.statusId = canceledStatus.id;
                        issue.updatedAt = new Date().toISOString();
                    }
                }
            }
        }

        this.notify();
        return relation;
    },

    removeRelation(relationId) {
        this.issueRelations = this.issueRelations.filter(r => r.id !== relationId);
        this.notify();
    },

    createLabel(data) {
        // Validate reserved names
        if (RESERVED_LABEL_NAMES.includes(data.name.toLowerCase())) {
            return { error: `"${data.name}" is a reserved label name.` };
        }
        const label = {
            id: `label-${this._nextLabelId++}`,
            name: data.name,
            color: data.color || '#6b7280',
            description: data.description || '',
            scope: data.scope || 'workspace',
            teamId: data.teamId || null,
            groupId: data.groupId || null,
            archived: false,
        };
        this.labels.push(label);
        this.notify();
        return label;
    },

    updateLabel(labelId, data) {
        const label = this.getLabelById(labelId);
        if (!label) return null;
        Object.assign(label, data);
        this.notify();
        return label;
    },

    deleteLabel(labelId) {
        // Remove from all issues
        this.issues.forEach(i => {
            i.labelIds = i.labelIds.filter(id => id !== labelId);
        });
        this.labels = this.labels.filter(l => l.id !== labelId);
        this.notify();
    },

    createLabelGroup(data) {
        const group = {
            id: `lg-${this._nextLabelGroupId++}`,
            name: data.name,
            scope: data.scope || 'workspace',
            teamId: data.teamId || null,
            color: data.color || '#6b7280',
        };
        this.labelGroups.push(group);
        this.notify();
        return group;
    },

    updateLabelGroup(groupId, data) {
        const group = this.getLabelGroupById(groupId);
        if (!group) return null;
        Object.assign(group, data);
        this.notify();
        return group;
    },

    deleteLabelGroup(groupId) {
        // Ungroup labels in this group
        this.labels.forEach(l => {
            if (l.groupId === groupId) l.groupId = null;
        });
        this.labelGroups = this.labelGroups.filter(g => g.id !== groupId);
        this.notify();
    },

    updateTeamSettings(teamId, settings) {
        const team = this.getTeamById(teamId);
        if (!team) return;
        Object.assign(team.settings, settings);
        this.notify();
    },

    createTemplate(data) {
        const template = {
            id: `template-${this._nextTemplateId++}`,
            name: data.name,
            description: data.description || '',
            teamId: data.teamId || null,
            defaultPriority: data.defaultPriority || getPriorityByName('No priority'),
            defaultLabelIds: data.defaultLabelIds || [],
            defaultEstimate: data.defaultEstimate || null,
            templateDescription: data.templateDescription || '',
            createdAt: new Date().toISOString(),
        };
        this.templates.push(template);
        this.notify();
        return template;
    },

    updateTemplate(templateId, data) {
        const template = this.getTemplateById(templateId);
        if (!template) return null;
        Object.assign(template, data);
        this.notify();
        return template;
    },

    deleteTemplate(templateId) {
        this.templates = this.templates.filter(t => t.id !== templateId);
        this.notify();
    },

    createCustomer(data) {
        const customer = {
            id: `customer-${this._nextCustomerId++}`,
            name: data.name,
            domain: data.domain || '',
            tier: data.tier || 'Free',
            contactName: data.contactName || '',
            contactEmail: data.contactEmail || '',
            revenue: data.revenue || 0,
            createdAt: new Date().toISOString(),
        };
        this.customers.push(customer);
        this.notify();
        return customer;
    },

    addCustomerRequest(data) {
        const request = {
            id: `cr-${this._nextCustomerRequestId++}`,
            customerId: data.customerId,
            issueId: data.issueId || null,
            title: data.title || '',
            description: data.description || '',
            priority: data.priority || 'medium',
            createdAt: new Date().toISOString(),
        };
        this.customerRequests.push(request);
        this.notify();
        return request;
    },

    createProject(data) {
        const project = {
            id: `project-${Date.now()}`,
            name: data.name,
            description: data.description || '',
            color: data.color || '#6366f1',
            status: data.status || 'planned',
            leadId: data.leadId || null,
            teamIds: data.teamIds || [],
            startDate: data.startDate || null,
            targetDate: data.targetDate || null,
            createdAt: new Date().toISOString(),
        };
        this.projects.push(project);
        this.notify();
        return project;
    },

    createCycle(data) {
        const cycle = {
            id: `cycle-${Date.now()}`,
            name: data.name,
            teamId: data.teamId,
            startDate: data.startDate || null,
            endDate: data.endDate || null,
            status: data.status || 'upcoming',
        };
        this.cycles.push(cycle);
        this.notify();
        return cycle;
    },
};
