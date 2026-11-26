"use strict";
// Mini DOM para probar los scripts de static/js sin navegador ni dependencias.
// Solo implementa lo que usan bot.js y main.js.

const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

class FakeClassList {
  constructor(el) {
    this.el = el;
  }
  _set() {
    return new Set((this.el.className || "").split(/\s+/).filter(Boolean));
  }
  add(...names) {
    const s = this._set();
    names.forEach((n) => s.add(n));
    this.el.className = [...s].join(" ");
  }
  remove(...names) {
    const s = this._set();
    names.forEach((n) => s.delete(n));
    this.el.className = [...s].join(" ");
  }
  contains(name) {
    return this._set().has(name);
  }
}

class FakeText {
  constructor(text) {
    this.nodeType = 3;
    this.textContent = String(text);
  }
}

class FakeElement {
  constructor(tagName) {
    this.tagName = tagName.toUpperCase();
    this.children = [];
    this.attributes = {};
    this.listeners = {};
    this.className = "";
    this.classList = new FakeClassList(this);
    this.disabled = false;
    this.value = "";
    this.scrollTop = 0;
    this.scrollHeight = 500;
    this.focusCalls = 0;
    this.queryMap = {};
    this._text = "";
  }
  get textContent() {
    if (this.children.length === 0) return this._text;
    return this.children.map((c) => c.textContent).join("");
  }
  set textContent(value) {
    this.children = [];
    this._text = String(value);
  }
  appendChild(child) {
    this.children.push(child);
    return child;
  }
  setAttribute(name, value) {
    this.attributes[name] = String(value);
  }
  getAttribute(name) {
    return Object.prototype.hasOwnProperty.call(this.attributes, name)
      ? this.attributes[name]
      : null;
  }
  addEventListener(type, fn) {
    (this.listeners[type] = this.listeners[type] || []).push(fn);
  }
  dispatchEvent(event) {
    (this.listeners[event.type] || []).forEach((fn) => fn(event));
    return true;
  }
  click() {
    this.dispatchEvent(fakeEvent("click"));
  }
  focus() {
    this.focusCalls += 1;
  }
  querySelector(selector) {
    return this.queryMap[selector] || null;
  }
}

function fakeEvent(type, extra) {
  const event = {
    type,
    defaultPrevented: false,
    preventDefault() {
      this.defaultPrevented = true;
    },
  };
  return Object.assign(event, extra || {});
}

// ids: mapa id -> FakeElement. Devuelve un document minimo.
function createDocument(ids) {
  const doc = {
    listeners: {},
    selectorMap: {},
    selectorAllMap: {},
    getElementById(id) {
      return ids[id] || null;
    },
    querySelector(selector) {
      return doc.selectorMap[selector] || null;
    },
    querySelectorAll(selector) {
      return doc.selectorAllMap[selector] || [];
    },
    createElement(tag) {
      return new FakeElement(tag);
    },
    createTextNode(text) {
      return new FakeText(text);
    },
    addEventListener(type, fn) {
      (doc.listeners[type] = doc.listeners[type] || []).push(fn);
    },
  };
  return doc;
}

// Ejecuta un script de static/js como si fuera una pagina cargada.
function loadScript(fileName, doc) {
  const file = path.join(__dirname, "..", "..", "static", "js", fileName);
  const source = fs.readFileSync(file, "utf8");
  globalThis.document = doc;
  vm.runInThisContext(source, { filename: file });
}

function flush() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}

module.exports = {
  FakeElement,
  FakeText,
  createDocument,
  fakeEvent,
  loadScript,
  flush,
};
