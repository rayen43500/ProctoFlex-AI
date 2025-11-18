/**
 * Dashboard Administrateur Complet
 * ProctoFlex AI - Université de Monastir - ESPRIM
 */

import React, { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import { API_BASE, getAuthHeaders } from '@/contexts/AuthContext';
// Lightweight placeholders used instead of chart.js to avoid adding new deps here.
import { 
	Users, 
	Monitor, 
	AlertTriangle, 
	Eye, 
	Settings,
	Download,
	Search,
	RefreshCw,
	TrendingUp,
	TrendingDown,
	Clock,
	CheckCircle,
	XCircle,
	AlertCircle
} from 'lucide-react';


interface Exam {
	id: string;
	title: string;
	description: string;
	duration?: number;
	duration_minutes?: number;
	startTime?: Date;
	endTime?: Date;
	status?: string;
	participants: number;
	maxParticipants: number;
	instructor: string;
	instructions: string;
	allowedApps: string[];
	allowedDomains: string[];
	createdAt?: string;
	created_at?: string;
	updatedAt?: string;
}

interface Student {
	id: string;
	name: string;
	email: string;
	studentId: string;
	status: 'active' | 'inactive' | 'suspended';
	lastLogin: Date;
	totalExams: number;
	violations: number;
	createdAt: Date;
}

interface SurveillanceAlert {
	id: string;
	timestamp: Date;
	studentId: string;
	examId: string;
	incidentType: string;
	alertLevel: 'low' | 'medium' | 'high' | 'critical';
	confidence: number;
	description: string;
	metadata: Record<string, any>;
	processed: boolean;
}

interface ExamSession {
	id: string;
	examId: string;
	studentId: string;
	studentName: string;
	startTime: Date;
	endTime?: Date;
	status: 'active' | 'completed' | 'terminated';
	violations: number;
	lastActivity: Date;
	recordingFiles: {
		video?: string;
		audio?: string;
		screen?: string[];
	};
}

interface DashboardStats {
	totalExams: number;
	activeExams: number;
	totalStudents: number;
	activeSessions: number;
	totalAlerts: number;
	criticalAlerts: number;
	systemHealth: number;
	averageSessionDuration: number;
}

const Dashboard: React.FC = () => {
	const [activeTab, setActiveTab] = useState<'overview' | 'exams' | 'students' | 'surveillance' | 'settings'>('overview');
	const [isLoading, setIsLoading] = useState(true);
	const [refreshInterval, setRefreshInterval] = useState(5000);

	const [stats, setStats] = useState<DashboardStats>({
		totalExams: 0,
		activeExams: 0,
		totalStudents: 0,
		activeSessions: 0,
		totalAlerts: 0,
		criticalAlerts: 0,
		systemHealth: 100,
		averageSessionDuration: 0
	});

	const [exams, setExams] = useState<Exam[]>([]);
	const [students, setStudents] = useState<Student[]>([]);
	const [alerts, setAlerts] = useState<SurveillanceAlert[]>([]);
	const [sessions, setSessions] = useState<ExamSession[]>([]);

	// Helper: safely parse JSON responses and guard against HTML/error pages
	const safeParseJson = async (res: Response, ctx = ''): Promise<any | null> => {
		const ct = res.headers.get('content-type') || '';
		if (!ct.includes('application/json')) {
			const text = await res.text().catch(() => '');
			console.error(`Non-JSON response for ${ctx}:`, text);
			return null;
		}
		try {
			return await res.json();
		} catch (e) {
			const text = await res.text().catch(() => '');
			console.error(`Failed to parse JSON for ${ctx}:`, e, text);
			return null;
		}
	};

	const [searchTerm, setSearchTerm] = useState('');
	const [alertFilter, setAlertFilter] = useState<'all' | 'low' | 'medium' | 'high' | 'critical'>('all');
	const [examFilter, setExamFilter] = useState<'all' | 'scheduled' | 'active' | 'completed'>('all');

	const loadDashboardData = useCallback(async () => {
		setIsLoading(true);

		// Helper: safely parse JSON responses and guard against HTML/error pages
		const safeParseJson = async (res: Response, ctx = ''): Promise<any | null> => {
			const ct = res.headers.get('content-type') || '';
			if (!ct.includes('application/json')) {
				const text = await res.text().catch(() => '');
				console.error(`Non-JSON response for ${ctx}:`, text);
				return null;
			}
			try {
				return await res.json();
			} catch (e) {
				const text = await res.text().catch(() => '');
				console.error(`Failed to parse JSON for ${ctx}:`, e, text);
				return null;
			}
		};

		try {
			// Backend doesn't expose /admin/* routes in the simplified server.
			// Use the available endpoints and compute aggregated stats locally.

			// Exams
			const examsResponse = await fetch(`${API_BASE}/exams`, { headers: { 'Content-Type': 'application/json', ...getAuthHeaders() } });
			let examsData = null;
			if (examsResponse.ok) {
				examsData = await safeParseJson(examsResponse, '/exams');
				if (examsData) setExams(examsData);
			} else {
				console.error('Failed to load exams:', examsResponse.status, await examsResponse.text().catch(() => ''));
			}

			// Alerts (timeline)
			const alertsResponse = await fetch(`${API_BASE}/alerts`, { headers: { 'Content-Type': 'application/json', ...getAuthHeaders() } });
			let alertsData = null;
			if (alertsResponse.ok) {
				alertsData = await safeParseJson(alertsResponse, '/alerts');
				if (alertsData) setAlerts(alertsData);
			} else {
				console.error('Failed to load alerts:', alertsResponse.status, await alertsResponse.text().catch(() => ''));
			}

			// Sessions (simple list)
			const sessionsResponse = await fetch(`${API_BASE}/sessions`, { headers: { 'Content-Type': 'application/json', ...getAuthHeaders() } });
			let sessionsData = null;
			if (sessionsResponse.ok) {
				sessionsData = await safeParseJson(sessionsResponse, '/sessions');
				if (sessionsData) setSessions(sessionsData);
			} else {
				console.error('Failed to load sessions:', sessionsResponse.status, await sessionsResponse.text().catch(() => ''));
			}

			// Users / students
			const usersResponse = await fetch(`${API_BASE}/users`, { headers: { 'Content-Type': 'application/json', ...getAuthHeaders() } });
			let usersData = null;
			if (usersResponse.ok) {
				usersData = await safeParseJson(usersResponse, '/users');
				if (usersData) setStudents(usersData as any);
			} else {
				console.error('Failed to load users/students:', usersResponse.status, await usersResponse.text().catch(() => ''));
			}

			// Compute aggregated stats locally (best-effort)
			try {
				const totalExams = Array.isArray(examsData) ? examsData.length : 0;
				const activeExams = Array.isArray(examsData) ? examsData.filter((e: any) => (e.status || '').toString().toLowerCase() === 'active').length : 0;
				const totalStudents = Array.isArray(usersData) ? usersData.length : 0;
				const activeSessions = Array.isArray(sessionsData) ? sessionsData.filter((s: any) => (s.status || '').toString().toLowerCase() === 'active').length : 0;
				const totalAlerts = Array.isArray(alertsData) ? alertsData.length : 0;
				const criticalAlerts = Array.isArray(alertsData) ? alertsData.filter((a: any) => (a.alertLevel === 'critical' || a.severity === 'high' || a.severity === 'critical')).length : 0;

				// health: try surveillance health endpoint as proxy
				let systemHealth = 100;
				try {
					const healthRes = await fetch(`${API_BASE}/surveillance/health`, { headers: { ...getAuthHeaders() } });
					if (healthRes.ok) {
						const h = await safeParseJson(healthRes, '/surveillance/health');
						if (h && h.status === 'healthy') systemHealth = 100;
					}
				} catch (e) {
					// ignore
				}

				setStats({
					totalExams,
					activeExams,
					totalStudents,
					activeSessions,
					totalAlerts,
					criticalAlerts,
					systemHealth,
					averageSessionDuration: 0
				});
			} catch (e) {
				console.error('Erreur lors du calcul des stats locales:', e);
			}
		} catch (error) {
			console.error('Erreur lors du chargement des données:', error);
			toast.error('Erreur lors du chargement des données (voir console)');
		} finally {
			setIsLoading(false);
		}
	}, []);

	useEffect(() => {
		loadDashboardData();
		const interval = setInterval(loadDashboardData, refreshInterval);
		return () => clearInterval(interval);
	}, [loadDashboardData, refreshInterval]);

	const alertsOverTimeData = {
		labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
		datasets: [
			{
				label: 'Alertes Critiques',
				data: [2, 1, 3, 5, 2, 1],
				borderColor: 'rgb(239, 68, 68)',
				backgroundColor: 'rgba(239, 68, 68, 0.1)',
				tension: 0.4
			},
			{
				label: 'Alertes Élevées',
				data: [5, 3, 7, 8, 6, 4],
				borderColor: 'rgb(245, 158, 11)',
				backgroundColor: 'rgba(245, 158, 11, 0.1)',
				tension: 0.4
			},
			{
				label: 'Alertes Moyennes',
				data: [12, 8, 15, 18, 14, 10],
				borderColor: 'rgb(59, 130, 246)',
				backgroundColor: 'rgba(59, 130, 246, 0.1)',
				tension: 0.4
			}
		]
	};

	const examStatusData = {
		labels: ['Programmés', 'Actifs', 'Terminés', 'Annulés'],
		datasets: [
			{
				data: [stats.totalExams - stats.activeExams, stats.activeExams, 45, 2],
				backgroundColor: [
					'rgb(59, 130, 246)',
					'rgb(34, 197, 94)',
					'rgb(107, 114, 128)',
					'rgb(239, 68, 68)'
				],
				borderWidth: 0
			}
		]
	};

	const alertTypesData = {
		labels: ['Visage Non Visible', 'Regard Détourné', 'Voix Détectée', 'App Non Autorisée', 'Copier-Coller'],
		datasets: [
			{
				label: 'Nombre d\'alertes',
				data: [15, 8, 3, 2, 12],
				backgroundColor: [
					'rgb(239, 68, 68)',
					'rgb(245, 158, 11)',
					'rgb(59, 130, 246)',
					'rgb(168, 85, 247)',
					'rgb(34, 197, 94)'
				]
			}
		]
	};

	const filteredAlerts = alerts.filter(alert => {
		const desc = (alert.description || '').toString().toLowerCase();
		const student = (alert.studentId || '').toString().toLowerCase();
		const matchesSearch = desc.includes(searchTerm.toLowerCase()) || student.includes(searchTerm.toLowerCase());
		const matchesFilter = alertFilter === 'all' || alert.alertLevel === alertFilter;
		return matchesSearch && matchesFilter;
	});

	const filteredExams = exams.filter(exam => {
		const title = (exam.title || '').toString().toLowerCase();
		const instr = (exam.instructor || '').toString().toLowerCase();
		const matchesSearch = title.includes(searchTerm.toLowerCase()) || instr.includes(searchTerm.toLowerCase());
		const matchesFilter = examFilter === 'all' || (exam.status || '').toString() === examFilter;
		return matchesSearch && matchesFilter;
	});

	const handleProcessAlert = async (alertId: string) => {
		try {
				// Backend simplified server does not expose an endpoint to "process" an alert.
				// Perform a local update so the admin UI remains responsive.
				setAlerts(prev => prev.map(alert => alert.id === alertId ? { ...alert, processed: true } : alert));
				toast.success('Alerte marquée comme traitée (local)');
			} catch (error) {
				console.error('Erreur lors du traitement de l\'alerte:', error);
				toast.error('Erreur lors du traitement de l\'alerte');
			}
	};

	const handleTerminateSession = async (sessionId: string) => {
		try {
				// The simplified backend does not provide a terminate endpoint for sessions.
				// Remove locally to keep the UI responsive.
				setSessions(prev => prev.filter(session => session.id !== sessionId));
				toast.success('Session terminée (local)');
			} catch (error) {
				console.error('Erreur lors de la termination de la session:', error);
				toast.error('Erreur lors de la termination');
			}
	};

	const handleDownloadRecording = async (sessionId: string, fileType: 'video' | 'audio' | 'screen') => {
		try {
				// Recording download is not supported by the simplified backend.
				toast(`Téléchargement non pris en charge par le serveur — session:${sessionId} type:${fileType}`);
			} catch (error) {
				console.error('Erreur lors du téléchargement:', error);
				toast.error('Erreur lors du téléchargement');
			}
	};

	const StatCard: React.FC<{
		title: string;
		value: string | number;
		icon: React.ReactNode;
		trend?: 'up' | 'down' | 'neutral';
		trendValue?: string;
		color?: string;
	}> = ({ title, value, icon, trend, trendValue, color = 'blue' }) => (
		<div className={`bg-white rounded-lg shadow-md p-6 border-l-4 border-${color}-500`}>
			<div className="flex items-center justify-between">
				<div>
					<p className="text-sm font-medium text-gray-600">{title}</p>
					<p className="text-2xl font-bold text-gray-900">{value}</p>
					{trend && trendValue && (
						<div className={`flex items-center mt-2 text-sm ${
							trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'
						}`}>
							{trend === 'up' ? <TrendingUp className="w-4 h-4 mr-1" /> : 
							 trend === 'down' ? <TrendingDown className="w-4 h-4 mr-1" /> : 
							 <Clock className="w-4 h-4 mr-1" />}
							{trendValue}
						</div>
					)}
				</div>
				<div className={`p-3 rounded-full bg-${color}-100`}>
					{icon}
				</div>
			</div>
		</div>
	);

	const AlertCard: React.FC<{ alert: SurveillanceAlert }> = ({ alert }) => (
		<div className={`p-4 rounded-lg border-l-4 ${
			alert.alertLevel === 'critical' ? 'border-red-500 bg-red-50' :
			alert.alertLevel === 'high' ? 'border-orange-500 bg-orange-50' :
			alert.alertLevel === 'medium' ? 'border-yellow-500 bg-yellow-50' :
			'border-blue-500 bg-blue-50'
		}`}>
			<div className="flex items-start justify-between">
				<div className="flex-1">
					<div className="flex items-center space-x-2">
						<AlertCircle className={`w-5 h-5 ${
							alert.alertLevel === 'critical' ? 'text-red-500' :
							alert.alertLevel === 'high' ? 'text-orange-500' :
							alert.alertLevel === 'medium' ? 'text-yellow-500' :
							'text-blue-500'
						}`} />
						<span className={`font-medium ${
							alert.alertLevel === 'critical' ? 'text-red-800' :
							alert.alertLevel === 'high' ? 'text-orange-800' :
							alert.alertLevel === 'medium' ? 'text-yellow-800' :
							'text-blue-800'
						}`}>
							{alert.incidentType.replace(/_/g, ' ').toUpperCase()}
						</span>
						<span className={`px-2 py-1 text-xs rounded-full ${
							alert.alertLevel === 'critical' ? 'bg-red-200 text-red-800' :
							alert.alertLevel === 'high' ? 'bg-orange-200 text-orange-800' :
							alert.alertLevel === 'medium' ? 'bg-yellow-200 text-yellow-800' :
							'bg-blue-200 text-blue-800'
						}`}>
							{alert.alertLevel.toUpperCase()}
						</span>
					</div>
					<p className="mt-2 text-sm text-gray-700">{alert.description}</p>
					<div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
						<span>Étudiant: {alert.studentId}</span>
						<span>Confiance: {(alert.confidence * 100).toFixed(1)}%</span>
						<span>{new Date(alert.timestamp).toLocaleString()}</span>
					</div>
				</div>
				{!alert.processed && (
					<button
						onClick={() => handleProcessAlert(alert.id)}
						className="ml-4 px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
					>
						Traiter
					</button>
				)}
			</div>
		</div>
	);

	if (isLoading) {
		return (
			<div className="flex items-center justify-center h-screen">
				<div className="flex items-center space-x-2">
					<RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
					<span className="text-lg text-gray-600">Chargement du dashboard...</span>
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-gray-50">
			{/* Header */}
			<div className="bg-white shadow-sm border-b">
				<div className="px-6 py-4">
					<div className="flex items-center justify-between">
						<div>
							<h1 className="text-2xl font-bold text-gray-900">Dashboard Administrateur</h1>
							<p className="text-sm text-gray-600">ProctoFlex AI - Université de Monastir - ESPRIM</p>
						</div>
						<div className="flex items-center space-x-4">
							<button
								onClick={loadDashboardData}
								className="flex items-center space-x-2 px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
							>
								<RefreshCw className="w-4 h-4" />
								<span>Actualiser</span>
							</button>
							<div className="flex items-center space-x-2">
								<label className="text-sm text-gray-600">Rafraîchissement:</label>
								<select
									value={refreshInterval}
									onChange={(e) => setRefreshInterval(Number(e.target.value))}
									className="px-3 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
								>
									<option value={5000}>5s</option>
									<option value={10000}>10s</option>
									<option value={30000}>30s</option>
									<option value={60000}>1min</option>
								</select>
							</div>
						</div>
					</div>
				</div>
			</div>

			{/* Navigation */}
			<div className="bg-white border-b">
				<div className="px-6">
					<nav className="flex space-x-8">
						{[
							{ id: 'overview', label: 'Vue d\'ensemble', icon: Monitor },
							{ id: 'exams', label: 'Examens', icon: Users },
							{ id: 'students', label: 'Étudiants', icon: Users },
							{ id: 'surveillance', label: 'Surveillance', icon: Eye },
							{ id: 'settings', label: 'Paramètres', icon: Settings }
						].map(({ id, label, icon: Icon }) => (
							<button
								key={id}
								onClick={() => setActiveTab(id as any)}
								className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
									activeTab === id
										? 'border-blue-500 text-blue-600'
										: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
								}`}
							>
								<Icon className="w-4 h-4" />
								<span>{label}</span>
							</button>
						))}
					</nav>
				</div>
			</div>

			{/* Contenu principal */}
			<div className="p-6">
				{activeTab === 'overview' && (
					<div className="space-y-6">
						{/* Statistiques principales */}
						<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
							<StatCard
								title="Examens Actifs"
								value={stats.activeExams}
								icon={<Monitor className="w-6 h-6 text-blue-600" />}
								trend="up"
								trendValue="+12%"
								color="blue"
							/>
							<StatCard
								title="Sessions Actives"
								value={stats.activeSessions}
								icon={<Users className="w-6 h-6 text-green-600" />}
								trend="up"
								trendValue="+8%"
								color="green"
							/>
							<StatCard
								title="Alertes Critiques"
								value={stats.criticalAlerts}
								icon={<AlertTriangle className="w-6 h-6 text-red-600" />}
								trend="down"
								trendValue="-5%"
								color="red"
							/>
							<StatCard
								title="Santé Système"
								value={`${stats.systemHealth}%`}
								icon={<CheckCircle className="w-6 h-6 text-green-600" />}
								trend="neutral"
								color="green"
							/>
						</div>

						{/* Graphiques */}
						<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
							<div className="bg-white p-6 rounded-lg shadow">
								<h3 className="text-lg font-semibold text-gray-900 mb-4">Alertes dans le Temps</h3>
												<div className="h-48 rounded-lg bg-gradient-to-r from-slate-100 to-slate-200 flex items-center justify-center text-sm text-gray-500">Graphique (placeholder)</div>
							</div>
							<div className="bg-white p-6 rounded-lg shadow">
								<h3 className="text-lg font-semibold text-gray-900 mb-4">Statut des Examens</h3>
												<div className="h-48 rounded-lg bg-gradient-to-r from-slate-100 to-slate-200 flex items-center justify-center text-sm text-gray-500">Diagramme (placeholder)</div>
							</div>
						</div>

						{/* Alertes récentes */}
						<div className="bg-white rounded-lg shadow">
							<div className="px-6 py-4 border-b">
								<h3 className="text-lg font-semibold text-gray-900">Alertes Récentes</h3>
							</div>
							<div className="p-6 space-y-4">
								{filteredAlerts.slice(0, 5).map(alert => (
									<AlertCard key={alert.id} alert={alert} />
								))}
							</div>
						</div>
					</div>
				)}

				{activeTab === 'surveillance' && (
					<div className="space-y-6">
						{/* Filtres */}
						<div className="bg-white p-6 rounded-lg shadow">
							<div className="flex items-center space-x-4">
								<div className="flex-1">
									<div className="relative">
										<Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
										<input
											type="text"
											placeholder="Rechercher dans les alertes..."
											value={searchTerm}
											onChange={(e) => setSearchTerm(e.target.value)}
											className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
										/>
									</div>
								</div>
								<select
									value={alertFilter}
									onChange={(e) => setAlertFilter(e.target.value as any)}
									className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
								>
									<option value="all">Tous les niveaux</option>
									<option value="critical">Critique</option>
									<option value="high">Élevé</option>
									<option value="medium">Moyen</option>
									<option value="low">Faible</option>
								</select>
							</div>
						</div>

						{/* Graphique des types d'alertes */}
						<div className="bg-white p-6 rounded-lg shadow">
							<h3 className="text-lg font-semibold text-gray-900 mb-4">Types d'Alertes</h3>
											<div className="h-48 rounded-lg bg-gradient-to-r from-slate-100 to-slate-200 flex items-center justify-center text-sm text-gray-500">Barres (placeholder)</div>
						</div>

						{/* Sessions actives */}
						<div className="bg-white rounded-lg shadow">
							<div className="px-6 py-4 border-b">
								<h3 className="text-lg font-semibold text-gray-900">Sessions Actives</h3>
							</div>
							<div className="overflow-x-auto">
								<table className="w-full">
									<thead className="bg-gray-50">
										<tr>
											<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
												Étudiant
											</th>
											<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
												Examen
											</th>
											<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
												Durée
											</th>
											<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
												Violations
											</th>
											<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
												Actions
											</th>
										</tr>
									</thead>
									<tbody className="bg-white divide-y divide-gray-200">
										{sessions.map(session => (
											<tr key={session.id}>
												<td className="px-6 py-4 whitespace-nowrap">
													<div>
														<div className="text-sm font-medium text-gray-900">{session.studentName}</div>
														<div className="text-sm text-gray-500">{session.studentId}</div>
													</div>
												</td>
												<td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
													{session.examId}
												</td>
												<td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
													{Math.floor((Date.now() - new Date(session.startTime).getTime()) / 60000)} min
												</td>
												<td className="px-6 py-4 whitespace-nowrap">
													<span className={`px-2 py-1 text-xs rounded-full ${
														session.violations === 0 ? 'bg-green-100 text-green-800' :
														session.violations < 3 ? 'bg-yellow-100 text-yellow-800' :
														'bg-red-100 text-red-800'
													}`}>
														{session.violations}
													</span>
												</td>
												<td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
													<button
														onClick={() => handleDownloadRecording(session.id, 'video')}
														className="text-blue-600 hover:text-blue-900"
													>
														<Download className="w-4 h-4" />
													</button>
													<button
														onClick={() => handleTerminateSession(session.id)}
														className="text-red-600 hover:text-red-900"
													>
														<XCircle className="w-4 h-4" />
													</button>
												</td>
											</tr>
										))}
									</tbody>
								</table>
							</div>
						</div>

						{/* Liste des alertes */}
						<div className="bg-white rounded-lg shadow">
							<div className="px-6 py-4 border-b">
								<h3 className="text-lg font-semibold text-gray-900">Toutes les Alertes</h3>
							</div>
							<div className="divide-y divide-gray-200">
								{filteredAlerts.map(alert => (
									<AlertCard key={alert.id} alert={alert} />
								))}
							</div>
						</div>
					</div>
				)}

				{/* Autres onglets... */}
				{activeTab === 'exams' && (
					<div className="bg-white rounded-lg shadow p-6">
						<div className="flex items-center justify-between mb-4">
							<div>
								<h2 className="text-xl font-semibold text-gray-900">Gestion des Examens</h2>
								<p className="text-gray-600 text-sm">Créez et gérez vos examens</p>
							</div>
							<div className="flex items-center gap-3">
								<button
									onClick={loadDashboardData}
									className="px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 hover:bg-slate-100"
								>
									Actualiser
								</button>
								<button
									onClick={async () => {
										try {
											const payload = {
												title: 'Nouvel Examen',
												description: 'Description rapide',
												duration_minutes: 60,
												status: 'draft'
											};
												const res = await fetch(`${API_BASE}/exams`, {
													method: 'POST',
													headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
													body: JSON.stringify(payload)
												});
												if (res.ok) {
													const created = await safeParseJson(res, '/exams (create)');
													if (created) {
														toast.success('Examen créé');
														await loadDashboardData();
													} else {
														toast.error('Réponse inattendue du serveur à la création (voir console)');
													}
												} else {
													console.error('Erreur création examen', await res.text());
													toast.error('Erreur lors de la création de l\'examen');
												}
										} catch (e) {
											console.error(e);
										}
									}}
									className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
								>
									Nouvel Examen
								</button>
							</div>
						</div>

						<div className="overflow-x-auto">
							<table className="min-w-full divide-y divide-gray-200">
								<thead className="bg-gray-50">
									<tr>
										<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Examen</th>
										<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
										<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Durée</th>
										<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Créé le</th>
										<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
										<th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
									</tr>
								</thead>
								<tbody className="bg-white divide-y divide-gray-200">
									{filteredExams.length === 0 && (
										<tr>
											<td colSpan={6} className="px-6 py-8 text-center text-sm text-gray-500">Aucun examen trouvé</td>
										</tr>
									)}
									{filteredExams.map((exam) => (
										<tr key={exam.id}>
											<td className="px-6 py-4 whitespace-nowrap">
												<div className="text-sm font-medium text-gray-900">{exam.title}</div>
											</td>
											<td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{exam.description}</td>
											<td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{(exam.duration && exam.duration_minutes) ? `${exam.duration_minutes || exam.duration} min` : (exam.duration || exam.duration_minutes) ? `${exam.duration || exam.duration_minutes} min` : '—'}</td>
											<td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
												{(() => {
													const created = exam.createdAt || exam.created_at;
													return created ? new Date(created as any).toLocaleString() : '—';
												})()}
											</td>
											<td className="px-6 py-4 whitespace-nowrap text-sm">
												<span className={`px-2 py-1 rounded-full text-xs font-semibold ${exam.status === 'active' || exam.status === 'Actif' ? 'bg-green-100 text-green-800' : 'bg-slate-100 text-slate-800'}`}>
													{exam.status}
												</span>
											</td>
											<td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
												<button
													onClick={async () => {
														const ok = window.confirm(`Supprimer l'examen « ${exam.title} » ? Cette action est irréversible.`);
														if (!ok) return;
														try {
															const res = await fetch(`${API_BASE}/exams/${exam.id}`, { method: 'DELETE', headers: { ...getAuthHeaders() } });
															if (res.ok) {
																setExams(prev => prev.filter(e => e.id !== exam.id));
																toast.success('Examen supprimé');
															} else {
																const text = await res.text();
																console.error('Erreur suppression:', text);
																toast.error('Impossible de supprimer l\'examen (voir console)');
															}
														} catch (e) {
															console.error(e);
															toast.error('Erreur réseau lors de la suppression');
														}
													}}
													className="inline-flex items-center px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
												>Supprimer</button>
												<button
													onClick={() => { /* TODO: ouvrir modal édition */ }}
													className="inline-flex items-center px-3 py-1 bg-slate-50 text-slate-700 rounded hover:bg-slate-100 text-sm"
												>Modifier</button>
											</td>
										</tr>
									))}
								</tbody>
							</table>
						</div>
					</div>
				)}

				{activeTab === 'students' && (
					<div className="bg-white rounded-lg shadow p-6">
						<h2 className="text-xl font-semibold text-gray-900 mb-4">Gestion des Étudiants</h2>
						<p className="text-gray-600">Interface de gestion des étudiants en cours de développement...</p>
					</div>
				)}

				{activeTab === 'settings' && (
					<div className="bg-white rounded-lg shadow p-6">
						<h2 className="text-xl font-semibold text-gray-900 mb-4">Paramètres Système</h2>
						<p className="text-gray-600">Interface de configuration en cours de développement...</p>
					</div>
				)}
			</div>
		</div>
	);
};

export default Dashboard;
