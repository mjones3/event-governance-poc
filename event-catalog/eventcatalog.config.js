/** @type {import('@eventcatalog/core/bin/eventcatalog.config').Config} */
export default {
  title: 'EventCatalog',
  tagline: 'This internal platform provides a comprehensive view of our event-driven architecture across all systems. Use this portal to discover existing domains, explore services and their dependencies, and understand the message contracts that connect our infrastructure',
  organizationName: 'BioPro',
  homepageLink: 'https://eventcatalog.dev/',
  editUrl: 'https://github.com/boyney123/eventcatalog-demo/edit/master',
  output: 'static',
  trailingSlash: false,
  base: '/',
  logo: {
    alt: 'EventCatalog Logo',
    src: '/logo.png',
    text: 'EventCatalog'
  },
  docs: {
    sidebar: {
      type: 'LIST_VIEW'
    },
  },
  rss: {
    enabled: true,
    limit: 20
  },
  llmsTxt: {
    enabled: true,
  },
  cId: '0d73ee9c-504e-4b58-88ec-9b354c5a4c2b',
  generators: [
    [
      '@eventcatalog/generator-confluent-schema-registry',
      {
        schemaRegistryUrl: 'http://localhost:8081',
        licenseKey: 'CN7A-UDP7-2SF8-PZD4-EZE7-D3OB',
        includeAllVersions: true
      }
    ]
  ]
}
