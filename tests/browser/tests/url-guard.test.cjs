const { test } = require('node:test');
const assert = require('node:assert/strict');
const { validatedWhoamiUrl } = require('./url-guard.cjs');

test('accepts an isolated development branch URL', () => {
  assert.equal(validatedWhoamiUrl('https://whoami-golden-path.dev.lab.petebeegle.com'), 'https://whoami-golden-path.dev.lab.petebeegle.com/');
});
test('fails closed without URL', () => assert.throws(() => validatedWhoamiUrl(undefined), /required/));
for (const value of [
  'http://whoami-test.dev.lab.petebeegle.com',
  'https://whoami.lab.petebeegle.com',
  'https://whoami-test.dev.lab.petebeegle.com.evil.test',
  'https://whoami-test.dev.lab.petebeegle.com:8443',
  'https://whoami-test.dev.lab.petebeegle.com/admin',
  'https://user:pass@whoami-test.dev.lab.petebeegle.com',
]) test('rejects unsafe target: ' + value, () => assert.throws(() => validatedWhoamiUrl(value)));
