// AI Assistant Frontend Logic
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('chatForm');
  const input = document.getElementById('chatInput');
  const chatMessages = document.getElementById('chatMessages');

  // Quick prompt buttons
  document.querySelectorAll('.quick-prompt-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      input.value = btn.textContent;
      form.dispatchEvent(new Event('submit'));
    });
  });

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const query = input.value.trim();
      if (!query) return;

      // Add user message
      appendMessage('user', query);
      input.value = '';

      const sendBtn = document.getElementById('chatSendBtn');
      sendBtn.disabled = true;

      // Add typing indicator
      const typingIndicator = appendMessage('assistant', 'Thinking and retrieving grounded travel facts...');

      try {
        const activeTrip = TrackBuddy.getActiveTrip();
        const res = await fetch('/api/assistant/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: query,
            trip_context: activeTrip
          })
        });

        const data = await res.json();
        typingIndicator.remove();

        if (data.provider) {
          document.getElementById('aiProviderBadge').textContent = data.provider;
        }

        appendMessage('assistant', data.response);
      } catch(err) {
        typingIndicator.remove();
        appendMessage('assistant', "⚠️ Connection error: " + err.message);
      } finally {
        sendBtn.disabled = false;
      }
    });
  }

  function appendMessage(sender, text) {
    const msg = document.createElement('div');
    msg.style.maxWidth = '80%';
    msg.style.padding = '12px 16px';
    msg.style.borderRadius = 'var(--radius-sm)';
    msg.style.fontSize = '0.92rem';
    msg.style.lineHeight = '1.6';

    if (sender === 'user') {
      msg.style.alignSelf = 'flex-end';
      msg.style.background = 'var(--terracotta-primary)';
      msg.style.color = '#FFFFFF';
      msg.textContent = text;
    } else {
      msg.style.alignSelf = 'flex-start';
      msg.style.background = '#FFFFFF';
      msg.style.color = 'var(--ink-primary)';
      msg.style.border = '1px solid var(--border-vintage)';
      // Convert markdown bold and lists simply for readability
      msg.innerHTML = formatMarkdown(text);
    }

    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msg;
  }

  function formatMarkdown(str) {
    if (!str) return '';
    let formatted = str
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n•/g, '<br>•')
      .replace(/\n(\d+\.)/g, '<br>$1');
    return formatted;
  }
});
