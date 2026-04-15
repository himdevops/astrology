const form = document.getElementById('chartForm');
const output = document.getElementById('output');
const statusBox = document.getElementById('status');
const submitBtn = document.getElementById('submitBtn');
const apiBaseInput = document.getElementById('apiBase');

if (!apiBaseInput.value.trim()) {
  apiBaseInput.value = window.location.protocol === 'file:'
    ? 'http://127.0.0.1:8001'
    : window.location.origin;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const payload = {
    name: document.getElementById('name').value.trim(),
    date: document.getElementById('date').value,
    time: document.getElementById('time').value,
    place: document.getElementById('place').value.trim(),
    ayanamsa: document.getElementById('ayanamsa').value,
  };

  const apiBase = apiBaseInput.value.trim().replace(/\/$/, '');

  statusBox.className = 'status';
  statusBox.textContent = 'Calculating...';
  output.textContent = 'Waiting for response...';
  submitBtn.disabled = true;

  try {
    const response = await fetch(`${apiBase}/chart`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(typeof data === 'object' ? JSON.stringify(data, null, 2) : String(data));
    }

    statusBox.className = 'status success';
    statusBox.textContent = 'Chart calculated successfully';
    output.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    statusBox.className = 'status error';
    statusBox.textContent = 'Request failed';
    output.textContent = error.message;
  } finally {
    submitBtn.disabled = false;
  }
});
