import CardRenderer, {
  type CardListItem,
} from '@/components/common/cards/CardRenderer'

interface CardGridProps {
  type: 'default' | 'review' | 'test' | 'best'
  cards: CardListItem[]
  columns: 3 | 4
}

const CardGrid = ({ type, cards, columns }: CardGridProps) => {
  const colClass =
    columns === 3
      ? 'md:grid-cols-2 lg:grid-cols-3'
      : 'md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'

  return (
    <div className="relative mx-auto w-full max-w-[1281px]">
      <div className="scrollbar-hide relative overflow-x-auto px-10 md:hidden">
        <div className="flex gap-5">
          {cards.map((card, index) => (
            <div
              key={index}
              className="flex w-[220px] shrink-0 justify-center sm:w-[240px]"
            >
              <CardRenderer type={type} card={card} />
            </div>
          ))}
        </div>
      </div>

      <div
        className={`hidden w-full max-w-[1281px] ${colClass} justify-items-center gap-6 md:grid`}
      >
        {cards.map((card, index) => (
          <div key={index}>
            <CardRenderer type={type} card={card} />
          </div>
        ))}
      </div>
    </div>
  )
}

export default CardGrid
