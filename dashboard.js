// MaxReT3ch AI - Executive Dashboard & Human Approval Command Center
const Dashboard = {
    async init() {
        await this.loadMetrics();
        await this.loadPendingApprovals();
        await this.loadLeads();
        await this.loadCampaigns();
        await this.loadInteractions();
        this.bindEvents();
    },

    bindEvents() {
        // Marketing generator form
        const mktForm = document.getElementById('gen-marketing-form');
        if (mktForm) {
            mktForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const title = document.getElementById('mkt-title').value;
                const audience = document.getElementById('mkt-audience').value;
                const channel = document.getElementById('mkt-channel').value;

                try {
                    const res = await fetch('/api/ted/marketing', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ title, audience, channel })
                    });
                    const data = await res.json();
                    if (data.success) {
                        App.showToast("Ted generated marketing campaign successfully!", "success");
                        await this.loadCampaigns();
                    }
                } catch (err) {
                    App.showToast("Failed to generate campaign", "error");
                }
            });
        }
    },

    async loadMetrics() {
        try {
            const res = await fetch('/api/admin/metrics');
            if (res.status === 401 || res.status === 403) {
                // Not authorized
                return;
            }
            const data = await res.json();
            const m = data.metrics;

            // Update KPI cards
            const elPipeline = document.getElementById('kpi-pipeline');
            const elApproved = document.getElementById('kpi-approved');
            const elQueue = document.getElementById('kpi-queue');
            const elLeads = document.getElementById('kpi-leads');
            const elRepairs = document.getElementById('kpi-repairs');
            const elCarbon = document.getElementById('kpi-carbon');

            if (elPipeline) elPipeline.textContent = App.formatCurrency(m.total_pipeline_val);
            if (elApproved) elApproved.textContent = App.formatCurrency(m.approved_revenue);
            if (elQueue) {
                elQueue.textContent = m.pending_approval;
                if (m.pending_approval > 0) {
                    elQueue.classList.add('text-amber-400');
                }
            }
            if (elLeads) elLeads.textContent = `${m.total_leads} (${m.hot_leads} Hot)`;
            if (elRepairs) elRepairs.textContent = m.active_repairs;
            if (elCarbon) elCarbon.textContent = `${m.total_carbon_offset.toLocaleString()} kg`;
        } catch (e) {
            console.error('Failed to load metrics:', e);
        }
    },

    async loadPendingApprovals() {
        const container = document.getElementById('pending-approvals-table');
        if (!container) return;

        try {
            const res = await fetch('/api/proposals?status_filter=pending_approval');
            const data = await res.json();
            const list = data.proposals || [];

            if (list.length === 0) {
                container.innerHTML = `
                    <div class="p-6 text-center text-slate-400 text-sm">
                        <span class="text-emerald-400 text-lg">✓</span> All quotations and proposals have been reviewed. Queue is clear!
                    </div>
                `;
                return;
            }

            container.innerHTML = list.map(p => `
                <tr class="border-b border-slate-800/80 hover:bg-slate-800/30 transition-colors">
                    <td class="py-3 px-4 text-xs font-mono font-bold text-cyan-400">
                        <a href="/proposal/${p.quote_number}" target="_blank" class="hover:underline flex items-center gap-1">
                            ${p.quote_number} <span class="text-[10px] text-slate-500">↗</span>
                        </a>
                    </td>
                    <td class="py-3 px-4">
                        <div class="text-sm font-medium text-white">${p.client_name}</div>
                        <div class="text-xs text-slate-400">${p.client_company || p.client_email}</div>
                    </td>
                    <td class="py-3 px-4 text-xs text-slate-300 max-w-xs truncate">
                        ${p.project_title}
                    </td>
                    <td class="py-3 px-4 text-xs font-mono font-semibold text-emerald-400">
                        ${App.formatCurrency(p.total_amount)}
                    </td>
                    <td class="py-3 px-4 text-xs text-slate-400">
                        ${p.estimated_days} days
                    </td>
                    <td class="py-3 px-4 text-right">
                        <div class="flex items-center justify-end gap-2">
                            <button onclick="Dashboard.handleApproval('${p.quote_number}', 'approved')" class="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-semibold hover:bg-emerald-500/30 transition-all">
                                ✓ Approve
                            </button>
                            <button onclick="Dashboard.handleApproval('${p.quote_number}', 'rejected')" class="px-2.5 py-1 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40 text-xs font-semibold hover:bg-rose-500/30 transition-all">
                                ✕ Reject
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        } catch (e) {
            console.error(e);
        }
    },

    async handleApproval(quoteNumber, decision) {
        const notes = prompt(`Enter executive review notes for proposal ${quoteNumber} (${decision}):`, 
            decision === 'approved' ? 'Approved by executive management. Ready for client delivery.' : 'Scope requires pricing revision.');
        if (notes === null) return; // Cancelled

        try {
            const res = await fetch(`/api/proposals/${quoteNumber}/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ decision, approval_notes: notes })
            });
            const data = await res.json();
            if (res.ok) {
                App.showToast(`Proposal ${quoteNumber} ${decision}!`, decision === 'approved' ? 'success' : 'warning');
                await this.loadMetrics();
                await this.loadPendingApprovals();
            } else {
                App.showToast(data.detail || "Action failed", "error");
            }
        } catch (e) {
            App.showToast("Server error processing approval", "error");
        }
    },

    async loadLeads() {
        const container = document.getElementById('leads-table');
        if (!container) return;

        try {
            const res = await fetch('/api/leads');
            const data = await res.json();
            const list = data.leads || [];

            container.innerHTML = list.map(l => {
                const scoreBadge = l.score === 'hot' 
                    ? '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse">🔥 HOT</span>'
                    : l.score === 'warm'
                    ? '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">⚡ WARM</span>'
                    : '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-700 text-slate-300">COLD</span>';

                return `
                    <tr class="border-b border-slate-800/80 hover:bg-slate-800/30 transition-colors">
                        <td class="py-3 px-4">
                            <div class="text-sm font-semibold text-white">${l.name}</div>
                            <div class="text-xs text-slate-400">${l.email} ${l.company ? '• ' + l.company : ''}</div>
                        </td>
                        <td class="py-3 px-4 text-xs text-cyan-300 capitalize">
                            ${l.vertical_interest ? l.vertical_interest.replace('_', ' ') : 'General'}
                        </td>
                        <td class="py-3 px-4 text-xs font-mono text-slate-200">
                            ${l.estimated_budget ? App.formatCurrency(l.estimated_budget) : 'TBD'}
                        </td>
                        <td class="py-3 px-4">
                            ${scoreBadge}
                        </td>
                        <td class="py-3 px-4 text-xs">
                            <select onchange="Dashboard.updateLeadStatus(${l.id}, this.value)" class="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded px-2 py-1 focus:border-cyan-400 outline-none">
                                <option value="new" ${l.status === 'new' ? 'selected' : ''}>New</option>
                                <option value="contacted" ${l.status === 'contacted' ? 'selected' : ''}>Contacted</option>
                                <option value="in_review" ${l.status === 'in_review' ? 'selected' : ''}>In Review</option>
                                <option value="proposal_ready" ${l.status === 'proposal_ready' ? 'selected' : ''}>Proposal Ready</option>
                                <option value="won" ${l.status === 'won' ? 'selected' : ''}>Won (Closed)</option>
                                <option value="lost" ${l.status === 'lost' ? 'selected' : ''}>Lost</option>
                            </select>
                        </td>
                        <td class="py-3 px-4 text-xs text-slate-400">
                            ${l.captured_by === 'ted_ai' ? '<span class="text-cyan-400 font-semibold">🤖 Ted AI</span>' : 'Web Form'}
                        </td>
                    </tr>
                `;
            }).join('');
        } catch (e) {
            console.error(e);
        }
    },

    async updateLeadStatus(leadId, newStatus) {
        try {
            const res = await fetch(`/api/leads/${leadId}/status`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            if (res.ok) {
                App.showToast(`Lead status updated to ${newStatus}`, "success");
            }
        } catch (e) {
            App.showToast("Failed to update status", "error");
        }
    },

    async loadCampaigns() {
        const container = document.getElementById('campaigns-list');
        if (!container) return;

        try {
            const res = await fetch('/api/admin/campaigns');
            const data = await res.json();
            const list = data.campaigns || [];

            container.innerHTML = list.map(c => `
                <div class="p-4 rounded-lg bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 transition-all">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-xs font-bold text-cyan-400 uppercase tracking-wide">${c.channel}</span>
                        <span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400">${c.status.toUpperCase()}</span>
                    </div>
                    <div class="text-sm font-semibold text-white mb-2">${c.title}</div>
                    <div class="text-xs text-slate-300 whitespace-pre-line max-h-36 overflow-y-auto bg-black/40 p-3 rounded font-mono border border-slate-800/80 mb-3">
                        ${c.generated_content}
                    </div>
                    <div class="flex items-center justify-between text-xs text-slate-400">
                        <span>Audience: <strong class="text-slate-200">${c.target_audience}</strong></span>
                        <span>Projected Reach: <strong class="text-cyan-300 font-mono">${c.projected_reach.toLocaleString()}</strong></span>
                    </div>
                </div>
            `).join('');
        } catch (e) {
            console.error(e);
        }
    },

    async loadInteractions() {
        const container = document.getElementById('interactions-list');
        if (!container) return;

        try {
            const res = await fetch('/api/ted/interactions');
            const data = await res.json();
            const list = data.interactions || [];

            container.innerHTML = list.map(i => `
                <div class="p-4 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
                    <div class="flex items-center justify-between mb-1.5">
                        <span class="font-semibold text-white">${i.visitor_name} ${i.visitor_email ? '(' + i.visitor_email + ')' : ''}</span>
                        <span class="px-2 py-0.5 rounded text-[10px] font-semibold ${i.sentiment === 'positive' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-700 text-slate-300'}">
                            ${i.sentiment.toUpperCase()}
                        </span>
                    </div>
                    <div class="text-slate-300 mb-2">${i.summary}</div>
                    <div class="text-[11px] text-cyan-400 font-mono">Intent: ${i.primary_intent}</div>
                </div>
            `).join('');
        } catch (e) {
            console.error(e);
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    Dashboard.init();
});
