(function() {
    'use strict';

    let state = {
        taskId: null,
        lastTaskId: null,
        files: [],
        isConverting: false,
        statusPolling: null
    };

    const elements = {
        uploadArea: document.getElementById('uploadArea'),
        fileInput: document.getElementById('fileInput'),
        selectFilesBtn: document.getElementById('selectFilesBtn'),
        optionsSection: document.getElementById('optionsSection'),
        fileListSection: document.getElementById('fileListSection'),
        fileList: document.getElementById('fileList'),
        clearFilesBtn: document.getElementById('clearFilesBtn'),
        pdfTitle: document.getElementById('pdfTitle'),
        startConvertBtn: document.getElementById('startConvertBtn'),
        progressSection: document.getElementById('progressSection'),
        totalProgressBar: document.getElementById('totalProgressBar'),
        totalProgressFill: document.getElementById('totalProgressFill'),
        totalProgressPercent: document.getElementById('totalProgressPercent'),
        progressStatus: document.getElementById('progressStatus'),
        progressStats: document.getElementById('progressStats'),
        resultsSection: document.getElementById('resultsSection'),
        resultsList: document.getElementById('resultsList'),
        downloadAllBtn: document.getElementById('downloadAllBtn'),
        newTaskBtn: document.getElementById('newTaskBtn'),
        previewModal: document.getElementById('previewModal'),
        modalOverlay: document.getElementById('modalOverlay'),
        modalClose: document.getElementById('modalClose'),
        previewIframe: document.getElementById('previewIframe'),
        previewTitle: document.getElementById('previewTitle'),
        toastContainer: document.getElementById('toastContainer')
    };

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `<span class="toast-message">${message}</span>`;
        elements.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    function getFileIcon(fileName) {
        const ext = fileName.split('.').pop().toLowerCase();
        const icons = {
            pdf: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>',
            doc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
            docx: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
            xls: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>',
            xlsx: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>',
            ppt: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="18" rx="2"/><path d="M7 7h6a3 3 0 0 1 0 6H7z"/><line x1="7" y1="17" x2="17" y2="17"/></svg>',
            pptx: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="18" rx="2"/><path d="M7 7h6a3 3 0 0 1 0 6H7z"/><line x1="7" y1="17" x2="17" y2="17"/></svg>',
            jpg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
            jpeg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
            png: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
            gif: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
            txt: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/></svg>',
            md: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M8 13l2 2 4-4"/><line x1="8" y1="17" x2="16" y2="17"/></svg>',
            html: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><polyline points="16 13 12 17 8 13"/></svg>',
            xml: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><polyline points="10 13 7 16 10 19"/><polyline points="14 13 17 16 14 19"/></svg>',
            json: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><circle cx="9" cy="14" r="1"/><circle cx="15" cy="14" r="1"/><circle cx="12" cy="17" r="1"/></svg>',
            csv: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="12" y1="3" x2="12" y2="21"/></svg>'
        };
        return icons[ext] || icons.txt;
    }

    function getStatusBadgeClass(status) {
        const classes = {
            pending: 'pending',
            uploading: 'uploading',
            uploaded: 'pending',
            converting: 'converting',
            completed: 'completed',
            failed: 'failed'
        };
        return classes[status] || 'pending';
    }

    function getStatusText(status) {
        const texts = {
            pending: '等待中',
            uploading: '上传中',
            uploaded: '已上传',
            converting: '转换中',
            completed: '已完成',
            failed: '失败'
        };
        return texts[status] || '未知';
    }

    async function ensureTask() {
        if (!state.taskId) {
            try {
                const response = await fetch('/api/tasks/create', { method: 'POST' });
                const data = await response.json();
                state.taskId = data.task_id;
                console.log('Created new task:', state.taskId);
            } catch (error) {
                console.error('Failed to create task:', error);
                showToast('创建任务失败', 'error');
                return false;
            }
        }
        return true;
    }

    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`/api/tasks/${state.taskId}/upload`, {
                method: 'POST',
                body: formData
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Upload failed: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Failed to upload file:', error);
            throw error;
        }
    }

    async function getTaskStatus() {
        try {
            const response = await fetch(`/api/tasks/${state.taskId}/status`);
            if (!response.ok) {
                throw new Error(`Status check failed: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Failed to get task status:', error);
            return null;
        }
    }

    async function startConversion() {
        const pdfTitle = elements.pdfTitle.value.trim() || null;
        
        const formData = new FormData();
        if (pdfTitle) {
            formData.append('pdf_title', pdfTitle);
        }

        try {
            const response = await fetch(`/api/tasks/${state.taskId}/convert`, {
                method: 'POST',
                body: formData
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Conversion failed: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Failed to start conversion:', error);
            throw error;
        }
    }

    function renderFileList(files) {
        elements.fileList.innerHTML = '';
        
        files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-icon">${getFileIcon(file.original_name)}</div>
                <div class="file-info">
                    <div class="file-name">${escapeHtml(file.original_name)}</div>
                    <div class="file-size">${formatFileSize(file.file_size)}</div>
                </div>
                <span class="file-status ${getStatusBadgeClass(file.status)}">${getStatusText(file.status)}</span>
                <div class="file-actions">
                    <button class="btn btn-outline" onclick="app.removeFile(${index})" title="移除" ${state.isConverting ? 'disabled' : ''}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                            <line x1="18" y1="6" x2="6" y2="18"/>
                            <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
            `;
            elements.fileList.appendChild(fileItem);
        });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function updateProgress(statusData) {
        const progress = Math.round(statusData.total_progress);
        elements.totalProgressFill.style.width = `${progress}%`;
        elements.totalProgressPercent.textContent = `${progress}%`;
        
        const statusTexts = {
            pending: '准备中...',
            processing: '转换中...',
            completed: '转换完成',
            partial_failed: '部分失败',
            failed: '转换失败'
        };
        elements.progressStatus.textContent = statusTexts[statusData.status] || '处理中...';
        
        elements.progressStats.innerHTML = `
            <span><span class="stat-dot completed"></span> 成功: ${statusData.completed_count}</span>
            <span><span class="stat-dot failed"></span> 失败: ${statusData.failed_count}</span>
            <span><span class="stat-dot pending"></span> 总计: ${statusData.total_files}</span>
        `;
        
        state.files = statusData.files;
    }

    function renderResults(statusData) {
        elements.resultsList.innerHTML = '';
        
        const currentTaskId = statusData.task_id || state.taskId;
        console.log('renderResults using taskId:', currentTaskId);
        
        statusData.files.forEach(file => {
            const isSuccess = file.status === 'completed';
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';
            
            const successIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="16 8 10 14 8 12"/></svg>';
            const failIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>';
            
            let actionsHtml = '';
            if (isSuccess && currentTaskId) {
                actionsHtml = `
                    <button class="btn btn-primary" onclick="app.previewFile('${file.id}', '${currentTaskId}')" title="预览">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                            <circle cx="12" cy="12" r="3"/>
                        </svg>
                        预览
                    </button>
                    <a class="btn btn-success" href="/api/tasks/${currentTaskId}/download/${file.id}" download title="下载">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                            <polyline points="7 10 12 15 17 10"/>
                            <line x1="12" y1="15" x2="12" y2="3"/>
                        </svg>
                        下载
                    </a>
                `;
            }
            
            resultItem.innerHTML = `
                <div class="result-icon ${isSuccess ? 'success' : 'failed'}">
                    ${isSuccess ? successIcon : failIcon}
                </div>
                <div class="result-info">
                    <div class="result-name">${escapeHtml(file.original_name)}</div>
                    <div class="result-message">${isSuccess ? '转换成功' : escapeHtml(file.error_message || '转换失败')}</div>
                </div>
                <div class="result-actions">${actionsHtml}</div>
            `;
            elements.resultsList.appendChild(resultItem);
        });
    }

    async function startStatusPolling() {
        const poll = async () => {
            const statusData = await getTaskStatus();
            if (statusData) {
                updateProgress(statusData);
                
                if (['completed', 'partial_failed', 'failed'].includes(statusData.status)) {
                    stopStatusPolling();
                    state.isConverting = false;
                    elements.startConvertBtn.disabled = false;
                    showResults(statusData);
                }
            }
        };
        
        await poll();
        state.statusPolling = setInterval(poll, 1000);
    }

    function stopStatusPolling() {
        if (state.statusPolling) {
            clearInterval(state.statusPolling);
            state.statusPolling = null;
        }
    }

    function showResults(statusData) {
        state.lastTaskId = statusData.task_id || state.taskId;
        console.log('showResults - lastTaskId:', state.lastTaskId);
        
        elements.progressSection.style.display = 'none';
        elements.resultsSection.style.display = 'block';
        renderResults(statusData);
        
        const hasSuccess = statusData.files.some(f => f.status === 'completed');
        elements.downloadAllBtn.style.display = hasSuccess ? 'inline-flex' : 'none';
        
        if (statusData.status === 'completed') {
            showToast('所有文件转换完成！', 'success');
        } else if (statusData.status === 'partial_failed') {
            showToast('部分文件转换失败', 'warning');
        } else {
            showToast('转换失败', 'error');
        }
    }

    function showPreview(fileId, fileName, taskId) {
        const useTaskId = taskId || state.taskId;
        if (!useTaskId) {
            showToast('任务不存在', 'error');
            return;
        }
        
        elements.previewTitle.textContent = fileName;
        const previewUrl = `/api/tasks/${useTaskId}/preview/${fileId}`;
        elements.previewIframe.src = previewUrl;
        elements.previewModal.style.display = 'flex';
        
        console.log('Preview URL:', previewUrl);
    }

    function hidePreview() {
        elements.previewModal.style.display = 'none';
        elements.previewIframe.src = '';
    }

    function resetForNewTask() {
        stopStatusPolling();
        
        state = {
            taskId: null,
            lastTaskId: null,
            files: [],
            isConverting: false,
            statusPolling: null
        };
        
        elements.optionsSection.style.display = 'none';
        elements.fileListSection.style.display = 'none';
        elements.progressSection.style.display = 'none';
        elements.resultsSection.style.display = 'none';
        elements.pdfTitle.value = '';
        elements.fileInput.value = '';
        elements.startConvertBtn.disabled = false;
    }

    function removeFile(index) {
        if (state.isConverting) return;
        state.files.splice(index, 1);
        renderFileList(state.files);
        
        if (state.files.length === 0) {
            elements.optionsSection.style.display = 'none';
            elements.fileListSection.style.display = 'none';
        }
    }

    async function handleFiles(selectedFiles) {
        if (selectedFiles.length === 0) return;
        
        const taskOk = await ensureTask();
        if (!taskOk) return;
        
        elements.optionsSection.style.display = 'block';
        elements.fileListSection.style.display = 'block';
        
        let successCount = 0;
        
        for (const file of selectedFiles) {
            const fileData = {
                original_name: file.name,
                file_size: file.size,
                status: 'uploading',
                id: Math.random().toString(36).substr(2, 9)
            };
            state.files.push(fileData);
            renderFileList(state.files);
            
            try {
                const uploadResult = await uploadFile(file);
                if (uploadResult) {
                    fileData.id = uploadResult.file_id;
                    fileData.status = 'uploaded';
                    successCount++;
                } else {
                    fileData.status = 'failed';
                    showToast(`上传 ${file.name} 失败`, 'error');
                }
            } catch (error) {
                fileData.status = 'failed';
                showToast(`上传 ${file.name} 失败: ${error.message}`, 'error');
            }
            renderFileList(state.files);
        }
        
        if (successCount > 0) {
            showToast(`已添加 ${successCount} 个文件`, 'success');
        }
    }

    function initEventListeners() {
        elements.selectFilesBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            elements.fileInput.click();
        });

        elements.uploadArea.addEventListener('click', () => {
            elements.fileInput.click();
        });

        elements.fileInput.addEventListener('change', (e) => {
            handleFiles(Array.from(e.target.files));
        });

        elements.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            elements.uploadArea.classList.add('drag-over');
        });

        elements.uploadArea.addEventListener('dragleave', () => {
            elements.uploadArea.classList.remove('drag-over');
        });

        elements.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            elements.uploadArea.classList.remove('drag-over');
            
            const files = Array.from(e.dataTransfer.files).filter(file => !file.type.startsWith('directory/'));
            handleFiles(files);
        });

        elements.clearFilesBtn.addEventListener('click', () => {
            if (state.isConverting) return;
            state.files = [];
            elements.fileList.innerHTML = '';
            elements.optionsSection.style.display = 'none';
            elements.fileListSection.style.display = 'none';
            elements.fileInput.value = '';
            showToast('已清空文件列表', 'info');
        });

        elements.startConvertBtn.addEventListener('click', async () => {
            if (state.files.length === 0) {
                showToast('请先添加文件', 'warning');
                return;
            }
            
            if (state.isConverting) {
                showToast('正在转换中，请等待', 'warning');
                return;
            }
            
            state.isConverting = true;
            elements.startConvertBtn.disabled = true;
            
            elements.fileListSection.style.display = 'none';
            elements.optionsSection.style.display = 'none';
            elements.progressSection.style.display = 'block';
            
            try {
                const result = await startConversion();
                if (result) {
                    showToast('开始转换...', 'info');
                    startStatusPolling();
                } else {
                    throw new Error('Unknown error');
                }
            } catch (error) {
                state.isConverting = false;
                elements.startConvertBtn.disabled = false;
                elements.fileListSection.style.display = 'block';
                elements.optionsSection.style.display = 'block';
                elements.progressSection.style.display = 'none';
                showToast(`开始转换失败: ${error.message}`, 'error');
            }
        });

        elements.downloadAllBtn.addEventListener('click', () => {
            const currentTaskId = state.lastTaskId || state.taskId;
            if (!currentTaskId) {
                showToast('任务不存在', 'error');
                return;
            }
            const zipUrl = `/api/tasks/${currentTaskId}/download/zip`;
            console.log('Download ZIP URL:', zipUrl);
            window.location.href = zipUrl;
        });

        elements.newTaskBtn.addEventListener('click', () => {
            resetForNewTask();
            showToast('可以开始新任务了', 'info');
        });

        elements.modalOverlay.addEventListener('click', hidePreview);
        elements.modalClose.addEventListener('click', hidePreview);

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && elements.previewModal.style.display === 'flex') {
                hidePreview();
            }
        });
    }

    window.app = {
        removeFile: removeFile,
        previewFile: function(fileId, taskId) {
            const file = state.files.find(f => f.id === fileId);
            const useTaskId = taskId || state.taskId || state.lastTaskId;
            const pdfName = file ? file.original_name.replace(/\.[^.]+$/, '.pdf') : 'document.pdf';
            console.log('previewFile called with fileId:', fileId, 'taskId:', useTaskId);
            showPreview(fileId, pdfName, useTaskId);
        }
    };

    initEventListeners();
})();
