// OMEX ERP PWA Initialization
(function() {
    'use strict';

    // Skip PWA initialization on login/signup pages
    if (window.location.pathname.includes('/login') || 
        window.location.pathname.includes('/signup') ||
        window.location.hash.includes('forgot')) {
        console.log('Skipping PWA initialization on auth pages');
        return;
    }

    // Check if PWA features are supported
    if (!('serviceWorker' in navigator)) {
        console.log('Service Worker not supported');
        return;
    }

    let deferredPrompt;
    let installButton;

    // Register Service Worker
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/assets/erpnext/sw.js')
            .then((registration) => {
                console.log('OMEX ERP Service Worker registered successfully:', registration.scope);
                
                // Check for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            // New version available
                            showUpdateNotification();
                        }
                    });
                });
            })
            .catch((error) => {
                console.log('Service Worker registration failed:', error);
            });
    });

    // Handle PWA install prompt
    window.addEventListener('beforeinstallprompt', (e) => {
        console.log('PWA install prompt triggered');
        
        // Prevent the mini-infobar from appearing on mobile
        e.preventDefault();
        
        // Save the event so it can be triggered later
        deferredPrompt = e;
        
        // Show install button
        showInstallButton();
    });

    // Handle PWA installation
    window.addEventListener('appinstalled', (e) => {
        console.log('OMEX ERP PWA installed successfully');
        hideInstallButton();
        
        // Show success message
        if (typeof frappe !== 'undefined' && frappe.show_alert) {
            frappe.show_alert({
                message: 'OMEX ERP installed successfully! You can now access it from your home screen.',
                indicator: 'green'
            }, 5);
        }
    });

    // Show install button
    function showInstallButton() {
        // Only show on mobile devices
        if (!isMobileDevice()) {
            return;
        }

        // Create install button if it doesn't exist
        if (!installButton) {
            installButton = document.createElement('button');
            installButton.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                </svg>
                Install App
            `;
            installButton.className = 'btn btn-primary btn-sm pwa-install-btn';
            installButton.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 9999;
                border-radius: 25px;
                padding: 10px 15px;
                background: #061142;
                color: white;
                border: none;
                box-shadow: 0 4px 12px rgba(6, 17, 66, 0.3);
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
            `;
            
            installButton.addEventListener('click', installPWA);
            installButton.addEventListener('mouseenter', () => {
                installButton.style.transform = 'translateY(-2px)';
                installButton.style.boxShadow = '0 6px 16px rgba(6, 17, 66, 0.4)';
            });
            installButton.addEventListener('mouseleave', () => {
                installButton.style.transform = 'translateY(0)';
                installButton.style.boxShadow = '0 4px 12px rgba(6, 17, 66, 0.3)';
            });
            
            document.body.appendChild(installButton);
        }
        
        installButton.style.display = 'flex';
    }

    // Hide install button
    function hideInstallButton() {
        if (installButton) {
            installButton.style.display = 'none';
        }
    }

    // Install PWA
    function installPWA() {
        if (!deferredPrompt) {
            return;
        }

        // Show the install prompt
        deferredPrompt.prompt();

        // Wait for the user to respond to the prompt
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the PWA install prompt');
            } else {
                console.log('User dismissed the PWA install prompt');
            }
            deferredPrompt = null;
            hideInstallButton();
        });
    }

    // Check if device is mobile
    function isMobileDevice() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
               (window.innerWidth <= 768);
    }

    // Show update notification
    function showUpdateNotification() {
        if (typeof frappe !== 'undefined' && frappe.show_alert) {
            frappe.show_alert({
                message: 'A new version of OMEX ERP is available. Please refresh the page to update.',
                indicator: 'blue'
            }, 10);
        }
    }

    // Handle PWA display mode
    function handleDisplayMode() {
        if (window.matchMedia('(display-mode: standalone)').matches) {
            console.log('Running in PWA mode');
            document.body.classList.add('pwa-mode');
            
            // Add PWA status bar for iOS
            if (isIOS()) {
                const statusBar = document.createElement('div');
                statusBar.className = 'pwa-status-bar';
                document.body.insertBefore(statusBar, document.body.firstChild);
            }
        }
    }

    // Check if iOS
    function isIOS() {
        return /iPad|iPhone|iPod/.test(navigator.userAgent);
    }

    // Initialize PWA features when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        handleDisplayMode();
        
        // Add mobile-specific classes
        if (isMobileDevice()) {
            document.body.classList.add('mobile-device');
        }
        
        // Handle orientation changes
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                // Trigger resize event to adjust layout
                window.dispatchEvent(new Event('resize'));
            }, 100);
        });
    });

    // Handle PWA shortcuts
    if ('navigator' in window && 'serviceWorker' in navigator) {
        navigator.serviceWorker.addEventListener('message', (event) => {
            if (event.data && event.data.type === 'SHORTCUT_CLICKED') {
                console.log('PWA shortcut clicked:', event.data.shortcut);
                // Handle shortcut navigation
                switch (event.data.shortcut) {
                    case 'scan':
                        window.location.href = '/app/item?scan=true';
                        break;
                    case 'ai':
                        window.location.href = '/app?ai=true';
                        break;
                    case 'sales':
                        window.location.href = '/app/selling';
                        break;
                    case 'inventory':
                        window.location.href = '/app/stock';
                        break;
                }
            }
        });
    }

    // Export PWA utilities
    window.OMEX_PWA = {
        install: installPWA,
        isInstalled: () => window.matchMedia('(display-mode: standalone)').matches,
        isMobile: isMobileDevice,
        isIOS: isIOS
    };

    console.log('OMEX ERP PWA initialized');
})(); 