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
}

const Dashboard: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [isLoadingAlerts, setIsLoadingAlerts] = useState(false);

  const stats = [
    {
      name: 'Utilisateurs Actifs',
      value: '156',
      change: '+12%',
      changeType: 'positive',
      icon: Users,
    },
    {
      name: 'Examens en Cours',
      value: '23',
      change: '+5%',
      changeType: 'positive',
      icon: FileText,
    },
    {
      name: 'Sessions Actives',
      value: '89',
      change: '+18%',
      changeType: 'positive',
      icon: Monitor,
    },
    {
      name: 'Alertes',
      value: String(alerts.length),
      change: alerts.length > 0 ? '+1' : '0',
      changeType: alerts.length > 0 ? 'negative' : 'positive',
      icon: AlertTriangle,
    },
  ];

  useEffect(() => {
    let alive = true;
    let interval: any;

    async function loadAlerts() {
      try {
        setIsLoadingAlerts(true);
        const res = await fetch(`${API_BASE}/alerts`, {
          headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
        });
        if (!res.ok) return;
        const data = await res.json();
        if (alive && Array.isArray(data)) {
          // tri par timestamp desc si présent
          const sorted = data
            .slice()
            .sort((a: AlertItem, b: AlertItem) => {
              const ta = a.timestamp ? Date.parse(a.timestamp) : 0;
              const tb = b.timestamp ? Date.parse(b.timestamp) : 0;
              return tb - ta;
            });
          setAlerts(sorted);
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
  }, []);

  const recentSessions = [
    {
      id: 1,
      student: 'Ahmed Ben Ali',
      exam: 'Programmation Java',
      status: 'active',
      duration: '1h 23m',
      alerts: 0,
    },
    {
      id: 2,
      student: 'Fatma Mansouri',
      exam: 'Mathématiques Avancées',
      status: 'completed',
      duration: '2h 15m',
      alerts: 1,
    },
    {
      id: 3,
      student: 'Mohamed Karray',
      exam: 'Base de Données',
      status: 'active',
      duration: '45m',
      alerts: 0,
    },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      default:
        return <XCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-red-100 text-red-800';
    }
  };

  const severityColor = (sev?: string) => {
    switch (sev) {
      case 'critical':
        return 'bg-red-600';
      case 'high':
        return 'bg-red-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-blue-500';
      default:
        return 'bg-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      
      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((item) => (
          <div key={item.name} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <item.icon className="h-6 w-6 text-gray-400" />
                </div>
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

      {/* Sessions récentes (placeholder) */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h3 className="text-lg font-semibold text-gray-900">Sessions Récentes</h3>
        </div>
        <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          {recentSessions.map((s) => (
            <div key={s.id} className="border rounded p-4">
              <div className="flex items-center justify-between">
                <div className={`inline-flex items-center px-2 py-1 rounded text-xs ${getStatusColor(s.status)}`}>
                  {getStatusIcon(s.status)}
                  <span className="ml-1 capitalize">{s.status}</span>
                </div>
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
              {alerts.slice(0, 20).map((a, idx) => (
                <li key={idx} className="flex items-start">
                  <span className={`mt-1 h-2 w-2 rounded-full ${severityColor(a.severity)}`}></span>
                  <div className="ml-3">
                    <div className="text-sm text-gray-900">
                      {a.type || 'alerte'}{a.process ? ` · ${a.process}` : ''}
                    </div>
                    <div className="text-xs text-gray-600">
                      {a.message || 'Événement détecté'}
                    </div>
                    <div className="text-xs text-gray-400">
                      {a.timestamp ? new Date(a.timestamp).toLocaleString() : ''}
                    </div>
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
