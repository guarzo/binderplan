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

function buildBinder() {
  const document = new FakeDocument();
  const root = new FakeElement("div", { "data-binder": "volume-1" });
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

function runScenario({ mobile }) {
  const { document, root, previous, position, next } = buildBinder();
  const location = { hash: "" };
  const mediaQuery = {
    matches: mobile,
    addEventListener() {},
    addListener() {},
  };
  const window = {
    location,
    history: {
      pushState(_state, _title, hash) { location.hash = hash; },
      replaceState(_state, _title, hash) { location.hash = hash; },
    },
    matchMedia() { return mediaQuery; },
    addEventListener() {},
  };

  const context = vm.createContext({
    window,
    document,
    Element: FakeElement,
    console,
  });
  vm.runInContext(binderScript, context, { filename: "assets/js/binder.js" });
  window.initBinder(root);

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

  assert.equal(right.defaultPrevented, true, "ArrowRight should be handled");
  assert.equal(left.defaultPrevented, true, "ArrowLeft should be handled");
  assert.notEqual(initial.status, "", "initial live status should be nonempty");
  assert.notEqual(afterRight.status, "", "navigated live status should be nonempty");

  return { initial, afterRight, afterLeft };
}

const desktop = runScenario({ mobile: false });
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

const mobile = runScenario({ mobile: true });
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
