/**
 * Main JavaScript for the Arabic File Uploader application.
 * Handles UI interactions, drag & drop, file selection, upload, and feedback.
 */
document.addEventListener('DOMContentLoaded', function() {
    // --- DOM Element References --- //
    const uploadArea = document.getElementById('upload-area');
    const fileUploadInput = document.getElementById('file-upload');
    const fileInfoDisplay = document.getElementById('file-info');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress');
    const progressText = document.getElementById('progress-text');
    const resultContainer = document.getElementById('result-container');
    const downloadLinkInput = document.getElementById('download-link');
    const copyButton = document.getElementById('copy-button');
    const uploadAnotherButton = document.getElementById('upload-another');
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');

    let currentXhr = null; // To hold the current upload request

    // --- Event Listeners Setup --- //

    // Click to browse files
    if (uploadArea) {
        uploadArea.addEventListener('click', () => fileUploadInput?.click());
    }

    // File selection via browse button
    if (fileUploadInput) {
        fileUploadInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelection(e.target.files);
            }
        });
    }

    // Drag and Drop listeners
    if (uploadArea) {
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
    }

    // Copy download link
    if (copyButton) {
        copyButton.addEventListener('click', copyDownloadLink);
    }

    // Upload another file
    if (uploadAnotherButton) {
        uploadAnotherButton.addEventListener('click', resetUploadForm);
    }

    // --- Drag and Drop Handlers --- //

    function handleDragOver(e) {
        e.preventDefault(); // Necessary to allow drop
        e.stopPropagation();
        uploadArea?.classList.add('drag-over');
    }

    function handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea?.classList.remove('drag-over');
    }

    function handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea?.classList.remove('drag-over');
        
        const files = e.dataTransfer?.files;
        if (files && files.length > 0) {
            handleFileSelection(files);
        } else {
            showToast('لم يتم العثور على ملفات في السحب.', 'error');
        }
    }

    // --- Core Logic Functions --- //

    /**
     * Handles the selection of a file (either by browse or drag/drop).
     * @param {FileList} files - The list of files selected.
     */
    function handleFileSelection(files) {
        if (!files || files.length === 0) return;
        
        const file = files[0]; // Handle only the first file

        // Optional: Basic client-side validation (e.g., file size)
        // const maxSize = 500 * 1024 * 1024; // 500MB (example)
        // if (file.size > maxSize) {
        //     showToast(`حجم الملف يتجاوز الحد المسموح به (${formatFileSize(maxSize)}).`, 'error');
        //     return;
        // }
        
        if (fileInfoDisplay) {
            fileInfoDisplay.textContent = `الملف المحدد: ${file.name} (${formatFileSize(file.size)})`;
        }
        
        // Start the upload process
        uploadFile(file);
    }

    /**
     * Initiates the file upload using XMLHttpRequest for progress tracking.
     * @param {File} file - The file to upload.
     */
    function uploadFile(file) {
        // Cancel any ongoing upload
        if (currentXhr) {
            currentXhr.abort();
            currentXhr = null;
        }
        
        // Prepare FormData
        const formData = new FormData();
        formData.append('file', file);
        
        // Create and configure XMLHttpRequest
        const xhr = new XMLHttpRequest();
        currentXhr = xhr;

        // Progress event listener
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 100);
                updateProgress(percentComplete);
            }
        });
        
        // Load (success) event listener
        xhr.addEventListener('load', () => {
            currentXhr = null; // Clear current XHR
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.status === 'success' && response.download_link) {
                        showResult(response.download_link);
                    } else {
                        // Use error message from server response
                        showToast(response.message || 'فشل رفع الملف.', 'error');
                        resetUploadForm(); 
                    }
                } catch (parseError) {
                    console.error("Error parsing server response:", parseError);
                    showToast('حدث خطأ غير متوقع في استجابة الخادم.', 'error');
                    resetUploadForm();
                }
            } else {
                // Handle non-2xx HTTP statuses
                let errorMessage = `فشل الرفع: ${xhr.statusText} (${xhr.status})`;
                try {
                     const errorResponse = JSON.parse(xhr.responseText);
                     errorMessage = errorResponse.message || errorMessage;
                } catch (e) { /* Ignore if response is not JSON */ }
                showToast(errorMessage, 'error');
                resetUploadForm();
            }
        });
        
        // Error event listener (network errors, etc.)
        xhr.addEventListener('error', () => {
            currentXhr = null;
            console.error("XHR Error occurred");
            showToast('حدث خطأ في الشبكة أثناء محاولة الرفع.', 'error');
            resetUploadForm();
        });

        // Abort event listener
        xhr.addEventListener('abort', () => {
            currentXhr = null;
            console.log("Upload aborted by user.");
            // Optionally show a message, but usually just resetting is fine
             resetUploadForm();
        });
        
        // Open and send the request
        xhr.open('POST', '/upload', true); // Use true for asynchronous
        // Optional: Set headers if needed (e.g., CSRF token)
        // xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken')); 
        xhr.send(formData);
        
        // Update UI to show progress
        if (uploadArea) uploadArea.style.display = 'none';
        if (resultContainer) resultContainer.style.display = 'none';
        if (progressContainer) progressContainer.style.display = 'block';
        updateProgress(0); // Start progress at 0%
    }

    /**
     * Copies the download link to the clipboard.
     */
    function copyDownloadLink() {
        if (!downloadLinkInput) return;

        downloadLinkInput.select(); // Select the text
        downloadLinkInput.setSelectionRange(0, 99999); // For mobile devices

        try {
            // Use Clipboard API if available (more modern and secure)
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(downloadLinkInput.value).then(() => {
                    showToast('تم نسخ الرابط بنجاح!');
                }).catch(err => {
                    console.error('Failed to copy using Clipboard API:', err);
                    // Fallback to execCommand if Clipboard API fails
                    executeCopyCommand();
                });
            } else {
                // Fallback for older browsers
                executeCopyCommand();
            }
        } catch (err) {
            console.error('Error copying text: ', err);
            showToast('فشل نسخ الرابط.', 'error');
        }
    }

    /**
     * Fallback function using document.execCommand('copy').
     */
     function executeCopyCommand() {
         const successful = document.execCommand('copy');
         if (successful) {
             showToast('تم نسخ الرابط بنجاح!');
         } else {
             console.error('Fallback execCommand copy failed');
             showToast('فشل نسخ الرابط.', 'error');
         }
         // Deselect the text after copying
         window.getSelection()?.removeAllRanges(); 
     }

    // --- UI Update Functions --- //

    /**
     * Updates the progress bar and text.
     * @param {number} percent - The percentage complete (0-100).
     */
    function updateProgress(percent) {
        if (progressBar) {
            progressBar.style.width = percent + '%';
            progressBar.setAttribute('aria-valuenow', percent); // Accessibility
        }
        if (progressText) {
            progressText.textContent = percent + '%';
        }
    }

    /**
     * Shows the result section with the download link.
     * @param {string} link - The download link received from the server.
     */
    function showResult(link) {
        if (progressContainer) progressContainer.style.display = 'none';
        if (resultContainer) resultContainer.style.display = 'block';
        if (downloadLinkInput) downloadLinkInput.value = link;
    }

    /**
     * Resets the form to the initial state for a new upload.
     */
    function resetUploadForm() {
        if (fileUploadInput) fileUploadInput.value = ''; // Clear file input
        if (fileInfoDisplay) fileInfoDisplay.textContent = '';
        updateProgress(0);
        if (uploadArea) uploadArea.style.display = 'block';
        if (progressContainer) progressContainer.style.display = 'none';
        if (resultContainer) resultContainer.style.display = 'none';
        if (downloadLinkInput) downloadLinkInput.value = '';
        
        // If an upload was in progress, abort it
        if (currentXhr) {
            currentXhr.abort();
            currentXhr = null;
        }
    }

    /**
     * Displays a temporary toast message.
     * @param {string} message - The message to display.
     * @param {'info'|'error'|'success'} type - The type of message (affects styling if CSS is set up).
     */
    let toastTimeout = null;
    function showToast(message, type = 'info') {
        if (!toast || !toastMessage) return;

        toastMessage.textContent = message;
        toast.className = 'toast'; // Reset classes
        toast.classList.add('show');
        if (type === 'error') {
            toast.classList.add('error'); // Add error class if defined in CSS
        } else if (type === 'success') {
             toast.classList.add('success'); // Add success class if defined in CSS
        }

        // Clear existing timeout if a new toast is shown quickly
        if (toastTimeout) {
            clearTimeout(toastTimeout);
        }

        // Hide the toast after a delay
        toastTimeout = setTimeout(() => {
            toast.classList.remove('show');
            toastTimeout = null;
        }, 3500); // Slightly longer duration
    }

    // --- Utility Functions --- //

    /**
     * Formats file size in bytes to a human-readable string (KB, MB, GB).
     * @param {number} bytes - The file size in bytes.
     * @returns {string} - Human-readable file size.
     */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 بايت';
        const k = 1024;
        const sizes = ['بايت', 'كيلوبايت', 'ميجابايت', 'جيجابايت']; // Arabic units
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        // Use NumberFormat for locale-aware number formatting (optional but good practice)
        const formattedNumber = new Intl.NumberFormat('ar').format(parseFloat((bytes / Math.pow(k, i)).toFixed(2)));
        return formattedNumber + ' ' + sizes[i];
    }

    // Optional: Helper to get CSRF token if needed
    // function getCookie(name) { ... }

});
