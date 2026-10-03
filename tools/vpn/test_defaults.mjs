import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

// Run against the real libsql dependency, locally or inside the wg-easy image.
const library = process.env.WG_TEST_LIBSQL || '/app/server/node_modules/@libsql/client/lib-esm/node.js';
const { createClient } = await import(pathToFileURL(resolve(library)).href);
const manifest = await readFile(process.env.WG_TEST_CONFIG || 'kubernetes/infra/network/vpn/global-config.yaml', 'utf8');
const source = manifest.split('  reconcile-wg-easy-defaults.mjs: |\n')[1]
  .split('\n').map(line => line.replace(/^    /, '')).join('\n')
  .replace('/app/server/node_modules/@libsql/client/lib-esm/node.js', pathToFileURL(resolve(library)).href);
const root = await mkdtemp(join(tmpdir(), 'wg-defaults-'));
const script = join(root, 'reconcile.mjs');
await writeFile(script, source);
let passed = 0;
async function test(name, fn) {
  const directory = await mkdtemp(join(root, 'case-'));
  const path = join(directory, 'test.db');
  const db = createClient({ url: 'file:' + path });
  try {
    await db.execute(`CREATE TABLE user_configs_table (id TEXT PRIMARY KEY, host TEXT, port INTEGER,
      default_allowed_ips TEXT, default_dns TEXT)`);
    await db.execute(`INSERT INTO user_configs_table VALUES
      ('wg0', 'old.example.net', 30000, '["192.168.40.0/24"]', '["192.168.40.250"]'),
      ('untouched', 'other.example.net', 12345, '[]', '[]')`);
    await db.execute('CREATE TABLE clients_table (id INTEGER, private_key TEXT)');
    await db.execute("INSERT INTO clients_table VALUES (1, 'test-key-preserve')");
    const run = (extra = {}) => spawnSync(process.execPath, [script], { encoding: 'utf8', env: {
      ...process.env, WG_EASY_DB_PATH: path, WG_EASY_CONFIG_ID: 'wg0',
      WG_EASY_HOST: 'new.example.net', WG_EASY_DEFAULT_ALLOWED_IPS: '192.168.40.0/24',
      WG_EASY_DEFAULT_DNS: '192.168.40.250', ...extra,
    }});
    await fn({ db, run, path });
    console.log('PASS ' + name);
    passed++;
  } finally { db.close(); }
}
try {
  await test('corrects stale host and preserves port, peers, and unrelated config', async ({ db, run }) => {
    const beforePeers = (await db.execute('SELECT * FROM clients_table')).rows;
    const beforeOther = (await db.execute("SELECT * FROM user_configs_table WHERE id='untouched'")).rows;
    const result = run();
    assert.equal(result.status, 0, result.stderr);
    const row = (await db.execute("SELECT * FROM user_configs_table WHERE id='wg0'")).rows[0];
    assert.equal(row.host, 'new.example.net');
    assert.equal(row.port, 30000);
    assert.equal(row.default_allowed_ips, '["192.168.40.0/24"]');
    assert.equal(row.default_dns, '["192.168.40.250"]');
    assert.deepEqual((await db.execute('SELECT * FROM clients_table')).rows, beforePeers);
    assert.deepEqual((await db.execute("SELECT * FROM user_configs_table WHERE id='untouched'")).rows, beforeOther);
  });
  await test('second reconciliation performs no database update', async ({ db, run }) => {
    assert.equal(run().status, 0);
    await db.execute("CREATE TRIGGER reject_update BEFORE UPDATE ON user_configs_table BEGIN SELECT RAISE(FAIL, 'unexpected write'); END");
    const result = run();
    assert.equal(result.status, 0, result.stderr);
  });
  await test('still corrects DNS and allowed IP defaults together with host', async ({ db, run }) => {
    const result = run({ WG_EASY_DEFAULT_DNS: '192.0.2.53', WG_EASY_DEFAULT_ALLOWED_IPS: '192.0.2.0/24' });
    assert.equal(result.status, 0, result.stderr);
    const row = (await db.execute("SELECT * FROM user_configs_table WHERE id='wg0'")).rows[0];
    assert.equal(row.host, 'new.example.net');
    assert.equal(row.default_dns, '["192.0.2.53"]');
    assert.equal(row.default_allowed_ips, '["192.0.2.0/24"]');
  });
  await test('rejects a missing host without modifying the database', async ({ db, run }) => {
    const before = (await db.execute('SELECT * FROM user_configs_table')).rows;
    assert.notEqual(run({ WG_EASY_HOST: '' }).status, 0);
    assert.deepEqual((await db.execute('SELECT * FROM user_configs_table')).rows, before);
  });
  await test('fresh installation without a database is left to wg-easy setup', async ({ run, path }) => {
    const result = run({ WG_EASY_DB_PATH: path + '.absent' });
    assert.equal(result.status, 0, result.stderr);
  });
  await test('missing wg0 row does not overwrite other configurations', async ({ db, run }) => {
    await db.execute("DELETE FROM user_configs_table WHERE id='wg0'");
    const before = (await db.execute('SELECT * FROM user_configs_table')).rows;
    const result = run();
    assert.equal(result.status, 0, result.stderr);
    assert.deepEqual((await db.execute('SELECT * FROM user_configs_table')).rows, before);
  });
  console.log(passed + ' tests passed');
} finally { await rm(root, { recursive: true, force: true }); }
