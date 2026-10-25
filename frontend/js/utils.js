function validateINN(inn) {
    inn = inn.toString().trim();
    if (!/^\d+$/.test(inn)) return false;
    return inn.length === 10 || inn.length === 12;
}

function toggleConsent(isChecked) {
    const btnLogin = document.getElementById('btn-alfa-login');
    const btnSearch = document.getElementById('btn-inn-search');
    if (btnLogin) btnLogin.disabled = !isChecked;
    if (btnSearch) btnSearch.disabled = !isChecked;
}

function showToast(message, color = 'emerald') {
    const toast = document.getElementById('toast');
    const msg = document.getElementById('toast-msg');
    const icon = document.getElementById('toast-icon');
    msg.innerText = message;
    icon.className = color === 'rose' ? "fa-solid fa-circle-xmark text-rose-400" : "fa-solid fa-circle-check text-emerald-400";
    toast.classList.remove('translate-y-20', 'opacity-0');
    setTimeout(() => toast.classList.add('translate-y-20', 'opacity-0'), 3000);
}

function openDSModal() { document.getElementById('ds-modal').classList.remove('hidden'); }
function closeDSModal() { document.getElementById('ds-modal').classList.add('hidden'); }
function confirmDigitalSignature() {
    closeDSModal();
    showToast('Договор подписан! Средства отправлены.', 'emerald');
}