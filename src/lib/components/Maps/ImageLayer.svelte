<script>
  import { getContext, onDestroy } from 'svelte';
  import maplibregl from 'maplibre-gl';

  let {
    id,
    imageUrl,
    data = { type: 'FeatureCollection', features: [] },
    iconSize = 0.07,
    popup = null,
  } = $props();

  const ctx = getContext('maplibre-map');
  if (!ctx) throw new Error('ImageLayer must be placed inside a Map component.');

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

  async function addLayer() {
    const map = ctx.getMap();
    if (!map) return;

    try {
      if (!map.hasImage(id)) {
        const response = await map.loadImage(imageUrl);
        map.addImage(id, response.data);
      }
    } catch (err) {
      console.error(`ImageLayer: could not load image "${imageUrl}"`, err);
      return;
    }

    if (map.getLayer(id)) map.removeLayer(id);
    if (map.getSource(id)) map.removeSource(id);

    map.addSource(id, { type: 'geojson', data });
    map.addLayer({
      id,
      type: 'symbol',
      source: id,
      layout: {
        'icon-image': id,
        'icon-size': iconSize,
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
    const currentData = data;
    const source = map.getSource(id);
    if (source) source.setData(currentData);
  });

  onDestroy(() => {
    ctx.offStyleLoad(handleStyleLoad);
    const map = ctx.getMap();
    if (!map) return;
    if (popup) map.off('click', id, handleClick);
    if (map.getLayer(id)) map.removeLayer(id);
    if (map.getSource(id)) map.removeSource(id);
    if (openPopup) { openPopup.remove(); openPopup = null; }
  });
</script>
