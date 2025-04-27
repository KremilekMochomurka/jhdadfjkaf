/**
 * Navigation functionality for the file conversion system
 * Handles mobile menu toggle and active navigation links
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing navigation functionality');

    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');

    if (mobileMenuToggle && mainNav) {
        mobileMenuToggle.addEventListener('click', () => {
            mainNav.classList.toggle('active');

            // Change icon based on menu state
            const icon = mobileMenuToggle.querySelector('i');
            if (mainNav.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });

        // Close menu when clicking outside
        document.addEventListener('click', (event) => {
            if (!mainNav.contains(event.target) && !mobileMenuToggle.contains(event.target) && mainNav.classList.contains('active')) {
                mainNav.classList.remove('active');
                const icon = mobileMenuToggle.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }

    // Set active navigation link based on current page
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');

        // Check if the link path matches the current path
        if (linkPath === currentPath ||
            (linkPath !== '/' && currentPath.startsWith(linkPath)) ||
            (linkPath === '/' && currentPath === '/')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }

        // Add click event listeners for navigation
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            // Handle navigation within the same page
            if (href === '/' && window.location.pathname === '/') {
                e.preventDefault();
                showHomeView();
            } else if (href === '/documents' || this.id === 'documents-tab') {
                e.preventDefault();
                showDocumentsView();
            } else if (href === '/folders' || this.id === 'folders-tab') {
                e.preventDefault();
                showFoldersView();
            } else if (href === '/settings' || this.id === 'settings-tab') {
                e.preventDefault();
                showSettingsView();
            }

            // Update active state
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Function to show home view (upload section)
    function showHomeView() {
        document.getElementById('upload-section').style.display = 'block';
        document.getElementById('documents-section').style.display = 'block';
        document.getElementById('folder-section').style.display = 'none';
        document.getElementById('editor-section').style.display = 'none';

        // Hide settings view if it exists
        const settingsSection = document.getElementById('settings-section');
        if (settingsSection) {
            settingsSection.style.display = 'none';
        }
    }

    // Function to show documents view
    function showDocumentsView() {
        document.getElementById('upload-section').style.display = 'none';
        document.getElementById('documents-section').style.display = 'block';
        document.getElementById('folder-section').style.display = 'none';
        document.getElementById('editor-section').style.display = 'none';

        // Hide settings view if it exists
        const settingsSection = document.getElementById('settings-section');
        if (settingsSection) {
            settingsSection.style.display = 'none';
        }

        // Refresh document list
        if (window.refreshDocumentList && typeof window.refreshDocumentList === 'function') {
            window.refreshDocumentList();
        }
    }

    // Function to show folders view
    function showFoldersView() {
        document.getElementById('upload-section').style.display = 'none';
        document.getElementById('documents-section').style.display = 'none';
        document.getElementById('folder-section').style.display = 'block';
        document.getElementById('editor-section').style.display = 'none';

        // Hide settings view if it exists
        const settingsSection = document.getElementById('settings-section');
        if (settingsSection) {
            settingsSection.style.display = 'none';
        }

        // If no folder is selected, show the root folder
        if (!window.currentFolderId) {
            // Get the first folder (usually the root folder)
            fetch('/api/folders/')
                .then(response => response.json())
                .then(data => {
                    if (data.folders && data.folders.length > 0) {
                        const firstFolder = data.folders[0];
                        if (window.fetchFolderContents && typeof window.fetchFolderContents === 'function') {
                            window.fetchFolderContents(firstFolder.id);
                        }
                    }
                })
                .catch(error => console.error('Error loading folders:', error));
        }
    }

    // Function to show settings view
    function showSettingsView() {
        document.getElementById('upload-section').style.display = 'none';
        document.getElementById('documents-section').style.display = 'none';
        document.getElementById('folder-section').style.display = 'none';
        document.getElementById('editor-section').style.display = 'none';

        // Create settings section if it doesn't exist
        let settingsSection = document.getElementById('settings-section');
        if (!settingsSection) {
            settingsSection = document.createElement('section');
            settingsSection.id = 'settings-section';
            settingsSection.style.marginTop = '20px';

            // Add settings content
            settingsSection.innerHTML = `
                <h2>Nastavení aplikace</h2>
                <div class="settings-container">
                    <div class="settings-group">
                        <h3>Obecná nastavení</h3>
                        <div class="setting-item">
                            <label for="dark-mode-toggle">Tmavý režim</label>
                            <div class="toggle-switch">
                                <input type="checkbox" id="dark-mode-toggle">
                                <span class="toggle-slider"></span>
                            </div>
                        </div>
                        <div class="setting-item">
                            <label for="auto-refresh">Automatické obnovení (sekundy)</label>
                            <input type="number" id="auto-refresh" min="0" max="300" value="30">
                        </div>
                    </div>

                    <div class="settings-group">
                        <h3>Nastavení složek</h3>
                        <div class="setting-item">
                            <label for="default-folder">Výchozí složka pro nové dokumenty</label>
                            <select id="default-folder">
                                <option value="">Automaticky (podle obsahu)</option>
                                <!-- Folders will be loaded dynamically -->
                            </select>
                        </div>
                    </div>

                    <div class="settings-group">
                        <h3>O aplikaci</h3>
                        <p>Agent Asistent v1.0</p>
                        <p>Aplikace pro správu a konverzi dokumentů</p>
                    </div>
                </div>
            `;

            // Add settings section to main
            document.querySelector('main').appendChild(settingsSection);

            // Load folders for default folder setting
            fetch('/api/folders/')
                .then(response => response.json())
                .then(data => {
                    const defaultFolderSelect = document.getElementById('default-folder');
                    if (defaultFolderSelect && data.folders) {
                        data.folders.forEach(folder => {
                            const option = document.createElement('option');
                            option.value = folder.id;
                            option.textContent = folder.name;
                            defaultFolderSelect.appendChild(option);
                        });
                    }
                })
                .catch(error => console.error('Error loading folders for settings:', error));

            // Add event listener for dark mode toggle
            const darkModeToggle = document.getElementById('dark-mode-toggle');
            if (darkModeToggle) {
                // Check if dark mode is already enabled
                if (localStorage.getItem('darkMode') === 'enabled') {
                    darkModeToggle.checked = true;
                    document.body.classList.add('dark-mode');
                }

                darkModeToggle.addEventListener('change', function() {
                    if (this.checked) {
                        document.body.classList.add('dark-mode');
                        localStorage.setItem('darkMode', 'enabled');
                    } else {
                        document.body.classList.remove('dark-mode');
                        localStorage.setItem('darkMode', 'disabled');
                    }
                });
            }
        }

        settingsSection.style.display = 'block';
    }

    // Make functions available globally
    window.showHomeView = showHomeView;
    window.showDocumentsView = showDocumentsView;
    window.showFoldersView = showFoldersView;
    window.showSettingsView = showSettingsView;
});
