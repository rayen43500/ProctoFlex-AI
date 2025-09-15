import React, { useEffect, useState } from 'react';
import { 
  Users, 
  FileText, 
  Monitor, 
  AlertTriangle,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { API_BASE, getAuthHeaders } from '@/contexts/AuthContext';

interface AlertItem {
  type?: string;
  process?: string;
  message?: string;
  severity?: 'low' | 'medium' | 'high' | 'critical' | string;
  timestamp?: string;
  student?: string;
}

const Dashboard: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [isLoadingAlerts, setIsLoadingAlerts] = useState(false);
  const [studentFilter, setStudentFilter] = useState('');

  const [activeUsers, setActiveUsers] = useState<number>(0);
  const [examsInProgress, setExamsInProgress] = useState<number>(0);
  const [activeSessions, setActiveSessions] = useState<number>(0);
  const [recentSessions, setRecentSessions] = useState<any[]>([]);
  const [alertsByStudent, setAlertsByStudent] = useState<Array<{ student: string; count: number }>>([]);

  const stats = [
    { name: 'Utilisateurs Actifs', value: String(activeUsers), icon: Users },
    { name: 'Examens en Cours', value: String(examsInProgress), icon: FileText },
    { name: 'Sessions Actives', value: String(activeSessions), icon: Monitor },
    { name: 'Alertes', value: String(alerts.length), icon: AlertTriangle },
  ];

  useEffect(() => {
    let alive = true;
    let interval: any;

    async function loadAlerts() {
      try {
        setIsLoadingAlerts(true);
        const url = new URL(`${API_BASE}/alerts`);
        if (studentFilter.trim()) url.searchParams.set('student', studentFilter.trim());
        const res = await fetch(url.toString(), {
          headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
        });
        if (!res.ok) return;
        const data = await res.json();
        if (alive && Array.isArray(data)) {
          // Dédupliquer les alertes par (timestamp,type,process,student)
          const uniqueMap = new Map<string, AlertItem>();
          for (const a of data) {
            const k = [a.timestamp || '', a.type || '', a.process || '', a.student || ''].join('|');
            if (!uniqueMap.has(k)) uniqueMap.set(k, a);
          }
          const deduped = Array.from(uniqueMap.values());
          const sorted = deduped
            .slice()
            .sort((a: AlertItem, b: AlertItem) => {
              const ta = a.timestamp ? Date.parse(a.timestamp) : 0;
              const tb = b.timestamp ? Date.parse(b.timestamp) : 0;
              return tb - ta;
            });
          setAlerts(sorted);

          // Agréger par étudiant (ignorer vides)
          const counts = new Map<string, number>();
          for (const a of sorted) {
            const s = (a.student || '').toString().trim();
            if (!s) continue;
            counts.set(s, (counts.get(s) || 0) + 1);
          }
          const agg = Array.from(counts.entries())
            .map(([student, count]) => ({ student, count }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 24);
          setAlertsByStudent(agg);
        }
      } catch {
        // ignore
      } finally {
        if (alive) setIsLoadingAlerts(false);
      }
    }

    loadAlerts();
    interval = setInterval(loadAlerts, 5000);
    return () => { alive = false; clearInterval(interval); };
  }, [studentFilter]);

  // Charger stats: utilisateurs, examens, sessions
  useEffect(() => {
    let alive = true;
    let interval: any;

    async function loadStats() {
      try {
        // Users stats
        const usersRes = await fetch(`${API_BASE}/users/stats`, { headers: getAuthHeaders() });
        if (usersRes.ok) {
          const u = await usersRes.json();
          if (alive) setActiveUsers(Number(u.active_today ?? 0));
        }

        // Exams
        const examsRes = await fetch(`${API_BASE}/exams`, { headers: getAuthHeaders() });
        if (examsRes.ok) {
          const ex = await examsRes.json();
          if (Array.isArray(ex) && alive) {
            const inProgress = ex.filter((e: any) => String(e.status).toLowerCase() === 'started').length;
            setExamsInProgress(inProgress);
          }
        }

        // Sessions
        const sessRes = await fetch(`${API_BASE}/sessions`, { headers: getAuthHeaders() });
        if (sessRes.ok) {
          const s = await sessRes.json();
          if (Array.isArray(s) && alive) {
            setActiveSessions(s.filter((it: any) => String(it.status).toLowerCase() === 'active').length);
            // Mapper sessions récentes pour affichage
            const mapped = s.slice(0, 9).map((it: any, idx: number) => ({
              id: it.id ?? idx,
              student: it.student_name || it.student_id || 'Étudiant',
              exam: it.exam_title || `Examen ${it.exam_id ?? ''}`,
              status: it.status ?? 'active',
              duration: it.duration || '—',
              alerts: Number(it.alerts_count ?? 0),
            }));
            setRecentSessions(mapped);
          }
        }
      } catch {
        // ignore
      }
    }

    loadStats();
    interval = setInterval(loadStats, 10000);
    return () => { alive = false; clearInterval(interval); };
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <Clock className="h-4 w-4 text-blue-500" />;
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />;
      default: return <XCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      default: return 'bg-red-100 text-red-800';
    }
  };

  const severityColor = (sev?: string) => {
    switch (sev) {
      case 'critical': return 'bg-red-600';
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-gray-400';
    }
  };

  return (
    <div className="space-y-6 min-h-[calc(100vh-4rem)]">
      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((item) => (
          <div key={item.name} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0"><item.icon className="h-6 w-6 text-gray-400" /></div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">{item.name}</dt>
                    <dd className="text-lg font-medium text-gray-900">{item.value}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Filtre utilisateur pour timeline */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center gap-3">
          <label className="text-sm text-gray-600">Filtrer par étudiant (email/username)</label>
          <input className="border rounded px-3 py-2" placeholder="ex: student@test.com" value={studentFilter} onChange={(e) => setStudentFilter(e.target.value)} />
          <span className="text-xs text-gray-400">{isLoadingAlerts ? 'Mise à jour...' : ''}</span>
        </div>
      </div>

      {/* Alertes par étudiant */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Alertes par étudiant</h3>
          <span className="text-xs text-gray-500">{alertsByStudent.reduce((a, b) => a + b.count, 0)} total</span>
        </div>
        <div className="p-4 flex flex-wrap gap-2">
          {alertsByStudent.length === 0 ? (
            <div className="text-sm text-gray-500 px-2">Aucune alerte</div>
          ) : alertsByStudent.map(({ student, count }) => (
            <button
              key={student}
              onClick={() => setStudentFilter(student)}
              className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm hover:shadow transition ${studentFilter === student ? 'bg-blue-50 border-blue-300 text-blue-700' : 'bg-white border-gray-200 text-gray-700'}`}
              title={`Voir les alertes de ${student}`}
            >
              <span className="font-medium">{student}</span>
              <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 text-gray-700 text-xs">{count}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Sessions récentes */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b"><h3 className="text-lg font-semibold text-gray-900">Sessions Récentes</h3></div>
        <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          {recentSessions.length === 0 ? (
            <div className="text-sm text-gray-500">Aucune session récente</div>
          ) : recentSessions.map((s) => (
            <div key={s.id} className="border rounded p-4">
              <div className="flex items-center justify-between">
                <div className={`inline-flex items-center px-2 py-1 rounded text-xs ${getStatusColor(s.status)}`}>{getStatusIcon(s.status)}<span className="ml-1 capitalize">{s.status}</span></div>
                <div className="text-sm text-gray-500">{s.duration}</div>
              </div>
              <div className="mt-2 text-sm font-medium text-gray-900">{s.student}</div>
              <div className="text-sm text-gray-600">{s.exam}</div>
              <div className="mt-2 text-sm text-gray-500">Alertes: {s.alerts}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Timeline d'alertes temps réel */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Timeline d’Alertes (temps réel)</h3>
          {isLoadingAlerts && <span className="text-xs text-gray-500">Mise à jour...</span>}
        </div>
        <div className="p-6">
          {alerts.length === 0 ? (
            <div className="text-sm text-gray-500">Aucune alerte</div>
          ) : (
            <ul className="space-y-3">
              {alerts.slice(0, 50).map((a, idx) => (
                <li key={idx} className="flex items-start">
                  <span className={`mt-1 h-2 w-2 rounded-full ${severityColor(a.severity)}`}></span>
                  <div className="ml-3">
                    <div className="text-sm text-gray-900">
                      {a.type || 'alerte'}{a.process ? ` · ${a.process}` : ''}{a.student ? ` · ${a.student}` : ''}
                    </div>
                    <div className="text-xs text-gray-600">{a.message || 'Événement détecté'}</div>
                    <div className="text-xs text-gray-400">{a.timestamp ? new Date(a.timestamp).toLocaleString() : ''}</div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
