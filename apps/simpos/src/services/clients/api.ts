import axios from 'axios';
import get from 'lodash.get';
import camelcaseKeys from 'camelcase-keys';
import { AuthUserMeta } from '../db';

export const simApi = axios.create({
  baseURL: import.meta.env.VITE_ODOO_BASE_URL,
});

simApi.interceptors.response.use(
  async function (response) {
    if (response.data.error) {
      throw new Error(
        get(response, 'data.error.data.message', 'Request error'),
      );
    }

    return camelcaseKeys(get(response, 'data.result', {}), {
      deep: true,
    });
  },
  function (error) {
    const responseData = error.response?.data;
    if (typeof responseData === 'string' && responseData.includes('odoo.http.SessionExpiredException')) {
      throw new Error('Unauthorized error');
    }
    // Add more specific error handling for debugging
    const status = error.response?.status;
    const url = error.config?.url;
    const data = error.response?.data;
    
    console.error('API Error Details:', {
      status,
      url, 
      data: typeof data === 'string' ? data.substring(0, 200) : data
    });
    
    if (status === 404) {
      throw new Error(`404 Not Found: ${url || 'Unknown endpoint'}`);
    }
    
    throw new Error(`${status || 'Unknown'} error: ${error.message}`);
  },
);

export const updateSimApiToken = (meta: AuthUserMeta) => {
  if (!meta.accessToken) {
    console.warn('token is blank or undefined');
  }
  simApi.defaults.headers.common['Authorization'] =
    `Bearer ${meta.accessToken}`;
};
