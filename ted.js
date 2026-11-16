// MaxReT3ch AI - Ted Intelligent Digital Employee Interface
const Ted = {
    sessionId: 'sess_' + Math.floor(Math.random() * 900000 + 100000),
    voiceEnabled: false,
    speechSynth: window.speechSynthesis || null,
    isListening: false,
    recognition: null,

    init() {
        this.initSpeechRecognition();
        this.bindEvents();
    },

    bindEvents() {
        // Chat form submit
        const chatForm = document.getElementById('ted-chat-form');
        const chatInput = document.getElementById('ted-chat-input');
        if (chatForm && chatInput) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const msg = chatInput.value.trim();
                if (msg) {
                    this.sendMessage(msg);
                    chatInput.value = '';
                }
            });
        }

        // Voice toggle
        const voiceBtn = document.getElementById('ted-voice-toggle');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => {
                this.voiceEnabled = !this.voiceEnabled;
                voiceBtn.classList.toggle('text-cyan-400', this.voiceEnabled);
                voiceBtn.classList.toggle('border-cyan-400', this.voiceEnabled);
                if (this.voiceEnabled) {
                    this.speak("Ted voice synthesis online. How can I assist your operations?");
                    App.showToast("Ted Voice Synthesis Enabled", "info");
                } else {
                    if (this.speechSynth) this.speechSynth.cancel();
                    App.showToast("Ted Voice Muted", "info");
                }
            });
        }

        // Mic Speech-to-Text
        const micBtn = document.getElementById('ted-mic-btn');
        if (micBtn && this.recognition) {
            micBtn.addEventListener('click', () => {
                if (this.isListening) {
                    this.recognition.stop();
                } else {
                    try {
                        this.recognition.start();
                    } catch (e) {
                        console.warn(e);
                    }
                }
            });
        }

        // Floating chat quick listeners
        const floatForm = document.getElementById('floating-ted-form');
        const floatInput = document.getElementById('floating-ted-input');
        if (floatForm && floatInput) {
            floatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const msg = floatInput.value.trim();
                if (msg) {
                    this.sendFloatingMessage(msg);
                    floatInput.value = '';
                }
            });
        }
    },

    initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onstart = () => {
                this.isListening = true;
                const micBtn = document.getElementById('ted-mic-btn');
                if (micBtn) micBtn.classList.add('text-rose-400', 'animate-pulse');
                App.showToast("Ted is listening...", "info");
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const chatInput = document.getElementById('ted-chat-input');
                if (chatInput) {
                    chatInput.value = transcript;
                    this.sendMessage(transcript);
                    chatInput.value = '';
                }
            };

            this.recognition.onend = () => {
                this.isListening = false;
                const micBtn = document.getElementById('ted-mic-btn');
                if (micBtn) micBtn.classList.remove('text-rose-400', 'animate-pulse');
            };

            this.recognition.onerror = () => {
                this.isListening = false;
                const micBtn = document.getElementById('ted-mic-btn');
                if (micBtn) micBtn.classList.remove('text-rose-400', 'animate-pulse');
            };
        }
    },

    speak(text) {
        if (!this.voiceEnabled || !this.speechSynth) return;
        this.speechSynth.cancel();
        // Clean markdown for speech
        const cleanText = text.replace(/[*#_`\[\]()]/g, '').replace(/https?:\/\/\S+/g, '');
        const utterance = new SpeechSynthesisUtterance(cleanText.substring(0, 300));
        utterance.rate = 1.05;
        utterance.pitch = 0.95;
        this.speechSynth.speak(utterance);
    },

    async sendMessage(messageText) {
        const chatContainer = document.getElementById('ted-messages-container');
        if (!chatContainer) return;

        // Append user bubble
        this.appendMessage('user', messageText);

        // Typing indicator
        const typingEl = this.appendTypingIndicator();

        try {
            const visitorName = App.currentUser ? App.currentUser.full_name : 'Visitor';
            const visitorEmail = App.currentUser ? App.currentUser.email : null;

            const res = await fetch('/api/ted/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: messageText,
                    session_id: this.sessionId,
                    visitor_name: visitorName,
                    visitor_email: visitorEmail
                })
            });

            const data = await res.json();
            typingEl.remove();

            if (res.ok) {
                this.appendTedReply(data);
                this.speak(data.reply);
            } else {
                this.appendMessage('ted', "I encountered an operational anomaly processing your request. Please retry.");
            }
        } catch (e) {
            console.error(e);
            typingEl.remove();
            this.appendMessage('ted', "Connection to Ted's neural core timed out. Please check network connectivity.");
        }
    },

    appendMessage(sender, text) {
        const container = document.getElementById('ted-messages-container');
        if (!container) return;

        const row = document.createElement('div');
        row.className = sender === 'user' ? 'flex justify-end mb-4' : 'flex justify-start mb-4';

        if (sender === 'user') {
            row.innerHTML = `
                <div class="chat-bubble-user p-4 max-w-lg text-slate-100 text-sm leading-relaxed shadow-lg">
                    ${this.escapeHtml(text)}
                </div>
            `;
        } else {
            row.innerHTML = `
                <div class="flex items-start gap-3 max-w-2xl">
                    <div class="w-8 h-8 rounded-full bg-cyan-950 border border-cyan-400 flex items-center justify-center text-cyan-300 text-xs font-bold shrink-0 shadow-[0_0_10px_rgba(0,240,255,0.4)]">
                        TED
                    </div>
                    <div class="chat-bubble-ted p-4 text-slate-200 text-sm leading-relaxed">
                        ${this.formatMarkdown(text)}
                    </div>
                </div>
            `;
        }

        container.appendChild(row);
        container.scrollTop = container.scrollHeight;
    },

    appendTedReply(data) {
        const container = document.getElementById('ted-messages-container');
        if (!container) return;

        const row = document.createElement('div');
        row.className = 'flex items-start gap-3 max-w-2xl mb-4';

        let extraCardHtml = '';

        // If Ted generated a Proposal
        if (data.generated_proposal) {
            const p = data.generated_proposal;
            extraCardHtml += `
                <div class="mt-4 p-4 rounded-lg bg-cyan-950/40 border border-cyan-400/40 shadow-[0_0_15px_rgba(0,240,255,0.15)]">
                    <div class="flex items-center justify-between border-b border-cyan-500/30 pb-2 mb-3">
                        <span class="text-xs font-bold text-cyan-400 uppercase tracking-wider">Formal Quotation Draft</span>
                        <span class="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold">⚠️ Pending Executive Human Approval</span>
                    </div>
                    <div class="text-sm font-semibold text-white">${this.escapeHtml(p.project_title)}</div>
                    <div class="text-xs text-slate-400 mt-0.5">Quote #: ${p.quote_number} | Turnaround: ${p.estimated_days} business days</div>
                    
                    <div class="mt-3 divide-y divide-slate-800 text-xs">
                        ${p.items.map(it => `
                            <div class="flex justify-between py-1 text-slate-300">
                                <span>${this.escapeHtml(it.item)}</span>
                                <span class="font-mono text-cyan-300">KSh ${it.total.toLocaleString()}</span>
                            </div>
                        `).join('')}
                    </div>

                    <div class="mt-3 pt-2 border-t border-slate-700 flex justify-between items-center text-xs">
                        <span class="text-slate-400">Total with 8% Ted Incentive:</span>
                        <span class="text-base font-bold font-mono text-cyan-400">KSh ${p.total_amount.toLocaleString()}</span>
                    </div>

                    <div class="mt-4 flex gap-2">
                        <a href="/proposal/${p.quote_number}" target="_blank" class="px-3 py-1.5 rounded bg-cyan-500 text-black font-semibold text-xs hover:bg-cyan-400 transition-colors flex items-center gap-1.5 shadow-[0_0_10px_rgba(0,240,255,0.3)]">
                            <span>📄 View Formal Document</span>
                        </a>
                        <a href="/dashboard" class="px-3 py-1.5 rounded bg-slate-800 text-slate-200 border border-slate-700 font-medium text-xs hover:bg-slate-700 transition-colors">
                            Admin Approval Queue
                        </a>
                    </div>
                </div>
            `;
        }

        // If Diagnostic Steps
        if (data.diagnostic_result) {
            const d = data.diagnostic_result;
            extraCardHtml += `
                <div class="mt-4 p-4 rounded-lg bg-slate-900/90 border border-cyan-500/30">
                    <div class="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2">⚡ Lab Diagnostic Recommendation</div>
                    <div class="text-xs text-slate-300">${d.triage_summary}</div>
                    <div class="mt-3 flex gap-2">
                        <a href="/hardware" class="px-3 py-1.5 rounded bg-cyan-500 text-black font-semibold text-xs hover:bg-cyan-400 transition-colors">
                            Book Hardware Bench Intake
                        </a>
                    </div>
                </div>
            `;
        }

        // Suggested Actions Pills
        let actionsHtml = '';
        if (data.suggested_actions && data.suggested_actions.length > 0) {
            actionsHtml = `
                <div class="mt-3 flex flex-wrap gap-2">
                    ${data.suggested_actions.map(act => `
                        <button type="button" onclick="Ted.handleAction('${this.escapeHtml(act.label)}', '${act.action}')" class="px-2.5 py-1 rounded-full text-xs font-medium bg-cyan-950/60 text-cyan-300 border border-cyan-500/30 hover:border-cyan-400 hover:bg-cyan-900/60 transition-all shadow-[0_0_8px_rgba(0,240,255,0.1)]">
                            ${this.escapeHtml(act.label)}
                        </button>
                    `).join('')}
                </div>
            `;
        }

        row.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-cyan-950 border border-cyan-400 flex items-center justify-center text-cyan-300 text-xs font-bold shrink-0 shadow-[0_0_10px_rgba(0,240,255,0.4)]">
                TED
            </div>
            <div class="flex-1 chat-bubble-ted p-4 text-slate-200 text-sm leading-relaxed">
                ${this.formatMarkdown(data.reply)}
                ${extraCardHtml}
                ${actionsHtml}
            </div>
        `;

        container.appendChild(row);
        container.scrollTop = container.scrollHeight;
    },

    appendTypingIndicator() {
        const container = document.getElementById('ted-messages-container');
        const row = document.createElement('div');
        row.className = 'flex items-center gap-3 max-w-lg mb-4';
        row.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-cyan-950 border border-cyan-400 flex items-center justify-center text-cyan-300 text-xs font-bold shrink-0 animate-pulse">
                TED
            </div>
            <div class="chat-bubble-ted px-4 py-3 flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-cyan-400 animate-bounce"></span>
                <span class="w-2 h-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.2s]"></span>
                <span class="w-2 h-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.4s]"></span>
            </div>
        `;
        container.appendChild(row);
        container.scrollTop = container.scrollHeight;
        return row;
    },

    handleAction(label, actionKey) {
        if (actionKey.startsWith('view_proposal_')) {
            const quoteNum = actionKey.replace('view_proposal_', '');
            window.open(`/proposal/${quoteNum}`, '_blank');
            return;
        }
        if (actionKey === 'request_quote') {
            this.sendMessage("Please provide a project quotation for our company.");
            return;
        }
        if (actionKey === 'troubleshoot') {
            this.sendMessage("My PC has fans spinning but shows no display on the screen.");
            return;
        }
        if (actionKey === 'ewaste' || actionKey === 'open_ewaste_calculator') {
            window.location.href = '/green-tech';
            return;
        }
        if (actionKey === 'hardware' || actionKey === 'view_hardware') {
            window.location.href = '/hardware';
            return;
        }
        if (actionKey === 'open_dashboard' || actionKey === 'open_approvals') {
            window.location.href = '/dashboard';
            return;
        }
        if (actionKey === 'view_tutorials' || actionKey === 'launch_sandbox') {
            window.location.href = '/education';
            return;
        }
        if (actionKey === 'book_repair') {
            window.location.href = '/hardware#repair-section';
            return;
        }
        if (actionKey === 'business_report') {
            this.sendMessage("Show me the executive business performance report.");
            return;
        }
        
        // Default: send label text
        this.sendMessage(label);
    },

    async sendFloatingMessage(messageText) {
        const container = document.getElementById('floating-ted-messages');
        if (!container) return;

        // User message
        const uRow = document.createElement('div');
        uRow.className = 'flex justify-end mb-2';
        uRow.innerHTML = `<div class="bg-slate-800 text-xs text-white p-2.5 rounded-lg max-w-[85%]">${this.escapeHtml(messageText)}</div>`;
        container.appendChild(uRow);
        container.scrollTop = container.scrollHeight;

        try {
            const res = await fetch('/api/ted/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: messageText,
                    session_id: this.sessionId,
                    visitor_name: App.currentUser ? App.currentUser.full_name : 'Visitor'
                })
            });
            const data = await res.json();
            const tRow = document.createElement('div');
            tRow.className = 'flex justify-start mb-2';
            tRow.innerHTML = `
                <div class="flex gap-2 max-w-[90%]">
                    <div class="w-6 h-6 rounded-full bg-cyan-900 border border-cyan-400 text-cyan-300 text-[10px] font-bold flex items-center justify-center shrink-0">T</div>
                    <div class="bg-cyan-950/80 border border-cyan-500/30 text-xs text-slate-200 p-2.5 rounded-lg leading-relaxed">
                        ${this.formatMarkdown(data.reply)}
                    </div>
                </div>
            `;
            container.appendChild(tRow);
            container.scrollTop = container.scrollHeight;
        } catch (e) {
            console.error(e);
        }
    },

    formatMarkdown(text) {
        if (!text) return '';
        let escaped = this.escapeHtml(text);
        
        // Bold
        escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>');
        // Bullet points
        escaped = escaped.replace(/^\s*•\s*(.*)$/gm, '<li class="ml-4 list-disc text-slate-300">$1</li>');
        escaped = escaped.replace(/^\s*\d+\.\s*(.*)$/gm, '<li class="ml-4 list-decimal text-slate-300">$1</li>');
        // Line breaks
        escaped = escaped.replace(/\n\n/g, '<div class="h-2"></div>');
        escaped = escaped.replace(/\n/g, '<br/>');

        return escaped;
    },

    escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    Ted.init();
});
