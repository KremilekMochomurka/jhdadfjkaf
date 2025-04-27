// Jednoduchý JavaScript pro nahrávání souborů
// Global variables and functions
let uploadForm, fileInput, uploadStatus, documentList;

// Make fetchDocumentList globally accessible
window.fetchDocumentList = async function() {
    console.log('Global fetchDocumentList called');
    if (typeof fetchDocumentList === 'function') {
        return fetchDocumentList();
    }
};

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM content loaded');

    // Základní elementy pro nahrávání souborů
    uploadForm = document.getElementById('upload-form');
    fileInput = document.getElementById('file-input');
    uploadStatus = document.getElementById('upload-status');
    documentList = document.getElementById('document-list');

    console.log('Upload form:', uploadForm);
    console.log('File input:', fileInput);
    console.log('Upload status:', uploadStatus);

    // Nastavení změny souboru
    if (fileInput) {
        console.log('Adding change event listener to file input');
        fileInput.addEventListener('change', () => {
            console.log('File input changed');
            if (fileInput.files.length > 0) {
                console.log(`Selected ${fileInput.files.length} files`);

                // Zobrazit názvy vybraných souborů
                const selectedFilesContainer = document.getElementById('selected-files-container');
                if (selectedFilesContainer) {
                    selectedFilesContainer.innerHTML = '';

                    let fileList = document.createElement('ul');
                    fileList.className = 'selected-files-list';

                    for (let i = 0; i < fileInput.files.length; i++) {
                        let fileItem = document.createElement('li');
                        fileItem.className = 'selected-file-item';

                        // Ikona podle typu souboru
                        let fileIcon = document.createElement('i');
                        const fileExt = fileInput.files[i].name.split('.').pop().toLowerCase();

                        if (['pdf'].includes(fileExt)) {
                            fileIcon.className = 'fas fa-file-pdf';
                        } else if (['doc', 'docx', 'odt'].includes(fileExt)) {
                            fileIcon.className = 'fas fa-file-word';
                        } else if (['xls', 'xlsx', 'csv'].includes(fileExt)) {
                            fileIcon.className = 'fas fa-file-excel';
                        } else if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(fileExt)) {
                            fileIcon.className = 'fas fa-file-image';
                        } else if (['html', 'htm'].includes(fileExt)) {
                            fileIcon.className = 'fas fa-file-code';
                        } else if (['json'].includes(fileExt)) {
                            fileIcon.className = 'fas fa-file-code';
                        } else {
                            fileIcon.className = 'fas fa-file-alt';
                        }

                        // Název souboru
                        let fileName = document.createElement('span');
                        fileName.textContent = fileInput.files[i].name;

                        fileItem.appendChild(fileIcon);
                        fileItem.appendChild(fileName);
                        fileList.appendChild(fileItem);
                    }

                    selectedFilesContainer.appendChild(fileList);
                }

                if (uploadStatus) {
                    uploadStatus.innerHTML = `Vybrané soubory: ${fileInput.files.length}`;
                    uploadStatus.style.display = 'block';
                }
            }
        });
    }

    // Nastavení formuláře pro nahrávání
    if (uploadForm) {
        console.log('Upload form found, adding event listener');

        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Upload form submitted');

            // Kontrola vybraných souborů
            if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
                alert('Chyba: Vyberte soubory k nahrání.');
                return;
            }

            const files = fileInput.files;
            console.log(`Selected ${files.length} files for upload`);

            // Zobrazit status nahrávání
            if (uploadStatus) {
                uploadStatus.textContent = `Nahrávám ${files.length} souborů...`;
                uploadStatus.style.display = 'block';
            }

            // Vytvoření FormData s vybranými soubory
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('files[]', files[i]);
            }

            try {
                console.log('Sending upload request to /api/upload');

                // Nahrání souborů
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData,
                });

                console.log('Upload response status:', response.status);

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                console.log('Upload response data:', result);

                // Zobrazit úspěšný status
                if (uploadStatus) {
                    uploadStatus.textContent = `${files.length} souborů nahráno úspěšně.`;
                }

                // Aktualizovat seznam dokumentů
                await fetchDocumentList();

                // Resetovat formulář a vyčistit vybrané soubory
                const selectedFilesContainer = document.getElementById('selected-files-container');
                if (selectedFilesContainer) {
                    selectedFilesContainer.innerHTML = '';
                }
            } catch (error) {
                console.error('Upload error:', error);
                if (uploadStatus) {
                    uploadStatus.textContent = `Chyba při nahrávání: ${error.message}`;
                } else {
                    alert(`Chyba při nahrávání: ${error.message}`);
                }
            } finally {
                uploadForm.reset(); // Vyčistit formulář
            }
        });
    } else {
        console.error('Upload form element not found');
    }

    // Funkce pro načtení seznamu dokumentů
    async function fetchDocumentList() {
        console.log('Fetching document list');
        try {
            const response = await fetch('/api/documents');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Documents fetched:', result);

            // Get the documents array from the response
            const documents = result.documents || [];

            // Zobrazit seznam dokumentů
            const documentList = document.getElementById('document-list');
            if (documentList) {
                documentList.innerHTML = '';

                if (documents.length === 0) {
                    documentList.innerHTML = '<li class="no-documents"><i class="fas fa-file-alt fa-3x" style="opacity: 0.3; margin-bottom: 1rem;"></i><div>Žádné dokumenty k zobrazení</div><div style="font-size: 0.9rem; margin-top: 0.5rem;">Nahrajte nové dokumenty pomocí formuláře výše</div></li>';
                } else {
                    documents.forEach(doc => {
                        const li = document.createElement('li');
                        li.className = 'document-item';
                        li.setAttribute('data-id', doc.id);
                        li.setAttribute('draggable', 'true');

                        // Add status indicator
                        const docStatus = document.createElement('div');
                        docStatus.className = `doc-status ${doc.status ? 'status-' + doc.status.toLowerCase() : ''}`;
                        li.appendChild(docStatus);

                        // Create document content
                        const docInfo = document.createElement('div');
                        docInfo.className = 'doc-info';

                        const docTitle = document.createElement('div');
                        docTitle.className = 'doc-title';
                        docTitle.textContent = doc.original_filename;

                        const docMeta = document.createElement('div');
                        docMeta.className = 'doc-meta';

                        // Add upload time
                        const uploadTimeItem = document.createElement('div');
                        uploadTimeItem.className = 'doc-meta-item';

                        const timeIcon = document.createElement('i');
                        timeIcon.className = 'fas fa-clock';
                        uploadTimeItem.appendChild(timeIcon);

                        const timeText = document.createElement('span');
                        timeText.textContent = new Date(doc.upload_time).toLocaleString();
                        uploadTimeItem.appendChild(timeText);

                        docMeta.appendChild(uploadTimeItem);

                        // Add file type if available
                        if (doc.content_type) {
                            const typeItem = document.createElement('div');
                            typeItem.className = 'doc-meta-item';

                            const typeIcon = document.createElement('i');
                            typeIcon.className = getFileTypeIcon(doc.content_type);
                            typeItem.appendChild(typeIcon);

                            const typeText = document.createElement('span');
                            typeText.textContent = doc.content_type;
                            typeItem.appendChild(typeText);

                            docMeta.appendChild(typeItem);
                        }

                        // Add status if available
                        if (doc.status) {
                            const statusItem = document.createElement('div');
                            statusItem.className = 'doc-meta-item';

                            const statusIcon = document.createElement('i');
                            statusIcon.className = getStatusIcon(doc.status);
                            statusItem.appendChild(statusIcon);

                            const statusText = document.createElement('span');
                            statusText.textContent = getStatusText(doc.status);
                            statusItem.appendChild(statusText);

                            docMeta.appendChild(statusItem);
                        }

                        docInfo.appendChild(docTitle);
                        docInfo.appendChild(docMeta);

                        // Create document actions
                        const docActions = document.createElement('div');
                        docActions.className = 'doc-actions';

                        const viewBtn = document.createElement('button');
                        viewBtn.className = 'btn-sm';
                        viewBtn.innerHTML = '<i class="fas fa-eye"></i> Zobrazit';
                        viewBtn.addEventListener('click', () => viewDocument(doc.id));

                        const deleteBtn = document.createElement('button');
                        deleteBtn.className = 'btn-sm delete-btn';
                        deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i> Smazat';
                        deleteBtn.addEventListener('click', () => deleteDocument(doc.id));

                        docActions.appendChild(viewBtn);
                        docActions.appendChild(deleteBtn);

                        li.appendChild(docInfo);
                        li.appendChild(docActions);

                        // Add drag and drop event listeners
                        li.addEventListener('dragstart', handleDragStart);
                        li.addEventListener('dragend', handleDragEnd);

                        documentList.appendChild(li);
                    });

                    // Update draggable items after creating the list
                    if (window.dragAndDrop && typeof window.dragAndDrop.updateDraggableItems === 'function') {
                        window.dragAndDrop.updateDraggableItems();
                    }
                }
            }
        } catch (error) {
            console.error('Error fetching document list:', error);
            if (documentList) {
                documentList.innerHTML = '<li>Chyba při načítání seznamu dokumentů</li>';
            }
        }
    }

    // Helper function to get human-readable status text
    function getStatusText(status) {
        const statusMap = {
            'pending': 'Čeká',
            'processing': 'Zpracovává se',
            'completed': 'Dokončeno',
            'error': 'Chyba',
            'warning': 'Varování',
            'splitting': 'Rozdělování',
            'split': 'Rozděleno',
            'incomplete': 'Neúplné'
        };

        return statusMap[status.toLowerCase()] || status;
    }

    // Helper function to get status icon
    function getStatusIcon(status) {
        const iconMap = {
            'pending': 'fas fa-clock',
            'processing': 'fas fa-spinner fa-spin',
            'completed': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'splitting': 'fas fa-cut',
            'split': 'fas fa-layer-group',
            'incomplete': 'fas fa-hourglass-half'
        };

        return iconMap[status.toLowerCase()] || 'fas fa-question-circle';
    }

    // Helper function to get file type icon
    function getFileTypeIcon(contentType) {
        const iconMap = {
            'text': 'fas fa-file-alt',
            'pdf': 'fas fa-file-pdf',
            'word': 'fas fa-file-word',
            'excel': 'fas fa-file-excel',
            'csv': 'fas fa-file-csv',
            'image': 'fas fa-file-image',
            'email': 'fas fa-envelope',
            'know_how': 'fas fa-lightbulb',
            'general': 'fas fa-file',
            'html': 'fas fa-file-code',
            'json': 'fas fa-file-code',
            'table': 'fas fa-table'
        };

        return iconMap[contentType.toLowerCase()] || 'fas fa-file';
    }

    // Funkce pro úpravu dokumentu byla odstraněna, protože ji již nepoužíváme

    // Function to view a document
    async function viewDocument(docId) {
        console.log(`Viewing document ${docId}`);

        try {
            // Fetch document details
            const response = await fetch(`/api/documents/${docId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const docData = await response.json();
            console.log('Document details:', docData);

            // Get editor section elements
            const editorSection = document.getElementById('editor-section');
            const editorDocTitle = document.getElementById('editor-doc-title');
            const documentContent = document.getElementById('document-content');
            const editorStatus = document.getElementById('editor-status');

            if (!editorSection || !editorDocTitle || !documentContent) {
                throw new Error('Editor elements not found');
            }

            // Set document title
            editorDocTitle.textContent = docData.original_filename;

            // Set document content
            if (docData.processed_content) {
                // Check if content is JSON and format it
                try {
                    const contentObj = JSON.parse(docData.processed_content);
                    documentContent.innerHTML = formatContent(contentObj, docData.content_type);
                } catch (e) {
                    // Not JSON, display as is
                    documentContent.innerHTML = docData.processed_content;
                }
            } else {
                documentContent.innerHTML = '<p>Žádný obsah k zobrazení</p>';
            }

            // Show editor section
            editorSection.style.display = 'block';

            // Scroll to editor section
            editorSection.scrollIntoView({ behavior: 'smooth' });

            // Set up back to list button
            const backToListBtn = document.getElementById('back-to-list-btn');
            if (backToListBtn) {
                backToListBtn.onclick = function() {
                    // Hide editor section
                    editorSection.style.display = 'none';

                    // Show appropriate section based on context
                    if (window.currentFolderId) {
                        // We're in a folder view
                        const folderSection = document.getElementById('folder-section');
                        if (folderSection) {
                            folderSection.style.display = 'block';
                        }
                    } else {
                        // We're in the main document list
                        const documentsSection = document.getElementById('documents-section');
                        if (documentsSection) {
                            documentsSection.style.display = 'block';
                        }
                    }
                };
            }

        } catch (error) {
            console.error('Error viewing document:', error);
            if (window.dragAndDrop && typeof window.dragAndDrop.showNotification === 'function') {
                window.dragAndDrop.showNotification(`Chyba při zobrazení dokumentu: ${error.message}`, 'error');
            } else {
                alert(`Chyba při zobrazení dokumentu: ${error.message}`);
            }
        }
    }

    // Helper function to format content based on type
    function formatContent(content, contentType) {
        if (!content) return '<p>Žádný obsah k zobrazení</p>';

        if (contentType === 'email' && Array.isArray(content)) {
            // Format email correspondence
            return formatEmailContent(content);
        } else if (contentType === 'table' && Array.isArray(content)) {
            // Format table data
            return formatTableContent(content);
        } else if (typeof content === 'object') {
            // Format JSON with syntax highlighting
            return `<pre>${JSON.stringify(content, null, 2)}</pre>`;
        }

        // Default formatting
        return content.toString();
    }

    // Format email content
    function formatEmailContent(emails) {
        if (!emails || emails.length === 0) {
            return '<p>Žádné emaily k zobrazení</p>';
        }

        let html = '<div class="email-correspondence">';

        // Add email thread
        html += '<div class="email-thread">';

        emails.forEach((email, index) => {
            const isLatest = index === 0;
            html += `<div class="email-message ${isLatest ? 'latest-email' : ''}">`;

            // Email header
            html += '<div class="email-message-header">';
            html += `<div class="email-sender">${email.sender || 'Neznámý odesílatel'}`;
            if (email.sender_email) {
                html += `<span class="sender-email">&lt;${email.sender_email}&gt;</span>`;
            }
            html += '</div>';

            // Email date
            if (email.date) {
                html += `<div class="email-date">${new Date(email.date).toLocaleString()}</div>`;
            }
            html += '</div>';

            // Email metadata
            html += '<div class="email-message-meta">';
            if (email.recipients) {
                html += `<div class="email-recipients"><strong>Komu:</strong> ${email.recipients}</div>`;
            }
            if (email.subject) {
                html += `<div class="email-subject"><strong>Předmět:</strong> ${email.subject}</div>`;
            }
            html += '</div>';

            // Email content
            html += `<div class="email-message-content">${email.content || ''}</div>`;

            html += '</div>';
        });

        html += '</div></div>';
        return html;
    }

    // Format table content
    function formatTableContent(tableData) {
        if (!tableData || tableData.length === 0) {
            return '<p>Žádná tabulková data k zobrazení</p>';
        }

        let html = '<div class="table-content"><table class="markdown-table">';

        // Add header row if first row has headers
        if (tableData[0] && Array.isArray(tableData[0])) {
            html += '<thead><tr>';
            tableData[0].forEach(cell => {
                html += `<th>${cell}</th>`;
            });
            html += '</tr></thead>';
        }

        // Add data rows
        html += '<tbody>';
        for (let i = 1; i < tableData.length; i++) {
            if (Array.isArray(tableData[i])) {
                html += '<tr>';
                tableData[i].forEach(cell => {
                    html += `<td>${cell}</td>`;
                });
                html += '</tr>';
            }
        }
        html += '</tbody></table></div>';

        return html;
    }

    // Funkce pro ukládání obsahu dokumentu byla odstraněna, protože ji již nepoužíváme

    // Function to delete a document
    async function deleteDocument(docId) {
        if (!confirm('Opravdu chcete smazat tento dokument?')) {
            return;
        }

        console.log(`Deleting document ${docId}`);

        try {
            const response = await fetch(`/api/documents/${docId}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Show success notification
            if (window.dragAndDrop && typeof window.dragAndDrop.showNotification === 'function') {
                window.dragAndDrop.showNotification('Dokument byl úspěšně smazán', 'success');
            } else {
                alert('Dokument byl úspěšně smazán');
            }

            // Refresh the document list
            fetchDocumentList();

            // Also refresh folder structure to update counts
            fetchFolderStructure();

            // If we're in a folder view, refresh that too
            if (window.currentFolderId) {
                fetchFolderContents(window.currentFolderId);
            }
        } catch (error) {
            console.error('Error deleting document:', error);

            // Show error notification
            if (window.dragAndDrop && typeof window.dragAndDrop.showNotification === 'function') {
                window.dragAndDrop.showNotification(`Chyba při mazání dokumentu: ${error.message}`, 'error');
            } else {
                alert(`Chyba při mazání dokumentu: ${error.message}`);
            }
        }
    }

    // Drag and drop event handlers
    function handleDragStart(e) {
        console.log('Drag started from main.js');
        this.classList.add('dragging');
        e.dataTransfer.setData('text/plain', this.dataset.id || '');
        e.dataTransfer.effectAllowed = 'move';
    }

    function handleDragEnd() {
        console.log('Drag ended from main.js');
        this.classList.remove('dragging');
    }

    // Načíst seznam dokumentů při načtení stránky
    fetchDocumentList();

    // Načíst strukturu složek
    fetchFolderStructure();

    // Set up auto-refresh for documents and folders (only if not already set up)
    if (!window.refreshIntervals) {
        setupAutoRefresh();
    }

    // Přidání event listenerů pro tlačítka v navigaci
    const documentsTab = document.getElementById('documents-tab');
    const foldersTab = document.getElementById('folders-tab');
    const settingsTab = document.getElementById('settings-tab');

    if (documentsTab) {
        documentsTab.addEventListener('click', function(e) {
            e.preventDefault();
            if (window.showDocumentsView) {
                window.showDocumentsView();
            }
        });
    }

    if (foldersTab) {
        foldersTab.addEventListener('click', function(e) {
            e.preventDefault();
            if (window.showFoldersView) {
                window.showFoldersView();
            }
        });
    }

    if (settingsTab) {
        settingsTab.addEventListener('click', function(e) {
            e.preventDefault();
            if (window.showSettingsView) {
                window.showSettingsView();
            }
        });
    }

    // Funkce pro načtení struktury složek
    async function fetchFolderStructure() {
        const folderTree = document.getElementById('folder-tree');
        if (!folderTree) {
            console.log('Folder tree element not found');
            return;
        }

        console.log('Fetching folder structure');

        try {
            // Remove trailing slash to avoid 404 errors
            const response = await fetch('/api/folders');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const folders = await response.json();
            console.log('Folders fetched:', folders);

            // Clear the folder tree
            folderTree.innerHTML = '';

            // If no folders, show a message
            if (folders.length === 0) {
                folderTree.innerHTML = '<div class="empty-message">Žádné složky</div>';
                return;
            }

            // Build the folder tree
            const rootFolders = folders.filter(folder => !folder.parent_id);

            // Create folder items for root folders
            rootFolders.forEach(folder => {
                const folderItem = createFolderItem(folder, folders);
                folderTree.appendChild(folderItem);
            });

            // Make folders droppable
            const folderItems = document.querySelectorAll('.folder-item');
            folderItems.forEach(item => {
                item.addEventListener('dragover', handleFolderDragOver);
                item.addEventListener('dragenter', handleFolderDragEnter);
                item.addEventListener('dragleave', handleFolderDragLeave);
                item.addEventListener('drop', handleFolderDrop);
            });
        } catch (error) {
            console.error('Error fetching folder structure:', error);
            folderTree.innerHTML = '<div class="empty-message">Chyba při načítání složek</div>';
        }
    }

    // Helper function to create a folder item
    function createFolderItem(folder, allFolders) {
        const folderItem = document.createElement('div');
        folderItem.className = `folder-item folder-type-${folder.folder_type || 'general'}`;
        folderItem.setAttribute('data-id', folder.id);

        const folderContent = document.createElement('div');
        folderContent.className = 'folder-item-content';

        const folderIcon = document.createElement('i');
        folderIcon.className = 'folder-icon fas fa-folder';

        const folderName = document.createElement('div');
        folderName.className = 'folder-name';
        folderName.textContent = folder.name;

        const folderCount = document.createElement('div');
        folderCount.className = 'folder-count';
        folderCount.textContent = folder.document_count || '0';

        folderContent.appendChild(folderIcon);
        folderContent.appendChild(folderName);
        folderContent.appendChild(folderCount);

        folderItem.appendChild(folderContent);

        // Add click event to open folder
        folderContent.addEventListener('click', () => openFolder(folder.id));

        // Add edit button for folder
        const folderEditBtn = document.createElement('button');
        folderEditBtn.className = 'folder-edit-btn';
        folderEditBtn.innerHTML = '<i class="fas fa-edit"></i>';
        folderEditBtn.title = 'Upravit složku';
        folderEditBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent opening the folder
            editFolder(folder);
        });

        folderContent.appendChild(folderEditBtn);

        // Check if this folder has children
        const children = allFolders.filter(f => f.parent_id === folder.id);

        if (children.length > 0) {
            const subfolders = document.createElement('div');
            subfolders.className = 'subfolders';

            children.forEach(child => {
                const childItem = createFolderItem(child, allFolders);
                subfolders.appendChild(childItem);
            });

            folderItem.appendChild(subfolders);
        }

        return folderItem;
    }

    // Function to open a folder
    function openFolder(folderId) {
        console.log(`Opening folder ${folderId}`);
        // Implement folder opening logic here
        // For example, fetch folder contents and show them
        fetchFolderContents(folderId);
    }

    // Function to fetch folder contents
    async function fetchFolderContents(folderId) {
        console.log(`Fetching contents of folder ${folderId}`);

        try {
            const response = await fetch(`/api/folders/${folderId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const folder = await response.json();
            console.log('Folder contents:', folder);

            // Show folder section and hide documents section
            const documentsSection = document.getElementById('documents-section');
            const folderSection = document.getElementById('folder-section');

            if (documentsSection && folderSection) {
                documentsSection.style.display = 'none';
                folderSection.style.display = 'block';

                // Set folder name and description
                const folderName = document.getElementById('folder-name');
                const folderDescription = document.getElementById('folder-description');

                if (folderName) {
                    folderName.textContent = folder.name;
                }

                if (folderDescription) {
                    folderDescription.textContent = folder.description || '';
                }

                // Store current folder ID for later use
                window.currentFolderId = folderId;

                // Render subfolders
                renderSubfolders(folder.subfolders || []);

                // Render documents in this folder
                renderFolderDocuments(folder.documents || []);
            }
        } catch (error) {
            console.error(`Error fetching folder contents: ${error}`);
            if (window.dragAndDrop && typeof window.dragAndDrop.showNotification === 'function') {
                window.dragAndDrop.showNotification(`Chyba při načítání obsahu složky: ${error.message}`, 'error');
            } else {
                alert(`Chyba při načítání obsahu složky: ${error.message}`);
            }
        }
    }

    // Function to render subfolders
    function renderSubfolders(subfolders) {
        const subfolderList = document.getElementById('subfolder-list');

        if (!subfolderList) {
            console.error('Subfolder list element not found');
            return;
        }

        subfolderList.innerHTML = '';

        if (subfolders.length === 0) {
            subfolderList.innerHTML = '<div class="empty-message">Žádné podsložky</div>';
            return;
        }

        subfolders.forEach(subfolder => {
            const subfolderItem = document.createElement('div');
            subfolderItem.className = `subfolder-item folder-type-${subfolder.folder_type || 'general'}`;
            subfolderItem.setAttribute('data-id', subfolder.id);

            const subfolderIcon = document.createElement('i');
            subfolderIcon.className = 'subfolder-icon fas fa-folder';

            const subfolderName = document.createElement('div');
            subfolderName.className = 'subfolder-name';
            subfolderName.textContent = subfolder.name;

            const subfolderCount = document.createElement('div');
            subfolderCount.className = 'subfolder-count';
            subfolderCount.textContent = `${subfolder.document_count || '0'} dokumentů`;

            subfolderItem.appendChild(subfolderIcon);
            subfolderItem.appendChild(subfolderName);
            subfolderItem.appendChild(subfolderCount);

            // Add click event to open subfolder
            subfolderItem.addEventListener('click', () => openFolder(subfolder.id));

            // Make subfolder droppable
            subfolderItem.addEventListener('dragover', handleFolderDragOver);
            subfolderItem.addEventListener('dragenter', handleFolderDragEnter);
            subfolderItem.addEventListener('dragleave', handleFolderDragLeave);
            subfolderItem.addEventListener('drop', handleFolderDrop);

            subfolderList.appendChild(subfolderItem);
        });
    }

    // Function to render documents in a folder
    function renderFolderDocuments(documents) {
        const folderDocumentList = document.getElementById('folder-document-list');

        if (!folderDocumentList) {
            console.error('Folder document list element not found');
            return;
        }

        folderDocumentList.innerHTML = '';

        if (documents.length === 0) {
            folderDocumentList.innerHTML = '<li class="empty-message">Žádné dokumenty</li>';
            return;
        }

        documents.forEach(doc => {
            const li = document.createElement('li');
            li.className = 'document-item';
            li.setAttribute('data-id', doc.id);
            li.setAttribute('draggable', 'true');

            // Create document content
            const docInfo = document.createElement('div');
            docInfo.className = 'doc-info';

            const docName = document.createElement('div');
            docName.className = 'doc-name';
            docName.textContent = doc.original_filename;

            const uploadTime = document.createElement('div');
            uploadTime.className = 'upload-time';
            uploadTime.textContent = new Date(doc.upload_time).toLocaleString();

            docInfo.appendChild(docName);
            docInfo.appendChild(uploadTime);

            // Create document actions
            const docActions = document.createElement('div');
            docActions.className = 'doc-actions';

            const viewBtn = document.createElement('button');
            viewBtn.className = 'btn-sm';
            viewBtn.innerHTML = '<i class="fas fa-eye"></i> Zobrazit';
            viewBtn.addEventListener('click', () => viewDocument(doc.id));

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn-sm delete-btn';
            deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i> Smazat';
            deleteBtn.addEventListener('click', () => deleteDocument(doc.id));

            docActions.appendChild(viewBtn);
            docActions.appendChild(deleteBtn);

            // Add status indicator if available
            if (doc.status) {
                const statusSpan = document.createElement('span');
                statusSpan.className = `status-${doc.status.toLowerCase()}`;
                statusSpan.textContent = getStatusText(doc.status);
                docActions.appendChild(statusSpan);
            }

            // Add document type indicator if available
            if (doc.content_type) {
                const typeIndicator = document.createElement('div');
                typeIndicator.className = `document-type-indicator document-type-${doc.content_type.toLowerCase()}`;
                typeIndicator.textContent = doc.content_type.charAt(0).toUpperCase();
                li.appendChild(typeIndicator);
            }

            li.appendChild(docInfo);
            li.appendChild(docActions);

            // Add drag and drop event listeners
            li.addEventListener('dragstart', handleDragStart);
            li.addEventListener('dragend', handleDragEnd);

            folderDocumentList.appendChild(li);
        });

        // Update draggable items after creating the list
        if (window.dragAndDrop && typeof window.dragAndDrop.updateDraggableItems === 'function') {
            window.dragAndDrop.updateDraggableItems();
        }
    }

    // Folder drag and drop event handlers
    function handleFolderDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    }

    function handleFolderDragEnter(e) {
        e.preventDefault();
        this.classList.add('drop-target');
    }

    function handleFolderDragLeave() {
        this.classList.remove('drop-target');
    }

    async function handleFolderDrop(e) {
        e.preventDefault();
        this.classList.remove('drop-target');

        const documentId = e.dataTransfer.getData('text/plain');
        const folderId = this.dataset.id;

        if (!documentId) {
            console.error('No document ID found in drag data');
            return;
        }

        if (!folderId) {
            console.error('No folder ID found in drop target');
            return;
        }

        console.log(`Moving document ${documentId} to folder ${folderId}`);

        try {
            const response = await fetch(`/api/documents/${documentId}/move`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    folder_id: folderId
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Move response:', result);

            // Show success notification
            if (window.dragAndDrop && typeof window.dragAndDrop.showNotification === 'function') {
                window.dragAndDrop.showNotification('Dokument byl úspěšně přesunut', 'success');
            } else {
                alert('Dokument byl úspěšně přesunut');
            }

            // Refresh the document lists and folder structure
            if (window.currentFolderId) {
                fetchFolderContents(window.currentFolderId);
            } else {
                fetchDocumentList();
            }

            // Also refresh folder structure to update counts
            fetchFolderStructure();

        } catch (error) {
            console.error('Error moving document:', error);

            // Show error notification
            if (window.dragAndDrop && typeof window.dragAndDrop.showNotification === 'function') {
                window.dragAndDrop.showNotification(`Chyba při přesouvání dokumentu: ${error.message}`, 'error');
            } else {
                alert(`Chyba při přesouvání dokumentu: ${error.message}`);
            }
        }
    }

    // Add back button functionality
    const folderBackBtn = document.getElementById('folder-back-btn');
    if (folderBackBtn) {
        folderBackBtn.addEventListener('click', () => {
            // Hide folder section and show documents section
            const documentsSection = document.getElementById('documents-section');
            const folderSection = document.getElementById('folder-section');

            if (documentsSection && folderSection) {
                folderSection.style.display = 'none';
                documentsSection.style.display = 'block';

                // Clear current folder ID
                window.currentFolderId = null;

                // Refresh document list
                fetchDocumentList();
            }
        });
    }

    // Add edit folder button functionality
    const folderEditBtn = document.getElementById('folder-edit-btn');
    if (folderEditBtn) {
        folderEditBtn.addEventListener('click', async () => {
            console.log('Edit folder button clicked');

            if (!window.currentFolderId) {
                console.error('No current folder ID');
                return;
            }

            try {
                // Fetch folder details
                const response = await fetch(`/api/folders/${window.currentFolderId}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const folder = await response.json();
                console.log('Folder details:', folder);

                // Open folder modal with folder data
                openFolderModal(folder);

            } catch (error) {
                console.error('Error fetching folder details:', error);
                if (window.dragAndDrop && typeof window.dragAndDrop.showNotification === 'function') {
                    window.dragAndDrop.showNotification(`Chyba při načítání detailů složky: ${error.message}`, 'error');
                } else {
                    alert(`Chyba při načítání detailů složky: ${error.message}`);
                }
            }
        });
    }

    // Make fetchFolderContents globally accessible
    window.fetchFolderContents = fetchFolderContents;

    // Add folder button functionality
    const addFolderBtn = document.getElementById('add-folder-btn');
    if (addFolderBtn) {
        addFolderBtn.addEventListener('click', () => {
            console.log('Add folder button clicked');
            openFolderModal();
        });
    }

    // Folder modal functionality
    const folderModal = document.getElementById('folder-modal');
    const folderModalClose = document.getElementById('folder-modal-close');
    const folderModalCancel = document.getElementById('folder-modal-cancel');
    const folderModalSave = document.getElementById('folder-modal-save');
    const folderForm = document.getElementById('folder-form');
    const folderNameInput = document.getElementById('folder-name-input');
    const folderDescriptionInput = document.getElementById('folder-description-input');
    const folderTypeSelect = document.getElementById('folder-type-select');
    const folderParentSelect = document.getElementById('folder-parent-select');
    const folderIdInput = document.getElementById('folder-id-input');

    // Close modal on close button click
    if (folderModalClose) {
        folderModalClose.addEventListener('click', closeFolderModal);
    }

    // Close modal on cancel button click
    if (folderModalCancel) {
        folderModalCancel.addEventListener('click', closeFolderModal);
    }

    // Save folder on save button click
    if (folderModalSave) {
        folderModalSave.addEventListener('click', saveFolder);
    }

    // Close modal when clicking outside
    if (folderModal) {
        folderModal.addEventListener('click', (e) => {
            if (e.target === folderModal) {
                closeFolderModal();
            }
        });
    }

    // Function to edit a folder
    function editFolder(folder) {
        console.log(`Editing folder ${folder.id}`);
        openFolderModal(folder);
    }

    // Function to open folder modal
    function openFolderModal(folder = null) {
        console.log('Opening folder modal', folder);

        if (!folderModal || !folderForm || !folderParentSelect) {
            console.error('Folder modal elements not found');
            return;
        }

        // Reset form
        folderForm.reset();

        // Set modal title
        const modalTitle = document.getElementById('folder-modal-title');
        if (modalTitle) {
            modalTitle.textContent = folder ? 'Upravit složku' : 'Nová složka';
        }

        // Fill form if editing existing folder
        if (folder) {
            if (folderNameInput) folderNameInput.value = folder.name || '';
            if (folderDescriptionInput) folderDescriptionInput.value = folder.description || '';
            if (folderTypeSelect) folderTypeSelect.value = folder.folder_type || 'general';
            if (folderIdInput) folderIdInput.value = folder.id || '';
        } else {
            if (folderIdInput) folderIdInput.value = '';
        }

        // Load parent folder options
        loadFolderOptions();

        // Set parent folder if editing
        if (folder && folderParentSelect) {
            folderParentSelect.value = folder.parent_id || '';
        }

        // Show modal
        folderModal.style.display = 'flex';
    }

    // Function to close folder modal
    function closeFolderModal() {
        console.log('Closing folder modal');

        if (folderModal) {
            folderModal.style.display = 'none';
        }
    }

    // Function to load folder options for parent select
    async function loadFolderOptions() {
        console.log('Loading folder options');

        if (!folderParentSelect) {
            console.error('Folder parent select element not found');
            return;
        }

        try {
            const response = await fetch('/api/folders');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const folders = await response.json();
            console.log('Folders fetched for options:', folders);

            // Clear options except the first one (no parent)
            while (folderParentSelect.options.length > 1) {
                folderParentSelect.remove(1);
            }

            // Add folder options
            folders.forEach(folder => {
                const option = document.createElement('option');
                option.value = folder.id;
                option.textContent = folder.name;
                folderParentSelect.appendChild(option);
            });

        } catch (error) {
            console.error('Error loading folder options:', error);
            if (window.dragAndDrop && typeof window.dragAndDrop.showNotification === 'function') {
                window.dragAndDrop.showNotification(`Chyba při načítání složek: ${error.message}`, 'error');
            }
        }
    }

    // Function to save folder
    async function saveFolder() {
        console.log('Saving folder');

        if (!folderForm || !folderNameInput) {
            console.error('Folder form elements not found');
            return;
        }

        // Validate form
        if (!folderNameInput.value.trim()) {
            if (window.dragAndDrop && typeof window.dragAndDrop.showNotification === 'function') {
                window.dragAndDrop.showNotification('Zadejte název složky', 'error');
            } else {
                alert('Zadejte název složky');
            }
            return;
        }

        // Get form data
        const folderData = {
            name: folderNameInput.value.trim(),
            description: folderDescriptionInput ? folderDescriptionInput.value.trim() : '',
            folder_type: folderTypeSelect ? folderTypeSelect.value : 'general',
            parent_id: folderParentSelect && folderParentSelect.value ? folderParentSelect.value : null
        };

        // Add ID if editing
        if (folderIdInput && folderIdInput.value) {
            folderData.id = folderIdInput.value;
        }

        console.log('Folder data:', folderData);

        try {
            // Determine if creating or updating
            const isUpdate = folderData.id ? true : false;
            const url = isUpdate ? `/api/folders/${folderData.id}` : '/api/folders';
            const method = isUpdate ? 'PUT' : 'POST';

            // Send request
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(folderData),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Save folder response:', result);

            // Show success notification
            if (window.dragAndDrop && typeof window.dragAndDrop.showNotification === 'function') {
                window.dragAndDrop.showNotification(
                    isUpdate ? 'Složka byla úspěšně aktualizována' : 'Složka byla úspěšně vytvořena',
                    'success'
                );
            } else {
                alert(isUpdate ? 'Složka byla úspěšně aktualizována' : 'Složka byla úspěšně vytvořena');
            }

            // Close modal
            closeFolderModal();

            // Refresh folder structure
            fetchFolderStructure();

        } catch (error) {
            console.error('Error saving folder:', error);
            if (window.dragAndDrop && typeof window.dragAndDrop.showNotification === 'function') {
                window.dragAndDrop.showNotification(`Chyba při ukládání složky: ${error.message}`, 'error');
            } else {
                alert(`Chyba při ukládání složky: ${error.message}`);
            }
        }
    }

    // Function to set up auto-refresh for documents and folders
    function setupAutoRefresh() {
        console.log('Setting up auto-refresh');

        // Clear any existing intervals
        if (window.refreshIntervals) {
            console.log('Clearing existing refresh intervals');
            clearInterval(window.refreshIntervals.documents);
            clearInterval(window.refreshIntervals.folders);
        }

        // Store the current state to detect changes
        let lastDocumentCount = 0;
        let lastDocumentStatuses = {};
        let lastFolderCounts = {};

        // Function to check for document updates
        async function checkForDocumentUpdates() {
            try {
                const response = await fetch('/api/documents');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                const documents = result.documents || [];

                // Check if document count has changed
                if (documents.length !== lastDocumentCount) {
                    console.log('Document count changed, refreshing list');
                    fetchDocumentList();
                    lastDocumentCount = documents.length;
                    return; // Full refresh already done
                }

                // Check if any document status has changed
                let statusChanged = false;
                documents.forEach(doc => {
                    if (!lastDocumentStatuses[doc.id] || lastDocumentStatuses[doc.id] !== doc.status) {
                        statusChanged = true;
                        lastDocumentStatuses[doc.id] = doc.status;

                        // Update status indicator for this document
                        updateDocumentStatus(doc.id, doc.status);
                    }
                });

                if (statusChanged) {
                    console.log('Document statuses changed, updating indicators');
                }

            } catch (error) {
                console.error('Error checking for document updates:', error);
            }
        }

        // Function to check for folder updates
        async function checkForFolderUpdates() {
            try {
                const response = await fetch('/api/folders');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const folders = await response.json();

                // Check if any folder document count has changed
                let countsChanged = false;
                folders.forEach(folder => {
                    if (!lastFolderCounts[folder.id] || lastFolderCounts[folder.id] !== folder.document_count) {
                        countsChanged = true;
                        lastFolderCounts[folder.id] = folder.document_count;

                        // Update count indicator for this folder
                        updateFolderCount(folder.id, folder.document_count);
                    }
                });

                if (countsChanged) {
                    console.log('Folder counts changed, updating indicators');
                }

            } catch (error) {
                console.error('Error checking for folder updates:', error);
            }
        }

        // Function to update document status indicator
        function updateDocumentStatus(docId, status) {
            // Update in main document list
            const docItems = document.querySelectorAll(`.document-item[data-id="${docId}"]`);

            docItems.forEach(item => {
                // Update status indicator
                let statusIndicator = item.querySelector('.doc-status');
                if (!statusIndicator) {
                    statusIndicator = document.createElement('div');
                    statusIndicator.className = 'doc-status';
                    item.appendChild(statusIndicator);
                }

                // Update class
                statusIndicator.className = `doc-status ${status ? 'status-' + status.toLowerCase() : ''}`;

                // Update status text in meta if it exists
                const statusMeta = item.querySelector('.doc-meta-item i[class*="fa-"]');
                if (statusMeta) {
                    statusMeta.className = getStatusIcon(status);
                    const statusText = statusMeta.nextElementSibling;
                    if (statusText) {
                        statusText.textContent = getStatusText(status);
                    }
                }

                // If status is 'completed' and was previously 'processing', show notification
                if (status === 'completed' && lastDocumentStatuses[docId] === 'processing') {
                    if (window.dragAndDrop && typeof window.dragAndDrop.showNotification === 'function') {
                        window.dragAndDrop.showNotification(`Dokument "${item.querySelector('.doc-title')?.textContent || 'Dokument'}" byl úspěšně zpracován`, 'success');
                    }
                }

                // If status is 'error' and was previously 'processing', show error notification
                if (status === 'error' && lastDocumentStatuses[docId] === 'processing') {
                    if (window.dragAndDrop && typeof window.dragAndDrop.showNotification === 'function') {
                        window.dragAndDrop.showNotification(`Při zpracování dokumentu "${item.querySelector('.doc-title')?.textContent || 'Dokument'}" došlo k chybě`, 'error');
                    }
                }
            });
        }

        // Function to update folder count indicator
        function updateFolderCount(folderId, count) {
            // Update in folder tree
            const folderItems = document.querySelectorAll(`.folder-item[data-id="${folderId}"]`);

            folderItems.forEach(item => {
                const countElement = item.querySelector('.folder-count');
                if (countElement) {
                    countElement.textContent = count || '0';
                }
            });

            // Update in subfolder list
            const subfolderItems = document.querySelectorAll(`.subfolder-item[data-id="${folderId}"]`);

            subfolderItems.forEach(item => {
                const countElement = item.querySelector('.subfolder-count');
                if (countElement) {
                    countElement.textContent = `${count || '0'} dokumentů`;
                }
            });
        }

        // Set up intervals for checking updates
        const documentCheckInterval = setInterval(checkForDocumentUpdates, 3000); // Check every 3 seconds
        const folderCheckInterval = setInterval(checkForFolderUpdates, 5000); // Check every 5 seconds

        // Initial check
        checkForDocumentUpdates();
        checkForFolderUpdates();

        // Store intervals in window object so they can be cleared if needed
        window.refreshIntervals = {
            documents: documentCheckInterval,
            folders: folderCheckInterval
        };
    }

    // Export fetchDocumentList function to global scope
    window.fetchDocumentList = fetchDocumentList;
});
