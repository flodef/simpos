import React, { useContext, useEffect, useReducer } from 'react';
import {
  AccountTax,
  OrderLine,
  orderLineRepository,
  partnerRepository,
  ProductVariant,
} from '../../services/db';
import { Order, orderRepository } from '../../services/db/order';
import { useData, useGlobalDataDispatch } from '../DataProvider';

export interface ActiveOrder {
  order: Order;
  orderLines: OrderLine[];
}
export interface OrderManagerState {
  activeOrderId: string;
  orders: Order[];
  activeOrder?: ActiveOrder;
}

export type OrderManagerDispatchAction =
  | {
      type: 'INITIAL_LOAD';
      payload: Pick<OrderManagerState, 'activeOrderId' | 'orders'>;
    }
  | {
      type: 'NEW_ORDER';
      payload: Order;
    }
  | {
      type: 'SELECT_ORDER';
      payload: Order;
    }
  | {
      type: 'DELETE_ORDER';
      payload: Order;
    }
  | {
      type: 'ACTIVE_ORDER_LOADED';
      payload: ActiveOrder;
    }
  | {
      type: 'UPDATE_ACTIVE_ORDER';
      payload: Partial<Order>;
    }
  | {
      type: 'ADD_ORDER_LINE_TO_ACTIVE_ORDER';
      payload: OrderLine;
    };

export type OrderManagerDispatch = (action: OrderManagerDispatchAction) => void;
export interface OrderManagerAction {
  addNewOrder: () => Promise<Order>;
  selectOrder: (order: Order) => Promise<Order>;
  deleteOrder: (order: Order) => Promise<Order>;
  selectCustomer: (partnerId?: number) => Promise<number | undefined>;
  selectTableNo: (no?: string) => Promise<string | undefined>;
  selectVibrationCardNo: (no?: string) => Promise<string | undefined>;
  addProductVariantToCart: (
    variant: ProductVariant,
  ) => Promise<OrderLine | undefined>;
}

const initialState: OrderManagerState = {
  orders: [],
  activeOrderId: '',
  activeOrder: undefined,
};

const OrderManagerStateContext = React.createContext<OrderManagerState>(
  initialState,
);

const OrderManagerDispatchContext = React.createContext<
  OrderManagerDispatch | undefined
>(undefined);

const OrderManagerActionContext = React.createContext<
  OrderManagerAction | undefined
>(undefined);

export function orderManagerReducer(
  state: OrderManagerState,
  action: OrderManagerDispatchAction,
): OrderManagerState {
  switch (action.type) {
    case 'INITIAL_LOAD':
      return {
        ...state,
        ...action.payload,
      };
    case 'NEW_ORDER':
      return {
        ...state,
        orders: [...state.orders, action.payload],
        activeOrderId: action.payload.id,
      };
    case 'SELECT_ORDER':
      return {
        ...state,
        activeOrderId: action.payload.id,
      };
    case 'DELETE_ORDER':
      const updatedOrders = state.orders.filter(
        (order) => order.id !== action.payload.id,
      );
      let activeOrderId = state.activeOrderId;
      if (
        state.activeOrderId === action.payload.id &&
        updatedOrders.length > 0
      ) {
        activeOrderId = updatedOrders[0].id;
      }
      return {
        ...state,
        orders: updatedOrders,
        activeOrderId,
      };
    case 'ACTIVE_ORDER_LOADED':
      return {
        ...state,
        activeOrder: action.payload,
      };
    case 'UPDATE_ACTIVE_ORDER':
      return {
        ...state,
        activeOrder: {
          ...state.activeOrder!,
          order: {
            ...state.activeOrder!.order,
            ...action.payload,
          },
        },
      };
    case 'ADD_ORDER_LINE_TO_ACTIVE_ORDER':
      return {
        ...state,
        activeOrder: {
          ...state.activeOrder!,
          orderLines: [...state.activeOrder!.orderLines, action.payload],
        },
      };
    default:
      return state;
  }
}

