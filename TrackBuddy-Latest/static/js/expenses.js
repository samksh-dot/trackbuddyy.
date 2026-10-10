// Expenses & Group Split Logic
let localRecordedExpenses = [
  { id: '1', description: 'Auto to Amber Fort (2 autos)', amount: 280, paid_by: 'Aarav', category: 'Local Transport' },
  { id: '2', description: 'Rawat Pyaaz Kachori & Lassi', amount: 480, paid_by: 'Neha', category: 'Food' },
  { id: '3', description: 'Student Monuments Composite Pass (4x ₹100)', amount: 400, paid_by: 'Kabir', category: 'Attraction Tickets' },
  { id: '4', description: 'Zostel Jaipur Dorm Advance', amount: 2600, paid_by: 'Riya', category: 'Accommodation' }
];

const tripMembers = ['Aarav', 'Neha', 'Kabir', 'Riya'];

document.addEventListener('DOMContentLoaded', () => {
  const recalcBtn = document.getElementById('recalcBudgetBtn');
  if (recalcBtn) recalcBtn.addEventListener('click', calculateBudgetUI);

  const expForm = document.getElementById('recordExpenseForm');
  if (expForm) {
    expForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const desc = document.getElementById('expDesc').value;
      const amt = parseFloat(document.getElementById('expAmount').value) || 0;
      const cat = document.getElementById('expCategory').value;
      const paidBy = document.getElementById('expPaidBy').value;

      localRecordedExpenses.unshift({
        id: Date.now().toString(),
        description: desc,
        amount: amt,
        category: cat,
        paid_by: paidBy
      });

      document.getElementById('expDesc').value = '';
      document.getElementById('expAmount').value = '';
      TrackBuddy.showToast(`Recorded ₹${amt} paid by ${paidBy}`);
      renderGroupSplits();
    });
  }

  calculateBudgetUI();
  renderGroupSplits();
});

async function calculateBudgetUI() {
  const travelers = parseInt(document.getElementById('calcTravelers').value) || 4;
  const days = parseInt(document.getElementById('calcDays').value) || 2;
  const hotelPrice = parseFloat(document.getElementById('calcHotel').value) || 650;
  const rooms = parseInt(document.getElementById('calcRooms').value) || 4;
  const transit = parseFloat(document.getElementById('calcTransit').value) || 480;
  const tickets = parseFloat(document.getElementById('calcTickets').value) || 100;
  const food = parseFloat(document.getElementById('calcFood').value) || 350;
  const misc = parseFloat(document.getElementById('calcMisc').value) || 100;
  const discount = parseFloat(document.getElementById('calcDiscount').value) || 1000;

  try {
    const res = await fetch('/api/budget/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        travelers_count: travelers,
        days_count: days,
        hotel_price_per_night: hotelPrice,
        rooms_count: rooms,
        local_transit_est: transit,
        attraction_tickets_per_person: tickets,
        daily_food_per_person: food,
        misc_per_person: misc,
        student_discount_total: discount
      })
    });

    const b = await res.json();
    document.getElementById('dispEstSpent').textContent = '₹' + b.total_cost.toLocaleString('en-IN');
    document.getElementById('dispPerPerson').textContent = '₹' + b.per_person_cost.toLocaleString('en-IN');
    
    const totalBudget = 6000;
    const remaining = totalBudget - b.total_cost;
    document.getElementById('dispRemaining').textContent = '₹' + remaining.toLocaleString('en-IN');
    document.getElementById('dispRemaining').style.color = remaining >= 0 ? 'var(--sage-dark)' : 'var(--status-alert)';

    // Render Progress / Categories breakdown
    const barsContainer = document.getElementById('categoryBars');
    barsContainer.innerHTML = '<h4 style="margin-bottom: 10px; font-size: 0.95rem;">Category Allocation</h4>';

    (b.categories || []).forEach(cat => {
      const row = document.createElement('div');
      row.style.marginBottom = '10px';
      row.innerHTML = `
        <div style="display: flex; justify-content: space-between; font-size: 0.84rem; margin-bottom: 3px;">
          <span>${cat.category}</span>
          <span><strong>₹${cat.amount.toLocaleString('en-IN')}</strong> (${cat.percentage}%)</span>
        </div>
        <div style="width: 100%; height: 6px; background: var(--border-vintage); border-radius: 3px; overflow: hidden;">
          <div style="width: ${cat.percentage}%; height: 100%; background: var(--terracotta-primary);"></div>
        </div>
      `;
      barsContainer.appendChild(row);
    });
  } catch(e) {
    TrackBuddy.showToast("Budget calc error: " + e.message);
  }
}

function renderGroupSplits() {
  const total = localRecordedExpenses.reduce((s, e) => s + e.amount, 0);
  const fairShare = total / tripMembers.length;

  const paidMap = {};
  tripMembers.forEach(m => paidMap[m] = 0);
  localRecordedExpenses.forEach(e => {
    paidMap[e.paid_by] = (paidMap[e.paid_by] || 0) + e.amount;
  });

  const balances = {};
  tripMembers.forEach(m => {
    balances[m] = Math.round(paidMap[m] - fairShare);
  });

  // Calculate settlement transactions
  const debtors = [];
  const creditors = [];
  tripMembers.forEach(m => {
    if (balances[m] < -1) debtors.push({ name: m, amt: -balances[m] });
    else if (balances[m] > 1) creditors.push({ name: m, amt: balances[m] });
  });

  debtors.sort((a,b) => b.amt - a.amt);
  creditors.sort((a,b) => b.amt - a.amt);

  const settlements = [];
  let i = 0, j = 0;
  while (i < debtors.length && j < creditors.length) {
    const settle = Math.min(debtors[i].amt, creditors[j].amt);
    if (settle > 1) {
      settlements.push({ from: debtors[i].name, to: creditors[j].name, amt: settle });
      debtors[i].amt -= settle;
      creditors[j].amt -= settle;
    }
    if (debtors[i].amt <= 1) i++;
    if (creditors[j].amt <= 1) j++;
  }

  // Render settlements
  const setCont = document.getElementById('settlementsContainer');
  setCont.innerHTML = '';
  if (settlements.length === 0) {
    setCont.innerHTML = '<div style="font-size: 0.88rem; color: var(--sage-dark);">All group balances are settled even!</div>';
  } else {
    settlements.forEach(s => {
      const div = document.createElement('div');
      div.style.padding = '8px 12px';
      div.style.background = 'var(--bg-card-subtle)';
      div.style.borderRadius = 'var(--radius-sm)';
      div.style.marginBottom = '6px';
      div.style.fontSize = '0.9rem';
      div.innerHTML = `
        💸 <strong>${s.from}</strong> owes <strong>${s.to}</strong>: <span style="color: var(--terracotta-primary); font-weight: 700;">₹${Math.round(s.amt)}</span>
      `;
      setCont.appendChild(div);
    });
  }

  // Render expense list
  const list = document.getElementById('expenseList');
  list.innerHTML = '';
  localRecordedExpenses.forEach(e => {
    const item = document.createElement('div');
    item.style.padding = '8px 0';
    item.style.borderBottom = '1px solid var(--border-vintage)';
    item.style.fontSize = '0.85rem';
    item.style.display = 'flex';
    item.style.justifyContent = 'space-between';
    item.innerHTML = `
      <div>
        <strong>${e.description}</strong>
        <div style="font-size: 0.78rem; color: var(--ink-muted);">Paid by ${e.paid_by} • ${e.category}</div>
      </div>
      <div style="font-weight: 600; color: var(--terracotta-primary);">₹${e.amount}</div>
    `;
    list.appendChild(item);
  });
}
