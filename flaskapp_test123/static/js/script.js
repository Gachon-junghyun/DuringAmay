window.addEventListener('DOMContentLoaded', () => {
  let prompts = {};
  const promptsSelect = document.getElementById('savedPrompts');
  const customInput = document.getElementById('customPrompt');
  const newKeyInput = document.getElementById('newPromptKey');
  const saveBtn = document.getElementById('saveBtn');
  const sendBtn = document.getElementById('sendBtn');
  const resetBtn = document.getElementById('resetBtn');
  const chatLog = document.getElementById('chatLog');

  // Load saved prompts
  function loadPrompts() {
    fetch('/prompts')
      .then(res => res.json())
      .then(data => {
        prompts = data.prompts;
        promptsSelect.innerHTML = '<option value="">-- choose prompt --</option>';
        for (const key in prompts) {
          const opt = document.createElement('option');
          opt.value = key;
          opt.textContent = prompts[key];
          promptsSelect.appendChild(opt);
        }
      });
  }
  loadPrompts();

  function appendMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${role}`;
    const span = document.createElement('span');
    span.textContent = text;
    msgDiv.appendChild(span);
    chatLog.appendChild(msgDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  saveBtn.addEventListener('click', () => {
    const key = newKeyInput.value.trim();
    const prompt = customInput.value.trim();
    if (!key || !prompt) return alert('Key and prompt text required');
    fetch('/prompts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, prompt })
    })
    .then(res => res.json())
    .then(res => {
      if (res.error) return alert(res.error);
      newKeyInput.value = '';
      customInput.value = '';
      loadPrompts();
      alert('Prompt saved!');
    });
  });

  sendBtn.addEventListener('click', () => {
    const promptId = promptsSelect.value;
    const prompt = customInput.value.trim();
    if (!promptId && !prompt) return alert('Provide a prompt!');

    appendMessage('user', promptId ? prompts[promptId] : prompt);

    fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt_id: promptId || undefined, prompt: prompt || undefined })
    })
    .then(res => res.json())
    .then(res => {
      if (res.error) return alert(res.error);
      appendMessage('assistant', res.response);
    });

    customInput.value = '';
    promptsSelect.value = '';
  });

  resetBtn.addEventListener('click', () => {
    fetch('/memory/reset', { method: 'POST' })
      .then(() => { chatLog.innerHTML = ''; });
  });
});