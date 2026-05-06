/** DRF page responses: { count, results } vs plain arrays */
export function normalizePaginated(data) {
  if (Array.isArray(data)) {
    return { items: data, total: data.length }
  }
  if (data && Array.isArray(data.results)) {
    const total = typeof data.count === 'number' ? data.count : data.results.length
    return { items: data.results, total }
  }
  return { items: [], total: 0 }
}
