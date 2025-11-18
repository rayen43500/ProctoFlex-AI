import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { Monitor, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { API_BASE, getAuthHeaders } from '@/contexts/AuthContext';

type SessionItem = {
  id: number | string;
  exam_id?: number | string;
  student_id?: number | string;
  status: string;
  start_time?: string;
  risk_level?: string;
};

const Sessions: React.FC = () => {
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(`${API_BASE}/sessions`, { headers: { 'Content-Type': 'application/json', ...getAuthHeaders() } });
      if (!res.ok) throw new Error(`Erreur ${res.status}`);
      const ct = res.headers.get('content-type') || '';
      if (!ct.includes('application/json')) {
        const text = await res.text().catch(() => '');
        console.error('Non-JSON response for /sessions:', text);
        toast.error('Réponse inattendue du serveur pour les sessions (voir console)');
        setSessions([]);
      } else {
        const data = await res.json();
        setSessions(Array.isArray(data) ? data : []);
      }
    } catch (e: any) {
      setError(e.message || 'Erreur de chargement');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <Monitor className="h-4 w-4 text-green-500" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-blue-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'En cours';
      case 'completed':
        return 'Terminé';
      case 'warning':
        return 'Attention';
      default:
        return 'Inconnu';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Sessions de Surveillance</h1>
        <p className="text-gray-600">Suivi en temps réel des sessions d'examen</p>
      </div>

      {loading && <div className="bg-white p-4 rounded shadow">Chargement...</div>}
      {error && <div className="bg-red-50 text-red-700 p-4 rounded shadow">{error}</div>}

      {/* Sessions Table */}
      {!loading && !error && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Sessions</h3>
            <div className="overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Session</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Examen</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Début</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risque</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sessions.map((s) => (
                    <tr key={s.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{s.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{s.exam_id ?? '-'}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {getStatusIcon(s.status)}
                          <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(s.status)}`}>{getStatusText(s.status)}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{s.start_time ? new Date(s.start_time).toLocaleString() : '-'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{s.risk_level ?? '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sessions;
