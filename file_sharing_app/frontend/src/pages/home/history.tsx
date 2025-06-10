import React, { useEffect, useState } from "react";
import { Table, Spinner, Alert, Container } from "react-bootstrap";
import api from "../../api";
import { useInView } from "react-intersection-observer";
import Navbar from "./navbar";

interface HistoryItem {
  file_id: number;
  original_filename: string;
  shared_with: string;
  shared_at: string;
  expires_at: string;
  message: string;
  downloaded: boolean;
}

const History: React.FC = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { ref, inView } = useInView();

  const fetchHistory = async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    try {
      const response = await api.get(`/history?page=${page}&per_page=15`);
      const newItems: HistoryItem[] = response.data.history;
      setHistory(prev => [...prev, ...newItems]);

      // Check if this was the last page
      if (page >= response.data.total_pages) {
        setHasMore(false);
      } else {
        setPage(prev => prev + 1);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to load history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    if (inView && hasMore) {
      fetchHistory();
    }
  }, [inView]);

  return (
  <>
    <Navbar />
    <Container className="py-4">
      <h2 className="fs-4 text-center text-md-start">📜 Share History</h2>

      {history.length === 0 && !loading && (
        <Alert variant="info" className="text-center">
          No shared files found.
        </Alert>
      )}

      <div className="table-responsive">
        <Table striped bordered hover className="mt-3 mb-0">
          <thead className="table-light text-nowrap">
            <tr>
              <th>File Name</th>
              <th>Shared With</th>
              <th>Shared At</th>
              <th>Expires At</th>
              <th>Message</th>
              <th>Downloaded</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item) => (
              <tr key={`${item.file_id}-${item.shared_at}`}>
                <td className="text-break">{item.original_filename}</td>
                <td className="text-break">{item.shared_with}</td>
                <td className="text-nowrap">{new Date(item.shared_at).toLocaleString()}</td>
                <td className="text-nowrap">{new Date(item.expires_at).toLocaleString()}</td>
                <td className="text-break">{item.message || "—"}</td>
                <td className="text-center">{item.downloaded ? "✅" : "⏳"}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>

      <div ref={ref} style={{ height: "30px" }} />
      {loading && (
        <div className="text-center my-3">
          <Spinner animation="border" />
        </div>
      )}
      {error && (
        <Alert variant="danger" className="text-center">
          {error}
        </Alert>
      )}
    </Container>
  </>
);
}

export default History;
