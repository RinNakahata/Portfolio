// Portfolio AWS Infrastructure - JavaScript

// ==============================================================================
// API TESTING FUNCTIONALITY
// ==============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize API testing
    initializeApiTesting();
    
    // Initialize monitoring dashboard
    initializeMonitoring();
    
    // Initialize smooth scrolling for navigation
    initializeSmoothScrolling();
});

// API Testing Implementation
function initializeApiTesting() {
    const testButton = document.getElementById('test-api');
    const endpointSelect = document.getElementById('api-endpoint');
    const resultContainer = document.getElementById('api-result');
    
    if (!testButton || !endpointSelect || !resultContainer) {
        console.warn('API testing elements not found');
        return;
    }
    
    testButton.addEventListener('click', async function() {
        const selectedEndpoint = endpointSelect.value;
        
        // Update UI to show loading state
        testButton.textContent = 'テスト実行中...';
        testButton.disabled = true;
        resultContainer.textContent = 'APIリクエストを送信中...';
        
        try {
            // Since this is a demo, simulate API calls
            const response = await simulateApiCall(selectedEndpoint);
            displayApiResponse(response, resultContainer);
        } catch (error) {
            displayApiError(error, resultContainer);
        } finally {
            // Reset button state
            testButton.textContent = 'APIテスト実行';
            testButton.disabled = false;
        }
    });
}

// Simulate API calls for demo purposes
async function simulateApiCall(endpoint) {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));
    
    const responses = {
        '/health': {
            status: 200,
            data: {
                status: 'healthy',
                timestamp: new Date().toISOString(),
                version: '1.0.0',
                uptime: '2d 4h 30m',
                database: 'connected',
                cache: 'operational'
            }
        },
        '/users': {
            status: 200,
            data: {
                users: [
                    {
                        user_id: 'user_001',
                        username: 'demo_user',
                        email: 'demo@example.com',
                        created_at: '2025-08-20T10:30:00Z',
                        last_login: '2025-08-23T14:22:15Z'
                    },
                    {
                        user_id: 'user_002',
                        username: 'test_user',
                        email: 'test@example.com',
                        created_at: '2025-08-21T09:15:30Z',
                        last_login: '2025-08-23T13:45:22Z'
                    }
                ],
                total_count: 2
            }
        },
        '/metrics': {
            status: 200,
            data: {
                metrics: [
                    {
                        device_id: 'device_001',
                        timestamp: Date.now() - 300000,
                        cpu_usage: 45.2,
                        memory_usage: 62.8,
                        disk_usage: 34.1,
                        status: 'active'
                    },
                    {
                        device_id: 'device_002',
                        timestamp: Date.now() - 600000,
                        cpu_usage: 23.7,
                        memory_usage: 41.3,
                        disk_usage: 28.9,
                        status: 'active'
                    }
                ],
                total_count: 2
            }
        },
        '/metrics/latest': {
            status: 200,
            data: {
                latest_metrics: {
                    device_id: 'device_001',
                    timestamp: Date.now(),
                    cpu_usage: 38.5,
                    memory_usage: 58.2,
                    disk_usage: 35.7,
                    network_in: 1024.5,
                    network_out: 2048.3,
                    status: 'active',
                    region: 'ap-northeast-1'
                }
            }
        }
    };
    
    const response = responses[endpoint];
    if (!response) {
        throw new Error(`Unknown endpoint: ${endpoint}`);
    }
    
    // Simulate occasional errors
    if (Math.random() < 0.1) {
        throw new Error('Simulated network error');
    }
    
    return response;
}

// Display successful API response
function displayApiResponse(response, container) {
    const formattedResponse = {
        status: response.status,
        timestamp: new Date().toISOString(),
        data: response.data
    };
    
    container.textContent = JSON.stringify(formattedResponse, null, 2);
    container.style.color = '#333';
}

// Display API error
function displayApiError(error, container) {
    const errorResponse = {
        error: true,
        message: error.message,
        timestamp: new Date().toISOString(),
        status: 500
    };
    
    container.textContent = JSON.stringify(errorResponse, null, 2);
    container.style.color = '#dc3545';
}

// ==============================================================================
// MONITORING DASHBOARD
// ==============================================================================

function initializeMonitoring() {
    // Start updating metrics every 5 seconds
    updateMetrics();
    setInterval(updateMetrics, 5000);
}

function updateMetrics() {
    updateResponseTime();
    updateRequestCount();
    updateErrorRate();
    updateSystemStatus();
}

function updateResponseTime() {
    const element = document.getElementById('response-time');
    if (element) {
        // Simulate response time between 50-200ms
        const responseTime = Math.floor(Math.random() * 150) + 50;
        element.textContent = responseTime;
    }
}

function updateRequestCount() {
    const element = document.getElementById('request-count');
    if (element) {
        // Simulate request count between 10-100 per minute
        const requestCount = Math.floor(Math.random() * 90) + 10;
        element.textContent = requestCount;
    }
}

function updateErrorRate() {
    const element = document.getElementById('error-rate');
    if (element) {
        // Simulate error rate between 0-5%
        const errorRate = (Math.random() * 5).toFixed(2);
        element.textContent = errorRate;
    }
}

function updateSystemStatus() {
    const element = document.getElementById('system-status');
    if (element) {
        const statuses = ['稼働中', '正常', '健全'];
        const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
        element.textContent = randomStatus;
        
        // Update color based on status
        element.className = 'metric-value status';
        if (randomStatus === '稼働中') {
            element.style.color = '#28a745';
        } else if (randomStatus === '正常') {
            element.style.color = '#17a2b8';
        } else {
            element.style.color = '#007bff';
        }
    }
}

// ==============================================================================
// SMOOTH SCROLLING NAVIGATION
// ==============================================================================

function initializeSmoothScrolling() {
    const navLinks = document.querySelectorAll('.nav-menu a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetSection.offsetTop - headerHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ==============================================================================
// UTILITY FUNCTIONS
// ==============================================================================

// Format timestamp for display
function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString('ja-JP', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Format JSON for display
function formatJsonResponse(data) {
    return JSON.stringify(data, null, 2);
}

// Show notification (for future enhancements)
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    // Future: Implement toast notifications
}

// Error handling wrapper
function handleError(error, context = 'unknown') {
    console.error(`Error in ${context}:`, error);
    showNotification(`エラーが発生しました: ${error.message}`, 'error');
}

// ==============================================================================
// PERFORMANCE MONITORING
// ==============================================================================

// Track page load performance
window.addEventListener('load', function() {
    const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
    console.log(`Page loaded in ${loadTime}ms`);
});

// Track API response times
function trackApiResponseTime(endpoint, startTime) {
    const endTime = performance.now();
    const responseTime = Math.round(endTime - startTime);
    console.log(`${endpoint} response time: ${responseTime}ms`);
    return responseTime;
}