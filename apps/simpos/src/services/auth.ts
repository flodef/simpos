import { simApi } from './clients';
import { AuthUserContext, authUserMeta, AuthUserMeta } from './db/authUserMeta';

export interface LoginParams {
  login: string;
  password: string;
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
  login: (params: LoginParams) => {
    return simApi.post('/simpos/v1/sign_in', {
      db: import.meta.env.VITE_ODOO_DB,
      login: params.login,
      password: params.password,
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
};
