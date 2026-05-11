<script module>
  import RecentPosts from '$lib/components/Article/RecentPosts.svelte';

  export const meta = {
    title: 'Article/RecentPosts',
    component: RecentPosts,
  };
</script>

<script>
  import { Story } from '@storybook/addon-svelte-csf';

  const samplePosts = [
    {
      title: 'Sample Article One',
      date: '2026-05-01',
      url: 'https://example.com/1',
      image: null,
    },
    {
      title: 'Sample Article Two',
      date: '2026-04-28',
      url: 'https://example.com/2',
      image: null,
    },
  ];
</script>

<Story name="Default" args={{ posts: samplePosts }} />
