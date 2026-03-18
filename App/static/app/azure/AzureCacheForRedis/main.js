/**
 * Azure Cache For Redis 운영 도구 전용 스크립트
 */
document.addEventListener('DOMContentLoaded', function() {
    // 1. DOM 요소 캐싱
    const elements = {
        accessKeyForm: document.getElementById('accessKeyForm'),
        workloadIdentityForm: document.getElementById('workload-IdentityForm'),
        ttlCheckForm: document.getElementById('ttl-CheckForm'),
        resultBox: document.getElementById('resultBox'),
        resultMessage: document.getElementById('resultMessage')
    };

    /**
     * 로그 텍스트 분석 및 컬러링 렌더링
     */
    function renderLog(message) {
        if (!message) return;
        
        const lines = message.split('\n');
        const coloredLines = lines.map(line => {
            if (line.includes('✅')) return `<span style="color: #28a745; font-weight: bold;">${line}</span>`; 
            if (line.includes('❌') || line.includes('Error')) return `<span style="color: #dc3545; font-weight: bold;">${line}</span>`;
            if (line.includes('⚠️') || line.includes('💡')) return `<span style="color: #fd7e14; font-weight: bold;">${line}</span>`;
            if (line.includes('🚀') || line.includes('Step')) return `<span style="color: #007bff; font-weight: bold;">${line}</span>`;
            return line;
        });
        
        elements.resultMessage.innerHTML = coloredLines.join('\n');
    }

    /**
     * 서버 요청 공통 함수
     */
    async function sendRequest(url, payload, successClass = 'box-success') {
        elements.resultMessage.textContent = '🚀 처리 중...';
        elements.resultBox.style.display = 'block';
        elements.resultBox.className = 'box box-warning'; // 진행 중일 때 주황색

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (response.ok) {
                renderLog(result.message);
                elements.resultBox.className = `box ${successClass}`;
            } else {
                renderLog(result.message || '❌ 알 수 없는 오류가 발생했습니다.');
                elements.resultBox.className = 'box box-danger';
            }
        } catch (error) {
            console.error(`${url} Error:`, error);
            renderLog(`❌ 통신 중 예외 발생: ${error.message}`);
            elements.resultBox.className = 'box box-danger';
        }
    }

    // --- 이벤트 리스너 등록 ---

    // 1. Access Key 인증
    elements.accessKeyForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const payload = {
            redis_host: document.getElementById('redis_host').value,
            redis_port: document.getElementById('redis_port').value,
            redis_username: document.getElementById('redis_username').value,
            redis_password: document.getElementById('redis_password').value
        };

        if (!payload.redis_host || !payload.redis_password) {
            alert('필수 정보를 입력해주세요.');
            return;
        }
        sendRequest('/Redis/accesskey', payload);
    });

    // 2. Workload Identity 인증
    elements.workloadIdentityForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const payload = {
            redis_host: document.getElementById('redis_host_wi').value,
            redis_port: document.getElementById('redis_port_wi').value
        };
        sendRequest('/Redis/workloadIdentity', payload);
    });

    // 3. TTL Check 점검
    elements.ttlCheckForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const payload = {
            redis_host: document.getElementById('redis_host_ttl').value,
            redis_port: document.getElementById('redis_port_ttl').value
        };
        sendRequest('/Redis/TTL_Check', payload);
    });
});