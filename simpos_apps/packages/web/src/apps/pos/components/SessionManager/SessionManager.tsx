import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  Button,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

import React, { useCallback, useEffect, useState } from 'react';
import { getLoadModelsMap } from '../../../../contexts/DataProvider/dataLoader';
import { PosConfig, PosSession } from '../../../../services/db';
import { AuthUserMeta } from '../../../../services/db/root';
import { posConfigService } from '../../../../services/pos-config';
import { SessionConfig } from './SessionConfig';

const loadModelsMap = getLoadModelsMap();
export interface SessionManagerProps {
  authUserMeta: AuthUserMeta;
  onSessionSelected: (session: PosSession) => void;
}
export const SessionManager: React.FunctionComponent<SessionManagerProps> = ({
  authUserMeta,
  onSessionSelected,
}) => {
  const [configs, setConfigs] = useState<PosConfig[]>([]);
  const updateSession = useCallback(
    (posSessions: PosSession[]) => {
      const assignedSession = posSessions.find(
        (session) => session.responsibleUserId === authUserMeta.uid,
      );

      if (assignedSession) {
        onSessionSelected(assignedSession);
      }
    },
    [authUserMeta, onSessionSelected],
  );

  useEffect(() => {
    const fetchSession = async () => {
      const posConfigs = await loadModelsMap['pos.config'].load();
      const posSessions = await loadModelsMap['pos.session'].load();
      setConfigs(posConfigs);
      updateSession(posSessions);
    };
    fetchSession();
  }, [authUserMeta, onSessionSelected, updateSession]);

  const openSession = async (configId: number) => {
    await posConfigService.createSession(configId);

    const posSessions = await loadModelsMap['pos.session'].load();
    updateSession(posSessions);
  };

  if (configs.length === 0) {
    return null;
  }

  return (
    <Modal isOpen={true} onClose={() => {}}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Chọn phiên bán hàng</ModalHeader>
        <ModalBody>
          {configs.map((config) => (
            <SessionConfig
              key={config.id}
              config={config}
              openSession={openSession}
            />
          ))}

          <Button
            my={2}
            as={RouterLink}
            to="/purchase"
            variant="link"
            colorScheme="blue"
          >
            Mua hàng
          </Button>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};
