import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import vm from 'node:vm';

const script = readFileSync(resolve(import.meta.dirname, '../assets/js/slab-inspector.js'), 'utf8');

function element() {
  const listeners = new Map();
  const attributes = new Map();
  const classes = new Set();
  return {
    hidden: false, disabled: false, isConnected: true, textContent: '',
    classList: {
      add: (name) => classes.add(name),
      remove: (name) => classes.delete(name),
      contains: (name) => classes.has(name),
      toggle: (name) => classes.has(name) ? (classes.delete(name), false) : (classes.add(name), true),
    },
    addEventListener: (type, callback) => listeners.set(type, callback),
    fire: (type, event = {}) => listeners.get(type)?.(event),
    setAttribute: (name, value) => attributes.set(name, value),
    getAttribute: (name) => attributes.get(name),
    removeAttribute(name) { attributes.delete(name); if (name === 'src') this.src = ''; },
    append: () => {},
    focus() { this.focused = true; },
    replaceChildren(...nodes) { this.children = nodes; },
    scrollTo: () => {},
  };
}

function createGallery() {
  const controls = Object.fromEntries([
    'image', 'stage', 'error', 'description', 'position', 'close', 'previous', 'next', 'zoom',
  ].map((name) => [name, element()]));
  const dialog = element();
  dialog.querySelector = (selector) => {
    const name = selector.match(/data-slab-inspector-([\w-]+)/)?.[1];
    return controls[name] || null;
  };
  dialog.showModal = () => { dialog.open = true; };
  dialog.close = () => { dialog.open = false; dialog.fire('close'); };

  function grid(items, wanted = false) {
    const figures = items.map(([name, src, currentSrc]) => {
      const photo = { alt: name, src, currentSrc };
      const caption = {
        textContent: name,
        childNodes: [{ cloneNode: () => ({ textContent: name }) }],
        querySelector: () => null,
      };
      return {
        querySelector: (selector) => selector === 'img' ? photo : caption,
        insertBefore(button) { this.button = button; },
        photo,
      };
    });
    return {
      figures,
      hasAttribute: () => wanted,
      querySelectorAll: () => figures,
    };
  }

  const owned = grid([
    ['Alakazam', 'http://local/masaki_alakazam.jpg', 'http://local/masaki_alakazam.webp'],
    ['Gengar', 'http://local/masaki_gengar.jpg', 'http://local/masaki_gengar.webp'],
  ]);
  const wanted = grid([
    ['Golem', 'http://local/golem.webp', 'http://local/golem.webp'],
    ['Omastar', 'http://local/omastar.webp', 'http://local/omastar.webp'],
  ], true);
  const page = {
    querySelector: () => dialog,
    querySelectorAll: () => [owned, wanted],
  };
  const document = {
    querySelector: () => page,
    createElement: () => element(),
    addEventListener: (_, callback) => { document.ready = callback; },
  };
  vm.runInNewContext(script, { document });
  document.ready();
  return { owned, wanted, dialog, controls };
}

const { owned, wanted, dialog, controls } = createGallery();
owned.figures[0].button.fire('click');
assert.equal(dialog.open, true);
assert.equal(controls.image.src, 'http://local/masaki_alakazam.jpg');
assert.equal(controls.previous.disabled, true);
assert.match(controls.position.textContent, /Slab 1 of 2/);
controls.next.fire('click');
assert.match(controls.position.textContent, /Slab 2 of 2/);
assert.equal(controls.next.disabled, true);
controls.zoom.fire('click');
assert.equal(controls.zoom.getAttribute('aria-pressed'), 'true');
dialog.close();
assert.equal(owned.figures[0].button.focused, true);

wanted.figures[0].button.fire('click');
assert.match(controls.position.textContent, /Not owned/);
assert.equal(controls.zoom.disabled, true);
assert.equal(controls.previous.disabled, true);
assert.equal(controls.image.src, 'http://local/golem.webp');
controls.image.fire('error');
assert.equal(controls.image.hidden, true);
assert.equal(controls.error.hidden, false);
dialog.close();

owned.figures[0].button.fire('click');
controls.image.fire('error');
assert.equal(controls.image.src, 'http://local/masaki_alakazam.webp');
assert.equal(controls.image.hidden, false);
assert.equal(controls.zoom.disabled, true);
assert.match(controls.error.textContent, /gallery preview/);
console.log('PASS: slab group boundaries, original inspection, zoom, focus, and fallback');
