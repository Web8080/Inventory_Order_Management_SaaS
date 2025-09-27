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
  Flex,
  Progress,
} from '@chakra-ui/react';

export function InventoryPage() {
  const stockItems = [
    {
      id: '1',
      product: 'iPhone 15 Pro',
      warehouse: 'Main Warehouse',
      quantity: 25,
      reserved: 5,
      available: 20,
      reorderPoint: 10,
      status: 'In Stock',
    },
    {
      id: '2',
      product: 'Samsung Galaxy S24',
      warehouse: 'Main Warehouse',
      quantity: 15,
      reserved: 2,
      available: 13,
      reorderPoint: 15,
      status: 'In Stock',
    },
    {
      id: '3',
      product: 'MacBook Pro M3',
      warehouse: 'Main Warehouse',
      quantity: 8,
      reserved: 1,
      available: 7,
      reorderPoint: 10,
      status: 'Low Stock',
    },
    {
      id: '4',
      product: 'Dell XPS 13',
      warehouse: 'Main Warehouse',
      quantity: 12,
      reserved: 3,
      available: 9,
      reorderPoint: 15,
      status: 'In Stock',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'In Stock': return 'green';
      case 'Low Stock': return 'yellow';
      case 'Out of Stock': return 'red';
      default: return 'gray';
    }
  };

  const getStockPercentage = (quantity: number, reorderPoint: number) => {
    return Math.min((quantity / (reorderPoint * 2)) * 100, 100);
  };

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        <Flex justify="space-between" align="center">
          <Box>
            <Heading size="lg" color="gray.700" mb={2}>
              Inventory
            </Heading>
            <Text color="gray.600">
              Track stock levels and manage inventory
            </Text>
          </Box>
          <Button colorScheme="blue">Adjust Stock</Button>
        </Flex>

        <Card>
          <CardHeader>
            <Heading size="md">Stock Levels ({stockItems.length} items)</Heading>
          </CardHeader>
          <CardBody>
            <TableContainer>
              <Table size="sm">
                <Thead>
                  <Tr>
                    <Th>Product</Th>
                    <Th>Warehouse</Th>
                    <Th>Quantity</Th>
                    <Th>Reserved</Th>
                    <Th>Available</Th>
                    <Th>Reorder Point</Th>
                    <Th>Stock Level</Th>
                    <Th>Status</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {stockItems.map((item) => (
                    <Tr key={item.id}>
                      <Td>
                        <Text fontWeight="medium">{item.product}</Text>
                      </Td>
                      <Td>{item.warehouse}</Td>
                      <Td>
                        <Text fontWeight="medium">{item.quantity}</Text>
                      </Td>
                      <Td>{item.reserved}</Td>
                      <Td>
                        <Text fontWeight="medium">{item.available}</Text>
                      </Td>
                      <Td>{item.reorderPoint}</Td>
                      <Td>
                        <Box w="100px">
                          <Progress
                            value={getStockPercentage(item.quantity, item.reorderPoint)}
                            colorScheme={
                              item.quantity <= item.reorderPoint ? 'red' : 
                              item.quantity <= item.reorderPoint * 1.5 ? 'yellow' : 'green'
                            }
                            size="sm"
                          />
                        </Box>
                      </Td>
                      <Td>
                        <Badge colorScheme={getStatusColor(item.status)} size="sm">
                          {item.status}
                        </Badge>
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