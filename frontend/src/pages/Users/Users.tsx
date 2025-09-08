import React, { useEffect, useState } from 'react';
import { Plus, Edit, Trash2, User, Calendar } from 'lucide-react';
import { API_BASE, getAuthHeaders } from '../../contexts/AuthContext';

type BackendUser = {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
};

const Users: React.FC = () => {
  const [users, setUsers] = useState<BackendUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE}/users`, { headers: { 'Content-Type': 'application/json', ...getAuthHeaders() } });
        if (!res.ok) throw new Error(`Erreur ${res.status}`);
        const data = await res.json();
        if (!cancelled) setUsers(Array.isArray(data) ? data : []);
      } catch (e: any) {
        if (!cancelled) setError(e.message || 'Erreur de chargement');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const total = users.length;
  const students = users.filter(u => u.role === 'student').length;
  const admins = users.filter(u => u.role === 'admin').length;
  const activesToday = users.filter(u => u.is_active).length; // approximation

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'bg-purple-100 text-purple-800';
      case 'student':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (active: boolean) => (active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gestion des Utilisateurs</h1>
          <p className="text-gray-600">Gérez les comptes étudiants et administrateurs</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Nouvel Utilisateur
        </button>
      </div>

      {loading && <div className="bg-white p-4 rounded shadow">Chargement...</div>}
      {error && <div className="bg-red-50 text-red-700 p-4 rounded shadow">{error}</div>}

      {!loading && !error && (
        <>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
            <div className="bg-white overflow-hidden shadow rounded-lg"><div className="p-5"><div className="flex items-center"><div className="flex-shrink-0"><User className="h-6 w-6 text-blue-500" /></div><div className="ml-5 w-0 flex-1"><dl><dt className="text-sm font-medium text-gray-500 truncate">Total Utilisateurs</dt><dd className="text-lg font-medium text-gray-900">{total}</dd></dl></div></div></div></div>
            <div className="bg-white overflow-hidden shadow rounded-lg"><div className="p-5"><div className="flex items-center"><div className="flex-shrink-0"><User className="h-6 w-6 text-green-500" /></div><div className="ml-5 w-0 flex-1"><dl><dt className="text-sm font-medium text-gray-500 truncate">Étudiants</dt><dd className="text-lg font-medium text-gray-900">{students}</dd></dl></div></div></div></div>
            <div className="bg-white overflow-hidden shadow rounded-lg"><div className="p-5"><div className="flex items-center"><div className="flex-shrink-0"><User className="h-6 w-6 text-purple-500" /></div><div className="ml-5 w-0 flex-1"><dl><dt className="text-sm font-medium text-gray-500 truncate">Administrateurs</dt><dd className="text-lg font-medium text-gray-900">{admins}</dd></dl></div></div></div></div>
            <div className="bg-white overflow-hidden shadow rounded-lg"><div className="p-5"><div className="flex items-center"><div className="flex-shrink-0"><Calendar className="h-6 w-6 text-orange-500" /></div><div className="ml-5 w-0 flex-1"><dl><dt className="text-sm font-medium text-gray-500 truncate">Actifs Aujourd'hui</dt><dd className="text-lg font-medium text-gray-900">{activesToday}</dd></dl></div></div></div></div>
          </div>

          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50"><tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Utilisateur</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rôle</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Créé le</th>
                  </tr></thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {users.map((u) => (
                      <tr key={u.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center"><div className="flex-shrink-0 h-10 w-10"><div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center"><span className="text-sm font-medium text-white">{(u.full_name?.[0] || u.username?.[0] || '?').toUpperCase()}</span></div></div><div className="ml-4"><div className="text-sm font-medium text-gray-900">{u.full_name || u.username}</div><div className="text-sm text-gray-500">{u.email}</div></div></div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap"><span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRoleColor(u.role)}`}>{u.role === 'admin' ? 'Administrateur' : 'Étudiant'}</span></td>
                        <td className="px-6 py-4 whitespace-nowrap"><span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(u.is_active)}`}>{u.is_active ? 'Actif' : 'Inactif'}</span></td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{new Date(u.created_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Users;
