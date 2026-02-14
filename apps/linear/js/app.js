// ============================================================
// Linear Issue Management — Router + Event Handlers + Init
// ============================================================

const Router = {
    routes: {
        '/':                   () => Views.myIssues(),
        '/team/:id':           (p) => Views.teamIssueList(p.id),
        '/team/:id/board':     (p) => Views.teamBoard(p.id),
        '/team/:id/cycles':    (p) => Views.teamCycles(p.id),
        '/team/:id/settings':  (p) => Views.teamSettings(p.id),
        '/team/:id/labels':    (p) => Views.teamLabels(p.id),
        '/issue/:id':          (p) => Views.issueDetail(p.id),
        '/labels':             () => Views.workspaceLabels(),
        '/templates':          () => Views.templates(),
        '/projects':           () => Views.projects(),
        '/customers':          () => Views.customers(),
    },

    navigate(path, skipHistory = false) {
        const [basePath] = path.split('?');
        AppState.currentRoute = basePath;
        if (!skipHistory) history.pushState({ path }, '', `#${path}`);
        this.render();
    },

    render() {
        const path = AppState.currentRoute;
        const contentWrapper = document.getElementById('contentWrapper');
        let html = null;

        for (const [pattern, handler] of Object.entries(this.routes)) {
            const match = this.matchRoute(pattern, path);
            if (match !== null) { html = handler(match); break; }
        }
        if (html === null) html = Views._notFound('Page not found');
        contentWrapper.innerHTML = html;

        // Update sidebar active state
        document.querySelectorAll('.sidebar-item').forEach(item => {
            const route = item.getAttribute('data-route');
            if (!route) return;
            if (route === path || (route !== '/' && path.startsWith(route))) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // Update breadcrumb
        this.updateBreadcrumb(path);
        this.attachHandlers();
    },

    matchRoute(pattern, path) {
        const pp = pattern.split('/');
        const pa = path.split('/');
        if (pp.length !== pa.length) return null;
        const params = {};
        for (let i = 0; i < pp.length; i++) {
            if (pp[i].startsWith(':')) params[pp[i].substring(1)] = pa[i];
            else if (pp[i] !== pa[i]) return null;
        }
        return params;
    },

    updateBreadcrumb(path) {
        const bc = document.getElementById('breadcrumb');
        if (!bc) return;
        const parts = [];

        if (path === '/') {
            parts.push({ label: 'My Issues', route: '/' });
        } else if (path.startsWith('/team/')) {
            const segments = path.split('/');
            const teamId = segments[2];
            const team = AppState.getTeamById(teamId);
            if (team) {
                parts.push({ label: team.name, route: `/team/${teamId}` });
                if (segments[3] === 'board') parts.push({ label: 'Board' });
                else if (segments[3] === 'cycles') parts.push({ label: 'Cycles' });
                else if (segments[3] === 'settings') parts.push({ label: 'Settings' });
                else if (segments[3] === 'labels') parts.push({ label: 'Labels' });
            }
        } else if (path.startsWith('/issue/')) {
            const issueId = path.split('/')[2];
            const issue = AppState.getIssueById(issueId);
            if (issue) {
                const team = AppState.getTeamById(issue.teamId);
                if (team) parts.push({ label: team.name, route: `/team/${team.id}` });
                parts.push({ label: issue.identifier });
            }
        } else if (path === '/labels') {
            parts.push({ label: 'Workspace Labels' });
        } else if (path === '/templates') {
            parts.push({ label: 'Templates' });
        } else if (path === '/projects') {
            parts.push({ label: 'Projects' });
        } else if (path === '/customers') {
            parts.push({ label: 'Customers' });
        }

        bc.innerHTML = parts.map((p, i) => {
            const isLast = i === parts.length - 1;
            if (p.route && !isLast) return `<a data-route="${p.route}">${Components.esc(p.label)}</a><span class="breadcrumb-separator">/</span>`;
            return `<span class="current">${Components.esc(p.label)}</span>`;
        }).join('');
    },

    // ── Attach event handlers ───────────────────────────────
    attachHandlers() {
        // Route links
        document.querySelectorAll('[data-route]').forEach(el => {
            if (el._routeHandler) return;
            el._routeHandler = true;
            el.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                Router.navigate(el.getAttribute('data-route'));
            });
        });

        // Issue row clicks -> navigate to detail
        document.querySelectorAll('.issue-row[data-issue-id], .board-card[data-issue-id], .sub-issue-row[data-issue-id]').forEach(el => {
            if (el._clickHandler) return;
            el._clickHandler = true;
            el.addEventListener('click', (e) => {
                if (e.target.closest('[data-action]') || e.target.closest('[data-route]')) return;
                Router.navigate(`/issue/${el.getAttribute('data-issue-id')}`);
            });
        });

        // Custom dropdown toggles
        document.querySelectorAll('.custom-dropdown .dropdown-trigger').forEach(trigger => {
            if (trigger._handler) return;
            trigger._handler = true;
            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                const menu = trigger.parentElement.querySelector('.dropdown-menu');
                const wasOpen = menu.classList.contains('open');
                document.querySelectorAll('.dropdown-menu.open').forEach(m => m.classList.remove('open'));
                if (!wasOpen) menu.classList.add('open');
            });
        });

        // Dropdown search
        document.querySelectorAll('.dropdown-search').forEach(input => {
            if (input._handler) return;
            input._handler = true;
            input.addEventListener('input', () => {
                const query = input.value.toLowerCase();
                const items = input.parentElement.querySelectorAll('.dropdown-item');
                items.forEach(item => {
                    const text = item.textContent.toLowerCase();
                    item.style.display = text.includes(query) ? '' : 'none';
                });
            });
            input.addEventListener('click', (e) => e.stopPropagation());
        });

        // Close dropdowns on outside click
        if (!document._dropdownClose) {
            document._dropdownClose = true;
            document.addEventListener('click', () => {
                document.querySelectorAll('.dropdown-menu.open').forEach(m => m.classList.remove('open'));
                document.querySelectorAll('.inline-selector-menu').forEach(m => m.remove());
            });
        }

        // ── Action handlers ──────────────────────────────
        this._attachActionHandlers();
        this._attachInlineSelectors();
        this._attachIssueDetailHandlers();
        this._attachSettingsHandlers();
        this._attachFilterHandlers();
    },

    // ── Action button handlers ──────────────────────────────
    _attachActionHandlers() {
        // Create issue button
        document.querySelectorAll('[data-action="create-issue"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => {
                const teamId = btn.getAttribute('data-team-id');
                ModalManager.showCreateIssueModal(teamId);
            });
        });

        // Delete issue
        document.querySelectorAll('[data-action="delete-issue"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => {
                const issueId = btn.getAttribute('data-issue-id');
                AppState.deleteIssue(issueId);
                Router.render();
                Components.showToast('Issue deleted', 'info');
            });
        });

        // Restore issue
        document.querySelectorAll('[data-action="restore-issue"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => {
                const issueId = btn.getAttribute('data-issue-id');
                AppState.restoreIssue(issueId);
                Router.render();
                Components.showToast('Issue restored', 'success');
            });
        });

        // Post comment
        document.querySelectorAll('[data-action="post-comment"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => {
                const issueId = btn.getAttribute('data-issue-id');
                const input = document.getElementById('commentInput');
                if (!input || !input.value.trim()) return;
                const parentId = input.getAttribute('data-reply-to') || null;
                AppState.addComment(issueId, input.value.trim(), parentId);
                Router.render();
                Components.showToast('Comment added', 'success');
            });
        });

        // Reply to comment
        document.querySelectorAll('[data-action="reply-comment"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => {
                const commentId = btn.getAttribute('data-comment-id');
                const input = document.getElementById('commentInput');
                if (input) {
                    input.setAttribute('data-reply-to', commentId);
                    input.placeholder = 'Write a reply...';
                    input.focus();
                }
            });
        });

        // Resolve thread
        document.querySelectorAll('[data-action="resolve-thread"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => {
                AppState.resolveThread(btn.getAttribute('data-comment-id'));
                Router.render();
            });
        });

        // Delete comment
        document.querySelectorAll('[data-action="delete-comment"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => {
                AppState.deleteComment(btn.getAttribute('data-comment-id'));
                Router.render();
                Components.showToast('Comment deleted', 'info');
            });
        });

        // Remove relation
        document.querySelectorAll('[data-action="remove-relation"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                AppState.removeRelation(btn.getAttribute('data-relation-id'));
                Router.render();
            });
        });

        // Add sub-issue
        document.querySelectorAll('[data-action="add-sub-issue"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => {
                const parentId = btn.getAttribute('data-parent-id');
                const teamId = btn.getAttribute('data-team-id');
                ModalManager.showCreateIssueModal(teamId, parentId);
            });
        });

        // Add relation
        document.querySelectorAll('[data-action="add-relation"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => {
                ModalManager.showAddRelationModal(btn.getAttribute('data-issue-id'));
            });
        });

        // Create label
        document.querySelectorAll('[data-action="create-label"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => {
                ModalManager.showCreateLabelModal(btn.getAttribute('data-team-id'));
            });
        });

        // Create label group
        document.querySelectorAll('[data-action="create-label-group"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => {
                ModalManager.showCreateLabelGroupModal(btn.getAttribute('data-team-id'));
            });
        });

        // Create template
        document.querySelectorAll('[data-action="create-template"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => {
                ModalManager.showCreateTemplateModal();
            });
        });

        // Template cards (create issue from template)
        document.querySelectorAll('.template-card[data-template-id]').forEach(card => {
            if (card._handler) return;
            card._handler = true;
            card.addEventListener('click', () => {
                ModalManager.showCreateIssueFromTemplateModal(card.getAttribute('data-template-id'));
            });
        });

        // Create customer
        document.querySelectorAll('[data-action="create-customer"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => {
                ModalManager.showCreateCustomerModal();
            });
        });

        // Add customer request
        document.querySelectorAll('[data-action="add-customer-request"]').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => {
                ModalManager.showAddCustomerRequestModal(btn.getAttribute('data-issue-id'));
            });
        });
    },

    // ── Inline property selectors ───────────────────────────
    _attachInlineSelectors() {
        document.querySelectorAll('.inline-selector[data-prop]').forEach(el => {
            if (el._handler) return;
            el._handler = true;
            el.addEventListener('click', (e) => {
                e.stopPropagation();
                const prop = el.getAttribute('data-prop');
                const issueId = el.getAttribute('data-issue-id');
                const issue = AppState.getIssueById(issueId);
                if (!issue) return;

                // Remove any existing menus
                document.querySelectorAll('.inline-selector-menu').forEach(m => m.remove());

                const menu = document.createElement('div');
                menu.className = 'inline-selector-menu';
                menu.style.position = 'absolute';
                menu.style.zIndex = '1000';

                let items = [];

                if (prop === 'statusId') {
                    const team = AppState.getTeamById(issue.teamId);
                    items = (team ? team.statuses : []).map(s => ({
                        value: s.id, label: s.name, selected: s.id === issue.statusId,
                        html: `${Components.statusDot(s)} ${Components.esc(s.name)}`
                    }));
                } else if (prop === 'priority') {
                    items = PRIORITIES.map(p => ({
                        value: String(p.value), label: p.name, selected: issue.priority && issue.priority.value === p.value,
                        html: `<span style="color:${p.color}">${p.icon}</span> ${Components.esc(p.name)}`
                    }));
                } else if (prop === 'assigneeId') {
                    items = [{ value: '', label: 'Unassigned', selected: !issue.assigneeId, html: 'Unassigned' }];
                    items = items.concat(AppState.users.map(u => ({
                        value: u.id, label: u.name, selected: u.id === issue.assigneeId,
                        html: `${Components.userAvatar(u, 18)} ${Components.esc(u.name)}`
                    })));
                } else if (prop === 'labels') {
                    const team = AppState.getTeamById(issue.teamId);
                    const available = team ? AppState.getLabelsForTeam(team.id) : [];
                    items = available.map(l => ({
                        value: l.id, label: l.name, selected: issue.labelIds.includes(l.id),
                        html: `<span class="label-dot" style="background:${l.color}"></span> ${Components.esc(l.name)}`
                    }));
                } else if (prop === 'team') {
                    items = AppState.teams.map(t => ({
                        value: t.id, label: t.name, selected: t.id === issue.teamId,
                        html: `${t.icon} ${Components.esc(t.name)}`
                    }));
                } else if (prop === 'projectId') {
                    items = [{ value: '', label: 'No project', selected: !issue.projectId, html: 'No project' }];
                    items = items.concat(AppState.projects.map(p => ({
                        value: p.id, label: p.name, selected: p.id === issue.projectId,
                        html: `<span class="project-color-dot" style="background:${p.color};width:10px;height:10px;border-radius:50%;display:inline-block"></span> ${Components.esc(p.name)}`
                    })));
                } else if (prop === 'cycleId') {
                    const team = AppState.getTeamById(issue.teamId);
                    const cycles = team ? AppState.getCyclesForTeam(team.id) : [];
                    items = [{ value: '', label: 'No cycle', selected: !issue.cycleId, html: 'No cycle' }];
                    items = items.concat(cycles.map(c => ({
                        value: c.id, label: c.name, selected: c.id === issue.cycleId,
                        html: `${Components.esc(c.name)} <span class="text-xs text-muted">(${c.status})</span>`
                    })));
                } else if (prop === 'estimate') {
                    const team = AppState.getTeamById(issue.teamId);
                    const scale = team && team.settings.estimatesEnabled ? (ESTIMATE_SCALES[team.settings.estimateScale] || []) : ESTIMATE_SCALES.Fibonacci;
                    items = [{ value: '', label: 'No estimate', selected: issue.estimate == null, html: 'No estimate' }];
                    items = items.concat(scale.map(v => ({
                        value: String(v), label: String(v), selected: issue.estimate == v,
                        html: String(v)
                    })));
                } else if (prop === 'dueDate') {
                    // Show a text input for date
                    menu.innerHTML = `<div style="padding:8px">
                        <input type="text" class="form-input" placeholder="YYYY-MM-DD" value="${issue.dueDate || ''}" data-testid="due-date-input" style="width:160px">
                        <button class="btn btn-primary btn-sm mt-2" data-testid="set-due-date-btn" style="margin-top:8px">Set</button>
                        <button class="btn btn-ghost btn-sm mt-2" data-testid="clear-due-date-btn" style="margin-top:8px">Clear</button>
                    </div>`;
                    const rect = el.getBoundingClientRect();
                    menu.style.top = (rect.bottom + window.scrollY) + 'px';
                    menu.style.left = rect.left + 'px';
                    document.body.appendChild(menu);

                    const input = menu.querySelector('input');
                    input.focus();
                    menu.querySelector('[data-testid="set-due-date-btn"]').addEventListener('click', () => {
                        const val = input.value.trim();
                        if (val && /^\d{4}-\d{2}-\d{2}$/.test(val)) {
                            AppState.updateIssue(issueId, { dueDate: val });
                            menu.remove();
                            Router.render();
                        }
                    });
                    menu.querySelector('[data-testid="clear-due-date-btn"]').addEventListener('click', () => {
                        AppState.updateIssue(issueId, { dueDate: null });
                        menu.remove();
                        Router.render();
                    });
                    menu.addEventListener('click', (e) => e.stopPropagation());
                    return;
                }

                // Build menu items
                menu.innerHTML = `<input type="text" class="dropdown-search" placeholder="Search..." style="margin:4px;width:calc(100% - 8px)">` +
                    items.map(item => `<div class="dropdown-item${item.selected ? ' selected' : ''}" data-value="${Components.esc(item.value)}">${item.html}</div>`).join('');

                const rect = el.getBoundingClientRect();
                menu.style.top = (rect.bottom + window.scrollY) + 'px';
                menu.style.left = rect.left + 'px';
                document.body.appendChild(menu);

                // Search
                const search = menu.querySelector('.dropdown-search');
                if (search) {
                    search.focus();
                    search.addEventListener('input', () => {
                        const q = search.value.toLowerCase();
                        menu.querySelectorAll('.dropdown-item').forEach(item => {
                            item.style.display = item.textContent.toLowerCase().includes(q) ? '' : 'none';
                        });
                    });
                    search.addEventListener('click', (e) => e.stopPropagation());
                }

                // Item click
                menu.querySelectorAll('.dropdown-item').forEach(item => {
                    item.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const val = item.getAttribute('data-value');

                        if (prop === 'statusId') {
                            AppState.updateIssue(issueId, { statusId: val });
                        } else if (prop === 'priority') {
                            AppState.updateIssue(issueId, { priority: getPriorityByValue(parseInt(val)) });
                        } else if (prop === 'assigneeId') {
                            AppState.updateIssue(issueId, { assigneeId: val || null });
                        } else if (prop === 'labels') {
                            if (issue.labelIds.includes(val)) {
                                AppState.removeLabelFromIssue(issueId, val);
                            } else {
                                AppState.addLabelToIssue(issueId, val);
                            }
                        } else if (prop === 'team') {
                            if (val !== issue.teamId) {
                                AppState.moveIssueToTeam(issueId, val);
                            }
                        } else if (prop === 'projectId') {
                            AppState.updateIssue(issueId, { projectId: val || null });
                        } else if (prop === 'cycleId') {
                            AppState.updateIssue(issueId, { cycleId: val || null });
                        } else if (prop === 'estimate') {
                            const numVal = val === '' ? null : (isNaN(Number(val)) ? val : Number(val));
                            AppState.updateIssue(issueId, { estimate: numVal });
                        }

                        menu.remove();
                        Router.render();
                    });
                });

                menu.addEventListener('click', (e) => e.stopPropagation());
            });
        });
    },

    // ── Issue detail handlers ───────────────────────────────
    _attachIssueDetailHandlers() {
        // Title editing
        document.querySelectorAll('.issue-detail-title[contenteditable]').forEach(el => {
            if (el._handler) return;
            el._handler = true;
            el.addEventListener('blur', () => {
                const issueId = el.getAttribute('data-issue-id');
                const newTitle = el.textContent.trim();
                if (newTitle) AppState.updateIssue(issueId, { title: newTitle });
            });
        });

        // Description editing
        document.querySelectorAll('.issue-description[data-issue-id]').forEach(el => {
            if (el._handler) return;
            el._handler = true;
            el.addEventListener('blur', () => {
                const issueId = el.getAttribute('data-issue-id');
                AppState.updateIssue(issueId, { description: el.value });
            });
        });
    },

    // ── Settings handlers ───────────────────────────────────
    _attachSettingsHandlers() {
        // Toggle switches
        document.querySelectorAll('.toggle').forEach(toggle => {
            if (toggle._handler) return;
            toggle._handler = true;
            toggle.addEventListener('click', () => {
                toggle.classList.toggle('on');
            });
        });

        // Estimate scale dropdown items
        const estDropdown = document.getElementById('estimateScaleDropdown');
        if (estDropdown && !estDropdown._handler) {
            estDropdown._handler = true;
            estDropdown.querySelectorAll('.dropdown-item').forEach(item => {
                item.addEventListener('click', () => {
                    const val = item.getAttribute('data-value');
                    estDropdown.querySelector('.dropdown-trigger').textContent = val;
                    estDropdown.querySelectorAll('.dropdown-item').forEach(i => i.classList.remove('selected'));
                    item.classList.add('selected');
                    estDropdown.querySelector('.dropdown-menu').classList.remove('open');
                });
            });
        }

        // Save team settings
        const saveBtn = document.getElementById('saveTeamSettings');
        if (saveBtn && !saveBtn._handler) {
            saveBtn._handler = true;
            saveBtn.addEventListener('click', () => {
                const teamId = saveBtn.getAttribute('data-team-id');
                const estimatesEnabled = document.getElementById('toggleEstimates').classList.contains('on');
                const scaleDropdown = document.getElementById('estimateScaleDropdown');
                const estimateScale = scaleDropdown ? scaleDropdown.querySelector('.dropdown-trigger').textContent.trim() : 'Fibonacci';
                const autoClosePeriod = parseInt(document.getElementById('autoClosePeriod').value) || 3;
                const autoArchivePeriod = parseInt(document.getElementById('autoArchivePeriod').value) || 6;

                AppState.updateTeamSettings(teamId, {
                    estimatesEnabled,
                    estimateScale,
                    autoClosePeriod,
                    autoArchivePeriod,
                });
                Components.showToast('Settings saved', 'success');
            });
        }
    },

    // ── Filter handlers ─────────────────────────────────────
    _attachFilterHandlers() {
        document.querySelectorAll('.filter-chip[data-filter]').forEach(chip => {
            if (chip._handler) return;
            chip._handler = true;
            chip.addEventListener('click', () => {
                document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                const filter = chip.getAttribute('data-filter');
                document.querySelectorAll('.issue-row').forEach(row => {
                    if (filter === 'all') { row.style.display = ''; return; }
                    const issueId = row.getAttribute('data-issue-id');
                    const issue = AppState.getIssueById(issueId);
                    if (!issue) return;
                    if (filter.startsWith('priority-')) {
                        const pVal = parseInt(filter.split('-')[1]);
                        row.style.display = (issue.priority && issue.priority.value === pVal) ? '' : 'none';
                    }
                });
            });
        });
    },
};

