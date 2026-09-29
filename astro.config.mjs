import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  trailingSlash: 'always',
  // Node 22 resolves "localhost" to IPv6 ::1 only; on this machine the browser
  // could not reach it (ERR_CONNECTION_REFUSED). Bind explicitly to IPv4 loopback.
  // For testing on a phone in the same Wi-Fi: npm run dev -- --host
  server: {
    host: '127.0.0.1',
    port: 4321,
  },
});
