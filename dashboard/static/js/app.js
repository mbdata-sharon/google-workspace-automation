/* Google Workspace Automation - Dashboard JS */

const API = "";

// Navigation
document.querySelectorAll(".nav-links li").forEach((item) => {
    item.addEventListener("click", () => {
        document.querySelectorAll(".nav-links li").forEach((i) => i.classList.remove("active"));
        document.querySelectorAll(".section").forEach((s) => s.classList.remove("active"));

        item.classList.add("active");
        const section = item.dataset.section;
        document.getElementById(section).classList.add("active");

        if (section === "overview") loadOverview();
        if (section === "gmail") loadEmails();
        if (section === "calendar") loadTodayEvents();
        if (section === "drive") loadRecentFiles();
    });
});

// --- OVERVIEW ---
async function loadOverview() {
    try {
        const [emails, events, files, storage] = await Promise.all([
            fetch(`${API}/api/gmail/unread`).then((r) => r.json()),
            fetch(`${API}/api/calendar/today`).then((r) => r.json()),
            fetch(`${API}/api/drive/recent`).then((r) => r.json()),
            fetch(`${API}/api/drive/storage`).then((r) => r.json()),
        ]);

        document.getElementById("unread-count").textContent = emails.emails?.length || 0;
        document.getElementById("events-count").textContent = events.events?.length || 0;
        document.getElementById("files-count").textContent = files.files?.length || 0;
        document.getElementById("storage-info").textContent = `${storage.used_gb} GB`;
    } catch (e) {
        console.error("Error cargando overview:", e);
    }
}

document.getElementById("btn-summary")?.addEventListener("click", async () => {
    const box = document.getElementById("ai-summary");
    box.textContent = "Generando resumen con IA...";
    try {
        const res = await fetch(`${API}/api/gmail/summary`);
        const data = await res.json();
        box.textContent = data.summary;
    } catch (e) {
        box.textContent = "Error al generar resumen.";
    }
});

// --- GMAIL ---
let currentReplyEmail = null;

async function loadEmails() {
    const container = document.getElementById("email-list");
    container.innerHTML = '<div class="loading">Cargando emails...</div>';
    try {
        const res = await fetch(`${API}/api/gmail/unread`);
        const data = await res.json();

        if (!data.emails?.length) {
            container.innerHTML = '<div class="loading">No hay emails no leidos</div>';
            return;
        }

        container.innerHTML = data.emails
            .map(
                (email) => `
            <div class="list-item">
                <div class="list-item-info">
                    <h4>${escapeHtml(email.subject)}</h4>
                    <p>${escapeHtml(email.from)} - ${email.date}</p>
                    <p>${escapeHtml(email.snippet?.substring(0, 120))}...</p>
                </div>
                <div class="list-item-actions">
                    <button class="btn" onclick="openReplyModal('${email.id}', '${email.thread_id}', '${escapeHtml(email.subject)}')">Responder con IA</button>
                </div>
            </div>
        `
            )
            .join("");
    } catch (e) {
        container.innerHTML = '<div class="loading">Error al cargar emails</div>';
    }
}

document.getElementById("btn-triage")?.addEventListener("click", async () => {
    const container = document.getElementById("email-list");
    container.innerHTML = '<div class="loading">Clasificando emails...</div>';
    try {
        const res = await fetch(`${API}/api/gmail/triage`);
        const data = await res.json();

        let html = "";

        if (data.urgent?.length) {
            html += '<h3>Urgente</h3>';
            html += data.urgent.map((e) => emailItem(e, "urgent")).join("");
        }
        if (data.important?.length) {
            html += '<h3 style="margin-top:16px">Importante</h3>';
            html += data.important.map((e) => emailItem(e, "important")).join("");
        }
        if (data.low?.length) {
            html += `<h3 style="margin-top:16px">Baja prioridad (${data.low.length})</h3>`;
            html += data.low.map((e) => emailItem(e, "low")).join("");
        }

        container.innerHTML = html || '<div class="loading">Inbox vacio</div>';
    } catch (e) {
        container.innerHTML = '<div class="loading">Error en triage</div>';
    }
});

function emailItem(email, priority) {
    return `
        <div class="list-item">
            <div class="list-item-info">
                <span class="badge badge-${priority}">${priority}</span>
                <h4>${escapeHtml(email.subject)}</h4>
                <p>${escapeHtml(email.from)}</p>
            </div>
            <div class="list-item-actions">
                <button class="btn" onclick="openReplyModal('${email.id}', '${email.thread_id || ""}', '${escapeHtml(email.subject)}')">Responder</button>
            </div>
        </div>`;
}

document.getElementById("btn-refresh-email")?.addEventListener("click", loadEmails);

// Reply Modal
function openReplyModal(messageId, threadId, subject) {
    currentReplyEmail = { messageId, threadId };
    document.getElementById("reply-original").textContent = `Respondiendo a: ${subject}`;
    document.getElementById("reply-instruction").value = "";
    document.getElementById("reply-draft").classList.add("hidden");
    document.getElementById("btn-send-reply").classList.add("hidden");
    document.getElementById("reply-modal").classList.remove("hidden");
}

document.getElementById("btn-cancel-reply")?.addEventListener("click", () => {
    document.getElementById("reply-modal").classList.add("hidden");
});

