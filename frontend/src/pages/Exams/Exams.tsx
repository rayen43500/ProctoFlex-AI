import React, { useEffect, useState } from 'react';
import { Plus, Edit, Trash2, Eye } from 'lucide-react';
import { API_BASE, getAuthHeaders } from '@/contexts/AuthContext';

type Exam = {
  id: string;
  title: string;
  description: string;
  duration_minutes: number;
  status: string;
  instructions?: string;
  created_at?: string;
};

const Exams: React.FC = () => {
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(`${API_BASE}/exams`, { headers: { 'Content-Type': 'application/json', ...getAuthHeaders() } });
      if (!res.ok) throw new Error(`Erreur ${res.status}`);
      const data = await res.json();
      setExams(Array.isArray(data) ? data : []);
    } catch (e: any) {
      setError(e.message || 'Erreur de chargement');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  function getStatusColor(status: string) {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'scheduled':
        return 'bg-blue-100 text-blue-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }

  function getStatusText(status: string) {
    switch (status) {
      case 'active':
        return 'Actif';
      case 'scheduled':
        return 'Programmé';
      case 'draft':
        return 'Brouillon';
      default:
        return 'Inconnu';
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gestion des Examens</h1>
          <p className="text-gray-600">Créez et gérez vos examens</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Nouvel Examen
        </button>
      </div>

      {loading && <div className="bg-white p-4 rounded shadow">Chargement...</div>}
      {error && <div className="bg-red-50 text-red-700 p-4 rounded shadow">{error}</div>}

      {/* Exams Table */}
      {!loading && !error && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Examen</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Durée</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Créé le</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {exams.map((exam) => (
                    <tr key={exam.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{exam.title}</div>
                          <div className="text-sm text-gray-500">{exam.description}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{exam.duration_minutes} min</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{exam.created_at ? new Date(exam.created_at).toLocaleString() : '-'}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(exam.status)}`}>{getStatusText(exam.status)}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button className="text-blue-600 hover:text-blue-900"><Eye className="h-4 w-4" /></button>
                          <button className="text-indigo-600 hover:text-indigo-900"><Edit className="h-4 w-4" /></button>
                          <button className="text-red-600 hover:text-red-900"><Trash2 className="h-4 w-4" /></button>
                        </div>
                      </td>
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

export default Exams;
