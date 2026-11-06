function validatedWhoamiUrl(raw) {
  if (!raw) throw new Error('WHOAMI_URL is required; browser smoke was not run');
  let url;
  try { url = new URL(raw); } catch { throw new Error('WHOAMI_URL must be a valid URL'); }
  if (url.protocol !== 'https:' ||
      !/^whoami-[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.dev\.lab\.petebeegle\.com$/.test(url.hostname) ||
      url.username || url.password || url.port || url.pathname !== '/' || url.search || url.hash) {
    throw new Error('WHOAMI_URL must be an HTTPS Whoami branch host in dev.lab.petebeegle.com, with no credentials, custom port, path, query, or fragment');
  }
  return url.href;
}
module.exports = { validatedWhoamiUrl };
