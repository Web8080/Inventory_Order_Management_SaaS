import {
  Box,
  Flex,
  HStack,
  IconButton,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  Text,
  useColorModeValue,
} from '@chakra-ui/react';
import { ChevronDownIcon, SettingsIcon, HamburgerIcon } from '@chakra-ui/icons';
import { useAuth, useAuthActions } from '../store/authStore';

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const { user } = useAuth();
  const { logout } = useAuthActions();
  const bg = useColorModeValue('white', 'gray.800');

  const handleLogout = () => {
    logout();
  };

  return (
    <Box bg={bg} px={6} py={4} borderBottom="1px" borderColor="gray.200">
      <Flex justify="space-between" align="center">
        <HStack spacing={4}>
          <IconButton
            aria-label="Open menu"
            icon={<HamburgerIcon />}
            variant="ghost"
            onClick={onMenuClick}
            display={{ base: 'flex', lg: 'none' }}
          />
          <Text fontSize="xl" fontWeight="bold" color="brand.500">
            Inventory SaaS
          </Text>
        </HStack>

        <HStack spacing={4}>
          <Text fontSize="sm" color="gray.600">
            {user?.tenant_name}
          </Text>
          
          <Menu>
            <MenuButton
              as={IconButton}
              aria-label="User menu"
              icon={<Avatar size="sm" name={user?.full_name} />}
              variant="ghost"
            />
            <MenuList>
              <MenuItem icon={<SettingsIcon />}>
                Profile Settings
              </MenuItem>
              <MenuDivider />
              <MenuItem onClick={handleLogout}>
                Logout
              </MenuItem>
            </MenuList>
          </Menu>
        </HStack>
      </Flex>
    </Box>
  );
}
