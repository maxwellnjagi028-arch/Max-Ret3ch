// MaxReT3ch AI - Core Application Framework
const App = {
    currentUser: null,

    async init() {
        await this.checkAuth();
        this.updateAuthUI();
        this.initGlobalChatModal();
    },

    async checkAuth() {
        try {
            const res = await fetch('/api/auth/me');
            const data = await res.json();
            if (data.authenticated && data.user) {
                this.currentUser = data.user;
            } else {
                this.currentUser = null;
            }
        } catch (e) {
            console.warn('Auth check failed:', e);
            this.currentUser = null;
        }
    },

    updateAuthUI() {
        const guestElements = document.querySelectorAll('.auth-guest-only');
        const userElements = document.querySelectorAll('.auth-user-only');
        const staffElements = document.querySelectorAll('.auth-staff-only');
        const userNameDisplays = document.querySelectorAll('.auth-user-name');
        const userRoleDisplays = document.querySelectorAll('.auth-user-role');

        if (this.currentUser) {
            guestElements.forEach(el => el.classList.add('hidden'));
            userElements.forEach(el => el.classList.remove('hidden'));
            
            const isStaffOrAdmin = ['admin', 'staff'].includes(this.currentUser.role);
            staffElements.forEach(el => {
                if (isStaffOrAdmin) el.classList.remove('hidden');
                else el.classList.add('hidden');
            });

            userNameDisplays.forEach(el => el.textContent = this.currentUser.full_name || this.currentUser.username);
            userRoleDisplays.forEach(el => {
                el.textContent = this.currentUser.role.toUpperCase();
                if (this.currentUser.role === 'admin') {
                    el.className = 'px-2 py-0.5 rounded text-xs font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/30';
                } else if (this.currentUser.role === 'staff') {
                    el.className = 'px-2 py-0.5 rounded text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30';
                } else {
                    el.className = 'px-2 py-0.5 rounded text-xs font-semibold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30';
                }
            });
        } else {
            guestElements.forEach(el => el.classList.remove('hidden'));
            userElements.forEach(el => el.classList.add('hidden'));
            staffElements.forEach(el => el.classList.add('hidden'));
        }
    },

    async logout() {
        try {
            await fetch('/api/auth/logout', { method: 'POST' });
            this.showToast('Logged out successfully', 'info');
            setTimeout(() => {
                window.location.href = '/';
            }, 600);
        } catch (e) {
            console.error('Logout error:', e);
        }
    },

    showToast(message, type = 'info') {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        const colors = {
            success: 'bg-emerald-950/90 border-emerald-500 text-emerald-200',
            error: 'bg-rose-950/90 border-rose-500 text-rose-200',
            warning: 'bg-amber-950/90 border-amber-500 text-amber-200',
            info: 'bg-cyan-950/90 border-cyan-500 text-cyan-200'
        };

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: '⚡'
        };

        toast.className = `flex items-center gap-3 px-4 py-3 rounded-lg border backdrop-blur-md shadow-lg shadow-black/50 transition-all duration-300 transform translate-y-4 opacity-0 ${colors[type] || colors.info}`;
        toast.innerHTML = `
            <span class="font-bold text-lg">${icons[type] || '⚡'}</span>
            <div class="text-sm font-medium flex-1">${message}</div>
        `;

        container.appendChild(toast);
        setTimeout(() => {
            toast.classList.remove('translate-y-4', 'opacity-0');
        }, 10);

        setTimeout(() => {
            toast.classList.add('opacity-0', 'translate-y-2');
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    },

    formatCurrency(amount) {
        const val = Number(amount || 0);
        return 'KSh ' + val.toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },

    initGlobalChatModal() {
        // Floating Ted AI button listener
        const floatingBtn = document.getElementById('floating-ted-btn');
        const modal = document.getElementById('floating-ted-modal');
        const closeBtn = document.getElementById('close-floating-ted');

        if (floatingBtn && modal) {
            floatingBtn.addEventListener('click', () => {
                modal.classList.toggle('hidden');
                if (!modal.classList.contains('hidden')) {
                    const input = document.getElementById('floating-ted-input');
                    if (input) input.focus();
                }
            });
        }

        if (closeBtn && modal) {
            closeBtn.addEventListener('click', () => {
                modal.classList.add('hidden');
            });
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
