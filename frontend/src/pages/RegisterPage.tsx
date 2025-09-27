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

export function RegisterPage() {
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
              Create your account
            </Text>
          </Box>

          <Box w="full">
            <VStack spacing={4}>
              <FormControl>
                <FormLabel>Company Name</FormLabel>
                <Input placeholder="Enter your company name" />
              </FormControl>

              <FormControl>
                <FormLabel>Email</FormLabel>
                <Input type="email" placeholder="Enter your email" />
              </FormControl>

              <FormControl>
                <FormLabel>Password</FormLabel>
                <Input type="password" placeholder="Create a password" />
              </FormControl>

              <Button
                colorScheme="brand"
                size="lg"
                w="full"
              >
                Create Account
              </Button>
            </VStack>
          </Box>

          <Text textAlign="center">
            Already have an account?{' '}
            <Text as="span" color="brand.500" cursor="pointer">
              Sign in
            </Text>
          </Text>
        </VStack>
      </Box>
    </Flex>
  );
}