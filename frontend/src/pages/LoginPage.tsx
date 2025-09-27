import {
  Box,
  Flex,
  FormControl,
  FormLabel,
  Input,
  Button,
  Text,
  VStack,
  Heading,
  useColorModeValue,
} from '@chakra-ui/react';

export function LoginPage() {
  const bg = useColorModeValue('white', 'gray.800');
  
  return (
    <Flex minH="100vh" align="center" justify="center" bg="gray.50">
      <Box
        bg={bg}
        p={8}
        rounded="lg"
        shadow="lg"
        w="full"
        maxW="md"
      >
        <VStack spacing={6}>
          <Box textAlign="center">
            <Heading size="lg" color="brand.500">
              🏭 Inventory SaaS
            </Heading>
            <Text color="gray.600" mt={2}>
              Sign in to your account
            </Text>
          </Box>

          <Box w="full">
            <VStack spacing={4}>
              <FormControl>
                <FormLabel>Email</FormLabel>
                <Input
                  type="email"
                  placeholder="Enter your email"
                  defaultValue="demo@example.com"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Password</FormLabel>
                <Input
                  type="password"
                  placeholder="Enter your password"
                  defaultValue="demo123"
                />
              </FormControl>

              <Button
                colorScheme="brand"
                size="lg"
                w="full"
                onClick={() => window.location.href = '/dashboard'}
              >
                Sign In
              </Button>
            </VStack>
          </Box>

          <Text textAlign="center" fontSize="sm" color="gray.600">
            Demo credentials: demo@example.com / demo123
          </Text>
        </VStack>
      </Box>
    </Flex>
  );
}