import React from 'react';
import { Badge, Box, Flex, Heading, Image, Text } from '@chakra-ui/react';
import { Product } from '../../../../services/db';
import {
  useMoneyFormatter,
  useProductVariantExtensions,
} from '../../../../hooks';

export interface ProductCardProps {
  product: Product;
}
export const ProductCard: React.FunctionComponent<ProductCardProps> = ({
  product,
}) => {
  const { getPrice } = useProductVariantExtensions(product.productVariants[0]);
  const price = getPrice();
  const { formatCurrency } = useMoneyFormatter();
  return (
    <Box as="button" display="flex" mb={2}>
      <Box width="66px">
        <Image
          borderRadius="md"
          src="https://images.foody.vn/res/g101/1002166/s120x120/bd77f2d7-36a3-43ef-953f-536f50001570.jpg"
          alt="Banh my"
        />
      </Box>
      <Box textAlign="left" ml={2} flex={1}>
        <Heading size="sm" fontWeight="medium">
          <Badge mr={1}>{product.defaultCode}</Badge>
          {product.name}
        </Heading>

        <Flex alignItems="center" justifyContent="space-between" mt={2}>
          <Heading size="sm">{formatCurrency(price, 'Product Price')}</Heading>
          {product.productVariantIds.length > 1 && (
            <Text fontSize="sm">
              Có {product.productVariantIds.length} biến thể
            </Text>
          )}
        </Flex>
      </Box>
    </Box>
  );
};