document.getElementById("btn-generate-reply")?.addEventListener("click", async () => {
    const instruction = document.getElementById("reply-instruction").value;
    if (!instruction) return;

    const draftBox = document.getElementById("reply-draft");
    draftBox.textContent = "Generando respuesta con IA...";
    draftBox.classList.remove("hidden");

    try {
        const res = await fetch(`${API}/api/gmail/reply`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message_id: currentReplyEmail.messageId,
                thread_id: currentReplyEmail.threadId,
                instruction: instruction,
            }),
        });
        const data = await res.json();
        draftBox.textContent = data.draft;
        document.getElementById("btn-send-reply").classList.remove("hidden");
    } catch (e) {
        draftBox.textContent = "Error al generar respuesta.";
    }
});

document.getElementById("btn-send-reply")?.addEventListener("click", async () => {
    const instruction = document.getElementById("reply-instruction").value;
    try {
        const res = await fetch(`${API}/api/gmail/reply/confirm`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message_id: currentReplyEmail.messageId,
                thread_id: currentReplyEmail.threadId,
                instruction: instruction,
            }),
        });
        const data = await res.json();
        if (data.status === "replied") {
            document.getElementById("reply-modal").classList.add("hidden");
            loadEmails();
        }
    } catch (e) {
        alert("Error al enviar respuesta");
    }
});

// --- CALENDAR ---
async function loadTodayEvents() {
    const container = document.getElementById("calendar-events");
    container.innerHTML = '<div class="loading">Cargando eventos...</div>';
    try {
        const res = await fetch(`${API}/api/calendar/today`);
        const data = await res.json();

        if (!data.events?.length) {
            container.innerHTML = '<div class="loading">No hay eventos hoy</div>';
            return;
        }

        container.innerHTML = data.events
            .map((event) => {
                const time = event.start.includes("T") ? event.start.split("T")[1].substring(0, 5) : "Todo el dia";
                return `
                <div class="list-item">
                    <div class="list-item-info">
                        <h4>${time} - ${escapeHtml(event.summary)}</h4>
                        <p>${event.location ? "Lugar: " + escapeHtml(event.location) : ""}</p>
                    </div>
                </div>`;
            })
            .join("");
    } catch (e) {
        container.innerHTML = '<div class="loading">Error al cargar eventos</div>';
    }
}

document.getElementById("btn-today")?.addEventListener("click", loadTodayEvents);
document.getElementById("btn-week")?.addEventListener("click", async () => {
    const container = document.getElementById("calendar-events");
    container.innerHTML = '<div class="loading">Cargando semana...</div>';
    try {
        const res = await fetch(`${API}/api/calendar/upcoming?days=7`);
        const data = await res.json();

        if (!data.events?.length) {
            container.innerHTML = '<div class="loading">No hay eventos esta semana</div>';
            return;
        }

        let html = "";
        let currentDate = "";
        data.events.forEach((event) => {
            const date = event.start.split("T")[0];
            if (date !== currentDate) {
                currentDate = date;
                html += `<h3 style="margin:16px 0 8px">${date}</h3>`;
            }
            const time = event.start.includes("T") ? event.start.split("T")[1].substring(0, 5) : "Todo el dia";
            html += `
                <div class="list-item">
                    <div class="list-item-info">
                        <h4>${time} - ${escapeHtml(event.summary)}</h4>
                    </div>
                </div>`;
        });
        container.innerHTML = html;
    } catch (e) {
        container.innerHTML = '<div class="loading">Error al cargar semana</div>';
    }
});

// --- DRIVE ---
async function loadRecentFiles() {
    const container = document.getElementById("drive-files");
    container.innerHTML = '<div class="loading">Cargando archivos...</div>';
    try {
        const res = await fetch(`${API}/api/drive/recent`);
        const data = await res.json();

        container.innerHTML = data.files
            .map(
                (file) => `
            <div class="list-item">
                <div class="list-item-info">
                    <h4>${escapeHtml(file.name)}</h4>
                    <p>Modificado: ${file.modified?.substring(0, 10)} | ${escapeHtml(file.owner || "")}</p>
                </div>
                <div class="list-item-actions">
                    ${file.link ? `<a href="${file.link}" target="_blank" class="btn">Abrir</a>` : ""}
                </div>
            </div>
        `
            )
            .join("");
    } catch (e) {
        container.innerHTML = '<div class="loading">Error al cargar archivos</div>';
    }
}

document.getElementById("btn-search-drive")?.addEventListener("click", async () => {
    const query = document.getElementById("drive-search").value;
    if (!query) return;

    const container = document.getElementById("drive-files");
    container.innerHTML = '<div class="loading">Buscando...</div>';
    try {
        const res = await fetch(`${API}/api/drive/search`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
        });
        const data = await res.json();

        if (!data.files?.length) {
            container.innerHTML = `<div class="loading">No se encontraron archivos para: "${escapeHtml(query)}"</div>`;
            return;
        }

        container.innerHTML = data.files
            .map(
                (file) => `
            <div class="list-item">
                <div class="list-item-info">
                    <h4>${escapeHtml(file.name)}</h4>
                    <p>Modificado: ${file.modified?.substring(0, 10)}</p>
                </div>
                <div class="list-item-actions">
                    ${file.link ? `<a href="${file.link}" target="_blank" class="btn">Abrir</a>` : ""}
                </div>
            </div>
        `
            )
            .join("");
    } catch (e) {
        container.innerHTML = '<div class="loading">Error al buscar</div>';
    }
});

// --- UTILS ---
function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Load overview on start
loadOverview();
