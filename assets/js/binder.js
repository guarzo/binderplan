(function () {
  "use strict";

  function leafIdFromHash(hash) {
    return (hash || "").replace(/^#leaf-/, "");
  }

  function isInteractiveTarget(target) {
    return target instanceof Element && Boolean(target.closest(
      "a, button, input, select, textarea, summary, [contenteditable='true']"
    ));
  }

  function initBinder(root) {
    const leaves = Array.from(root.querySelectorAll("[data-binder-leaf]"));
    if (!leaves.length && !root.hasAttribute("data-home-exhibits")) return;

    const controls = root.querySelector("[data-binder-controls]");
    const previous = controls && controls.querySelector("[data-binder-prev]");
    const next = controls && controls.querySelector("[data-binder-next]");
    const position = controls && controls.querySelector("[data-binder-position]");
    const dialog = root.querySelector("[data-card-inspector]");
    const binderRoots = document.querySelectorAll("[data-binder]");
    const mobile = window.matchMedia("(max-width: 720px)");
    const leafIndex = new Map(leaves.map((leaf, index) => [leaf, index]));
    const idIndex = new Map(leaves.map((leaf, index) => [leaf.dataset.binderLeaf, index]));
    const pocketButtons = Array.from(root.querySelectorAll("button[data-card-id]"));
    let index = indexFromHash(0);
    let originFocus = null;
    let inspectedIndex = -1;

    function indexFromHash(fallback) {
      return idIndex.get(leafIdFromHash(window.location.hash)) ?? fallback;
    }

    function ownsCurrentHash() {
      return idIndex.has(leafIdFromHash(window.location.hash));
    }

    function normalizedIndex(candidate) {
      const bounded = Math.max(0, Math.min(candidate, leaves.length - 1));
      return mobile.matches ? bounded : bounded - (bounded % 2);
    }

    function hashFor(leafIndex) {
      return "#leaf-" + leaves[leafIndex].dataset.binderLeaf;
    }

    function setHash(leafIndex, replace) {
      const hash = hashFor(leafIndex);
      if (window.location.hash === hash) return;
      if (replace) {
        window.history.replaceState(null, "", hash);
      } else {
        window.history.pushState(null, "", hash);
      }
    }

    function render(syncHash) {
      index = normalizedIndex(index);
      const activeIndexes = mobile.matches ? [index] : [index, index + 1];
      const activeLeaves = leaves.filter((leaf, leafIndex) => activeIndexes.includes(leafIndex));
      leaves.forEach((leaf, leafIndex) => {
        leaf.classList.toggle("is-active", activeIndexes.includes(leafIndex));
      });
      root.querySelectorAll("[data-binder-spread]").forEach((spread) => {
        spread.classList.toggle("is-active", activeLeaves.some((leaf) => spread.contains(leaf)));
      });
      if (previous) previous.href = hashFor(normalizedIndex(index - (mobile.matches ? 1 : 2)));
      if (next) next.href = hashFor(normalizedIndex(index + (mobile.matches ? 1 : 2)));
      if (position) {
        const spread = Math.floor(index / 2) + 1;
        const spreads = Math.ceil(leaves.length / 2);
        position.textContent = mobile.matches
          ? "Leaf " + (index + 1) + " of " + leaves.length + " · spread " + spread + " of " + spreads
          : "Spread " + spread + " of " + spreads + " · leaves " + (index + 1)
            + (index + 1 < leaves.length ? "–" + (index + 2) : "");
      }
      root.dataset.binderReady = "true";
      if (syncHash) setHash(index, true);
    }

    function goTo(candidate) {
      index = normalizedIndex(candidate);
      setHash(index, false);
      render(false);
    }

    function move(direction) {
      goTo(index + direction * (mobile.matches ? 1 : 2));
    }

    if (previous) {
      previous.addEventListener("click", (event) => {
        event.preventDefault();
        move(-1);
      });
    }
    if (next) {
      next.addEventListener("click", (event) => {
        event.preventDefault();
        move(1);
      });
    }

    function renderHashDestination() {
      if (!ownsCurrentHash()) return;
      index = indexFromHash(index);
      render(false);
    }

    window.addEventListener("hashchange", renderHashDestination);
    window.addEventListener("popstate", renderHashDestination);
    const onMediaChange = () => {
      if (leaves.length) render(binderRoots.length === 1 || ownsCurrentHash());
    };
    if (mobile.addEventListener) {
      mobile.addEventListener("change", onMediaChange);
    } else {
      mobile.addListener(onMediaChange);
    }

    document.addEventListener("keydown", (event) => {
      if (!leaves.length) return;
      const eventRoot = event.target instanceof Element && event.target.closest("[data-binder]");
      const belongsToRoot = eventRoot ? eventRoot === root : binderRoots.length === 1;
      if (!belongsToRoot || document.querySelector("dialog[open]")
          || event.defaultPrevented || isInteractiveTarget(event.target)) return;
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        move(-1);
      } else if (event.key === "ArrowRight") {
        event.preventDefault();
        move(1);
      }
    });

    if (dialog) {
      const close = dialog.querySelector("[data-card-inspector-close]");
      const priorCard = dialog.querySelector("[data-card-inspector-previous]");
      const nextCard = dialog.querySelector("[data-card-inspector-next]");
      const image = dialog.querySelector("[data-card-inspector-image]");
      const name = dialog.querySelector("[data-card-inspector-name]");
      const fields = new Map(Array.from(dialog.querySelectorAll("[data-card-inspector-field]"))
        .map((field) => [field.dataset.cardInspectorField, field]));
      const expectedFields = [
        "language",
        "set-number",
        "theme-pocket",
        "image-classification",
        "image-source",
        "image-note",
        "placement"
      ];

      function hasRequiredInspectorParts() {
        return Boolean(close && priorCard && nextCard && image && name)
          && expectedFields.every((field) => fields.has(field));
      }

      function setField(field, value) {
        const target = fields.get(field);
        if (target) target.textContent = value;
      }

      if (!hasRequiredInspectorParts()) return;

      function placementText(button) {
        if (button.dataset.placementStatus !== "pending") return "Confirmed placement";
        const detail = button.dataset.placementObservedCardId
          ? "observed " + button.dataset.placementObservedCardId
          : button.dataset.placementPhysicalState === "unknown"
            ? "physical state unknown"
            : "awaiting review";
        return "Placement pending confirmation · " + detail;
      }

      function classificationText(classification) {
        return {
          exact: "Exact image",
          "photo-crop": "Photo crop",
          proxy: "Reference image",
          missing: "Image unavailable"
        }[classification] || classification;
      }

      function renderInspector(button) {
        const focusedAdjacentControl = [priorCard, nextCard].includes(document.activeElement)
          ? document.activeElement
          : null;
        inspectedIndex = pocketButtons.indexOf(button);
        name.replaceChildren();
        name.textContent = button.dataset.cardPrintedName
          ? button.dataset.cardEnglishName
          : button.dataset.cardName;
        if (button.dataset.cardPrintedName) {
          const printed = document.createElement("span");
          printed.setAttribute("lang", button.dataset.cardLanguage === "JP" ? "ja" : "zh-Hans");
          printed.textContent = " · " + button.dataset.cardPrintedName;
          name.append(printed);
        }
        setField("language", button.dataset.cardLanguage);
        const setNumber = [button.dataset.cardSet, button.dataset.cardNumber]
          .filter((value) => value && value.trim())
          .join(" · ");
        setField("set-number", setNumber || "Unresolved");
        setField("theme-pocket", button.dataset.leafTheme + " · pocket " + button.dataset.pocketPosition);
        setField("image-classification", classificationText(button.dataset.classification));
        setField("image-source", button.dataset.imageProvenance
          + (button.dataset.imageSource ? " · " + button.dataset.imageSource : ""));
        setField("image-note", button.dataset.imageNote || "None");
        setField("placement", placementText(button));
        image.removeAttribute("src");
        image.alt = [button.dataset.cardName, setNumber]
          .filter((value) => value && value.trim())
          .join(", ");
        image.hidden = !button.dataset.inspectorSrc;
        if (button.dataset.inspectorSrc) image.src = button.dataset.inspectorSrc;
        priorCard.disabled = inspectedIndex <= 0;
        nextCard.disabled = inspectedIndex >= pocketButtons.length - 1;
        if (focusedAdjacentControl && focusedAdjacentControl.disabled) close.focus();
      }

      function openInspector(button) {
        const destinationIndex = leafIndex.get(button.closest("[data-binder-leaf]"));
        if (destinationIndex !== undefined && !button.closest("[data-binder-leaf]").classList.contains("is-active")) {
          goTo(destinationIndex);
        }
        if (!dialog.open) originFocus = button;
        renderInspector(button);
        if (!dialog.open) {
          dialog.showModal();
          close.focus();
        }
      }

      function showAdjacent(change) {
        const adjacent = pocketButtons[inspectedIndex + change];
        if (adjacent) openInspector(adjacent);
      }

      pocketButtons.forEach((button) => {
        button.addEventListener("click", () => openInspector(button));
        if (root.hasAttribute("data-home-exhibits")) button.disabled = false;
      });
      if (root.hasAttribute("data-home-exhibits")) root.dataset.homeReady = "true";
      close.addEventListener("click", () => dialog.close());
      priorCard.addEventListener("click", () => showAdjacent(-1));
      nextCard.addEventListener("click", () => showAdjacent(1));
      dialog.addEventListener("cancel", (event) => {
        event.preventDefault();
        dialog.close();
      });
      dialog.addEventListener("close", () => {
        image.removeAttribute("src");
        image.alt = "";
        image.hidden = true;
        if (originFocus && originFocus.isConnected) {
          const originLeaf = originFocus.closest("[data-binder-leaf]");
          const originIndex = leafIndex.get(originLeaf);
          if (originIndex !== undefined && !originLeaf.classList.contains("is-active")) {
            index = normalizedIndex(originIndex);
            render(false);
            setHash(index, true);
          }
          originFocus.focus();
        }
        originFocus = null;
      });
      dialog.addEventListener("keydown", (event) => {
        if (event.key !== "Tab") return;
        const focusable = [close, priorCard, nextCard].filter((control) => !control.disabled);
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (!first || !last) return;
        if (!focusable.includes(document.activeElement)) {
          event.preventDefault();
          (event.shiftKey ? last : first).focus();
        } else if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      });
    }

    if (leaves.length) render(binderRoots.length === 1 || !window.location.hash || ownsCurrentHash());
  }

  window.initBinder = initBinder;
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-binder], [data-home-exhibits]").forEach(initBinder);
  });
}());
