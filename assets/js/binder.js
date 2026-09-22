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
    if (!leaves.length) return;

    const controls = document.querySelector("[data-binder-controls]");
    const previous = controls && controls.querySelector("[data-binder-prev]");
    const next = controls && controls.querySelector("[data-binder-next]");
    const position = controls && controls.querySelector("[data-binder-position]");
    const legend = document.querySelector("[data-binder-legend]");
    const legendItems = legend && legend.querySelector("[data-binder-legend-items]");
    const dialog = document.querySelector("[data-card-inspector]");
    const mobile = window.matchMedia("(max-width: 720px)");
    const leafIndex = new Map(leaves.map((leaf, index) => [leaf, index]));
    const idIndex = new Map(leaves.map((leaf, index) => [leaf.dataset.binderLeaf, index]));
    const pocketButtons = Array.from(root.querySelectorAll("button[data-card-id]"));
    let index = indexFromHash();
    let originFocus = null;
    let inspectedIndex = -1;

    function indexFromHash() {
      return idIndex.get(leafIdFromHash(window.location.hash)) ?? 0;
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

    function updateLegend(activeLeaves) {
      if (!legend || !legendItems) return;
      const labels = new Set();
      activeLeaves.forEach((leaf) => {
        leaf.querySelectorAll("button[data-card-id]").forEach((button) => {
          const classification = button.dataset.classification;
          if (classification === "proxy") labels.add("Reference image");
          if (classification === "photo-crop") labels.add("Photo crop");
          if (classification === "missing") labels.add("Image unavailable");
          if (button.dataset.placementStatus === "pending") labels.add("Placement pending");
        });
      });
      legendItems.replaceChildren();
      labels.forEach((label) => {
        const item = document.createElement("li");
        item.textContent = label;
        legendItems.append(item);
      });
      legend.hidden = labels.size === 0;
    }

    function render(syncHash) {
      index = normalizedIndex(index);
      const activeIndexes = mobile.matches ? [index] : [index, index + 1];
      const spreadStart = index - (index % 2);
      const spreadLeaves = leaves.slice(spreadStart, spreadStart + 2);
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
      updateLegend(spreadLeaves);
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

    window.addEventListener("hashchange", () => {
      index = indexFromHash();
      render(true);
    });
    window.addEventListener("popstate", () => {
      index = indexFromHash();
      render(true);
    });
    const onMediaChange = () => render(true);
    if (mobile.addEventListener) {
      mobile.addEventListener("change", onMediaChange);
    } else {
      mobile.addListener(onMediaChange);
    }

    document.addEventListener("keydown", (event) => {
      if (dialog && dialog.open || event.defaultPrevented || isInteractiveTarget(event.target)) return;
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

      function setField(field, value) {
        fields.get(field).textContent = value;
      }

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
        inspectedIndex = pocketButtons.indexOf(button);
        name.textContent = button.dataset.cardName;
        setField("language", button.dataset.cardLanguage);
        setField("set-number", button.dataset.cardSet + " · " + button.dataset.cardNumber);
        setField("theme-pocket", button.dataset.leafTheme + " · pocket " + button.dataset.pocketPosition);
        setField("image-classification", classificationText(button.dataset.classification));
        setField("image-source", button.dataset.imageProvenance
          + (button.dataset.imageSource ? " · " + button.dataset.imageSource : ""));
        setField("image-note", button.dataset.imageNote || "None");
        setField("placement", placementText(button));
        image.removeAttribute("src");
        image.alt = button.dataset.cardName + ", " + button.dataset.cardSet + " " + button.dataset.cardNumber;
        image.hidden = !button.dataset.inspectorSrc;
        if (button.dataset.inspectorSrc) image.src = button.dataset.inspectorSrc;
        priorCard.disabled = inspectedIndex <= 0;
        nextCard.disabled = inspectedIndex >= pocketButtons.length - 1;
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

      pocketButtons.forEach((button) => button.addEventListener("click", () => openInspector(button)));
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

    render(true);
  }

  window.initBinder = initBinder;
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-binder]").forEach(initBinder);
  });
}());
