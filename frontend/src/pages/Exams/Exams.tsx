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
  pdf_filename?: string | null;
  instructor_id?: number;
  is_active?: boolean;
  selected_students?: number[];
};

type User = {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: string;
  is_active: boolean;
};

const Exams: React.FC = () => {
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Exam | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [duration, setDuration] = useState<number>(60);
  const [status, setStatus] = useState<'draft' | 'scheduled' | 'active'>('draft');
  const [instructions, setInstructions] = useState('');
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [pdfUploadStatus, setPdfUploadStatus] = useState<string | null>(null);

  // Students management
  const [students, setStudents] = useState<User[]>([]);
  const [selectedStudents, setSelectedStudents] = useState<number[]>([]);
  const [loadingStudents, setLoadingStudents] = useState(false);

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

  async function loadStudents() {
    try {
      setLoadingStudents(true);
      const res = await fetch(`${API_BASE}/users`, { headers: { 'Content-Type': 'application/json', ...getAuthHeaders() } });
      if (!res.ok) throw new Error('Erreur lors du chargement des étudiants');
      const data = await res.json();
      // Filtrer seulement les étudiants
      const studentUsers = data.filter((user: User) => user.role === 'student' && user.is_active);
      setStudents(studentUsers);
    } catch (err) {
      console.error('Erreur lors du chargement des étudiants:', err);
    } finally {
      setLoadingStudents(false);
    }
  }

  useEffect(() => { 
    load(); 
    loadStudents();
  }, []);

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

  function openCreate() {
    setEditing(null);
    setTitle('');
    setDescription('');
    setDuration(60);
    setStatus('draft');
    setInstructions('');
    setPdfFile(null);
    setFormError(null);
    setPdfUploadStatus(null);
    setSelectedStudents([]);
    setShowForm(true);
  }

  function openEdit(exam: Exam) {
    setEditing(exam);
    setTitle(exam.title);
    setDescription(exam.description);
    setDuration(exam.duration_minutes);
    setStatus((exam.status as any) || 'draft');
    setInstructions(exam.instructions || '');
    setPdfFile(null);
    setFormError(null);
    setPdfUploadStatus(null);
    setShowForm(true);
  }

  async function uploadPdfIfAny(examId: string) {
    if (!pdfFile) return;
    setPdfUploadStatus('Upload du PDF en cours...');
    try {
      const form = new FormData();
      form.append('file', pdfFile);
      const response = await fetch(`${API_BASE}/exams/${examId}/material`, {
        method: 'POST',
        headers: { ...getAuthHeaders() },
        body: form
      });
      
      if (!response.ok) {
        console.error('Erreur lors de l\'upload du PDF:', response.statusText);
        setPdfUploadStatus('Erreur lors de l\'upload du PDF');
        throw new Error('Échec de l\'upload du PDF');
      }
      
      const result = await response.json();
      console.log('PDF uploadé avec succès:', result);
      setPdfUploadStatus('PDF uploadé avec succès');
    } catch (error) {
      console.error('Erreur upload PDF:', error);
      setPdfUploadStatus('Erreur lors de l\'upload du PDF');
      // Ne pas bloquer la création de l'examen si l'upload PDF échoue
    }
  }

  async function submitForm(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) { setFormError('Titre requis'); return; }
    setSubmitting(true);
    setFormError(null);
    try {
      if (editing) {
        // Mise à jour d'un examen existant
        const payload = { title, description, duration_minutes: duration, status, instructions };
        const res = await fetch(`${API_BASE}/exams/${editing.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Échec de la mise à jour');
        const updated = await res.json().catch(() => null);
        const examId = (updated && updated.id) ? updated.id : editing.id;
        await uploadPdfIfAny(examId);
        if (updated && updated.id) {
          setExams((prev) => prev.map((e) => (e.id === updated.id ? updated : e)));
        } else {
          await load();
        }
      } else {
        // Création d'un nouvel examen avec JSON
        const payload = {
          title,
          description: description || '',
          duration_minutes: duration,
          instructions: instructions || '',
          status,
          selected_students: selectedStudents,
          instructor_id: 1 // ID de l'instructeur actuel
        };
        
        const res = await fetch(`${API_BASE}/exams`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Échec de la création');
        const created = await res.json().catch(() => null);
        if (created && created.id) {
          // Upload du PDF si fourni
          if (pdfFile) {
            await uploadPdfIfAny(created.id);
          }
          setExams((prev) => [created, ...prev]);
        } else {
          await load();
        }
      }
      setShowForm(false);
    } catch (err: any) {
      setFormError(err.message || 'Erreur lors de l\'enregistrement');
    } finally {
      setSubmitting(false);
    }
  }

  async function deleteExam(exam: Exam) {
    const ok = confirm(`Supprimer l'examen "${exam.title}" ?`);
    if (!ok) return;
    try {
      const res = await fetch(`${API_BASE}/exams/${exam.id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }
      });
      if (!res.ok) throw new Error('Échec de la suppression');
      setExams((prev) => prev.filter((e) => e.id !== exam.id));
    } catch (err: any) {
      alert(err.message || 'Erreur lors de la suppression');
    }
  }

  function toggleStudent(studentId: number) {
    setSelectedStudents(prev => 
      prev.includes(studentId) 
        ? prev.filter(id => id !== studentId)
        : [...prev, studentId]
    );
  }

  function selectAllStudents() {
    setSelectedStudents(students.map(s => s.id));
  }

  function deselectAllStudents() {
    setSelectedStudents([]);
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gestion des Examens</h1>
          <p className="text-gray-600">Créez et gérez vos examens</p>
        </div>
        <button onClick={openCreate} className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Nouvel Examen
        </button>
      </div>

      {loading && <div className="bg-white p-4 rounded shadow">Chargement...</div>}
      {error && <div className="bg-red-50 text-red-700 p-4 rounded shadow">{error}</div>}

      {/* Formulaire */}
      {showForm && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{editing ? 'Modifier un examen' : 'Créer un examen'}</h3>
            <form className="grid gap-4" onSubmit={submitForm}>
              <div>
                <label className="block text-sm font-medium text-gray-700">Titre</label>
                <input className="mt-1 w-full border rounded px-3 py-2" value={title} onChange={(e) => setTitle(e.target.value)} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <textarea className="mt-1 w-full border rounded px-3 py-2" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Durée (minutes)</label>
                  <input type="number" min={10} className="mt-1 w-full border rounded px-3 py-2" value={duration} onChange={(e) => setDuration(Number(e.target.value))} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Statut</label>
                  <select className="mt-1 w-full border rounded px-3 py-2" value={status} onChange={(e) => setStatus(e.target.value as any)}>
                    <option value="draft">Brouillon</option>
                    <option value="scheduled">Programmé</option>
                    <option value="active">Actif</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Instructions</label>
                  <input className="mt-1 w-full border rounded px-3 py-2" value={instructions} onChange={(e) => setInstructions(e.target.value)} />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Document PDF (optionnel)</label>
                <input type="file" accept="application/pdf" onChange={(e) => setPdfFile(e.target.files?.[0] || null)} />
                {pdfFile && (
                  <div className="mt-1 text-sm text-gray-600">
                    Fichier sélectionné: {pdfFile.name}
                  </div>
                )}
                {pdfUploadStatus && (
                  <div className={`mt-1 text-sm p-2 rounded ${
                    pdfUploadStatus.includes('succès') 
                      ? 'bg-green-50 text-green-700' 
                      : pdfUploadStatus.includes('Erreur')
                      ? 'bg-red-50 text-red-700'
                      : 'bg-blue-50 text-blue-700'
                  }`}>
                    {pdfUploadStatus}
                  </div>
                )}
              </div>

              {/* Sélection des étudiants */}
              {!editing && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Étudiants concernés ({selectedStudents.length} sélectionné{selectedStudents.length > 1 ? 's' : ''})
                  </label>
                  
                  <div className="flex gap-2 mb-3">
                    <button
                      type="button"
                      onClick={selectAllStudents}
                      className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                    >
                      Tout sélectionner
                    </button>
                    <button
                      type="button"
                      onClick={deselectAllStudents}
                      className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                    >
                      Tout désélectionner
                    </button>
                  </div>

                  <div className="max-h-40 overflow-y-auto border rounded p-3 space-y-2">
                    {loadingStudents ? (
                      <div className="text-sm text-gray-500">Chargement des étudiants...</div>
                    ) : students.length === 0 ? (
                      <div className="text-sm text-gray-500">Aucun étudiant disponible</div>
                    ) : (
                      students.map((student) => (
                        <label key={student.id} className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-2 rounded">
                          <input
                            type="checkbox"
                            checked={selectedStudents.includes(student.id)}
                            onChange={() => toggleStudent(student.id)}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                          <div className="flex-1">
                            <div className="text-sm font-medium text-gray-900">{student.full_name}</div>
                            <div className="text-xs text-gray-500">{student.email}</div>
                          </div>
                        </label>
                      ))
                    )}
                  </div>
                </div>
              )}

              {formError && <div className="bg-red-50 text-red-700 p-2 rounded text-sm">{formError}</div>}

              <div className="flex gap-2">
                <button disabled={submitting} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50">
                  {submitting ? 'Enregistrement...' : 'Enregistrer'}
                </button>
                <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 rounded border">Annuler</button>
              </div>
            </form>
          </div>
        </div>
      )}

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
                          {exam.pdf_filename && (
                            <a href={`${API_BASE}/exams/${exam.id}/material`} target="_blank" rel="noreferrer" className="text-blue-600 hover:text-blue-900" title="PDF">PDF</a>
                          )}
                          <button onClick={() => openEdit(exam)} className="text-indigo-600 hover:text-indigo-900" title="Modifier"><Edit className="h-4 w-4" /></button>
                          <button onClick={() => deleteExam(exam)} className="text-red-600 hover:text-red-900" title="Supprimer"><Trash2 className="h-4 w-4" /></button>
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
