<!--
@component
RecentPosts.svelte — A sidebar showing a list of recent posts with thumbnails and dates.

Displays recent articles with optional images, titles, and publication dates.

USAGE EXAMPLE:
<RecentPosts posts={recentPostsData} />
-->
<script>
  let {
    posts = [
      {
        title: 'Sample Post Title',
        date: '2026-05-01',
        url: '#',
        image: null,
      },
    ],
  } = $props();

  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }
</script>

<aside class="recent-posts">
  <h3 class="recent-posts-title">Recent Posts</h3>
  <ul class="posts-list">
    {#each posts as post (post.url)}
      <li class="post-item">
        <a href={post.url} class="post-link">
          {#if post.image}
            <img src={post.image} alt={post.title} class="post-image" />
          {/if}
          <span class="post-content">
            <span class="post-title">{post.title}</span>
            <span class="post-date">{formatDate(post.date)}</span>
          </span>
        </a>
      </li>
    {/each}
  </ul>
</aside>

<style lang="scss">
  @use '../../styles' as *;

  .recent-posts {
    background: #f9f9f9;
    border-left: 3px solid var(--color-accent);
    padding: var(--spacing-md);
    margin: var(--spacing-lg) 0;
  }

  .recent-posts-title {
    font-family: var(--font-display);
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    color: var(--color-dark);
    margin: 0 0 var(--spacing-md) 0;
    padding: 0;
  }

  .posts-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .post-item {
    border-bottom: 1px solid #e5e5e5;
    padding-bottom: var(--spacing-md);

    &:last-child {
      border-bottom: none;
      padding-bottom: 0;
    }
  }

  .post-link {
    display: flex;
    gap: var(--spacing-sm);
    text-decoration: none;
    color: var(--color-dark);
    transition: var(--transition-opacity);

    &:hover {
      opacity: 0.8;
    }
  }

  .post-image {
    width: 80px;
    height: 80px;
    object-fit: cover;
    flex-shrink: 0;
    border-radius: 3px;
  }

  .post-content {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    flex: 1;
    gap: var(--spacing-xs);
  }

  .post-title {
    font-family: var(--font-sans);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-bold);
    line-height: 1.3;
    color: var(--color-dark);
  }

  .post-date {
    font-family: var(--font-sans);
    font-size: var(--font-size-xs);
    color: var(--color-medium-gray);
  }

  @include tablet {
    .recent-posts {
      margin: var(--spacing-xl) 0;
      padding: var(--spacing-lg);
    }
  }
</style>
