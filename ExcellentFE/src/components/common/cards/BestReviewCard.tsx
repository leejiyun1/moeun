import maskingUserId from '@/utils/masking'
import StarRating from '@/components/common/StarRating'
import Button from '@/components/common/Button'
import { useState } from 'react'
import Modal from '@/components/common/Modal'
import { Link } from 'react-router-dom'
import SafeImage from '@/components/common/SafeImage'
import type { BestReviewCardProps } from '@/types/cardProps'

const BestReviewCard = ({
  product_name,
  product_id,
  imgSrc,
  imgAlt,
  review,
  userId,
  date,
  defaultRating,
}: BestReviewCardProps) => {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const openModal = () => setIsModalOpen(true)
  const closeModal = () => setIsModalOpen(false)

  return (
    <div className="flex w-full max-w-[1268px] flex-col items-center justify-center gap-8 md:flex-row md:gap-10 xl:min-h-123 xl:gap-19">
      <SafeImage
        src={imgSrc}
        alt={imgAlt || '모은 주류'}
        className="h-[260px] w-full max-w-[420px] object-contain md:h-[360px] md:w-[45%] md:max-w-none xl:h-123 xl:w-[48%] xl:max-w-155"
      />
      <div className="flex w-full max-w-[570px] flex-col md:min-w-0 md:flex-1">
        <div className="mb-[10px] flex flex-col gap-3 md:items-start 2xl:flex-row 2xl:items-center 2xl:justify-between">
          <p className="pb-[4px] text-[26px] font-semibold md:text-[32px] 2xl:text-[40px]">
            {product_name}
          </p>
          <StarRating
            totalStars={5}
            readOnly
            defaultRating={defaultRating}
            size={25}
            showRatingValue={false}
          />
        </div>
        <p className="min-h-[120px] text-base leading-7 text-[#333333] md:text-[20px] md:leading-8 xl:min-h-[165px] xl:text-[22px]">
          {review}
        </p>
        <div className="mt-8 mb-10 flex w-full max-w-[281px] justify-between text-base text-[#666666] md:mt-12 md:text-[20px] xl:mt-15 xl:mb-[50px] xl:text-[22px]">
          <p> {userId ? maskingUserId(userId) : 'Unknown User'}</p>
          <p>{date ? date.slice(0, 10) : ''}</p>
        </div>
        <Button
          onClick={openModal}
          className="h-14 w-full max-w-[570px] text-base md:h-[72px] md:text-2xl"
        >
          이 전통주가 궁금하다면?
        </Button>
        <Modal
          isOpen={isModalOpen}
          onClose={closeModal}
          title="한 잔 취향 이 달의 후기"
          className="review-modal-scroll h-[min(900px,90vh)] w-[min(680px,calc(100vw-32px))] overflow-x-hidden overflow-y-auto"
        >
          <div>
            <SafeImage
              src={imgSrc}
              alt={imgAlt || '모은 주류'}
              className="mt-14 mb-[34px] h-auto max-h-119 w-full max-w-150 rounded-[10px] border border-[#333333] object-contain"
            />
            <p className="pb-[4px] text-[28px] font-semibold md:text-[40px]">
              {product_name}
            </p>
            <StarRating
              totalStars={5}
              readOnly
              defaultRating={defaultRating}
              size={25}
              showRatingValue={false}
              className="my-[23px]"
            />
            <p className="mb-10 text-base leading-7 text-[#333333] md:mb-15 md:text-[22px] md:leading-8">
              {review}
            </p>
            <div className="mb-12 flex w-full max-w-[250px] justify-between text-base text-[#666666] md:mb-[101px] md:text-[22px]">
              <p> {userId ? maskingUserId(userId) : 'Unknown User'}</p>
              <p>{date ? date.slice(0, 10) : ''}</p>
            </div>
            <Link to={`/product/${String(product_id)}`}>
              <Button className="h-14 w-full text-base md:h-[72px] md:text-2xl">
                제품 상세보기
              </Button>
            </Link>
          </div>
        </Modal>
      </div>
    </div>
  )
}

export default BestReviewCard
