
const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Init-Data": tg.initData
    }
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Помилка запиту");
  }

  return response.status === 204 ? null : response.json();
}

let timer;

function toast(message) {
  const el = $("toast");
  el.textContent = message;
  el.hidden = false;
  clearTimeout(timer);
  timer = setTimeout(() => {
    el.hidden = true;
  }, 2500);
}

function formatMoment(iso) {
  const [date, time] = iso.split("T");
  const [year, month, day] = date.split("-");
  return `${day}.${month}.${year} ${time.slice(0, 5)}`;
}

function statusLabel(item) {
  if (item.status === "sent") return "✅ надіслано";
  if (item.status === "failed") return `⚠️ ${item.error}`;
  return "⏳ чекає";
}

function render(items) {
  $("list").replaceChildren(...items.map((item) => {
    const title = document.createElement("div");
    title.textContent = `@${item.recipient}${item.repeat ? " 🔁" : ""}`;

    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = `${formatMoment(item.send_at)} · ${statusLabel(item)}`;

    const info = document.createElement("div");
    info.append(title, meta);

    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "✕";

    remove.onclick = async () => {
      try {
        await api(`/api/greetings/${item.id}`, {
          method: "DELETE"
        });
        await load();
      } catch (err) {
        toast(err.message);
      }
    };

    const li = document.createElement("li");
    li.append(info, remove);
    return li;
  }));
}

async function load() {
  const data = await api("/api/greetings");
  render(data.items);
  return data.styles;
}

async function showPreview() {
  const custom = $("text").value.trim();

  if (custom) {
    $("preview").textContent = custom;
    return;
  }

  const data = await api(
    `/api/preview?style=${encodeURIComponent($("style").value)}`
  );

  $("preview").textContent = data.text;
}

async function init() {
  const styles = await load();

  styles.forEach((s) => {
    $("style").add(new Option(s.title, s.key));
  });

  $("style").onchange = showPreview;
  $("text").oninput = showPreview;

  await showPreview();

  $("form").onsubmit = async (event) => {
    event.preventDefault();

    try {
      const localValue = $("when").value;

      if (!localValue) {
        throw new Error("Вкажіть дату та час");
      }

      const sendAt = new Date(localValue);

      if (Number.isNaN(sendAt.getTime())) {
        throw new Error("Некоректна дата");
      }

      await api("/api/greetings", {
        method: "POST",
        body: JSON.stringify({
          recipient: $("username").value,
          send_at: sendAt.toISOString(),
          style: $("style").value,
          text: $("text").value || null,
          repeat: $("repeat").checked
        })
      });

      $("form").reset();
      await showPreview();
      await load();

      toast("Заплановано");
    } catch (err) {
      toast(err.message);
    }
  };
}

init().catch((err) => toast(err.message));
