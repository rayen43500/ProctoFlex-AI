/**
 * Advanced Surveillance & Technology Dashboard - ProctoFlex AI
 * Real-time exam monitoring interface with advanced analytics
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Users,
  BookOpen,
  Activity,
  AlertTriangle,
  Settings,
  LogOut,
  Trash2,
  Edit2,
  Plus,
  Mail,
  User,
  Eye,
  Radar,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

interface StatCard {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  color: 'blue' | 'green' | 'orange' | 'red';
}

interface Alert {
  id: string;
  student?: string;
  type: string;
  severity: string;
  message: string;
  timestamp: string;
}

interface Exam {
  id: string | number;
  title: string;
  description?: string;
  duration_minutes?: number;
  status?: string;
  created_at?: string;
}

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

interface Session {
  id: string;
  student_name?: string;
  studentName?: string;
  exam_id?: string | number;
  examId?: string | number;
  status: string;
  start_time?: string;
  startTime?: string;
  violations?: number;
}

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user: authUser, logout } = useAuth();

  // State
  const [activeTab, setActiveTab] = useState<'dashboard' | 'exams' | 'sessions' | 'users' | 'settings'>('dashboard');
  const [stats, setStats] = useState({ activeUsers: 0, activeExams: 0, activeSessions: 0, alerts: 0 });
  const [exams, setExams] = useState<Exam[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(false);
  const [studentFilter, setStudentFilter] = useState('');
  const [filteredAlerts, setFilteredAlerts] = useState<Alert[]>([]);

  // Load dashboard data
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      // Load users
      const usersRes = await fetch('/api/v1/users');
      if (usersRes.ok) {
        const usersData = await usersRes.json();
        setUsers(usersData);
      }

      // Load exams
      const examsRes = await fetch('/api/v1/exams');
      if (examsRes.ok) {
        const examsData = await examsRes.json();
        setExams(examsData);
      }

      // Load alerts
      const alertsRes = await fetch('/api/v1/alerts');
      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        setAlerts(alertsData);
      }

      // Calculate stats
      const activeUserCount = users.filter(u => u.is_active).length;
      const activeExamCount = exams.filter(e => e.status === 'active' || e.status === 'Actif').length;
      const alertCount = alerts.length;

      setStats({
        activeUsers: activeUserCount,
        activeExams: activeExamCount,
        activeSessions: 1, // mock
        alerts: alertCount
      });
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoading(false);
    }
  }, [users, exams, alerts]);

  // Filter alerts by student
  useEffect(() => {
    if (studentFilter.trim()) {
      const query = studentFilter.toLowerCase();
      setFilteredAlerts(alerts.filter(a =>
        (a.student && a.student.toLowerCase().includes(query)) ||
        a.type?.toLowerCase().includes(query)
      ));
    } else {
      setFilteredAlerts(alerts);
    }
  }, [studentFilter, alerts]);

  // Load data on mount
  useEffect(() => {
    loadData();
  }, []);

  // Delete exam with improved error handling
  const deleteExam = async (examId: string | number) => {
    if (!window.confirm('🚨 Êtes-vous CERTAIN de vouloir supprimer cet examen ?\n\nCette action est IRRÉVERSIBLE')) return;
    
    try {
      const res = await fetch(`/api/v1/exams/${examId}`, { 
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (res.ok) {
        const data = await res.json();
        if (data.success) {
          // Optimistic update: remove from UI immediately
          setExams(prev => prev.filter(e => e.id !== examId));
          // Show success feedback
          console.log(`✅ Examen ${examId} supprimé avec succès`);
        } else {
          console.error('❌ Erreur serveur: réponse non valide');
          alert('❌ Erreur : La suppression n\'a pas été confirmée par le serveur');
        }
      } else if (res.status === 404) {
        alert('❌ Examen introuvable (déjà supprimé?)');
        // Still remove from UI
        setExams(prev => prev.filter(e => e.id !== examId));
      } else if (res.status === 503) {
        alert('❌ Erreur serveur : Base de données indisponible');
      } else {
        const errorData = await res.json().catch(() => ({}));
        alert(`❌ Erreur ${res.status}: ${errorData.detail || 'Suppression échouée'}`);
      }
    } catch (err) {
      console.error('Erreur réseau lors de la suppression:', err);
      alert('❌ Erreur réseau : Impossible de supprimer l\'examen');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Stat card component - Tech Surveillance Theme
  const StatCard: React.FC<{ stat: StatCard }> = ({ stat }) => {
    const colorClass = {
      blue: 'from-cyan-600 to-blue-600',
      green: 'from-emerald-600 to-teal-600',
      orange: 'from-amber-600 to-orange-600',
      red: 'from-red-600 to-rose-600'
    }[stat.color];

    const bgClass = {
      blue: 'bg-cyan-50/50',
      green: 'bg-emerald-50/50',
      orange: 'bg-amber-50/50',
      red: 'bg-red-50/50'
    }[stat.color];

    const borderClass = {
      blue: 'border-cyan-200',
      green: 'border-emerald-200',
      orange: 'border-amber-200',
      red: 'border-red-200'
    }[stat.color];

    return (
      <div className={`${bgClass} rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 overflow-hidden border-2 ${borderClass} backdrop-blur-sm`}>
        <div className="flex items-center p-8 relative">
          {/* Animated background glow */}
          <div className={`absolute -top-8 -right-8 w-32 h-32 bg-gradient-to-br ${colorClass} opacity-10 rounded-full blur-3xl`}></div>
          
          <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${colorClass} flex items-center justify-center mr-6 shadow-2xl border-2 border-white/50 relative z-10`}>
            <div className="text-white">{stat.icon}</div>
          </div>
          <div className="flex-1 relative z-10">
            <p className="text-xs font-bold text-gray-700 uppercase tracking-widest">{stat.label}</p>
            <p className="text-5xl font-black bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mt-2">{stat.value}</p>
          </div>
        </div>
        {/* Bottom accent line */}
        <div className={`h-1 bg-gradient-to-r ${colorClass}`}></div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header - Tech Surveillance Theme */}
      <header className="bg-gradient-to-r from-slate-800/95 to-blue-900/95 backdrop-blur-xl shadow-2xl sticky top-0 z-50 border-b-2 border-cyan-500/30">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl blur-lg opacity-75 animate-pulse"></div>
                <div className="relative w-14 h-14 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-2xl flex items-center justify-center shadow-xl border-2 border-cyan-300">
                  <Radar className="w-7 h-7 text-white animate-spin" style={{ animationDuration: '3s' }} />
                </div>
              </div>
              <div>
                <h1 className="text-4xl font-black bg-gradient-to-r from-cyan-400 via-blue-300 to-cyan-300 bg-clip-text text-transparent">ProctoFlex AI</h1>
                <p className="text-xs font-bold text-cyan-400 uppercase tracking-widest">🔐 Surveillance & Analytics</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={loadData}
                className="p-3 hover:bg-cyan-500/20 rounded-xl transition-all duration-300 hover:scale-110 text-cyan-400 hover:text-cyan-300 border border-cyan-500/50 hover:border-cyan-400 font-bold"
                title="Refresh Data"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
              <div className="flex items-center gap-3 pl-4 border-l-2 border-cyan-500/30">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full blur-md opacity-50"></div>
                  <div className="relative w-11 h-11 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-full flex items-center justify-center shadow-lg border-2 border-cyan-300">
                    <User className="w-5 h-5 text-white" />
                  </div>
                </div>
                <div className="hidden sm:block">
                  <p className="text-sm font-bold text-white">Administrateur</p>
                  <p className="text-xs text-cyan-300">{authUser?.email || 'admin@proctoflex.ai'}</p>
                </div>
                <button
                  onClick={handleLogout}
                  className="ml-3 p-3 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 text-white rounded-xl transition-all duration-300 hover:scale-110 font-bold shadow-lg hover:shadow-xl border-2 border-red-400/50"
                  title="Logout"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Tab Navigation - Tech Surveillance */}
        <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl shadow-2xl mb-8 border-2 border-cyan-500/30 overflow-hidden backdrop-blur-sm">
          <div className="flex border-b-2 border-cyan-500/20 flex-nowrap overflow-x-auto no-scrollbar">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: Eye },
              { id: 'exams', label: 'Examens', icon: BookOpen },
              { id: 'sessions', label: 'Sessions', icon: Activity },
              { id: 'users', label: 'Utilisateurs', icon: Users },
              { id: 'settings', label: 'Paramètres', icon: Settings }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as any)}
                className={`min-w-[110px] flex-shrink-0 flex items-center gap-2 px-4 sm:px-6 py-3 sm:py-4 font-bold transition-all duration-300 border-b-4 text-left whitespace-nowrap relative ${
                  activeTab === id
                    ? 'border-cyan-500 text-cyan-300 bg-cyan-500/8'
                    : 'border-transparent text-gray-400 hover:text-cyan-300 hover:bg-cyan-500/6'
                }`}
              >
                {activeTab === id && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-cyan-400 to-transparent"></div>
                )}
                <Icon className="w-5 h-5" />
                <span className="truncate">{label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            {/* Statistics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard stat={{ label: 'Utilisateurs Actifs', value: stats.activeUsers, icon: <Users className="w-7 h-7" />, color: 'blue' }} />
              <StatCard stat={{ label: 'Examens en Cours', value: stats.activeExams, icon: <BookOpen className="w-7 h-7" />, color: 'green' }} />
              <StatCard stat={{ label: 'Sessions Actives', value: stats.activeSessions, icon: <Activity className="w-7 h-7" />, color: 'orange' }} />
              <StatCard stat={{ label: 'Alertes', value: stats.alerts, icon: <AlertTriangle className="w-7 h-7" />, color: 'red' }} />
            </div>

            {/* Alerts Section - Tech Surveillance */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-2xl p-8 border-2 border-cyan-500/30 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h2 className="text-3xl font-black bg-gradient-to-r from-cyan-300 to-red-300 bg-clip-text text-transparent">Alertes Système</h2>
                  <p className="text-xs text-cyan-400 font-bold mt-2 uppercase tracking-widest">Monitoring en Temps Réel</p>
                </div>
                <div className="px-4 py-3 bg-gradient-to-r from-red-600/20 to-rose-600/20 text-red-300 rounded-xl text-sm font-bold shadow-lg border-2 border-red-500/50">
                  🚨 {stats.alerts} alerte{stats.alerts !== 1 ? 's' : ''}
                </div>
              </div>

              {/* Student Filter */}
              <div className="mb-8">
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-cyan-400" />
                  <input
                    type="text"
                    placeholder="Filtrer par étudiant (email/username)"
                    value={studentFilter}
                    onChange={(e) => setStudentFilter(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 border-2 border-cyan-500/30 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all duration-200 bg-slate-700/50 hover:bg-slate-700/70 text-white placeholder-gray-400"
                  />
                </div>
                <p className="text-xs text-cyan-400 mt-2 font-medium">ex: student@test.com</p>
              </div>

              {/* Alerts Table */}
              <div className="overflow-x-auto rounded-xl border-2 border-cyan-500/30 bg-slate-800/50">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b-2 border-cyan-500/30 bg-gradient-to-r from-red-600/20 to-rose-600/20">
                      <th className="px-6 py-4 text-left font-bold text-red-300 uppercase tracking-wider">Étudiant</th>
                      <th className="px-6 py-4 text-left font-bold text-red-300 uppercase tracking-wider">Type</th>
                      <th className="px-6 py-4 text-left font-bold text-red-300 uppercase tracking-wider">Sévérité</th>
                      <th className="px-6 py-4 text-left font-bold text-red-300 uppercase tracking-wider">Message</th>
                      <th className="px-6 py-4 text-left font-bold text-red-300 uppercase tracking-wider">Temps</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredAlerts.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center text-cyan-400">
                          <div className="text-6xl mb-3">📭</div>
                          <p className="font-bold text-lg">Aucune alerte détectée</p>
                          <p className="text-xs text-gray-400 mt-2">Le système fonctionne normalement</p>
                        </td>
                      </tr>
                    ) : (
                      filteredAlerts.slice(0, 10).map((alert, idx) => (
                        <tr key={alert.id} className={`border-b border-cyan-500/20 transition-all duration-300 hover:bg-red-600/10 group ${idx % 2 === 0 ? 'bg-slate-800/30' : 'bg-slate-900/30'}`}>
                          <td className="px-6 py-4 font-bold text-white group-hover:text-red-300">{alert.student || '—'}</td>
                          <td className="px-6 py-4 text-gray-300">{alert.type}</td>
                          <td className="px-6 py-4">
                            <span className={`px-3 py-2 rounded-full text-xs font-bold shadow-lg border ${
                              alert.severity === 'critical' ? 'bg-red-600/80 text-red-100 border-red-400/50' :
                              alert.severity === 'high' ? 'bg-orange-600/80 text-orange-100 border-orange-400/50' :
                              alert.severity === 'medium' ? 'bg-yellow-600/80 text-yellow-100 border-yellow-400/50' :
                              'bg-blue-600/80 text-blue-100 border-blue-400/50'
                            }`}>
                              {alert.severity === 'critical' ? '🔴 CRITIQUE' :
                               alert.severity === 'high' ? '🟠 ÉLEVÉ' :
                               alert.severity === 'medium' ? '🟡 MOYEN' :
                               '🔵 BAS'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-gray-300">{alert.message}</td>
                          <td className="px-6 py-4 text-gray-400 text-xs font-mono">{new Date(alert.timestamp).toLocaleString('fr-FR')}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Recent Sessions */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-2xl p-8 border-2 border-cyan-500/30 backdrop-blur-sm">
              <div>
                <h2 className="text-3xl font-black bg-gradient-to-r from-cyan-300 to-emerald-300 bg-clip-text text-transparent mb-2">Sessions Récentes</h2>
                <p className="text-xs text-cyan-400 font-bold uppercase tracking-widest mb-8">Surveillance des Examens</p>
              </div>
              <div className="overflow-x-auto rounded-xl border-2 border-cyan-500/30 bg-slate-800/50">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b-2 border-cyan-500/30 bg-gradient-to-r from-emerald-600/20 to-teal-600/20">
                      <th className="px-6 py-4 text-left font-bold text-emerald-300 uppercase tracking-wider">Étudiant</th>
                      <th className="px-6 py-4 text-left font-bold text-emerald-300 uppercase tracking-wider">Examen</th>
                      <th className="px-6 py-4 text-left font-bold text-emerald-300 uppercase tracking-wider">Statut</th>
                      <th className="px-6 py-4 text-left font-bold text-emerald-300 uppercase tracking-wider">Violations</th>
                      <th className="px-6 py-4 text-left font-bold text-emerald-300 uppercase tracking-wider">Début</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sessions.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center text-cyan-400">
                          <div className="text-6xl mb-3">💤</div>
                          <p className="font-bold text-lg">Aucune session active</p>
                          <p className="text-xs text-gray-400 mt-2">Toutes les sessions sont terminées</p>
                        </td>
                      </tr>
                    ) : (
                      sessions.slice(0, 5).map((session, idx) => (
                        <tr key={session.id} className={`border-b border-cyan-500/20 transition-all duration-300 hover:bg-emerald-600/10 group ${idx % 2 === 0 ? 'bg-slate-800/30' : 'bg-slate-900/30'}`}>
                          <td className="px-6 py-4 font-bold text-white group-hover:text-emerald-300">{session.student_name || session.studentName || '—'}</td>
                          <td className="px-6 py-4 text-gray-300">{session.exam_id || session.examId || '—'}</td>
                          <td className="px-6 py-4">
                            <span className={`px-3 py-2 rounded-full text-xs font-bold shadow-lg border ${
                              session.status === 'active' 
                                ? 'bg-emerald-600/80 text-emerald-100 border-emerald-400/50' 
                                : 'bg-slate-600/80 text-slate-100 border-slate-400/50'
                            }`}>
                              {session.status === 'active' ? '🟢 ACTIF' : '⏸️ TERMINÉ'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-gray-300 font-bold">{session.violations || 0}</td>
                          <td className="px-6 py-4 text-gray-400 text-xs font-mono">{session.start_time || session.startTime || '—'}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Exams Tab */}
        {activeTab === 'exams' && (
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-2xl p-8 border-2 border-cyan-500/30 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-3xl font-black bg-gradient-to-r from-cyan-300 to-blue-300 bg-clip-text text-transparent">Gestion des Examens</h2>
                <p className="text-xs text-cyan-400 font-bold mt-2 uppercase tracking-widest">Surveillance Active</p>
              </div>
              <button className="flex items-center gap-2 px-6 py-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl shadow-lg hover:shadow-2xl hover:scale-105 transition-all duration-300 font-bold border-2 border-cyan-400/50">
                <Plus className="w-6 h-6" />
                Nouvel Examen
              </button>
            </div>

            <div className="overflow-x-auto rounded-xl border-2 border-cyan-500/30 bg-slate-800/50">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b-2 border-cyan-500/30 bg-gradient-to-r from-cyan-600/20 to-blue-600/20">
                    <th className="px-6 py-4 text-left font-bold text-cyan-300 uppercase tracking-wider">Titre</th>
                    <th className="px-6 py-4 text-left font-bold text-cyan-300 uppercase tracking-wider">Description</th>
                    <th className="px-6 py-4 text-left font-bold text-cyan-300 uppercase tracking-wider">Durée</th>
                    <th className="px-6 py-4 text-left font-bold text-cyan-300 uppercase tracking-wider">Statut</th>
                    <th className="px-6 py-4 text-left font-bold text-cyan-300 uppercase tracking-wider">Créé</th>
                    <th className="px-6 py-4 text-right font-bold text-cyan-300 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {exams.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-cyan-400">
                        <div className="text-6xl mb-3">📋</div>
                        <p className="font-bold text-lg">Aucun examen trouvé</p>
                        <p className="text-xs text-gray-400 mt-2">Créez un nouvel examen pour commencer</p>
                      </td>
                    </tr>
                  ) : (
                    exams.map((exam, idx) => (
                      <tr key={exam.id} className={`border-b border-cyan-500/20 transition-all duration-300 hover:bg-cyan-500/10 group ${idx % 2 === 0 ? 'bg-slate-800/30' : 'bg-slate-900/30'}`}>
                        <td className="px-6 py-4 font-bold text-white group-hover:text-cyan-300">{exam.title}</td>
                        <td className="px-6 py-4 text-gray-300 max-w-xs truncate">{exam.description || '—'}</td>
                        <td className="px-6 py-4 text-gray-300 font-semibold">{exam.duration_minutes ? `${exam.duration_minutes} min` : '—'}</td>
                        <td className="px-6 py-4">
                          <span className={`px-3 py-2 rounded-full text-xs font-bold shadow-lg border ${
                            exam.status === 'active' || exam.status === 'Actif' 
                              ? 'bg-emerald-600/80 text-emerald-100 border-emerald-400/50' 
                              : 'bg-amber-600/80 text-amber-100 border-amber-400/50'
                          }`}>
                            {exam.status === 'active' || exam.status === 'Actif' ? '🔴 ACTIF' : '⏸️ BROUILLON'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-gray-400 text-xs font-mono">{exam.created_at ? new Date(exam.created_at).toLocaleString('fr-FR') : '—'}</td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-all duration-300">
                            <button className="p-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white rounded-lg transition-all duration-300 hover:scale-110 font-bold shadow-lg border-2 border-blue-400/50 hover:border-blue-300">
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => deleteExam(exam.id)}
                              className="p-3 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white rounded-lg transition-all duration-300 hover:scale-110 font-bold shadow-lg border-2 border-red-400/50 hover:border-red-300 active:scale-95"
                              title="Supprimer cet examen"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Sessions Tab */}
        {activeTab === 'sessions' && (
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-2xl p-8 border-2 border-cyan-500/30 backdrop-blur-sm">
            <h2 className="text-3xl font-black bg-gradient-to-r from-cyan-300 to-blue-300 bg-clip-text text-transparent mb-2">Gestion des Sessions</h2>
            <p className="text-xs text-cyan-400 font-bold uppercase tracking-widest mb-8">Surveillance Active</p>
            <div className="text-center py-20">
              <div className="inline-block p-4 bg-gradient-to-br from-cyan-600/20 to-blue-600/20 rounded-2xl border-2 border-cyan-500/30 mb-6">
                <div className="text-6xl">🔧</div>
              </div>
              <p className="text-cyan-300 font-bold text-lg">Module en cours de développement</p>
              <p className="text-gray-400 text-sm mt-2">Cette fonctionnalité sera bientôt disponible</p>
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-2xl p-8 border-2 border-cyan-500/30 backdrop-blur-sm">
            <h2 className="text-3xl font-black bg-gradient-to-r from-cyan-300 to-blue-300 bg-clip-text text-transparent mb-2">Paramètres Système</h2>
            <p className="text-xs text-cyan-400 font-bold uppercase tracking-widest mb-8">Configuration Avancée</p>
            <div className="text-center py-20">
              <div className="inline-block p-4 bg-gradient-to-br from-cyan-600/20 to-blue-600/20 rounded-2xl border-2 border-cyan-500/30 mb-6">
                <div className="text-6xl">⚙️</div>
              </div>
              <p className="text-cyan-300 font-bold text-lg">Module en cours de développement</p>
              <p className="text-gray-400 text-sm mt-2">Cette fonctionnalité sera bientôt disponible</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminDashboard;
