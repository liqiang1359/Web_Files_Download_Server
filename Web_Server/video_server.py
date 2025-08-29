from flask import Flask, send_file, jsonify, abort, request, render_template_string
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# 文件目录
VIDEO_DIR = r'./files'

# 支持的文件类型
FILE_TYPES = {
    '音视频文件': {
        'extensions': ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'm4v', '3gp', 'webm', 'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma'],
        'icon': '🎬',
        'color': '#ff6b6b'
    },
    '文档文件': {
        'extensions': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'pages', 'xls', 'xlsx', 'csv', 'ods', 'ppt', 'pptx', 'odp', 'key'],
        'icon': '📄',
        'color': '#4ecdc4'
    },
    '图片文件': {
        'extensions': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg', 'webp'],
        'icon': '🖼️',
        'color': '#45b7d1'
    },
    '其他文件': {
        'extensions': ['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'js', 'py', 'html', 'css', 'json', 'xml', 'java', 'cpp', 'c'],
        'icon': '📦',
        'color': '#96ceb4'
    }
}

def allowed_file(filename, file_type=None):
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if file_type and file_type in FILE_TYPES:
        return extension in FILE_TYPES[file_type]['extensions']
    
    # 检查是否在任何类型中
    for type_info in FILE_TYPES.values():
        if extension in type_info['extensions']:
            return True
    return False

def get_file_type(filename):
    if '.' not in filename:
        return '未知文件'
    
    extension = filename.rsplit('.', 1)[1].lower()
    for type_name, type_info in FILE_TYPES.items():
        if extension in type_info['extensions']:
            return type_name
    return '其他文件'

