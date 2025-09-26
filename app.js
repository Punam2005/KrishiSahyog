// CropScope AI Dashboard JavaScript
class CropScopeApp {
    constructor() {
        this.currentSection = 'dashboard';
        this.charts = {};
        this.fieldsData = [
            {
                id: 1,
                name: "North Field A",
                location: "40.7128, -74.0060",
                lastScan: "2024-09-12",
                healthScore: 87,
                status: "Healthy",
                area: "25.3 hectares",
                cropType: "Corn",
                alerts: 1
            },
            {
                id: 2,
                name: "South Field B",
                location: "40.7589, -73.9851",
                lastScan: "2024-09-11",
                healthScore: 65,
                status: "Attention Needed",
                area: "18.7 hectares",
                cropType: "Wheat",
                alerts: 3
            },
            {
                id: 3,
                name: "East Field C",
                location: "40.6892, -74.0445",
                lastScan: "2024-09-10",
                healthScore: 92,
                status: "Excellent",
                area: "31.2 hectares",
                cropType: "Soybeans",
                alerts: 0
            }
        ];
        this.healthMetrics = {
            chlorophyllContent: 78,
            waterStress: 23,
            nutrientDeficiency: 15,
            diseaseRisk: 12
        };
        this.pestAlerts = [
            {
                id: 1,
                fieldName: "North Field A",
                pestType: "Aphids",
                severity: "Medium",
                confidence: 0.82,
                detectedDate: "2024-09-12",
                recommendation: "Monitor closely, consider beneficial insects"
            },
            {
                id: 2,
                fieldName: "South Field B",
                pestType: "Corn Borer",
                severity: "High",
                confidence: 0.95,
                detectedDate: "2024-09-11",
                recommendation: "Immediate treatment recommended"
            },
            {
                id: 3,
                fieldName: "South Field B",
                pestType: "Leaf Rust",
                severity: "Medium",
                confidence: 0.73,
                detectedDate: "2024-09-11",
                recommendation: "Apply fungicide treatment"
            }
        ];
        this.soilData = {
            ph: 6.8,
            organicMatter: 4.2,
            moistureContent: 67,
            nitrogen: 85,
            phosphorus: 72,
            potassium: 68
        };
        this.spectralData = {
            wavelengths: [400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900],
            reflectance: [0.05, 0.08, 0.12, 0.45, 0.15, 0.06, 0.85, 0.82, 0.79, 0.76, 0.73],
            bands: ["Blue", "Green", "Red", "Red Edge", "NIR1", "NIR2", "NIR3"]
        };
        this.trendsData = {
            healthScores: [
                {date: "2024-09-01", score: 82},
                {date: "2024-09-03", score: 84},
                {date: "2024-09-05", score: 80},
                {date: "2024-09-07", score: 78},
                {date: "2024-09-09", score: 85},
                {date: "2024-09-11", score: 87},
                {date: "2024-09-13", score: 89}
            ]
        };
        
        this.init();
    }

