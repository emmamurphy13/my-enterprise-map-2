<script>
  import { base } from '$app/paths';

  let {
    navLinks = [
      { label: 'Economy', href: 'https://issuenumberone.journalism.cuny.edu/category/economy/' },
      { label: 'Featured', href: 'https://issuenumberone.journalism.cuny.edu/category/featured/' },
      { label: 'Immigration', href: 'https://issuenumberone.journalism.cuny.edu/category/immigration/' },
      { label: 'Jobs', href: 'https://issuenumberone.journalism.cuny.edu/category/jobs/' },
      { label: 'Manufacturing', href: 'https://issuenumberone.journalism.cuny.edu/category/manufacturing/' },
      { label: 'Oil and Gas', href: 'https://issuenumberone.journalism.cuny.edu/category/oil-and-gas/' },
    ],
  } = $props();
</script>

<header class="site-header">
  <div class="masthead-wrapper">
    <div class="masthead">
      <a href={`${base}/`} class="logo" aria-label="Issue Number One">
        <img
          src="http://cdn.nycitynewsservice.com/blogs.dir/423/files/2017/03/issue_logo.png"
          alt="Issue Number One"
          class="logo-img"
        />
      </a>

      {#if navLinks.length > 0}
        <nav class="main-nav" aria-label="Main navigation">
          <ul class="nav-list">
            {#each navLinks as link (link.href)}
              <li>
                <a href={link.href} class="nav-link">{link.label}</a>
              </li>
            {/each}
          </ul>
        </nav>
      {/if}
    </div>
  </div>
</header>

<style lang="scss">
  @use '../../styles' as *;

  .site-header {
    border-bottom: 1px solid #d9d9d9;
    box-shadow: 0 1px 0 rgba(0, 0, 0, 0.03);
  }

  .masthead-wrapper {
    background: #ffffff;
  }

  .masthead {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--spacing-md);
    padding: var(--spacing-sm) var(--spacing-md);
    max-width: var(--max-width-wide);
    margin: 0 auto;
  }

  .logo {
    display: inline-block;
    text-decoration: none;
    flex-shrink: 0;
  }

  .logo:hover {
    opacity: 0.85;
    text-decoration: none;
  }

  .logo-img {
    height: 54px;
    width: auto;
    display: block;
  }

  .main-nav {
    display: none;
  }

  .nav-list {
    display: flex;
    flex-wrap: nowrap;
    list-style: none;
    gap: var(--spacing-md);
    margin: 0;
    padding: 0;
  }

  .nav-link {
    color: var(--color-dark);
    text-decoration: none;
    font-family: var(--font-sans);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-normal);
    text-transform: uppercase;
    letter-spacing: var(--letter-spacing-wide);
    white-space: nowrap;
    transition: var(--transition-opacity);
  }

  .nav-link:hover {
    color: var(--color-accent);
    text-decoration: none;
  }

  @include desktop {
    .main-nav {
      display: flex;
      align-items: center;
    }
  }

  @include tablet {
    .masthead {
      padding-inline: var(--spacing-sm);
    }
  }
</style>
