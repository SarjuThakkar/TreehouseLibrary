document.addEventListener('DOMContentLoaded', () => {
    const scanInput = document.getElementById('scan-input');

    // Auto-focus the hidden input on load
    if (scanInput) {
        scanInput.focus();
    }

    // Keep focus on the hidden input unless user is typing in another field
    // Keep focus on the hidden input unless user is typing in another field or clicking a button/link
    document.addEventListener('click', (e) => {
        if (!scanInput) return;

        const tag = e.target.tagName;
        if (tag !== 'INPUT' && tag !== 'TEXTAREA' && tag !== 'BUTTON' && tag !== 'A' && !e.target.closest('button') && !e.target.closest('a')) {
            scanInput.focus();
        }
    });
});
