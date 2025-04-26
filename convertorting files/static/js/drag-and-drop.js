/**
 * Drag and Drop functionality for the file conversion system
 * Handles document dragging between folders and file uploads via drag and drop
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing drag and drop functionality');
    
    // Initialize drag and drop for documents
    initDocumentDragAndDrop();
    
    // Initialize drag and drop for file uploads
    initFileUploadDragAndDrop();
});

/**
 * Initialize drag and drop functionality for documents
 */
function initDocumentDragAndDrop() {
    // Get all draggable lists
    const draggableLists = document.querySelectorAll('.draggable-list');
    
    if (draggableLists.length === 0) {
        console.log('No draggable lists found');
        return;
    }
    
    console.log(`Found ${draggableLists.length} draggable lists`);
    
    // Get all folder items that can be drop targets
    const folderItems = document.querySelectorAll('.folder-item');
    
    if (folderItems.length === 0) {
        console.log('No folder items found');
    } else {
        console.log(`Found ${folderItems.length} folder items`);
    }
    
    // Track the currently dragged element
    let draggedElement = null;
    
    // Add event listeners to all draggable items
    draggableLists.forEach(list => {
        // Get all list items
        const items = list.querySelectorAll('li');
        
        items.forEach(item => {
            // Make the item draggable
            item.setAttribute('draggable', 'true');
            
            // Add dragstart event listener
            item.addEventListener('dragstart', handleDragStart);
            
            // Add dragend event listener
            item.addEventListener('dragend', handleDragEnd);
        });
    });
    
    // Add event listeners to all folder items
    folderItems.forEach(folder => {
        folder.addEventListener('dragover', handleDragOver);
        folder.addEventListener('dragenter', handleDragEnter);
        folder.addEventListener('dragleave', handleDragLeave);
        folder.addEventListener('drop', handleDrop);
    });
    
    /**
     * Handle the start of a drag operation
     * @param {DragEvent} e - The drag event
     */
    function handleDragStart(e) {
        console.log('Drag started');
        
        // Store the dragged element
        draggedElement = this;
        
        // Add a class to style the dragged element
        this.classList.add('dragging');
        
        // Set the drag data
        e.dataTransfer.setData('text/plain', this.dataset.id || '');
        e.dataTransfer.effectAllowed = 'move';
        
        // Set a custom drag image if needed
        // const dragImage = document.createElement('div');
        // dragImage.textContent = this.textContent;
        // dragImage.classList.add('drag-image');
        // document.body.appendChild(dragImage);
        // e.dataTransfer.setDragImage(dragImage, 0, 0);
        // setTimeout(() => document.body.removeChild(dragImage), 0);
    }
    
    /**
     * Handle the end of a drag operation
     */
    function handleDragEnd() {
        console.log('Drag ended');
        
        // Remove the dragging class
        this.classList.remove('dragging');
        
        // Clear the dragged element
        draggedElement = null;
        
        // Remove drop-target class from all folders
        folderItems.forEach(folder => {
            folder.classList.remove('drop-target');
        });
    }
    
    /**
     * Handle dragover event on a drop target
     * @param {DragEvent} e - The drag event
     */
    function handleDragOver(e) {
        // Prevent default to allow drop
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    }
    
    /**
     * Handle dragenter event on a drop target
     * @param {DragEvent} e - The drag event
     */
    function handleDragEnter(e) {
        // Prevent default to allow drop
        e.preventDefault();
        
        // Add a class to highlight the drop target
        this.classList.add('drop-target');
    }
    
    /**
     * Handle dragleave event on a drop target
     */
    function handleDragLeave() {
        // Remove the highlight class
        this.classList.remove('drop-target');
    }
    
    /**
     * Handle drop event on a drop target
     * @param {DragEvent} e - The drag event
     */
    async function handleDrop(e) {
        // Prevent default action
        e.preventDefault();
        
        // Remove the highlight class
        this.classList.remove('drop-target');
        
        // Get the document ID from the dragged element
        const documentId = e.dataTransfer.getData('text/plain');
        
        if (!documentId) {
            console.error('No document ID found in drag data');
            showNotification('Chyba: Nelze přesunout dokument bez ID', 'error');
            return;
        }
        
        // Get the folder ID from the drop target
        const folderId = this.dataset.id;
        
        if (!folderId) {
            console.error('No folder ID found in drop target');
            showNotification('Chyba: Nelze přesunout do složky bez ID', 'error');
            return;
        }
        
        console.log(`Moving document ${documentId} to folder ${folderId}`);
        
        try {
            // Call the API to move the document
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
            showNotification('Dokument byl úspěšně přesunut', 'success');
            
            // Remove the document from its original list
            if (draggedElement && draggedElement.parentNode) {
                draggedElement.parentNode.removeChild(draggedElement);
            }
            
            // Refresh the document lists if needed
            // This depends on your application structure
            // You might want to refresh the source and target lists
            
            // Option 1: Refresh the entire document list
            if (typeof fetchDocumentList === 'function') {
                fetchDocumentList();
            }
            
            // Option 2: Refresh the folder contents if we're in folder view
            if (typeof fetchFolderContents === 'function' && window.currentFolderId) {
                fetchFolderContents(window.currentFolderId);
            }
            
        } catch (error) {
            console.error('Error moving document:', error);
            showNotification(`Chyba při přesouvání dokumentu: ${error.message}`, 'error');
        }
    }
}

