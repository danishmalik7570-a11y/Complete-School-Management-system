// Main JavaScript for DNL Institute Dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeSidebar();
    initializeAlerts();
    initializeTooltips();
    initializeFormValidation();
    initializeDataTables();
    initializePrintFunctions();
    initializeCurrentDate();
    
    console.log('DNL Institute Dashboard initialized successfully');
});

// Initialize current date display
function initializeCurrentDate() {
    const dateElement = document.getElementById('current-date');
    if (dateElement) {
        const now = new Date();
        const options = {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        dateElement.textContent = now.toLocaleDateString('en-US', options);
    }
}

// Sidebar functionality
function initializeSidebar() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('active');
                }
            }
        });
    }
}

// Auto-dismiss alerts
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (alert.classList.contains('alert-success')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Real-time validation for specific fields
    initializeCNICValidation();
    initializePhoneValidation();
    initializeFeeCalculation();
}

// CNIC format validation
function initializeCNICValidation() {
    const cnicInputs = document.querySelectorAll('input[name*="cnic"]');
    
    cnicInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 5) value = value.substring(0, 5) + '-' + value.substring(5);
            if (value.length >= 13) value = value.substring(0, 13) + '-' + value.substring(13);
            if (value.length > 15) value = value.substring(0, 15);
            e.target.value = value;
        });
    });
}

// Phone number validation
function initializePhoneValidation() {
    const phoneInputs = document.querySelectorAll('input[name*="contact"], input[name*="phone"]');
    
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) value = value.substring(0, 11);
            e.target.value = value;
        });
    });
}

// Fee calculation
function initializeFeeCalculation() {
    const totalFeeInput = document.getElementById('total_fee');
    const monthlyInstallmentDisplay = document.getElementById('monthly_installment');
    
    if (totalFeeInput && monthlyInstallmentDisplay) {
        totalFeeInput.addEventListener('input', function() {
            const totalFee = parseFloat(this.value) || 0;
            const monthlyInstallment = totalFee / 6;
            monthlyInstallmentDisplay.textContent = `Rs. ${monthlyInstallment.toFixed(2)}`;
        });
        
        // Calculate on page load if editing
        if (totalFeeInput.value) {
            totalFeeInput.dispatchEvent(new Event('input'));
        }
    }
}

// Data tables enhancement
function initializeDataTables() {
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
        // Add sorting capability
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            if (header.textContent.trim() !== 'Actions') {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => sortTable(table, index));
            }
        });
    });
}

// Table sorting function
function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAsc = table.dataset.sortOrder !== 'asc';
    
    rows.sort((a, b) => {
        const aText = a.cells[column].textContent.trim();
        const bText = b.cells[column].textContent.trim();
        
        // Check if numeric
        if (!isNaN(aText) && !isNaN(bText)) {
            return isAsc ? aText - bText : bText - aText;
        }
        
        // String comparison
        return isAsc ? aText.localeCompare(bText) : bText.localeCompare(aText);
    });
    
    // Update table
    rows.forEach(row => tbody.appendChild(row));
    table.dataset.sortOrder = isAsc ? 'asc' : 'desc';
    
    // Update sort indicators
    const headers = table.querySelectorAll('th');
    headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
    headers[column].classList.add(isAsc ? 'sort-asc' : 'sort-desc');
}

// Print functions
function initializePrintFunctions() {
    const printButtons = document.querySelectorAll('[data-print]');
    
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.dataset.print;
            
            if (target === 'page') {
                window.print();
            } else if (target === 'admission-slip') {
                printAdmissionSlip();
            } else if (target === 'student-list') {
                printStudentList();
            }
        });
    });
}

// Print admission slip
function printAdmissionSlip() {
    const printContent = document.querySelector('.admission-slip');
    if (printContent) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Admission Slip</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body { font-size: 12px; }
                    .admission-slip { max-width: 600px; margin: 0 auto; padding: 20px; border: 2px solid #007bff; }
                    .institute-header { text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }
                    .confirmation-badge { background: linear-gradient(45deg, #28a745, #20c997); color: white; padding: 10px 20px; border-radius: 25px; font-weight: bold; display: inline-block; margin: 10px 0; }
                </style>
            </head>
            <body>
                ${printContent.innerHTML}
            </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
}

// Print student list
function printStudentList() {
    const table = document.querySelector('table');
    if (table) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Student List - DNL Institute</title>
                <style>
                    body { font-family: Arial, sans-serif; font-size: 12px; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; font-weight: bold; }
                    .header { text-align: center; margin-bottom: 20px; }
                    .actions { display: none; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>DNL Institute of Information Technology</h2>
                    <h3>Student List</h3>
                    <p>Generated on: ${new Date().toLocaleDateString()}</p>
                </div>
                ${table.outerHTML}
            </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-PK', {
        style: 'currency',
        currency: 'PKR'
    }).format(amount);
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-PK');
}

// Search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('[data-search]');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const targetTable = document.querySelector(this.dataset.search);
            
            if (targetTable) {
                const rows = targetTable.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }
        });
    });
}

// Dashboard animations
function initializeDashboardAnimations() {
    const cards = document.querySelectorAll('.card');
    
    // Animate cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// Form auto-save (draft functionality)
function initializeAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(form => {
        const formId = form.dataset.autosave;
        
        // Load saved data
        const savedData = localStorage.getItem(`draft_${formId}`);
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) input.value = data[key];
            });
        }
        
        // Save on input
        form.addEventListener('input', debounce(() => {
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            localStorage.setItem(`draft_${formId}`, JSON.stringify(data));
        }, 1000));
        
        // Clear on submit
        form.addEventListener('submit', () => {
            localStorage.removeItem(`draft_${formId}`);
        });
    });
}

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global use
window.DNLInstitute = {
    formatCurrency,
    formatDate,
    printAdmissionSlip,
    printStudentList,
    sortTable
};
