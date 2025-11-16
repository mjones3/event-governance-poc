export default {
  cId: '4f57ce39-d69d-4c1a-b920-2a6780ee6039',
  title: 'BioPro Event Catalog',
  tagline: 'Event Governance and Schema Documentation',
  organizationName: 'BioPro',
  homepageLink: 'https://github.com/mjones3/event-governance-poc',
  landingPage: '',

  // Logo and branding
  logo: {
    alt: 'BioPro Logo',
    src: '/logo.png',
  },

  // Documentation sections
  docs: {
    sidebar: {
      hideable: true,
    },
  },

  // Generators (plugins)
  generators: [
    [
      './plugins/schema-registry-generator',
      {
        schemaRegistryUrl: 'http://localhost:8081',
        // Map schema subjects to domains
        domainMapping: {
          'OrderCreatedEvent': 'Orders',
          'ApheresisPlasmaProductCreatedEvent': 'Manufacturing',
          'CollectionReceivedEvent': 'Collections'
        },
        // Services that publish these events
        serviceMapping: {
          'OrderCreatedEvent': 'orders-service',
          'ApheresisPlasmaProductCreatedEvent': 'manufacturing-service',
          'CollectionReceivedEvent': 'collections-service'
        }
      }
    ]
  ],
};
