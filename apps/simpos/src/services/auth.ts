import { simApi } from './clients';
import { AuthUserContext, authUserMeta, AuthUserMeta } from './db/authUserMeta';

export interface LoginParams {
  login: string;
  password: string;
}

export interface UnifiedLoginResponse {
  success: boolean;
  user_id: number;
  login: string;
  message: string;
  pos_metadata?: {
    userContext: AuthUserContext;
    config: {
      id: number;
      name: string;
      currency: string;
      current_session_id: number;
      current_session_state: string;
    };
  };
}
export interface PosMetadataParams {
  config_id?: number;
}

export interface SessionInfo {
  userContext: AuthUserContext;
}
export interface ServerMetadata {
  loginNumber: number;
  sessionInfo: SessionInfo;
}

export const authService = {
  login: (params: LoginParams & { config_id?: number }) => {
    return simApi.post('/simpos/v1/sign_in', {
      db_name: import.meta.env.VITE_ODOO_DB,
      login: params.login,
      password: params.password,
      config_id: params.config_id, // Include config_id for unified response
    });
  },
  saveAuthMeta: async (authMeta: AuthUserMeta) => {
    await authUserMeta.create(authMeta);
  },
  getAuthMeta: async () => authUserMeta.first(),
  clearLogin: async () => authUserMeta.clear(),

  refreshMetadata: async (
    params: PosMetadataParams,
  ): Promise<ServerMetadata> => {
    const data: ServerMetadata = await simApi.post('/pos_metadata', {
      params: {
        config_id: params.config_id,
      },
    });

    await authUserMeta.update({
      userContext: data.sessionInfo.userContext,
    });
    return data;
  },

  // Extract metadata from unified login response
  extractMetadataFromLogin: async (loginResponse: UnifiedLoginResponse): Promise<ServerMetadata | null> => {
    if (loginResponse.pos_metadata) {
      const metadata: ServerMetadata = {
        loginNumber: loginResponse.user_id,
        sessionInfo: {
          userContext: loginResponse.pos_metadata.userContext
        }
      };
      
      await authUserMeta.update({
        userContext: loginResponse.pos_metadata.userContext,
      });
      
      return metadata;
    }
    return null;
  },
};
