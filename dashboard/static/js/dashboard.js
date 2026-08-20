/* Dashboard JavaScript for Satta Matka Market Analysis */
class MarketDashboard {
    constructor() {
        this.marketDataContainer = document.getElementById('market-data-container');
        this.updateInterval = null;
        this.markets = [
            'Kalyan', 
            'Main Bazar', 
            'Milan Day', 
            'Milan Night', 
            'Rajdhani Day', 
            'Rajdhani Night'
        ];
        
        // Initialize the dashboard
        this.init();
    }
    
    init() {
        // Load initial market data
        this.fetchMarketData();
        
        // Set up periodic updates (every 30 seconds as specified)
        this.updateInterval = setInterval(() => {
            this.fetchMarketData();
        }, 30000);
        
        // Set up navigation
        this.setupNavigation();
        
        // Set up export button
        this.setupExportButton();
    }
    
    fetchMarketData() {
        // Show loading state
        this.showLoading();
        
        // Fetch data from API
        fetch('/api/market-data')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                this.renderMarketData(data);
            })
            .catch(error => {
                console.error('Error fetching market data:', error);
                this.showError('Failed to load market data. Please try again later.');
            });
    }
    
    showLoading() {
        this.marketDataContainer.innerHTML = '<div class="loading">Loading market data...</div>';
    }
    
    showError(message) {
        this.marketDataContainer.innerHTML = `<div class="error">${message}</div>`;
    }
    
    renderMarketData(data) {
        if (!data || Object.keys(data).length === 0) {
            this.showError('No market data available');
            return;
        }
        
        // Create market grid
        let html = '<div class="market-grid">';
        
        // Process each market
        this.markets.forEach(market => {
            const marketData = data[market] || {};
            
            // Determine market status based on data freshness
            const timestamp = marketData.timestamp || 0;
            const ageInSeconds = Date.now() / 1000 - timestamp;
            let statusText = 'Live';
            let statusClass = 'live';
            
            if (ageInSeconds > 300) { // Older than 5 minutes
                statusText = 'Delayed';
                statusClass = 'delayed';
            }
            if (ageInSeconds > 1800) { // Older than 30 minutes
                statusText = 'Offline';
                statusClass = 'offline';
            }
            
            html += `
                <div class="market-card">
                    <h3>
                        ${market}
                        <span class="market-status ${statusClass}">${statusText}</span>
                    </h3>
                    <div class="market-values">
                        <div class="value-item">
                            <div class="value-label">Open</div>
                            <div class="value-display market-open">${marketData.open || '--'}</div>
                        </div>
                        <div class="value-item">
                            <div class="value-label">Jodi</div>
                            <div class="value-display market-jodi">${marketData.jodi || '--'}</div>
                        </div>
                        <div class="value-item">
                            <div class="value-label">Close</div>
                            <div class="value-display market-close">${marketData.close || '--'}</div>
                        </div>
                        <div class="value-item">
                            <div class="value-label">Final Ank</div>
                            <div class="value-display market-final-ank">${marketData.final_ank || '--'}</div>
                        </div>
                    </div>
                    <div class="timestamp">
                        Last updated: ${new Date(timestamp * 1000).toLocaleTimeString()}
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        
        this.marketDataContainer.innerHTML = html;
    }
    
    setupNavigation() {
        const navLinks = document.querySelectorAll('nav ul li a');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Remove active class from all links
                navLinks.forEach(l => l.classList.remove('active'));
                
                // Add active class to clicked link
                link.classList.add('active');
                
                // Hide all sections
                document.querySelectorAll('main section').forEach(section => {
                    section.style.display = 'none';
                });
                
                // Show selected section
                const sectionId = link.getAttribute('href').substring(1);
                const section = document.getElementById(sectionId);
                if (section) {
                    section.style.display = 'block';
                }
            });
        });
        
        // Show overview section by default
        document.querySelectorAll('main section').forEach(section => {
            section.style.display = 'none';
        });
        document.getElementById('overview').style.display = 'block';
    }
    
    setupExportButton() {
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                // Trigger Excel export functionality
                // This would typically call an export endpoint
                alert('Export functionality would be implemented here');
                // In a real implementation, this would call /api/export/excel or similar
            });
        }
    }
    
    // Cleanup method
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.marketDashboard = new MarketDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.marketDashboard) {
        window.marketDashboard.destroy();
    }
});
