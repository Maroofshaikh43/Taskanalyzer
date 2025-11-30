async function analyzeTasks() {
  const text = document.getElementById('taskInput').value;
  let tasks;

  // Parse user input JSON
  try {
    tasks = JSON.parse(text);
    if (!Array.isArray(tasks)) throw new Error('Not array');
  } catch (e) {
    alert('Invalid JSON. Please supply an array of tasks.');
    return;
  }

  // Optional strategy field
  const strategy = document.getElementById('strategy')?.value || null;

  // Payload that also instructs backend to save tasks
  const payload = {
    save: true,
    tasks: tasks,
    strategy: strategy
  };

  // Single backend call
  try {
    const resp = await fetch('/api/tasks/analyze/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      alert('Server error: ' + JSON.stringify(err));
      return;
    }

    const sorted = await resp.json();

    // If backend returns {results: [...]} → use sorted.results
    displayResults(sorted);
  } catch (err) {
    console.error(err);
    alert('Failed to contact backend. Make sure Django server is running.');
  }
}


function displayResults(list) {
  const container = document.getElementById('results');
  container.innerHTML = '';

  list.forEach(item => {
    const score = item.score || 0;

    let cls = 'low';
    if (score > 100) cls = 'high';
    else if (score > 40) cls = 'medium';

    const div = document.createElement('div');
    div.className = 'task-card ' + cls;

    div.innerHTML = `
      <strong>${item.title}</strong>
      <span class="small">score: ${score}</span>
      <div class="small">
        Due: ${item.due_date || 'N/A'}
        • Importance: ${item.importance || 'N/A'}
        • Est hours: ${item.estimated_hours || 'N/A'}
      </div>
    `;

    container.appendChild(div);
  });
}


// Button listener
document.getElementById('analyzeBtn').addEventListener('click', analyzeTasks);
