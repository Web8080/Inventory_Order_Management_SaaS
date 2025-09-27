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
  Input,
  InputGroup,
  InputLeftElement,
  Select,
  Flex,
  IconButton,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
} from '@chakra-ui/react';
import { useState } from 'react';

export function ProductsPage() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Mock data
  const products = [
    {
      id: '1',
      sku: 'IPH15-128-BLK',
      name: 'iPhone 15 Pro',
      category: 'Electronics',
      price: 999.99,
      stock: 25,
      status: 'In Stock',
      supplier: 'Apple Inc.',
    },
    {
      id: '2',
      sku: 'SGS24-256-BLU',
      name: 'Samsung Galaxy S24',
      category: 'Electronics',
      price: 799.99,
      stock: 15,
      status: 'In Stock',
      supplier: 'Samsung Electronics',
    },
    {
      id: '3',
      sku: 'MBP-M3-512-SLV',
      name: 'MacBook Pro M3',
      category: 'Electronics',
      price: 1999.99,
      stock: 8,
      status: 'Low Stock',
      supplier: 'Apple Inc.',
    },
    {
      id: '4',
      sku: 'DXP13-512-BLK',
      name: 'Dell XPS 13',
      category: 'Electronics',
      price: 1299.99,
      stock: 12,
      status: 'In Stock',
      supplier: 'Dell Technologies',
    },
    {
      id: '5',
      sku: 'TSH-BLK-M',
      name: 'Basic T-Shirt',
      category: 'Clothing',
      price: 19.99,
      stock: 150,
      status: 'In Stock',
      supplier: 'Fashion Forward Ltd.',
    },
  ];

  const categories = ['all', 'Electronics', 'Clothing', 'Home & Garden', 'Sports & Outdoors'];

  const filteredProducts = products.filter((product) => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.sku.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'In Stock': return 'green';
      case 'Low Stock': return 'yellow';
      case 'Out of Stock': return 'red';
      default: return 'gray';
    }
  };

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Flex justify="space-between" align="center">
          <Box>
            <Heading size="lg" color="gray.700" mb={2}>
              Products
            </Heading>
            <Text color="gray.600">
              Manage your product catalog and inventory
            </Text>
          </Box>
          <Button colorScheme="blue" onClick={onOpen}>
            Add Product
          </Button>
        </Flex>

        {/* Filters */}
        <Card>
          <CardBody>
            <HStack spacing={4}>
              <InputGroup maxW="300px">
                <InputLeftElement>
                  <Text>🔍</Text>
                </InputLeftElement>
                <Input
                  placeholder="Search products..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </InputGroup>
              <Select
                maxW="200px"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category === 'all' ? 'All Categories' : category}
                  </option>
                ))}
              </Select>
            </HStack>
          </CardBody>
        </Card>

        {/* Products Table */}
        <Card>
          <CardHeader>
            <Heading size="md">Product List ({filteredProducts.length} products)</Heading>
          </CardHeader>
          <CardBody>
            <TableContainer>
              <Table size="sm">
                <Thead>
                  <Tr>
                    <Th>SKU</Th>
                    <Th>Name</Th>
                    <Th>Category</Th>
                    <Th>Price</Th>
                    <Th>Stock</Th>
                    <Th>Status</Th>
                    <Th>Supplier</Th>
                    <Th>Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {filteredProducts.map((product) => (
                    <Tr key={product.id}>
                      <Td>
                        <Text fontFamily="mono" fontSize="sm">
                          {product.sku}
                        </Text>
                      </Td>
                      <Td>
                        <Text fontWeight="medium">{product.name}</Text>
                      </Td>
                      <Td>
                        <Badge colorScheme="blue" size="sm">
                          {product.category}
                        </Badge>
                      </Td>
                      <Td>
                        <Text fontWeight="medium">${product.price}</Text>
                      </Td>
                      <Td>
                        <Text>{product.stock}</Text>
                      </Td>
                      <Td>
                        <Badge colorScheme={getStatusColor(product.status)} size="sm">
                          {product.status}
                        </Badge>
                      </Td>
                      <Td>
                        <Text fontSize="sm">{product.supplier}</Text>
                      </Td>
                      <Td>
                        <HStack spacing={2}>
                          <IconButton
                            aria-label="Edit product"
                            size="sm"
                            variant="ghost"
                            icon={<Text>✏️</Text>}
                          />
                          <IconButton
                            aria-label="Delete product"
                            size="sm"
                            variant="ghost"
                            icon={<Text>🗑️</Text>}
                          />
                        </HStack>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </TableContainer>
          </CardBody>
        </Card>

        {/* Add Product Modal */}
        <Modal isOpen={isOpen} onClose={onClose} size="lg">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Add New Product</ModalHeader>
            <ModalCloseButton />
            <ModalBody pb={6}>
              <VStack spacing={4}>
                <FormControl>
                  <FormLabel>Product Name</FormLabel>
                  <Input placeholder="Enter product name" />
                </FormControl>
                <FormControl>
                  <FormLabel>SKU</FormLabel>
                  <Input placeholder="Enter SKU" />
                </FormControl>
                <FormControl>
                  <FormLabel>Category</FormLabel>
                  <Select placeholder="Select category">
                    <option value="Electronics">Electronics</option>
                    <option value="Clothing">Clothing</option>
                    <option value="Home & Garden">Home & Garden</option>
                    <option value="Sports & Outdoors">Sports & Outdoors</option>
                  </Select>
                </FormControl>
                <FormControl>
                  <FormLabel>Price</FormLabel>
                  <NumberInput>
                    <NumberInputField placeholder="0.00" />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
                <FormControl>
                  <FormLabel>Initial Stock</FormLabel>
                  <NumberInput>
                    <NumberInputField placeholder="0" />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
                <HStack spacing={4} w="full">
                  <Button colorScheme="blue" flex={1}>
                    Add Product
                  </Button>
                  <Button variant="ghost" onClick={onClose} flex={1}>
                    Cancel
                  </Button>
                </HStack>
              </VStack>
            </ModalBody>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
}