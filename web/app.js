const API_URL = "http://127.0.0.1:8000/v1"; // tu backend
const ACCEPT = "application/vnd.threads.v1+json";

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const els = {
  form: $("#new-thread-form"),
  channel: $("#channel"),
  title: $("#title"),
  createdBy: $("#created_by"),
  list: $("#threads"),
  tpl: $("#thread-item"),
  reload: $("#reload"),
  errors: $("#errors"),
  dialog: $("#detail"),
  dTitle: $("#d-title"),
  dMeta: $("#d-meta"),
  dJson: $("#d-json"),
  dClose: $("#d-close"),
};

function showError(msg) {
  els.errors.textContent = msg;
  els.errors.hidden = !msg;
}

async function apiGetThreads(channelId) {
  const url = channelId ? `${API_URL}?channel_id=${encodeURIComponent(channelId)}` : API_URL;
  const res = await fetch(url, { headers: { Accept: ACCEPT } });
  if (!res.ok) throw new Error(`GET /v1 → ${res.status} ${await res.text()}`);
  return res.json();
}

async function apiCreateThread({ channel_id, title, created_by }) {
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: ACCEPT },
    body: JSON.stringify({ channel_id, title, created_by }),
  });
  if (!res.ok) throw new Error(`POST /v1 → ${res.status} ${await res.text()}`);
  return res.json();
}

async function apiGetThread(id) {
  const res = await fetch(`${API_URL}/${encodeURIComponent(id)}`, { headers: { Accept: ACCEPT } });
  if (!res.ok) throw new Error(`GET /v1/${id} → ${res.status} ${await res.text()}`);
  return res.json();
}

async function apiArchiveThread(id) {
  const res = await fetch(`${API_URL}/${encodeURIComponent(id)}:archive`, {
    method: "POST",
    headers: { Accept: ACCEPT },
  });
  if (!res.ok) throw new Error(`POST /v1/${id}:archive → ${res.status} ${await res.text()}`);
  return res.json();
}

async function apiDeleteThread(id) {
  const res = await fetch(`${API_URL}/${encodeURIComponent(id)}`, {
    method: "DELETE",
    headers: { Accept: ACCEPT },
  });
  if (!res.ok && res.status !== 204) throw new Error(`DELETE /v1/${id} → ${res.status} ${await res.text()}`);
}

function renderList(items) {
  els.list.innerHTML = "";
  items.forEach((t) => {
    const li = els.tpl.content.firstElementChild.cloneNode(true);
    li.querySelector(".t-title").textContent = t.title;
    li.querySelector(".t-meta").textContent =
      `#${t.id} · canal: ${t.channel_id} · por ${t.created_by} · estado: ${t.status}`;

    li.querySelector(".btn-abrir").addEventListener("click", async () => {
      try {
        const full = await apiGetThread(t.id);
        els.dTitle.textContent = full.title;
        els.dMeta.textContent = `canal ${full.channel_id} · por ${full.created_by} · estado ${full.status}`;
        els.dJson.textContent = JSON.stringify(full, null, 2);
        els.dialog.showModal();
      } catch (e) {
        showError(String(e));
      }
    });

    li.querySelector(".btn-archivar").addEventListener("click", async () => {
      try {
        await apiArchiveThread(t.id);
        await load();
      } catch (e) {
        showError(String(e));
      }
    });

    li.querySelector(".btn-borrar").addEventListener("click", async () => {
      if (!confirm("¿Borrar hilo?")) return;
      try {
        await apiDeleteThread(t.id);
        await load();
      } catch (e) {
        showError(String(e));
      }
    });

    els.list.appendChild(li);
  });
}

async function load() {
  showError("");
  try {
    const channel = els.channel.value.trim();
    const data = await apiGetThreads(channel || undefined);
    renderList(data);
  } catch (e) {
    showError(String(e));
  }
}

els.form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  showError("");
  try {
    const payload = {
      channel_id: els.channel.value.trim(),
      title: els.title.value.trim(),
      created_by: els.createdBy.value.trim(),
    };
    if (!payload.channel_id || !payload.title || !payload.created_by) {
      showError("Completa todos los campos");
      return;
    }
    await apiCreateThread(payload);
    els.title.value = "";
    await load();
  } catch (e) {
    showError(String(e));
  }
});

els.reload.addEventListener("click", load);
els.dClose.addEventListener("click", () => els.dialog.close());

load();