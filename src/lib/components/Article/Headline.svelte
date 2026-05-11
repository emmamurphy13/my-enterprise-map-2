<!--
@component
Headline.svelte — A large serif h1 headline shared by ArticleHeader and DatabaseHeader.

Displays the provided text as a bold serif heading in the site dark color with
tight line-height. Font size steps up at the tablet breakpoint.

USAGE EXAMPLE:
<Headline text="City Council Approves New Budget" />
-->
<script>
  let {
    text = '', // The headline text to display
  } = $props();
</script>

{#if text}
  <h1 class="headline">{text}</h1>
{/if}

<style lang="scss">
  @use '../../styles' as *;

  .headline {
    font-family: var(--font-display);
    font-size: clamp(2rem, 5.5vw, 3.75rem);
    font-weight: 600;
    line-height: 1.1;
    color: var(--color-dark);
    margin: 1rem 0 0.6rem 0;
    letter-spacing: -0.015em;
    text-align: center;

    @include tablet {
      font-size: clamp(2.75rem, 5.5vw, 4.5rem);
      text-align: left;
      margin-left: 0;
    }
  }
</style>
