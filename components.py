# components.py

# 기존 원본 templates.py의 디자인과 구조를 100% 유지합니다. 🕵️
ABOUT_SECTION = """
        <section id="about" class="bg-white p-16 rounded-3xl shadow-xl border border-gray-100">
            <div class="text-center mb-16">
                <h2 class="text-5xl font-black text-gray-900 font-poppins">About SixSense</h2>
                <div class="title-underline" style="width: 60px; height: 5px; background: #6366F1; margin: 15px auto 0; border-radius: 10px;"></div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-5 gap-16 items-center">
                <div class="md:col-span-3 text-gray-700 text-xl leading-relaxed space-y-6 font-medium">
                    <p>SixSense는 복잡한 문서 변환 과정을 단 한 번의 드래그로 해결합니다. 인프라 엔지니어의 시각에서 <span class="text-indigo-600 font-black">S3 연동 보안</span>과 <span class="text-indigo-600 font-black">병합 성능</span>을 최우선으로 설계되었습니다.</p>
                    <p>우리는 LibreOffice 엔진을 최적화하여 한글 깨짐 없는 완벽한 결과물을 보장하며, 모든 변환 데이터는 S3에 저장되어 5분간만 유효한 보안 링크를 통해 제공됩니다.</p>
                </div>
                <div class="md:col-span-2">
                    <div class="infra-card shadow-2xl" style="background: #312E81; color: #E0E7FF; border-radius: 2rem; padding: 2.5rem;">
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
"""

# 🚀 API 문서의 파라미터 정확도를 높였습니다. 🎖️
API_SECTION = """
        <section id="api" class="space-y-12">
            <div class="text-center">
                <h2 class="text-5xl font-black text-gray-900 font-poppins">Developer API</h2>
                <div class="title-underline" style="width: 60px; height: 5px; background: #6366F1; margin: 15px auto 0; border-radius: 10px;"></div>
            </div>
            <div class="api-box shadow-2xl" style="background: #111827; color: #A5B4FC; border-radius: 2rem; padding: 3rem; font-family: 'Courier New', monospace; position: relative; overflow: hidden;">
                <div class="api-label" style="position: absolute; top: 1.5rem; right: 2rem; font-size: 4rem; font-weight: 900; color: rgba(255,255,255,0.03); font-family: 'Poppins', sans-serif;">API</div>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
                    <div class="space-y-8">
                        <div>
                            <p class="text-gray-500 font-bold mb-3">// Single File Convert</p>
                            <p class="font-black text-2xl tracking-tight"><span class="text-purple-400">POST</span> <span class="text-green-400">/convert-single/</span></p>
                        </div>
                        <div class="pl-6 border-l-4 border-gray-800 space-y-1 text-sm">
                            <p class="text-indigo-300 font-bold mb-2">Payload (multipart/form-data)</p>
                            <p class="text-gray-400">file: <span class="text-white">document.docx</span></p>
                            <p class="text-gray-400">wm_type: <span class="text-white">text | image (Optional)</span></p>
                            <p class="text-gray-400">wm_text: <span class="text-white">"SIX SENSE" (Optional)</span></p>
                        </div>
                    </div>
                    <div class="space-y-8">
                        <div>
                            <p class="text-gray-500 font-bold mb-3">// Multi-File Merge & Convert</p>
                            <p class="font-black text-2xl tracking-tight"><span class="text-purple-400">POST</span> <span class="text-green-400">/convert-merge/</span></p>
                        </div>
                        <div class="pl-6 border-l-4 border-gray-800 space-y-1 text-sm">
                            <p class="text-indigo-300 font-bold mb-2">Payload (multipart/form-data)</p>
                            <p class="text-gray-400">files: <span class="text-white">file1.pdf, file2.xlsx... (Array)</span></p>
                            <p class="text-gray-400">wm_type: <span class="text-white">text | image (Optional)</span></p>
                            <p class="text-gray-400">wm_text: <span class="text-white">"SIX SENSE" (Optional)</span></p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
"""
