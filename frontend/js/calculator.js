function updateCalculator() {
    const amount = parseInt(document.getElementById('amount-slider').value);
    const term = parseInt(document.getElementById('term-slider').value);
    const isStress = document.getElementById('stress-toggle').checked;

    window.appState.currentAmount = amount;
    window.appState.currentTerm = term;
    saveState();

    document.getElementById('amount-display').innerText = amount.toLocaleString('ru-RU') + ' ₽';
    document.getElementById('term-display').innerText = term + ' мес.';

    const annualRate = 0.185;
    const monthlyRate = annualRate / 12;
    const payment = (amount * monthlyRate * Math.pow(1 + monthlyRate, term)) / (Math.pow(1 + monthlyRate, term) - 1);
    
    document.getElementById('monthly-payment-display').innerHTML = Math.round(payment).toLocaleString('ru-RU') + ' ₽';
    document.getElementById('total-overpay-display').innerText = Math.round((payment * term) - amount).toLocaleString('ru-RU') + ' ₽';

    const stressPay = (amount * (0.215/12) * Math.pow(1 + (0.215/12), term)) / (Math.pow(1 + (0.215/12), term) - 1);
    const stressBox = document.getElementById('stress-result-box');

    if (isStress) {
        stressBox.className = "mt-4 opacity-100 bg-rose-950/20 p-5 rounded-xl border border-rose-500/30";
        document.getElementById('stress-payment-display').innerText = Math.round(stressPay).toLocaleString('ru-RU') + ' ₽ / мес';
        document.getElementById('stress-payment-display').className = "text-xl font-black text-rose-400";
    } else {
        stressBox.className = "mt-4 opacity-50 bg-neutral-900/50 p-5 rounded-xl border border-neutral-800";
        document.getElementById('stress-payment-display').innerText = "--- ₽ / мес";
        document.getElementById('stress-payment-display').className = "text-xl font-black text-neutral-400";
    }
}