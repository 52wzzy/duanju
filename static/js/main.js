// 全局变量
let uploadedTemplate = null;
let uploadedReference = null;

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    console.log('电商主图生成工具已加载');
});

// 初始化事件监听器
function initializeEventListeners() {
    // 文件上传事件
    document.getElementById('templateUpload').addEventListener('change', handleTemplateUpload);
    document.getElementById('referenceUpload').addEventListener('change', handleReferenceUpload);
    
    // 按钮点击事件
    document.getElementById('checkWordsBtn').addEventListener('click', checkForbiddenWords);
    document.getElementById('generateMainImageBtn').addEventListener('click', generateMainImage);
    document.getElementById('generateDetailBtn').addEventListener('click', generateDetailPage);
    
    // 添加AI生成按钮事件监听
    const aiGenerateBtn = document.getElementById('generateAIImageBtn');
    if (aiGenerateBtn) {
        aiGenerateBtn.addEventListener('click', generateAIImage);
    }

    // AI模型选择事件
    initializeAIModelListeners();
}

// 显示加载状态
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

// 隐藏加载状态
function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// 显示消息提示
function showMessage(message, type = 'info') {
    const alertClass = type === 'success' ? 'alert-success' : 
                      type === 'error' ? 'alert-danger' : 'alert-info';
    
    const messageHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // 在第一个卡片前插入消息
    const firstCard = document.querySelector('.card');
    firstCard.insertAdjacentHTML('beforebegin', messageHtml);
    
    // 3秒后自动消失
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) {
            alert.remove();
        }
    }, 3000);
}