// ── Modal Manager ───────────────────────────────────────────
const ModalManager = {
    _overlay: null,

    _getOverlay() {
        if (!this._overlay) {
            this._overlay = document.createElement('div');
            this._overlay.className = 'modal-overlay hidden';
            this._overlay.id = 'modalOverlay';
            this._overlay.setAttribute('data-testid', 'modal-overlay');
            document.body.appendChild(this._overlay);
            this._overlay.addEventListener('click', (e) => {
                if (e.target === this._overlay) this.close();
            });
        }
        return this._overlay;
    },

    show(html) {
        const overlay = this._getOverlay();
        overlay.innerHTML = html;
        overlay.classList.remove('hidden');
    },

    close() {
        const overlay = this._getOverlay();
        overlay.classList.add('hidden');
        overlay.innerHTML = '';
    },

    // ── Create Issue Modal ──────────────────────────────────
    showCreateIssueModal(teamId, parentIssueId = null) {
        const team = AppState.getTeamById(teamId);
        if (!team) return;
        const labels = AppState.getLabelsForTeam(teamId);
        const teamCycles = AppState.getCyclesForTeam(teamId);

        let selectedPriority = 0;
        let selectedAssignee = '';
        let selectedLabels = [];
        let selectedProject = '';
        let selectedCycle = '';
        let selectedEstimate = null;

        const html = `<div class="modal" data-testid="create-issue-modal">
            <div class="modal-header">
                <span class="modal-title">${parentIssueId ? 'Add Sub-issue' : 'New Issue'} — ${Components.esc(team.name)}</span>
                <button class="modal-close" data-testid="modal-close">×</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">Title *</label>
                    <input type="text" class="form-input" id="issueTitle" data-testid="issue-title-input" placeholder="Issue title" autofocus>
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <textarea class="form-textarea" id="issueDescription" data-testid="issue-description-input" placeholder="Add a description..."></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">Priority</label>
                    <div class="custom-dropdown" id="priorityDropdown" data-testid="priority-dropdown">
                        <div class="dropdown-trigger"><span style="color:#8b8b8b">—</span> No priority</div>
                        <div class="dropdown-menu">
                            ${PRIORITIES.map(p => `<div class="dropdown-item" data-value="${p.value}"><span style="color:${p.color}">${p.icon}</span> ${Components.esc(p.name)}</div>`).join('')}
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Assignee</label>
                    <div class="custom-dropdown" id="assigneeDropdown" data-testid="assignee-dropdown">
                        <div class="dropdown-trigger">Unassigned</div>
                        <div class="dropdown-menu">
                            <input type="text" class="dropdown-search" placeholder="Search...">
                            <div class="dropdown-item" data-value="">Unassigned</div>
                            ${AppState.users.map(u => `<div class="dropdown-item" data-value="${u.id}">${Components.userAvatar(u, 18)} ${Components.esc(u.name)}</div>`).join('')}
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Labels</label>
                    <div class="custom-dropdown" id="labelsDropdown" data-testid="labels-dropdown">
                        <div class="dropdown-trigger">Select labels</div>
                        <div class="dropdown-menu">
                            <input type="text" class="dropdown-search" placeholder="Search labels...">
                            ${labels.map(l => `<div class="dropdown-item" data-value="${l.id}"><span class="label-dot" style="background:${l.color}"></span> ${Components.esc(l.name)}</div>`).join('')}
                        </div>
                    </div>
                    <div id="selectedLabelsDisplay" style="margin-top:4px;display:flex;gap:4px;flex-wrap:wrap"></div>
                </div>
                <div class="form-group">
                    <label class="form-label">Project</label>
                    <div class="custom-dropdown" id="projectDropdown" data-testid="project-dropdown">
                        <div class="dropdown-trigger">No project</div>
                        <div class="dropdown-menu">
                            <div class="dropdown-item" data-value="">No project</div>
                            ${AppState.projects.map(p => `<div class="dropdown-item" data-value="${p.id}">${Components.esc(p.name)}</div>`).join('')}
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Cycle</label>
                    <div class="custom-dropdown" id="cycleDropdown" data-testid="cycle-dropdown">
                        <div class="dropdown-trigger">No cycle</div>
                        <div class="dropdown-menu">
                            <div class="dropdown-item" data-value="">No cycle</div>
                            ${teamCycles.map(c => `<div class="dropdown-item" data-value="${c.id}">${Components.esc(c.name)} (${c.status})</div>`).join('')}
                        </div>
                    </div>
                </div>
                ${team.settings.estimatesEnabled ? `<div class="form-group">
                    <label class="form-label">Estimate</label>
                    <div class="custom-dropdown" id="estimateDropdown" data-testid="estimate-dropdown">
                        <div class="dropdown-trigger">No estimate</div>
                        <div class="dropdown-menu">
                            <div class="dropdown-item" data-value="">No estimate</div>
                            ${(ESTIMATE_SCALES[team.settings.estimateScale] || []).map(v => `<div class="dropdown-item" data-value="${v}">${v}</div>`).join('')}
                        </div>
                    </div>
                </div>` : ''}
                <div class="form-group">
                    <label class="form-label">Due date</label>
                    <input type="text" class="form-input" id="issueDueDate" data-testid="issue-due-date-input" placeholder="YYYY-MM-DD">
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" data-testid="cancel-btn" id="cancelCreateIssue">Cancel</button>
                <button class="btn btn-primary" data-testid="create-issue-submit" id="submitCreateIssue">Create Issue</button>
            </div>
        </div>`;

        this.show(html);

        // Wire up modal dropdowns
        this._wireModalDropdowns();

        // Label multi-select
        const labelsDropdown = document.getElementById('labelsDropdown');
        if (labelsDropdown) {
            labelsDropdown.querySelectorAll('.dropdown-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const val = item.getAttribute('data-value');
                    const idx = selectedLabels.indexOf(val);
                    if (idx >= 0) {
                        selectedLabels.splice(idx, 1);
                        item.classList.remove('selected');
                    } else {
                        selectedLabels.push(val);
                        item.classList.add('selected');
                    }
                    // Update display
                    const display = document.getElementById('selectedLabelsDisplay');
                    if (display) {
                        display.innerHTML = selectedLabels.map(id => {
                            const l = AppState.getLabelById(id);
                            return l ? Components.labelBadge(l) : '';
                        }).join('');
                    }
                });
            });
        }

        // Priority dropdown
        const prioDropdown = document.getElementById('priorityDropdown');
        if (prioDropdown) {
            prioDropdown.querySelectorAll('.dropdown-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    selectedPriority = parseInt(item.getAttribute('data-value'));
                    const p = getPriorityByValue(selectedPriority);
                    prioDropdown.querySelector('.dropdown-trigger').innerHTML = `<span style="color:${p.color}">${p.icon}</span> ${p.name}`;
                    prioDropdown.querySelector('.dropdown-menu').classList.remove('open');
                });
            });
        }

        // Assignee dropdown
        const assDropdown = document.getElementById('assigneeDropdown');
        if (assDropdown) {
            assDropdown.querySelectorAll('.dropdown-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    selectedAssignee = item.getAttribute('data-value');
                    assDropdown.querySelector('.dropdown-trigger').innerHTML = selectedAssignee ?
                        AppState.getUserById(selectedAssignee)?.name || 'Unknown' : 'Unassigned';
                    assDropdown.querySelector('.dropdown-menu').classList.remove('open');
                });
            });
        }

        // Project dropdown
        const projDropdown = document.getElementById('projectDropdown');
        if (projDropdown) {
            projDropdown.querySelectorAll('.dropdown-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    selectedProject = item.getAttribute('data-value');
                    projDropdown.querySelector('.dropdown-trigger').textContent =
                        selectedProject ? (AppState.getProjectById(selectedProject)?.name || 'Unknown') : 'No project';
                    projDropdown.querySelector('.dropdown-menu').classList.remove('open');
                });
            });
        }

        // Cycle dropdown
        const cycDropdown = document.getElementById('cycleDropdown');
        if (cycDropdown) {
            cycDropdown.querySelectorAll('.dropdown-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    selectedCycle = item.getAttribute('data-value');
                    cycDropdown.querySelector('.dropdown-trigger').textContent =
                        selectedCycle ? (AppState.getCycleById(selectedCycle)?.name || 'Unknown') : 'No cycle';
                    cycDropdown.querySelector('.dropdown-menu').classList.remove('open');
                });
            });
        }

        // Estimate dropdown
        const estDropdown = document.getElementById('estimateDropdown');
        if (estDropdown) {
            estDropdown.querySelectorAll('.dropdown-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const val = item.getAttribute('data-value');
                    selectedEstimate = val === '' ? null : (isNaN(Number(val)) ? val : Number(val));
                    estDropdown.querySelector('.dropdown-trigger').textContent = val || 'No estimate';
                    estDropdown.querySelector('.dropdown-menu').classList.remove('open');
                });
            });
        }

        // Cancel
        document.getElementById('cancelCreateIssue').addEventListener('click', () => this.close());

        // Submit
        document.getElementById('submitCreateIssue').addEventListener('click', () => {
            const title = document.getElementById('issueTitle').value.trim();
            if (!title) {
                Components.showToast('Title is required', 'error');
                return;
            }
            const dueDate = document.getElementById('issueDueDate')?.value.trim() || null;

            const issue = AppState.createIssue({
                title,
                description: document.getElementById('issueDescription').value.trim(),
                teamId,
                priority: getPriorityByValue(selectedPriority),
                assigneeId: selectedAssignee || null,
                labelIds: [...selectedLabels],
                projectId: selectedProject || null,
                cycleId: selectedCycle || null,
                parentIssueId: parentIssueId || null,
                estimate: selectedEstimate,
                dueDate: dueDate && /^\d{4}-\d{2}-\d{2}$/.test(dueDate) ? dueDate : null,
            });

            this.close();
            Components.showToast(`Created ${issue.identifier}`, 'success');
            Router.render();
        });
    },

    // ── Create Issue from Template ──────────────────────────
    showCreateIssueFromTemplateModal(templateId) {
        const template = AppState.getTemplateById(templateId);
        if (!template) return;

        // Show a team selection first, then create with template defaults
        const html = `<div class="modal" data-testid="template-issue-modal">
            <div class="modal-header">
                <span class="modal-title">Create from "${Components.esc(template.name)}"</span>
                <button class="modal-close" data-testid="modal-close">×</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">Title *</label>
                    <input type="text" class="form-input" id="templateIssueTitle" data-testid="template-issue-title" placeholder="Issue title">
                </div>
                <div class="form-group">
                    <label class="form-label">Team *</label>
                    <div class="custom-dropdown" id="templateTeamDropdown" data-testid="template-team-dropdown">
                        <div class="dropdown-trigger">Select team</div>
                        <div class="dropdown-menu">
                            ${AppState.teams.map(t => `<div class="dropdown-item" data-value="${t.id}">${t.icon} ${Components.esc(t.name)}</div>`).join('')}
                        </div>
                    </div>
                </div>
                <div class="text-sm text-muted mt-2">
                    Priority: ${template.defaultPriority ? template.defaultPriority.name : 'None'}<br>
                    ${template.defaultLabelIds.length > 0 ? 'Labels: ' + template.defaultLabelIds.map(id => AppState.getLabelById(id)?.name).filter(Boolean).join(', ') : ''}
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" id="cancelTemplateIssue">Cancel</button>
                <button class="btn btn-primary" id="submitTemplateIssue" data-testid="create-from-template-btn">Create</button>
            </div>
        </div>`;

        this.show(html);
        this._wireModalDropdowns();

        let selectedTeam = '';
        const teamDropdown = document.getElementById('templateTeamDropdown');
        if (teamDropdown) {
            teamDropdown.querySelectorAll('.dropdown-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    selectedTeam = item.getAttribute('data-value');
                    const t = AppState.getTeamById(selectedTeam);
                    teamDropdown.querySelector('.dropdown-trigger').textContent = t ? `${t.icon} ${t.name}` : 'Select team';
                    teamDropdown.querySelector('.dropdown-menu').classList.remove('open');
                });
            });
        }

        document.getElementById('cancelTemplateIssue').addEventListener('click', () => this.close());
        document.getElementById('submitTemplateIssue').addEventListener('click', () => {
            const title = document.getElementById('templateIssueTitle').value.trim();
            if (!title || !selectedTeam) {
                Components.showToast('Title and team are required', 'error');
                return;
            }
            const issue = AppState.createIssue({
                title,
                description: template.templateDescription || '',
                teamId: selectedTeam,
                priority: template.defaultPriority || getPriorityByName('No priority'),
                labelIds: [...(template.defaultLabelIds || [])],
                estimate: template.defaultEstimate,
            });
            this.close();
            Components.showToast(`Created ${issue.identifier} from template`, 'success');
            Router.navigate(`/issue/${issue.id}`);
        });
    },

    // ── Add Relation Modal ──────────────────────────────────
    showAddRelationModal(issueId) {
        const issue = AppState.getIssueById(issueId);
        if (!issue) return;
        const allIssues = AppState.issues.filter(i => i.id !== issueId && !i.deletedAt);

        const html = `<div class="modal" data-testid="add-relation-modal">
            <div class="modal-header">
                <span class="modal-title">Add Relation to ${Components.esc(issue.identifier)}</span>
                <button class="modal-close" data-testid="modal-close">×</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">Relation type</label>
                    <div class="custom-dropdown" id="relationTypeDropdown" data-testid="relation-type-dropdown">
                        <div class="dropdown-trigger">related</div>
                        <div class="dropdown-menu">
                            ${RELATION_TYPES.map(t => `<div class="dropdown-item" data-value="${t}">${t}</div>`).join('')}
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Related issue</label>
                    <div class="custom-dropdown" id="relatedIssueDropdown" data-testid="related-issue-dropdown">
                        <div class="dropdown-trigger">Select issue</div>
                        <div class="dropdown-menu">
                            <input type="text" class="dropdown-search" placeholder="Search issues...">
                            ${allIssues.map(i => `<div class="dropdown-item" data-value="${i.id}">${Components.esc(i.identifier)} ${Components.esc(i.title)}</div>`).join('')}
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" id="cancelRelation">Cancel</button>
                <button class="btn btn-primary" id="submitRelation" data-testid="add-relation-submit">Add Relation</button>
            </div>
        </div>`;

        this.show(html);
        this._wireModalDropdowns();

        let selectedType = 'related';
        let selectedIssue = '';

        document.getElementById('relationTypeDropdown').querySelectorAll('.dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                selectedType = item.getAttribute('data-value');
                document.getElementById('relationTypeDropdown').querySelector('.dropdown-trigger').textContent = selectedType;
                document.getElementById('relationTypeDropdown').querySelector('.dropdown-menu').classList.remove('open');
            });
        });

        document.getElementById('relatedIssueDropdown').querySelectorAll('.dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                selectedIssue = item.getAttribute('data-value');
                const si = AppState.getIssueById(selectedIssue);
                document.getElementById('relatedIssueDropdown').querySelector('.dropdown-trigger').textContent =
                    si ? `${si.identifier} ${si.title}` : 'Select issue';
                document.getElementById('relatedIssueDropdown').querySelector('.dropdown-menu').classList.remove('open');
            });
        });

        document.getElementById('cancelRelation').addEventListener('click', () => this.close());
        document.getElementById('submitRelation').addEventListener('click', () => {
            if (!selectedIssue) { Components.showToast('Select an issue', 'error'); return; }
            AppState.addRelation(issueId, selectedIssue, selectedType);
            this.close();
            Components.showToast('Relation added', 'success');
            Router.render();
        });
    },

    // ── Create Label Modal ──────────────────────────────────
    showCreateLabelModal(teamId) {
        const groups = AppState.labelGroups;
        let selectedColor = '#6366f1';
        let selectedGroup = '';

        const html = `<div class="modal" data-testid="create-label-modal">
            <div class="modal-header">
                <span class="modal-title">Create Label</span>
                <button class="modal-close" data-testid="modal-close">×</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">Name *</label>
                    <input type="text" class="form-input" id="labelName" data-testid="label-name-input" placeholder="Label name">
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <input type="text" class="form-input" id="labelDescription" data-testid="label-description-input" placeholder="Brief description">
                </div>
                <div class="form-group">
                    <label class="form-label">Color</label>
                    ${Components.colorPalette(selectedColor, 'labelColorPalette')}
                </div>
                <div class="form-group">
                    <label class="form-label">Group (optional)</label>
                    <div class="custom-dropdown" id="labelGroupDropdown" data-testid="label-group-dropdown">
                        <div class="dropdown-trigger">No group</div>
                        <div class="dropdown-menu">
                            <div class="dropdown-item" data-value="">No group</div>
                            ${groups.map(g => `<div class="dropdown-item" data-value="${g.id}">${Components.esc(g.name)}</div>`).join('')}
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Scope</label>
                    <div class="custom-dropdown" id="labelScopeDropdown" data-testid="label-scope-dropdown">
                        <div class="dropdown-trigger">workspace</div>
                        <div class="dropdown-menu">
                            <div class="dropdown-item selected" data-value="workspace">Workspace</div>
                            ${teamId ? `<div class="dropdown-item" data-value="team">Team</div>` : ''}
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" id="cancelLabel">Cancel</button>
                <button class="btn btn-primary" id="submitLabel" data-testid="create-label-submit">Create Label</button>
            </div>
        </div>`;

        this.show(html);
        this._wireModalDropdowns();
        this._wireColorPalette('labelColorPalette', c => { selectedColor = c; });

        let selectedScope = 'workspace';

        document.getElementById('labelGroupDropdown')?.querySelectorAll('.dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                selectedGroup = item.getAttribute('data-value');
                document.getElementById('labelGroupDropdown').querySelector('.dropdown-trigger').textContent =
                    selectedGroup ? (AppState.getLabelGroupById(selectedGroup)?.name || 'Group') : 'No group';
                document.getElementById('labelGroupDropdown').querySelector('.dropdown-menu').classList.remove('open');
            });
        });

        document.getElementById('labelScopeDropdown')?.querySelectorAll('.dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                selectedScope = item.getAttribute('data-value');
                document.getElementById('labelScopeDropdown').querySelector('.dropdown-trigger').textContent = selectedScope;
                document.getElementById('labelScopeDropdown').querySelector('.dropdown-menu').classList.remove('open');
            });
        });

        document.getElementById('cancelLabel').addEventListener('click', () => this.close());
        document.getElementById('submitLabel').addEventListener('click', () => {
            const name = document.getElementById('labelName').value.trim();
            if (!name) { Components.showToast('Name is required', 'error'); return; }
            const result = AppState.createLabel({
                name,
                description: document.getElementById('labelDescription').value.trim(),
                color: selectedColor,
                scope: selectedScope,
                teamId: selectedScope === 'team' ? teamId : null,
                groupId: selectedGroup || null,
            });
            if (result.error) { Components.showToast(result.error, 'error'); return; }
            this.close();
            Components.showToast(`Label "${name}" created`, 'success');
            Router.render();
        });
    },

    // ── Create Label Group Modal ────────────────────────────
    showCreateLabelGroupModal(teamId) {
        let selectedColor = '#6366f1';

        const html = `<div class="modal" data-testid="create-label-group-modal">
            <div class="modal-header">
                <span class="modal-title">Create Label Group</span>
                <button class="modal-close" data-testid="modal-close">×</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">Name *</label>
                    <input type="text" class="form-input" id="groupName" data-testid="group-name-input" placeholder="Group name">
                </div>
                <div class="form-group">
                    <label class="form-label">Color</label>
                    ${Components.colorPalette(selectedColor, 'groupColorPalette')}
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" id="cancelGroup">Cancel</button>
                <button class="btn btn-primary" id="submitGroup" data-testid="create-group-submit">Create Group</button>
            </div>
        </div>`;

        this.show(html);
        this._wireColorPalette('groupColorPalette', c => { selectedColor = c; });

        document.getElementById('cancelGroup').addEventListener('click', () => this.close());
        document.getElementById('submitGroup').addEventListener('click', () => {
            const name = document.getElementById('groupName').value.trim();
            if (!name) { Components.showToast('Name is required', 'error'); return; }
            AppState.createLabelGroup({
                name,
                scope: teamId ? 'team' : 'workspace',
                teamId: teamId || null,
                color: selectedColor,
            });
            this.close();
            Components.showToast(`Label group "${name}" created`, 'success');
            Router.render();
        });
    },

    // ── Create Template Modal ───────────────────────────────
    showCreateTemplateModal() {
        let selectedPriority = 0;

        const html = `<div class="modal" data-testid="create-template-modal">
            <div class="modal-header">
                <span class="modal-title">Create Template</span>
                <button class="modal-close" data-testid="modal-close">×</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">Name *</label>
                    <input type="text" class="form-input" id="templateName" data-testid="template-name-input" placeholder="Template name">
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <input type="text" class="form-input" id="templateDesc" data-testid="template-description-input" placeholder="Template description">
                </div>
                <div class="form-group">
                    <label class="form-label">Default Priority</label>
                    <div class="custom-dropdown" id="templatePriorityDropdown" data-testid="template-priority-dropdown">
                        <div class="dropdown-trigger"><span style="color:#8b8b8b">—</span> No priority</div>
                        <div class="dropdown-menu">
                            ${PRIORITIES.map(p => `<div class="dropdown-item" data-value="${p.value}"><span style="color:${p.color}">${p.icon}</span> ${Components.esc(p.name)}</div>`).join('')}
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Template body</label>
                    <textarea class="form-textarea" id="templateBody" data-testid="template-body-input" placeholder="Issue description template..."></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" id="cancelTemplate">Cancel</button>
                <button class="btn btn-primary" id="submitTemplate" data-testid="create-template-submit">Create Template</button>
            </div>
        </div>`;

        this.show(html);
        this._wireModalDropdowns();

        document.getElementById('templatePriorityDropdown').querySelectorAll('.dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                selectedPriority = parseInt(item.getAttribute('data-value'));
                const p = getPriorityByValue(selectedPriority);
                document.getElementById('templatePriorityDropdown').querySelector('.dropdown-trigger').innerHTML =
                    `<span style="color:${p.color}">${p.icon}</span> ${p.name}`;
                document.getElementById('templatePriorityDropdown').querySelector('.dropdown-menu').classList.remove('open');
            });
        });

        document.getElementById('cancelTemplate').addEventListener('click', () => this.close());
        document.getElementById('submitTemplate').addEventListener('click', () => {
            const name = document.getElementById('templateName').value.trim();
            if (!name) { Components.showToast('Name is required', 'error'); return; }
            AppState.createTemplate({
                name,
                description: document.getElementById('templateDesc').value.trim(),
                defaultPriority: getPriorityByValue(selectedPriority),
                templateDescription: document.getElementById('templateBody').value.trim(),
            });
            this.close();
            Components.showToast(`Template "${name}" created`, 'success');
            Router.render();
        });
    },

    // ── Wire modal dropdowns ────────────────────────────────
    _wireModalDropdowns() {
        document.querySelectorAll('.modal .dropdown-trigger').forEach(trigger => {
            if (trigger._handler) return;
            trigger._handler = true;
            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                const menu = trigger.parentElement.querySelector('.dropdown-menu');
                const wasOpen = menu.classList.contains('open');
                document.querySelectorAll('.modal .dropdown-menu.open').forEach(m => m.classList.remove('open'));
                if (!wasOpen) menu.classList.add('open');
            });
        });

        document.querySelectorAll('.modal .dropdown-search').forEach(input => {
            if (input._handler) return;
            input._handler = true;
            input.addEventListener('input', () => {
                const q = input.value.toLowerCase();
                input.parentElement.querySelectorAll('.dropdown-item').forEach(item => {
                    item.style.display = item.textContent.toLowerCase().includes(q) ? '' : 'none';
                });
            });
            input.addEventListener('click', (e) => e.stopPropagation());
        });

        document.querySelectorAll('.modal-close').forEach(btn => {
            if (btn._handler) return;
            btn._handler = true;
            btn.addEventListener('click', () => this.close());
        });
    },

    // ── Wire color palette ──────────────────────────────────
    // ── Create Customer Modal ───────────────────────────────
    showCreateCustomerModal() {
        const tiers = ['Free', 'Pro', 'Business', 'Enterprise'];
        let selectedTier = 'Business';

        const html = `<div class="modal" data-testid="create-customer-modal">
            <div class="modal-header">
                <span class="modal-title">Create Customer</span>
                <button class="modal-close" data-testid="modal-close">×</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">Name *</label>
                    <input type="text" class="form-input" id="customerName" data-testid="customer-name-input" placeholder="Company name">
                </div>
                <div class="form-group">
                    <label class="form-label">Domain</label>
                    <input type="text" class="form-input" id="customerDomain" data-testid="customer-domain-input" placeholder="example.com">
                </div>
                <div class="form-group">
                    <label class="form-label">Tier</label>
                    <div class="custom-dropdown" id="customerTierDropdown" data-testid="customer-tier-dropdown">
                        <div class="dropdown-trigger">Business</div>
                        <div class="dropdown-menu">
                            ${tiers.map(t => `<div class="dropdown-item${t === selectedTier ? ' selected' : ''}" data-value="${t}">${t}</div>`).join('')}
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Contact name</label>
                    <input type="text" class="form-input" id="customerContactName" data-testid="customer-contact-name-input" placeholder="Contact person">
                </div>
                <div class="form-group">
                    <label class="form-label">Contact email</label>
                    <input type="text" class="form-input" id="customerContactEmail" data-testid="customer-contact-email-input" placeholder="contact@example.com">
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" id="cancelCustomer">Cancel</button>
                <button class="btn btn-primary" id="submitCustomer" data-testid="create-customer-submit">Create Customer</button>
            </div>
        </div>`;

        this.show(html);
        this._wireModalDropdowns();

        const tierDropdown = document.getElementById('customerTierDropdown');
        if (tierDropdown) {
            tierDropdown.querySelectorAll('.dropdown-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    selectedTier = item.getAttribute('data-value');
                    tierDropdown.querySelector('.dropdown-trigger').textContent = selectedTier;
                    tierDropdown.querySelector('.dropdown-menu').classList.remove('open');
                });
            });
        }

        document.getElementById('cancelCustomer').addEventListener('click', () => this.close());
        document.getElementById('submitCustomer').addEventListener('click', () => {
            const name = document.getElementById('customerName').value.trim();
            if (!name) { Components.showToast('Name is required', 'error'); return; }
            AppState.createCustomer({
                name,
                domain: document.getElementById('customerDomain').value.trim(),
                tier: selectedTier,
                contactName: document.getElementById('customerContactName').value.trim(),
                contactEmail: document.getElementById('customerContactEmail').value.trim(),
            });
            this.close();
            Components.showToast(`Customer "${name}" created`, 'success');
            Router.render();
        });
    },

    // ── Add Customer Request Modal ──────────────────────────
    showAddCustomerRequestModal(issueId) {
        const issue = issueId ? AppState.getIssueById(issueId) : null;
        const customers = AppState.customers;
        let selectedCustomer = '';
        let selectedIssue = issueId || '';

        const html = `<div class="modal" data-testid="add-customer-request-modal">
            <div class="modal-header">
                <span class="modal-title">Add Customer Request</span>
                <button class="modal-close" data-testid="modal-close">×</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">Customer *</label>
                    <div class="custom-dropdown" id="requestCustomerDropdown" data-testid="request-customer-dropdown">
                        <div class="dropdown-trigger">Select customer</div>
                        <div class="dropdown-menu">
                            ${customers.map(c => `<div class="dropdown-item" data-value="${c.id}">${Components.esc(c.name)}</div>`).join('')}
                        </div>
                    </div>
                </div>
                ${!issueId ? `<div class="form-group">
                    <label class="form-label">Issue</label>
                    <div class="custom-dropdown" id="requestIssueDropdown" data-testid="request-issue-dropdown">
                        <div class="dropdown-trigger">Select issue</div>
                        <div class="dropdown-menu">
                            <input type="text" class="dropdown-search" placeholder="Search...">
                            ${AppState.issues.filter(i => !i.deletedAt).map(i => `<div class="dropdown-item" data-value="${i.id}">${Components.esc(i.identifier)} ${Components.esc(i.title)}</div>`).join('')}
                        </div>
                    </div>
                </div>` : ''}
                <div class="form-group">
                    <label class="form-label">Title *</label>
                    <input type="text" class="form-input" id="requestTitle" data-testid="request-title-input" placeholder="Request title">
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <textarea class="form-textarea" id="requestDescription" data-testid="request-description-input" placeholder="Request details..."></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" id="cancelRequest">Cancel</button>
                <button class="btn btn-primary" id="submitRequest" data-testid="add-request-submit">Add Request</button>
            </div>
        </div>`;

        this.show(html);
        this._wireModalDropdowns();

        const custDropdown = document.getElementById('requestCustomerDropdown');
        if (custDropdown) {
            custDropdown.querySelectorAll('.dropdown-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    selectedCustomer = item.getAttribute('data-value');
                    const c = AppState.getCustomerById(selectedCustomer);
                    custDropdown.querySelector('.dropdown-trigger').textContent = c ? c.name : 'Select customer';
                    custDropdown.querySelector('.dropdown-menu').classList.remove('open');
                });
            });
        }

        const issueDropdown = document.getElementById('requestIssueDropdown');
        if (issueDropdown) {
            issueDropdown.querySelectorAll('.dropdown-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    selectedIssue = item.getAttribute('data-value');
                    const i = AppState.getIssueById(selectedIssue);
                    issueDropdown.querySelector('.dropdown-trigger').textContent = i ? `${i.identifier} ${i.title}` : 'Select issue';
                    issueDropdown.querySelector('.dropdown-menu').classList.remove('open');
                });
            });
        }

        document.getElementById('cancelRequest').addEventListener('click', () => this.close());
        document.getElementById('submitRequest').addEventListener('click', () => {
            const title = document.getElementById('requestTitle').value.trim();
            if (!title || !selectedCustomer) { Components.showToast('Customer and title required', 'error'); return; }
            AppState.addCustomerRequest({
                customerId: selectedCustomer,
                issueId: selectedIssue || null,
                title,
                description: document.getElementById('requestDescription').value.trim(),
            });
            this.close();
            Components.showToast('Customer request added', 'success');
            Router.render();
        });
    },

    _wireColorPalette(paletteId, callback) {
        const palette = document.getElementById(paletteId);
        if (!palette) return;
        palette.querySelectorAll('.color-swatch').forEach(swatch => {
            swatch.addEventListener('click', () => {
                palette.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
                swatch.classList.add('selected');
                callback(swatch.getAttribute('data-color'));
            });
        });
    },
};

