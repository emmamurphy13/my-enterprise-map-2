<script>
  const currentYear = new Date().getFullYear();
</script>

<footer class="site-footer">
  <div class="footer-main">
    <div class="footer-container">
      <div class="footer-grid">
        <div class="footer-widget">
          <h4 class="footer-widget-title"><em>Welcome to Issue Number One</em></h4>
        </div>
        <div class="footer-widget">
          <p class="footer-widget-text">
            Welcome to <em>Issue Number One</em>, a site covering the economy produced by young
            journalists in New York City. Email the editor Greg David at
            <a href="mailto:gregdavid49@gmail.com">gregdavid49@gmail.com</a>.
          </p>
        </div>
      </div>
    </div>
  </div>

  <div class="footer-bottom">
    <div class="footer-container">
      <p class="footer-credit">
        Designed by
        <a href="http://www.elegantthemes.com" rel="noopener noreferrer">Elegant Themes</a>
        | Powered by
        <a href="http://www.wordpress.org" rel="noopener noreferrer">WordPress</a>
      </p>
    </div>
  </div>
</footer>

<style lang="scss">
  @use '../../styles' as *;

  .site-footer {
    margin-top: var(--spacing-xxl);
  }

  .footer-main {
    background-color: #282828;
    padding: var(--spacing-xl) var(--spacing-md);
  }

  .footer-container {
    max-width: var(--max-width-wide);
    margin: 0 auto;
  }

  .footer-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);

    @include tablet {
      grid-template-columns: 1fr 2fr;
      gap: var(--spacing-xl);
    }
  }

  .footer-widget-title {
    color: #cccccc;
    font-family: var(--font-display);
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    margin: 0;
    line-height: var(--leading-snug);
  }

  .footer-widget-text {
    color: #9b9b9b;
    font-family: var(--font-sans);
    font-size: var(--font-size-sm);
    line-height: var(--leading-normal);
    margin: 0;
  }

  .footer-widget-text a {
    color: #aaaaaa;
    text-decoration: underline;
  }

  .footer-widget-text a:hover {
    color: #cccccc;
  }

  .footer-bottom {
    background-color: #1e1e1e;
    padding: var(--spacing-sm) var(--spacing-md);
    text-align: center;
  }

  .footer-credit {
    color: #777777;
    font-family: var(--font-sans);
    font-size: var(--font-size-sm);
    margin: 0;
  }

  .footer-credit a {
    color: #888888;
    text-decoration: none;
  }

  .footer-credit a:hover {
    color: #aaaaaa;
    text-decoration: underline;
  }
</style>
