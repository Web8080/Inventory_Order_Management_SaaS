import {
  Box,
  Grid,
  GridItem,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
} from '@chakra-ui/react';

export function DashboardPage() {
  // Mock data for demonstration
  const stats = [
    {
      label: 'Total Products',
      value: '1,234',
      change: '+12%',
      changeType: 'increase' as const,
    },
    {
      label: 'Total Orders',
      value: '456',
      change: '+8%',
      changeType: 'increase' as const,
    },
    {
      label: 'Revenue',
      value: '$12,345',
      change: '+15%',
      changeType: 'increase' as const,
    },
    {
      label: 'Low Stock Items',
      value: '23',
      change: '-5%',
      changeType: 'decrease' as const,
    },
  ];

  const recentOrders = [
    { id: 'ORD-001', customer: 'John Doe', amount: '$125.50', status: 'Completed' },
    { id: 'ORD-002', customer: 'Jane Smith', amount: '$89.99', status: 'Processing' },
    { id: 'ORD-003', customer: 'Bob Johnson', amount: '$234.75', status: 'Pending' },
    { id: 'ORD-004', customer: 'Alice Brown', amount: '$67.25', status: 'Completed' },
  ];

  const lowStockItems = [
    { product: 'iPhone 15 Pro', current: 5, reorder: 10 },
    { product: 'Samsung Galaxy S24', current: 3, reorder: 15 },
    { product: 'MacBook Pro M3', current: 2, reorder: 8 },
    { product: 'Dell XPS 13', current: 4, reorder: 12 },
  ];

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" color="gray.700" mb={2}>
            Dashboard
          </Heading>
          <Text color="gray.600">
            Welcome back! Here's what's happening with your inventory today.
          </Text>
        </Box>

        {/* Stats Grid */}
        <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={6}>
          {stats.map((stat, index) => (
            <GridItem key={index}>
              <Card>
                <CardBody>
                  <Stat>
                    <StatLabel>{stat.label}</StatLabel>
                    <StatNumber>{stat.value}</StatNumber>
                    <StatHelpText>
                      <StatArrow type={stat.changeType} />
                      {stat.change} from last month
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
            </GridItem>
          ))}
        </Grid>

        {/* Content Grid */}
        <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={6}>
          {/* Recent Orders */}
          <GridItem>
            <Card>
              <CardHeader>
                <Heading size="md">Recent Orders</Heading>
              </CardHeader>
              <CardBody>
                <TableContainer>
                  <Table size="sm">
                    <Thead>
                      <Tr>
                        <Th>Order ID</Th>
                        <Th>Customer</Th>
                        <Th>Amount</Th>
                        <Th>Status</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {recentOrders.map((order) => (
                        <Tr key={order.id}>
                          <Td>{order.id}</Td>
                          <Td>{order.customer}</Td>
                          <Td>{order.amount}</Td>
                          <Td>
                            <Badge
                              colorScheme={
                                order.status === 'Completed'
                                  ? 'green'
                                  : order.status === 'Processing'
                                  ? 'blue'
                                  : 'yellow'
                              }
                            >
                              {order.status}
                            </Badge>
                          </Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
              </CardBody>
            </Card>
          </GridItem>

          {/* Low Stock Alerts */}
          <GridItem>
            <Card>
              <CardHeader>
                <Heading size="md">Low Stock Alerts</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={3} align="stretch">
                  {lowStockItems.map((item, index) => (
                    <Box
                      key={index}
                      p={3}
                      bg="red.50"
                      borderRadius="md"
                      borderLeft="4px solid"
                      borderLeftColor="red.400"
                    >
                      <HStack justify="space-between">
                        <VStack align="start" spacing={1}>
                          <Text fontWeight="medium" fontSize="sm">
                            {item.product}
                          </Text>
                          <Text fontSize="xs" color="gray.600">
                            Current: {item.current} | Reorder: {item.reorder}
                          </Text>
                        </VStack>
                        <Badge colorScheme="red" size="sm">
                          Low Stock
                        </Badge>
                      </HStack>
                    </Box>
                  ))}
                </VStack>
              </CardBody>
            </Card>
          </GridItem>
        </Grid>
      </VStack>
    </Box>
  );
}