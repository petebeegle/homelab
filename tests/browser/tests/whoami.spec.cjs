const { test, expect } = require('@playwright/test');
const { validatedWhoamiUrl } = require('./url-guard.cjs');

test('Whoami responds through the real development Gateway', async ({ page }) => {
  const target = validatedWhoamiUrl(process.env.WHOAMI_URL);
  const response = await page.goto(target, { waitUntil: 'domcontentloaded' });
  expect(response, 'navigation must yield an HTTP response').not.toBeNull();
  expect(response.status(), 'Gateway response must be successful').toBeGreaterThanOrEqual(200);
  expect(response.status(), 'Gateway response must be successful').toBeLessThan(300);
  expect(new URL(page.url()).origin, 'unexpected redirect outside development route').toBe(new URL(target).origin);
  const body = await page.locator('body').innerText();
  expect(body, 'Whoami should expose its request identity').toMatch(/Hostname:|IP:|Request:|GET \/ HTTP/i);
});