// ── Sidebar rendering ───────────────────────────────────────
function renderSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;

    const teams = AppState.teams;
    const teamLinks = teams.map(t => {
        const issueCount = AppState.getIssuesForTeam(t.id).length;
        return `<div class="sidebar-section">
            <a class="sidebar-item" data-route="/team/${t.id}" data-testid="nav-team-${t.identifier}">
                <span class="sidebar-icon">${t.icon}</span>
                <span class="sidebar-label">${Components.esc(t.name)}</span>
                <span class="sidebar-count">${issueCount}</span>
            </a>
            <a class="sidebar-item" data-route="/team/${t.id}/board" data-testid="nav-team-${t.identifier}-board" style="padding-left:44px;font-size:12px">Board</a>
            <a class="sidebar-item" data-route="/team/${t.id}/cycles" data-testid="nav-team-${t.identifier}-cycles" style="padding-left:44px;font-size:12px">Cycles</a>
            <a class="sidebar-item" data-route="/team/${t.id}/settings" data-testid="nav-team-${t.identifier}-settings" style="padding-left:44px;font-size:12px">Settings</a>
            <a class="sidebar-item" data-route="/team/${t.id}/labels" data-testid="nav-team-${t.identifier}-labels" style="padding-left:44px;font-size:12px">Labels</a>
        </div>`;
    }).join('');

    sidebar.innerHTML = `<nav class="sidebar-nav">
        <div class="sidebar-section">
            <a class="sidebar-item" data-route="/" data-testid="nav-my-issues">
                <span class="sidebar-icon">📋</span>
                <span class="sidebar-label">My Issues</span>
            </a>
        </div>
        <div class="sidebar-divider"></div>
        <div class="sidebar-section">
            <div class="sidebar-section-title">Teams</div>
        </div>
        ${teamLinks}
        <div class="sidebar-divider"></div>
        <div class="sidebar-section">
            <a class="sidebar-item" data-route="/projects" data-testid="nav-projects">
                <span class="sidebar-icon">📊</span>
                <span class="sidebar-label">Projects</span>
            </a>
            <a class="sidebar-item" data-route="/labels" data-testid="nav-labels">
                <span class="sidebar-icon">🏷️</span>
                <span class="sidebar-label">Labels</span>
            </a>
            <a class="sidebar-item" data-route="/templates" data-testid="nav-templates">
                <span class="sidebar-icon">📄</span>
                <span class="sidebar-label">Templates</span>
            </a>
            <a class="sidebar-item" data-route="/customers" data-testid="nav-customers">
                <span class="sidebar-icon">👥</span>
                <span class="sidebar-label">Customers</span>
            </a>
        </div>
    </nav>`;
}

// ── SSE listener ────────────────────────────────────────────
function setupSSE() {
    const eventSource = new EventSource('/api/events');
    eventSource.onmessage = (e) => {
        if (e.data === 'reset') {
            AppState.resetToSeedData();
            Router.navigate('/');
        }
    };
    eventSource.onerror = () => {
        setTimeout(setupSSE, 5000);
        eventSource.close();
    };
}

// ── Init ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    AppState.init();
    renderSidebar();

    // Render user avatar in header
    const user = AppState.getCurrentUser();
    if (user) {
        const avatarEl = document.getElementById('currentUserAvatar');
        if (avatarEl) {
            avatarEl.style.background = user.avatarColor;
            avatarEl.textContent = user.name.split(' ').map(n => n[0]).join('');
            avatarEl.title = user.name;
        }
    }

    // Handle hash-based routing
    const hash = window.location.hash.slice(1) || '/';
    Router.navigate(hash, true);

    window.addEventListener('popstate', (e) => {
        const path = e.state?.path || window.location.hash.slice(1) || '/';
        Router.navigate(path, true);
    });

    setupSSE();
});
