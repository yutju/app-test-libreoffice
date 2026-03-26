# templates.py

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SixSense Doc-Converter | 프리미엄 변환 & 병합 서비스</title>

    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Poppins:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">

    <style>
        :root {
            --primary: #4F46E5;
            --primary-dark: #4338CA;
            --bg-main: #F9FAFB;
            --text-main: #1F2937;
            --glass-bg: rgba(255, 255, 255, 0.8);
            --glass-border: rgba(255, 255, 255, 0.2);
        }

        body { font-family: 'Noto Sans KR', sans-serif; background-color: var(--bg-main); color: var(--text-main); scroll-behavior: smooth; }
        .font-poppins { font-family: 'Poppins', sans-serif; }

        .gradient-bg {
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
        }
        @keyframes gradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

        .glass-card { background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); }
        .hover-lift { transition: transform 0.3s ease, box-shadow 0.3s ease; }
        .hover-lift:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }

        .drop-zone { border: 3px dashed #d1d5db; transition: all 0.3s ease; cursor: pointer; min-height: 250px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
        .drop-zone.active { border-color: var(--primary); background-color: #EEF2FF; }

        .tab-btn { transition: all 0.3s ease; border-radius: 9999px; font-weight: 800; padding: 0.75rem 2.5rem; }
        .tab-btn.active { background-color: var(--primary); color: white; box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4); }
        .tab-btn.inactive { background-color: #E5E7EB; color: #6B7280; }

        .title-underline { width: 60px; height: 5px; background: #6366F1; margin: 15px auto 0; border-radius: 10px; }
        .infra-card { background: #312E81; color: #E0E7FF; border-radius: 2rem; padding: 2.5rem; }
        .api-box { background: #111827; color: #A5B4FC; border-radius: 2rem; padding: 3rem; font-family: 'Courier New', monospace; position: relative; overflow: hidden; }
        .api-label { position: absolute; top: 1.5rem; right: 2rem; font-size: 4rem; font-weight: 900; color: rgba(255,255,255,0.03); font-family: 'Poppins', sans-serif; }
        
        .loader-ring { display: inline-block; width: 80px; height: 80px; position: relative; }
        .loader-ring div { box-sizing: border-box; display: block; position: absolute; width: 64px; height: 64px; margin: 8px; border: 8px solid var(--primary); border-radius: 50%; animation: loader-ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite; border-color: var(--primary) transparent transparent transparent; }
        @keyframes loader-ring { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body class="min-h-screen">

    <nav class="glass-card sticky top-0 z-50 border-b shadow-sm">
        <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div class="flex items-center space-x-2">
                <span class="text-3xl">👀</span>
                <span class="text-3xl font-extrabold tracking-tighter text-gray-900 font-poppins">SixSense</span>
            </div>
            <div class="flex items-center space-x-8 text-sm font-bold text-gray-600">
                <a href="#convert" class="hover:text-indigo-600 transition">변환하기</a>
                <a href="#about" class="hover:text-indigo-600 transition">서비스 소개</a>
                <a href="#api" class="hover:text-indigo-600 transition">API 문서</a>
                <button class="bg-indigo-600 text-white px-6 py-2.5 rounded-full hover:bg-indigo-700 transition shadow-lg">Cloud Native</button>
            </div>
        </div>
    </nav>

    <header class="gradient-bg py-24 text-white text-center">
        <div class="max-w-5xl mx-auto px-6">
            <h1 class="text-6xl font-black tracking-tight leading-tight font-poppins mb-6">단 한 번의 드래그로,<br>모든 문서를 <span class="text-yellow-300">완벽한 PDF</span>로</h1>
            <p class="text-xl font-light opacity-90">인프라 엔지니어를 위한 듀얼 엔진 변환 서비스</p>
        </div>
    </header>

    <main id="convert" class="max-w-7xl mx-auto px-6 -mt-20 space-y-20 pb-32 relative z-10">

        <div class="glass-card p-12 rounded-3xl shadow-2xl hover-lift">
            <div class="flex justify-center space-x-4 mb-10 bg-gray-100 p-2 rounded-full w-max mx-auto">
                <button id="btnSingle" class="tab-btn active">단일 파일 변환</button>
                <button id="btnMerge" class="tab-btn inactive">다중 파일 병합</button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-12 items-start">
                <div class="md:col-span-1 pr-6 border-r border-gray-100 sticky top-32">
                    <h2 id="guideTitle" class="text-3xl font-black text-gray-900 mb-6">스마트 업로드</h2>
                    <p id="guideDesc" class="text-gray-600 mb-8 leading-relaxed">PNG, JPG, DOCX, HWP, TXT 파일을 지원합니다. (최대 100MB)</p>
                    <div class="space-y-4">
                        <div class="flex items-center space-x-3 text-sm text-green-700 font-bold bg-green-50 p-4 rounded-xl border border-green-100">✅ 나눔고딕 한글 완벽 지원</div>
                        <div class="flex items-center space-x-3 text-sm text-indigo-700 font-bold bg-indigo-50 p-4 rounded-xl border border-indigo-100">✅ S3 보안 스토리지 연동</div>
                    </div>
                </div>

                <div class="md:col-span-2">
                    <div id="sectionSingle" class="space-y-6">
                        <div id="dropZoneSingle" class="drop-zone rounded-3xl bg-gray-50 hover:bg-white transition shadow-inner p-10">
                            <div class="text-6xl mb-6">📄</div>
                            <p class="text-2xl font-black text-gray-800">단일 파일을 드래그하세요</p>
                            <input type="file" id="inputSingle" class="hidden">
                        </div>
                        <div id="infoSingle" class="hidden bg-indigo-50 p-6 rounded-2xl border border-indigo-200 flex justify-between items-center shadow-sm">
                            <div class="flex items-center space-x-4 truncate">
                                <span class="text-2xl">📎</span>
                                <span id="nameSingle" class="text-indigo-900 font-black text-lg truncate"></span>
                            </div>
                            <button type="button" onclick="resetSingle()" class="text-red-500 text-2xl font-bold">❌</button>
                        </div>
                        <button onclick="handleSingleUpload()" class="w-full bg-indigo-600 text-white font-black py-6 rounded-2xl text-2xl shadow-xl hover:bg-indigo-700 transition transform hover:-translate-y-1">PDF 단일 변환 ✨</button>
                    </div>

                    <div id="sectionMerge" class="hidden space-y-6">
                        <div id="dropZoneMerge" class="drop-zone rounded-3xl bg-gray-50 hover:bg-white transition shadow-inner p-10">
                            <div class="text-6xl mb-6">📚</div>
                            <p class="text-2xl font-black text-gray-800">여러 파일을 드래그하세요</p>
                            <p class="text-sm text-gray-500 mt-2">최대 10개 파일 자동 병합</p>
                            <input type="file" id="inputMerge" class="hidden" multiple>
                        </div>
                        <div id="listMerge" class="hidden space-y-3 max-h-64 overflow-y-auto p-2">
                            </div>
                        <button onclick="handleMergeUpload()" class="w-full bg-indigo-600 text-white font-black py-6 rounded-2xl text-2xl shadow-xl hover:bg-indigo-700 transition transform hover:-translate-y-1">통합 PDF 병합 시작 🚀</button>
                    </div>
                </div>
            </div>
        </div>

        <section id="about" class="bg-white p-16 rounded-3xl shadow-xl border border-gray-100">
            <div class="text-center mb-16">
                <h2 class="text-5xl font-black text-gray-900 font-poppins">About SixSense</h2>
                <div class="title-underline"></div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-5 gap-16 items-center">
                <div class="md:col-span-3 text-gray-700 text-xl leading-relaxed space-y-6 font-medium">
                    <p>SixSense는 복잡한 문서 변환 과정을 단 한 번의 드래그로 해결합니다. 인프라 엔지니어의 시각에서 <span class="text-indigo-600 font-black">S3 연동 보안</span>과 <span class="text-indigo-600 font-black">병합 성능</span>을 최우선으로 설계되었습니다.</p>
                    <p>우리는 LibreOffice 엔진을 최적화하여 한글 깨짐 없는 완벽한 결과물을 보장하며, 모든 변환 데이터는 S3에 저장되어 5분간만 유효한 보안 링크를 통해 제공됩니다.</p>
                </div>
                <div class="md:col-span-2">
                    <div class="infra-card shadow-2xl">
                        <h3 class="text-2xl font-black mb-8 font-poppins text-white border-b border-indigo-400 pb-4">Core Infrastructure</h3>
                        <ul class="space-y-5 text-lg font-bold">
                            <li class="flex items-center text-indigo-100"><span class="mr-3 text-indigo-400">•</span> S3 & IAM Integration</li>
                            <li class="flex items-center text-indigo-100"><span class="mr-3 text-indigo-400">•</span> EC2 Auto Scaling Nodes</li>
                            <li class="flex items-center text-indigo-100"><span class="mr-3 text-indigo-400">•</span> Ansible Configuration</li>
                            <li class="flex items-center text-indigo-100"><span class="mr-3 text-indigo-400">•</span> Prometheus Monitoring</li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <section id="api" class="space-y-12">
            <div class="text-center">
                <h2 class="text-5xl font-black text-gray-900 font-poppins">Developer API</h2>
                <div class="title-underline"></div>
            </div>
            <div class="api-box shadow-2xl">
                <div class="api-label">API</div>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
                    <div class="space-y-8">
                        <div>
                            <p class="text-gray-500 font-bold mb-3">// Single File Convert</p>
                            <p class="font-black text-2xl tracking-tight"><span class="text-purple-400">POST</span> <span class="text-green-400">/convert-single/</span></p>
                        </div>
                        <div class="pl-6 border-l-4 border-gray-800">
                            <p class="text-indigo-300 font-bold mb-2">Payload (multipart)</p>
                            <p class="text-gray-400">file: <span class="text-white">document.hwp</span></p>
                        </div>
                    </div>
                    <div class="space-y-8">
                        <div>
                            <p class="text-gray-500 font-bold mb-3">// Multi-File Merge</p>
                            <p class="font-black text-2xl tracking-tight"><span class="text-purple-400">POST</span> <span class="text-green-400">/convert-merge/</span></p>
                        </div>
                        <div class="pl-6 border-l-4 border-gray-800">
                            <p class="text-indigo-300 font-bold mb-2">Payload (multipart)</p>
                            <p class="text-gray-400">files: <span class="text-white">file1.pdf, file2.jpg...</span></p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <p class="text-center text-gray-400 font-bold mt-12">© 2026 SixSense Project | Built for Infrastructure Engineers</p>
    </main>

    <div id="loadingScreen" class="hidden fixed inset-0 bg-gray-900 bg-opacity-80 flex items-center justify-center z-50 backdrop-blur-md">
        <div class="bg-white p-16 rounded-3xl text-center shadow-2xl">
            <div class="loader-ring mx-auto mb-8"><div></div></div>
            <p id="loadingText" class="text-3xl font-black text-gray-900 animate-pulse">엔진 가동 중...</p>
        </div>
    </div>

    <div id="resultArea" class="hidden fixed inset-0 bg-gray-900 bg-opacity-90 flex items-center justify-center z-50 backdrop-blur-xl transition-all duration-300 opacity-0 transform scale-95">
        <div class="bg-white p-20 rounded-3xl text-center shadow-2xl border-4 border-green-500 max-w-2xl w-full mx-6">
            <span class="text-9xl">🎉</span>
            <h2 class="text-6xl font-black text-green-800 mt-10 tracking-tighter">변환 성공!</h2>
            <p class="text-green-700 mt-6 text-2xl font-bold">S3 보안 링크가 생성되었습니다.</p>
            <a id="downloadLink" href="#" target="_blank" class="inline-block mt-16 gradient-bg text-white font-black p-8 w-full rounded-2xl text-4xl shadow-2xl hover:opacity-95 transition transform hover:-translate-y-2">📥 다운로드</a>
            <button onclick="location.reload()" class="mt-10 text-gray-400 hover:text-gray-600 text-lg font-bold underline">새로운 문서 처리하기</button>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <script>
        const btnSingle = document.getElementById('btnSingle');
        const btnMerge = document.getElementById('btnMerge');
        const sectionSingle = document.getElementById('sectionSingle');
        const sectionMerge = document.getElementById('sectionMerge');
        const guideTitle = document.getElementById('guideTitle');
        const guideDesc = document.getElementById('guideDesc');

        // 탭 스위치 로직
        btnSingle.onclick = () => {
            btnSingle.className = "tab-btn active";
            btnMerge.className = "tab-btn inactive";
            sectionSingle.classList.remove('hidden');
            sectionMerge.classList.add('hidden');
            guideTitle.textContent = "스마트 업로드";
            guideDesc.textContent = "PNG, JPG, DOCX, HWP, TXT 파일을 지원합니다. (최대 100MB)";
        };

        btnMerge.onclick = () => {
            btnMerge.className = "tab-btn active";
            btnSingle.className = "tab-btn inactive";
            sectionMerge.classList.remove('hidden');
            sectionSingle.classList.add('hidden');
            guideTitle.textContent = "다중 병합 모드";
            guideDesc.textContent = "여러 문서를 순서대로 합쳐 하나의 PDF로 생성합니다. (최대 10개)";
        };

        // 단일 파일 핸들링
        const dropZoneSingle = document.getElementById('dropZoneSingle');
        const inputSingle = document.getElementById('inputSingle');
        const infoSingle = document.getElementById('infoSingle');
        const nameSingle = document.getElementById('nameSingle');
        let singleFile = null;

        dropZoneSingle.onclick = () => inputSingle.click();
        inputSingle.onchange = (e) => {
            singleFile = e.target.files[0];
            if(singleFile) {
                nameSingle.textContent = singleFile.name;
                infoSingle.classList.remove('hidden');
            }
        };

        function resetSingle() {
            singleFile = null;
            inputSingle.value = '';
            infoSingle.classList.add('hidden');
        }

        async function handleSingleUpload() {
            if(!singleFile) return alert('파일을 선택해주세요.');
            const formData = new FormData();
            formData.append('file', singleFile);
            showLoading("엔진 가동 중...");
            try {
                const res = await axios.post('/convert-single/', formData);
                showResult(res.data.download_url);
            } catch (err) { alert('변환 실패!'); hideLoading(); }
        }

        // 다중 파일 핸들링
        const dropZoneMerge = document.getElementById('dropZoneMerge');
        const inputMerge = document.getElementById('inputMerge');
        const listMerge = document.getElementById('listMerge');
        let mergeFiles = [];

        dropZoneMerge.onclick = () => inputMerge.click();
        inputMerge.onchange = (e) => {
            mergeFiles = Array.from(e.target.files).slice(0, 10);
            updateMergeList();
        };

        function updateMergeList() {
            if(mergeFiles.length > 0) {
                listMerge.classList.remove('hidden');
                listMerge.innerHTML = mergeFiles.map((f, i) => `
                    <div class="bg-white border border-gray-200 p-4 rounded-xl flex justify-between shadow-sm">
                        <span class="font-bold text-gray-700">${i+1}. ${f.name}</span>
                        <span class="text-xs text-gray-400 font-mono">${(f.size/1024).toFixed(1)}KB</span>
                    </div>
                `).join('');
            } else { listMerge.classList.add('hidden'); }
        }

        async function handleMergeUpload() {
            if(mergeFiles.length < 1) return alert('파일을 1개 이상 선택해주세요.');
            const formData = new FormData();
            mergeFiles.forEach(f => formData.append('files', f));
            showLoading("여러 문서 병합 중...");
            try {
                const res = await axios.post('/convert-merge/', formData);
                showResult(res.data.download_url);
            } catch (err) { alert('병합 실패!'); hideLoading(); }
        }

        // 공통 UI 함수
        function showLoading(text) {
            document.getElementById('loadingText').textContent = text;
            document.getElementById('loadingScreen').classList.remove('hidden');
        }
        function hideLoading() { document.getElementById('loadingScreen').classList.add('hidden'); }
        function showResult(url) {
            hideLoading();
            const ra = document.getElementById('resultArea');
            document.getElementById('downloadLink').href = url;
            ra.classList.remove('hidden');
            setTimeout(() => { ra.classList.remove('opacity-0', 'scale-95'); }, 10);
        }

        // 드래그 앤 드롭 (공통)
        [dropZoneSingle, dropZoneMerge].forEach(dz => {
            dz.addEventListener('dragover', (e) => { e.preventDefault(); dz.classList.add('active'); });
            dz.addEventListener('dragleave', () => dz.classList.remove('active'));
            dz.addEventListener('drop', (e) => {
                e.preventDefault();
                dz.classList.remove('active');
                if(dz === dropZoneSingle) {
                    singleFile = e.dataTransfer.files[0];
                    nameSingle.textContent = singleFile.name;
                    infoSingle.classList.remove('hidden');
                } else {
                    mergeFiles = Array.from(e.dataTransfer.files).slice(0, 10);
                    updateMergeList();
                }
            });
        });
    </script>
</body>
</html>
"""
