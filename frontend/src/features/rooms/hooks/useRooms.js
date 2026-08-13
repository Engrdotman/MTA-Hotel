import { useCallback, useEffect, useMemo, useState } from "react";

import { getRooms, getRoomSummary, getRoomTypes } from "../services/roomService.js";
import { getApiErrorMessage } from "../roomUtils.js";

const emptyPage = { count: 0, next: null, previous: null, results: [] };

export function useRooms({ filters, page, pageSize, search }) {
  const [rooms, setRooms] = useState(emptyPage);
  const [summary, setSummary] = useState({ total: 0, available: 0, occupied: 0, reserved: 0 });
  const [roomTypes, setRoomTypes] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const params = useMemo(
    () => ({
      page,
      page_size: pageSize,
      search: search || undefined,
      room_type: filters.roomType || undefined,
      status: filters.status || undefined,
      floor: filters.floor || undefined,
      ordering: "room_number",
    }),
    [filters.floor, filters.roomType, filters.status, page, pageSize, search],
  );

  const loadRooms = useCallback(async () => {
    setIsLoading(true);
    setError("");

    try {
      const [roomResponse, summaryResponse, roomTypeResponse] = await Promise.all([
        getRooms(params),
        getRoomSummary(),
        getRoomTypes({ page_size: 100, ordering: "name" }),
      ]);
      setRooms(roomResponse);
      setSummary(summaryResponse);
      setRoomTypes(roomTypeResponse.results || []);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, [params]);

  useEffect(() => {
    loadRooms();
  }, [loadRooms]);

  return {
    rooms: rooms.results,
    count: rooms.count,
    hasNext: Boolean(rooms.next),
    hasPrevious: Boolean(rooms.previous),
    summary,
    roomTypes,
    isLoading,
    error,
    retry: loadRooms,
  };
}
