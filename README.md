# Pokemon Art Collection

A curated gallery treating Pokemon cards as art, not commodities. Built with [Hugo](https://gohugo.io/).

## Development

```bash
# Run local server
hugo server

# Build for production
hugo
```

## Structure

- `content/` - Site content (philosophy, gallery, guides)
- `layouts/` - HTML templates
- `static/` - Static assets
- `hugo.toml` - Site configuration

## Adding Images

### Binder Spreads

1. Add image to `static/images/binder/` (e.g., `theme_name_1.png`)
2. Edit `content/gallery/volume-1/_index.md` and add within the appropriate chapter:

```html
<figure class="gallery-item">
  <img src="../../images/binder/theme_name_1.png" alt="Description" loading="lazy">
  <figcaption>Caption</figcaption>
</figure>
```

### Slabs

1. Add image to `static/images/slabs/` (e.g., `category-1.png`)
2. Edit `content/gallery/slabs/_index.md` and add within the appropriate section:

```html
<figure class="gallery-item">
  <img src="../../images/slabs/category-1.png" alt="Description" loading="lazy">
  <figcaption>Caption</figcaption>
</figure>
```
