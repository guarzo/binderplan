import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, "..");
const binderScript = fs.readFileSync(path.join(rootDir, "assets/js/binder.js"), "utf8");

function datasetKey(attribute) {
  return attribute.slice(5).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
}

class FakeClassList {
  constructor() {
    this.classes = new Set();
  }

  toggle(name, force) {
    if (force) {
      this.classes.add(name);
    } else {
      this.classes.delete(name);
    }
  }

  contains(name) {
    return this.classes.has(name);
  }
}

class FakeElement {
  constructor(tagName, attributes = {}) {
    this.tagName = tagName.toUpperCase();
    this.children = [];
    this.parentElement = null;
    this.attributes = new Map();
    this.dataset = {};
    this.classList = new FakeClassList();
    this.listeners = new Map();
    this.textContent = "";
    this.href = "";

    Object.entries(attributes).forEach(([name, value]) => this.setAttribute(name, value));
  }

  append(...children) {
    children.forEach((child) => {
      child.parentElement = this;
      this.children.push(child);
    });
  }

  get textContent() {
    return this._textContent + this.children.map((child) => child.textContent).join("");
  }

  set textContent(value) {
    this._textContent = String(value);
    this.children = [];
  }

  setAttribute(name, value = "") {
    const stringValue = String(value);
    this.attributes.set(name, stringValue);
    if (name.startsWith("data-")) this.dataset[datasetKey(name)] = stringValue;
    if (name === "href") this.href = stringValue;
  }

  getAttribute(name) {
    return this.attributes.has(name) ? this.attributes.get(name) : null;
  }

  hasAttribute(name) {
    return this.attributes.has(name);
  }

