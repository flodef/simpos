import { useContext } from 'react';
import { DataContext, GlobalDataDispatchContext, GlobalDataDispatch } from './DataProvider';

export function useData() {
  return useContext(DataContext)!;
}

export function useGlobalDataDispatch(): GlobalDataDispatch {
  const context = useContext(GlobalDataDispatchContext);
  if (!context) {
    throw new Error('useGlobalDataDispatch must be inside a DataProvider');
  }
  return context;
}
