const state = {
  token: localStorage.getItem('dd_access_token') || '',
  baseUrl: localStorage.getItem('dd_base_url') || 'http://localhost:8000',
  activeView: 'customer',
};

const el = (id) => document.getElementById(id);

const views = {
  customer: {
    title: 'Панель клиента',
    endpoint: '/api/bff/customer/dashboard/',
    node: el('customer-view'),
  },
  manager: {
    title: 'Панель менеджера',
    endpoint: '/api/bff/manager/dashboard/',
    node: el('manager-view'),
  },
  operator: {
    title: 'Панель оператора',
    endpoint: '/api/bff/operator/control/',
    node: el('operator-view'),
  },
};

function normalizeBaseUrl() {
  return el('base-url').value.replace(/\/$/, '');
}

function setText(id, value) {
  el(id).textContent = value;
}

function setStatus(message) {
  setText('auth-status', message);
}

async function api(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }

  const response = await fetch(`${state.baseUrl}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${response.status}: ${body || response.statusText}`);
  }

  return response.json();
}

function renderList(node, items, renderer, emptyText) {
  node.innerHTML = '';

  if (!items || items.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.textContent = emptyText;
    node.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    node.insertAdjacentHTML('beforeend', renderer(item));
  });
}

function missionCard(mission) {
  const drone = mission.drone ? `${mission.drone.serial_number}, ${mission.drone.battery_level}%` : 'дрон не назначен';
  return `
    <article class="list-item">
      <strong>Миссия #${mission.id}</strong>
      <p>${mission.delivery_address || 'адрес не указан'}</p>
      <p>Дрон: ${drone}</p>
      <span class="badge ${mission.status}">${mission.status}</span>
    </article>
  `;
}

function droneCard(drone) {
  return `
    <article class="list-item">
      <strong>${drone.serial_number}</strong>
      <p>${drone.model_name}</p>
      <p>Батарея: ${drone.battery_level}%</p>
      <span class="badge ${drone.status}">${drone.status}</span>
    </article>
  `;
}

function telemetryCard(item) {
  return `
    <article class="list-item">
      <strong>${item.serial_number || `Drone #${item.drone_id}`}</strong>
      <p>lat ${item.latitude}, lon ${item.longitude}</p>
      <p>Высота: ${item.altitude}, батарея: ${item.battery_level}%</p>
    </article>
  `;
}

function updateGlobalMetrics(data) {
  if (data.profile) {
    setText('metric-user', data.profile.username);
  }

  if (data.missions) {
    setText('metric-missions', data.missions.length);
  }

  if (data.ready_drones) {
    setText('metric-drones', data.ready_drones.length);
  }

  if (data.metrics) {
    setText('metric-missions', Object.values(data.metrics.missions_by_status || {}).reduce((a, b) => a + b, 0));
    setText('metric-drones', data.metrics.ready_drones);
  }
}

function renderCustomer(data) {
  updateGlobalMetrics(data);
  setText('customer-count', data.missions.length);
  setText('catalog-count', data.catalog_preview.length);
  renderList(el('customer-missions'), data.missions, missionCard, 'У клиента пока нет миссий');
  renderList(
    el('catalog-list'),
    data.catalog_preview,
    (item) => `
      <article class="catalog-item">
        <strong>${item.name}</strong>
        <p>${item.store_display}</p>
        <span class="badge">${item.price} руб.</span>
      </article>
    `,
    'Каталог пуст'
  );
}

function renderManager(data) {
  updateGlobalMetrics(data);
  setText('manager-count', data.missions.length);
  el('manager-metrics').innerHTML = Object.entries(data.metrics)
    .map(([key, value]) => {
      const safeValue = typeof value === 'object' ? JSON.stringify(value) : value;
      return `<div class="metric-row"><strong>${key}</strong>: ${safeValue}</div>`;
    })
    .join('');
  renderList(el('manager-missions'), data.missions, missionCard, 'Миссий нет');
}

function renderOperator(data) {
  updateGlobalMetrics(data);
  setText('operator-mission-count', data.new_missions.length);
  setText('operator-drone-count', data.ready_drones.length);
  setText('telemetry-count', data.telemetry.length);
  renderList(el('operator-missions'), data.new_missions, missionCard, 'Новых миссий нет');
  renderList(el('operator-drones'), data.ready_drones, droneCard, 'Готовых дронов нет');
  renderList(el('telemetry-list'), data.telemetry, telemetryCard, 'Телеметрия не поступала');
}

async function loadActiveView() {
  if (!state.token) {
    setStatus('Сначала получите JWT токен');
    return;
  }

  const view = views[state.activeView];
  const data = await api(view.endpoint);

  if (state.activeView === 'customer') renderCustomer(data);
  if (state.activeView === 'manager') renderManager(data);
  if (state.activeView === 'operator') renderOperator(data);
}

function switchView(nextView) {
  state.activeView = nextView;
  Object.entries(views).forEach(([key, view]) => {
    view.node.classList.toggle('active', key === nextView);
  });
  document.querySelectorAll('.tab-button').forEach((button) => {
    button.classList.toggle('active', button.dataset.view === nextView);
  });
  setText('view-title', views[nextView].title);
  loadActiveView().catch((error) => setStatus(error.message));
}

el('base-url').value = state.baseUrl;
if (state.token) setStatus('Токен сохранен в браузере');

el('login-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  state.baseUrl = normalizeBaseUrl();
  localStorage.setItem('dd_base_url', state.baseUrl);

  try {
    const data = await api('/api/token/', {
      method: 'POST',
      body: JSON.stringify({
        username: el('username').value,
        password: el('password').value,
      }),
    });
    state.token = data.access;
    localStorage.setItem('dd_access_token', state.token);
    setStatus('JWT токен получен');
    await loadActiveView();
  } catch (error) {
    setStatus(error.message);
  }
});

el('order-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const mission = await api('/api/bff/customer/dashboard/', {
      method: 'POST',
      body: JSON.stringify({
        delivery_address: el('delivery-address').value,
        order_content: JSON.parse(el('order-content').value),
      }),
    });
    setText('order-status', `Создана миссия #${mission.id}`);
    await loadActiveView();
  } catch (error) {
    setText('order-status', error.message);
  }
});

el('refresh-button').addEventListener('click', () => {
  loadActiveView().catch((error) => setStatus(error.message));
});

el('health-button').addEventListener('click', async () => {
  try {
    const data = await api('/api/bff/health/');
    setText('metric-api', data.status);
  } catch (error) {
    setText('metric-api', 'Ошибка');
    setStatus(error.message);
  }
});

document.querySelectorAll('.tab-button').forEach((button) => {
  button.addEventListener('click', () => switchView(button.dataset.view));
});
