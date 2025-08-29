// Real Estate AI Bot - JavaScript principal

class RealEstateAI {
    constructor() {
        this.apiBase = '/api';
        this.dataLoaded = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupQuickQuestions();
        console.log('🤖 Real Estate AI Bot initialized');
    }

    setupEventListeners() {
        // Load data button
        document.getElementById('loadDataBtn').addEventListener('click', () => {
            this.loadData();
        });

        // Chat input and send
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');

        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !sendBtn.disabled) {
                this.sendMessage();
            }
        });

        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });
    }

    setupQuickQuestions() {
        document.querySelectorAll('.quick-question').forEach(btn => {
            btn.addEventListener('click', () => {
                const question = btn.getAttribute('data-question');
                document.getElementById('chatInput').value = question;
                if (this.dataLoaded) {
                    this.sendMessage();
                }
            });
        });
    }

    async loadData() {
        const loadBtn = document.getElementById('loadDataBtn');
        const loadStatus = document.getElementById('loadStatus');
        
        loadBtn.disabled = true;
        loadBtn.textContent = '⏳ Cargando...';
        loadStatus.innerHTML = '<div style="color: #666;">Procesando archivos CSV...</div>';

        try {
            const response = await fetch(`${this.apiBase}/load-data`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();

            if (data.success) {
                this.dataLoaded = true;
                loadStatus.innerHTML = `<div class="success">✅ ${data.message}</div>`;
                
                // Update status bar
                document.getElementById('totalRecords').textContent = data.stats.records.toLocaleString();
                document.getElementById('activeFunds').textContent = data.stats.funds;
                document.getElementById('metricsAvailable').textContent = data.stats.metrics;
                document.getElementById('systemStatus').textContent = '🟢';

                // Enable chat
                document.getElementById('chatInput').disabled = false;
                document.getElementById('sendBtn').disabled = false;

                // Load funds summary
                await this.loadFundsSummary();

                // Add success message to chat
                this.addMessage('ai', `✅ Datos cargados exitosamente!<br>
                    📊 ${data.stats.records.toLocaleString()} registros procesados<br>
                    🏢 ${data.stats.funds} fondos disponibles<br>
                    📈 ${data.stats.metrics} métricas diferentes<br><br>
                    Ahora puedes hacer preguntas sobre tus fondos.`);

            } else {
                throw new Error(data.error || 'Error desconocido');
            }

        } catch (error) {
            loadStatus.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
        } finally {
            loadBtn.disabled = false;
            loadBtn.textContent = '📂 Cargar Datos';
        }
    }

    async loadFundsSummary() {
        try {
            const response = await fetch(`${this.apiBase}/funds-summary`);
            const data = await response.json();

            if (data.success) {
                this.displayFundsSummary(data.summary);
            }
        } catch (error) {
            console.error('Error loading funds summary:', error);
        }
    }

    displayFundsSummary(summary) {
        const grid = document.getElementById('fundsGrid');
        grid.innerHTML = '';

        Object.entries(summary).forEach(([fundName, metrics]) => {
            const card = document.createElement('div');
            card.className = 'fund-card';

            const formatValue = (value, isPercentage = false) => {
                if (value === null || value === undefined) return 'N/A';
                if (isPercentage) return `${(value * 100).toFixed(2)}%`;
                return typeof value === 'number' ? value.toLocaleString() : value;
            };

            card.innerHTML = `
                <h3>${fundName}</h3>
                <div class="fund-metric">
                    <div class="metric-label">Net IRR</div>
                    <div class="metric-value">${formatValue(metrics.net_irr, true)}</div>
                </div>
                <div class="fund-metric">
                    <div class="metric-label">Net TVPI</div>
                    <div class="metric-value">${formatValue(metrics.net_tvpi)}x</div>
                </div>
                <div class="fund-metric">
                    <div class="metric-label">NAV</div>
                    <div class="metric-value">${formatValue(metrics.nav)}</div>
                </div>
            `;

            grid.appendChild(card);
        });
    }

    async sendMessage() {
        const input = document.getElementById('chatInput');
        const question = input.value.trim();

        if (!question || !this.dataLoaded) return;

        // Add user message
        this.addMessage('user', question);
        input.value = '';

        // Show loading
        const loadingId = this.addMessage('ai', '🤔 Analizando tu pregunta...');

        try {
            const response = await fetch(`${this.apiBase}/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });

            const data = await response.json();

            // Remove loading message
            document.getElementById(loadingId).remove();

            if (data.success) {
                this.displayQueryResult(data.result);
            } else {
                this.addMessage('ai', `❌ Error: ${data.error}`);
            }

        } catch (error) {
            document.getElementById(loadingId).remove();
            this.addMessage('ai', `❌ Error de conexión: ${error.message}`);
        }
    }

    displayQueryResult(result) {
        let response = `<strong>🎯 ${result.analysis_type || 'Análisis'}</strong><br><br>`;

        if (result.query_result) {
            const qr = result.query_result;

            if (qr.error) {
                response += `❌ ${qr.error}`;
            } else {
                response += `📋 ${qr.summary}<br><br>`;

                if (qr.results) {
                    response += '<strong>📊 Resultados:</strong><br>';
                    
                    Object.entries(qr.results).forEach(([key, value]) => {
                        if (typeof value === 'object' && value !== null) {
                            response += `<br><strong>${key}:</strong><br>`;
                            Object.entries(value).forEach(([subKey, subValue]) => {
                                if (subValue !== null && subValue !== undefined) {
                                    response += `&nbsp;&nbsp;• ${subKey}: ${subValue}<br>`;
                                }
                            });
                        } else if (value !== null && value !== undefined) {
                            let displayValue = value;
                            if (typeof value === 'number' && key.toLowerCase().includes('irr')) {
                                displayValue = `${(value * 100).toFixed(2)}%`;
                            }
                            response += `• ${key}: ${displayValue}<br>`;
                        }
                    });
                }

                if (qr.best_performer) {
                    response += `<br>🏆 <strong>Mejor performance:</strong> ${qr.best_performer}`;
                }
            }
        }

        this.addMessage('ai', response);
    }

    addMessage(sender, message) {
        const container = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        messageDiv.id = messageId;
        messageDiv.className = `message ${sender}`;
        messageDiv.innerHTML = `<div class="message-bubble">${message}</div>`;

        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;

        return messageId;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new RealEstateAI();
});