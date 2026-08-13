import { useCallback, useEffect, useMemo, useState } from "react";

import { getGuests } from "../services/guestService.js";
import { getApiErrorMessage } from "../guestUtils.js";

export function useGuests({ filters, page, pageSize, search }) {
  const [data, setData] = useState({ count: 0, next: null, previous: null, results: [] });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const params = useMemo(
    () => ({
      page,
      page_size: pageSize,
      search: search || undefined,
      nationality: filters.nationality || undefined,
      id_type: filters.idType || undefined,
      ordering: "-created_at",
    }),
    [filters.idType, filters.nationality, page, pageSize, search],
  );

  const loadGuests = useCallback(async () => {
    setIsLoading(true);
    setError("");

    try {
      const response = await getGuests(params);
      setData(response);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, [params]);

  useEffect(() => {
    loadGuests();
  }, [loadGuests]);

  return {
    guests: data.results,
    count: data.count,
    hasNext: Boolean(data.next),
    hasPrevious: Boolean(data.previous),
    isLoading,
    error,
    retry: loadGuests,
  };
}
