document.addEventListener('DOMContentLoaded', function() {
    // form 객체 정의
    const accessKeyForm = document.getElementById('accessKeyForm');
    const workload_IdentityForm = document.getElementById('workload-IdentityForm');
    const get_image_form = document.getElementById('get-image-form');
    const get_image_gpt_form = document.getElementById('get-image-gpt-form');
    
    // 결과 출력 객체 정의
    const resultBox = document.getElementById('resultBox');
    const resultMessage = document.getElementById('resultMessage');

    // [추가] 로그 강조 및 렌더링 함수
    // [수정] 로그 강조 및 UI 데코레이션 함수
    function renderLog(message, isHTML = false, status = 'success') {
        const statusBadge = document.getElementById('statusBadge');
        const execTime = document.getElementById('execTime');
        const summaryInfo = document.getElementById('summaryInfo');

        // 1. 실행 시간 업데이트
        summaryInfo.style.display = 'block';
        execTime.textContent = new Date().toLocaleString();

        // 2. 상태 배지 생성 (Label)
        if (status === 'success') {
            statusBadge.innerHTML = '<span class="label label-success" style="font-size: 12px;">SUCCESS</span>';
        } else if (status === 'warning') {
            statusBadge.innerHTML = '<span class="label label-warning" style="font-size: 12px;">WARNING</span>';
        } else {
            statusBadge.innerHTML = '<span class="label label-danger" style="font-size: 12px;">FAILED</span>';
        }

        // 3. 로그 컬러링 로직 (기존 유지)
        if (isHTML) {
            resultMessage.innerHTML = message;
        } else {
            const lines = message.split('\n');
            const coloredLines = lines.map(line => {
                if (line.includes('✅') || line.includes('성공')) return `<span style="color: #a6e22e; font-weight: bold;">${line}</span>`; // 연두색
                if (line.includes('❌') || line.includes('실패')) return `<span style="color: #f92672; font-weight: bold;">${line}</span>`; // 핑크색
                if (line.includes('⚠️')) return `<span style="color: #fd971f; font-weight: bold;">${line}</span>`; // 오렌지색
                if (line.includes('🚀') || line.includes('Step')) return `<span style="color: #66d9ef; font-weight: bold;">${line}</span>`; // 하늘색
                return line;
            });
            resultMessage.innerHTML = coloredLines.join('\n');
        }
    }

    // [추가] 결과 영역 초기화 함수 (이미지 중복 방지)
    function prepareResult(msg = '처리 중...') {
        resultBox.style.display = 'block';
        // 기존에 생성된 이미지들 제거
        const existingImgs = resultBox.querySelectorAll("img");
        existingImgs.forEach(img => img.remove());
        renderLog(msg);
    }

    // 1. Access Key 인증
    accessKeyForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const connectionString = document.getElementById('connectionString').value;
        if (!connectionString) return alert('Connection String을 입력해주세요.');

        prepareResult('🚀 Access Key 인증 확인 중...');

        try {
            const response = await fetch('/StorageAccount/accesskey', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ connection_string: connectionString })
            });
            const result = await response.json();

            if (response.ok) {
                renderLog(`✅ 인증 성공:\n${result.message}`);
                resultBox.className = 'box box-success';
            } else {
                renderLog(`❌ 인증 실패: ${result.message || '알 수 없는 오류'}`);
                resultBox.className = 'box box-danger';
            }
        } catch (error) {
            renderLog(`❌ 오류 발생: ${error.message}`);
            resultBox.className = 'box box-danger';
        }
    });

    // 2. Workload Identity 인증
    workload_IdentityForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const account_url = document.getElementById('account_url').value;
        if (!account_url) return alert('Account URL을 입력해주세요.');

        prepareResult('🚀 Workload Identity 인증 확인 중...');

        try {
            const response = await fetch('/StorageAccount/workloadIdentity', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ account_url: account_url })
            });
            const result = await response.json();

            if (response.ok) {
                renderLog(`✅ 인증 성공:\n${result.message}`);
                resultBox.className = 'box box-success';
            } else {
                renderLog(`❌ 인증 실패: ${result.message || '알 수 없는 오류'}`);
                resultBox.className = 'box box-danger';
            }
        } catch (error) {
            renderLog(`❌ 오류 발생: ${error.message}`);
            resultBox.className = 'box box-danger';
        }
    });

    // 3. 이미지 가져오기 (일반)
    get_image_form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const account_url = document.getElementById('account_url_image').value;
        const container_name = document.getElementById('container_name_image').value;
        const blob_dir = document.getElementById('blob_dir_image').value;

        if (!account_url || !container_name || !blob_dir) return alert('모든 필드를 입력해주세요.');

        prepareResult('🚀 이미지를 불러오는 중...');

        try {
            const response = await fetch('/StorageAccount/get-image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ account_url, container_name, blob_dir })
            });

            if (response.ok) {
                const blob = await response.blob();
                const imgUrl = URL.createObjectURL(blob);
                
                const imgElement = document.createElement("img");
                imgElement.src = imgUrl;
                imgElement.style.maxWidth = "100%";
                imgElement.style.marginTop = "15px";
                imgElement.style.border = "2px solid #ddd";
                
                resultBox.appendChild(imgElement);
                renderLog("✅ 이미지를 성공적으로 가져왔습니다.");
                resultBox.className = 'box box-success';
            } else {
                const result = await response.json();
                renderLog(`❌ 오류: ${result.message || '이미지를 찾을 수 없습니다.'}`);
                resultBox.className = 'box box-danger';
            }
        } catch (error) {
            renderLog(`❌ 오류 발생: ${error.message}`);
            resultBox.className = 'box box-danger';
        }
    });

    // 4. 이미지 가져오기 + GPT 분석
    get_image_gpt_form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const account_url = document.getElementById('account_url_gpt').value;
        const container_name = document.getElementById('container_name_gpt').value;
        const blob_dir = document.getElementById('blob_dir_gpt').value;

        if (!account_url || !container_name || !blob_dir) return alert('모든 필드를 입력해주세요.');

        prepareResult('🚀 GPT가 이미지를 분석 중입니다. 잠시만 기다려주세요...');

        try {
            const response = await fetch('/StorageAccount/get-image-and-analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ account_url, container_name, blob_dir })
            });
            const result = await response.json();

            if (response.ok) {
                const imgUrl = `data:${result.mime_type};base64,${result.image_base64}`;
                
                const imgElement = document.createElement("img");
                imgElement.src = imgUrl;
                imgElement.style.maxWidth = "100%";
                imgElement.style.marginTop = "15px";
                imgElement.style.border = "2px solid #ddd";

                resultBox.appendChild(imgElement);
                renderLog(`<strong>🤖 LLM 분석 결과:</strong><br>${result.message}`, true);
                resultBox.className = 'box box-success';
            } else {
                renderLog(`❌ 분석 실패: ${result.message || '알 수 없는 오류'}`);
                resultBox.className = 'box box-danger';
            }
        } catch (error) {
            renderLog(`❌ 오류 발생: ${error.message}`);
            resultBox.className = 'box box-danger';
        }
    });
});