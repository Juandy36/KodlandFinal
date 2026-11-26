"use strict";
const { test, beforeEach } = require("node:test");
const assert = require("node:assert/strict");
const {
  FakeElement,
  FakeText,
  createDocument,
  fakeEvent,
  loadScript,
  flush,
} = require("./fake-dom.js");

// Monta el DOM minimo de bot.html (ids y clases que usa bot.js).
function buildBotDom() {
  const form = new FakeElement("form");
  const input = new FakeElement("input");
  const messages = new FakeElement("div");
  const chatBox = new FakeElement("div");
  const submit = new FakeElement("button");
  submit.setAttribute("type", "submit");
  form.queryMap['button[type="submit"]'] = submit;
  // requestSubmit: en un navegador dispara el evento submit.
  form.requestSubmit = function () {
    this.dispatchEvent(fakeEvent("submit"));
  };

  const doc = createDocument({
    "chat-form": form,
    "user-message": input,
    messages,
    "chat-box": chatBox,
  });
  const chips = ["hola", "frenos"].map((texto) => {
    const chip = new FakeElement("button");
    chip.setAttribute("data-mensaje", texto);
    return chip;
  });
  doc.selectorAllMap["[data-mensaje]"] = chips;

  return { doc, form, input, messages, chatBox, submit, chips };
}

// fetch falso: registra cada llamada y responde con el handler dado.
function fakeFetch(handler) {
  const calls = [];
  const fn = (url, opts) => {
    calls.push({ url, opts });
    return handler(url, opts);
  };
  fn.calls = calls;
  return fn;
}

function okJson(body) {
  return Promise.resolve({ ok: true, status: 200, json: async () => body });
}

function lastBubble(messages) {
  return messages.children[messages.children.length - 1];
}

beforeEach(() => {
  globalThis.fetch = fakeFetch(() => okJson({ response: "ok" }));
});

test("no envia mensajes vacios ni solo espacios", async () => {
  const dom = buildBotDom();
  dom.input.value = "   ";
  loadScript("bot.js", dom.doc);

  const event = fakeEvent("submit");
  dom.form.dispatchEvent(event);
  await flush();

  assert.equal(event.defaultPrevented, true);
  assert.equal(globalThis.fetch.calls.length, 0);
  assert.equal(dom.messages.children.length, 0);
  assert.equal(dom.input.focusCalls, 1);
});

test("envia el mensaje recortado, muestra la burbuja del usuario y bloquea el boton mientras espera", async () => {
  const dom = buildBotDom();
  dom.input.value = "  hola  ";
  let resolveRequest;
  globalThis.fetch = fakeFetch(
    () => new Promise((resolve) => (resolveRequest = resolve))
  );
  loadScript("bot.js", dom.doc);

  dom.form.dispatchEvent(fakeEvent("submit"));

  const [call] = globalThis.fetch.calls;
  assert.equal(call.url, "/enviar_mensaje");
  assert.equal(call.opts.method, "POST");
  assert.equal(JSON.parse(call.opts.body).message, "hola");
  assert.equal(dom.submit.disabled, true);
  assert.equal(dom.input.value, "");
  assert.equal(lastBubble(dom.messages).className, "user-message");

  resolveRequest({ ok: true, status: 200, json: async () => ({ response: "Hola!" }) });
  await flush();

  assert.equal(dom.submit.disabled, false);
  const bot = lastBubble(dom.messages);
  assert.equal(bot.className, "bot-message");
  assert.equal(bot.children[1].textContent, "Hola!");
});

test("la respuesta se pinta como texto, nunca como HTML", async () => {
  const dom = buildBotDom();
  const payload = '<img src=x onerror="alert(1)"><b>x</b>';
  globalThis.fetch = fakeFetch(() => okJson({ response: payload }));
  dom.input.value = "hola";
  loadScript("bot.js", dom.doc);

  dom.form.dispatchEvent(fakeEvent("submit"));
  await flush();

  const bot = lastBubble(dom.messages);
  // Solo el prefijo oculto (span) y un nodo de texto; ningun elemento creado.
  assert.equal(bot.children.length, 2);
  assert.ok(bot.children[1] instanceof FakeText);
  assert.equal(bot.children[1].textContent, payload);
});

test("una respuesta en lista se une con saltos de linea", async () => {
  const dom = buildBotDom();
  globalThis.fetch = fakeFetch(() =>
    okJson({ response: ["¿Has revisado X?", "Otra opción: Y"] })
  );
  dom.input.value = "aceleracion";
  loadScript("bot.js", dom.doc);

  dom.form.dispatchEvent(fakeEvent("submit"));
  await flush();

  assert.equal(lastBubble(dom.messages).children[1].textContent,
    "¿Has revisado X?\nOtra opción: Y");
});

test("error de red: muestra aviso de error, reactiva el boton y devuelve el foco", async () => {
  const dom = buildBotDom();
  globalThis.fetch = fakeFetch(() => Promise.reject(new TypeError("Failed to fetch")));
  dom.input.value = "hola";
  loadScript("bot.js", dom.doc);

  dom.form.dispatchEvent(fakeEvent("submit"));
  await flush();

  const bot = lastBubble(dom.messages);
  assert.equal(bot.classList.contains("is-error"), true);
  assert.match(bot.textContent, /No se pudo contactar/);
  assert.equal(dom.submit.disabled, false);
  assert.ok(dom.input.focusCalls >= 2);
});

test("respuesta HTTP de error (no ok) tambien muestra aviso", async () => {
  const dom = buildBotDom();
  globalThis.fetch = fakeFetch(() =>
    Promise.resolve({ ok: false, status: 500, json: async () => ({}) })
  );
  dom.input.value = "hola";
  loadScript("bot.js", dom.doc);

  dom.form.dispatchEvent(fakeEvent("submit"));
  await flush();

  assert.equal(lastBubble(dom.messages).classList.contains("is-error"), true);
  assert.equal(dom.submit.disabled, false);
});

test("las sugerencias rellenan el mensaje y lo envian", async () => {
  const dom = buildBotDom();
  loadScript("bot.js", dom.doc);

  dom.chips[1].click(); // "frenos"
  await flush();

  assert.equal(globalThis.fetch.calls.length, 1);
  assert.equal(JSON.parse(globalThis.fetch.calls[0].opts.body).message, "frenos");
});

test("sin requestSubmit, las sugerencias disparan el evento submit", async () => {
  const dom = buildBotDom();
  delete dom.form.requestSubmit;
  loadScript("bot.js", dom.doc);

  dom.chips[0].click(); // "hola"
  await flush();

  assert.equal(globalThis.fetch.calls.length, 1);
  assert.equal(JSON.parse(globalThis.fetch.calls[0].opts.body).message, "hola");
});

test("sin los elementos del chat no lanza error", () => {
  const doc = createDocument({});
  assert.doesNotThrow(() => loadScript("bot.js", doc));
});
