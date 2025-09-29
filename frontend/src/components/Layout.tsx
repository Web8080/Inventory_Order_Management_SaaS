import { ReactNode } from 'react';
import {
  Box,
  Flex,
  VStack,
  HStack,
  Text,
  IconButton,
  useDisclosure,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useBreakpointValue,
} from '@chakra-ui/react';
import { HamburgerIcon } from '@chakra-ui/icons';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const isMobile = useBreakpointValue({ base: true, lg: false });

  return (
    <Flex h="100vh">
      {/* Desktop Sidebar */}
      {!isMobile && (
        <Box w="250px" bg="white" borderRight="1px" borderColor="gray.200">
          <Sidebar />
        </Box>
      )}

      {/* Mobile Drawer */}
      <Drawer isOpen={isOpen} onClose={onClose} placement="left">
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader>Menu</DrawerHeader>
          <DrawerBody p={0}>
            <Sidebar onClose={onClose} />
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Main Content */}
      <VStack flex={1} spacing={0}>
        {/* Header */}
        <Header onMenuClick={onOpen} />

        {/* Page Content */}
        <Box flex={1} w="full" p={6} overflow="auto">
          {children}
        </Box>
      </VStack>
    </Flex>
  );
}

