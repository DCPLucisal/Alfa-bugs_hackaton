async function checkStatusAndRender() {
    const appId = window.appState.currentApplicationId;
    const container = document.getElementById('result-container');
    
    if (!appId) {
        container.innerHTML = `<p class="text-center text-neutral-400 py-8">Заявка не создана</p>`;
        return;
    }
    
    try {
        const app = await apiGetApplicationById(appId);
        const status = app.status;
        const amount = app.amount || window.appState.currentAmount || 0;

        if (status === 'validating' || status === 'scoring' || status === 'draft') {
            container.innerHTML = `
                <div class="text-center py-10 space-y-4">
                    <i class="fa-solid fa-hourglass-half text-amber-500 text-5xl animate-pulse"></i>
                    <h2 class="text-2xl font-black text-white">Заявка отправлена менеджеру</h2>
                    <p class="text-neutral-400">Пожалуйста, ожидайте решения.</p>
                </div>
            `;
            return;
        } 


        container.innerHTML = `<div class="text-center py-10"><i class="fa-solid fa-circle-notch fa-spin text-alfa-red text-2xl"></i></div>`;
        
        let finalAiText = app.manager_comment || window.appState.aiExplanation;
        try {
            const aiResult = await apiClientResultAI(appId);
            if (aiResult && aiResult.ai_answer_text) {
                finalAiText = aiResult.ai_answer_text;
            }
        } catch (e) {
            console.log("Не удалось сгенерировать ответ ИИ:", e);
        }
        

        if (status === 'approved') {
            container.innerHTML = `
                <div class="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-6 space-y-4">
                    <div class="flex items-center space-x-3">
                        <div class="w-12 h-12 rounded-full bg-emerald-500 flex items-center justify-center text-white text-xl"><i class="fa-solid fa-check"></i></div>
                        <div>
                            <span class="text-xs text-emerald-400 font-bold uppercase tracking-wider">Заявка одобрена</span>
                            <h3 class="text-xl font-black text-white">Кредит на ${amount.toLocaleString('ru-RU')} ₽</h3>
                        </div>
                    </div>
                    <p class="text-sm text-neutral-300 leading-relaxed">${finalAiText}</p>
                </div>
                <button onclick="openDSModal()" class="w-full bg-alfa-red hover:bg-alfa-redHover text-white font-bold py-4 rounded-2xl shadow-lg transition"><i class="fa-solid fa-file-signature mr-2"></i> Подписать договор</button>
            `;
        }
        else if (status === 'approved_with_conditions') {
            const conditionsText = app.manager_comment || 'Менеджер предложил изменить условия. Свяжитесь с ним для уточнения.';
            
            container.innerHTML = `
                <div class="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-6 space-y-4">
                    <div class="flex items-center space-x-3">
                        <div class="w-12 h-12 rounded-full bg-amber-500 flex items-center justify-center text-white text-xl">
                            <i class="fa-solid fa-triangle-exclamation"></i>
                        </div>
                        <div>
                            <span class="text-xs text-amber-400 font-bold uppercase tracking-wider">Одобрено с условиями</span>
                            <h3 class="text-xl font-black text-white">Требуется согласование новых условий</h3>
                        </div>
                    </div>

                    <!-- Условия менеджера -->
                    <div class="bg-neutral-900/50 p-4 rounded-xl border border-amber-500/20 text-sm text-neutral-300 leading-relaxed">
                        <p class="font-bold text-amber-400 mb-2 flex items-center gap-2">
                            <i class="fa-solid fa-list-check"></i> Предложение менеджера:
                        </p>
                        <p>${conditionsText}</p>
                    </div>

                    <!-- Резюме от ИИ -->
                    <p class="text-xs text-neutral-400 italic border-t border-amber-500/10 pt-3">
                        <i class="fa-solid fa-robot mr-1"></i> ИИ-ассистент: ${finalAiText}
                    </p>
                </div>

                <!-- Одна кнопка на всю ширину -->
                <button onclick="acceptConditions()" class="w-full bg-amber-600 hover:bg-amber-500 text-white font-bold py-4 rounded-2xl shadow-lg transition">
                    <i class="fa-solid fa-check mr-2"></i> Согласен с условиями
                </button>
            `;
        }
        else if (status === 'rejected_with_alternative' || status === 'rejected') {
            container.innerHTML = `
                <div class="bg-rose-500/10 border border-rose-500/30 rounded-2xl p-6 space-y-4">
                    <div class="flex items-center space-x-3">
                        <div class="w-12 h-12 rounded-full bg-rose-500 flex items-center justify-center text-white text-xl"><i class="fa-solid fa-xmark"></i></div>
                        <div>
                            <span class="text-xs text-rose-400 font-bold uppercase tracking-wider">Заявка отклонена</span>
                            <h3 class="text-xl font-black text-white">К сожалению, мы не можем одобрить кредит</h3>
                        </div>
                    </div>
                    <div class="bg-neutral-900/50 p-4 rounded-xl border border-rose-500/20 text-sm text-neutral-300 leading-relaxed">
                        <p class="font-bold text-rose-400 mb-1"><i class="fa-solid fa-robot mr-1"></i> Объяснение от ИИ:</p>
                        ${finalAiText}
                    </div>
                </div>
            `;
        }
        else if (status === 'info_requests') {
            container.innerHTML = `
                <div class="bg-blue-500/10 border border-blue-500/30 rounded-2xl p-6 space-y-4">
                    <div class="flex items-center space-x-3">
                        <div class="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center text-white text-xl"><i class="fa-solid fa-folder-open"></i></div>
                        <div>
                            <span class="text-xs text-blue-400 font-bold uppercase tracking-wider">Требуются документы</span>
                            <h3 class="text-xl font-black text-white">Запрос дополнительной информации</h3>
                        </div>
                    </div>
                    <div class="bg-neutral-900/50 p-4 rounded-xl border border-blue-500/20 text-sm text-neutral-300 leading-relaxed">
                        <p class="font-bold text-blue-400 mb-1"><i class="fa-solid fa-robot mr-1"></i> Комментарий менеджера:</p>
                        ${finalAiText}
                    </div>
                    <p class="text-xs text-neutral-500">Пожалуйста, загрузите запрошенные документы в личном кабинете.</p>
                </div>
                <button onclick="showToast('Переход к загрузке документов (демо)', 'emerald')" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-2xl shadow-lg transition">
                    <i class="fa-solid fa-upload mr-2"></i> Загрузить документы
                </button>
            `;
        }
    } catch (err) {
        container.innerHTML = `<p class="text-rose-400">Ошибка загрузки статуса: ${err.message}</p>`;
    }
}