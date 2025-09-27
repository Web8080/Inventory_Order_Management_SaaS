import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
  Flex,
  Icon,
  Divider,
} from '@chakra-ui/react';

export function IntegrationsPage() {
  const integrations = [
    {
      name: 'Shopify',
      description: 'Connect your Shopify store to sync products and orders',
      status: 'Connected',
      lastSync: '2 hours ago',
      icon: '🛍️',
    },
    {
      name: 'WooCommerce',
      description: 'Sync your WooCommerce store data',
      status: 'Not Connected',
      lastSync: 'Never',
      icon: '🛒',
    },
    {
      name: 'Amazon',
      description: 'Manage your Amazon marketplace listings',
      status: 'Not Connected',
      lastSync: 'Never',
      icon: '📦',
    },
    {
      name: 'QuickBooks',
      description: 'Sync financial data with QuickBooks',
      status: 'Not Connected',
      lastSync: 'Never',
      icon: '📊',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Connected': return 'green';
      case 'Not Connected': return 'gray';
      case 'Error': return 'red';
      default: return 'gray';
    }
  };

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        <Box>
          <Heading size="lg" color="gray.700" mb={2}>
            Integrations
          </Heading>
          <Text color="gray.600">
            Connect your external platforms to sync data automatically
          </Text>
        </Box>

        <VStack spacing={4} align="stretch">
          {integrations.map((integration, index) => (
            <Card key={index}>
              <CardBody>
                <Flex justify="space-between" align="center">
                  <HStack spacing={4}>
                    <Text fontSize="2xl">{integration.icon}</Text>
                    <Box>
                      <Heading size="md">{integration.name}</Heading>
                      <Text color="gray.600" fontSize="sm">
                        {integration.description}
                      </Text>
                      <HStack spacing={4} mt={2}>
                        <Badge colorScheme={getStatusColor(integration.status)} size="sm">
                          {integration.status}
                        </Badge>
                        <Text fontSize="xs" color="gray.500">
                          Last sync: {integration.lastSync}
                        </Text>
                      </HStack>
                    </Box>
                  </HStack>
                  <Button
                    colorScheme={integration.status === 'Connected' ? 'gray' : 'blue'}
                    variant={integration.status === 'Connected' ? 'outline' : 'solid'}
                    size="sm"
                  >
                    {integration.status === 'Connected' ? 'Manage' : 'Connect'}
                  </Button>
                </Flex>
              </CardBody>
            </Card>
          ))}
        </VStack>

        <Divider />

        <Card>
          <CardHeader>
            <Heading size="md">API Documentation</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Text color="gray.600">
                Use our REST API to integrate with your own applications or build custom integrations.
              </Text>
              <HStack spacing={4}>
                <Button colorScheme="blue" size="sm">
                  View API Docs
                </Button>
                <Button variant="outline" size="sm">
                  Generate API Key
                </Button>
              </HStack>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  );
}