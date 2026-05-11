import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import SiteHeader from '$lib/components/Layout/SiteHeader.svelte';
import SiteFooter from '$lib/components/Layout/SiteFooter.svelte';

describe('SiteHeader', () => {
  it('renders the logo', () => {
    render(SiteHeader);
    expect(screen.getByLabelText('Issue Number One')).toBeTruthy();
  });

  it('renders default navigation links', () => {
    render(SiteHeader);
    expect(screen.getByText('Economy')).toBeTruthy();
    expect(screen.getByText('Featured')).toBeTruthy();
  });

  it('renders custom navigation links', () => {
    render(SiteHeader, {
      props: {
        navLinks: [{ label: 'Sports', href: '/sports' }],
      },
    });
    expect(screen.getByText('Sports')).toBeTruthy();
  });

  it('hides nav when navLinks is empty', () => {
    const { container } = render(SiteHeader, {
      props: { navLinks: [] },
    });
    expect(container.querySelector('nav')).toBeNull();
  });
});

describe('SiteFooter', () => {
  it('renders the footer title', () => {
    render(SiteFooter);
    expect(screen.getByText('Welcome to Issue Number One')).toBeTruthy();
  });

  it('renders footer credit', () => {
    render(SiteFooter);
    expect(screen.getByText('Elegant Themes')).toBeTruthy();
    expect(screen.getByText('WordPress')).toBeTruthy();
  });
});
