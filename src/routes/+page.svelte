<script>
  import { base } from '$app/paths';
  import { onMount } from 'svelte';

  import ArticleBody from '$lib/components/Article/ArticleBody.svelte';
  import ArticleHeader from '$lib/components/Article/ArticleHeader.svelte';
  import RecentPosts from '$lib/components/Article/RecentPosts.svelte';
  import Legend from '$lib/components/Maps/Legend.svelte';
  import Map from '$lib/components/Maps/Map.svelte';
  import MapLayer from '$lib/components/Maps/MapLayer.svelte';
  import ImageLayer from '$lib/components/Maps/ImageLayer.svelte';
  import bundledPointsRaw from '$lib/data/arpa-project-points.geojson?raw';
  const bundledPoints = JSON.parse(bundledPointsRaw);

  const STATE_ABBREV = {
    Alabama: 'AL', Alaska: 'AK', Arizona: 'AZ', Arkansas: 'AR',
    California: 'CA', Colorado: 'CO', Connecticut: 'CT', Delaware: 'DE',
    Florida: 'FL', Georgia: 'GA', Hawaii: 'HI', Idaho: 'ID',
    Illinois: 'IL', Indiana: 'IN', Iowa: 'IA', Kansas: 'KS',
    Kentucky: 'KY', Louisiana: 'LA', Maine: 'ME', Maryland: 'MD',
    Massachusetts: 'MA', Michigan: 'MI', Minnesota: 'MN', Mississippi: 'MS',
    Missouri: 'MO', Montana: 'MT', Nebraska: 'NE', Nevada: 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', Ohio: 'OH', Oklahoma: 'OK',
    Oregon: 'OR', Pennsylvania: 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', Tennessee: 'TN', Texas: 'TX', Utah: 'UT',
    Vermont: 'VT', Virginia: 'VA', Washington: 'WA', 'West Virginia': 'WV',
    Wisconsin: 'WI', Wyoming: 'WY', 'District of Columbia': 'DC',
  };

  const EMPTY_FC = { type: 'FeatureCollection', features: [] };

  const headline = 'ARPA construction projects across the United States';
  const byline = 'NYCity News Service';
  const pubDate = '2026-05-09';

  const currencyFormatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  });

  const compactCurrencyFormatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    maximumFractionDigits: 1,
  });

  const statusColors = {
    Completed: '#166534',
    'Completed 50% or more': '#facc15',
    'Completed less than 50%': '#0284c7',
    Cancelled: '#dc2626',
    'Not Started': '#f97316',
    'Not reported': '#6b7280',
  };

  const statusLegend = [
    { label: 'Completed', color: statusColors.Completed },
    { label: '≥50% complete', color: statusColors['Completed 50% or more'] },
    { label: '<50% complete', color: statusColors['Completed less than 50%'] },
    { label: 'Not started', color: statusColors['Not Started'] },
    { label: 'Cancelled', color: statusColors.Cancelled },
  ];

  const ALL_STATUSES = [
    'Completed',
    'Completed 50% or more',
    'Completed less than 50%',
    'Not Started',
    'Cancelled',
    'Not reported',
  ];

  const BUILDING_TYPES = [
    'Fire Station',
    'Government Building',
    'Criminal Justice',
    'Public Safety',
    'Recreation',
    'Library',
    'Housing',
    'Animal Shelter',
    'Medical',
    'Education',
    'Mental Health and Human Services',
    'Senior Center',
    'Emergency Operations Center',
    'Food Pantry',
    'Public Works',
  ];

  function classifyBuilding(name) {
    const n = (name ?? '').toLowerCase();
    if (/medical examiner|morgue/.test(n)) return 'Medical';
    if (/aquarium/.test(n)) return 'Recreation';
    if (/animal shelter|animal cage/.test(n)) return 'Animal Shelter';
    if (/ambulance|\bems\b/.test(n)) return 'Medical';
    if (/emergency operations|emergency management operations/.test(n)) return 'Emergency Operations Center';
    if (/food pantry|food bank/.test(n)) return 'Food Pantry';
    if (/public school/.test(n)) return 'Education';
    if (/fairground|farmer.{0,3}s? market|\bag &\b|agriculture/.test(n)) return 'Recreation';
    if (/medical and behavioral health facility/.test(n)) return 'Criminal Justice';
    if (/mental health|behavioral health|human services|counseling service/.test(n)) return 'Mental Health and Human Services';
    if (/senior center|senior citizen/.test(n)) return 'Senior Center';
    if (/domestic violence|\bdvip\b|homeless|shelter|transitional|poverello|homeward point|family motel|miracle of cedar street/.test(n)) return 'Housing';
    if (/fire station|fire department|fire dept|fire district|firehouse|volunteer fire|\bvfd\b|fire rescue|\bfire\b/.test(n)) return 'Fire Station';
    if (/city hall|town hall|municipal building|civic center|township building/.test(n)) return 'Government Building';
    if (/\bjail\b|justice center|forensic|prison|evidence (facility|processing|room)|corrections building|sheriff.{0,5}office/.test(n)) return 'Criminal Justice';
    if (/police|\bpd building\b|public safety (building|facility|$)/.test(n)) return 'Public Safety';
    if (/community center|recreation center|\bpark\b|centers for youth|adult community/.test(n)) return 'Recreation';
    if (/library/.test(n)) return 'Library';
    if (/school|career center|technical center|training center|education center|college|university/.test(n)) return 'Education';
    if (/courthouse|transition facility/.test(n)) return 'Criminal Justice';
    if (/public works|municipal garage/.test(n)) return 'Public Works';
    if (/historic|cultural|artifact/.test(n)) return 'Recreation';
    return 'Recreation';
  }

  const highlightedProjectId = 'TPN-051622';
  const recentPosts = [
    {
      title: '5 Things to Watch Out For in the Upcoming Trade Report',
      date: '2026-05-05',
      url: 'https://issuenumberone.journalism.cuny.edu/2026/05/05/5-things-to-watch-out-for-in-the-upcoming-trade-report/',
      image: 'https://cdn.nycitynewsservice.com/blogs.dir/423/files/2026/05/AdobeStock_348581370-200x150.jpeg',
    },
    {
      title: 'The Sun is Still Shining on US Solar',
      date: '2026-05-02',
      url: 'https://issuenumberone.journalism.cuny.edu/2026/05/02/the-sun-is-still-shining-on-us-solar/',
      image: null,
    },
    {
      title: 'U.S. Manufacturing Growth Driven by War-Related Uncertainties',
      date: '2026-05-01',
      url: 'https://issuenumberone.journalism.cuny.edu/2026/05/01/u-s-manufacturing-growth-driven-by-war-related-uncertainties/',
      image: 'https://cdn.nycitynewsservice.com/blogs.dir/423/files/2026/05/pexels-hoang-nc-483165236-19544248-200x150.jpg',
    },
    {
      title: 'Five things to watch for in the March durable goods report',
      date: '2026-04-28',
      url: 'https://issuenumberone.journalism.cuny.edu/2026/04/28/five-things-to-watch-for-in-the-march-durable-goods-report-2/',
      image: 'https://cdn.nycitynewsservice.com/blogs.dir/423/files/2026/05/work-progresses-at-boeing-south-carolina-an-assembly-site-for-boeings-commercial-dfc78c-1024-1-200x150.jpg',
    },
  ];

  let pointFeatures = $state([]);
  let loading = $state(true);
  let errorMessage = $state('');
  let statesData = $state(EMPTY_FC);
  let selectedFeature = $state(null);

  let filterSpending = $state('any');
  let filterStatuses = $state([]);
  let filterRecipientType = $state('all');
  let filterBuildings = $state([]);

  function handleDescriptionClick(e) {
    const btn = e.target.closest('.popup-info-btn');
    if (!btn) return;
    const projectId = btn.dataset.projectId;
    selectedFeature = pointFeatures.find((f) => f.properties.projectId === projectId) ?? null;
  }

  onMount(() => {
    document.addEventListener('click', handleDescriptionClick);

    function handleDWMessage(a) {
      if (void 0 !== a.data['datawrapper-height']) {
        const iframes = document.querySelectorAll('iframe');
        for (const t in a.data['datawrapper-height']) {
          for (let i = 0; i < iframes.length; i++) {
            if (iframes[i].contentWindow === a.source) {
              iframes[i].style.height = a.data['datawrapper-height'][t] + 'px';
            }
          }
        }
      }
    }
    window.addEventListener('message', handleDWMessage);

    return () => {
      document.removeEventListener('click', handleDescriptionClick);
      window.removeEventListener('message', handleDWMessage);
    };
  });

  const filteredFeatures = $derived.by(() => {
    return pointFeatures.filter((f) => {
      const p = f.properties;

      const exp = p.totalExpenditures;
      if (filterSpending === 'zero' && exp !== 0) return false;
      if (filterSpending === 'under100k' && exp >= 100_000) return false;
      if (filterSpending === '100k-1m' && (exp < 100_000 || exp >= 1_000_000)) return false;
      if (filterSpending === '1m-10m' && (exp < 1_000_000 || exp >= 10_000_000)) return false;
      if (filterSpending === 'over10m' && exp < 10_000_000) return false;

      if (filterStatuses.length > 0 && !filterStatuses.includes(p.completionStatus)) return false;
      if (filterRecipientType !== 'all' && p.recipientType !== filterRecipientType) return false;
      if (filterBuildings.length > 0 && !filterBuildings.includes(classifyBuilding(p.projectName))) return false;

      return true;
    });
  });

  const hasActiveFilters = $derived(
    filterSpending !== 'any' ||
    filterStatuses.length > 0 ||
    filterRecipientType !== 'all' ||
    filterBuildings.length > 0
  );

  function clearFilters() {
    filterSpending = 'any';
    filterStatuses = [];
    filterRecipientType = 'all';
    filterBuildings = [];
  }

  const pointLayerData = $derived.by(() => ({
    type: 'FeatureCollection',
    features: filteredFeatures,
  }));

  const highlightedFeature = $derived.by(
    () => filteredFeatures.find((f) => f.properties.projectId === highlightedProjectId) ?? null
  );

  const highlightedLayerData = $derived.by(() => ({
    type: 'FeatureCollection',
    features: highlightedFeature ? [highlightedFeature] : [],
  }));

  const highlightedSpentLabel = $derived.by(() =>
    highlightedFeature
      ? `${formatCompactCurrency(highlightedFeature.properties.totalExpenditures)} spent`
      : ''

  const weirData = $derived.by(() => ({
    type: 'FeatureCollection',
    features: pointFeatures.filter((f) => f.properties.projectId === 'TPN-195614'),
  }));

  const aquariumData = $derived.by(() => ({
    type: 'FeatureCollection',
    features: pointFeatures.filter((f) => f.properties.projectId === 'TPN-255980'),
  }));

  const alabamaJailData = $derived.by(() => ({
    type: 'FeatureCollection',
    features: pointFeatures.filter((f) => f.properties.projectId === 'TPN-051622'),
  }));
  );

  const totals = $derived.by(() =>
    filteredFeatures.reduce(
      (acc, f) => {
        acc.projects += 1;
        acc.obligations += f.properties.totalObligations;
        acc.expenditures += f.properties.totalExpenditures;
        return acc;
      },
      { projects: 0, obligations: 0, expenditures: 0 }
    )
  );

  function formatCurrency(value) {
    return currencyFormatter.format(value);
  }

  function formatCompactCurrency(value) {
    return compactCurrencyFormatter.format(value);
  }

  function buildPopup(feature) {
    const completionStatus = feature.properties.completionStatus;
    const color = statusColors[completionStatus] ?? statusColors['Not reported'];

    return `
      <div class="project-popup">
        <span class="badge" style="background:${color}">${completionStatus}</span>
        <strong>${feature.properties.projectName}</strong>
        <div>${feature.properties.recipientName} (${feature.properties.state})</div>
        <div>Obligations: ${formatCurrency(feature.properties.totalObligations)}</div>
        <div>Expenditures: ${formatCurrency(feature.properties.totalExpenditures)}</div>
        ${feature.properties.description ? `<button class="popup-info-btn" data-project-id="${feature.properties.projectId}">View description →</button>` : ''}
      </div>
    `;
  }

  onMount(async () => {
    try {
      const response = await fetch(`${base}/data/arpa-project-points.geojson`);
      if (!response.ok) throw new Error('Project point data failed to load.');
      const geojson = await response.json();
      if (!geojson || !Array.isArray(geojson.features)) {
        throw new Error('Project point data is invalid or missing a features array. Falling back to bundled data.');
      }

      pointFeatures = geojson.features;
    } catch (error) {
      // If fetch or validation failed, fall back to bundled JSON included in the app bundle.
      try {
        if (bundledPoints && Array.isArray(bundledPoints.features)) {
          pointFeatures = bundledPoints.features;
          errorMessage = '';
        } else {
          errorMessage = error instanceof Error ? error.message : 'Unable to load project points.';
        }
      } catch (e) {
        errorMessage = error instanceof Error ? error.message : 'Unable to load project points.';
      }
    } finally {
      loading = false;
    }

    fetch('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json')
      .then((r) => r.json())
      .then((geojson) => {
        statesData = {
          type: 'FeatureCollection',
          features: geojson.features.map((f) => ({
            ...f,
            properties: { ...f.properties, abbrev: STATE_ABBREV[f.properties.name] ?? '' },
          })),
        };
      })
      .catch(() => {});
  });
