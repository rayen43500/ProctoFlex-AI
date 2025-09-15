import React, { useState, useEffect } from 'react';
import { API_BASE, getAuthHeaders } from '@/contexts/AuthContext';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: 'admin' | 'student' | 'instructor';
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

interface UserStats {
  total_users: number;
  students: number;
  admins: number;
  instructors: number;
  active_today: number;
}

export default function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Form fields
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<'admin' | 'student' | 'instructor'>('student');
  const [password, setPassword] = useState('');
  const [isActive, setIsActive] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      setError(null);
      
      const headers = { 'Content-Type': 'application/json', ...getAuthHeaders() };
      const [usersResponse, statsResponse] = await Promise.all([
        fetch(`${API_BASE}/users`, { headers }),
        fetch(`${API_BASE}/users/stats`, { headers })
      ]);

      if (!usersResponse.ok) throw new Error('Erreur lors du chargement des utilisateurs');
      if (!statsResponse.ok) throw new Error('Erreur lors du chargement des statistiques');

      const usersData = await usersResponse.json();
      const statsData = await statsResponse.json();

      setUsers(usersData);
      setStats(statsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    } finally {
      setLoading(false);
    }
  }

  function getRoleLabel(role: string) {
    switch (role) {
      case 'admin': return 'Administrateur';
      case 'student': return 'Étudiant';
      case 'instructor': return 'Instructeur';
      default: return 'Inconnu';
    }
  }

  function getStatusLabel(isActive: boolean) {
    return isActive ? 'Actif' : 'Inactif';
  }

  function getStatusColor(isActive: boolean) {
    return isActive ? 'text-green-600' : 'text-red-600';
  }

  function formatDate(dateString: string) {
    if (!dateString) return '-';
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return '-';
    return d.toLocaleString('fr-FR');
  }

  function openCreate() {
    setEditing(null);
    setEmail('');
    setUsername('');
    setFullName('');
    setRole('student');
    setPassword('');
    setIsActive(true);
    setFormError(null);
    setShowForm(true);
  }

  function openEdit(user: User) {
    setEditing(user);
    setEmail(user.email);
    setUsername(user.username);
    setFullName(user.full_name);
    setRole(user.role);
    setPassword('');
    setIsActive(user.is_active);
    setFormError(null);
    setShowForm(true);
  }

  async function submitForm(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim() || !username.trim() || !fullName.trim()) {
      setFormError('Tous les champs sont requis');
      return;
    }
    if (!editing && !password.trim()) {
      setFormError('Le mot de passe est requis pour un nouvel utilisateur');
      return;
    }

    setSubmitting(true);
    try {
      const userData = {
        email: email.trim(),
        username: username.trim(),
        full_name: fullName.trim(),
        role,
        is_active: isActive,
        ...(password.trim() && { password: password.trim() })
      };

      const url = editing ? `${API_BASE}/users/${editing.id}` : `${API_BASE}/users`;
      const method = editing ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de l\'enregistrement');
      }

      await loadData();
      setShowForm(false);
      setFormError(null);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Erreur inconnue');
    } finally {
      setSubmitting(false);
    }
  }

  async function toggleUserStatus(user: User) {
    try {
      const response = await fetch(`${API_BASE}/users/${user.id}/toggle-status`, {
        method: 'PATCH'
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la modification du statut');
      }

      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    }
  }

  async function deleteUser(user: User) {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer l'utilisateur ${user.full_name} ?`)) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/users/${user.id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    }
  }

  function closeForm() {
    setShowForm(false);
    setEditing(null);
    setFormError(null);
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="bg-gray-200 rounded-lg p-4 h-24"></div>
            ))}
          </div>
          <div className="bg-gray-200 rounded-lg h-64"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gestion des Utilisateurs</h1>
          <p className="text-gray-600">Gérez les comptes étudiants et administrateurs</p>
        </div>
        <button
          onClick={openCreate}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Nouvel Utilisateur
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {/* Statistiques */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-2xl font-bold text-gray-900">{stats.total_users}</div>
            <div className="text-sm text-gray-600">Total Utilisateurs</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-2xl font-bold text-blue-600">{stats.students}</div>
            <div className="text-sm text-gray-600">Étudiants</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-2xl font-bold text-red-600">{stats.admins}</div>
            <div className="text-sm text-gray-600">Administrateurs</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-2xl font-bold text-green-600">{stats.active_today}</div>
            <div className="text-sm text-gray-600">Actifs Aujourd'hui</div>
          </div>
        </div>
      )}

      {/* Tableau des utilisateurs */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Utilisateur
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rôle
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Statut
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Créé le
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                          <span className="text-sm font-medium text-gray-700">
                            {user.full_name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.role === 'admin' ? 'bg-red-100 text-red-800' :
                      user.role === 'student' ? 'bg-blue-100 text-blue-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {getRoleLabel(user.role)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm font-medium ${getStatusColor(user.is_active)}`}>
                      {getStatusLabel(user.is_active)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(user.created_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => openEdit(user)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Modifier
                      </button>
                      <button
                        onClick={() => toggleUserStatus(user)}
                        className={`${
                          user.is_active ? 'text-yellow-600 hover:text-yellow-900' : 'text-green-600 hover:text-green-900'
                        }`}
                      >
                        {user.is_active ? 'Désactiver' : 'Activer'}
                      </button>
                      <button
                        onClick={() => deleteUser(user)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Supprimer
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Formulaire de création/édition */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold mb-4">
              {editing ? 'Modifier l\'utilisateur' : 'Nouvel Utilisateur'}
            </h2>
            
            <form onSubmit={submitForm} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  className="mt-1 w-full border rounded px-3 py-2"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Nom d'utilisateur</label>
                <input
                  type="text"
                  className="mt-1 w-full border rounded px-3 py-2"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Nom complet</label>
                <input
                  type="text"
                  className="mt-1 w-full border rounded px-3 py-2"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Rôle</label>
                <select
                  className="mt-1 w-full border rounded px-3 py-2"
                  value={role}
                  onChange={(e) => setRole(e.target.value as any)}
                >
                  <option value="student">Étudiant</option>
                  <option value="instructor">Instructeur</option>
                  <option value="admin">Administrateur</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Mot de passe {editing && '(laisser vide pour ne pas changer)'}
                </label>
                <input
                  type="password"
                  className="mt-1 w-full border rounded px-3 py-2"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required={!editing}
                />
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="isActive"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  checked={isActive}
                  onChange={(e) => setIsActive(e.target.checked)}
                />
                <label htmlFor="isActive" className="ml-2 block text-sm text-gray-900">
                  Utilisateur actif
                </label>
              </div>

              {formError && (
                <div className="bg-red-50 text-red-700 p-2 rounded text-sm">
                  {formError}
                </div>
              )}

              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={submitting}
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {submitting ? 'Enregistrement...' : 'Enregistrer'}
                </button>
                <button
                  type="button"
                  onClick={closeForm}
                  className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
                >
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}