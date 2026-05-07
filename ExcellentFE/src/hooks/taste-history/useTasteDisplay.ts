export const useTasteDisplay = (tasteData: {
  sweetness?: string
  acidity?: string
  body?: string
  carbonation?: string
  aroma?: string
  bitterness?: string
}) => {
  const tasteInfo = {
    단맛: tasteData.sweetness,
    산미: tasteData.acidity,
    바디감: tasteData.body,
    탄산감: tasteData.carbonation,
    향: tasteData.aroma,
    쓴맛: tasteData.bitterness,
  }

  const tasteInfoArray = Object.entries(tasteInfo)
    .filter(([_, value]) => value)
    .map(([key, value]) => `${key} 적합도 ${value}점`)

  const tasteDisplay = tasteInfoArray.join(', ')

  return {
    tasteDisplay,
    fullTasteDisplay: tasteDisplay,
  }
}