    init() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupApp();
            });
        } else {
            this.setupApp();
        }
    }

    setupApp() {
        this.setupEventListeners();
        this.initializeCharts();
        this.setupThemeToggle();
        this.setupFileUpload();
        this.setupModal();
        this.simulateRealTimeUpdates();
    }

    setupEventListeners() {
        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.querySelector('.main-content');

        if (sidebarToggle && sidebar && mainContent) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                sidebar.classList.toggle('open');
                mainContent.classList.toggle('expanded');
            });
        }

        // Navigation - Fixed to properly switch sections
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('data-section');
                if (section) {
                    this.navigateToSection(section);
                }
            });
        });

        // Field cards click events
        const fieldCards = document.querySelectorAll('.field-card');
        fieldCards.forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.closest('button')) {
                    const fieldId = card.getAttribute('data-field-id');
                    this.showFieldDetails(fieldId);
                }
            });
        });

        // Upload button - Fixed
        const uploadBtn = document.getElementById('uploadBtn');
        if (uploadBtn) {
            uploadBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const fileInput = document.getElementById('fileInput');
                if (fileInput) {
                    fileInput.click();
                }
            });
        }

        // Alert action buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.alert-actions .btn--primary')) {
                e.preventDefault();
                this.handlePestAlert(e.target.closest('.alert-card'));
            }
        });

        // Add other button event listeners
        this.setupButtonListeners();
    }

    setupButtonListeners() {
        // Handle various button clicks throughout the app
        document.addEventListener('click', (e) => {
            const button = e.target.closest('button');
            if (!button) return;

            const buttonText = button.textContent.trim();
            
            // Handle different button types
            switch (buttonText) {
                case 'View Details':
                    e.preventDefault();
                    const fieldCard = button.closest('.field-card');
                    if (fieldCard) {
                        const fieldId = fieldCard.getAttribute('data-field-id');
                        this.showFieldDetails(fieldId);
                    }
                    break;
                case 'Analyze':
                    e.preventDefault();
                    this.navigateToSection('health');
                    this.showNotification('Starting field analysis...', 'info');
                    break;
                case 'Take Action':
                    e.preventDefault();
                    const alertCard = button.closest('.alert-card');
                    if (alertCard) {
                        this.handlePestAlert(alertCard);
                    }
                    break;
                case 'Export Report':
                    e.preventDefault();
                    this.exportReport();
                    break;
                case 'Start Analysis':
                    e.preventDefault();
                    this.navigateToSection('health');
                    const modal = document.getElementById('fieldModal');
                    if (modal) {
                        modal.classList.add('hidden');
                    }
                    break;
            }
        });
    }

    navigateToSection(section) {
        console.log('Navigating to section:', section);
        
        // Update navigation active state
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => item.classList.remove('active'));
        
        const activeLink = document.querySelector(`[data-section="${section}"]`);
        if (activeLink) {
            activeLink.closest('.nav-item').classList.add('active');
        }

        // Hide all sections
        const sections = document.querySelectorAll('.content-section');
        sections.forEach(sec => {
            sec.classList.remove('active');
            sec.style.display = 'none';
        });
        
        // Show target section
        const targetSection = document.getElementById(section);
        if (targetSection) {
            targetSection.classList.add('active');
            targetSection.style.display = 'block';
        }

        // Update breadcrumb
        const breadcrumb = document.getElementById('breadcrumbText');
        if (breadcrumb) {
            const sectionNames = {
                'dashboard': 'Dashboard / Overview',
                'fields': 'Field Management',
                'health': 'Health Analysis',
                'pests': 'Pest Detection',
                'soil': 'Soil Monitoring',
                'reports': 'Reports & Analytics'
            };
            breadcrumb.textContent = sectionNames[section] || section;
        }

        this.currentSection = section;

        // Initialize section-specific charts with delay to ensure DOM is ready
        setTimeout(() => {
            this.initializeSectionCharts(section);
        }, 100);
    }

    initializeSectionCharts(section) {
        switch (section) {
            case 'health':
                if (!this.charts.spectralChart) {
                    this.initializeSpectralChart();
                }
                break;
            case 'pests':
                if (!this.charts.pestTrendChart) {
                    this.initializePestChart();
                }
                break;
            case 'soil':
                if (!this.charts.nutrientChart) {
                    this.initializeNutrientChart();
                }
                break;
            case 'reports':
                if (!this.charts.fieldComparisonChart) {
                    this.initializeReportCharts();
                }
                break;
        }
    }

    initializeCharts() {
        // Initialize dashboard charts immediately
        setTimeout(() => {
            this.initializeHealthTrendChart();
        }, 100);
    }

    initializeHealthTrendChart() {
        const ctx = document.getElementById('healthTrendChart');
        if (!ctx) return;

        try {
            this.charts.healthTrendChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: this.trendsData.healthScores.map(item => {
                        const date = new Date(item.date);
                        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                    }),
                    datasets: [{
                        label: 'Health Score',
                        data: this.trendsData.healthScores.map(item => item.score),
                        borderColor: '#1FB8CD',
                        backgroundColor: 'rgba(31, 184, 205, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#1FB8CD',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            min: 70,
                            max: 100,
                            grid: {
                                color: 'rgba(0,0,0,0.1)'
                            },
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    }
                }
            });
        } catch (error) {
            console.error('Error initializing health trend chart:', error);
        }
    }

    initializeSpectralChart() {
        const ctx = document.getElementById('spectralChart');
        if (!ctx) return;

        try {
            this.charts.spectralChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: this.spectralData.wavelengths.map(w => w + 'nm'),
                    datasets: [
                        {
                            label: 'Healthy Crop',
                            data: this.spectralData.reflectance,
                            borderColor: '#1FB8CD',
                            backgroundColor: 'rgba(31, 184, 205, 0.1)',
                            borderWidth: 2,
                            fill: false,
                            tension: 0.2
                        },
                        {
                            label: 'Stressed Crop',
                            data: this.spectralData.reflectance.map(r => r * 0.8 + Math.random() * 0.1),
                            borderColor: '#B4413C',
                            backgroundColor: 'rgba(180, 65, 60, 0.1)',
                            borderWidth: 2,
                            fill: false,
                            tension: 0.2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 1,
                            title: {
                                display: true,
                                text: 'Reflectance'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Wavelength (nm)'
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error initializing spectral chart:', error);
        }
    }

    initializePestChart() {
        const ctx = document.getElementById('pestTrendChart');
        if (!ctx) return;

        const pestData = {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [
                {
                    label: 'Aphids',
                    data: [2, 3, 1, 4],
                    backgroundColor: '#FFC185',
                    borderColor: '#FFC185',
                    borderWidth: 1
                },
                {
                    label: 'Corn Borer',
                    data: [0, 1, 2, 3],
                    backgroundColor: '#B4413C',
                    borderColor: '#B4413C',
                    borderWidth: 1
                },
                {
                    label: 'Leaf Rust',
                    data: [1, 0, 1, 2],
                    backgroundColor: '#D2BA4C',
                    borderColor: '#D2BA4C',
                    borderWidth: 1
                }
            ]
        };

        try {
            this.charts.pestTrendChart = new Chart(ctx, {
                type: 'bar',
                data: pestData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Number of Detections'
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error initializing pest chart:', error);
        }
    }

    initializeNutrientChart() {
        const ctx = document.getElementById('nutrientChart');
        if (!ctx) return;

        try {
            this.charts.nutrientChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'Other'],
                    datasets: [{
                        data: [this.soilData.nitrogen, this.soilData.phosphorus, this.soilData.potassium, 20],
                        backgroundColor: ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error initializing nutrient chart:', error);
        }
    }

    initializeReportCharts() {
        // Field Comparison Chart
        const comparisonCtx = document.getElementById('fieldComparisonChart');
        if (comparisonCtx) {
            try {
                this.charts.fieldComparisonChart = new Chart(comparisonCtx, {
                    type: 'radar',
                    data: {
                        labels: ['Health Score', 'Chlorophyll', 'Water Content', 'Nutrient Level', 'Disease Resistance'],
                        datasets: [
                            {
                                label: 'North Field A',
                                data: [87, 78, 85, 80, 90],
                                backgroundColor: 'rgba(31, 184, 205, 0.2)',
                                borderColor: '#1FB8CD',
                                pointBackgroundColor: '#1FB8CD'
                            },
                            {
                                label: 'South Field B',
                                data: [65, 60, 70, 65, 75],
                                backgroundColor: 'rgba(255, 193, 133, 0.2)',
                                borderColor: '#FFC185',
                                pointBackgroundColor: '#FFC185'
                            },
                            {
                                label: 'East Field C',
                                data: [92, 88, 90, 85, 95],
                                backgroundColor: 'rgba(180, 65, 60, 0.2)',
                                borderColor: '#B4413C',
                                pointBackgroundColor: '#B4413C'
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            r: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Error initializing field comparison chart:', error);
            }
        }

        // Yield Prediction Chart
        const yieldCtx = document.getElementById('yieldPredictionChart');
        if (yieldCtx) {
            try {
                this.charts.yieldPredictionChart = new Chart(yieldCtx, {
                    type: 'line',
                    data: {
                        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                        datasets: [
                            {
                                label: 'Predicted Yield',
                                data: [0, 0, 10, 25, 45, 70, 85, 90, 88, 75, 40, 10],
                                borderColor: '#1FB8CD',
                                backgroundColor: 'rgba(31, 184, 205, 0.1)',
                                fill: true,
                                tension: 0.4
                            },
                            {
                                label: 'Last Year Actual',
                                data: [0, 0, 8, 22, 42, 68, 82, 87, 85, 72, 38, 8],
                                borderColor: '#B4413C',
                                backgroundColor: 'rgba(180, 65, 60, 0.1)',
                                fill: false,
                                borderDash: [5, 5]
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Yield (%)'
                                }
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Error initializing yield prediction chart:', error);
            }
        }
    }

    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        if (!themeToggle) return;
        
        const currentTheme = localStorage.getItem('theme') || 'light';
        
        // Set initial theme
        document.documentElement.setAttribute('data-color-scheme', currentTheme);
        this.updateThemeIcon(currentTheme);

        themeToggle.addEventListener('click', (e) => {
            e.preventDefault();
            const newTheme = document.documentElement.getAttribute('data-color-scheme') === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-color-scheme', newTheme);
            localStorage.setItem('theme', newTheme);
            this.updateThemeIcon(newTheme);
            
            // Update charts to match new theme
            this.updateChartsTheme();
            
            this.showNotification(`Switched to ${newTheme} theme`, 'info');
        });
    }

    updateThemeIcon(theme) {
        const themeToggle = document.getElementById('themeToggle');
        if (!themeToggle) return;
        
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    }

    updateChartsTheme() {
        // Update chart colors based on theme
        Object.keys(this.charts).forEach(chartKey => {
            if (this.charts[chartKey]) {
                this.charts[chartKey].update();
            }
        });
    }

    setupFileUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        if (!uploadArea || !fileInput) return;

        // Drag and drop handlers
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            this.handleFileUpload(files);
        });

        uploadArea.addEventListener('click', (e) => {
            e.preventDefault();
            fileInput.click();
        });

        // Handle choose files button specifically
        const chooseFilesBtn = uploadArea.querySelector('.btn');
        if (chooseFilesBtn) {
            chooseFilesBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                fileInput.click();
            });
        }

        fileInput.addEventListener('change', (e) => {
            const files = e.target.files;
            this.handleFileUpload(files);
        });
    }

    handleFileUpload(files) {
        if (files.length === 0) return;
        
        Array.from(files).forEach(file => {
            if (this.isValidHyperspectralFile(file)) {
                this.processHyperspectralImage(file);
            } else {
                this.showNotification('Invalid file type. Please upload TIFF, HDR, or RAW files.', 'error');
            }
        });
    }

    isValidHyperspectralFile(file) {
        const validExtensions = ['.tiff', '.tif', '.hdr', '.raw'];
        const fileName = file.name.toLowerCase();
        return validExtensions.some(ext => fileName.endsWith(ext));
    }

    processHyperspectralImage(file) {
        // Simulate hyperspectral image processing
        this.showNotification(`Processing ${file.name}...`, 'info');
        
        // Simulate processing time
        setTimeout(() => {
            const analysisResult = this.generateHyperspectralAnalysis(file);
            this.displayAnalysisResults(analysisResult);
            this.showNotification(`Analysis complete for ${file.name}`, 'success');
        }, 3000 + Math.random() * 2000);
    }

    generateHyperspectralAnalysis(file) {
        // Simulate AI analysis results
        return {
            fileName: file.name,
            healthScore: Math.floor(Math.random() * 30) + 70, // 70-100
            chlorophyll: Math.floor(Math.random() * 40) + 60, // 60-100
            waterStress: Math.floor(Math.random() * 30) + 10, // 10-40
            nutrientDeficiency: Math.floor(Math.random() * 20) + 5, // 5-25
            diseaseRisk: Math.floor(Math.random() * 15) + 5, // 5-20
            pestDetected: Math.random() > 0.7,
            pestType: ['Aphids', 'Corn Borer', 'Leaf Rust', 'Spider Mites'][Math.floor(Math.random() * 4)],
            confidence: Math.random() * 0.3 + 0.7, // 0.7-1.0
            timestamp: new Date().toISOString()
        };
    }

    displayAnalysisResults(result) {
        // Update UI with new analysis results
        this.updateActivityFeed(result);
        this.updateHealthMetrics(result);
        
        // If on health analysis page, update the display
        if (this.currentSection === 'health') {
            this.updateHealthAnalysisDisplay(result);
        }
    }

    updateActivityFeed(result) {
        const feed = document.querySelector('.activity-feed');
        if (!feed) return;
        
        const newActivity = document.createElement('div');
        newActivity.className = 'activity-item';
        newActivity.innerHTML = `
            <div class="activity-icon ${result.healthScore > 80 ? 'success' : 'warning'}">
                <i class="fas fa-camera"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">New hyperspectral analysis completed</div>
                <div class="activity-desc">${result.fileName} - Health score: ${result.healthScore}%</div>
                <div class="activity-time">Just now</div>
            </div>
        `;
        
        feed.insertBefore(newActivity, feed.firstChild);
        
        // Remove oldest item if more than 5
        if (feed.children.length > 5) {
            feed.removeChild(feed.lastChild);
        }
    }

    updateHealthMetrics(result) {
        this.healthMetrics.chlorophyllContent = result.chlorophyll;
        this.healthMetrics.waterStress = result.waterStress;
        this.healthMetrics.nutrientDeficiency = result.nutrientDeficiency;
        this.healthMetrics.diseaseRisk = result.diseaseRisk;
        
        // Update the health metrics display if visible
        this.refreshHealthMetricsDisplay();
    }

    refreshHealthMetricsDisplay() {
        const metricsContainer = document.querySelector('.health-metrics');
        if (!metricsContainer) return;
        
        const metrics = [
            { key: 'chlorophyllContent', element: metricsContainer.querySelector('.metric-item:nth-child(1)') },
            { key: 'waterStress', element: metricsContainer.querySelector('.metric-item:nth-child(2)') },
            { key: 'nutrientDeficiency', element: metricsContainer.querySelector('.metric-item:nth-child(3)') },
            { key: 'diseaseRisk', element: metricsContainer.querySelector('.metric-item:nth-child(4)') }
        ];

        metrics.forEach(metric => {
            if (metric.element) {
                const valueElement = metric.element.querySelector('.metric-value');
                const fillElement = metric.element.querySelector('.metric-fill');
                if (valueElement && fillElement) {
                    const value = this.healthMetrics[metric.key];
                    
                    valueElement.textContent = value + '%';
                    fillElement.style.width = value + '%';
                    
                    // Update color based on value
                    const isGood = (metric.key === 'chlorophyllContent' && value > 70) ||
                                 (metric.key !== 'chlorophyllContent' && value < 30);
                    
                    valueElement.className = `metric-value ${isGood ? 'good' : 'warning'}`;
                    fillElement.className = `metric-fill ${isGood ? 'good' : 'warning'}`;
                }
            }
        });
    }

    setupModal() {
        const modal = document.getElementById('fieldModal');
        const closeBtn = document.getElementById('closeModal');

        if (closeBtn) {
            closeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (modal) {
                    modal.classList.add('hidden');
                }
            });
        }

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                }
            });
        }

        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
                modal.classList.add('hidden');
            }
        });
    }

    showFieldDetails(fieldId) {
        const field = this.fieldsData.find(f => f.id == fieldId);
        if (!field) return;

        const modal = document.getElementById('fieldModal');
        if (!modal) return;
        
        // Update modal content
        const elements = {
            modalFieldName: field.name,
            modalCropType: field.cropType,
            modalArea: field.area,
            modalLocation: field.location,
            modalHealthScore: field.healthScore + '%',
            modalLastScan: field.lastScan
        };

        Object.keys(elements).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = elements[id];
            }
        });

        modal.classList.remove('hidden');
    }

    handlePestAlert(alertCard) {
        if (!alertCard) return;
        
        const alertTitle = alertCard.querySelector('.alert-content h4');
        const alertTitleText = alertTitle ? alertTitle.textContent : 'pest alert';
        
        // Simulate taking action
        alertCard.style.opacity = '0.6';
        alertCard.style.pointerEvents = 'none';
        
        setTimeout(() => {
            alertCard.style.opacity = '1';
            alertCard.style.pointerEvents = 'auto';
            alertCard.style.borderLeftColor = 'var(--color-success)';
            
            const severitySpan = alertCard.querySelector('.alert-severity span');
            const severityIcon = alertCard.querySelector('.alert-severity i');
            
            if (severitySpan) severitySpan.textContent = 'Action Taken';
            if (severityIcon) {
                severityIcon.className = 'fas fa-check-circle';
                severityIcon.style.color = 'var(--color-success)';
            }
            
            this.showNotification(`Action initiated for ${alertTitleText}`, 'success');
        }, 2000);
    }

    exportReport() {
        this.showNotification('Generating report...', 'info');
        
        setTimeout(() => {
            this.showNotification('Report exported successfully!', 'success');
            
            // Simulate file download
            const link = document.createElement('a');
            link.href = 'data:text/plain;charset=utf-8,CropScope AI Report - Generated on ' + new Date().toLocaleDateString();
            link.download = 'cropscope-report-' + new Date().toISOString().slice(0, 10) + '.txt';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }, 1500);
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(n => n.remove());

        const notification = document.createElement('div');
        notification.className = `notification notification--${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Add notification styles if not exists
        if (!document.querySelector('#notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 80px;
                    right: 20px;
                    background: var(--color-surface);
                    border: 1px solid var(--color-border);
                    border-radius: var(--radius-base);
                    padding: var(--space-12) var(--space-16);
                    box-shadow: var(--shadow-md);
                    z-index: 3000;
                    transform: translateX(400px);
                    transition: transform var(--duration-normal) var(--ease-standard);
                    max-width: 300px;
                }
                .notification--success { border-left: 4px solid var(--color-success); }
                .notification--error { border-left: 4px solid var(--color-error); }
                .notification--info { border-left: 4px solid var(--color-primary); }
                .notification-content {
                    display: flex;
                    align-items: center;
                    gap: var(--space-8);
                    color: var(--color-text);
                    font-size: var(--font-size-sm);
                }
                .notification--success .notification-content i { color: var(--color-success); }
                .notification--error .notification-content i { color: var(--color-error); }
                .notification--info .notification-content i { color: var(--color-primary); }
            `;
            document.head.appendChild(styles);
        }

        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto remove
        setTimeout(() => {
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }

    simulateRealTimeUpdates() {
        // Simulate periodic updates to make the dashboard feel alive
        setInterval(() => {
            // Update weather data occasionally
            if (Math.random() > 0.8) {
                this.updateWeatherData();
            }
            
            // Randomly add new activity
            if (Math.random() > 0.9) {
                this.simulateNewActivity();
            }
        }, 30000); // Every 30 seconds
    }

    updateWeatherData() {
        const temps = ['22°C', '23°C', '24°C', '25°C', '26°C'];
        const conditions = ['Sunny', 'Partly Cloudy', 'Cloudy', 'Light Rain'];
        
        const tempElement = document.querySelector('.weather-temp');
        const descElement = document.querySelector('.weather-desc');
        
        if (tempElement && descElement) {
            tempElement.textContent = temps[Math.floor(Math.random() * temps.length)];
            descElement.textContent = conditions[Math.floor(Math.random() * conditions.length)];
        }
    }

    simulateNewActivity() {
        const activities = [
            { title: 'Automated scan initiated', desc: 'East Field C - Scheduled monitoring', icon: 'camera' },
            { title: 'Irrigation system activated', desc: 'North Field A - Based on water stress analysis', icon: 'tint' },
            { title: 'Nutrient analysis updated', desc: 'South Field B - Soil composition reviewed', icon: 'flask' }
        ];
        
        const activity = activities[Math.floor(Math.random() * activities.length)];
        
        const feed = document.querySelector('.activity-feed');
        if (feed) {
            const newActivity = document.createElement('div');
            newActivity.className = 'activity-item';
            newActivity.innerHTML = `
                <div class="activity-icon success">
                    <i class="fas fa-${activity.icon}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-desc">${activity.desc}</div>
                    <div class="activity-time">Just now</div>
                </div>
            `;
            
            feed.insertBefore(newActivity, feed.firstChild);
            
            // Keep only recent activities
            if (feed.children.length > 5) {
                feed.removeChild(feed.lastChild);
            }
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new CropScopeApp();
    
    // Make app globally accessible for debugging
    window.cropScopeApp = app;
});