"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const {
  FakeElement,
  createDocument,
  fakeEvent,
  loadScript,
} = require("./fake-dom.js");

// Monta el boton hamburguesa y el menu de main.js.
function buildNav() {
  const toggle = new FakeElement("button");
  toggle.setAttribute("aria-expanded", "false");
  const nav = new FakeElement("nav");
  const doc = createDocument({ "site-nav": nav });
  doc.selectorMap[".nav-toggle"] = toggle;
  return { doc, toggle };
}

function pressKey(doc, key) {
  (doc.listeners.keydown || []).forEach((fn) => fn(fakeEvent("keydown", { key })));
}

test("el boton alterna aria-expanded", () => {
  const { doc, toggle } = buildNav();
  loadScript("main.js", doc);

  toggle.click();
  assert.equal(toggle.getAttribute("aria-expanded"), "true");
  toggle.click();
  assert.equal(toggle.getAttribute("aria-expanded"), "false");
});

test("Escape cierra el menu abierto y devuelve el foco al boton", () => {
  const { doc, toggle } = buildNav();
  loadScript("main.js", doc);

  toggle.click();
  pressKey(doc, "Escape");

  assert.equal(toggle.getAttribute("aria-expanded"), "false");
  assert.equal(toggle.focusCalls, 1);
});

test("Escape con el menu cerrado no mueve el foco", () => {
  const { doc, toggle } = buildNav();
  loadScript("main.js", doc);

  pressKey(doc, "Escape");

  assert.equal(toggle.getAttribute("aria-expanded"), "false");
  assert.equal(toggle.focusCalls, 0);
});

test("otras teclas no cierran el menu", () => {
  const { doc, toggle } = buildNav();
  loadScript("main.js", doc);

  toggle.click();
  pressKey(doc, "Enter");

  assert.equal(toggle.getAttribute("aria-expanded"), "true");
});

test("sin boton de menu no lanza error", () => {
  const doc = createDocument({});
  assert.doesNotThrow(() => loadScript("main.js", doc));
});
