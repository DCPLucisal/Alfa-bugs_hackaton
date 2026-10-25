let selectedManagerAppId = null;

// Загрузка списка заявок
async function loadManagerDashboard() {
    const tbody = document.getElementById('manager-apps-table');
    tbody.innerHTML = '<tr><td colspan="4" class="py-4 text-center text-neutral-500">Загрузка...</td></tr>';
    
    try {
        const apps = await apiGetApplicationsAnalysis();
        if (!apps || apps.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="py-4 text-center text-neutral-500">Нет активных заявок</td></tr>';
            return;
        }

        tbody.innerHTML = apps.map(app => {
            const riskColor = app.risk_category === 'low' ? 'text-emerald-400' : app.risk_category === 'middle' ? 'text-amber-400' : 'text-rose-400';
            return `
                <tr class="hover:bg-neutral-900/50 cursor-pointer transition" onclick="selectManagerApp(${app.application_id})">
                    <td class="py-3 font-bold text-white">${app.name} ${app.lastname}</td>
                    <td class="py-3 text-neutral-300">${app.amount.toLocaleString('ru-RU')} ₽</td>
                    <td class="py-3"><span class="${riskColor} font-semibold">${app.status}</span></td>
                    <td class="py-3 text-right text-alfa-red font-bold">Выбрать &rarr;</td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4" class="py-4 text-center text-rose-400">Ошибка: ${err.message}</td></tr>`;
    }
}

// Клик по заявке
async function selectManagerApp(appId) {
    selectedManagerAppId = appId;
    const panel = document.getElementById('manager-details-panel');
    panel.innerHTML = '<div class="text-center py-10"><i class="fa-solid fa-circle-notch fa-spin text-alfa-red text-2xl"></i></div>';

    try {
        // 1. Получаем детали заявки
        const app = await apiGetApplicationById(appId);
        
        // 2. Запрашиваем AI-резюме для менеджера
        const ai = await apiManagerSummaryAI(appId);
        
        // 3. Рисуем панель
        panel.innerHTML = `
            <div class="flex justify-between items-start border-b border-neutral-800 pb-4">
                <div>
                    <span class="text-[11px] text-neutral-500 uppercase">Заявка #${appId}</span>
                    <h4 class="text-lg font-black text-white mt-1">${app.client_name} ${app.client_lastname}</h4>
                    <p class="text-xs text-neutral-400">ИНН: ${app.inn}</p>
                </div>
                <span class="px-2 py-1 rounded text-xs font-bold bg-neutral-800 text-white">${app.status}</span>
            </div>

            <div class="bg-alfa-cardBg p-4 rounded-xl border border-neutral-800 space-y-2 mt-4">
                <div class="flex items-center space-x-2 text-alfa-red text-xs font-bold uppercase">
                    <i class="fa-solid fa-brain"></i> <span>ИИ-Резюме</span>
                </div>
                <p class="text-xs text-neutral-300 leading-relaxed">${ai.ai_answer_text}</p>
            </div>

            <div class="space-y-2 text-xs text-neutral-400 mt-4 bg-neutral-950 p-4 rounded-xl border border-neutral-800">
                <div class="flex justify-between"><span>Сумма:</span><strong class="text-white">${app.amount.toLocaleString('ru-RU')} ₽</strong></div>
                <div class="flex justify-between"><span>Срок:</span><strong class="text-white">${app.term_value} мес.</strong></div>
                <div class="flex justify-between"><span>Балл скоринга:</span><strong class="text-white">${app.final_score || '—'}/100</strong></div>
                <div class="flex justify-between"><span>Риск:</span><strong class="text-white">${app.risk_category || '—'}</strong></div>
            </div>

            <div class="mt-4 space-y-2">
                <label class="text-xs font-bold text-neutral-400">Комментарий для клиента (опционально):</label>
                <textarea id="manager-comment" rows="2" class="w-full bg-neutral-950 border border-neutral-700 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-alfa-red" placeholder="Например: Требуется залог..."></textarea>
            </div>

            <div class="grid grid-cols-2 gap-3 pt-4 border-t border-neutral-800 mt-4">
                <button onclick="managerAction('approved')" class="bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-xl text-xs">Одобрить</button>
                <button onclick="managerAction('approved_with_conditions')" class="bg-amber-600 hover:bg-amber-500 text-white font-bold py-3 rounded-xl text-xs">С условиями</button>
                <button onclick="managerAction('info_requests')" class="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl text-xs">Запросить док.</button>
                <button onclick="managerAction('rejected_with_alternative')" class="bg-rose-600 hover:bg-rose-500 text-white font-bold py-3 rounded-xl text-xs">Отклонить</button>
            </div>
        `;
    } catch (err) {
        panel.innerHTML = `<p class="text-rose-400 text-sm">Ошибка: ${err.message}</p>`;
    }
}


async function managerAction(status) {
    if (!selectedManagerAppId) return;
    
    const comment = document.getElementById('manager-comment').value.trim();
    try {
        await apiUpdateApplication(selectedManagerAppId, { 
            status: status, 
            manager_comment: comment || null 
        });
        showToast(`Решение принято`, 'emerald');
        
        document.getElementById('manager-details-panel').innerHTML = `
            <div class="text-center py-10 space-y-3">
                <i class="fa-solid fa-check-circle text-emerald-500 text-4xl"></i>
                <p class="text-emerald-400 font-bold">Решение сохранено!</p>
                <p class="text-neutral-400 text-xs">Заявка убрана из списка активных.</p>
            </div>
        `;
        selectedManagerAppId = null;
        
        loadManagerDashboard(); 
        
    } catch (err) {
        showToast(`Ошибка: ${err.message}`, 'rose');
    }
}