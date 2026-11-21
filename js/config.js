/*
 * Configuration System for Streaming Dashboard
 * Loads stream data from data/streams.json (organized by sheet/tab)
 */

class ConfigManager {
    constructor() {
        this.streams = [];
        this.config = null;
        this.sheets = {};
        this.activeSheet = null;
    }

    // Load configuration from JSON file
    async loadConfig() {
        try {
            const response = await fetch(`data/streams.json?t=${Date.now()}`, { cache: 'no-store' });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.config = await response.json();
            this.sheets = this.config.sheets || {};
            // Default active sheet is the first one (Religa)
            this.activeSheet = Object.keys(this.sheets)[0] || null;
            console.log('Configuration loaded successfully');
            return this.config;
        } catch (error) {
            console.error('Failed to load configuration:', error);
            this.handleConfigError(error);
            return null;
        }
    }

    // Get all sheet names
    getSheetNames() {
        return Object.keys(this.sheets);
    }

    // Get raw entries for a given sheet
    getSheet(name) {
        return this.sheets[name] || [];
    }

    // Process stream data for a given sheet
    processStreams(sheetName) {
        const name = sheetName || this.activeSheet;
        const raw = this.getSheet(name);
        this.streams = raw.map((stream, i) => ({
            id: stream.id || String(i + 1),
            name: stream.name || 'Unknown Stream',
            url: stream.url || null,
            playout_url: stream.playout_url || null,
            category: stream.category || 'General',
            status: 'unknown',
            quality: stream.quality || 'unknown',
            description: stream.description || '',
            thumbnail: stream.thumbnail || 'https://via.placeholder.com/150',
            // Client IDs
            religa_id: stream.religa_id || null,
            ezugi_id: stream.ezugi_id || null,
            vivo_id: stream.vivo_id || null,
            lucky_streak_id: stream.lucky_streak_id || null,
            alg_id: stream.alg_id || null,
            // Additional metadata
            switcher: stream.switcher || 'No',
            partner: stream.partner || null,
            location: stream.location || null,
            country: stream.country || null,
            local_remote: stream.local_remote || null,
            table_id: stream.table_id || null
        }));
        this.activeSheet = name;
        console.log(`Processed ${this.streams.length} streams for sheet: ${name}`);
        return this.streams;
    }

    // Validate configuration data
    validateConfig() {
        if (!this.config) {
            return { valid: false, errors: ['No configuration data loaded'] };
        }

        const errors = [];

        if (!this.config.sheets || typeof this.config.sheets !== 'object') {
            errors.push('Invalid or missing sheets object');
        } else {
            const names = Object.keys(this.config.sheets);
            if (names.length === 0) {
                errors.push('No sheets found');
            }
            names.forEach(name => {
                if (!Array.isArray(this.config.sheets[name])) {
                    errors.push(`Sheet "${name}" is not an array`);
                }
            });
        }

        return { valid: errors.length === 0, errors: errors };
    }

    // Handle configuration errors
    handleConfigError(error) {
        const errorContainer = document.getElementById('config-error');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="error-message">
                    <h3>Configuration Error</h3>
                    <p>Failed to load stream configuration. Please check the JSON file.</p>
                    <pre>${error.message}</pre>
                </div>
            `;
        }
        console.error('Configuration Error:', error);
    }

    // Get all streams (for the active sheet)
    getStreams() {
        return this.streams;
    }

    // Get streams by category
    getStreamsByCategory(category) {
        return this.streams.filter(stream => stream.category === category);
    }

    // Get a specific stream by ID
    getStreamById(id) {
        return this.streams.find(stream => stream.id === id);
    }

    // Update stream status
    updateStreamStatus(id, status) {
        const stream = this.getStreamById(id);
        if (stream) {
            stream.status = status;
            return true;
        }
        return false;
    }

    // Render streams table (legacy - used by original dashboard.html)
    renderStreamsTable() {
        const tbody = document.getElementById('streams-tbody');
        const loadingIndicator = document.getElementById('loading-indicator');

        if (!tbody) {
            console.error('Table body not found');
            return;
        }

        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }

        tbody.innerHTML = '';

        if (this.streams.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6">No streams available</td></tr>';
            return;
        }

        this.streams.forEach(stream => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><img src="${stream.thumbnail}" alt="${stream.name}" class="stream-thumbnail"></td>
                <td><a href="${stream.url || '#'}" target="_blank">${stream.name}</a></td>
                <td>${stream.category}</td>
                <td><span class="status unknown">Unknown</span></td>
                <td>${stream.quality}</td>
                <td>${stream.description}</td>
            `;
            tbody.appendChild(row);
        });
    }
}

// Initialize configuration manager
const configManager = new ConfigManager();

// Load configuration when page loads (only auto-render if the legacy dashboard is present)
document.addEventListener('DOMContentLoaded', async () => {
    await configManager.loadConfig();
    const validation = configManager.validateConfig();

    // Only auto-process/render for the legacy dashboard.html
    if (document.getElementById('streams-table') && !window.__SEARCH_DASHBOARD__) {
        if (validation.valid) {
            configManager.processStreams();
            configManager.renderStreamsTable();
            document.dispatchEvent(new CustomEvent('configLoaded', { detail: configManager.getStreams() }));
        } else {
            console.error('Configuration validation failed:', validation.errors);
            const errorContainer = document.getElementById('config-error');
            if (errorContainer) {
                errorContainer.innerHTML = `
                    <div class="error-message">
                        <h3>Configuration Validation Error</h3>
                        <ul>
                            ${validation.errors.map(error => `<li>${error}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
        }
    }
});
