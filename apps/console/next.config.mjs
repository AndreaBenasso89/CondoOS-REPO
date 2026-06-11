/** @type {import('next').NextConfig} */
// Local dev (`pnpm dev`) runs as a normal app. For a hostable build we produce a fully static
// export (the Console is entirely client-side, with state in localStorage), suitable for GitHub
// Pages or any static host. `STATIC_EXPORT` + `BASE_PATH` are set by the deploy workflow.
const isExport = process.env.STATIC_EXPORT === "true";
const basePath = process.env.BASE_PATH || "";

const nextConfig = {
  reactStrictMode: true,
  ...(isExport
    ? {
        output: "export",
        trailingSlash: true,
        images: { unoptimized: true },
        basePath,
        assetPrefix: basePath || undefined,
      }
    : {}),
};

export default nextConfig;
