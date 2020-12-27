import {
  Avatar,
  Box,
  Flex,
  Heading,
  Stack,
  Text,
  Image,
  BoxProps,
} from '@chakra-ui/react';
import styled from '@emotion/styled';
import React from 'react';
import {
  IconChevronDown,
  IconSync,
  IconWifiSlash,
} from '../../../../components/icons';

import { IconBell } from '../../../../components/icons/output/IconBell';
import { IconWifi } from '../../../../components/icons/output/IconWifi';
import { usePreference } from '../../../../contexts/PreferenceProvider';

const IconWrapper = styled(Flex)`
  width: 2rem;
  height: 2rem;
  align-items: center;
  justify-content: center;
`;

export interface SessionBarProps extends BoxProps {}

export const SessionBar: React.FunctionComponent<SessionBarProps> = ({
  ...boxProps
}) => {
  const { isOnline } = usePreference();
  return (
    <Flex {...boxProps}>
      <Box width="40px">
        <Image borderRadius="md" src="/logo.svg" />
      </Box>
      <Stack direction="row" spacing={2} alignItems="center" ml="auto">
        <IconWrapper>
          {isOnline ? (
            <IconWifi size="24" color="#48BB78" />
          ) : (
            <IconWifiSlash color="#E53E3E" size="24" />
          )}
        </IconWrapper>
        <IconWrapper>
          <IconBell size="24" />
        </IconWrapper>
        <Stack as="button" direction="row" alignItems="center" spacing={2}>
          <Box textAlign="left">
            <Text fontSize="sm">Thu ngân</Text>
            <Heading size="sm">Hieu Tran</Heading>
          </Box>

          <IconSync size="1.5rem" />
        </Stack>
      </Stack>
    </Flex>
  );
};
