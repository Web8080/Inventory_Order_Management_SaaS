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
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Select,
  Flex,
} from '@chakra-ui/react';

export function OrdersPage() {
  const orders = [
    {
      id: 'ORD-001',
      customer: 'John Doe',
      type: 'Sale',
      status: 'Completed',
      amount: 125.50,
      date: '2024-01-15',
    },
    {
      id: 'ORD-002',
      customer: 'Jane Smith',
      type: 'Sale',
      status: 'Processing',
      amount: 89.99,
      date: '2024-01-14',
    },
    {
      id: 'ORD-003',
      customer: 'Apple Inc.',
      type: 'Purchase',
      status: 'Pending',
      amount: 234.75,
      date: '2024-01-13',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Completed': return 'green';
      case 'Processing': return 'blue';
      case 'Pending': return 'yellow';
      default: return 'gray';
    }
  };

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        <Flex justify="space-between" align="center">
          <Box>
            <Heading size="lg" color="gray.700" mb={2}>
              Orders
            </Heading>
            <Text color="gray.600">
              Manage sales and purchase orders
            </Text>
          </Box>
          <Button colorScheme="blue">Create Order</Button>
        </Flex>

        <Card>
          <CardHeader>
            <Heading size="md">Order List ({orders.length} orders)</Heading>
          </CardHeader>
          <CardBody>
            <TableContainer>
              <Table size="sm">
                <Thead>
                  <Tr>
                    <Th>Order ID</Th>
                    <Th>Customer/Supplier</Th>
                    <Th>Type</Th>
                    <Th>Status</Th>
                    <Th>Amount</Th>
                    <Th>Date</Th>
                    <Th>Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {orders.map((order) => (
                    <Tr key={order.id}>
                      <Td>
                        <Text fontFamily="mono" fontSize="sm">
                          {order.id}
                        </Text>
                      </Td>
                      <Td>{order.customer}</Td>
                      <Td>
                        <Badge colorScheme={order.type === 'Sale' ? 'green' : 'blue'} size="sm">
                          {order.type}
                        </Badge>
                      </Td>
                      <Td>
                        <Badge colorScheme={getStatusColor(order.status)} size="sm">
                          {order.status}
                        </Badge>
                      </Td>
                      <Td>
                        <Text fontWeight="medium">${order.amount}</Text>
                      </Td>
                      <Td>{order.date}</Td>
                      <Td>
                        <HStack spacing={2}>
                          <Button size="sm" variant="ghost">
                            View
                          </Button>
                          <Button size="sm" variant="ghost">
                            Edit
                          </Button>
                        </HStack>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </TableContainer>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  );
}