</script>

<svelte:head>
  <title>{headline} | NYCity News Service</title>
  <meta
    name="description"
    content="A U.S. map plotting every ARPA construction project point with placement by county, city, or state and jitter offsets to avoid stacked markers."
  />
</svelte:head>

<!-- Two-column layout: article + map on the left, sidebar on the right -->
<div class="page-layout">

  <article class="article-column">
    <ArticleHeader {headline} {byline} {pubDate} />

    <ArticleBody>
      <p class="dropcap">
        This county was far from alone in the way that it chose to use its ARPA dollars. While the
        "American Rescue Plan Act" sounds like a superhero funding package, bringing aid to towns
        suffering from ailments prompted by COVID, in reality it wasn't exactly that. It was a $1.9
        trillion stimulus package aimed at getting people and governments to spend, so a sleepy
        economy could function again after the pandemic. While most of the money went to government
        administration and repairing sewer systems and highways, some embarked on more extensive
        projects that like [anecdote] and communities had a range of opinions on how the money was
        used.
      </p>
      <p>
        ARPA grants helped construct well over 200 new buildings across the country, over 60 of
        which are still being built, according to data last updated by the U.S. Treasury on
        September, 30, 2025. While some of these programs have helped build Town Halls in rural
        communities, libraries and animal shelters, many were used to build jails and police
        departments, projects that were very sensitive especially following the Black Lives Matter
        Protests.
      </p>

      {@html `<iframe title="Types of Projects Built" aria-label="Bar Chart" id="datawrapper-chart-LQT60" src="https://datawrapper.dwcdn.net/LQT60/2/" scrolling="no" frameborder="0" style="width: 0; min-width: 100% !important; border: none;" height="553" data-external="1"></iframe>`}

      <p>
        In Fall of 2021, Alabama announced that it would use $400 million of its ARPA grants to
        build two new prisons. Even for a state as focused on public safety as Alabama this ruffled
        some feathers. Multiple federal lawsuits were filed against the use of relief funding for a
        prison but they were unsuccessful. The American Civil Liberties Union and Southern Poverty
        Law Center have both been outspoken against the facility.
      </p>
      <blockquote>
        <p>
          "Alabama's healthcare system is in dire straits. We have rural hospitals and clinics that
          are closing," said SPLC Alabama Policy Director Jerome Dees. "We've got a hospital in
          Montgomery that's filing for bankruptcy."
        </p>
      </blockquote>
      <p>
        Still outside of the protest from advocacy organizations, there hasn't been the outrage that
        might have been felt in other states or cities. Mildred Warner, a Cornell Professor of City
        and Regional planning, says that's by design.
      </p>
      <blockquote>
        <p>
          "You have to be politically savvy about the community you live in and what's going to work
          for them," said Warner. "If you're in Alabama and you lead with equity, that's a political
          nonstarter, so lead with the jail."
        </p>
      </blockquote>
      <p>
        States are required to keep their prisons in good condition and Alabama's prisons needed
        renovation. Even Dees admits there are benefits to a correctional facility revamp for
        prisoners. According to Warner's research, using ARPA funds publicly allowed Alabama to
        please their majority conservative constituents while also funding social services less
        publicly.
      </p>
      <p>
        Whether or not each project was well received is far from the only controversy surrounding
        the Recovery Plan. Many economists, politicians and voters blame Biden's stimulus for
        inflation. While this is hotly debated it's unlikely that it was the cause of rising prices
        that occurred around the globe, but it's possible it had some effect on inflation in America.
      </p>
      <p>
        But the plan is also praised for helping to lower unemployment. After the money was doled
        out unemployment dropped rapidly, and while, again, it's unlikely that the stimulus was the
        primary cause, it's also likely that it played a role. Take Alabama as an example – the
        prisons are still being constructed and won't be finished until 2025. This gave builders,
        contractors, architects and engineers a large, long term project to work on.
      </p>

      {@html `<iframe title="Unemployment Rate" aria-label="Line chart" id="datawrapper-chart-LyjDA" src="https://datawrapper.dwcdn.net/LyjDA/1/" scrolling="no" frameborder="0" style="width: 0; min-width: 100% !important; border: none;" height="394" data-external="1"></iframe>`}

      <p>
        A similar example is ongoing in Syracuse, NY. The Onondaga County Legislature announced an
        $85 million aquarium not long after
      </p>
    </ArticleBody>

    <section class="map-section" aria-labelledby="point-map-heading">
      <h2 id="point-map-heading">All project points</h2>

    <div class="summary-grid" aria-label="Point map summary">
      <div class="summary-card">
        <span class="label">Plotted projects</span>
        <strong>{totals.projects}</strong>
      </div>
      <div class="summary-card">
        <span class="label">Total obligations</span>
        <strong>{formatCompactCurrency(totals.obligations)}</strong>
      </div>
      <div class="summary-card">
        <span class="label">Total expenditures</span>
        <strong>{formatCompactCurrency(totals.expenditures)}</strong>
      </div>
      {#if highlightedFeature}
        <div class="summary-card highlight-card">
          <span class="label">Alabama highlighted project</span>
          <strong>{formatCompactCurrency(highlightedFeature.properties.totalExpenditures)}</strong>
        </div>
      {/if}
    </div>

    <Legend
      title="Completion status"
      mode="categorical"
      items={statusLegend}
      noData={{ label: 'Not reported', color: statusColors['Not reported'] }}
    />

    <div class="filter-panel">
      <div class="filter-top-row">
      </div>
      <div class="filter-group filter-group--building">
        <fieldset class="filter-fieldset">
          <legend class="filter-label">Building type</legend>
          <div class="building-grid">
            {#each BUILDING_TYPES as b}
              <label class="checkbox-item">
                <input
                  type="checkbox"
                  checked={filterBuildings.includes(b)}
                  onchange={(e) => {
                    filterBuildings = e.target.checked
                      ? [...filterBuildings, b]
                      : filterBuildings.filter((x) => x !== b);
                  }}
                />
                {b}
              </label>
            {/each}
          </div>
        </fieldset>
      </div>
      <div class="filter-footer">
        <span class="filter-count">
          {filteredFeatures.length} of {pointFeatures.length} projects shown
        </span>
        {#if hasActiveFilters}
          <button class="filter-clear" onclick={clearFilters}>Clear filters</button>
        {/if}
      </div>
    </div>

    {#if loading}
      <div class="loading-panel">Loading project points…</div>
    {:else if errorMessage}
      <div class="loading-panel error">{errorMessage}</div>
    {:else}
      <Map
        longitude={-98}
        latitude={39}
        zoom={3.3}
        minZoom={2.5}
        maxBounds={[[-180, 10], [-50, 75]]}
        theme="positron"
        height={500}
        border
        caption="All projects with anti-overlap point offsets enabled. Point size reflects total expenditures."
        credit="Map tiles: OpenFreeMap / OpenStreetMap contributors"
      >
        <MapLayer
          id="state-lines"
          type="line"
          data={statesData}
          paint={{
            'line-color': '#aaaaaa',
            'line-width': 0.8,
            'line-opacity': 0.9,
          }}
        />
        <MapLayer
          id="state-labels"
          type="symbol"
          data={statesData}
          layout={{
            'text-field': ['get', 'abbrev'],
            'text-size': 10,
            'text-font': ['Open Sans Bold'],
            'text-allow-overlap': false,
            'text-ignore-placement': false,
          }}
          paint={{
            'text-color': '#444444',
            'text-halo-color': 'rgba(255,255,255,0.85)',
            'text-halo-width': 1.5,
          }}
        />
        <MapLayer
          id="project-points"
          type="circle"
          data={pointLayerData}
          paint={{
            'circle-color': [
              'match',
              ['get', 'completionStatus'],
              'Completed', statusColors.Completed,
              'Completed 50% or more', statusColors['Completed 50% or more'],
              'Completed less than 50%', statusColors['Completed less than 50%'],
              'Cancelled', statusColors.Cancelled,
              'Not Started', statusColors['Not Started'],
              statusColors['Not reported'],
            ],
            'circle-radius': [
              'step', ['get', 'totalExpenditures'],
              5, 100_000, 6, 1_000_000, 7, 5_000_000, 8.5, 10_000_000, 10,
            ],
            'circle-stroke-width': 1.2,
            'circle-stroke-color': '#ffffff',
            'circle-opacity': 0.86,
          }}
          popup={buildPopup}
        />
        <ImageLayer
          id="weir-community-center"
          imageUrl="{base}/communitycenter.jpg"
          data={weirData}
          iconSize={0.07}
          popup={buildPopup}
        />
        <ImageLayer
          id="syracuse-aquarium"
          imageUrl="{base}/fish.png"
          data={aquariumData}
          iconSize={0.07}
          popup={buildPopup}
        />
        <ImageLayer
          id="alabama-jail"
          imageUrl="{base}/jail.avif"
          data={alabamaJailData}
          iconSize={0.07}
          popup={buildPopup}
        />
        <MapLayer
          id="highlighted-alabama-project-label"
          type="symbol"
          data={highlightedLayerData}
          layout={{
            'text-field': highlightedSpentLabel,
            'text-size': 12,
            'text-offset': [0, 1.8],
            'text-anchor': 'top',
            'text-font': ['Open Sans Bold'],
          }}
          paint={{
            'text-color': '#111827',
            'text-halo-color': '#ffffff',
            'text-halo-width': 1.1,
          }}
        />
      </Map>
    {/if}
    </section>
  </article>

  <!-- Sticky sidebar -->
  <aside class="sidebar">
    <RecentPosts posts={recentPosts} />
  </aside>

</div>

{#if selectedFeature}
  <div
    class="detail-overlay"
    role="presentation"
    onclick={() => (selectedFeature = null)}
    onkeydown={(e) => { if (e.key === 'Escape') selectedFeature = null; }}
  >
    <div
      class="detail-window"
      role="dialog"
      aria-modal="true"
      aria-label="Project description"
      onclick={(e) => e.stopPropagation()}
    >
      <div class="detail-header">
        <h3 class="detail-title">{selectedFeature.properties.projectName}</h3>
        <button class="detail-close" onclick={() => (selectedFeature = null)} aria-label="Close">&#x2715;</button>
      </div>
      <div class="detail-body">
        <p class="detail-meta">
          {selectedFeature.properties.recipientName} &middot; {selectedFeature.properties.state}
        </p>
        <p class="detail-description">{selectedFeature.properties.description}</p>
        <div class="detail-financials">
          <div class="detail-financial-item">
            <span class="detail-financial-label">Total obligations</span>
            <strong>{formatCurrency(selectedFeature.properties.totalObligations)}</strong>
          </div>
          <div class="detail-financial-item">
            <span class="detail-financial-label">Total expenditures</span>
            <strong>{formatCurrency(selectedFeature.properties.totalExpenditures)}</strong>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}

<style lang="scss">
  @use '$lib/styles' as *;

  /* ── Two-column page grid ── */
  .page-layout {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 280px;
    gap: var(--spacing-xl);
    align-items: start;
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--spacing-lg) var(--spacing-md);
    box-sizing: border-box;
  }

  /* ── Article column ── */
  .article-column {
    /* min-width: 0 prevents the column from overflowing the grid cell */
    min-width: 0;
  }

  /* ── Map section ── */
  .map-section {
    margin-top: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
  }

  h2 {
    font-family: var(--font-serif);
    color: var(--color-dark);
    font-size: clamp(var(--font-size-2xl), 3vw, var(--font-size-4xl));
    margin: 0 0 var(--spacing-sm);
  }

  .summary-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--spacing-xs);
    margin-bottom: var(--spacing-md);
  }

  .summary-card,
  .loading-panel {
    background: var(--color-white);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-md);
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
  }

  .summary-card {
    padding: var(--spacing-sm);
    display: grid;
    gap: var(--spacing-xxs);

    .label {
      color: var(--color-medium-gray);
      font-size: var(--font-size-xs);
    }

    strong {
      font-size: var(--font-size-lg);
      line-height: var(--leading-tight);
      color: var(--color-dark);
    }
  }

  .highlight-card {
    border-color: #f3b184;
    background: color-mix(in srgb, #d74d00 8%, white);
  }

  .loading-panel {
    padding: var(--spacing-lg);
  }

  .loading-panel.error {
    border-color: #f4c7c3;
    background: #fff5f5;
    color: #8b1f1f;
  }

  :global(.project-popup) {
    display: grid;
    gap: 0.25rem;
    font-size: var(--font-size-sm);
  }

  :global(.project-popup .badge) {
    display: inline-flex;
    width: fit-content;
    color: #fff;
    font-size: var(--font-size-xs);
    border-radius: 999px;
    padding: 0.12rem 0.5rem;
    margin-bottom: 0.2rem;
  }

  :global(.project-popup strong) {
    color: var(--color-dark);
  }

  :global(.popup-info-btn) {
    display: block;
    width: 100%;
    margin-top: 0.4rem;
    padding: 0.25rem 0.5rem;
    background: none;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    font-family: var(--font-sans);
    font-size: var(--font-size-xs);
    color: var(--color-medium-gray);
    cursor: pointer;
    text-align: left;
  }

  :global(.popup-info-btn:hover) {
    background: var(--color-light-gray);
    color: var(--color-dark);
  }

  /* ── Filter panel ── */
  .filter-panel {
    background: var(--color-light-gray);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-sm);
    padding: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .filter-top-row {
    display: grid;
    grid-template-columns: auto auto 1fr;
    gap: var(--spacing-sm);
    align-items: start;
  }

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }

  .filter-label {
    font-family: var(--font-sans);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-bold);
    text-transform: uppercase;
    letter-spacing: var(--letter-spacing-wide);
    color: var(--color-medium-gray);
    margin: 0;
    padding: 0;
    border: none;
  }

  .filter-select {
    font-family: var(--font-sans);
    font-size: var(--font-size-xs);
    color: var(--color-dark);
    background: var(--color-white);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    padding: 0.25rem 0.4rem;
    cursor: pointer;
  }

  .filter-fieldset {
    border: none;
    margin: 0;
    padding: 0;
  }

  .checkbox-group {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem 0.75rem;
    margin-top: 0.1rem;
  }

  .building-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.2rem 0.75rem;
    margin-top: 0.1rem;
  }

  .checkbox-item {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    font-family: var(--font-sans);
    font-size: var(--font-size-xs);
    color: var(--color-text);
    cursor: pointer;
    white-space: nowrap;

    input[type='checkbox'] {
      width: 12px;
      height: 12px;
      flex-shrink: 0;
      cursor: pointer;
      accent-color: var(--color-dark);
    }
  }

  .filter-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: var(--spacing-xxs);
    border-top: 1px solid var(--color-border);
  }

  .filter-count {
    font-family: var(--font-sans);
    font-size: var(--font-size-xs);
    color: var(--color-medium-gray);
  }

  .filter-clear {
    font-family: var(--font-sans);
    font-size: var(--font-size-xs);
    color: var(--color-medium-gray);
    background: none;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    padding: 0.2rem 0.5rem;
    cursor: pointer;

    &:hover {
      background: var(--color-white);
      color: var(--color-dark);
    }
  }

  @include mobile {
    .filter-top-row {
      grid-template-columns: 1fr 1fr;
    }

    .filter-group--status {
      grid-column: 1 / -1;
    }
  }

  /* ── Detail modal ── */
  .detail-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.45);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-md);
  }

  .detail-window {
    background: var(--color-white);
    border-radius: var(--border-radius-md);
    box-shadow: 0 24px 64px rgba(0, 0, 0, 0.25);
    max-width: 500px;
    width: 100%;
    max-height: 80vh;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }

  .detail-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: var(--spacing-sm);
    padding: var(--spacing-md);
    border-bottom: 1px solid var(--color-border);
    position: sticky;
    top: 0;
    background: var(--color-white);
  }

  .detail-title {
    font-family: var(--font-display);
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-dark);
    margin: 0;
    line-height: var(--leading-snug);
  }

  .detail-close {
    flex-shrink: 0;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.1rem;
    line-height: 1;
    color: var(--color-medium-gray);
    padding: 0.1rem 0.25rem;
    border-radius: 4px;
  }

  .detail-close:hover {
    background: var(--color-light-gray);
    color: var(--color-dark);
  }

  .detail-body {
    padding: var(--spacing-md);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .detail-meta {
    font-family: var(--font-sans);
    font-size: var(--font-size-sm);
    color: var(--color-medium-gray);
    margin: 0;
  }

  .detail-description {
    font-family: var(--font-sans);
    font-size: var(--font-size-base);
    line-height: var(--leading-normal);
    color: var(--color-text);
    margin: 0;
  }

  .detail-financials {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-xs);
    padding-top: var(--spacing-sm);
    border-top: 1px solid var(--color-border);
  }

  .detail-financial-item {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }

  .detail-financial-label {
    font-family: var(--font-sans);
    font-size: var(--font-size-xs);
    color: var(--color-medium-gray);
    text-transform: uppercase;
    letter-spacing: var(--letter-spacing-wide);
  }

  .detail-financial-item strong {
    font-size: var(--font-size-base);
    color: var(--color-dark);
  }

  /* ── Sidebar ── */
  .sidebar {
    position: sticky;
    top: var(--spacing-lg);
    padding-top: var(--spacing-lg);
  }

  /* ── Mobile ── */
  @include mobile {
    .page-layout {
      grid-template-columns: 1fr;
      gap: var(--spacing-lg);
      padding: var(--spacing-md);
    }

    .sidebar {
      position: static;
      padding-top: 0;
      border-top: 2px solid var(--color-border);
      padding-top: var(--spacing-md);
    }

    .summary-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
</style>
