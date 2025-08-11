function addEnterListenerToChatTextarea() {
    var textareas = document.querySelectorAll('textarea[placeholder="Type your question and press Enter..."]');
    textareas.forEach(function(textarea) {
        if (!textarea._enterListenerAdded) {
            textarea.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    var sendBtn = document.querySelector('[id="send-btn"]');
                    if (sendBtn) sendBtn.click();
                }
            });
            textarea._enterListenerAdded = true;
        }
    });
}
setInterval(addEnterListenerToChatTextarea, 500); 