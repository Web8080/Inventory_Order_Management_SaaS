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
  FormControl,
  FormLabel,
  Input,
  Select,
  Switch,
  Divider,
  Avatar,
  Badge,
} from '@chakra-ui/react';

export function SettingsPage() {
  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        <Box>
          <Heading size="lg" color="gray.700" mb={2}>
            Settings
          </Heading>
          <Text color="gray.600">
            Manage your account and application preferences
          </Text>
        </Box>

        {/* Profile Settings */}
        <Card>
          <CardHeader>
            <Heading size="md">Profile Settings</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <HStack spacing={4}>
                <Avatar size="lg" name="Demo User" />
                <VStack align="start" spacing={1}>
                  <Text fontWeight="medium">Demo User</Text>
                  <Text fontSize="sm" color="gray.600">demo@example.com</Text>
                  <Badge colorScheme="blue" size="sm">Owner</Badge>
                </VStack>
              </HStack>
              <HStack spacing={4}>
                <FormControl>
                  <FormLabel>First Name</FormLabel>
                  <Input defaultValue="Demo" />
                </FormControl>
                <FormControl>
                  <FormLabel>Last Name</FormLabel>
                  <Input defaultValue="User" />
                </FormControl>
              </HStack>
              <FormControl>
                <FormLabel>Email</FormLabel>
                <Input defaultValue="demo@example.com" />
              </FormControl>
              <FormControl>
                <FormLabel>Phone</FormLabel>
                <Input placeholder="Enter phone number" />
              </FormControl>
              <Button colorScheme="blue" maxW="200px">
                Update Profile
              </Button>
            </VStack>
          </CardBody>
        </Card>

        {/* Company Settings */}
        <Card>
          <CardHeader>
            <Heading size="md">Company Settings</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel>Company Name</FormLabel>
                <Input defaultValue="Demo Company" />
              </FormControl>
              <FormControl>
                <FormLabel>Timezone</FormLabel>
                <Select defaultValue="America/New_York">
                  <option value="America/New_York">Eastern Time (ET)</option>
                  <option value="America/Chicago">Central Time (CT)</option>
                  <option value="America/Denver">Mountain Time (MT)</option>
                  <option value="America/Los_Angeles">Pacific Time (PT)</option>
                </Select>
              </FormControl>
              <FormControl>
                <FormLabel>Currency</FormLabel>
                <Select defaultValue="USD">
                  <option value="USD">USD - US Dollar</option>
                  <option value="EUR">EUR - Euro</option>
                  <option value="GBP">GBP - British Pound</option>
                  <option value="CAD">CAD - Canadian Dollar</option>
                </Select>
              </FormControl>
              <Button colorScheme="blue" maxW="200px">
                Update Company
              </Button>
            </VStack>
          </CardBody>
        </Card>

        {/* Notification Settings */}
        <Card>
          <CardHeader>
            <Heading size="md">Notification Settings</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between">
                <Box>
                  <Text fontWeight="medium">Low Stock Alerts</Text>
                  <Text fontSize="sm" color="gray.600">
                    Get notified when inventory levels are low
                  </Text>
                </Box>
                <Switch defaultChecked />
              </HStack>
              <HStack justify="space-between">
                <Box>
                  <Text fontWeight="medium">Order Notifications</Text>
                  <Text fontSize="sm" color="gray.600">
                    Get notified about new orders
                  </Text>
                </Box>
                <Switch defaultChecked />
              </HStack>
              <HStack justify="space-between">
                <Box>
                  <Text fontWeight="medium">Email Reports</Text>
                  <Text fontSize="sm" color="gray.600">
                    Receive weekly inventory reports
                  </Text>
                </Box>
                <Switch />
              </HStack>
            </VStack>
          </CardBody>
        </Card>

        {/* Security Settings */}
        <Card>
          <CardHeader>
            <Heading size="md">Security</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Button colorScheme="blue" variant="outline" maxW="200px">
                Change Password
              </Button>
              <Button colorScheme="red" variant="outline" maxW="200px">
                Delete Account
              </Button>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  );
}