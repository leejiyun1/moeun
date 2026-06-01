import type {
  BestReviewCardProps,
  CardBaseProps,
  ReviewCardProps,
  TestCardProps,
} from '@/types/cardProps'
import Card from '@/components/common/cards/Card.tsx'

export type CardListItem =
  | CardBaseProps
  | ReviewCardProps
  | TestCardProps
  | BestReviewCardProps

interface CardRendererProps {
  type: 'default' | 'review' | 'test' | 'best'
  card: CardListItem
}

const CardRenderer = ({ type, card }: CardRendererProps) => {
  switch (type) {
    case 'default':
      return <Card type="default" data={card as CardBaseProps} />
    case 'review':
      return <Card type="review" data={card as ReviewCardProps} />
    case 'test':
      return <Card type="test" data={card as TestCardProps} />
    case 'best':
      return <Card type="best" data={card as BestReviewCardProps} />
  }
}

export default CardRenderer
