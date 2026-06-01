import type { ProductDetail } from '@/types/product'
import { DRINK_INFO_ROWS, PACKAGE_INFO_ROWS } from '@/constants/detailPage'
import SafeImage from '@/components/common/SafeImage'

const DetailInformation = ({ data }: { data: ProductDetail }) => {
  const infoRows =
    data.product_type === 'package'
      ? PACKAGE_INFO_ROWS(data)
      : DRINK_INFO_ROWS(data)

  return (
    <div>
      {/* 탭 메뉴 */}
      <div className="border-b">
        <div className="flex w-full overflow-x-auto">
          <button className="min-w-[140px] flex-1 cursor-pointer border-b-2 border-black px-4 py-3 text-base font-bold text-black md:px-6 md:text-lg">
            상품상세정보
          </button>
          <button className="min-w-[160px] flex-1 cursor-pointer px-4 py-3 text-base text-[#666666] md:px-6 md:text-lg">
            배송/교환/반품 안내
          </button>
          <button className="min-w-[120px] flex-1 px-4 py-3 text-base text-[#666666] md:px-6 md:text-lg">
            상품후기
          </button>
        </div>
      </div>

      {/* 상품 정보 테이블 */}
      <div className="mt-[50px]">
        <table className="w-full border-collapse border-t border-b border-[#d9d9d9]">
          <tbody>
            {infoRows.map((row, idx) => (
              <tr key={idx} className="h-20 border-b border-[#d9d9d9]">
                <td className="w-28 bg-[#f2f2f2] px-3 py-3 text-center text-base font-bold md:w-95 md:px-4 md:text-lg">
                  {row.label}
                </td>
                <td className="px-4 text-base break-keep text-[#666666] md:pl-15 md:text-lg">
                  {row.value}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 상세 이미지 */}
      <div className="mt-[50px]">
        <div className="w-full">
          <SafeImage
            src={data?.description_image_url}
            alt="막걸리 브랜드"
            className="max-h-[1200px] w-full object-contain"
          />
        </div>
      </div>
    </div>
  )
}

export default DetailInformation