export const OrderManager: React.FunctionComponent = ({ children }) => {
  const [state, dispatch] = useReducer(orderManagerReducer, initialState);
  const globalDataDispatch = useGlobalDataDispatch();
  const data = useData();
  // TODO: Here we only use the default pricelist
  const addNewOrder = async (): Promise<Order> => {
    const newOrder = await orderRepository.addNewOrder({
      posSession: data.posSession,
      defaultPriceList: data.defaultPriceList,
    });
    dispatch({ type: 'NEW_ORDER', payload: newOrder });
    globalDataDispatch({
      type: 'UPDATE_DATA',
      payload: {
        posSession: {
          ...data.posSession,
          sequenceNumber: newOrder.sequenceNumber,
        },
      },
    });
    return newOrder;
  };

  const selectOrder = async (order: Order): Promise<Order> => {
    dispatch({ type: 'SELECT_ORDER', payload: order });
    return order;
  };

  const deleteOrder = async (order: Order): Promise<Order> => {
    await orderRepository.delete(order.id);
    const deletingLastOrder = state.orders.length === 1;
    dispatch({ type: 'DELETE_ORDER', payload: order });
    if (deletingLastOrder) {
      await addNewOrder();
    }
    return order;
  };

  const selectCustomer = async (
    partnerId?: number,
  ): Promise<number | undefined> => {
    await orderRepository.update(state.activeOrderId, {
      partnerId,
    });

    let partner;
    if (partnerId) {
      partner = await partnerRepository.findById(partnerId);
    }

    dispatch({ type: 'UPDATE_ACTIVE_ORDER', payload: { partnerId, partner } });
    return partnerId;
  };

  const selectTableNo = async (no?: string): Promise<string | undefined> => {
    await orderRepository.update(state.activeOrderId, {
      tableNo: no,
    });
    dispatch({ type: 'UPDATE_ACTIVE_ORDER', payload: { tableNo: no } });
    return no;
  };

  const selectVibrationCardNo = async (
    no?: string,
  ): Promise<string | undefined> => {
    await orderRepository.update(state.activeOrderId, {
      vibrationCardNo: no,
    });
    dispatch({ type: 'UPDATE_ACTIVE_ORDER', payload: { vibrationCardNo: no } });
    return no;
  };

  const getApplicableTaxes = (variant: ProductVariant): AccountTax[] => {
    const taxesSet: Record<number, boolean> = variant.taxesId.reduce(
      (prev, current) => {
        return {
          ...prev,
          [current]: true,
        };
      },
      {},
    );

    return data.taxes.filter((tax) => taxesSet[tax.id]);
  };

  const addProductVariantToCart = async (
    variant: ProductVariant,
  ): Promise<OrderLine | undefined> => {
    const orderLineId = await orderLineRepository.create({
      orderId: state.activeOrderId,
      // TODO: Use getPrice function and check about fiscalPosition
      priceUnit: variant.lstPrice,
      productId: variant.id,
      discount: 0,
      qty: 1,
      note: '',
      applicableTaxIds: getApplicableTaxes(variant).map(({ id }) => id),
    });
    // TODO: Merge order feature
    const orderLine = await orderLineRepository.findById(orderLineId as number);
    dispatch({ type: 'ADD_ORDER_LINE_TO_ACTIVE_ORDER', payload: orderLine! });
    return orderLine;
  };

  const initilizeOrderManager = async () => {
    const currentOrders = await orderRepository.all();
    if (currentOrders.length > 0) {
      dispatch({
        type: 'INITIAL_LOAD',
        payload: {
          activeOrderId: currentOrders[0].id,
          orders: currentOrders,
        },
      });
    } else {
      await addNewOrder();
    }
  };
  useEffect(() => {
    initilizeOrderManager();
  }, []);

  const fetchOrder = async (orderId: string) => {
    if (orderId) {
      const [order, orderLines] = await Promise.all([
        orderRepository.findById(orderId),
        orderLineRepository.getOrderLines(orderId),
      ]);
      if (!order) {
        throw new Error('Not found order');
      }
      dispatch({
        type: 'ACTIVE_ORDER_LOADED',
        payload: {
          order,
          orderLines,
        },
      });
    }
  };
  useEffect(() => {
    fetchOrder(state.activeOrderId);
  }, [state.activeOrderId]);

  return (
    <OrderManagerStateContext.Provider value={state}>
      <OrderManagerActionContext.Provider
        value={{
          addNewOrder,
          selectOrder,
          deleteOrder,
          selectCustomer,
          selectTableNo,
          selectVibrationCardNo,
          addProductVariantToCart,
        }}
      >
        {children}
      </OrderManagerActionContext.Provider>
    </OrderManagerStateContext.Provider>
  );
};

export function useOrderManagerState(): OrderManagerState {
  const context = useContext(OrderManagerStateContext);
  if (!context) {
    throw new Error('useOrderManagerState must be inside a OrderManager');
  }
  return context;
}

export function useOrderManagerDispatch(): OrderManagerDispatch {
  const context = useContext(OrderManagerDispatchContext);
  if (!context) {
    throw new Error('useOrderManagerDispatch must be inside a OrderManager');
  }
  return context;
}

export function useOrderManagerAction(): OrderManagerAction {
  const context = useContext(OrderManagerActionContext);
  if (!context) {
    throw new Error('useOrderManagerAction must be inside a OrderManager');
  }
  return context;
}
