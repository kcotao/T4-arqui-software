const API_URL = "http://127.0.0.1:8000/v1"; // backend threads
const ACCEPT = "application/vnd.threads.v1+json";

// NUEVO: microservicio messages
const MESSAGES_API_URL = "http://127.0.0.1:8001/v1/messages";
const MESSAGES_ACCEPT = "application/vnd.messages.v1+json";

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
  comments: $("#comments"),
  loadComments: $("#load-comments"),
};

let currentThreadId = null;

function showError(msg) {
  els.errors.textContent = msg;
  els.errors.hidden = !msg;
}

// --------------------- API ---------------------

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

// 🔹 Nueva función: obtener mensajes del microservicio messages
async function apiGetComments(threadId) {
  const url = `${MESSAGES_API_URL}?thread_id=${encodeURIComponent(threadId)}`;
  const res = await fetch(url, { headers: { Accept: MESSAGES_ACCEPT } });
  if (!res.ok) throw new Error(`GET /v1/messages → ${res.status} ${await res.text()}`);
  return res.json();
}

// --------------------- UI ---------------------

function renderList(items) {
  els.list.innerHTML = "";
  items.forEach((t) => {
    const li = els.tpl.content.firstElementChild.cloneNode(true);
    li.querySelector(".t-title").textContent = t.title;
    li.querySelector(".t-meta").textContent =
      `Canal: ${t.channel_id} · por ${t.created_by} · estado: ${t.status}`;

    // Abrir hilo
    li.querySelector(".btn-abrir").addEventListener("click", async () => {
      try {
        const full = await apiGetThread(t.id);
        currentThreadId = t.id; // guardar id actual para cargar comentarios
        els.dTitle.textContent = full.title;
        els.dMeta.textContent = `canal ${full.channel_id} · por ${full.created_by} · estado ${full.status}`;
        els.dJson.textContent = JSON.stringify(full, null, 2);
        els.comments.innerHTML = ""; // limpiar lista de comentarios
        els.dialog.showModal();
      } catch (e) {
        showError(String(e));
      }
    });

    // Archivar
    li.querySelector(".btn-archivar").addEventListener("click", async () => {
      try {
        await apiArchiveThread(t.id);
        await load();
      } catch (e) {
        showError(String(e));
      }
    });

    // Borrar
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

// --------------------- Eventos ---------------------

// Cargar comentarios desde el modal
els.loadComments.addEventListener("click", async () => {
  if (!currentThreadId) return;
  try {
    els.comments.innerHTML = "<li>Cargando...</li>";
    const comments = await apiGetComments(currentThreadId);
    els.comments.innerHTML = comments.length
      ? comments.map(c => `<li><strong>${c.author}:</strong> ${c.content}</li>`).join("")
      : "<li>Sin comentarios aún</li>";
  } catch (e) {
    showError(String(e));
  }
});



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

// --------------------- Inicio ---------------------
load();

