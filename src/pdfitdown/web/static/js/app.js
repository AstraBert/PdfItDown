(function() {
    'use strict';

    const App = {
        currentFeature: 'convert',
        previewModal: null,
        toastContainer: null,

        init: function() {
            this.initElements();
            this.initEventListeners();
            this.initModules();
        },

        initElements: function() {
            this.previewModal = document.getElementById('previewModal');
            this.toastContainer = document.getElementById('toastContainer');
        },

        initEventListeners: function() {
            const featureTabs = document.querySelectorAll('.feature-tab');
            featureTabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    this.switchFeature(tab.dataset.feature);
                });
            });

            const modalOverlay = document.getElementById('modalOverlay');
            const modalClose = document.getElementById('modalClose');
            if (modalOverlay) modalOverlay.addEventListener('click', () => this.hidePreview());
            if (modalClose) modalClose.addEventListener('click', () => this.hidePreview());

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.previewModal && this.previewModal.style.display === 'flex') {
                    this.hidePreview();
                }
            });
        },

        initModules: function() {
            ConvertModule.init();
            MergeModule.init();
            SplitModule.init();
            CompressModule.init();
        },

        switchFeature: function(feature) {
            const tabs = document.querySelectorAll('.feature-tab');
            const contents = document.querySelectorAll('.feature-content');

            tabs.forEach(tab => {
                tab.classList.toggle('active', tab.dataset.feature === feature);
            });

            contents.forEach(content => {
                content.style.display = content.id === feature + 'Feature' ? 'block' : 'none';
            });

            this.currentFeature = feature;
            this.showToast(`已切换到${this.getFeatureName(feature)}功能`, 'info');
        },

        getFeatureName: function(feature) {
            const names = {
                convert: '转换PDF',
                merge: '合并PDF',
                split: '拆分PDF',
                compress: '压缩PDF'
            };
            return names[feature] || feature;
        },

        showToast: function(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.innerHTML = `<span class="toast-message">${message}</span>`;
            this.toastContainer.appendChild(toast);

            setTimeout(() => {
                toast.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.parentNode.removeChild(toast);
                    }
                }, 300);
            }, 3000);
        },

        showPreview: function(blob, title) {
            const previewTitle = document.getElementById('previewTitle');
            const previewIframe = document.getElementById('previewIframe');

            if (previewTitle) previewTitle.textContent = title || 'PDF 预览';
            if (previewIframe) {
                const url = window.URL.createObjectURL(blob);
                previewIframe.src = url;
            }
            if (this.previewModal) this.previewModal.style.display = 'flex';
            this.showToast('预览加载完成', 'success');
        },

        hidePreview: function() {
            const previewIframe = document.getElementById('previewIframe');
            if (this.previewModal) this.previewModal.style.display = 'none';
            if (previewIframe) {
                if (previewIframe.src && previewIframe.src.startsWith('blob:')) {
                    window.URL.revokeObjectURL(previewIframe.src);
                }
                previewIframe.src = '';
            }
        },

        formatFileSize: function(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
        },

        getFileIcon: function(fileName) {
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
        },

        escapeHtml: function(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        createTask: async function(featureType) {
            try {
                const response = await fetch(`/api/features/${featureType}/tasks/create`, { method: 'POST' });
                const data = await response.json();
                return data.task_id;
            } catch (error) {
                console.error('Failed to create task:', error);
                this.showToast('创建任务失败', 'error');
                return null;
            }
        },

        uploadFile: async function(taskId, file) {
            const formData = new FormData();
            formData.append('file', file);
            try {
                const response = await fetch(`/api/features/tasks/${taskId}/upload`, {
                    method: 'POST',
                    body: formData
                });
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `Upload failed: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('Failed to upload file:', error);
                throw error;
            }
        },

        getTaskStatus: async function(taskId) {
            try {
                const response = await fetch(`/api/features/tasks/${taskId}/status`);
                if (!response.ok) {
                    throw new Error(`Status check failed: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('Failed to get task status:', error);
                return null;
            }
        },

        getPdfInfo: async function(taskId) {
            try {
                const response = await fetch(`/api/features/tasks/${taskId}/pdf-info`);
                if (!response.ok) {
                    throw new Error(`Get PDF info failed: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('Failed to get PDF info:', error);
                return null;
            }
        },

        downloadFile: async function(taskId, fileId, originalName) {
            const downloadName = originalName || 'document.pdf';
            try {
                this.showToast('正在准备下载...', 'info');
                const response = await fetch(`/api/features/tasks/${taskId}/download/${fileId}`);
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `下载失败: ${response.status}`);
                }
                const blob = await response.blob();
                if (blob.size === 0) throw new Error('下载的文件为空');
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = downloadName;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                this.showToast('下载完成', 'success');
            } catch (error) {
                console.error('Download failed:', error);
                this.showToast(`下载失败: ${error.message}`, 'error');
            }
        },

        downloadZip: async function(taskId) {
            try {
                this.showToast('正在准备打包下载...', 'info');
                const response = await fetch(`/api/features/tasks/${taskId}/download/zip`);
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `下载失败: ${response.status}`);
                }
                const blob = await response.blob();
                if (blob.size === 0) throw new Error('下载的文件为空');
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `pdf_processed_${taskId.slice(0, 8)}.zip`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                this.showToast('下载完成', 'success');
            } catch (error) {
                console.error('ZIP download failed:', error);
                this.showToast(`打包下载失败: ${error.message}`, 'error');
            }
        },

        previewFile: async function(taskId, fileId, originalName) {
            const pdfName = originalName || 'document.pdf';
            try {
                this.showToast('正在加载预览...', 'info');
                const response = await fetch(`/api/features/tasks/${taskId}/preview/${fileId}`);
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `加载预览失败: ${response.status}`);
                }
                const blob = await response.blob();
                if (blob.size === 0) throw new Error('预览文件为空');
                this.showPreview(blob, pdfName);
            } catch (error) {
                console.error('Preview failed:', error);
                this.showToast(`加载预览失败: ${error.message}`, 'error');
            }
        }
    };

    const ConvertModule = {
        state: {
            taskId: null,
            lastTaskId: null,
            files: [],
            isConverting: false,
            statusPolling: null
        },

        elements: {},

        init: function() {
            this.cacheElements();
            this.bindEvents();
        },

        createTask: async function() {
            try {
                const response = await fetch('/api/tasks/create', { method: 'POST' });
                const data = await response.json();
                return data.task_id;
            } catch (error) {
                console.error('Failed to create convert task:', error);
                App.showToast('创建任务失败', 'error');
                return null;
            }
        },

        uploadFile: async function(taskId, file) {
            const formData = new FormData();
            formData.append('file', file);
            try {
                const response = await fetch(`/api/tasks/${taskId}/upload`, {
                    method: 'POST',
                    body: formData
                });
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `Upload failed: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('Failed to upload file:', error);
                throw error;
            }
        },

        getTaskStatus: async function(taskId) {
            try {
                const response = await fetch(`/api/tasks/${taskId}/status`);
                if (!response.ok) {
                    throw new Error(`Status check failed: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('Failed to get task status:', error);
                return null;
            }
        },

        downloadZip: async function(taskId) {
            try {
                App.showToast('正在准备打包下载...', 'info');
                const response = await fetch(`/api/tasks/${taskId}/download/zip`);
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `下载失败: ${response.status}`);
                }
                const blob = await response.blob();
                if (blob.size === 0) throw new Error('下载的文件为空');
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `converted_${taskId.slice(0, 8)}.zip`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                App.showToast('下载完成', 'success');
            } catch (error) {
                console.error('Download failed:', error);
                App.showToast(`下载失败: ${error.message}`, 'error');
            }
        },

        previewFile: function(taskId, fileId, originalName) {
            const downloadName = originalName || 'document.pdf';
            window.open(`/api/tasks/${taskId}/preview/${fileId}`, '_blank');
        },

        downloadFile: async function(taskId, fileId, originalName) {
            const downloadName = originalName || 'document.pdf';
            try {
                App.showToast('正在准备下载...', 'info');
                const response = await fetch(`/api/tasks/${taskId}/download/${fileId}`);
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `下载失败: ${response.status}`);
                }
                const blob = await response.blob();
                if (blob.size === 0) throw new Error('下载的文件为空');
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = downloadName;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                App.showToast('下载完成', 'success');
            } catch (error) {
                console.error('Download failed:', error);
                App.showToast(`下载失败: ${error.message}`, 'error');
            }
        },

        cacheElements: function() {
            this.elements = {
                uploadArea: document.getElementById('convertUploadArea'),
                fileInput: document.getElementById('convertFileInput'),
                selectFilesBtn: document.getElementById('convertSelectFilesBtn'),
                optionsSection: document.getElementById('convertOptionsSection'),
                fileListSection: document.getElementById('convertFileListSection'),
                fileList: document.getElementById('convertFileList'),
                clearBtn: document.getElementById('convertClearBtn'),
                pdfTitle: document.getElementById('convertPdfTitle'),
                startBtn: document.getElementById('convertStartBtn'),
                progressSection: document.getElementById('convertProgressSection'),
                progressBar: document.getElementById('convertProgressBar'),
                progressFill: document.getElementById('convertProgressFill'),
                progressPercent: document.getElementById('convertProgressPercent'),
                progressStatus: document.getElementById('convertProgressStatus'),
                progressStats: document.getElementById('convertProgressStats'),
                resultsSection: document.getElementById('convertResultsSection'),
                resultsList: document.getElementById('convertResultsList'),
                downloadAllBtn: document.getElementById('convertDownloadAllBtn'),
                newTaskBtn: document.getElementById('convertNewTaskBtn')
            };
        },

        bindEvents: function() {
            const el = this.elements;
            if (el.selectFilesBtn) {
                el.selectFilesBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    el.fileInput.click();
                });
            }
            if (el.uploadArea) {
                el.uploadArea.addEventListener('click', () => el.fileInput.click());
                el.uploadArea.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    el.uploadArea.classList.add('drag-over');
                });
                el.uploadArea.addEventListener('dragleave', () => {
                    el.uploadArea.classList.remove('drag-over');
                });
                el.uploadArea.addEventListener('drop', (e) => {
                    e.preventDefault();
                    el.uploadArea.classList.remove('drag-over');
                    const files = Array.from(e.dataTransfer.files).filter(file => !file.type.startsWith('directory/'));
                    this.handleFiles(files);
                });
            }
            if (el.fileInput) {
                el.fileInput.addEventListener('change', (e) => {
                    this.handleFiles(Array.from(e.target.files));
                });
            }
            if (el.clearBtn) {
                el.clearBtn.addEventListener('click', () => this.clearFiles());
            }
            if (el.startBtn) {
                el.startBtn.addEventListener('click', () => this.startConversion());
            }
            if (el.downloadAllBtn) {
                el.downloadAllBtn.addEventListener('click', () => {
                    const taskId = this.state.lastTaskId || this.state.taskId;
                    if (taskId) this.downloadZip(taskId);
                });
            }
            if (el.newTaskBtn) {
                el.newTaskBtn.addEventListener('click', () => this.resetForNewTask());
            }
        },

        handleFiles: async function(selectedFiles) {
            if (selectedFiles.length === 0) return;
            
            if (!this.state.taskId) {
                const taskId = await this.createTask();
                if (!taskId) return;
                this.state.taskId = taskId;
            }

            const el = this.elements;
            if (el.optionsSection) el.optionsSection.style.display = 'block';
            if (el.fileListSection) el.fileListSection.style.display = 'block';

            let successCount = 0;
            for (const file of selectedFiles) {
                const fileData = {
                    original_name: file.name,
                    file_size: file.size,
                    status: 'uploading',
                    id: Math.random().toString(36).substr(2, 9)
                };
                this.state.files.push(fileData);
                this.renderFileList();

                try {
                    const uploadResult = await this.uploadFile(this.state.taskId, file);
                    if (uploadResult) {
                        fileData.id = uploadResult.file_id;
                        fileData.status = 'uploaded';
                        successCount++;
                    } else {
                        fileData.status = 'failed';
                        App.showToast(`上传 ${file.name} 失败`, 'error');
                    }
                } catch (error) {
                    fileData.status = 'failed';
                    App.showToast(`上传 ${file.name} 失败: ${error.message}`, 'error');
                }
                this.renderFileList();
            }

            if (successCount > 0) {
                App.showToast(`已添加 ${successCount} 个文件`, 'success');
            }
        },

        renderFileList: function() {
            const el = this.elements;
            if (!el.fileList) return;
            
            el.fileList.innerHTML = '';
            this.state.files.forEach((file, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.innerHTML = `
                    <div class="file-icon">${App.getFileIcon(file.original_name)}</div>
                    <div class="file-info">
                        <div class="file-name">${App.escapeHtml(file.original_name)}</div>
                        <div class="file-size">${App.formatFileSize(file.file_size)}</div>
                    </div>
                    <span class="file-status ${this.getStatusBadgeClass(file.status)}">${this.getStatusText(file.status)}</span>
                    <div class="file-actions">
                        <button class="btn btn-outline" onclick="ConvertModule.removeFile(${index})" title="移除" ${this.state.isConverting ? 'disabled' : ''}>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                                <line x1="18" y1="6" x2="6" y2="18"/>
                                <line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    </div>
                `;
                el.fileList.appendChild(fileItem);
            });
        },

        getStatusBadgeClass: function(status) {
            const classes = {
                pending: 'pending',
                uploading: 'uploading',
                uploaded: 'pending',
                converting: 'converting',
                completed: 'completed',
                failed: 'failed'
            };
            return classes[status] || 'pending';
        },

        getStatusText: function(status) {
            const texts = {
                pending: '等待中',
                uploading: '上传中',
                uploaded: '已上传',
                converting: '转换中',
                completed: '已完成',
                failed: '失败'
            };
            return texts[status] || '未知';
        },

        removeFile: function(index) {
            if (this.state.isConverting) return;
            this.state.files.splice(index, 1);
            this.renderFileList();
            
            if (this.state.files.length === 0) {
                const el = this.elements;
                if (el.optionsSection) el.optionsSection.style.display = 'none';
                if (el.fileListSection) el.fileListSection.style.display = 'none';
            }
        },

        clearFiles: function() {
            if (this.state.isConverting) return;
            this.state.files = [];
            const el = this.elements;
            if (el.fileList) el.fileList.innerHTML = '';
            if (el.optionsSection) el.optionsSection.style.display = 'none';
            if (el.fileListSection) el.fileListSection.style.display = 'none';
            if (el.fileInput) el.fileInput.value = '';
            App.showToast('已清空文件列表', 'info');
        },

        async startConversion() {
            if (this.state.files.length === 0) {
                App.showToast('请先添加文件', 'warning');
                return;
            }
            
            if (this.state.isConverting) {
                App.showToast('正在转换中，请等待', 'warning');
                return;
            }
            
            this.state.isConverting = true;
            const el = this.elements;
            if (el.startBtn) el.startBtn.disabled = true;
            
            if (el.fileListSection) el.fileListSection.style.display = 'none';
            if (el.optionsSection) el.optionsSection.style.display = 'none';
            if (el.progressSection) el.progressSection.style.display = 'block';
            
            try {
                const pdfTitle = el.pdfTitle ? el.pdfTitle.value.trim() || null : null;
                const formData = new FormData();
                if (pdfTitle) formData.append('pdf_title', pdfTitle);

                const response = await fetch(`/api/tasks/${this.state.taskId}/convert`, {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `转换失败: ${response.status}`);
                }

                App.showToast('开始转换...', 'info');
                this.startStatusPolling();
            } catch (error) {
                this.state.isConverting = false;
                if (el.startBtn) el.startBtn.disabled = false;
                if (el.fileListSection) el.fileListSection.style.display = 'block';
                if (el.optionsSection) el.optionsSection.style.display = 'block';
                if (el.progressSection) el.progressSection.style.display = 'none';
                App.showToast(`开始转换失败: ${error.message}`, 'error');
            }
        },

        async startStatusPolling() {
            const poll = async () => {
                const statusData = await this.getTaskStatus(this.state.taskId);
                if (statusData) {
                    this.updateProgress(statusData);
                    
                    if (['completed', 'partial_failed', 'failed'].includes(statusData.status)) {
                        this.stopStatusPolling();
                        this.state.isConverting = false;
                        const el = this.elements;
                        if (el.startBtn) el.startBtn.disabled = false;
                        this.showResults(statusData);
                    }
                }
            };
            
            await poll();
            this.state.statusPolling = setInterval(() => poll(), 1000);
        },

        stopStatusPolling() {
            if (this.state.statusPolling) {
                clearInterval(this.state.statusPolling);
                this.state.statusPolling = null;
            }
        },

        updateProgress(statusData) {
            const el = this.elements;
            const progress = Math.round(statusData.total_progress || 0);
            if (el.progressFill) el.progressFill.style.width = `${progress}%`;
            if (el.progressPercent) el.progressPercent.textContent = `${progress}%`;
            
            const statusTexts = {
                pending: '准备中...',
                processing: '转换中...',
                completed: '转换完成',
                partial_failed: '部分失败',
                failed: '转换失败'
            };
            if (el.progressStatus) el.progressStatus.textContent = statusTexts[statusData.status] || '处理中...';
            
            if (el.progressStats) {
                el.progressStats.innerHTML = `
                    <span><span class="stat-dot completed"></span> 成功: ${statusData.completed_count || 0}</span>
                    <span><span class="stat-dot failed"></span> 失败: ${statusData.failed_count || 0}</span>
                    <span><span class="stat-dot pending"></span> 总计: ${statusData.total_files || 0}</span>
                `;
            }
            
            this.state.files = statusData.files || [];
        },

        showResults(statusData) {
            this.state.lastTaskId = statusData.task_id || this.state.taskId;
            const el = this.elements;
            
            if (el.progressSection) el.progressSection.style.display = 'none';
            if (el.resultsSection) el.resultsSection.style.display = 'block';
            this.renderResults(statusData);
            
            const hasSuccess = (statusData.files || []).some(f => f.status === 'completed');
            if (el.downloadAllBtn) el.downloadAllBtn.style.display = hasSuccess ? 'inline-flex' : 'none';
            
            if (statusData.status === 'completed') {
                App.showToast('所有文件转换完成！', 'success');
            } else if (statusData.status === 'partial_failed') {
                App.showToast('部分文件转换失败', 'warning');
            } else {
                App.showToast('转换失败', 'error');
            }
        },

        renderResults(statusData) {
            const el = this.elements;
            if (!el.resultsList) return;
            
            const currentTaskId = statusData.task_id || this.state.taskId || this.state.lastTaskId;
            el.resultsList.innerHTML = '';
            
            (statusData.files || []).forEach((file, index) => {
                const isSuccess = file.status === 'completed';
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';
                
                const successIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="16 8 10 14 8 12"/></svg>';
                const failIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>';
                
                let actionsHtml = '';
                if (isSuccess && currentTaskId) {
                    const pdfName = file.original_name.replace(/\.[^.]+$/, '.pdf') || 'document.pdf';
                    actionsHtml = `
                        <button class="btn btn-primary" onclick="ConvertModule.previewFile('${currentTaskId}', '${file.id}', '${App.escapeHtml(pdfName)}')" title="预览">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                                <circle cx="12" cy="12" r="3"/>
                            </svg>
                            预览
                        </button>
                        <button class="btn btn-success" onclick="ConvertModule.downloadFile('${currentTaskId}', '${file.id}', '${App.escapeHtml(pdfName)}')" title="下载">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                <polyline points="7 10 12 15 17 10"/>
                                <line x1="12" y1="15" x2="12" y2="3"/>
                            </svg>
                            下载
                        </button>
                    `;
                }
                
                resultItem.innerHTML = `
                    <div class="result-icon ${isSuccess ? 'success' : 'failed'}">
                        ${isSuccess ? successIcon : failIcon}
                    </div>
                    <div class="result-info">
                        <div class="result-name">${App.escapeHtml(file.original_name)}</div>
                        <div class="result-message">${isSuccess ? '转换成功' : App.escapeHtml(file.error_message || '转换失败')}</div>
                    </div>
                    <div class="result-actions">${actionsHtml}</div>
                `;
                el.resultsList.appendChild(resultItem);
            });
        },

        resetForNewTask() {
            this.stopStatusPolling();
            this.state = {
                taskId: null,
                lastTaskId: null,
                files: [],
                isConverting: false,
                statusPolling: null
            };
            
            const el = this.elements;
            if (el.optionsSection) el.optionsSection.style.display = 'none';
            if (el.fileListSection) el.fileListSection.style.display = 'none';
            if (el.progressSection) el.progressSection.style.display = 'none';
            if (el.resultsSection) el.resultsSection.style.display = 'none';
            if (el.pdfTitle) el.pdfTitle.value = '';
            if (el.fileInput) el.fileInput.value = '';
            if (el.startBtn) el.startBtn.disabled = false;
            
            App.showToast('可以开始新任务了', 'info');
        }
    };

    const MergeModule = {
        state: {
            taskId: null,
            lastTaskId: null,
            files: [],
            isMerging: false,
            statusPolling: null,
            draggedIndex: null
        },

        elements: {},

        init: function() {
            this.cacheElements();
            this.bindEvents();
        },

        cacheElements: function() {
            this.elements = {
                uploadArea: document.getElementById('mergeUploadArea'),
                fileInput: document.getElementById('mergeFileInput'),
                selectFilesBtn: document.getElementById('mergeSelectFilesBtn'),
                fileListSection: document.getElementById('mergeFileListSection'),
                fileList: document.getElementById('mergeFileList'),
                clearBtn: document.getElementById('mergeClearBtn'),
                startBtn: document.getElementById('mergeStartBtn'),
                fileCount: document.getElementById('mergeFileCount'),
                mergeInfo: document.getElementById('mergeInfo'),
                progressSection: document.getElementById('mergeProgressSection'),
                progressFill: document.getElementById('mergeProgressFill'),
                progressPercent: document.getElementById('mergeProgressPercent'),
                progressStatus: document.getElementById('mergeProgressStatus'),
                resultsSection: document.getElementById('mergeResultsSection'),
                resultsList: document.getElementById('mergeResultsList'),
                newTaskBtn: document.getElementById('mergeNewTaskBtn')
            };
        },

        bindEvents: function() {
            const el = this.elements;
            if (el.selectFilesBtn) {
                el.selectFilesBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    el.fileInput.click();
                });
            }
            if (el.uploadArea) {
                el.uploadArea.addEventListener('click', () => el.fileInput.click());
                el.uploadArea.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    el.uploadArea.classList.add('drag-over');
                });
                el.uploadArea.addEventListener('dragleave', () => {
                    el.uploadArea.classList.remove('drag-over');
                });
                el.uploadArea.addEventListener('drop', (e) => {
                    e.preventDefault();
                    el.uploadArea.classList.remove('drag-over');
                    const files = Array.from(e.dataTransfer.files).filter(file => 
                        file.name.toLowerCase().endsWith('.pdf')
                    );
                    this.handleFiles(files);
                });
            }
            if (el.fileInput) {
                el.fileInput.addEventListener('change', (e) => {
                    this.handleFiles(Array.from(e.target.files));
                });
            }
            if (el.clearBtn) {
                el.clearBtn.addEventListener('click', () => this.clearFiles());
            }
            if (el.startBtn) {
                el.startBtn.addEventListener('click', () => this.startMerge());
            }
            if (el.newTaskBtn) {
                el.newTaskBtn.addEventListener('click', () => this.resetForNewTask());
            }
        },

        handleFiles: async function(selectedFiles) {
            if (selectedFiles.length === 0) return;

            const pdfFiles = selectedFiles.filter(f => f.name.toLowerCase().endsWith('.pdf'));
            if (pdfFiles.length < selectedFiles.length) {
                App.showToast('只支持PDF文件，其他文件已被忽略', 'warning');
            }

            if (pdfFiles.length === 0) {
                App.showToast('请选择PDF文件', 'warning');
                return;
            }

            if (!this.state.taskId) {
                const taskId = await App.createTask('merge');
                if (!taskId) return;
                this.state.taskId = taskId;
            }

            const el = this.elements;
            if (el.fileListSection) el.fileListSection.style.display = 'block';
            if (el.mergeInfo) el.mergeInfo.style.display = 'block';

            let successCount = 0;
            for (const file of pdfFiles) {
                const fileData = {
                    original_name: file.name,
                    file_size: file.size,
                    status: 'uploading',
                    id: Math.random().toString(36).substr(2, 9)
                };
                this.state.files.push(fileData);
                this.renderFileList();

                try {
                    const uploadResult = await App.uploadFile(this.state.taskId, file);
                    if (uploadResult) {
                        fileData.id = uploadResult.file_id;
                        fileData.status = 'uploaded';
                        successCount++;
                    } else {
                        fileData.status = 'failed';
                        App.showToast(`上传 ${file.name} 失败`, 'error');
                    }
                } catch (error) {
                    fileData.status = 'failed';
                    App.showToast(`上传 ${file.name} 失败: ${error.message}`, 'error');
                }
                this.renderFileList();
            }

            if (successCount > 0) {
                App.showToast(`已添加 ${successCount} 个 PDF 文件`, 'success');
            }
        },

        renderFileList: function() {
            const el = this.elements;
            if (!el.fileList) return;
            
            if (el.fileCount) el.fileCount.textContent = this.state.files.length;
            
            el.fileList.innerHTML = '';
            this.state.files.forEach((file, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.draggable = true;
                fileItem.dataset.index = index;
                
                fileItem.addEventListener('dragstart', (e) => this.onDragStart(e, index));
                fileItem.addEventListener('dragend', (e) => this.onDragEnd(e));
                fileItem.addEventListener('dragover', (e) => this.onDragOver(e));
                fileItem.addEventListener('drop', (e) => this.onDrop(e, index));
                
                fileItem.innerHTML = `
                    <div class="file-icon">${App.getFileIcon(file.original_name)}</div>
                    <div class="file-info">
                        <div class="file-name">${App.escapeHtml(file.original_name)}</div>
                        <div class="file-size">${App.formatFileSize(file.file_size)}</div>
                    </div>
                    <span class="file-order">第 ${index + 1} 个</span>
                    <div class="file-actions">
                        <button class="btn btn-outline" onclick="MergeModule.moveUp(${index})" title="上移" ${index === 0 || this.state.isMerging ? 'disabled' : ''}>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                                <polyline points="18 15 12 9 6 15"/>
                            </svg>
                        </button>
                        <button class="btn btn-outline" onclick="MergeModule.moveDown(${index})" title="下移" ${index === this.state.files.length - 1 || this.state.isMerging ? 'disabled' : ''}>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                                <polyline points="6 9 12 15 18 9"/>
                            </svg>
                        </button>
                        <button class="btn btn-outline" onclick="MergeModule.removeFile(${index})" title="移除" ${this.state.isMerging ? 'disabled' : ''}>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                                <line x1="18" y1="6" x2="6" y2="18"/>
                                <line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    </div>
                `;
                el.fileList.appendChild(fileItem);
            });
        },

        onDragStart: function(e, index) {
            this.state.draggedIndex = index;
            e.target.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        },

        onDragEnd: function(e) {
            e.target.classList.remove('dragging');
            this.state.draggedIndex = null;
        },

        onDragOver: function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            var item = e.target.closest('.file-item');
            if (item) item.classList.add('drag-over');
        },

        onDrop: function(e, targetIndex) {
            e.preventDefault();
            var item = e.target.closest('.file-item');
            if (item) item.classList.remove('drag-over');
            
            if (this.state.draggedIndex !== null && this.state.draggedIndex !== targetIndex) {
                const files = this.state.files;
                const [removed] = files.splice(this.state.draggedIndex, 1);
                files.splice(targetIndex, 0, removed);
                this.renderFileList();
                this.reorderOnServer();
            }
        },

        moveUp: function(index) {
            if (index === 0 || this.state.isMerging) return;
            const files = this.state.files;
            [files[index - 1], files[index]] = [files[index], files[index - 1]];
            this.renderFileList();
            this.reorderOnServer();
        },

        moveDown: function(index) {
            if (index === this.state.files.length - 1 || this.state.isMerging) return;
            const files = this.state.files;
            [files[index], files[index + 1]] = [files[index + 1], files[index]];
            this.renderFileList();
            this.reorderOnServer();
        },

        removeFile: function(index) {
            if (this.state.isMerging) return;
            this.state.files.splice(index, 1);
            this.renderFileList();
            
            if (this.state.files.length === 0) {
                const el = this.elements;
                if (el.fileListSection) el.fileListSection.style.display = 'none';
                if (el.mergeInfo) el.mergeInfo.style.display = 'none';
            }
        },

        reorderOnServer: async function() {
            if (!this.state.taskId) return;
            
            const order = this.state.files.map(f => f.id);
            try {
                await fetch(`/api/features/tasks/${this.state.taskId}/reorder`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ order })
                });
            } catch (error) {
                console.error('Reorder failed:', error);
            }
        },

        clearFiles: function() {
            if (this.state.isMerging) return;
            this.state.files = [];
            const el = this.elements;
            if (el.fileList) el.fileList.innerHTML = '';
            if (el.fileListSection) el.fileListSection.style.display = 'none';
            if (el.mergeInfo) el.mergeInfo.style.display = 'none';
            if (el.fileInput) el.fileInput.value = '';
            App.showToast('已清空文件列表', 'info');
        },

        startMerge: async function() {
            if (this.state.files.length < 2) {
                App.showToast('至少需要2个PDF文件才能合并', 'warning');
                return;
            }

            if (this.state.isMerging) {
                App.showToast('正在合并中，请等待', 'warning');
                return;
            }

            this.state.isMerging = true;
            const el = this.elements;
            if (el.startBtn) el.startBtn.disabled = true;

            if (el.fileListSection) el.fileListSection.style.display = 'none';
            if (el.progressSection) el.progressSection.style.display = 'block';

            try {
                const order = this.state.files.map(f => f.id);
                const response = await fetch(`/api/features/tasks/${this.state.taskId}/merge`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ order })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `合并失败: ${response.status}`);
                }

                App.showToast('开始合并...', 'info');
                this.startStatusPolling();
            } catch (error) {
                this.state.isMerging = false;
                if (el.startBtn) el.startBtn.disabled = false;
                if (el.fileListSection) el.fileListSection.style.display = 'block';
                if (el.progressSection) el.progressSection.style.display = 'none';
                App.showToast(`开始合并失败: ${error.message}`, 'error');
            }
        },

        async startStatusPolling() {
            const poll = async () => {
                const statusData = await App.getTaskStatus(this.state.taskId);
                if (statusData) {
                    this.updateProgress(statusData);
                    
                    if (['completed', 'failed'].includes(statusData.status)) {
                        this.stopStatusPolling();
                        this.state.isMerging = false;
                        this.showResults(statusData);
                    }
                }
            };
            
            await poll();
            this.state.statusPolling = setInterval(() => poll(), 1000);
        },

        stopStatusPolling() {
            if (this.state.statusPolling) {
                clearInterval(this.state.statusPolling);
                this.state.statusPolling = null;
            }
        },

        updateProgress(statusData) {
            const el = this.elements;
            const progress = Math.round(statusData.total_progress || 0);
            if (el.progressFill) el.progressFill.style.width = `${progress}%`;
            if (el.progressPercent) el.progressPercent.textContent = `${progress}%`;
            
            const statusTexts = {
                pending: '准备中...',
                processing: '合并中...',
                completed: '合并完成',
                failed: '合并失败'
            };
            if (el.progressStatus) el.progressStatus.textContent = statusTexts[statusData.status] || '处理中...';
        },

        showResults(statusData) {
            this.state.lastTaskId = statusData.task_id || this.state.taskId;
            const el = this.elements;
            
            if (el.progressSection) el.progressSection.style.display = 'none';
            if (el.resultsSection) el.resultsSection.style.display = 'block';
            this.renderResults(statusData);
            
            if (statusData.status === 'completed') {
                App.showToast('PDF合并完成！', 'success');
            } else {
                App.showToast('合并失败', 'error');
            }
        },

        renderResults(statusData) {
            const el = this.elements;
            if (!el.resultsList) return;
            
            const currentTaskId = statusData.task_id || this.state.taskId || this.state.lastTaskId;
            el.resultsList.innerHTML = '';
            
            const outputs = statusData.outputs || [];
            outputs.forEach((output) => {
                const isSuccess = true;
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';
                
                const successIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="16 8 10 14 8 12"/></svg>';
                
                let actionsHtml = '';
                if (currentTaskId) {
                    actionsHtml = `
                        <button class="btn btn-primary" onclick="App.previewFile('${currentTaskId}', '${output.id}', '${App.escapeHtml(output.filename)}')" title="预览">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                                <circle cx="12" cy="12" r="3"/>
                            </svg>
                            预览
                        </button>
                        <button class="btn btn-success" onclick="App.downloadFile('${currentTaskId}', '${output.id}', '${App.escapeHtml(output.filename)}')" title="下载">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                <polyline points="7 10 12 15 17 10"/>
                                <line x1="12" y1="15" x2="12" y2="3"/>
                            </svg>
                            下载
                        </button>
                    `;
                }
                
                resultItem.innerHTML = `
                    <div class="result-icon success">
                        ${successIcon}
                    </div>
                    <div class="result-info">
                        <div class="result-name">${App.escapeHtml(output.filename)}</div>
                        <div class="result-message">合并成功 - ${App.formatFileSize(output.size || 0)}</div>
                    </div>
                    <div class="result-actions">${actionsHtml}</div>
                `;
                el.resultsList.appendChild(resultItem);
            });
        },

        resetForNewTask() {
            this.stopStatusPolling();
            this.state = {
                taskId: null,
                lastTaskId: null,
                files: [],
                isMerging: false,
                statusPolling: null,
                draggedIndex: null
            };
            
            const el = this.elements;
            if (el.fileListSection) el.fileListSection.style.display = 'none';
            if (el.mergeInfo) el.mergeInfo.style.display = 'none';
            if (el.progressSection) el.progressSection.style.display = 'none';
            if (el.resultsSection) el.resultsSection.style.display = 'none';
            if (el.fileInput) el.fileInput.value = '';
            if (el.startBtn) el.startBtn.disabled = false;
            
            App.showToast('可以开始新任务了', 'info');
        }
    };

    const SplitModule = {
        state: {
            taskId: null,
            lastTaskId: null,
            file: null,
            pdfInfo: null,
            isSplitting: false,
            statusPolling: null,
            splitMode: 'range'
        },

        elements: {},

        init: function() {
            this.cacheElements();
            this.bindEvents();
        },

        cacheElements: function() {
            this.elements = {
                uploadArea: document.getElementById('splitUploadArea'),
                fileInput: document.getElementById('splitFileInput'),
                selectFilesBtn: document.getElementById('splitSelectFilesBtn'),
                optionsSection: document.getElementById('splitOptionsSection'),
                fileName: document.getElementById('splitFileName'),
                fileSize: document.getElementById('splitFileSize'),
                pageCount: document.getElementById('splitPageCount'),
                pageSize: document.getElementById('splitPageSize'),
                modeRadios: document.querySelectorAll('input[name="splitMode"]'),
                rangeOption: document.getElementById('splitRangeOption'),
                pagesOption: document.getElementById('splitPagesOption'),
                everyNOption: document.getElementById('splitEveryNOption'),
                rangeInputs: document.getElementById('splitRangeInputs'),
                addRangeBtn: document.getElementById('splitAddRange'),
                pagesInput: document.getElementById('splitPagesInput'),
                everyNInput: document.getElementById('splitEveryNInput'),
                outputPrefix: document.getElementById('splitOutputPrefix'),
                startBtn: document.getElementById('splitStartBtn'),
                progressSection: document.getElementById('splitProgressSection'),
                progressFill: document.getElementById('splitProgressFill'),
                progressPercent: document.getElementById('splitProgressPercent'),
                progressStatus: document.getElementById('splitProgressStatus'),
                resultsSection: document.getElementById('splitResultsSection'),
                resultsList: document.getElementById('splitResultsList'),
                downloadAllBtn: document.getElementById('splitDownloadAllBtn'),
                newTaskBtn: document.getElementById('splitNewTaskBtn')
            };
        },

        bindEvents: function() {
            const el = this.elements;
            if (el.selectFilesBtn) {
                el.selectFilesBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    el.fileInput.click();
                });
            }
            if (el.uploadArea) {
                el.uploadArea.addEventListener('click', () => el.fileInput.click());
                el.uploadArea.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    el.uploadArea.classList.add('drag-over');
                });
                el.uploadArea.addEventListener('dragleave', () => {
                    el.uploadArea.classList.remove('drag-over');
                });
                el.uploadArea.addEventListener('drop', (e) => {
                    e.preventDefault();
                    el.uploadArea.classList.remove('drag-over');
                    const files = Array.from(e.dataTransfer.files).filter(file => 
                        file.name.toLowerCase().endsWith('.pdf')
                    );
                    if (files.length > 0) this.handleFile(files[0]);
                });
            }
            if (el.fileInput) {
                el.fileInput.addEventListener('change', (e) => {
                    const files = Array.from(e.target.files);
                    if (files.length > 0) this.handleFile(files[0]);
                });
            }
            if (el.modeRadios) {
                el.modeRadios.forEach(radio => {
                    radio.addEventListener('change', (e) => this.onModeChange(e.target.value));
                });
            }
            if (el.addRangeBtn) {
                el.addRangeBtn.addEventListener('click', () => this.addRangeInput());
            }
            if (el.startBtn) {
                el.startBtn.addEventListener('click', () => this.startSplit());
            }
            if (el.downloadAllBtn) {
                el.downloadAllBtn.addEventListener('click', () => {
                    const taskId = this.state.lastTaskId || this.state.taskId;
                    if (taskId) App.downloadZip(taskId);
                });
            }
            if (el.newTaskBtn) {
                el.newTaskBtn.addEventListener('click', () => this.resetForNewTask());
            }
        },

        handleFile: async function(file) {
            if (!file.name.toLowerCase().endsWith('.pdf')) {
                App.showToast('只支持PDF文件', 'warning');
                return;
            }

            if (!this.state.taskId) {
                const taskId = await App.createTask('split');
                if (!taskId) return;
                this.state.taskId = taskId;
            }

            this.state.file = {
                original_name: file.name,
                file_size: file.size,
                status: 'uploading'
            };

            try {
                const uploadResult = await App.uploadFile(this.state.taskId, file);
                if (uploadResult) {
                    this.state.file.id = uploadResult.file_id;
                    this.state.file.status = 'uploaded';
                    
                    const pdfInfo = await App.getPdfInfo(this.state.taskId);
                    if (pdfInfo) {
                        this.state.pdfInfo = pdfInfo;
                        this.updatePdfInfo();
                    }
                    
                    const el = this.elements;
                    if (el.optionsSection) el.optionsSection.style.display = 'block';
                    App.showToast('PDF文件上传成功', 'success');
                }
            } catch (error) {
                this.state.file.status = 'failed';
                App.showToast(`上传失败: ${error.message}`, 'error');
            }
        },

        updatePdfInfo: function() {
            const el = this.elements;
            const info = this.state.pdfInfo;
            if (!info) return;

            if (el.fileName) el.fileName.textContent = info.filename || '-';
            if (el.fileSize) el.fileSize.textContent = App.formatFileSize(info.file_size || info.size || 0);
            if (el.pageCount) el.pageCount.textContent = info.page_count || '-';
            if (el.pageSize && info.page_size) {
                el.pageSize.textContent = `${info.page_size.width.toFixed(0)} x ${info.page_size.height.toFixed(0)} pt`;
            }
        },

        onModeChange: function(mode) {
            this.state.splitMode = mode;
            const el = this.elements;
            
            document.querySelectorAll('.split-mode-item').forEach(item => {
                item.classList.remove('active');
                const radio = item.querySelector('input[type="radio"]');
                if (radio && radio.value === mode) {
                    item.classList.add('active');
                }
            });

            if (el.rangeOption) el.rangeOption.style.display = mode === 'range' ? 'block' : 'none';
            if (el.pagesOption) el.pagesOption.style.display = mode === 'pages' ? 'block' : 'none';
            if (el.everyNOption) el.everyNOption.style.display = mode === 'every_n' ? 'block' : 'none';
        },

        addRangeInput: function() {
            const el = this.elements;
            if (!el.rangeInputs) return;

            const row = document.createElement('div');
            row.className = 'range-input-row';
            row.innerHTML = `
                <input type="number" class="form-input range-start" placeholder="起始页" min="1">
                <span class="range-separator">-</span>
                <input type="number" class="form-input range-end" placeholder="结束页" min="1">
                <button class="btn btn-outline remove-range" type="button" onclick="SplitModule.removeRangeInput(this)">-</button>
            `;
            el.rangeInputs.appendChild(row);
        },

        removeRangeInput: function(btn) {
            const row = btn.closest('.range-input-row');
            const el = this.elements;
            if (row && el.rangeInputs && el.rangeInputs.children.length > 1) {
                row.remove();
            }
        },

        getSplitRequest: function() {
            const el = this.elements;
            const mode = this.state.splitMode;
            const request = {
                mode: mode,
                output_prefix: el.outputPrefix ? el.outputPrefix.value.trim() || null : null
            };

            if (mode === 'range') {
                const rangeRows = document.querySelectorAll('.range-input-row');
                request.ranges = [];
                rangeRows.forEach(row => {
                    var startInput = row.querySelector('.range-start');
                    var endInput = row.querySelector('.range-end');
                    var start = startInput ? startInput.value : null;
                    var end = endInput ? endInput.value : null;
                    if (start && end) {
                        request.ranges.push({ start: parseInt(start), end: parseInt(end) });
                    }
                });
            } else if (mode === 'pages') {
                var pagesText = el.pagesInput ? el.pagesInput.value : '';
                request.pages = pagesText.split(',').map(function(p) { return p.trim(); }).filter(function(p) { return p; });
            } else if (mode === 'every_n') {
                var everyNValue = el.everyNInput ? el.everyNInput.value : '1';
                request.every_n = parseInt(everyNValue || '1');
            }

            return request;
        },

        validateSplitRequest: function() {
            const request = this.getSplitRequest();
            var pageCount = this.state.pdfInfo ? this.state.pdfInfo.page_count : 0;
            pageCount = pageCount || 0;

            if (!this.state.pdfInfo) {
                App.showToast('请先上传PDF文件', 'warning');
                return false;
            }

            if (request.mode === 'range') {
                if (!request.ranges || request.ranges.length === 0) {
                    App.showToast('请至少添加一个拆分范围', 'warning');
                    return false;
                }
                for (const range of request.ranges) {
                    if (range.start < 1 || range.end > pageCount) {
                        App.showToast(`页码范围超出范围（1 - ${pageCount}）`, 'warning');
                        return false;
                    }
                    if (range.start > range.end) {
                        App.showToast('起始页不能大于结束页', 'warning');
                        return false;
                    }
                }
            } else if (request.mode === 'pages') {
                if (!request.pages || request.pages.length === 0) {
                    App.showToast('请输入要拆分的页码', 'warning');
                    return false;
                }
            } else if (request.mode === 'every_n') {
                if (!request.every_n || request.every_n < 1) {
                    App.showToast('请输入有效的每N页数值', 'warning');
                    return false;
                }
            }

            return true;
        },

        startSplit: async function() {
            if (!this.validateSplitRequest()) return;

            if (this.state.isSplitting) {
                App.showToast('正在拆分中，请等待', 'warning');
                return;
            }

            this.state.isSplitting = true;
            const el = this.elements;
            if (el.startBtn) el.startBtn.disabled = true;

            if (el.optionsSection) el.optionsSection.style.display = 'none';
            if (el.progressSection) el.progressSection.style.display = 'block';

            try {
                const request = this.getSplitRequest();
                const response = await fetch(`/api/features/tasks/${this.state.taskId}/split`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(request)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `拆分失败: ${response.status}`);
                }

                App.showToast('开始拆分...', 'info');
                this.startStatusPolling();
            } catch (error) {
                this.state.isSplitting = false;
                if (el.startBtn) el.startBtn.disabled = false;
                if (el.optionsSection) el.optionsSection.style.display = 'block';
                if (el.progressSection) el.progressSection.style.display = 'none';
                App.showToast(`开始拆分失败: ${error.message}`, 'error');
            }
        },

        async startStatusPolling() {
            const poll = async () => {
                const statusData = await App.getTaskStatus(this.state.taskId);
                if (statusData) {
                    this.updateProgress(statusData);
                    
                    if (['completed', 'failed'].includes(statusData.status)) {
                        this.stopStatusPolling();
                        this.state.isSplitting = false;
                        this.showResults(statusData);
                    }
                }
            };
            
            await poll();
            this.state.statusPolling = setInterval(() => poll(), 1000);
        },

        stopStatusPolling() {
            if (this.state.statusPolling) {
                clearInterval(this.state.statusPolling);
                this.state.statusPolling = null;
            }
        },

        updateProgress(statusData) {
            const el = this.elements;
            const progress = Math.round(statusData.total_progress || 0);
            if (el.progressFill) el.progressFill.style.width = `${progress}%`;
            if (el.progressPercent) el.progressPercent.textContent = `${progress}%`;
            
            const statusTexts = {
                pending: '准备中...',
                processing: '拆分中...',
                completed: '拆分完成',
                failed: '拆分失败'
            };
            if (el.progressStatus) el.progressStatus.textContent = statusTexts[statusData.status] || '处理中...';
        },

        showResults(statusData) {
            this.state.lastTaskId = statusData.task_id || this.state.taskId;
            const el = this.elements;
            
            if (el.progressSection) el.progressSection.style.display = 'none';
            if (el.resultsSection) el.resultsSection.style.display = 'block';
            this.renderResults(statusData);
            
            if (statusData.status === 'completed') {
                App.showToast('PDF拆分完成！', 'success');
            } else {
                App.showToast('拆分失败', 'error');
            }
        },

        renderResults(statusData) {
            const el = this.elements;
            if (!el.resultsList) return;
            
            const currentTaskId = statusData.task_id || this.state.taskId || this.state.lastTaskId;
            el.resultsList.innerHTML = '';
            
            const outputs = statusData.outputs || [];
            outputs.forEach((output, index) => {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';
                
                const successIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="16 8 10 14 8 12"/></svg>';
                
                let actionsHtml = '';
                if (currentTaskId) {
                    actionsHtml = `
                        <button class="btn btn-primary" onclick="App.previewFile('${currentTaskId}', '${output.id}', '${App.escapeHtml(output.filename)}')" title="预览">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                                <circle cx="12" cy="12" r="3"/>
                            </svg>
                            预览
                        </button>
                        <button class="btn btn-success" onclick="App.downloadFile('${currentTaskId}', '${output.id}', '${App.escapeHtml(output.filename)}')" title="下载">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                <polyline points="7 10 12 15 17 10"/>
                                <line x1="12" y1="15" x2="12" y2="3"/>
                            </svg>
                            下载
                        </button>
                    `;
                }
                
                resultItem.innerHTML = `
                    <div class="result-icon success">
                        ${successIcon}
                    </div>
                    <div class="result-info">
                        <div class="result-name">${App.escapeHtml(output.filename)}</div>
                        <div class="result-message">拆分成功 - ${App.formatFileSize(output.size || 0)}</div>
                    </div>
                    <div class="result-actions">${actionsHtml}</div>
                `;
                el.resultsList.appendChild(resultItem);
            });
        },

        resetForNewTask() {
            this.stopStatusPolling();
            this.state = {
                taskId: null,
                lastTaskId: null,
                file: null,
                pdfInfo: null,
                isSplitting: false,
                statusPolling: null,
                splitMode: 'range'
            };
            
            const el = this.elements;
            if (el.optionsSection) el.optionsSection.style.display = 'none';
            if (el.progressSection) el.progressSection.style.display = 'none';
            if (el.resultsSection) el.resultsSection.style.display = 'none';
            if (el.fileInput) el.fileInput.value = '';
            if (el.pagesInput) el.pagesInput.value = '';
            if (el.everyNInput) el.everyNInput.value = '1';
            if (el.outputPrefix) el.outputPrefix.value = '';
            if (el.startBtn) el.startBtn.disabled = false;
            
            const rangeInputs = el.rangeInputs;
            if (rangeInputs) {
                rangeInputs.innerHTML = `
                    <div class="range-input-row">
                        <input type="number" class="form-input range-start" placeholder="起始页" min="1">
                        <span class="range-separator">-</span>
                        <input type="number" class="form-input range-end" placeholder="结束页" min="1">
                        <button class="btn btn-outline remove-range" type="button" onclick="SplitModule.removeRangeInput(this)">-</button>
                    </div>
                `;
            }
            
            App.showToast('可以开始新任务了', 'info');
        }
    };

    const CompressModule = {
        state: {
            taskId: null,
            lastTaskId: null,
            file: null,
            pdfInfo: null,
            isCompressing: false,
            statusPolling: null,
            compressLevel: 'medium'
        },

        elements: {},

        init: function() {
            this.cacheElements();
            this.bindEvents();
        },

        cacheElements: function() {
            this.elements = {
                uploadArea: document.getElementById('compressUploadArea'),
                fileInput: document.getElementById('compressFileInput'),
                selectFilesBtn: document.getElementById('compressSelectFilesBtn'),
                optionsSection: document.getElementById('compressOptionsSection'),
                fileName: document.getElementById('compressFileName'),
                fileSize: document.getElementById('compressFileSize'),
                pageCount: document.getElementById('compressPageCount'),
                levelRadios: document.querySelectorAll('input[name="compressLevel"]'),
                startBtn: document.getElementById('compressStartBtn'),
                progressSection: document.getElementById('compressProgressSection'),
                progressFill: document.getElementById('compressProgressFill'),
                progressPercent: document.getElementById('compressProgressPercent'),
                progressStatus: document.getElementById('compressProgressStatus'),
                resultsSection: document.getElementById('compressResultsSection'),
                resultsList: document.getElementById('compressResultsList'),
                newTaskBtn: document.getElementById('compressNewTaskBtn')
            };
        },

        bindEvents: function() {
            const el = this.elements;
            if (el.selectFilesBtn) {
                el.selectFilesBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    el.fileInput.click();
                });
            }
            if (el.uploadArea) {
                el.uploadArea.addEventListener('click', () => el.fileInput.click());
                el.uploadArea.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    el.uploadArea.classList.add('drag-over');
                });
                el.uploadArea.addEventListener('dragleave', () => {
                    el.uploadArea.classList.remove('drag-over');
                });
                el.uploadArea.addEventListener('drop', (e) => {
                    e.preventDefault();
                    el.uploadArea.classList.remove('drag-over');
                    const files = Array.from(e.dataTransfer.files).filter(file => 
                        file.name.toLowerCase().endsWith('.pdf')
                    );
                    if (files.length > 0) this.handleFile(files[0]);
                });
            }
            if (el.fileInput) {
                el.fileInput.addEventListener('change', (e) => {
                    const files = Array.from(e.target.files);
                    if (files.length > 0) this.handleFile(files[0]);
                });
            }
            if (el.levelRadios) {
                el.levelRadios.forEach(radio => {
                    radio.addEventListener('change', (e) => {
                        this.state.compressLevel = e.target.value;
                        document.querySelectorAll('.compress-level-item').forEach(item => {
                            item.classList.remove('active');
                            const r = item.querySelector('input[type="radio"]');
                            if (r && r.value === e.target.value) {
                                item.classList.add('active');
                            }
                        });
                    });
                });
            }
            if (el.startBtn) {
                el.startBtn.addEventListener('click', () => this.startCompress());
            }
            if (el.newTaskBtn) {
                el.newTaskBtn.addEventListener('click', () => this.resetForNewTask());
            }
        },

        handleFile: async function(file) {
            if (!file.name.toLowerCase().endsWith('.pdf')) {
                App.showToast('只支持PDF文件', 'warning');
                return;
            }

            if (!this.state.taskId) {
                const taskId = await App.createTask('compress');
                if (!taskId) return;
                this.state.taskId = taskId;
            }

            this.state.file = {
                original_name: file.name,
                file_size: file.size,
                status: 'uploading'
            };

            try {
                const uploadResult = await App.uploadFile(this.state.taskId, file);
                if (uploadResult) {
                    this.state.file.id = uploadResult.file_id;
                    this.state.file.status = 'uploaded';
                    
                    const pdfInfo = await App.getPdfInfo(this.state.taskId);
                    if (pdfInfo) {
                        this.state.pdfInfo = pdfInfo;
                        this.updatePdfInfo();
                    }
                    
                    const el = this.elements;
                    if (el.optionsSection) el.optionsSection.style.display = 'block';
                    App.showToast('PDF文件上传成功', 'success');
                }
            } catch (error) {
                this.state.file.status = 'failed';
                App.showToast(`上传失败: ${error.message}`, 'error');
            }
        },

        updatePdfInfo: function() {
            const el = this.elements;
            const info = this.state.pdfInfo;
            if (!info) return;

            if (el.fileName) el.fileName.textContent = info.filename || '-';
            if (el.fileSize) el.fileSize.textContent = App.formatFileSize(info.file_size || info.size || 0);
            if (el.pageCount) el.pageCount.textContent = info.page_count || '-';
        },

        startCompress: async function() {
            if (!this.state.pdfInfo) {
                App.showToast('请先上传PDF文件', 'warning');
                return;
            }

            if (this.state.isCompressing) {
                App.showToast('正在压缩中，请等待', 'warning');
                return;
            }

            this.state.isCompressing = true;
            const el = this.elements;
            if (el.startBtn) el.startBtn.disabled = true;

            if (el.optionsSection) el.optionsSection.style.display = 'none';
            if (el.progressSection) el.progressSection.style.display = 'block';

            try {
                const response = await fetch(`/api/features/tasks/${this.state.taskId}/compress`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ level: this.state.compressLevel })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `压缩失败: ${response.status}`);
                }

                App.showToast('开始压缩...', 'info');
                this.startStatusPolling();
            } catch (error) {
                this.state.isCompressing = false;
                if (el.startBtn) el.startBtn.disabled = false;
                if (el.optionsSection) el.optionsSection.style.display = 'block';
                if (el.progressSection) el.progressSection.style.display = 'none';
                App.showToast(`开始压缩失败: ${error.message}`, 'error');
            }
        },

        async startStatusPolling() {
            const poll = async () => {
                const statusData = await App.getTaskStatus(this.state.taskId);
                if (statusData) {
                    this.updateProgress(statusData);
                    
                    if (['completed', 'failed'].includes(statusData.status)) {
                        this.stopStatusPolling();
                        this.state.isCompressing = false;
                        this.showResults(statusData);
                    }
                }
            };
            
            await poll();
            this.state.statusPolling = setInterval(() => poll(), 1000);
        },

        stopStatusPolling() {
            if (this.state.statusPolling) {
                clearInterval(this.state.statusPolling);
                this.state.statusPolling = null;
            }
        },

        updateProgress(statusData) {
            const el = this.elements;
            const progress = Math.round(statusData.total_progress || 0);
            if (el.progressFill) el.progressFill.style.width = `${progress}%`;
            if (el.progressPercent) el.progressPercent.textContent = `${progress}%`;
            
            const statusTexts = {
                pending: '准备中...',
                processing: '压缩中...',
                completed: '压缩完成',
                failed: '压缩失败'
            };
            if (el.progressStatus) el.progressStatus.textContent = statusTexts[statusData.status] || '处理中...';
        },

        showResults(statusData) {
            this.state.lastTaskId = statusData.task_id || this.state.taskId;
            const el = this.elements;
            
            if (el.progressSection) el.progressSection.style.display = 'none';
            if (el.resultsSection) el.resultsSection.style.display = 'block';
            if (el.startBtn) el.startBtn.disabled = false;
            
            this.renderResults(statusData);
            
            if (statusData.status === 'completed') {
                App.showToast('PDF压缩完成！', 'success');
            } else {
                App.showToast('压缩失败', 'error');
            }
        },

        renderResults(statusData) {
            const el = this.elements;
            if (!el.resultsList) return;
            
            const currentTaskId = statusData.task_id || this.state.taskId || this.state.lastTaskId;
            el.resultsList.innerHTML = '';
            
            const outputs = statusData.outputs || [];
            var originalSize = 0;
            if (this.state.pdfInfo) {
                originalSize = this.state.pdfInfo.file_size || this.state.pdfInfo.size || 0;
            }
            originalSize = originalSize || 0;
            
            outputs.forEach((output) => {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';
                
                const successIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="16 8 10 14 8 12"/></svg>';
                
                const compressedSize = output.file_size || output.size || 0;
                const savedPercent = originalSize > 0 ? Math.round((1 - compressedSize / originalSize) * 100) : 0;
                
                let actionsHtml = '';
                if (currentTaskId) {
                    actionsHtml = `
                        <button class="btn btn-primary" onclick="App.previewFile('${currentTaskId}', '${output.id}', '${App.escapeHtml(output.filename)}')" title="预览">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                                <circle cx="12" cy="12" r="3"/>
                            </svg>
                            预览
                        </button>
                        <button class="btn btn-success" onclick="App.downloadFile('${currentTaskId}', '${output.id}', '${App.escapeHtml(output.filename)}')" title="下载">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                <polyline points="7 10 12 15 17 10"/>
                                <line x1="12" y1="15" x2="12" y2="3"/>
                            </svg>
                            下载
                        </button>
                    `;
                }
                
                resultItem.innerHTML = `
                    <div class="result-icon success">
                        ${successIcon}
                    </div>
                    <div class="result-info">
                        <div class="result-name">${App.escapeHtml(output.filename)}</div>
                        <div class="result-message">
                            原大小: ${App.formatFileSize(originalSize)} → 压缩后: ${App.formatFileSize(compressedSize)}
                            ${savedPercent > 0 ? `<span style="color: #10b981; font-weight: bold; margin-left: 8px;">节省 ${savedPercent}%</span>` : ''}
                        </div>
                    </div>
                    <div class="result-actions">${actionsHtml}</div>
                `;
                el.resultsList.appendChild(resultItem);
            });
        },

        resetForNewTask() {
            this.stopStatusPolling();
            this.state = {
                taskId: null,
                lastTaskId: null,
                file: null,
                pdfInfo: null,
                isCompressing: false,
                statusPolling: null,
                compressLevel: 'medium'
            };
            
            const el = this.elements;
            if (el.optionsSection) el.optionsSection.style.display = 'none';
            if (el.progressSection) el.progressSection.style.display = 'none';
            if (el.resultsSection) el.resultsSection.style.display = 'none';
            if (el.fileInput) el.fileInput.value = '';
            if (el.startBtn) el.startBtn.disabled = false;
            
            App.showToast('可以开始新任务了', 'info');
        }
    };

    window.App = App;
    window.ConvertModule = ConvertModule;
    window.MergeModule = MergeModule;
    window.SplitModule = SplitModule;
    window.CompressModule = CompressModule;

    document.addEventListener('DOMContentLoaded', function() {
        App.init();
    });
})();