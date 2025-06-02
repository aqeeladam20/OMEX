// Mobile Login Redirect Fix
// This fixes the issue where mobile users are redirected to homepage instead of /app after login

$(document).ready(function() {
    // Only apply this fix on login page
    if (window.location.pathname === '/login') {
        // Override the original login success handler
        if (window.login && window.login.login_handlers) {
            const originalHandler = window.login.login_handlers[200];
            
            window.login.login_handlers[200] = function(data) {
                if (data.message == 'Logged In') {
                    login.set_status('Success', 'green');
                    document.body.innerHTML = `{% include "templates/includes/splash_screen.html" %}`;
                    
                    // Force redirect to /app for mobile users
                    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
                    const isEmulator = window.location.hostname === '10.0.2.2';
                    
                    if (isMobile || isEmulator) {
                        window.location.href = '/app';
                    } else {
                        // Use the original redirect logic for desktop
                        window.location.href = frappe.utils.sanitise_redirect(frappe.utils.get_url_arg("redirect-to")) || data.home_page;
                    }
                } else {
                    // Call original handler for other cases
                    originalHandler.call(this, data);
                }
            };
        }
    }
}); 