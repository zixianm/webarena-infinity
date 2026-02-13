// ============================================================
// components.js — Reusable custom UI components
// ============================================================

const Components = {

    // ---- Avatar ----
    avatar(user, size = 32) {
        if (!user) return `<div class="avatar" style="width:${size}px;height:${size}px;background:#ccc;font-size:${size * 0.4}px" data-testid="avatar">?</div>`;
        const initials = user.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
        const color = user.avatarColor || '#6366f1';
        return `<div class="avatar" style="width:${size}px;height:${size}px;background:${color};font-size:${size * 0.4}px" data-testid="avatar-${user.username}" title="${Components.escapeHtml(user.name)}">${initials}</div>`;
    },

    // ---- Group/Org Avatar ----
    groupAvatar(entity, size = 32) {
        const initials = entity.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
        const color = entity.avatarColor || '#6366f1';
        return `<div class="avatar avatar-square" style="width:${size}px;height:${size}px;background:${color};font-size:${size * 0.4}px" data-testid="group-avatar-${entity.path || entity.id}">${initials}</div>`;
    },

    // ---- Custom Dropdown ----
    dropdown(id, options, selectedValue, opts = {}) {
        const placeholder = opts.placeholder || 'Select...';
        const disabled = opts.disabled || false;
        const selected = options.find(o => o.value === selectedValue);
        const labelText = selected ? selected.label : placeholder;
        const disabledClass = disabled ? 'disabled' : '';

        let optionsHtml = options.map(o => {
            const isSelected = o.value === selectedValue;
            const desc = o.description ? `<div class="dropdown-item-desc">${Components.escapeHtml(o.description)}</div>` : '';
            const badge = o.badge ? `<span class="badge ${o.badgeClass || ''}">${Components.escapeHtml(o.badge)}</span>` : '';
            return `<div class="dropdown-item ${isSelected ? 'selected' : ''}" data-value="${Components.escapeHtml(String(o.value))}" data-testid="dropdown-item-${o.value}">${Components.escapeHtml(o.label)} ${badge}${desc}</div>`;
        }).join('');

        return `
            <div class="custom-dropdown ${disabledClass}" id="${id}" data-testid="${id}" data-value="${Components.escapeHtml(String(selectedValue || ''))}" ${disabled ? 'data-disabled="true"' : ''}>
                <div class="dropdown-trigger" data-testid="${id}-trigger">
                    <span class="dropdown-trigger-text">${Components.escapeHtml(labelText)}</span>
                    <span class="dropdown-arrow">&#9662;</span>
                </div>
                <div class="dropdown-menu" data-testid="${id}-menu">
                    ${opts.searchable ? `<div class="dropdown-search"><input type="text" placeholder="Search..." class="dropdown-search-input" data-testid="${id}-search"></div>` : ''}
                    <div class="dropdown-items">${optionsHtml}</div>
                </div>
            </div>
        `;
    },

    // ---- Custom Modal ----
    showModal(title, bodyHtml, footerHtml = '', opts = {}) {
        const overlay = document.getElementById('modalOverlay');
        const container = document.getElementById('modalContainer');
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalBody').innerHTML = bodyHtml;
        document.getElementById('modalFooter').innerHTML = footerHtml;

        if (opts.wide) container.classList.add('modal-wide');
        else container.classList.remove('modal-wide');

        overlay.classList.add('active');
        AppState.modalOpen = true;

        // Trap focus
        setTimeout(() => {
            const firstInput = container.querySelector('input, select, textarea, button:not(.modal-close)');
            if (firstInput) firstInput.focus();
        }, 100);
    },

    closeModal() {
        document.getElementById('modalOverlay').classList.remove('active');
        AppState.modalOpen = false;
    },

    // ---- Toast Notifications ----
    showToast(message, type = 'info', duration = 4000) {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.setAttribute('data-testid', 'toast');
        const icons = { info: 'i', success: '✓', warning: '⚠', error: '✕' };
        toast.innerHTML = `<span class="toast-icon">${icons[type] || 'i'}</span><span class="toast-message">${Components.escapeHtml(message)}</span>`;
        container.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    // ---- Confirm Modal ----
    confirm(title, message, onConfirm, opts = {}) {
        const confirmLabel = opts.confirmLabel || 'Confirm';
        const confirmClass = opts.danger ? 'btn-danger' : 'btn-primary';
        Components.showModal(
            title,
            `<p>${Components.escapeHtml(message)}</p>`,
            `<button class="btn btn-secondary" onclick="Components.closeModal()" data-testid="modal-cancel">Cancel</button>
             <button class="btn ${confirmClass}" id="modalConfirmBtn" data-testid="modal-confirm">${Components.escapeHtml(confirmLabel)}</button>`
        );
        document.getElementById('modalConfirmBtn').addEventListener('click', () => {
            Components.closeModal();
            onConfirm();
        });
    },

    // ---- Tabs ----
    tabs(id, tabItems, activeTab) {
        const tabsHtml = tabItems.map(t =>
            `<div class="tab-item ${t.id === activeTab ? 'active' : ''}" data-tab="${t.id}" data-testid="tab-${t.id}">${Components.escapeHtml(t.label)}${t.count !== undefined ? ` <span class="tab-count">${t.count}</span>` : ''}</div>`
        ).join('');
        return `<div class="tabs" id="${id}" data-testid="${id}">${tabsHtml}</div>`;
    },

    // ---- Badge ----
    badge(text, type = 'default') {
        return `<span class="badge badge-${type}" data-testid="badge-${type}">${Components.escapeHtml(text)}</span>`;
    },

    // ---- Role Badge ----
    roleBadge(role) {
        const colorMap = {
            'Guest': 'guest', 'Planner': 'planner', 'Reporter': 'reporter',
            'Developer': 'developer', 'Maintainer': 'maintainer', 'Owner': 'owner',
            'Minimal Access': 'minimal'
        };
        return `<span class="role-badge role-${colorMap[role.name] || 'default'}" data-testid="role-badge">${Components.escapeHtml(role.name)}</span>`;
    },

    // ---- Visibility Badge ----
    visibilityBadge(visibility) {
        const vis = VISIBILITY[visibility.toUpperCase()] || { name: visibility, icon: '' };
        return `<span class="visibility-badge visibility-${visibility}" data-testid="visibility-badge">${vis.icon} ${vis.name}</span>`;
    },

    // ---- Membership Type Badge ----
    membershipBadge(type) {
        const labels = {
            direct: 'Direct', inherited: 'Inherited',
            shared: 'Shared', inherited_shared: 'Inherited shared'
        };
        return `<span class="membership-badge membership-${type}" data-testid="membership-badge">${labels[type] || type}</span>`;
    },

    // ---- Info/Warning/Error Boxes ----
    infoBox(message) {
        return `<div class="info-box" data-testid="info-box"><span class="box-icon">i</span> ${message}</div>`;
    },
    warningBox(message) {
        return `<div class="warning-box" data-testid="warning-box"><span class="box-icon">⚠</span> ${message}</div>`;
    },
    errorBox(message) {
        return `<div class="error-box" data-testid="error-box"><span class="box-icon">✕</span> ${message}</div>`;
    },
    successBox(message) {
        return `<div class="success-box" data-testid="success-box"><span class="box-icon">✓</span> ${message}</div>`;
    },

    // ---- Form Field ----
    formField(id, label, inputHtml, opts = {}) {
        const required = opts.required ? '<span class="required-mark">*</span>' : '';
        const helpText = opts.help ? `<div class="field-help">${opts.help}</div>` : '';
        const errorHtml = opts.error ? `<div class="error-message" data-testid="error-${id}">${Components.escapeHtml(opts.error)}</div>` : '';
        return `
            <div class="form-field ${opts.error ? 'has-error' : ''}" id="field-${id}" data-testid="field-${id}">
                <label for="${id}" class="form-label">${label} ${required}</label>
                ${inputHtml}
                ${helpText}
                ${errorHtml}
            </div>
        `;
    },

    // ---- Text Input ----
    textInput(id, value = '', opts = {}) {
        const placeholder = opts.placeholder || '';
        const maxlength = opts.maxlength ? `maxlength="${opts.maxlength}"` : '';
        const disabled = opts.disabled ? 'disabled' : '';
        const cls = opts.error ? 'field-error' : '';
        return `<input type="text" id="${id}" data-testid="${id}" class="form-input ${cls}" value="${Components.escapeAttr(value)}" placeholder="${Components.escapeAttr(placeholder)}" ${maxlength} ${disabled}>`;
    },

    // ---- Textarea ----
    textarea(id, value = '', opts = {}) {
        const placeholder = opts.placeholder || '';
        const rows = opts.rows || 3;
        return `<textarea id="${id}" data-testid="${id}" class="form-input form-textarea" rows="${rows}" placeholder="${Components.escapeAttr(placeholder)}">${Components.escapeHtml(value)}</textarea>`;
    },

    // ---- Checkbox ----
    checkbox(id, label, checked = false, opts = {}) {
        return `
            <label class="form-checkbox" data-testid="checkbox-${id}">
                <input type="checkbox" id="${id}" ${checked ? 'checked' : ''} ${opts.disabled ? 'disabled' : ''}>
                <span class="checkbox-mark"></span>
                <span class="checkbox-label">${label}</span>
            </label>
        `;
    },

    // ---- Date Input (custom text-based) ----
    dateInput(id, value = '', opts = {}) {
        const placeholder = opts.placeholder || 'YYYY-MM-DD';
        return `<input type="text" id="${id}" data-testid="${id}" class="form-input date-input ${opts.error ? 'field-error' : ''}" value="${Components.escapeAttr(value)}" placeholder="${Components.escapeAttr(placeholder)}" pattern="\\d{4}-\\d{2}-\\d{2}">`;
    },

    // ---- Empty State ----
    emptyState(title, description, actionHtml = '') {
        return `
            <div class="empty-state" data-testid="empty-state">
                <div class="empty-state-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
                </div>
                <h3 class="empty-state-title">${Components.escapeHtml(title)}</h3>
                <p class="empty-state-description">${Components.escapeHtml(description)}</p>
                ${actionHtml}
            </div>
        `;
    },

    // ---- Breadcrumb ----
    renderBreadcrumb(items) {
        const bc = document.getElementById('breadcrumb');
        if (!bc) return;
        bc.innerHTML = items.map((item, i) => {
            if (i === items.length - 1) {
                return `<span class="breadcrumb-item active">${Components.escapeHtml(item.label)}</span>`;
            }
            return `<a class="breadcrumb-item" data-route="${item.route}" href="#">${Components.escapeHtml(item.label)}</a>`;
        }).join('<span class="breadcrumb-separator">/</span>');

        // Attach route handlers
        bc.querySelectorAll('[data-route]').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                Router.navigate(el.getAttribute('data-route'));
            });
        });
    },

    // ---- Pagination ----
    pagination(currentPage, totalPages, onPageChange) {
        if (totalPages <= 1) return '';
        let pages = '';
        for (let i = 1; i <= totalPages; i++) {
            pages += `<button class="page-btn ${i === currentPage ? 'active' : ''}" data-page="${i}" data-testid="page-${i}">${i}</button>`;
        }
        return `<div class="pagination" data-testid="pagination">${pages}</div>`;
    },

    // ---- Search Input ----
    searchInput(id, value = '', placeholder = 'Search...') {
        return `
            <div class="search-input-wrapper" data-testid="${id}-wrapper">
                <span class="search-icon-inline">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                </span>
                <input type="text" id="${id}" data-testid="${id}" class="form-input search-input" value="${Components.escapeAttr(value)}" placeholder="${Components.escapeAttr(placeholder)}">
            </div>
        `;
    },

    // ---- Date formatting ----
    formatDate(isoString) {
        if (!isoString) return '—';
        const d = new Date(isoString);
        return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    },

    formatDateTime(isoString) {
        if (!isoString) return '—';
        const d = new Date(isoString);
        return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    },

    timeAgo(isoString) {
        if (!isoString) return '';
        const now = new Date();
        const d = new Date(isoString);
        const seconds = Math.floor((now - d) / 1000);
        if (seconds < 60) return 'just now';
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes}m ago`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        const days = Math.floor(hours / 24);
        if (days < 30) return `${days}d ago`;
        const months = Math.floor(days / 30);
        if (months < 12) return `${months}mo ago`;
        return `${Math.floor(months / 12)}y ago`;
    },

    // ---- Utility ----
    escapeHtml(str) {
        if (str === null || str === undefined) return '';
        const div = document.createElement('div');
        div.textContent = String(str);
        return div.innerHTML;
    },

    escapeAttr(str) {
        if (str === null || str === undefined) return '';
        return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
};

// ---- Dropdown Global Event Handling ----
document.addEventListener('click', (e) => {
    // Close all dropdowns
    document.querySelectorAll('.custom-dropdown.open').forEach(dd => {
        if (!dd.contains(e.target)) dd.classList.remove('open');
    });

    // Toggle dropdown
    const trigger = e.target.closest('.dropdown-trigger');
    if (trigger) {
        const dropdown = trigger.closest('.custom-dropdown');
        if (dropdown && !dropdown.hasAttribute('data-disabled')) {
            dropdown.classList.toggle('open');
            e.stopPropagation();
        }
    }

    // Select dropdown item
    const item = e.target.closest('.dropdown-item');
    if (item && item.closest('.custom-dropdown')) {
        const dropdown = item.closest('.custom-dropdown');
        const value = item.getAttribute('data-value');
        dropdown.setAttribute('data-value', value);
        dropdown.querySelector('.dropdown-trigger-text').textContent = item.textContent.trim();
        dropdown.querySelectorAll('.dropdown-item').forEach(i => i.classList.remove('selected'));
        item.classList.add('selected');
        dropdown.classList.remove('open');

        // Dispatch custom event
        dropdown.dispatchEvent(new CustomEvent('change', { detail: { value } }));
    }
});

// Dropdown search filtering
document.addEventListener('input', (e) => {
    if (e.target.classList.contains('dropdown-search-input')) {
        const query = e.target.value.toLowerCase();
        const items = e.target.closest('.dropdown-menu').querySelectorAll('.dropdown-item');
        items.forEach(item => {
            item.style.display = item.textContent.toLowerCase().includes(query) ? '' : 'none';
        });
    }
});

// Modal close events
document.addEventListener('click', (e) => {
    if (e.target.id === 'modalOverlay') Components.closeModal();
    if (e.target.id === 'modalClose' || e.target.closest('#modalClose')) Components.closeModal();
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && AppState.modalOpen) Components.closeModal();
});

// User menu dropdown
document.addEventListener('click', (e) => {
    const avatar = e.target.closest('#currentUserAvatar');
    if (avatar) {
        document.getElementById('userDropdown').classList.toggle('show');
        e.stopPropagation();
        return;
    }
    document.getElementById('userDropdown')?.classList.remove('show');

    const menuItem = e.target.closest('.user-dropdown .dropdown-item');
    if (menuItem) {
        const action = menuItem.getAttribute('data-action');
        if (action === 'profile') Router.navigate('/profile');
        if (action === 'signout') Components.showToast('Sign out simulated', 'info');
    }
});
