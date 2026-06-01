import CardCarousel from '@/components/common/cards/CardCarousel'
import CardGrid from '@/components/common/cards/CardGrid'
import type {
  BestReviewCardProps,
  CardBaseProps,
  ReviewCardProps,
  TestCardProps,
} from '@/types/cardProps'

type CardListOptions = {
  columns?: 3 | 4
  carousel?: boolean
  slidesToShow?: number
  gap?: string
  responsive?: {
    mobile?: number
    tablet?: number
    desktop?: number
  }
}

type CardListProps =
  | ({ type: 'default'; cards: CardBaseProps[] } & CardListOptions)
  | ({ type: 'review'; cards: ReviewCardProps[] } & CardListOptions)
  | ({ type: 'test'; cards: TestCardProps[] } & CardListOptions)
  | ({ type: 'best'; cards: BestReviewCardProps[] } & CardListOptions)

const CardList = (props: CardListProps) => {
  const columns = props.columns ?? 4

  if (props.carousel) {
    return (
      <CardCarousel
        type={props.type}
        cards={props.cards}
        slidesToShow={props.slidesToShow ?? columns}
        gap={props.gap ?? '27px'}
        responsive={props.responsive}
      />
    )
  }

  return <CardGrid type={props.type} cards={props.cards} columns={columns} />
}

export default CardList
