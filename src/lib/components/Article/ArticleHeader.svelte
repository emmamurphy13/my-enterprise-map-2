<script>
  import Kicker from './Kicker.svelte';
  import Headline from './Headline.svelte';

  let {
    headline, // Required: The main title of the article
    kicker = '', // Optional: Eyebrow label rendered above the headline
    byline = '', // Optional: The author's name(s)
    pubDate = '', // Optional: Publication date in YYYY-MM-DD format
  } = $props();

  // local date formatter to avoid importing Pubdate
  function formatDate(dateString) {
    if (!dateString) return '';
    if (!/^\d{4}-\d{2}-\d{2}$/.test(dateString)) return dateString;
    const [year, month, day] = dateString.split('-').map(Number);
    const d = new Date(year, month - 1, day);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(d);
  }
</script>

<header class="article-header">
  <Kicker text={kicker} />
  <Headline text={headline} />

  {#if byline || pubDate}
    <p class="meta-line">
      {#if byline}
        by <span class="meta-by">{byline}</span>
      {/if}
      {#if pubDate}
        {#if byline}<span class="sep"> | </span>{/if}
        <span class="meta-date">{formatDate(pubDate)}</span>
      {/if}
      <span class="sep"> | </span>
      <span class="meta-cat">Economy</span>
      <span class="sep"> | </span>
      <span class="meta-comments">0 comments</span>
    </p>
  {/if}
</header>

<style lang="scss">
  @use '../../styles' as *;

  .article-header {
    margin-bottom: var(--spacing-lg);
    text-align: center;
  }

  .meta-line {
    font-family: var(--font-sans);
    font-size: var(--font-size-sm);
    color: var(--color-medium-gray);
    margin: 0.5rem 0 1.25rem 0;
    text-align: center;
  }

  .meta-line .meta-by,
  .meta-line .meta-date,
  .meta-line .meta-cat,
  .meta-line .meta-comments {
    color: var(--color-medium-gray);
  }

  .meta-line .sep {
    color: var(--color-medium-gray);
    margin: 0 0.35rem;
  }

  @include tablet {
    .meta-line {
      font-size: var(--font-size-sm);
    }
  }

  @include desktop {
    .article-header {
      text-align: left;
      margin-left: 0;
    }

    .meta-line {
      text-align: left;
      margin-left: 0;
    }
  }
</style>