// 处理模板上传
async function handleTemplateUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
        showLoading();
        const result = await uploadFile(file, 'template');
        
        if (result.success) {
            uploadedTemplate = result.filename;
            displayImagePreview('templatePreview', result.url);
            showMessage('模板上传成功', 'success');
        } else {
            showMessage('模板上传失败: ' + result.error, 'error');
        }
    } catch (error) {
        showMessage('上传失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 处理参考图上传
async function handleReferenceUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
        showLoading();
        const result = await uploadFile(file, 'reference');
        
        if (result.success) {
            uploadedReference = result.filename;
            displayImagePreview('referencePreview', result.url);
            showMessage('参考图上传成功', 'success');
        } else {
            showMessage('参考图上传失败: ' + result.error, 'error');
        }
    } catch (error) {
        showMessage('上传失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 上传文件到服务器
async function uploadFile(file, type) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    
    const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}

// 显示图片预览
function displayImagePreview(containerId, imageUrl) {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <img src="${imageUrl}" class="preview-image" alt="预览图片">
        <div class="mt-2">
            <small class="text-muted">图片已上传</small>
        </div>
    `;
}

// 检查违禁词
async function checkForbiddenWords() {
    const title = document.getElementById('articleTitle').value.trim();
    const content = document.getElementById('articleContent').value.trim();
    
    if (!title && !content) {
        showMessage('请输入标题或内容后再检查', 'error');
        return;
    }
    
    try {
        showLoading();
        
        const text = title + ' ' + content;
        const response = await fetch('/api/check-words', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });
        
        const result = await response.json();
        displayWordsCheckResult(result);
        
    } catch (error) {
        showMessage('检查失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 显示违禁词检查结果
function displayWordsCheckResult(result) {
    const container = document.getElementById('wordsCheckResult');
    
    if (result.has_forbidden) {
        const forbiddenWordsHtml = result.forbidden_words.map(word => 
            `<span class="forbidden-word">${word}</span>`
        ).join('');
        
        container.innerHTML = `
            <div class="words-warning">
                <i class="bi bi-exclamation-triangle-fill me-1"></i>
                发现违禁词: ${forbiddenWordsHtml}
            </div>
            <div class="mt-2">
                <strong>建议修改为:</strong>
                <div class="form-control mt-1" style="background-color: #f8f9fa;">
                    ${result.clean_text}
                </div>
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="words-clean">
                <i class="bi bi-check-circle-fill me-1"></i>
                未发现违禁词，内容健康！
            </div>
        `;
    }
}

// 生成主图
async function generateMainImage() {
    const title = document.getElementById('articleTitle').value.trim();
    const content = document.getElementById('articleContent').value.trim();
    
    if (!title || !content) {
        showMessage('请输入完整的标题和内容', 'error');
        return;
    }
    
    if (!uploadedTemplate) {
        showMessage('请先上传主图模板', 'error');
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch('/api/generate-main-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title,
                content,
                template: uploadedTemplate,
                reference: uploadedReference,
                use_enhanced: true
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayMainImageResult(result);
            showMessage('主图生成成功！', 'success');
        } else {
            showMessage('生成失败: ' + result.error, 'error');
        }
        
    } catch (error) {
        showMessage('生成失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 显示主图生成结果
function displayMainImageResult(result) {
    const previewContainer = document.getElementById('mainImagePreview');
    const infoContainer = document.getElementById('mainImageInfo');
    
    previewContainer.innerHTML = `
        <img src="${result.image_url}" alt="生成的主图" class="img-fluid">
        <div class="mt-2">
            <button class="btn btn-outline-primary btn-sm" onclick="downloadImage('${result.image_url}')">
                <i class="bi bi-download me-1"></i>下载图片
            </button>
        </div>
    `;
    
    infoContainer.innerHTML = `
        <div class="detail-preview fade-in-up">
            <h6>生成信息</h6>
            <p><strong>主标题:</strong> ${result.text_data.main_title}</p>
            <p><strong>副标题:</strong> ${result.text_data.subtitle}</p>
            <p><strong>关键点:</strong></p>
            <ul>
                ${result.text_data.key_points.map(point => `<li>${point}</li>`).join('')}
            </ul>
        </div>
    `;
}

// 生成详情页
async function generateDetailPage() {
    const title = document.getElementById('articleTitle').value.trim();
    const content = document.getElementById('articleContent').value.trim();
    
    if (!title || !content) {
        showMessage('请输入完整的标题和内容', 'error');
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch('/api/generate-detail', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title,
                content
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayDetailPageResult(result.detail_content);
            showMessage('详情页生成成功！', 'success');
        } else {
            showMessage('生成失败: ' + result.error, 'error');
        }
        
    } catch (error) {
        showMessage('生成失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 显示详情页生成结果
function displayDetailPageResult(detailContent) {
    const container = document.getElementById('detailPagePreview');
    
    const sectionsHtml = detailContent.sections.map(section => `
        <div class="detail-section">
            <h6>${section.title}</h6>
            <p>${section.content}</p>
        </div>
    `).join('');
    
    const keyPointsHtml = detailContent.key_points.map(point => `
        <div class="detail-point">${point}</div>
    `).join('');
    
    container.innerHTML = `
        <div class="detail-preview fade-in-up">
            <div class="detail-title">${detailContent.title}</div>
            
            <div class="detail-section">
                <h6>简介</h6>
                <p>${detailContent.introduction}</p>
            </div>
            
            <div class="detail-section">
                <h6>核心要点</h6>
                ${keyPointsHtml}
            </div>
            
            ${sectionsHtml}
            
            <div class="mt-3">
                <button class="btn btn-outline-success btn-sm" onclick="copyDetailContent()">
                    <i class="bi bi-clipboard me-1"></i>复制内容
                </button>
                <button class="btn btn-outline-primary btn-sm ms-2" onclick="exportDetailContent()">
                    <i class="bi bi-file-earmark-text me-1"></i>导出HTML
                </button>
            </div>
        </div>
    `;
}

// 下载图片
function downloadImage(imageUrl) {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `main_image_${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 复制详情页内容
function copyDetailContent() {
    const detailText = document.querySelector('.detail-preview').innerText;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(detailText).then(() => {
            showMessage('内容已复制到剪贴板', 'success');
        }).catch(() => {
            showMessage('复制失败', 'error');
        });
    } else {
        // 降级方案
        const textArea = document.createElement('textarea');
        textArea.value = detailText;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showMessage('内容已复制到剪贴板', 'success');
        } catch (err) {
            showMessage('复制失败', 'error');
        }
        document.body.removeChild(textArea);
    }
}

// 导出详情页HTML
function exportDetailContent() {
    const detailHtml = document.querySelector('.detail-preview').outerHTML;
    
    const fullHtml = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>详情页</title>
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; }
        .detail-preview { max-width: 800px; margin: 0 auto; }
        .detail-title { font-size: 24px; font-weight: bold; margin-bottom: 20px; }
        .detail-section { margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #eee; }
        .detail-section h6 { color: #667eea; font-size: 16px; margin-bottom: 10px; }
        .detail-point { margin-left: 20px; position: relative; padding: 5px 0; }
        .detail-point::before { content: "•"; position: absolute; left: -15px; color: #667eea; }
    </style>
</head>
<body>
    ${detailHtml}
</body>
</html>
    `;
    
    const blob = new Blob([fullHtml], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `detail_page_${Date.now()}.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    showMessage('详情页已导出', 'success');
}

// 表单验证
function validateForm() {
    const title = document.getElementById('articleTitle').value.trim();
    const content = document.getElementById('articleContent').value.trim();
    
    if (!title) {
        showMessage('请输入文章标题', 'error');
        return false;
    }
    
    if (!content) {
        showMessage('请输入文章内容', 'error');
        return false;
    }
    
    if (title.length > 50) {
        showMessage('标题长度不能超过50个字符', 'error');
        return false;
    }
    
    if (content.length < 50) {
        showMessage('文章内容至少需要50个字符', 'error');
        return false;
    }
    
    return true;
}

// 错误处理
window.addEventListener('error', function(event) {
    console.error('页面错误:', event.error);
    showMessage('页面出现错误，请刷新重试', 'error');
});

// 生成AI图片
async function generateAIImage() {
    const title = document.getElementById('articleTitle').value.trim();
    const content = document.getElementById('articleContent').value.trim();
    const apiKey = document.getElementById('apiKey').value.trim();
    const aiModel = document.getElementById('aiModel').value;
    
    if (!title || !content) {
        showMessage('请输入完整的标题和内容', 'error');
        return;
    }
    
    if (!apiKey) {
        showMessage('请输入API密钥', 'error');
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch('/api/generate-ai-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title,
                content,
                api_key: apiKey,
                model_type: aiModel,
                style: 'commercial'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayAIImageResult(result);
            showMessage('AI图片生成成功！', 'success');
        } else {
            showMessage('AI生成失败: ' + result.error, 'error');
        }
        
    } catch (error) {
        showMessage('AI生成失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 显示AI图片生成结果
function displayAIImageResult(result) {
    const container = document.getElementById('aiImageResult');
    if (!container) {
        // 如果没有专门的AI结果容器，创建一个
        const aiResultHtml = `
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="card-title mb-0">
                        <i class="bi bi-robot me-2"></i>
                        AI生成结果
                    </h5>
                </div>
                <div class="card-body" id="aiImageResult">
                </div>
            </div>
        `;
        document.querySelector('.col-lg-6:last-child').insertAdjacentHTML('beforeend', aiResultHtml);
    }
    
    const resultContainer = document.getElementById('aiImageResult');
    resultContainer.innerHTML = `
        <div class="text-center">
            <img src="${result.image_url}" alt="AI生成的图片" class="img-fluid mb-3" style="max-height: 400px;">
            <div class="mb-3">
                <button class="btn btn-primary btn-sm me-2" onclick="saveAIImage('${result.image_url}')">
                    <i class="bi bi-download me-1"></i>保存到本地
                </button>
                <button class="btn btn-outline-primary btn-sm" onclick="useAsTemplate('${result.image_url}')">
                    <i class="bi bi-image me-1"></i>用作模板
                </button>
            </div>
            <div class="text-start">
                <h6>生成信息:</h6>
                <p><strong>模型:</strong> ${result.model_type}</p>
                <p><strong>提示词:</strong> ${result.prompt}</p>
            </div>
        </div>
    `;
}

// 保存AI图片到本地
async function saveAIImage(imageUrl) {
    try {
        showLoading();
        
        const response = await fetch('/api/save-ai-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image_url: imageUrl
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('图片已保存到本地', 'success');
            // 可以选择将其设置为模板
            uploadedTemplate = result.filename;
        } else {
            showMessage('保存失败: ' + result.error, 'error');
        }
        
    } catch (error) {
        showMessage('保存失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 将AI图片用作模板
function useAsTemplate(imageUrl) {
    uploadedTemplate = imageUrl.split('/').pop();
    showMessage('已设置为主图模板', 'success');
}

// 增强的图片预览功能
function displayImagePreview(containerId, imageUrl) {
    const container = document.getElementById(containerId);
    const imageId = containerId + 'Image';
    
    container.innerHTML = `
        <div class="position-relative">
            <img src="${imageUrl}" class="preview-image" alt="预览图片" id="${imageId}">
            <div class="mt-2 d-flex justify-content-between align-items-center">
                <small class="text-muted">图片已上传</small>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-secondary" onclick="rotateImage('${imageId}')">
                        <i class="bi bi-arrow-clockwise"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="removeImage('${containerId}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
}

// 旋转图片预览
function rotateImage(imageId) {
    const img = document.getElementById(imageId);
    if (img) {
        const currentRotation = img.style.transform.match(/rotate\((\d+)deg\)/) || [null, '0'];
        const newRotation = (parseInt(currentRotation[1]) + 90) % 360;
        img.style.transform = `rotate(${newRotation}deg)`;
    }
}

// 移除图片
function removeImage(containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '<div class="text-muted">暂无图片</div>';
    
    // 清空对应的全局变量
    if (containerId === 'templatePreview') {
        uploadedTemplate = null;
    } else if (containerId === 'referencePreview') {
        uploadedReference = null;
    }
}

// 增强的表单验证
function validateForm() {
    const title = document.getElementById('articleTitle').value.trim();
    const content = document.getElementById('articleContent').value.trim();
    
    if (!title) {
        showMessage('请输入文章标题', 'error');
        document.getElementById('articleTitle').focus();
        return false;
    }
    
    if (!content) {
        showMessage('请输入文章内容', 'error');
        document.getElementById('articleContent').focus();
        return false;
    }
    
    if (title.length > 50) {
        showMessage('标题长度不能超过50个字符', 'error');
        document.getElementById('articleTitle').focus();
        return false;
    }
    
    if (content.length < 50) {
        showMessage('文章内容至少需要50个字符', 'error');
        document.getElementById('articleContent').focus();
        return false;
    }
    
    return true;
}

// 自动保存草稿功能
function autoSaveDraft() {
    const title = document.getElementById('articleTitle').value;
    const content = document.getElementById('articleContent').value;
    
    if (title || content) {
        const draft = {
            title,
            content,
            timestamp: new Date().getTime()
        };
        localStorage.setItem('ecommerce_tool_draft', JSON.stringify(draft));
    }
}

// 加载草稿
function loadDraft() {
    const draft = localStorage.getItem('ecommerce_tool_draft');
    if (draft) {
        try {
            const data = JSON.parse(draft);
            if (data.title) document.getElementById('articleTitle').value = data.title;
            if (data.content) document.getElementById('articleContent').value = data.content;
            
            showMessage('已加载上次保存的草稿', 'info');
        } catch (e) {
            console.error('加载草稿失败:', e);
        }
    }
}

// 清除草稿
function clearDraft() {
    localStorage.removeItem('ecommerce_tool_draft');
    document.getElementById('articleTitle').value = '';
    document.getElementById('articleContent').value = '';
    showMessage('草稿已清除', 'info');
}

// 页面加载时自动加载草稿
document.addEventListener('DOMContentLoaded', function() {
    loadDraft();
    
    // 设置自动保存
    setInterval(autoSaveDraft, 30000); // 每30秒自动保存
    
    // 监听输入变化
    document.getElementById('articleTitle').addEventListener('input', autoSaveDraft);
    document.getElementById('articleContent').addEventListener('input', autoSaveDraft);
});

// AI模型管理功能
function initializeAIModelListeners() {
    // 模型类别切换
    document.querySelectorAll('input[name="modelCategory"]').forEach(radio => {
        radio.addEventListener('change', handleModelCategoryChange);
    });

    // 模型选择变化
    document.getElementById('aiModelDomestic').addEventListener('change', handleModelSelectionChange);
    document.getElementById('aiModelInternational').addEventListener('change', handleModelSelectionChange);
    document.getElementById('aiModelOpensource').addEventListener('change', handleModelSelectionChange);

    // API配置按钮
    document.getElementById('getApiKeyBtn').addEventListener('click', openApiKeyHelp);
    document.getElementById('testApiBtn').addEventListener('click', testApiConnection);
    document.getElementById('saveConfigBtn').addEventListener('click', saveApiConfig);

    // 初始化显示
    handleModelCategoryChange();
}

function handleModelCategoryChange() {
    const selectedCategory = document.querySelector('input[name="modelCategory"]:checked').value;
    
    // 隐藏所有模型选择
    document.getElementById('domesticModels').style.display = 'none';
    document.getElementById('internationalModels').style.display = 'none';
    document.getElementById('opensourceModels').style.display = 'none';
    
    // 显示对应的模型选择
    switch(selectedCategory) {
        case 'domestic':
            document.getElementById('domesticModels').style.display = 'block';
            break;
        case 'international':
            document.getElementById('internationalModels').style.display = 'block';
            break;
        case 'opensource':
            document.getElementById('opensourceModels').style.display = 'block';
            break;
    }
    
    handleModelSelectionChange();
}

function handleModelSelectionChange() {
    const selectedCategory = document.querySelector('input[name="modelCategory"]:checked').value;
    let selectedModel = '';
    
    // 获取当前选中的模型
    switch(selectedCategory) {
        case 'domestic':
            selectedModel = document.getElementById('aiModelDomestic').value;
            break;
        case 'international':
            selectedModel = document.getElementById('aiModelInternational').value;
            break;
        case 'opensource':
            selectedModel = document.getElementById('aiModelOpensource').value;
            break;
    }
    
    // 根据模型调整API配置界面
    updateApiConfigInterface(selectedModel);
    updateApiKeyHelp(selectedModel);
}

function updateApiConfigInterface(modelId) {
    const singleApiKey = document.getElementById('singleApiKey');
    const dualApiKeys = document.getElementById('dualApiKeys');
    
    // 需要双密钥的模型
    const dualKeyModels = ['baidu_wenxin', 'tencent_hunyuan'];
    
    if (dualKeyModels.includes(modelId)) {
        singleApiKey.style.display = 'none';
        dualApiKeys.style.display = 'block';
    } else {
        singleApiKey.style.display = 'block';
        dualApiKeys.style.display = 'none';
    }
}

function updateApiKeyHelp(modelId) {
    const helpText = document.getElementById('apiKeyHelp');
    const modelInfo = getModelInfo(modelId);
    
    if (modelInfo) {
        helpText.textContent = `请输入${modelInfo.name}的API密钥`;
        helpText.className = modelInfo.free ? 'text-success' : 'text-warning';
    }
}

function getModelInfo(modelId) {
    const modelInfoMap = {
        'baidu_wenxin': { name: '百度文心一格', free: true, url: 'https://console.bce.baidu.com/' },
        'ali_tongyi': { name: '阿里通义万相', free: true, url: 'https://dashscope.console.aliyun.com/' },
        'zhipu_cogview': { name: '智谱CogView', free: true, url: 'https://open.bigmodel.cn/' },
        'minimax_text2image': { name: 'MiniMax文生图', free: true, url: 'https://api.minimax.chat/' },
        'tencent_hunyuan': { name: '腾讯混元', free: true, url: 'https://console.cloud.tencent.com/' },
        'dalle3': { name: 'DALL-E 3', free: false, url: 'https://platform.openai.com/' },
        'stable_diffusion': { name: 'Stability AI', free: false, url: 'https://platform.stability.ai/' },
        'huggingface_diffusion': { name: 'Hugging Face', free: true, url: 'https://huggingface.co/' },
        'replicate_sdxl': { name: 'Replicate', free: true, url: 'https://replicate.com/' }
    };
    
    return modelInfoMap[modelId];
}

function openApiKeyHelp() {
    // 打开API密钥获取指南页面
    const helpWindow = window.open('/api-guide', '_blank', 'width=1000,height=800,scrollbars=yes');
    if (!helpWindow) {
        // 如果弹窗被阻止，显示提示
        showMessage('请允许弹窗以查看API密钥获取指南', 'warning');
    }
}

async function testApiConnection() {
    const apiConfig = getCurrentApiConfig();
    if (!apiConfig.model || !apiConfig.config.api_key) {
        showMessage('请先配置API密钥', 'warning');
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch('/api/test-ai-connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model_id: apiConfig.model,
                config: apiConfig.config
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('API连接测试成功！', 'success');
        } else {
            showMessage('API连接测试失败: ' + result.error, 'error');
        }
        
    } catch (error) {
        showMessage('连接测试失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function saveApiConfig() {
    const apiConfig = getCurrentApiConfig();
    if (!apiConfig.model || !apiConfig.config.api_key) {
        showMessage('请先配置API密钥', 'warning');
        return;
    }
    
    // 保存到localStorage
    const savedConfigs = JSON.parse(localStorage.getItem('ai_api_configs') || '{}');
    savedConfigs[apiConfig.model] = apiConfig.config;
    localStorage.setItem('ai_api_configs', JSON.stringify(savedConfigs));
    
    showMessage('API配置已保存', 'success');
}

function loadSavedApiConfigs() {
    const savedConfigs = JSON.parse(localStorage.getItem('ai_api_configs') || '{}');
    
    // 加载当前模型的配置
    const selectedCategory = document.querySelector('input[name="modelCategory"]:checked').value;
    let selectedModel = '';
    
    switch(selectedCategory) {
        case 'domestic':
            selectedModel = document.getElementById('aiModelDomestic').value;
            break;
        case 'international':
            selectedModel = document.getElementById('aiModelInternational').value;
            break;
        case 'opensource':
            selectedModel = document.getElementById('aiModelOpensource').value;
            break;
    }
    
    if (savedConfigs[selectedModel]) {
        const config = savedConfigs[selectedModel];
        
        if (config.api_key) {
            document.getElementById('apiKey').value = config.api_key;
        }
        
        if (config.secret_key) {
            document.getElementById('apiKeyPrimary').value = config.api_key;
            document.getElementById('apiKeySecondary').value = config.secret_key;
        }
    }
}

function getCurrentApiConfig() {
    const selectedCategory = document.querySelector('input[name="modelCategory"]:checked').value;
    let selectedModel = '';
    
    switch(selectedCategory) {
        case 'domestic':
            selectedModel = document.getElementById('aiModelDomestic').value;
            break;
        case 'international':
            selectedModel = document.getElementById('aiModelInternational').value;
            break;
        case 'opensource':
            selectedModel = document.getElementById('aiModelOpensource').value;
            break;
    }
    
    const config = {};
    const dualKeyModels = ['baidu_wenxin', 'tencent_hunyuan'];
    
    if (dualKeyModels.includes(selectedModel)) {
        config.api_key = document.getElementById('apiKeyPrimary').value.trim();
        config.secret_key = document.getElementById('apiKeySecondary').value.trim();
    } else {
        config.api_key = document.getElementById('apiKey').value.trim();
    }
    
    return {
        model: selectedModel,
        config: config
    };
}

// 增强的AI图片生成功能
async function generateAIImage() {
    const title = document.getElementById('articleTitle').value.trim();
    const content = document.getElementById('articleContent').value.trim();
    const apiConfig = getCurrentApiConfig();
    const imageSize = document.getElementById('imageSize').value;
    const imageStyle = document.getElementById('imageStyle').value;
    
    if (!title || !content) {
        showMessage('请输入完整的标题和内容', 'error');
        return;
    }
    
    if (!apiConfig.config.api_key) {
        showMessage('请配置API密钥', 'error');
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch('/api/generate-ai-image-enhanced', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title,
                content,
                model_id: apiConfig.model,
                config: apiConfig.config,
                size: imageSize,
                style: imageStyle
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayAIImageResult(result);
            showMessage(`${getModelInfo(apiConfig.model).name} 生成成功！`, 'success');
        } else {
            showMessage('AI生成失败: ' + result.error, 'error');
        }
        
    } catch (error) {
        showMessage('AI生成失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 页面加载时加载保存的配置
document.addEventListener('DOMContentLoaded', function() {
    // 延迟加载配置，确保UI已初始化
    setTimeout(() => {
        loadSavedApiConfigs();
    }, 500);
});

// 网络错误处理
window.addEventListener('unhandledrejection', function(event) {
    console.error('Promise错误:', event.reason);
    showMessage('网络请求失败，请检查网络连接', 'error');
});