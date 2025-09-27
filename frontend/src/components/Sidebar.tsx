import {
  VStack,
  Box,
  Text,
  Link as ChakraLink,
  Icon,
  useColorModeValue,
} from '@chakra-ui/react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  FiHome,
  FiPackage,
  FiShoppingCart,
  FiTrendingUp,
  FiSettings,
  FiZap,
} from 'react-icons/fi';

interface SidebarProps {
  onClose?: () => void;
}

const menuItems = [
  { label: 'Dashboard', icon: FiHome, path: '/dashboard' },
  { label: 'Products', icon: FiPackage, path: '/products' },
  { label: 'Orders', icon: FiShoppingCart, path: '/orders' },
  { label: 'Inventory', icon: FiTrendingUp, path: '/inventory' },
  { label: 'Integrations', icon: FiZap, path: '/integrations' },
  { label: 'Settings', icon: FiSettings, path: '/settings' },
];

export function Sidebar({ onClose }: SidebarProps) {
  const location = useLocation();
  const bg = useColorModeValue('white', 'gray.800');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');
  const activeBg = useColorModeValue('brand.50', 'brand.900');
  const activeColor = useColorModeValue('brand.500', 'brand.300');

  return (
    <VStack spacing={0} align="stretch" h="full" bg={bg}>
      <Box p={6}>
        <Text fontSize="lg" fontWeight="bold" color="brand.500">
          Inventory SaaS
        </Text>
      </Box>

      <VStack spacing={1} align="stretch" flex={1} px={4}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          
          return (
            <ChakraLink
              key={item.path}
              as={RouterLink}
              to={item.path}
              onClick={onClose}
              display="flex"
              alignItems="center"
              px={4}
              py={3}
              borderRadius="md"
              bg={isActive ? activeBg : 'transparent'}
              color={isActive ? activeColor : 'gray.700'}
              _hover={{
                bg: isActive ? activeBg : hoverBg,
                textDecoration: 'none',
              }}
              transition="all 0.2s"
            >
              <Icon as={item.icon} mr={3} boxSize={5} />
              <Text fontWeight={isActive ? 'semibold' : 'normal'}>
                {item.label}
              </Text>
            </ChakraLink>
          );
        })}
      </VStack>
    </VStack>
  );
}