/**
 * Initialize drag and drop functionality for file uploads
 */
function initFileUploadDragAndDrop() {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    
    if (!dropArea || !fileInput) {
        console.log('File upload drag and drop elements not found');
        return;
    }
    
    console.log('Initializing file upload drag and drop');
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    // Remove highlight when item is dragged out or dropped
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    dropArea.addEventListener('drop', handleDrop, false);
    
    /**
     * Prevent default drag and drop behaviors
     * @param {Event} e - The event
     */
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    /**
     * Highlight the drop area
     */
    function highlight() {
        dropArea.classList.add('highlight');
    }
    
    /**
     * Remove highlight from the drop area
     */
    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    /**
     * Handle dropped files
     * @param {DragEvent} e - The drop event
     */
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        // Update the file input with the dropped files
        if (files.length > 0) {
            // Unfortunately, we can't directly set the files property of the input
            // But we can display the file names and trigger the change event
            
            // Display file names
            let fileNames = '';
            for (let i = 0; i < files.length; i++) {
                fileNames += files[i].name + '<br>';
            }
            
            const selectedFilesContainer = document.getElementById('selected-files-container');
            if (selectedFilesContainer) {
                selectedFilesContainer.innerHTML = fileNames;
            }
            
            // Create a new FormData and append the files
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('files[]', files[i]);
            }
            
            // Show upload status
            const uploadStatus = document.getElementById('upload-status');
            if (uploadStatus) {
                uploadStatus.innerHTML = `Vybrané soubory:<br>${fileNames}`;
                uploadStatus.style.display = 'block';
            }
            
            // Option 1: Automatically submit the form
            // This depends on your application's UX design
            // If you want users to click the submit button manually, comment this out
            const uploadForm = document.getElementById('upload-form');
            if (uploadForm) {
                // Trigger form submission
                // uploadForm.dispatchEvent(new Event('submit'));
                
                // Or call the upload function directly
                uploadFiles(formData, files.length);
            }
        }
    }
    
    /**
     * Upload files to the server
     * @param {FormData} formData - The form data with files
     * @param {number} fileCount - The number of files
     */
    async function uploadFiles(formData, fileCount) {
        const uploadStatus = document.getElementById('upload-status');
        
        if (uploadStatus) {
            uploadStatus.textContent = `Nahrávám ${fileCount} souborů...`;
            uploadStatus.style.display = 'block';
        }
        
        try {
            console.log('Sending upload request to /api/upload');
            
            // Upload the files
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
            
            // Show success status
            if (uploadStatus) {
                uploadStatus.textContent = `${fileCount} souborů nahráno úspěšně.`;
            }
            
            // Update the document list
            if (typeof fetchDocumentList === 'function') {
                fetchDocumentList();
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            if (uploadStatus) {
                uploadStatus.textContent = `Chyba při nahrávání: ${error.message}`;
            } else {
                alert(`Chyba při nahrávání: ${error.message}`);
            }
        }
    }
}

/**
 * Show a notification to the user
 * @param {string} message - The notification message
 * @param {string} type - The notification type (success, error, info)
 */
function showNotification(message, type = 'info') {
    // Check if notification container exists, create if not
    let notificationContainer = document.getElementById('notification-container');
    
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        document.body.appendChild(notificationContainer);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Add close button functionality
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
        notification.classList.add('notification-hiding');
        setTimeout(() => {
            notificationContainer.removeChild(notification);
        }, 300);
    });
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode === notificationContainer) {
            notification.classList.add('notification-hiding');
            setTimeout(() => {
                if (notification.parentNode === notificationContainer) {
                    notificationContainer.removeChild(notification);
                }
            }, 300);
        }
    }, 5000);
}

/**
 * Update the document list items to make them draggable
 * Call this function after loading or refreshing the document list
 */
function updateDraggableItems() {
    console.log('Updating draggable items');
    
    // Get all draggable lists
    const draggableLists = document.querySelectorAll('.draggable-list');
    
    draggableLists.forEach(list => {
        // Get all list items
        const items = list.querySelectorAll('li');
        
        items.forEach(item => {
            // Skip items that are already draggable
            if (item.getAttribute('draggable') === 'true') {
                return;
            }
            
            // Make the item draggable
            item.setAttribute('draggable', 'true');
            
            // Add dragstart event listener
            item.addEventListener('dragstart', function(e) {
                console.log('Drag started');
                
                // Add a class to style the dragged element
                this.classList.add('dragging');
                
                // Set the drag data
                e.dataTransfer.setData('text/plain', this.dataset.id || '');
                e.dataTransfer.effectAllowed = 'move';
            });
            
            // Add dragend event listener
            item.addEventListener('dragend', function() {
                console.log('Drag ended');
                
                // Remove the dragging class
                this.classList.remove('dragging');
                
                // Remove drop-target class from all folders
                document.querySelectorAll('.folder-item').forEach(folder => {
                    folder.classList.remove('drop-target');
                });
            });
        });
    });
}

// Export functions that need to be called from other scripts
window.dragAndDrop = {
    updateDraggableItems,
    showNotification
};
