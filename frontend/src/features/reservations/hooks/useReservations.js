import { useCallback, useEffect, useMemo, useState } from "react";

import { getGuests } from "../../guests/services/guestService.js";
import { getRooms } from "../../rooms/services/roomService.js";
import { getApiErrorMessage } from "../reservationUtils.js";
import { getReservationSummary, getReservations } from "../services/reservationService.js";

const emptyPage = { count: 0, next: null, previous: null, results: [] };

export function useReservations({ filters, page, pageSize, search }) {
  const [reservations, setReservations] = useState(emptyPage);
  const [summary, setSummary] = useState({ total: 0, pending: 0, confirmed: 0, checked_in: 0, cancelled: 0 });
  const [guests, setGuests] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const params = useMemo(
    () => ({
      page,
      page_size: pageSize,
      search: search || undefined,
      status: filters.status || undefined,
      room: filters.room || undefined,
      guest: filters.guest || undefined,
      date_from: filters.dateFrom || undefined,
      date_to: filters.dateTo || undefined,
      ordering: "-check_in_date",
    }),
    [filters.dateFrom, filters.dateTo, filters.guest, filters.room, filters.status, page, pageSize, search],
  );

  const loadReservations = useCallback(async () => {
    setIsLoading(true);
    setError("");

    try {
      const [reservationResponse, summaryResponse, guestResponse, roomResponse] = await Promise.all([
        getReservations(params),
        getReservationSummary(),
        getGuests({ page_size: 100, ordering: "last_name" }).catch(() => ({ results: [] })),
        getRooms({ page_size: 100, ordering: "room_number" }).catch(() => ({ results: [] })),
      ]);
      setReservations(reservationResponse);
      setSummary(summaryResponse);
      setGuests(guestResponse.results || []);
      setRooms(roomResponse.results || []);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, [params]);

  useEffect(() => {
    loadReservations();
  }, [loadReservations]);

  return {
    reservations: reservations.results,
    count: reservations.count,
    hasNext: Boolean(reservations.next),
    hasPrevious: Boolean(reservations.previous),
    summary,
    guests,
    rooms,
    isLoading,
    error,
    retry: loadReservations,
  };
}
