// ============================================================
// Linear Issue Management — Reusable UI Components
// ============================================================

const Components = {

    // ── User avatar ─────────────────────────────────────────
    userAvatar(user, size = 22) {
        if (!user) return `<div class="issue-assignee" style="width:${size}px;height:${size}px;background:var(--bg-tertiary);font-size:${Math.round(size*0.45)}px">?</div>`;
        const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
        return `<div class="issue-assignee" style="width:${size}px;height:${size}px;background:${user.avatarColor};font-size:${Math.round(size*0.45)}px" title="${this.esc(user.name)}" data-testid="avatar-${user.id}">${initials}</div>`;
    },

    // ── Status dot ──────────────────────────────────────────
    statusDot(status) {
        if (!status) return '<div class="issue-status-dot"></div>';
        return `<div class="issue-status-dot ${status.category}" title="${this.esc(status.name)}" data-testid="status-dot-${status.id}"></div>`;
    },

    // ── Priority icon ───────────────────────────────────────
    priorityIcon(priority) {
        if (!priority || priority.value === 0) return `<span class="issue-priority-icon" style="color:#8b8b8b" title="No priority">—</span>`;
        return `<span class="issue-priority-icon" style="color:${priority.color}" title="${priority.name}">${priority.icon}</span>`;
    },

    // ── Label badge ─────────────────────────────────────────
    labelBadge(label) {
        if (!label) return '';
        return `<span class="label-badge" style="background:${label.color}20;color:${label.color}" data-testid="label-${label.id}"><span class="label-dot" style="background:${label.color}"></span>${this.esc(label.name)}</span>`;
    },

    // ── Issue row ───────────────────────────────────────────
    issueRow(issue) {
        const team = AppState.getTeamById(issue.teamId);
        const status = AppState.getStatusById(issue.statusId);
        const assignee = issue.assigneeId ? AppState.getUserById(issue.assigneeId) : null;
        const labels = (issue.labelIds || []).map(id => AppState.getLabelById(id)).filter(Boolean);

        return `<div class="issue-row" data-issue-id="${issue.id}" data-testid="issue-row-${issue.identifier}">
            ${this.priorityIcon(issue.priority)}
            ${this.statusDot(status)}
            <span class="issue-identifier">${this.esc(issue.identifier)}</span>
            <span class="issue-title-text">${this.esc(issue.title)}</span>
            <span class="issue-labels">${labels.slice(0, 3).map(l => this.labelBadge(l)).join('')}</span>
            ${issue.dueDate ? `<span class="issue-due-date">${issue.dueDate}</span>` : ''}
            <span class="issue-meta">
                ${assignee ? this.userAvatar(assignee) : ''}
            </span>
        </div>`;
    },

    // ── Board card ──────────────────────────────────────────
    boardCard(issue) {
        const assignee = issue.assigneeId ? AppState.getUserById(issue.assigneeId) : null;
        const labels = (issue.labelIds || []).map(id => AppState.getLabelById(id)).filter(Boolean);

        return `<div class="board-card" data-issue-id="${issue.id}" data-testid="board-card-${issue.identifier}">
            <div class="board-card-header">
                ${this.priorityIcon(issue.priority)}
                <span class="board-card-id">${this.esc(issue.identifier)}</span>
            </div>
            <div class="board-card-title">${this.esc(issue.title)}</div>
            <div class="issue-labels" style="margin-top:6px">${labels.map(l => this.labelBadge(l)).join('')}</div>
            <div class="board-card-footer">
                <span class="issue-due-date">${issue.dueDate || ''}</span>
                ${assignee ? this.userAvatar(assignee, 20) : '<span></span>'}
            </div>
        </div>`;
    },

    // ── Custom dropdown ─────────────────────────────────────
    dropdown(id, triggerText, items, options = {}) {
        const { searchable = false, testId = '' } = options;
        const itemsHtml = items.map(item =>
            item.divider ? '<div class="dropdown-divider"></div>' :
            item.header ? `<div class="dropdown-header-text">${this.esc(item.header)}</div>` :
            `<div class="dropdown-item${item.selected ? ' selected' : ''}" data-value="${this.esc(item.value)}" data-testid="dropdown-item-${this.esc(item.value)}">
                ${item.icon || ''}<span>${this.esc(item.label)}</span>${item.selected ? '<span class="check">✓</span>' : ''}
            </div>`
        ).join('');

        return `<div class="custom-dropdown" id="${id}" data-testid="${testId || id}">
            <div class="dropdown-trigger" data-testid="${testId || id}-trigger">${triggerText}</div>
            <div class="dropdown-menu" data-testid="${testId || id}-menu">
                ${searchable ? `<input type="text" class="dropdown-search" placeholder="Search..." data-testid="${testId || id}-search">` : ''}
                <div class="dropdown-items">${itemsHtml}</div>
            </div>
        </div>`;
    },

    // ── Toggle switch ───────────────────────────────────────
    toggle(id, isOn, label = '') {
        return `<div class="settings-row">
            <span class="settings-label">${this.esc(label)}</span>
            <div class="toggle${isOn ? ' on' : ''}" id="${id}" data-testid="${id}">
                <div class="toggle-knob"></div>
            </div>
        </div>`;
    },

    // ── Color palette ───────────────────────────────────────
    colorPalette(selectedColor, id = 'colorPalette') {
        const colors = ['#ef4444','#f97316','#f59e0b','#22c55e','#14b8a6','#3b82f6','#6366f1','#8b5cf6','#a855f7','#ec4899','#06b6d4','#dc2626','#78716c','#000000'];
        return `<div class="color-palette" id="${id}" data-testid="${id}">
            ${colors.map(c => `<div class="color-swatch${c === selectedColor ? ' selected' : ''}" style="background:${c}" data-color="${c}" data-testid="color-${c}"></div>`).join('')}
        </div>`;
    },

    // ── Toast ───────────────────────────────────────────────
    showToast(message, type = 'info') {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => { toast.remove(); }, 3000);
    },

    // ── Escape HTML ─────────────────────────────────────────
    esc(str) {
        if (str === null || str === undefined) return '';
        return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    },

    // ── Format date ─────────────────────────────────────────
    formatDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    },

    // ── Relative time ───────────────────────────────────────
    relativeTime(dateStr) {
        if (!dateStr) return '';
        const now = new Date();
        const d = new Date(dateStr);
        const diff = now - d;
        const mins = Math.floor(diff / 60000);
        if (mins < 1) return 'just now';
        if (mins < 60) return `${mins}m ago`;
        const hrs = Math.floor(mins / 60);
        if (hrs < 24) return `${hrs}h ago`;
        const days = Math.floor(hrs / 24);
        if (days < 30) return `${days}d ago`;
        return Components.formatDate(dateStr);
    },
};
