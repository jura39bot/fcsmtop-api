const API = '/api/v1';

async function get(path, params = {}) {
  const url = new URL(API + path, window.location.origin);
  Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  const r = await fetch(url);
  return r.json();
}

function resultBadge(r) {
  if (!r) return '—';
  return `<span class="badge badge-${r}">${{ W: '✓ V', D: '= N', L: '✗ D' }[r]}</span>`;
}

// ─── PAGE NATIONAL ────────────────────────────────────────────────────
async function loadNational() {
  // Classement
  try {
    const data = await get('/national/classement', { season: '2025' });
    const tbody = document.getElementById('tbody-classement');
    tbody.innerHTML = data.map(row => `
      <tr class="${row.team_short === 'FCSM' ? 'fcsm' : ''}">
        <td>${row.rank}</td>
        <td>${row.team}</td>
        <td>${row.played}</td>
        <td style="color:var(--green)">${row.won}</td>
        <td style="color:var(--yellow)">${row.drawn}</td>
        <td style="color:var(--red)">${row.lost}</td>
        <td>${row.goals_for}</td>
        <td>${row.goals_against}</td>
        <td>${row.goal_diff > 0 ? '+' : ''}${row.goal_diff}</td>
        <td><strong>${row.points}</strong></td>
      </tr>
    `).join('');
    document.getElementById('loading-classement').classList.add('hidden');
    document.getElementById('table-classement').classList.remove('hidden');
  } catch (e) { console.error('Classement:', e); }

  // Top buteurs + chart
  try {
    const data = await get('/national/buteurs', { season: '2025', limit: 10 });
    const tbody = document.getElementById('tbody-buteurs');
    tbody.innerHTML = data.map(row => `
      <tr>
        <td>${row.rank}</td>
        <td><strong>${row.full_name}</strong></td>
        <td>${row.team_short}</td>
        <td style="color:var(--green);font-weight:700">${row.goals}</td>
        <td>${row.assists}</td>
      </tr>
    `).join('');
    document.getElementById('loading-buteurs').classList.add('hidden');
    document.getElementById('table-buteurs').classList.remove('hidden');

    new Chart(document.getElementById('chart-buteurs'), {
      type: 'bar',
      data: {
        labels: data.slice(0, 10).map(r => r.full_name),
        datasets: [{
          label: 'Buts',
          data: data.slice(0, 10).map(r => r.goals),
          backgroundColor: data.slice(0, 10).map(r => r.team_short === 'FCSM' ? '#f5c518' : '#4caf50'),
          borderRadius: 4,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#888', font: { size: 11 } }, grid: { color: 'rgba(255,255,255,0.05)' } },
          y: { ticks: { color: '#888', stepSize: 1 }, grid: { color: 'rgba(255,255,255,0.05)' } },
        },
      },
    });
  } catch (e) { console.error('Buteurs:', e); }
}

// ─── PAGE FCSM ────────────────────────────────────────────────────────
async function loadFCSM() {
  // Forme
  try {
    const data = await get('/clubs/FCSM/form', { season: '2025', last: 5 });
    const balls = document.getElementById('form-display');
    balls.innerHTML = data.form_string.split('').map(c =>
      `<div class="form-ball ${c}">${c}</div>`
    ).join('');
    document.getElementById('form-stats').innerHTML = `
      <span><strong style="color:var(--green)">${data.wins}V</strong></span>
      <span><strong style="color:var(--yellow)">${data.draws}N</strong></span>
      <span><strong style="color:var(--red)">${data.losses}D</strong></span>
      <span>BP : <strong>${data.goals_scored}</strong></span>
      <span>BC : <strong>${data.goals_conceded}</strong></span>
    `;
  } catch (e) { console.error('Form:', e); }

  // Buteurs FCSM
  try {
    const data = await get('/clubs/FCSM/buteurs', { season: '2025' });
    const tbody = document.getElementById('tbody-fcsm-buteurs');
    tbody.innerHTML = data.map(r => `
      <tr>
        <td>${r.rank}</td>
        <td><strong>${r.full_name}</strong></td>
        <td style="color:var(--green);font-weight:700">${r.goals}</td>
        <td style="color:var(--text-muted)">${r.penalties || '—'}</td>
      </tr>
    `).join('');

    new Chart(document.getElementById('chart-fcsm-buteurs'), {
      type: 'doughnut',
      data: {
        labels: data.slice(0, 6).map(r => r.full_name),
        datasets: [{
          data: data.slice(0, 6).map(r => r.goals),
          backgroundColor: ['#f5c518','#4caf50','#2196F3','#ff9800','#9c27b0','#f44336'],
          borderWidth: 2, borderColor: '#1e293b',
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom', labels: { color: '#ccc', font: { size: 11 } } } },
      },
    });
  } catch (e) { console.error('FCSM buteurs:', e); }

  // Passeurs FCSM
  try {
    const data = await get('/clubs/FCSM/passeurs', { season: '2025' });
    const tbody = document.getElementById('tbody-fcsm-passeurs');
    tbody.innerHTML = data.map(r => `
      <tr>
        <td>${r.rank}</td>
        <td><strong>${r.full_name}</strong></td>
        <td style="color:var(--primary);font-weight:700">${r.assists}</td>
      </tr>
    `).join('');
  } catch (e) { console.error('FCSM passeurs:', e); }

  // Derniers matchs
  try {
    const data = await get('/clubs/FCSM/matches', { season: '2025', last: 10 });
    const tbody = document.getElementById('tbody-fcsm-matches');
    tbody.innerHTML = data.map(m => `
      <tr>
        <td>${m.matchday}</td>
        <td>${(m.match_date || '').slice(0, 10)}</td>
        <td>${m.home_team}</td>
        <td style="font-weight:700;text-align:center">${m.home_score ?? '?'} - ${m.away_score ?? '?'}</td>
        <td>${m.away_team}</td>
        <td>${resultBadge(m.result)}</td>
      </tr>
    `).join('');
  } catch (e) { console.error('FCSM matches:', e); }
}

// ─── INIT ─────────────────────────────────────────────────────────────
if (typeof PAGE !== 'undefined' && PAGE === 'fcsm') {
  loadFCSM();
} else {
  loadNational();
}