@app.route('/')
def index():
    upload_page = '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>文件上传管理系统</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .header {
                text-align: center;
                color: white;
                margin-bottom: 40px;
            }
            
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            
            .main-content {
                display: grid;
                grid-template-columns: 1fr 2fr;
                gap: 30px;
                margin-bottom: 30px;
            }
            
            @media (max-width: 768px) {
                .main-content {
                    grid-template-columns: 1fr;
                }
            }
            
            .card {
                background: white;
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .card-header {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 20px;
                font-weight: 600;
                font-size: 1.2rem;
            }
            
            .card-body {
                padding: 30px;
            }
            
            /* 文件类型选择 */
            .file-types {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .file-type-option {
                padding: 15px;
                border: 2px solid #e1e8ed;
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
                text-align: center;
                position: relative;
            }
            
            .file-type-option:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            
            .file-type-option.selected {
                border-color: #4facfe;
                background: linear-gradient(135deg, #4facfe15, #00f2fe15);
            }
            
            .file-type-icon {
                font-size: 2rem;
                margin-bottom: 8px;
                display: block;
            }
            
            .file-type-name {
                font-weight: 600;
                font-size: 0.9rem;
                margin-bottom: 4px;
            }
            
            .file-type-exts {
                font-size: 0.75rem;
                color: #666;
                line-height: 1.4;
            }
            
            /* 上传区域 */
            .upload-area {
                border: 3px dashed #ddd;
                border-radius: 16px;
                padding: 60px 20px;
                text-align: center;
                transition: all 0.3s ease;
                position: relative;
                background: #fafafa;
            }
            
            .upload-area.dragover {
                border-color: #4facfe;
                background: linear-gradient(135deg, #4facfe10, #00f2fe10);
                transform: scale(1.02);
            }
            
            .upload-icon {
                font-size: 4rem;
                color: #ccc;
                margin-bottom: 20px;
            }
            
            .upload-text {
                font-size: 1.2rem;
                color: #666;
                margin-bottom: 10px;
            }
            
            .upload-hint {
                color: #999;
                font-size: 0.9rem;
            }
            
            .file-input {
                display: none;
            }
            
            .upload-btn {
                background: linear-gradient(135deg, #4facfe, #00f2fe);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 20px;
            }
            
            .upload-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(79, 172, 254, 0.3);
            }
            
            /* 文件列表 */
            .file-list {
                margin-top: 30px;
            }
            
            .file-item {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 15px;
                border: 1px solid #e1e8ed;
                border-radius: 10px;
                margin-bottom: 10px;
                background: white;
                transition: all 0.3s ease;
            }
            
            .file-item:hover {
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .file-info {
                display: flex;
                align-items: center;
                flex: 1;
            }
            
            .file-icon {
                font-size: 1.5rem;
                margin-right: 12px;
            }
            
            .file-details h4 {
                margin: 0 0 4px 0;
                font-size: 0.9rem;
                color: #333;
            }
            
            .file-details p {
                margin: 0;
                font-size: 0.8rem;
                color: #666;
            }
            
            .file-progress {
                flex: 1;
                margin: 0 20px;
            }
            
            .progress-bar {
                width: 100%;
                height: 6px;
                background: #e1e8ed;
                border-radius: 3px;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #4facfe, #00f2fe);
                transition: width 0.3s ease;
                border-radius: 3px;
            }
            
            .progress-text {
                font-size: 0.75rem;
                color: #666;
                margin-top: 4px;
            }
            
            .file-actions {
                display: flex;
                gap: 10px;
            }
            
            .btn-small {
                padding: 6px 12px;
                border: none;
                border-radius: 15px;
                font-size: 0.8rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn-remove {
                background: #ff6b6b;
                color: white;
            }
            
            .btn-remove:hover {
                background: #ff5252;
                transform: translateY(-1px);
            }
            
            .status-success {
                color: #28a745;
                font-weight: 600;
            }
            
            .status-error {
                color: #dc3545;
                font-weight: 600;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            }
            
            .stat-number {
                font-size: 2rem;
                font-weight: bold;
                color: #4facfe;
                margin-bottom: 5px;
            }
            
            .stat-label {
                color: #666;
                font-size: 0.9rem;
            }
            
            /* 文件表格样式 */
            .file-table {
                width: 100%;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }
            
            .file-header {
                display: grid;
                grid-template-columns: 140px 1fr 100px 140px 90px 240px;
                background: #f8f9fa;
                padding: 15px;
                font-weight: 600;
                color: #495057;
                border-bottom: 2px solid #e9ecef;
                gap: 15px;
            }
            
            .file-row {
                display: grid;
                grid-template-columns: 140px 1fr 100px 140px 90px 240px;
                padding: 15px;
                border-bottom: 1px solid #e9ecef;
                background: white;
                transition: all 0.2s ease;
                gap: 15px;
                align-items: center;
            }
            
            .file-row:hover {
                background: #f8f9fa;
            }
            
            .file-row:last-child {
                border-bottom: none;
            }
            
            /* 文件类型列 */
            .file-type-column {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .file-type-icon {
                font-size: 1.5rem;
            }
            
            .file-type-name {
                font-size: 0.85rem;
                color: #666;
                font-weight: 500;
            }
            
            /* 文件名列 */
            .file-name-column {
                min-width: 0;
            }
            
            .file-name-primary {
                font-weight: 500;
                color: #333;
                font-size: 0.9rem;
                word-break: break-all;
            }
            
            /* 文件大小列 */
            .file-size-column {
                font-weight: 500;
                color: #666;
                font-size: 0.9rem;
                text-align: right;
            }
            
            /* 上传时间列 */
            .file-time-column {
                font-size: 0.85rem;
                color: #666;
                font-weight: 500;
            }
            
            /* 预览列 */
            .file-preview-column {
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            /* 操作按钮列 */
            .file-actions-column {
                display: flex;
                gap: 6px;
                justify-content: flex-end;
                flex-wrap: wrap;
            }
            
            .action-btn {
                padding: 6px 10px;
                border: none;
                border-radius: 15px;
                font-size: 0.7rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                white-space: nowrap;
                margin: 0 2px;
            }
            
            .preview-btn {
                background: #007bff;
                color: white;
                padding: 6px 12px;
                border-radius: 15px;
                font-size: 0.75rem;
            }
            
            .preview-btn:hover {
                background: #0056b3;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
            }
            
            .preview-btn:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            
            .download-btn {
                background: #28a745;
                color: white;
            }
            
            .download-btn:hover {
                background: #218838;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
            }
            
            .copy-btn {
                background: #6c757d;
                color: white;
            }
            
            .copy-btn:hover {
                background: #545b62;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(108, 117, 125, 0.3);
            }
            
            .delete-btn {
                background: #dc3545;
                color: white;
            }
            
            .delete-btn:hover {
                background: #c82333;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
            }
            
            /* 预览模态框样式 */
            .preview-modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.9);
                backdrop-filter: blur(5px);
            }
            
            .preview-modal.show {
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .preview-content {
                position: relative;
                max-width: 90%;
                max-height: 90%;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            
            .preview-header {
                background: linear-gradient(135deg, #4facfe, #00f2fe);
                color: white;
                padding: 15px 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .preview-title {
                font-weight: 600;
                font-size: 1.1rem;
                margin: 0;
            }
            
            .close-btn {
                background: none;
                border: none;
                color: white;
                font-size: 1.5rem;
                cursor: pointer;
                padding: 5px;
                border-radius: 50%;
                transition: background 0.3s ease;
            }
            
            .close-btn:hover {
                background: rgba(255,255,255,0.2);
            }
            
            .preview-body {
                padding: 20px;
                text-align: center;
            }
            
            .preview-media {
                max-width: 100%;
                max-height: 70vh;
                border-radius: 8px;
            }
            
            .preview-info {
                margin-top: 15px;
                color: #666;
                font-size: 0.9rem;
            }
            
            /* 中屏设备优化 */
            @media (max-width: 1200px) {
                .file-header,
                .file-row {
                    grid-template-columns: 120px 1fr 90px 120px 80px 200px;
                    gap: 10px;
                }
                
                .action-btn {
                    padding: 5px 8px;
                    font-size: 0.65rem;
                }
            }
            
            /* 响应式设计 */
            @media (max-width: 768px) {
                .file-header,
                .file-row {
                    grid-template-columns: 1fr;
                    gap: 10px;
                }
                
                .file-header {
                    display: none;
                }
                
                .file-row {
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    margin-bottom: 10px;
                    padding: 15px;
                }
                
                .file-type-column,
                .file-name-column,
                .file-size-column,
                .file-time-column,
                .file-preview-column,
                .file-actions-column {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 8px;
                }
                
                .file-type-column::before {
                    content: "类型: ";
                    font-weight: 600;
                    color: #666;
                }
                
                .file-size-column::before {
                    content: "大小: ";
                    font-weight: 600;
                    color: #666;
                }
                
                .file-time-column::before {
                    content: "上传时间: ";
                    font-weight: 600;
                    color: #666;
                }
                
                .file-preview-column::before {
                    content: "预览: ";
                    font-weight: 600;
                    color: #666;
                }
                
                .file-size-column {
                    text-align: left;
                }
                
                .file-actions-column {
                    justify-content: flex-start;
                    margin-top: 10px;
                    padding-top: 10px;
                    border-top: 1px solid #e9ecef;
                    margin-bottom: 0;
                }
                
                .file-actions-column::before {
                    content: "操作: ";
                    font-weight: 600;
                    color: #666;
                    margin-right: 10px;
                }
                
                .action-btn {
                    padding: 6px 10px;
                    font-size: 0.7rem;
                    margin: 2px;
                }
                
                .preview-content {
                    max-width: 95%;
                    max-height: 95%;
                }
                
                .preview-media {
                    max-height: 60vh;
                }
            }
            
            /* 分页样式 */
            .pagination-container {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 20px;
                padding: 15px 0;
            }
            
            .pagination-info {
                color: #666;
                font-size: 0.9rem;
            }
            
            .pagination {
                display: flex;
                gap: 8px;
                align-items: center;
            }
            
            .page-btn {
                padding: 8px 12px;
                border: 1px solid #e1e8ed;
                background: white;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.9rem;
                font-weight: 500;
                transition: all 0.3s ease;
                min-width: 40px;
                text-align: center;
                text-decoration: none;
                color: #666;
            }
            
            .page-btn:hover {
                background: #f8f9fa;
                border-color: #4facfe;
                color: #4facfe;
            }
            
            .page-btn.active {
                background: #4facfe;
                border-color: #4facfe;
                color: white;
            }
            
            .page-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                background: #f8f9fa;
                color: #999;
            }
            
            .page-btn:disabled:hover {
                background: #f8f9fa;
                border-color: #e1e8ed;
                color: #999;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📁 文件管理系统</h1>
                <p>专业的文件上传和管理平台</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="totalFiles">0</div>
                    <div class="stat-label">文件总数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="uploadedToday">0</div>
                    <div class="stat-label">今日上传</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="totalSize">0 MB</div>
                    <div class="stat-label">总大小</div>
                </div>
            </div>
            
            <div class="main-content">
                <!-- 左侧：文件类型选择 -->
                <div class="card">
                    <div class="card-header">
                        🎯 选择文件类型
                    </div>
                    <div class="card-body">
                        <div class="file-types" id="fileTypes">
                            <!-- 文件类型选项将通过 JavaScript 动态生成 -->
                        </div>
                    </div>
                </div>
                
                <!-- 右侧：上传区域 -->
                <div class="card">
                    <div class="card-header">
                        📤 文件上传
                    </div>
                    <div class="card-body">
                        <div class="upload-area" id="uploadArea">
                            <div class="upload-icon">☁️</div>
                            <div class="upload-text">拖拽文件到这里或点击上传</div>
                            <div class="upload-hint">支持多文件同时上传，最大500MB</div>
                            <button class="upload-btn" onclick="document.getElementById('fileInput').click()">
                                选择文件
                            </button>
                            <input type="file" id="fileInput" class="file-input" multiple>
                        </div>
                        
                        <div class="file-list" id="fileList">
                            <!-- 上传文件列表将动态显示在这里 -->
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 已上传文件列表 -->
            <div class="card">
                <div class="card-header">
                    📋 文件列表
                </div>
                <div class="card-body">
                    <div id="existingFiles">
                        <p style="text-align: center; color: #666; padding: 20px;">
                            正在加载文件列表...
                        </p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 预览模态框 -->
        <div id="previewModal" class="preview-modal">
            <div class="preview-content">
                <div class="preview-header">
                    <h3 class="preview-title" id="previewTitle">文件预览</h3>
                    <button class="close-btn" onclick="closePreview()">&times;</button>
                </div>
                <div class="preview-body">
                    <div id="previewContainer">
                        <!-- 预览内容将在这里动态生成 -->
                    </div>
                    <div class="preview-info" id="previewInfo">
                        <!-- 文件信息将在这里显示 -->
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // 文件类型配置
            const fileTypes = ''' + str(FILE_TYPES).replace("'", '"') + ''';
            
            let selectedFileTypes = new Set();
            let uploadQueue = [];
            let allFiles = [];
            let currentPage = 1;
            const filesPerPage = 10;
            
            // 初始化页面
            document.addEventListener('DOMContentLoaded', function() {
                initFileTypes();
                initUploadArea();
                loadExistingFiles();
                updateStats();
            });
            
            // 初始化文件类型选择
            function initFileTypes() {
                const container = document.getElementById('fileTypes');
                
                Object.entries(fileTypes).forEach(([typeName, typeInfo]) => {
                    const option = document.createElement('div');
                    option.className = 'file-type-option';
                    option.dataset.type = typeName;
                    
                    option.innerHTML = `
                        <span class="file-type-icon">${typeInfo.icon}</span>
                        <div class="file-type-name">${typeName}</div>
                        <div class="file-type-exts">${typeInfo.extensions.slice(0, 4).join(', ')}${typeInfo.extensions.length > 4 ? '...' : ''}</div>
                    `;
                    
                    option.style.borderColor = typeInfo.color + '40';
                    
                    option.addEventListener('click', function() {
                        toggleFileType(typeName, option);
                    });
                    
                    container.appendChild(option);
                });
            }
            
            // 切换文件类型选择
            function toggleFileType(typeName, element) {
                if (selectedFileTypes.has(typeName)) {
                    selectedFileTypes.delete(typeName);
                    element.classList.remove('selected');
                } else {
                    selectedFileTypes.add(typeName);
                    element.classList.add('selected');
                }
                
                updateFileFilter();
            }
            
            // 初始化上传区域
            function initUploadArea() {
                const uploadArea = document.getElementById('uploadArea');
                const fileInput = document.getElementById('fileInput');
                
                // 拖拽事件
                uploadArea.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    uploadArea.classList.add('dragover');
                });
                
                uploadArea.addEventListener('dragleave', function(e) {
                    e.preventDefault();
                    uploadArea.classList.remove('dragover');
                });
                
                uploadArea.addEventListener('drop', function(e) {
                    e.preventDefault();
                    uploadArea.classList.remove('dragover');
                    
                    const files = Array.from(e.dataTransfer.files);
                    handleFileSelection(files);
                });
                
                // 文件选择事件
                fileInput.addEventListener('change', function(e) {
                    const files = Array.from(e.target.files);
                    handleFileSelection(files);
                    e.target.value = ''; // 清空选择，允许重复选择同一文件
                });
            }
            
            // 处理文件选择
            function handleFileSelection(files) {
                files.forEach(file => {
                    if (isFileTypeAllowed(file)) {
                        addFileToQueue(file);
                    } else {
                        alert(`文件 "${file.name}" 类型不被当前选择的类型支持`);
                    }
                });
            }
            
            // 检查文件类型是否允许
            function isFileTypeAllowed(file) {
                if (selectedFileTypes.size === 0) return true;
                
                const fileName = file.name.toLowerCase();
                const extension = fileName.split('.').pop();
                
                for (let typeName of selectedFileTypes) {
                    if (fileTypes[typeName].extensions.includes(extension)) {
                        return true;
                    }
                }
                return false;
            }
            
            // 添加文件到上传队列
            function addFileToQueue(file) {
                const fileId = 'file_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                
                const fileItem = {
                    id: fileId,
                    file: file,
                    progress: 0,
                    status: 'pending',
                    uploadedSize: 0
                };
                
                uploadQueue.push(fileItem);
                renderFileItem(fileItem);
                
                // 自动开始上传
                setTimeout(() => uploadFile(fileItem), 100);
            }
            
            // 渲染文件项
            function renderFileItem(fileItem) {
                const fileList = document.getElementById('fileList');
                
                const fileTypeInfo = getFileTypeInfo(fileItem.file.name);
                const fileSizeText = formatFileSize(fileItem.file.size);
                
                const itemElement = document.createElement('div');
                itemElement.className = 'file-item';
                itemElement.id = fileItem.id;
                
                itemElement.innerHTML = `
                    <div class="file-info">
                        <span class="file-icon">${fileTypeInfo.icon}</span>
                        <div class="file-details">
                            <h4>${fileItem.file.name}</h4>
                            <p>${fileSizeText} • ${fileTypeInfo.typeName}</p>
                        </div>
                    </div>
                    <div class="file-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${fileItem.progress}%"></div>
                        </div>
                        <div class="progress-text">准备上传...</div>
                    </div>
                    <div class="file-actions">
                        <button class="btn-small btn-remove" onclick="removeFileFromQueue('${fileItem.id}')">
                            删除
                        </button>
                    </div>
                `;
                
                fileList.appendChild(itemElement);
            }
            
            // 上传文件
            function uploadFile(fileItem) {
                const formData = new FormData();
                formData.append('file', fileItem.file);
                
                const xhr = new XMLHttpRequest();
                
                // 上传进度
                xhr.upload.addEventListener('progress', function(e) {
                    if (e.lengthComputable) {
                        const percentComplete = Math.round((e.loaded / e.total) * 100);
                        updateFileProgress(fileItem.id, percentComplete, `上传中... ${percentComplete}%`);
                    }
                });
                
                // 上传完成
                xhr.addEventListener('load', function() {
                    if (xhr.status === 200) {
                        const response = JSON.parse(xhr.responseText);
                        updateFileProgress(fileItem.id, 100, '上传成功', 'success');
                        loadExistingFiles(); // 重新加载文件列表
                        updateStats();
                    } else {
                        updateFileProgress(fileItem.id, 0, '上传失败', 'error');
                    }
                });
                
                // 上传错误
                xhr.addEventListener('error', function() {
                    updateFileProgress(fileItem.id, 0, '网络错误', 'error');
                });
                
                xhr.open('POST', '/upload');
                xhr.send(formData);
                
                updateFileProgress(fileItem.id, 0, '正在上传...');
            }
            
            // 更新文件进度
            function updateFileProgress(fileId, progress, statusText, statusClass = '') {
                const element = document.getElementById(fileId);
                if (!element) return;
                
                const progressFill = element.querySelector('.progress-fill');
                const progressText = element.querySelector('.progress-text');
                
                progressFill.style.width = progress + '%';
                progressText.textContent = statusText;
                
                if (statusClass) {
                    progressText.className = `progress-text status-${statusClass}`;
                }
            }
            
            // 从队列中移除文件
            function removeFileFromQueue(fileId) {
                const element = document.getElementById(fileId);
                if (element) {
                    element.remove();
                }
                
                uploadQueue = uploadQueue.filter(item => item.id !== fileId);
            }
            
            // 获取文件类型信息
            function getFileTypeInfo(filename) {
                const extension = filename.toLowerCase().split('.').pop();
                
                for (let [typeName, typeInfo] of Object.entries(fileTypes)) {
                    if (typeInfo.extensions.includes(extension)) {
                        return { typeName, ...typeInfo };
                    }
                }
                
                return { typeName: '其他文件', icon: '📄', color: '#999' };
            }
            
            // 格式化文件大小
            function formatFileSize(bytes) {
                if (bytes === 0) return '0 B';
                
                const k = 1024;
                const sizes = ['B', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                
                return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
            }
            
            // 加载已存在的文件
            function loadExistingFiles() {
                fetch('/api/files')
                    .then(response => response.json())
                    .then(data => {
                        renderExistingFiles(data.files);
                    })
                    .catch(error => {
                        document.getElementById('existingFiles').innerHTML = 
                            '<p style="text-align: center; color: #dc3545;">加载文件列表失败</p>';
                    });
            }
            
            // 渲染已存在的文件
            function renderExistingFiles(files) {
                allFiles = files;
                renderCurrentPage();
            }
            
            // 渲染当前页面
            function renderCurrentPage() {
                const container = document.getElementById('existingFiles');
                
                if (allFiles.length === 0) {
                    container.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">暂无文件</p>';
                    return;
                }
                
                // 计算分页
                const totalPages = Math.ceil(allFiles.length / filesPerPage);
                const startIndex = (currentPage - 1) * filesPerPage;
                const endIndex = startIndex + filesPerPage;
                const currentFiles = allFiles.slice(startIndex, endIndex);
                
                // 生成文件列表
                const fileList = currentFiles.map((file, index) => {
                    const typeInfo = getFileTypeInfo(file.filename);
                    const fileUrl = `${window.location.origin}/files/${file.filename}`;
                    const canPreview = isPreviewable(file.filename);
                    
                    return `
                        <div class="file-row" data-index="${startIndex + index}">
                            <div class="file-type-column">
                                <span class="file-type-icon" style="color: ${typeInfo.color}">${typeInfo.icon}</span>
                                <span class="file-type-name">${typeInfo.typeName}</span>
                            </div>
                            <div class="file-name-column">
                                <div class="file-name-primary">${file.filename}</div>
                            </div>
                            <div class="file-size-column">
                                ${formatFileSize(file.size)}
                            </div>
                            <div class="file-time-column">
                                ${file.upload_date}
                            </div>
                            <div class="file-preview-column">
                                <button class="action-btn preview-btn" 
                                        ${canPreview ? '' : 'disabled'} 
                                        ${canPreview ? `onclick="previewFile('${file.filename.replace(/'/g, "\\'")}', '${typeInfo.typeName.replace(/'/g, "\\'")}')"` : ''}>
                                    👁️ 预览
                                </button>
                            </div>
                            <div class="file-actions-column">
                                <button class="action-btn download-btn" onclick="downloadFile('${file.filename}')">
                                    📥 下载
                                </button>
                                <button class="action-btn copy-btn" onclick="copyFileUrl('${fileUrl}', this)">
                                    📋 复制URL
                                </button>
                                <button class="action-btn delete-btn" onclick="deleteFile('${file.filename.replace(/'/g, "\\'")}')">
                                    🗑️ 删除
                                </button>
                            </div>
                        </div>
                    `;
                }).join('');
                
                // 生成分页控件
                const paginationHtml = generatePagination(currentPage, totalPages, allFiles.length);
                
                container.innerHTML = `
                    <div class="file-table">
                        <div class="file-header">
                            <div class="file-type-column">类型</div>
                            <div class="file-name-column">文件名</div>
                            <div class="file-size-column">大小</div>
                            <div class="file-time-column">上传时间</div>
                            <div class="file-preview-column">预览</div>
                            <div class="file-actions-column">操作</div>
                        </div>
                        ${fileList}
                    </div>
                    ${paginationHtml}
                `;
            }
            
            // 生成分页HTML
            function generatePagination(current, total, totalFiles) {
                if (total <= 1) return '';
                
                const startItem = (current - 1) * filesPerPage + 1;
                const endItem = Math.min(current * filesPerPage, totalFiles);
                
                let paginationButtons = '';
                
                // 上一页按钮
                paginationButtons += `
                    <button class="page-btn" ${current === 1 ? 'disabled' : ''} onclick="changePage(${current - 1})">
                        ← 上一页
                    </button>
                `;
                
                // 页码按钮
                let startPage = Math.max(1, current - 2);
                let endPage = Math.min(total, current + 2);
                
                // 确保显示5个页码（如果可能）
                if (endPage - startPage < 4) {
                    if (startPage === 1) {
                        endPage = Math.min(total, startPage + 4);
                    } else {
                        startPage = Math.max(1, endPage - 4);
                    }
                }
                
                for (let i = startPage; i <= endPage; i++) {
                    paginationButtons += `
                        <button class="page-btn ${i === current ? 'active' : ''}" onclick="changePage(${i})">
                            ${i}
                        </button>
                    `;
                }
                
                // 下一页按钮
                paginationButtons += `
                    <button class="page-btn" ${current === total ? 'disabled' : ''} onclick="changePage(${current + 1})">
                        下一页 →
                    </button>
                `;
                
                return `
                    <div class="pagination-container">
                        <div class="pagination-info">
                            显示第 ${startItem}-${endItem} 项，共 ${totalFiles} 项
                        </div>
                        <div class="pagination">
                            ${paginationButtons}
                        </div>
                    </div>
                `;
            }
            
            // 切换页面
            function changePage(page) {
                const totalPages = Math.ceil(allFiles.length / filesPerPage);
                if (page < 1 || page > totalPages) return;
                
                currentPage = page;
                renderCurrentPage();
                
                // 滚动到文件列表顶部
                document.getElementById('existingFiles').scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }
            
            // 下载文件
            function downloadFile(filename) {
                const link = document.createElement('a');
                link.href = `/files/${filename}`;
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
            
            // 复制文件URL
            function copyFileUrl(url, button) {
                console.log('尝试复制URL:', url);
                
                const originalText = button.textContent;
                const originalColor = button.style.background;
                
                // 优先使用现代的 Clipboard API
                if (navigator.clipboard && window.isSecureContext) {
                    navigator.clipboard.writeText(url).then(function() {
                        console.log('使用Clipboard API复制成功');
                        showCopySuccess(button, originalText, originalColor);
                    }).catch(function(err) {
                        console.log('Clipboard API失败，尝试降级方案:', err);
                        fallbackCopyMethod(url, button, originalText, originalColor);
                    });
                } else {
                    console.log('不支持Clipboard API，使用降级方案');
                    fallbackCopyMethod(url, button, originalText, originalColor);
                }
            }
            
            // 显示复制成功状态
            function showCopySuccess(button, originalText, originalColor) {
                button.textContent = '✅ 已复制';
                button.style.background = '#28a745';
                button.disabled = true;
                
                setTimeout(function() {
                    button.textContent = originalText;
                    button.style.background = originalColor || '#6c757d';
                    button.disabled = false;
                }, 2000);
            }
            
            // 降级复制方法
            function fallbackCopyMethod(url, button, originalText, originalColor) {
                try {
                    // 创建临时文本域
                    const textArea = document.createElement('textarea');
                    textArea.value = url;
                    textArea.style.position = 'fixed';
                    textArea.style.left = '-999999px';
                    textArea.style.top = '-999999px';
                    document.body.appendChild(textArea);
                    
                    // 选择并复制
                    textArea.focus();
                    textArea.select();
                    textArea.setSelectionRange(0, 99999); // 移动设备兼容性
                    
                    const successful = document.execCommand('copy');
                    document.body.removeChild(textArea);
                    
                    if (successful) {
                        console.log('使用execCommand复制成功');
                        showCopySuccess(button, originalText, originalColor);
                    } else {
                        throw new Error('execCommand复制失败');
                    }
                } catch (err) {
                    console.error('所有复制方法都失败了:', err);
                    // 创建一个模态对话框让用户手动复制
                    showManualCopyDialog(url, button, originalText, originalColor);
                }
            }
            
            // 显示手动复制对话框
            function showManualCopyDialog(url, button, originalText, originalColor) {
                // 创建模态框
                const modal = document.createElement('div');
                modal.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.7);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 10000;
                `;
                
                modal.innerHTML = `
                    <div style="
                        background: white;
                        padding: 30px;
                        border-radius: 12px;
                        max-width: 500px;
                        width: 90%;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    ">
                        <h3 style="margin: 0 0 15px 0; color: #333; text-align: center;">
                            📋 手动复制URL
                        </h3>
                        <p style="margin: 0 0 15px 0; color: #666; text-align: center;">
                            自动复制失败，请手动复制以下URL：
                        </p>
                        <div style="
                            background: #f8f9fa;
                            padding: 15px;
                            border: 1px solid #e9ecef;
                            border-radius: 6px;
                            margin: 15px 0;
                            font-family: monospace;
                            font-size: 0.9rem;
                            word-break: break-all;
                            user-select: all;
                            cursor: text;
                        " onclick="this.select()" id="urlToSelect">
                            ${url}
                        </div>
                        <div style="text-align: center; margin-top: 20px;">
                            <button onclick="document.body.removeChild(this.closest('div').parentElement)" style="
                                background: #007bff;
                                color: white;
                                border: none;
                                padding: 10px 20px;
                                border-radius: 6px;
                                cursor: pointer;
                                font-size: 0.9rem;
                            ">
                                关闭
                            </button>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
                
                // 点击模态框外部关闭
                modal.onclick = function(e) {
                    if (e.target === modal) {
                        document.body.removeChild(modal);
                    }
                };
                
                // 重置按钮状态
                button.textContent = '❌ 请手动复制';
                button.style.background = '#dc3545';
                setTimeout(function() {
                    button.textContent = originalText;
                    button.style.background = originalColor || '#6c757d';
                }, 3000);
            }
            
            // 更新统计信息
            function updateStats() {
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('totalFiles').textContent = data.total_files;
                        document.getElementById('uploadedToday').textContent = data.uploaded_today;
                        document.getElementById('totalSize').textContent = formatFileSize(data.total_size);
                    })
                    .catch(error => {
                        console.error('Failed to load stats:', error);
                    });
            }
            
            // 更新文件过滤器（如果需要的话）
            function updateFileFilter() {
                // 可以在这里添加实时过滤逻辑
            }
            
            // 检查文件是否可预览
            function isPreviewable(filename) {
                const extension = filename.toLowerCase().split('.').pop();
                const previewableTypes = {
                    '音视频文件': ['mp4', 'avi', 'mov', 'mkv', 'webm', 'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'],
                    '图片文件': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp']
                };
                
                for (let types of Object.values(previewableTypes)) {
                    if (types.includes(extension)) {
                        return true;
                    }
                }
                return false;
            }
            
            // 预览文件
            function previewFile(filename, fileType) {
                console.log('previewFile called with:', filename, fileType);
                const fileUrl = `/files/${filename}`;
                const modal = document.getElementById('previewModal');
                const container = document.getElementById('previewContainer');
                const title = document.getElementById('previewTitle');
                const info = document.getElementById('previewInfo');
                
                if (!modal) {
                    console.error('Preview modal not found!');
                    return;
                }
                
                title.textContent = filename;
                
                // 清空之前的内容
                container.innerHTML = '';
                
                const extension = filename.toLowerCase().split('.').pop();
                
                if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'].includes(extension)) {
                    // 图片预览
                    const img = document.createElement('img');
                    img.className = 'preview-media';
                    img.src = fileUrl;
                    img.alt = filename;
                    img.onload = function() {
                        info.innerHTML = `
                            <p>文件类型: ${fileType} | 分辨率: ${this.naturalWidth} × ${this.naturalHeight}</p>
                        `;
                    };
                    img.onerror = function() {
                        container.innerHTML = '<p style="color: #dc3545; padding: 40px;">图片加载失败</p>';
                    };
                    container.appendChild(img);
                } else if (['mp4', 'webm', 'mov', 'avi', 'mkv'].includes(extension)) {
                    // 视频预览
                    const video = document.createElement('video');
                    video.className = 'preview-media';
                    video.controls = true;
                    video.preload = 'metadata';
                    video.src = fileUrl;
                    video.onloadedmetadata = function() {
                        info.innerHTML = `
                            <p>文件类型: ${fileType} | 分辨率: ${this.videoWidth} × ${this.videoHeight} | 时长: ${formatDuration(this.duration)}</p>
                        `;
                    };
                    video.onerror = function() {
                        container.innerHTML = '<p style="color: #dc3545; padding: 40px;">视频加载失败</p>';
                    };
                    container.appendChild(video);
                } else if (['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'].includes(extension)) {
                    // 音频预览
                    const audio = document.createElement('audio');
                    audio.className = 'preview-media';
                    audio.controls = true;
                    audio.preload = 'metadata';
                    audio.src = fileUrl;
                    audio.style.width = '100%';
                    audio.style.maxWidth = '400px';
                    audio.onloadedmetadata = function() {
                        info.innerHTML = `
                            <p>文件类型: ${fileType} | 时长: ${formatDuration(this.duration)}</p>
                        `;
                    };
                    audio.onerror = function() {
                        container.innerHTML = '<p style="color: #dc3545; padding: 40px;">音频加载失败</p>';
                    };
                    container.appendChild(audio);
                } else {
                    container.innerHTML = '<p style="color: #666; padding: 40px;">该文件类型不支持预览</p>';
                }
                
                // 显示模态框
                modal.classList.add('show');
                document.body.style.overflow = 'hidden';
            }
            
            // 关闭预览
            function closePreview() {
                const modal = document.getElementById('previewModal');
                const container = document.getElementById('previewContainer');
                
                modal.classList.remove('show');
                document.body.style.overflow = 'auto';
                
                // 清空媒体内容，停止播放
                const media = container.querySelector('video, audio');
                if (media) {
                    media.pause();
                    media.currentTime = 0;
                }
                container.innerHTML = '';
            }
            
            // 格式化时长
            function formatDuration(seconds) {
                if (isNaN(seconds)) return '未知';
                
                const hours = Math.floor(seconds / 3600);
                const minutes = Math.floor((seconds % 3600) / 60);
                const secs = Math.floor(seconds % 60);
                
                if (hours > 0) {
                    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
                } else {
                    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
                }
            }
            
            // 点击模态框背景关闭
            document.getElementById('previewModal').addEventListener('click', function(e) {
                if (e.target === this) {
                    closePreview();
                }
            });
            
            // ESC键关闭模态框
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    const modal = document.getElementById('previewModal');
                    if (modal.classList.contains('show')) {
                        closePreview();
                    }
                }
            });
            
            // 删除文件
            function deleteFile(filename) {
                // 确认删除
                if (!confirm(`确定要删除文件 "${filename}" 吗？\n\n此操作无法撤销！`)) {
                    return;
                }
                
                console.log('Deleting file:', filename);
                
                // 发送删除请求
                fetch(`/api/files/${encodeURIComponent(filename)}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        return response.json().then(err => {
                            throw new Error(err.error || '删除失败');
                        });
                    }
                })
                .then(data => {
                    // 显示成功消息
                    alert('文件删除成功！');
                    
                    // 重新加载文件列表
                    loadExistingFiles();
                    updateStats();
                })
                .catch(error => {
                    console.error('Delete error:', error);
                    alert(`删除失败：${error.message}`);
                });
            }
        </script>
    </body>
    </html>
    '''
    return upload_page

# 上传文件接口
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名不能为空'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型'}), 400
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        unique_filename = timestamp + str(uuid.uuid4())[:8] + '_' + filename
        
        file_path = os.path.join(VIDEO_DIR, unique_filename)
        file.save(file_path)
        
        # 获取文件信息
        file_size = os.path.getsize(file_path)
        file_type = get_file_type(filename)
        
        return jsonify({
            'status': 'success',
            'message': '文件上传成功',
            'filename': unique_filename,
            'original_name': filename,
            'size': file_size,
            'type': file_type,
            'download_url': f'/files/{unique_filename}'
        })
        
    except Exception as e:
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

# 文件列表API
@app.route('/api/files')
def api_files():
    try:
        if not os.path.exists(VIDEO_DIR):
            return jsonify({'files': [], 'total': 0})
        
        files = []
        for filename in os.listdir(VIDEO_DIR):
            file_path = os.path.join(VIDEO_DIR, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                file_type = get_file_type(filename)
                
                files.append({
                    'filename': filename,
                    'size': file_size,
                    'type': file_type,
                    'download_url': f'/files/{filename}',
                    'upload_date': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # 按上传时间排序，最新的在前
        files.sort(key=lambda x: x['upload_date'], reverse=True)
        
        return jsonify({
            'files': files,
            'total': len(files)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 统计信息API
@app.route('/api/stats')
def api_stats():
    try:
        if not os.path.exists(VIDEO_DIR):
            return jsonify({
                'total_files': 0,
                'uploaded_today': 0,
                'total_size': 0
            })
        
        total_files = 0
        uploaded_today = 0
        total_size = 0
        today = datetime.now().date()
        
        for filename in os.listdir(VIDEO_DIR):
            file_path = os.path.join(VIDEO_DIR, filename)
            if os.path.isfile(file_path):
                total_files += 1
                file_size = os.path.getsize(file_path)
                total_size += file_size
                
                # 检查是否是今天上传的
                file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).date()
                if file_date == today:
                    uploaded_today += 1
        
        return jsonify({
            'total_files': total_files,
            'uploaded_today': uploaded_today,
            'total_size': total_size
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 删除文件API
@app.route('/api/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        file_path = os.path.join(VIDEO_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
            
        if not os.path.isfile(file_path):
            return jsonify({'error': '无效的文件'}), 400
            
        # 删除文件
        os.remove(file_path)
        
        return jsonify({
            'status': 'success',
            'message': '文件删除成功',
            'filename': filename
        })
        
    except PermissionError:
        return jsonify({'error': '没有权限删除文件'}), 403
    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500

# 文件下载接口（兼容原有的视频接口）
@app.route('/files/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(VIDEO_DIR, filename)
        
        if not os.path.exists(file_path):
            abort(404)
        
        if not os.path.isfile(file_path):
            abort(404)
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 兼容原有的视频接口
@app.route('/videos')
def list_videos():
    try:
        if not os.path.exists(VIDEO_DIR):
            return jsonify({'error': '文件目录不存在'}), 404
        
        files = []
        for filename in os.listdir(VIDEO_DIR):
            file_path = os.path.join(VIDEO_DIR, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                files.append({
                    'filename': filename,
                    'size': file_size,
                    'download_url': f'/files/{filename}'
                })
        
        return jsonify({
            'directory': VIDEO_DIR,
            'total_files': len(files),
            'files': files
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/videos/<filename>')
def download_video(filename):
    # 重定向到新的文件下载接口
    return download_file(filename)

if __name__ == '__main__':
    print(f"🚀 文件管理系统启动中...")
    print(f"📁 文件目录: {VIDEO_DIR}")
    print(f"🌐 访问地址:")
    print(f"   主页 (上传界面): http://localhost:8080/")
    print(f"   文件列表 API: http://localhost:8080/api/files")
    print(f"   统计信息 API: http://localhost:8080/api/stats")
    print(f"   文件下载接口: http://localhost:8080/files/<filename>")
    print(f"   兼容接口: http://localhost:8080/videos")
    print(f"💡 支持的文件类型:")
    for type_name, type_info in FILE_TYPES.items():
        print(f"   {type_info['icon']} {type_name}: {', '.join(type_info['extensions'][:5])}{'...' if len(type_info['extensions']) > 5 else ''}")
    print(f"📊 最大文件大小: 500MB")
    print(f"📄 分页显示: 每页10个文件")
    print(f"✨ 功能特性: 拖拽上传、多文件上传、实时进度、文件分类、分页浏览")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8080, debug=False)