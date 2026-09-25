// Only the photographed slab galleries use this inspector. Images and captions remain
// ordinary content when scripting is unavailable.
document.addEventListener('DOMContentLoaded', () => {
  const page = document.querySelector('.gallery-page--slab');
  if (!page) return;

  const dialog = page.querySelector('#slab-inspector');
  const image = dialog.querySelector('[data-slab-inspector-image]');
  const stage = dialog.querySelector('[data-slab-inspector-stage]');
  const error = dialog.querySelector('[data-slab-inspector-error]');
  const description = dialog.querySelector('[data-slab-inspector-description]');
  const position = dialog.querySelector('[data-slab-inspector-position]');
  const closeButton = dialog.querySelector('[data-slab-inspector-close]');
  const previous = dialog.querySelector('[data-slab-inspector-previous]');
  const next = dialog.querySelector('[data-slab-inspector-next]');
  const zoom = dialog.querySelector('[data-slab-inspector-zoom]');
  let group = [];
  let index = 0;
  let opener = null;

  function fit() {
    dialog.classList.remove('is-enlarged');
    zoom.setAttribute('aria-pressed', 'false');
    zoom.textContent = 'Enlarge photograph';
    stage.scrollTo(0, 0);
  }

  function show(newIndex) {
    index = newIndex;
    fit();
    const { figure, photo, wanted } = group[index];
    const caption = figure.querySelector('figcaption');
    position.textContent = wanted
      ? `Still Hunting · Reference scan ${index + 1} of ${group.length} · Not owned`
      : `Slab ${index + 1} of ${group.length}`;
    description.replaceChildren(...Array.from(caption.childNodes, (node) => node.cloneNode(true)));
    image.alt = photo.alt;
    error.hidden = true;
    image.hidden = false;
    image.src = photo.src;
    previous.disabled = index === 0;
    next.disabled = index === group.length - 1;
    zoom.disabled = wanted;
    zoom.title = wanted ? 'Small reference scan; enlargement unavailable' : '';
  }

  image.addEventListener('error', () => {
    image.hidden = true;
    error.hidden = false;
    zoom.disabled = true;
  });

  page.querySelectorAll('.gallery-grid').forEach((grid) => {
    const wanted = grid.hasAttribute('data-slab-wanted');
    const entries = Array.from(grid.querySelectorAll('.gallery-item')).map((figure) => {
      const photo = figure.querySelector('img');
      const caption = figure.querySelector('figcaption');
      const name = caption.querySelector('strong')?.textContent || caption.textContent;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'slab-open';
      button.setAttribute('aria-label', `${wanted ? 'Inspect reference scan of' : 'Inspect'} ${name.trim().replace(/\.$/, '')}`);
      button.setAttribute('aria-haspopup', 'dialog');
      figure.insertBefore(button, photo);
      button.append(photo);
      return { figure, photo, button, wanted };
    });
    entries.forEach((entry, entryIndex) => {
      entry.button.addEventListener('click', () => {
        group = entries;
        opener = entry.button;
        show(entryIndex);
        dialog.showModal();
        closeButton.focus();
      });
    });
  });

  closeButton.addEventListener('click', () => dialog.close());
  previous.addEventListener('click', () => show(index - 1));
  next.addEventListener('click', () => show(index + 1));
  zoom.addEventListener('click', () => {
    const enlarged = dialog.classList.toggle('is-enlarged');
    zoom.setAttribute('aria-pressed', String(enlarged));
    zoom.textContent = enlarged ? 'Fit whole slab' : 'Enlarge photograph';
    if (enlarged) {
      stage.scrollLeft = (stage.scrollWidth - stage.clientWidth) / 2;
      stage.scrollTop = (stage.scrollHeight - stage.clientHeight) * 0.45;
      stage.focus();
    } else {
      stage.scrollTo(0, 0);
    }
  });
  dialog.addEventListener('keydown', (event) => {
    if (dialog.classList.contains('is-enlarged')) return; // Arrows scroll the enlarged photograph.
    if (event.key === 'ArrowLeft' && !previous.disabled) { event.preventDefault(); show(index - 1); }
    if (event.key === 'ArrowRight' && !next.disabled) { event.preventDefault(); show(index + 1); }
  });
  dialog.addEventListener('close', () => {
    image.removeAttribute('src');
    fit();
    if (opener?.isConnected) opener.focus();
    opener = null;
  });
});