  addEventListener(type, listener) {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type).push(listener);
  }

  dispatchEvent(event) {
    event.target ??= this;
    for (const listener of this.listeners.get(event.type) || []) listener(event);
  }

  querySelector(selector) {
    return this.querySelectorAll(selector)[0] || null;
  }

  querySelectorAll(selector) {
    const matches = [];
    const visit = (element) => {
      if (element.matches(selector)) matches.push(element);
      element.children.forEach(visit);
    };
    this.children.forEach(visit);
    return matches;
  }

  closest(selector) {
    for (let element = this; element; element = element.parentElement) {
      if (element.matches(selector)) return element;
    }
    return null;
  }

  contains(candidate) {
    if (candidate === this) return true;
    return this.children.some((child) => child.contains(candidate));
  }

  matches(selector) {
    return selector.split(",").some((part) => this.matchesSingle(part.trim()));
  }

  matchesSingle(selector) {
    if (!selector) return false;
    if (/^[a-z]+$/i.test(selector)) return this.tagName.toLowerCase() === selector.toLowerCase();

    const tagAndAttribute = selector.match(/^([a-z]+)?\[([^=\]]+)(?:=['\"]?([^'\"]+)['\"]?)?\]$/i);
    if (!tagAndAttribute) return false;

    const [, tagName, attribute, expectedValue] = tagAndAttribute;
    if (tagName && this.tagName.toLowerCase() !== tagName.toLowerCase()) return false;
    if (!this.hasAttribute(attribute)) return false;
    return expectedValue === undefined || this.getAttribute(attribute) === expectedValue;
  }
}

class FakeDocument extends FakeElement {
  constructor() {
    super("document");
  }
  createElement(tagName) { return new FakeElement(tagName); }
}

function keyboardEvent(key, target) {
  return {
    type: "keydown",
    key,
    target,
    defaultPrevented: false,
    preventDefault() {
      this.defaultPrevented = true;
    },
  };
}

function buildBinder(binderId = "volume-1") {
  const document = new FakeDocument();
  const root = new FakeElement("div", { "data-binder": binderId });
  const controls = new FakeElement("nav", { "data-binder-controls": "" });
  const previous = new FakeElement("a", { "data-binder-prev": "", href: "#leaf-v1-01" });
  const position = new FakeElement("p", { "data-binder-position": "", "aria-live": "polite" });
  const next = new FakeElement("a", { "data-binder-next": "", href: "#leaf-v1-03" });
  const spreads = new FakeElement("div", { "data-binder-spreads": "" });

  controls.append(previous, position, next);
  for (let spreadIndex = 0; spreadIndex < 2; spreadIndex += 1) {
    const spread = new FakeElement("div", { "data-binder-spread": String(spreadIndex + 1) });
    for (let leafOffset = 0; leafOffset < 2; leafOffset += 1) {
      const leafNumber = spreadIndex * 2 + leafOffset + 1;
      const leaf = new FakeElement("section", {
        id: `leaf-v1-0${leafNumber}`,
        "data-binder-leaf": `v1-0${leafNumber}`,
      });
      spread.append(leaf);
    }
    spreads.append(spread);
  }
  root.append(controls, spreads);
  document.append(root);
  return { document, root, previous, position, next };
}

function runScenario({ mobile, directHash, directEvent, binderId, initialHash = "" }) {
  const { document, root, previous, position, next } = buildBinder(binderId);
  const location = { hash: initialHash };
  const mediaQuery = {
    matches: mobile,
    addEventListener() {},
    addListener() {},
  };
  const windowListeners = new Map();
  const window = {
    location,
    history: {
      pushState(_state, _title, hash) { location.hash = hash; },
      replaceState(_state, _title, hash) { location.hash = hash; },
    },
    matchMedia() { return mediaQuery; },
    addEventListener(type, listener) {
      if (!windowListeners.has(type)) windowListeners.set(type, []);
      windowListeners.get(type).push(listener);
    },
    dispatchEvent(event) {
      event.target ??= this;
      for (const listener of windowListeners.get(event.type) || []) listener(event);
    },
  };

  const context = vm.createContext({
    window,
    document,
    Element: FakeElement,
    console,
  });
  vm.runInContext(binderScript, context, { filename: "assets/js/binder.js" });
  document.dispatchEvent({ type: "DOMContentLoaded", target: document });

  const snapshot = () => ({
    status: position.textContent,
    hash: location.hash,
    previousHref: previous.href,
    nextHref: next.href,
  });

  const initial = snapshot();
  const right = keyboardEvent("ArrowRight", root);
  document.dispatchEvent(right);
  const afterRight = snapshot();
  const left = keyboardEvent("ArrowLeft", root);
  document.dispatchEvent(left);
  const afterLeft = snapshot();
  location.hash = directHash;
  window.dispatchEvent({ type: directEvent, target: window });
  const afterLocationEvent = snapshot();

  assert.equal(right.defaultPrevented, true, "ArrowRight should be handled");
  assert.equal(left.defaultPrevented, true, "ArrowLeft should be handled");
  assert.notEqual(initial.status, "", "bootstrap should populate initial live status");
  assert.notEqual(afterRight.status, "", "navigated live status should be nonempty");
  assert.notEqual(afterLocationEvent.status, "", "location event status should be nonempty");

  return { initial, afterRight, afterLeft, afterLocationEvent };
}

const desktop = runScenario({ mobile: false, directHash: "#leaf-v1-03", directEvent: "hashchange" });
assert.deepEqual(desktop.initial, {
  status: "Spread 1 of 2 · leaves 1–2",
  hash: "#leaf-v1-01",
  previousHref: "#leaf-v1-01",
  nextHref: "#leaf-v1-03",
});
assert.deepEqual(desktop.afterRight, {
  status: "Spread 2 of 2 · leaves 3–4",
  hash: "#leaf-v1-03",
  previousHref: "#leaf-v1-01",
  nextHref: "#leaf-v1-03",
});
assert.deepEqual(desktop.afterLeft, desktop.initial);
assert.deepEqual(desktop.afterLocationEvent, desktop.afterRight);

// A non-leaf anchor on the same page (such as Holding's Trade section) must survive
// binder initialization; otherwise direct links to that section are unusable.
const section = runScenario({ mobile: false, initialHash: "#trade-cards", directHash: "#leaf-v1-03", directEvent: "hashchange" });
assert.equal(section.initial.hash, "#trade-cards");
assert.equal(section.afterLocationEvent.hash, "#leaf-v1-03");

const mobile = runScenario({ mobile: true, directHash: "#leaf-v1-04", directEvent: "popstate" });
assert.deepEqual(mobile.initial, {
  status: "Leaf 1 of 4 · spread 1 of 2",
  hash: "#leaf-v1-01",
  previousHref: "#leaf-v1-01",
  nextHref: "#leaf-v1-02",
});
assert.deepEqual(mobile.afterRight, {
  status: "Leaf 2 of 4 · spread 1 of 2",
  hash: "#leaf-v1-02",
  previousHref: "#leaf-v1-01",
  nextHref: "#leaf-v1-03",
});
assert.deepEqual(mobile.afterLeft, mobile.initial);
assert.deepEqual(mobile.afterLocationEvent, {
  status: "Leaf 4 of 4 · spread 2 of 2",
  hash: "#leaf-v1-04",
  previousHref: "#leaf-v1-03",
  nextHref: "#leaf-v1-04",
});

const trainer = runScenario({ mobile: true, binderId: "waifu", directHash: "#leaf-v1-04", directEvent: "hashchange" });
assert.equal(trainer.initial.hash, "", "Trainer draft opens at its introduction, not below the sticky header");
assert.equal(trainer.afterRight.hash, "#leaf-v1-02", "Trainer page navigation still updates the leaf hash");
assert.equal(trainer.afterLocationEvent.hash, "#leaf-v1-04", "Trainer deep links remain navigable");

// The homepage wall uses the same inspector details without adding binder leaves.
{
  const document = new FakeDocument();
  const wall = new FakeElement("section", { "data-home-exhibits": "" });
  const cards = ["Sandshrew", "Audino · タブンネ"].map((cardName) => new FakeElement("button", {
    "data-card-id": cardName,
    "data-card-name": cardName,
    "data-card-english-name": cardName.split(" · ")[0],
    "data-card-printed-name": cardName.includes(" · ") ? "タブンネ" : "",
    "data-card-language": "JP",
    "data-card-set": "sv11B",
    "data-card-number": "156/086",
    "data-leaf-theme": "Calm in Nature",
    "data-pocket-position": "1",
    "data-classification": "exact",
    "data-image-provenance": "Reviewed image",
    "data-placement-status": "confirmed",
    "data-sort-status": "Keeper", "data-sort-subsection": "Heritage",
    "data-identity-confidence": "medium",
    "data-inspector-src": "/images/test.webp",
  }));
  const dialog = new FakeElement("dialog", { "data-card-inspector": "" });
  const close = new FakeElement("button", { "data-card-inspector-close": "" });
  const previous = new FakeElement("button", { "data-card-inspector-previous": "" });
  const next = new FakeElement("button", { "data-card-inspector-next": "" });
  const image = new FakeElement("img", { "data-card-inspector-image": "" });
  const name = new FakeElement("h2", { "data-card-inspector-name": "" });
  const fields = ["language", "set-number", "theme-pocket", "image-classification", "image-source", "image-note", "placement", "sort-status", "identity-confidence"]
    .map((field) => new FakeElement("dd", { "data-card-inspector-field": field }));
  dialog.showModal = () => { dialog.open = true; };
  dialog.close = () => { dialog.open = false; dialog.dispatchEvent({ type: "close" }); };
  image.removeAttribute = (attribute) => image.attributes.delete(attribute);
  [close, previous, next, ...cards].forEach((element) => {
    element.focus = () => { document.activeElement = element; };
    element.isConnected = true;
  });
  dialog.append(close, previous, next, image, name, ...fields);
  wall.append(...cards, dialog);
  document.append(wall);
  const window = { location: { hash: "" }, matchMedia() { return { matches: false, addEventListener() {} }; }, addEventListener() {} };
  vm.runInContext(binderScript, vm.createContext({ window, document, Element: FakeElement, console }));
  document.dispatchEvent({ type: "DOMContentLoaded" });
  assert.equal(cards[0].disabled, false, "the wall frames are enabled when inspector JS is ready");
  cards[0].dispatchEvent({ type: "click" });
  assert.equal(dialog.open, true, "a frame opens the shared inspector");
  assert.equal(name.textContent, "Sandshrew");
  assert.equal(fields.find((field) => field.dataset.cardInspectorField === "sort-status").textContent, "Keeper · Heritage");
  assert.equal(fields.find((field) => field.dataset.cardInspectorField === "identity-confidence").textContent, "medium");
  assert.equal(document.activeElement, close);
  next.dispatchEvent({ type: "click" });
  assert.equal(name.textContent, "Audino · タブンネ");
  assert.equal(name.children[0].getAttribute("lang"), "ja");
  assert.equal(name.children[0].textContent, " · タブンネ");
  previous.dispatchEvent({ type: "click" });
  assert.equal(name.textContent, "Sandshrew");
  assert.equal(name.children.length, 0, "switching to an English card removes the prior original-script span");
  close.dispatchEvent({ type: "click" });
  assert.equal(document.activeElement, cards[0], "closing returns focus to the opening frame");
}
