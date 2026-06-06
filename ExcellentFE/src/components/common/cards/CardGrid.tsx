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
  const mobileItemClass =
    type === 'test'
      ? 'flex w-[148px] shrink-0 justify-center sm:w-[154px]'
      : 'flex w-[220px] shrink-0 justify-center sm:w-[240px]'
  const desktopItemClass =
    type === 'test' ? 'w-full max-w-[154px]' : 'w-full max-w-[300px]'
  const mobileScrollerClass =
    type === 'test'
      ? 'scrollbar-hide relative overflow-x-auto md:hidden'
      : 'scrollbar-hide relative overflow-x-auto px-10 md:hidden'
  const mobileTrackClass =
    type === 'test' ? 'flex min-w-max gap-4 sm:gap-5' : 'flex gap-5'

  return (
    <div className="relative mx-auto w-full max-w-[1281px]">
      <div className={mobileScrollerClass}>
        <div className={mobileTrackClass}>
          {cards.map((card, index) => (
            <div key={index} className={mobileItemClass}>
              <CardRenderer type={type} card={card} />
            </div>
          ))}
        </div>
      </div>

      <div
        className={`hidden w-full max-w-[1281px] ${colClass} justify-items-center gap-6 md:grid`}
      >
        {cards.map((card, index) => (
          <div key={index} className={desktopItemClass}>
            <CardRenderer type={type} card={card} />
          </div>
        ))}
      </div>
    </div>
  )
}

export default CardGrid
