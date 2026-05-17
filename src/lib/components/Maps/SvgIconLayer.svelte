<script>
  import { getContext, onDestroy } from 'svelte';
  import maplibregl from 'maplibre-gl';

  let {
    id,
    svgMarkup,
    color = '#6b7280',
    size = 40,
    data = { type: 'FeatureCollection', features: [] },
    popup = null,
  } = $props();

  const ctx = getContext('maplibre-map');
  if (!ctx) throw new Error('SvgIconLayer must be placed inside a Map component.');

  let openPopup = null;

  function handleClick(e) {
    if (!popup) return;
    const feature = e.features?.[0];
    if (!feature) return;
    const html = popup(feature);
    if (!html) return;
    if (openPopup) openPopup.remove();
    openPopup = new maplibregl.Popup({ closeButton: true, closeOnClick: true })
      .setLngLat(e.lngLat)
      .setHTML(html)
      .addTo(ctx.getMap());
  }

  function svgToCanvas(svg, fillColor, sizePx) {
    return new Promise((resolve, reject) => {
      const colored = svg.replace(/currentColor/g, fillColor);
      const encoded = encodeURIComponent(colored);
      const img = new Image(sizePx, sizePx);
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = sizePx;
        canvas.height = sizePx;
        canvas.getContext('2d').drawImage(img, 0, 0, sizePx, sizePx);
        resolve(canvas);
      };
      img.onerror = reject;
      img.src = `data:image/svg+xml;charset=utf-8,${encoded}`;
    });
  }

  async function addLayer() {
    const map = ctx.getMap();
    if (!map) return;

    let canvas;
    try {
      canvas = await svgToCanvas(svgMarkup, color, size);
    } catch (err) {
      console.error(`SvgIconLayer: failed to render icon "${id}"`, err);
      return;
    }

    if (ctx.getMap() !== map) return;

    if (popup) map.off('click', id, handleClick);
    if (map.getLayer(id)) map.removeLayer(id);
    if (map.getSource(id)) map.removeSource(id);
    if (map.hasImage(id)) map.removeImage(id);

    map.addImage(id, canvas);
    map.addSource(id, { type: 'geojson', data });
    map.addLayer({
      id,
      type: 'symbol',
      source: id,
      layout: {
        'icon-image': id,
        'icon-size': 1,
        'icon-allow-overlap': true,
        'icon-anchor': 'center',
      },
    });

    if (popup) {
      map.on('click', id, handleClick);
      map.on('mouseenter', id, () => { map.getCanvas().style.cursor = 'pointer'; });
      map.on('mouseleave', id, () => { map.getCanvas().style.cursor = ''; });
    }
  }

  function handleStyleLoad() {
    addLayer();
  }

  addLayer();
  ctx.onStyleLoad(handleStyleLoad);

  $effect(() => {
    const map = ctx.getMap();
    if (!map) return;
    const source = map.getSource(id);
    if (source) source.setData(data);
  });

  $effect(() => {
    void color;
    const map = ctx.getMap();
    if (!map || !map.getSource(id)) return;
    addLayer();
  });

  onDestroy(() => {
    ctx.offStyleLoad(handleStyleLoad);
    const map = ctx.getMap();
    if (!map) return;
    if (popup) map.off('click', id, handleClick);
    if (map.getLayer(id)) map.removeLayer(id);
    if (map.getSource(id)) map.removeSource(id);
    if (map.hasImage(id)) map.removeImage(id);
    if (openPopup) { openPopup.remove(); openPopup = null; }
  });
</script>
