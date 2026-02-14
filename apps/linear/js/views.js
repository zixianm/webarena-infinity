// ============================================================
// Linear Issue Management — Views
// ============================================================

const Views = {

    // ── My Issues (Home) ────────────────────────────────────
    myIssues() {
        const issues = AppState.getMyIssues();
        const teamGroups = {};
        issues.forEach(i => {
            if (!teamGroups[i.teamId]) teamGroups[i.teamId] = [];
            teamGroups[i.teamId].push(i);
        });

        let content = '';
        for (const [teamId, teamIssues] of Object.entries(teamGroups)) {
            const team = AppState.getTeamById(teamId);
            if (!team) continue;
            content += `<div class="status-group">
                <div class="status-group-header">
                    <span>${team.icon} ${Components.esc(team.name)}</span>
                    <span class="status-group-count">${teamIssues.length}</span>
                </div>
                <div class="issue-list">${teamIssues.map(i => Components.issueRow(i)).join('')}</div>
            </div>`;
        }

        if (!content) content = '<div class="empty-state"><div class="empty-state-icon">📋</div><div class="empty-state-text">No issues assigned to you</div></div>';

        return `<div class="page-container" data-testid="my-issues-view">
            <div class="page-header">
                <div><div class="page-title">My Issues</div><div class="page-subtitle">Issues assigned to you</div></div>
            </div>
            ${content}
        </div>`;
    },

    // ── Team Issue List ─────────────────────────────────────
    teamIssueList(teamId) {
        const team = AppState.getTeamById(teamId);
        if (!team) return Views._notFound('Team not found');
        const issues = AppState.getIssuesForTeam(teamId);

        // Group by status
        const statusGroups = {};
        team.statuses.forEach(s => { statusGroups[s.id] = []; });
        issues.forEach(i => {
            if (statusGroups[i.statusId]) statusGroups[i.statusId].push(i);
        });

        let content = '';
        team.statuses.forEach(s => {
            const groupIssues = statusGroups[s.id] || [];
            if (groupIssues.length === 0) return;
            content += `<div class="status-group">
                <div class="status-group-header">
                    ${Components.statusDot(s)}
                    <span>${Components.esc(s.name)}</span>
                    <span class="status-group-count">${groupIssues.length}</span>
                </div>
                <div class="issue-list">${groupIssues.map(i => Components.issueRow(i)).join('')}</div>
            </div>`;
        });

        if (!content) content = '<div class="empty-state"><div class="empty-state-icon">📋</div><div class="empty-state-text">No issues in this team</div></div>';

        return `<div class="page-container" data-testid="team-issues-view">
            <div class="page-header">
                <div><div class="page-title">${team.icon} ${Components.esc(team.name)}</div><div class="page-subtitle">${Components.esc(team.identifier)} · ${issues.length} issues</div></div>
                <div class="flex gap-2">
                    <button class="btn btn-secondary" data-route="/team/${teamId}/board" data-testid="view-board-btn">Board</button>
                    <button class="btn btn-primary" data-action="create-issue" data-team-id="${teamId}" data-testid="create-issue-btn">New Issue</button>
                </div>
            </div>
            <div class="filter-bar" data-testid="filter-bar">
                <span class="filter-chip active" data-filter="all" data-testid="filter-all">All</span>
                ${PRIORITIES.filter(p => p.value > 0).map(p => `<span class="filter-chip" data-filter="priority-${p.value}" data-testid="filter-${p.name.toLowerCase()}">${p.icon} ${p.name}</span>`).join('')}
            </div>
            ${content}
        </div>`;
    },

    // ── Board View ──────────────────────────────────────────
    teamBoard(teamId) {
        const team = AppState.getTeamById(teamId);
        if (!team) return Views._notFound('Team not found');
        const issues = AppState.getIssuesForTeam(teamId);

        const columns = team.statuses.map(status => {
            const columnIssues = issues.filter(i => i.statusId === status.id);
            return `<div class="board-column" data-status-id="${status.id}" data-testid="board-column-${status.name.toLowerCase().replace(/\s+/g, '-')}">
                <div class="board-column-header">
                    ${Components.statusDot(status)}
                    <span>${Components.esc(status.name)}</span>
                    <span class="board-column-count">${columnIssues.length}</span>
                </div>
                <div class="board-column-body">
                    ${columnIssues.map(i => Components.boardCard(i)).join('')}
                </div>
            </div>`;
        });

        return `<div class="page-container" data-testid="team-board-view" style="max-width:none">
            <div class="page-header">
                <div><div class="page-title">${team.icon} ${Components.esc(team.name)} — Board</div></div>
                <div class="flex gap-2">
                    <button class="btn btn-secondary" data-route="/team/${teamId}" data-testid="view-list-btn">List</button>
                    <button class="btn btn-primary" data-action="create-issue" data-team-id="${teamId}" data-testid="create-issue-btn">New Issue</button>
                </div>
            </div>
            <div class="board-container">${columns.join('')}</div>
        </div>`;
    },

    // ── Issue Detail ────────────────────────────────────────
    issueDetail(issueId) {
        const issue = AppState.issues.find(i => i.id === issueId);
        if (!issue) return Views._notFound('Issue not found');
        const team = AppState.getTeamById(issue.teamId);
        const status = AppState.getStatusById(issue.statusId);
        const assignee = issue.assigneeId ? AppState.getUserById(issue.assigneeId) : null;
        const creator = AppState.getUserById(issue.creatorId);
        const labels = (issue.labelIds || []).map(id => AppState.getLabelById(id)).filter(Boolean);
        const project = issue.projectId ? AppState.getProjectById(issue.projectId) : null;
        const cycle = issue.cycleId ? AppState.getCycleById(issue.cycleId) : null;
        const parentIssue = issue.parentIssueId ? AppState.getIssueById(issue.parentIssueId) : null;
        const subIssues = AppState.getSubIssues(issue.id);
        const relations = AppState.getIssueRelations(issue.id);
        const comments = AppState.getCommentsForIssue(issue.id);
        const customerRequests = AppState.getCustomerRequestsForIssue(issue.id);

        // Build property sidebar items
        const statusItems = (team ? team.statuses : []).map(s => ({
            value: s.id, label: s.name, selected: s.id === issue.statusId,
            icon: `<span class="issue-status-dot ${s.category}" style="width:12px;height:12px"></span>`
        }));

        const priorityItems = PRIORITIES.map(p => ({
            value: String(p.value), label: p.name, selected: issue.priority && issue.priority.value === p.value,
            icon: `<span style="color:${p.color}">${p.icon}</span>`
        }));

        const assigneeItems = [{ value: '', label: 'Unassigned', selected: !issue.assigneeId }]
            .concat(AppState.users.map(u => ({
                value: u.id, label: u.name, selected: u.id === issue.assigneeId,
                icon: Components.userAvatar(u, 18)
            })));

        const availableLabels = team ? AppState.getLabelsForTeam(team.id) : [];

        const teamItems = AppState.teams.map(t => ({
            value: t.id, label: `${t.icon} ${t.name}`, selected: t.id === issue.teamId
        }));

        const projectItems = [{ value: '', label: 'No project', selected: !issue.projectId }]
            .concat(AppState.projects.map(p => ({
                value: p.id, label: p.name, selected: p.id === issue.projectId
            })));

        const teamCycles = team ? AppState.getCyclesForTeam(team.id) : [];
        const cycleItems = [{ value: '', label: 'No cycle', selected: !issue.cycleId }]
            .concat(teamCycles.map(c => ({
                value: c.id, label: c.name, selected: c.id === issue.cycleId
            })));

        // Estimate
        let estimateScale = [];
        if (team && team.settings.estimatesEnabled) {
            estimateScale = ESTIMATE_SCALES[team.settings.estimateScale] || [];
        }

        const deletedBanner = issue.deletedAt ?
            `<div class="deleted-banner" data-testid="deleted-banner">
                This issue has been deleted.
                <button class="btn btn-sm btn-secondary" data-action="restore-issue" data-issue-id="${issue.id}" data-testid="restore-issue-btn">Restore</button>
            </div>` : '';

        // Relations HTML
        const relationsHtml = relations.map(r => {
            const relIssue = AppState.getIssueById(r.relatedIssueId);
            if (!relIssue) return '';
            return `<div class="relation-row" data-testid="relation-${r.id}">
                <span class="relation-type ${r.type}">${r.type}</span>
                <span class="cursor-pointer" data-route="/issue/${relIssue.id}">${Components.esc(relIssue.identifier)} ${Components.esc(relIssue.title)}</span>
                <span class="relation-remove" data-action="remove-relation" data-relation-id="${r.id}" title="Remove relation">×</span>
            </div>`;
        }).join('');

        // Comments HTML
        const topLevelComments = comments.filter(c => !c.parentCommentId);
        const commentsHtml = topLevelComments.map(c => {
            const author = AppState.getUserById(c.userId);
            const replies = comments.filter(r => r.parentCommentId === c.id);
            const repliesHtml = replies.map(r => {
                const rAuthor = AppState.getUserById(r.userId);
                return `<div class="comment-item threaded${r.resolved ? ' comment-resolved' : ''}" data-comment-id="${r.id}" data-testid="comment-${r.id}">
                    <div class="comment-header">
                        ${Components.userAvatar(rAuthor, 20)}
                        <span class="comment-author">${Components.esc(rAuthor ? rAuthor.name : 'Unknown')}</span>
                        <span class="comment-time">${Components.relativeTime(r.createdAt)}</span>
                    </div>
                    <div class="comment-body">${Components.esc(r.body)}</div>
                    <div class="comment-actions">
                        <button class="btn btn-ghost btn-sm" data-action="delete-comment" data-comment-id="${r.id}">Delete</button>
                    </div>
                </div>`;
            }).join('');

            return `<div class="comment-item${c.resolved ? ' comment-resolved' : ''}" data-comment-id="${c.id}" data-testid="comment-${c.id}">
                <div class="comment-header">
                    ${Components.userAvatar(author, 24)}
                    <span class="comment-author">${Components.esc(author ? author.name : 'Unknown')}</span>
                    <span class="comment-time">${Components.relativeTime(c.createdAt)}</span>
                </div>
                <div class="comment-body">${Components.esc(c.body)}</div>
                <div class="comment-actions">
                    <button class="btn btn-ghost btn-sm" data-action="reply-comment" data-comment-id="${c.id}">Reply</button>
                    <button class="btn btn-ghost btn-sm" data-action="resolve-thread" data-comment-id="${c.id}">${c.resolved ? 'Unresolve' : 'Resolve'}</button>
                    <button class="btn btn-ghost btn-sm" data-action="delete-comment" data-comment-id="${c.id}">Delete</button>
                </div>
                ${repliesHtml}
            </div>`;
        }).join('');

        // Sub issues HTML
        const subIssuesHtml = subIssues.map(si => {
            const siStatus = AppState.getStatusById(si.statusId);
            return `<div class="sub-issue-row" data-issue-id="${si.id}" data-testid="sub-issue-${si.identifier}">
                ${Components.statusDot(siStatus)}
                <span class="issue-identifier">${Components.esc(si.identifier)}</span>
                <span class="issue-title-text">${Components.esc(si.title)}</span>
                ${Components.priorityIcon(si.priority)}
            </div>`;
        }).join('');

        // Customer requests HTML
        const crHtml = customerRequests.map(cr => {
            const customer = AppState.getCustomerById(cr.customerId);
            return `<div style="padding:4px 0;font-size:12px">
                <span class="fw-600">${Components.esc(customer ? customer.name : 'Unknown')}</span>: ${Components.esc(cr.title)}
            </div>`;
        }).join('');

        return `<div class="issue-detail-layout" data-testid="issue-detail-view">
            <div class="issue-detail-main">
                ${deletedBanner}
                ${parentIssue ? `<div class="mb-2 text-sm"><span class="cursor-pointer text-muted" data-route="/issue/${parentIssue.id}">${Components.esc(parentIssue.identifier)} ${Components.esc(parentIssue.title)}</span> ›</div>` : ''}
                <div class="issue-detail-identifier" data-testid="issue-identifier">${Components.esc(issue.identifier)}</div>
                <div class="issue-detail-title" contenteditable="true" data-testid="issue-title" data-issue-id="${issue.id}">${Components.esc(issue.title)}</div>
                <div class="mt-4">
                    <textarea class="issue-description" data-testid="issue-description" data-issue-id="${issue.id}" placeholder="Add a description...">${Components.esc(issue.description)}</textarea>
                </div>

                ${subIssues.length > 0 || true ? `<div class="sub-issues-section mt-4">
                    <div class="flex items-center justify-between mb-2">
                        <span class="property-section-title">Sub-issues</span>
                        <button class="btn btn-ghost btn-sm" data-action="add-sub-issue" data-parent-id="${issue.id}" data-team-id="${issue.teamId}" data-testid="add-sub-issue-btn">+ Add</button>
                    </div>
                    ${subIssuesHtml || '<div class="text-sm text-muted">No sub-issues</div>'}
                </div>` : ''}

                ${relations.length > 0 || true ? `<div class="relations-section mt-4">
                    <div class="flex items-center justify-between mb-2">
                        <span class="property-section-title">Relations</span>
                        <button class="btn btn-ghost btn-sm" data-action="add-relation" data-issue-id="${issue.id}" data-testid="add-relation-btn">+ Add</button>
                    </div>
                    ${relationsHtml || '<div class="text-sm text-muted">No relations</div>'}
                </div>` : ''}

                ${crHtml ? `<div class="mt-4"><div class="property-section-title mb-2">Customer Requests</div>${crHtml}</div>` : ''}

                <div class="comment-list mt-4">
                    <div class="property-section-title mb-2">Activity</div>
                    ${commentsHtml || '<div class="text-sm text-muted">No comments yet</div>'}
                    <div class="comment-input-area" data-testid="comment-input-area">
                        <textarea class="comment-input" id="commentInput" data-testid="comment-input" placeholder="Write a comment..."></textarea>
                        <div class="flex justify-between">
                            <span></span>
                            <button class="btn btn-primary btn-sm" data-action="post-comment" data-issue-id="${issue.id}" data-testid="post-comment-btn">Comment</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="issue-detail-sidebar" data-testid="issue-sidebar">
                <div class="property-section">
                    <div class="property-section-title">Properties</div>

                    <div class="property-row">
                        <span class="property-label">Status</span>
                        <div class="property-value inline-selector" data-prop="statusId" data-issue-id="${issue.id}" data-testid="prop-status">
                            ${status ? `${Components.statusDot(status)} ${Components.esc(status.name)}` : 'Set status'}
                        </div>
                    </div>

                    <div class="property-row">
                        <span class="property-label">Priority</span>
                        <div class="property-value inline-selector" data-prop="priority" data-issue-id="${issue.id}" data-testid="prop-priority">
                            ${Components.priorityIcon(issue.priority)} ${Components.esc(issue.priority ? issue.priority.name : 'No priority')}
                        </div>
                    </div>

                    <div class="property-row">
                        <span class="property-label">Assignee</span>
                        <div class="property-value inline-selector" data-prop="assigneeId" data-issue-id="${issue.id}" data-testid="prop-assignee">
                            ${assignee ? `${Components.userAvatar(assignee, 18)} ${Components.esc(assignee.name)}` : '<span class="empty">Unassigned</span>'}
                        </div>
                    </div>

                    <div class="property-row">
                        <span class="property-label">Labels</span>
                        <div class="property-value inline-selector" data-prop="labels" data-issue-id="${issue.id}" data-testid="prop-labels">
                            ${labels.length > 0 ? labels.map(l => Components.labelBadge(l)).join(' ') : '<span class="empty">No labels</span>'}
                        </div>
                    </div>

                    <div class="property-row">
                        <span class="property-label">Team</span>
                        <div class="property-value inline-selector" data-prop="team" data-issue-id="${issue.id}" data-testid="prop-team">
                            ${team ? `${team.icon} ${Components.esc(team.name)}` : 'No team'}
                        </div>
                    </div>

                    <div class="property-row">
                        <span class="property-label">Project</span>
                        <div class="property-value inline-selector" data-prop="projectId" data-issue-id="${issue.id}" data-testid="prop-project">
                            ${project ? Components.esc(project.name) : '<span class="empty">No project</span>'}
                        </div>
                    </div>

                    <div class="property-row">
                        <span class="property-label">Cycle</span>
                        <div class="property-value inline-selector" data-prop="cycleId" data-issue-id="${issue.id}" data-testid="prop-cycle">
                            ${cycle ? Components.esc(cycle.name) : '<span class="empty">No cycle</span>'}
                        </div>
                    </div>

                    <div class="property-row">
                        <span class="property-label">Estimate</span>
                        <div class="property-value inline-selector" data-prop="estimate" data-issue-id="${issue.id}" data-testid="prop-estimate">
                            ${issue.estimate != null ? issue.estimate : '<span class="empty">No estimate</span>'}
                        </div>
                    </div>

                    <div class="property-row">
                        <span class="property-label">Due date</span>
                        <div class="property-value inline-selector" data-prop="dueDate" data-issue-id="${issue.id}" data-testid="prop-due-date">
                            ${issue.dueDate || '<span class="empty">No due date</span>'}
                        </div>
                    </div>
                </div>

                <div class="property-section mt-4">
                    <div class="property-row">
                        <span class="property-label">Created</span>
                        <span class="text-sm text-muted">${Components.formatDate(issue.createdAt)}</span>
                    </div>
                    <div class="property-row">
                        <span class="property-label">Updated</span>
                        <span class="text-sm text-muted">${Components.relativeTime(issue.updatedAt)}</span>
                    </div>
                    ${creator ? `<div class="property-row"><span class="property-label">Creator</span><span class="text-sm">${Components.userAvatar(creator, 18)} ${Components.esc(creator.name)}</span></div>` : ''}
                </div>

                <div class="mt-4">
                    ${!issue.deletedAt ? `<button class="btn btn-danger btn-sm" data-action="delete-issue" data-issue-id="${issue.id}" data-testid="delete-issue-btn">Delete issue</button>` : ''}
                </div>
            </div>
        </div>`;
    },

    // ── Cycles View ─────────────────────────────────────────
    teamCycles(teamId) {
        const team = AppState.getTeamById(teamId);
        if (!team) return Views._notFound('Team not found');
        const cycles = AppState.getCyclesForTeam(teamId);

        const cyclesHtml = cycles.map(c => {
            const issues = AppState.getIssuesForCycle(c.id);
            const completed = issues.filter(i => { const s = AppState.getStatusById(i.statusId); return s && s.category === 'completed'; }).length;
            const progress = issues.length > 0 ? Math.round((completed / issues.length) * 100) : 0;

            return `<div class="cycle-card" data-testid="cycle-${c.id}">
                <div class="cycle-card-header">
                    <span class="cycle-card-name">${Components.esc(c.name)}</span>
                    <span class="cycle-status-badge ${c.status}">${c.status}</span>
                </div>
                <div class="cycle-dates">${Components.formatDate(c.startDate)} — ${Components.formatDate(c.endDate)}</div>
                <div class="cycle-progress">
                    <div class="flex justify-between text-xs text-muted mb-1">
                        <span>${issues.length} issues</span>
                        <span>${progress}% complete</span>
                    </div>
                    <div class="cycle-progress-bar"><div class="cycle-progress-fill" style="width:${progress}%"></div></div>
                </div>
            </div>`;
        }).join('');

        return `<div class="page-container" data-testid="cycles-view">
            <div class="page-header">
                <div><div class="page-title">${team.icon} ${Components.esc(team.name)} — Cycles</div></div>
            </div>
            ${cyclesHtml || '<div class="empty-state"><div class="empty-state-text">No cycles</div></div>'}
        </div>`;
    },

    // ── Team Settings ───────────────────────────────────────
    teamSettings(teamId) {
        const team = AppState.getTeamById(teamId);
        if (!team) return Views._notFound('Team not found');
        const s = team.settings;

        const scaleItems = Object.keys(ESTIMATE_SCALES).map(name => ({
            value: name, label: name, selected: name === s.estimateScale
        }));

        return `<div class="page-container" data-testid="team-settings-view">
            <div class="page-header">
                <div><div class="page-title">${team.icon} ${Components.esc(team.name)} — Settings</div></div>
            </div>

            <div class="settings-section">
                <div class="settings-title">Estimates</div>
                ${Components.toggle('toggleEstimates', s.estimatesEnabled, 'Enable estimates')}
                <div class="settings-row">
                    <span class="settings-label">Estimate scale</span>
                    <div class="custom-dropdown" id="estimateScaleDropdown" data-testid="estimate-scale-dropdown">
                        <div class="dropdown-trigger">${Components.esc(s.estimateScale)}</div>
                        <div class="dropdown-menu">
                            ${scaleItems.map(item => `<div class="dropdown-item${item.selected ? ' selected' : ''}" data-value="${Components.esc(item.value)}">${Components.esc(item.label)}</div>`).join('')}
                        </div>
                    </div>
                </div>
            </div>

            <div class="settings-section">
                <div class="settings-title">Workflow</div>
                <div class="settings-row">
                    <span class="settings-label">Auto-close period (months)</span>
                    <input type="text" class="form-input" style="width:60px" id="autoClosePeriod" value="${s.autoClosePeriod}" data-testid="auto-close-period">
                </div>
                <div class="settings-row">
                    <span class="settings-label">Auto-archive period (months)</span>
                    <input type="text" class="form-input" style="width:60px" id="autoArchivePeriod" value="${s.autoArchivePeriod}" data-testid="auto-archive-period">
                </div>
            </div>

            <button class="btn btn-primary" id="saveTeamSettings" data-team-id="${teamId}" data-testid="save-settings-btn">Save Settings</button>
        </div>`;
    },

    // ── Team Labels ─────────────────────────────────────────
    teamLabels(teamId) {
        const team = AppState.getTeamById(teamId);
        if (!team) return Views._notFound('Team not found');
        const labels = AppState.getLabelsForTeam(teamId);
        return this._labelsView(labels, `${team.icon} ${team.name} — Labels`, teamId);
    },

    // ── Workspace Labels ────────────────────────────────────
    workspaceLabels() {
        const labels = AppState.labels.filter(l => !l.archived);
        return this._labelsView(labels, 'Workspace Labels', null);
    },

    _labelsView(labels, title, teamId) {
        // Group labels: grouped ones first, then ungrouped
        const grouped = {};
        const ungrouped = [];
        labels.forEach(l => {
            if (l.groupId) {
                if (!grouped[l.groupId]) grouped[l.groupId] = [];
                grouped[l.groupId].push(l);
            } else {
                ungrouped.push(l);
            }
        });

        let content = '';
        // Label groups
        for (const [groupId, groupLabels] of Object.entries(grouped)) {
            const group = AppState.getLabelGroupById(groupId);
            if (!group) continue;
            content += `<div class="label-group-row" data-testid="label-group-${groupId}">
                <span class="label-color-swatch" style="background:${group.color}"></span>
                ${Components.esc(group.name)} <span class="text-xs text-muted">(${groupLabels.length})</span>
            </div>`;
            content += groupLabels.map(l => `<div class="label-row" data-label-id="${l.id}" data-testid="label-row-${l.id}">
                <span class="label-color-swatch" style="background:${l.color}"></span>
                <span class="label-name">${Components.esc(l.name)}</span>
                <span class="label-description">${Components.esc(l.description)}</span>
                <span class="label-scope-badge">${l.scope}</span>
            </div>`).join('');
        }

        // Ungrouped
        if (ungrouped.length > 0) {
            content += ungrouped.map(l => `<div class="label-row" data-label-id="${l.id}" data-testid="label-row-${l.id}">
                <span class="label-color-swatch" style="background:${l.color}"></span>
                <span class="label-name">${Components.esc(l.name)}</span>
                <span class="label-description">${Components.esc(l.description)}</span>
                <span class="label-scope-badge">${l.scope}</span>
            </div>`).join('');
        }

        return `<div class="page-container" data-testid="labels-view">
            <div class="page-header">
                <div><div class="page-title">${title}</div></div>
                <div class="flex gap-2">
                    <button class="btn btn-secondary" data-action="create-label-group" data-team-id="${teamId || ''}" data-testid="create-label-group-btn">New Group</button>
                    <button class="btn btn-primary" data-action="create-label" data-team-id="${teamId || ''}" data-testid="create-label-btn">New Label</button>
                </div>
            </div>
            <div class="label-list" data-testid="label-list">${content || '<div class="empty-state"><div class="empty-state-text">No labels</div></div>'}</div>
        </div>`;
    },

    // ── Templates View ──────────────────────────────────────
    templates() {
        const templates = AppState.templates;
        const templatesHtml = templates.map(t =>
            `<div class="template-card" data-template-id="${t.id}" data-testid="template-${t.id}">
                <div class="template-card-name">${Components.esc(t.name)}</div>
                <div class="template-card-desc">${Components.esc(t.description)}</div>
                <div class="text-xs text-muted mt-2">
                    Default priority: ${Components.esc(t.defaultPriority ? t.defaultPriority.name : 'None')}
                    ${t.defaultLabelIds.length > 0 ? ' · Labels: ' + t.defaultLabelIds.map(id => { const l = AppState.getLabelById(id); return l ? l.name : ''; }).filter(Boolean).join(', ') : ''}
                </div>
            </div>`
        ).join('');

        return `<div class="page-container" data-testid="templates-view">
            <div class="page-header">
                <div><div class="page-title">Templates</div><div class="page-subtitle">Issue templates for quick creation</div></div>
                <button class="btn btn-primary" data-action="create-template" data-testid="create-template-btn">New Template</button>
            </div>
            ${templatesHtml || '<div class="empty-state"><div class="empty-state-text">No templates</div></div>'}
        </div>`;
    },

    // ── Projects View ───────────────────────────────────────
    projects() {
        const projects = AppState.projects;
        const projectsHtml = projects.map(p => {
            const issues = AppState.getIssuesForProject(p.id);
            const lead = p.leadId ? AppState.getUserById(p.leadId) : null;
            return `<div class="project-card" data-project-id="${p.id}" data-testid="project-${p.id}">
                <div class="project-card-header">
                    <span class="project-color-dot" style="background:${p.color}"></span>
                    <span class="project-card-name">${Components.esc(p.name)}</span>
                </div>
                <div class="project-card-desc">${Components.esc(p.description)}</div>
                <div class="project-card-meta">
                    <span>${issues.length} issues</span>
                    <span>Status: ${p.status}</span>
                    ${lead ? `<span>Lead: ${Components.esc(lead.name)}</span>` : ''}
                    ${p.targetDate ? `<span>Target: ${Components.formatDate(p.targetDate)}</span>` : ''}
                </div>
            </div>`;
        }).join('');

        return `<div class="page-container" data-testid="projects-view">
            <div class="page-header">
                <div><div class="page-title">Projects</div></div>
            </div>
            ${projectsHtml || '<div class="empty-state"><div class="empty-state-text">No projects</div></div>'}
        </div>`;
    },

    // ── Customers View ──────────────────────────────────────
    customers() {
        const customers = AppState.customers;
        const customersHtml = customers.map(c => {
            const requests = AppState.getCustomerRequestsForCustomer(c.id);
            return `<div class="customer-card" data-customer-id="${c.id}" data-testid="customer-${c.id}">
                <div class="customer-card-header">
                    <span class="customer-name">${Components.esc(c.name)}</span>
                    <span class="customer-tier">${Components.esc(c.tier)}</span>
                </div>
                <div class="customer-meta">${Components.esc(c.domain)} · ${Components.esc(c.contactName)} · ${requests.length} requests</div>
            </div>`;
        }).join('');

        return `<div class="page-container" data-testid="customers-view">
            <div class="page-header">
                <div><div class="page-title">Customers</div></div>
                <button class="btn btn-primary" data-action="create-customer" data-testid="create-customer-btn">New Customer</button>
            </div>
            ${customersHtml || '<div class="empty-state"><div class="empty-state-text">No customers</div></div>'}
        </div>`;
    },

    // ── Not found ───────────────────────────────────────────
    _notFound(msg) {
        return `<div class="page-container"><div class="empty-state"><div class="empty-state-icon">🔍</div><div class="empty-state-text">${Components.esc(msg || 'Page not found')}</div></div></div>`;
    },
};
