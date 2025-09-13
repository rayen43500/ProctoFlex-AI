/**
 * Service API centralisé pour l'application Electron
 */

const API_BASE = 'http://localhost:8000/api/v1';

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
}

export interface Exam {
  id: string;
  title: string;
  description: string;
  duration_minutes: number;
  instructions: string;
  status: string;
  pdf_filename: string | null;
  pdf_path?: string;
  assigned_at: string;
  exam_status: string;
  created_at: string;
  instructor_id?: number;
}

export interface ExamCreateData {
  title: string;
  description: string;
  duration_minutes: number;
  instructions: string;
  status: string;
  selected_students: number[];
  instructor_id: number;
  pdf_file?: File;
}

class ApiService {
  private getAuthHeaders() {
    const token = localStorage.getItem('pf_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  private getAuthHeadersFormData() {
    const token = localStorage.getItem('pf_token');
    return {
      'Authorization': `Bearer ${token}`
    };
  }

  // Authentification avec email
  async login(email: string, password: string) {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: email, password })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Identifiants invalides');
    }

    return await response.json();
  }

  async register(userData: {
    username: string;
    full_name: string;
    email: string;
    password: string;
  }) {
    const response = await fetch(`${API_BASE}/auth/register-with-face`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...userData,
        role: 'student',
        face_image_base64: null
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Erreur lors de l\'inscription');
    }

    return await response.json();
  }

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_BASE}/auth/me`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      if (response.status === 404) {
        // Si l'endpoint /auth/me n'existe pas, retourner un utilisateur par défaut
        // basé sur les informations du token
        const token = localStorage.getItem('pf_token');
        if (token) {
          try {
            // Décoder le token JWT pour obtenir les informations utilisateur
            const payload = JSON.parse(atob(token.split('.')[1]));
            return {
              id: payload.user_id || 1,
              name: payload.username || 'Utilisateur',
              email: payload.username || 'user@example.com',
              role: payload.role || 'student',
              is_active: true
            };
          } catch (e) {
            throw new Error('Token invalide');
          }
        }
      }
      throw new Error('Erreur de récupération du profil');
    }

    return await response.json();
  }

  // Gestion des utilisateurs
  async getUsers(): Promise<User[]> {
    const response = await fetch(`${API_BASE}/users`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error('Erreur de récupération des utilisateurs');
    }

    return await response.json();
  }

  // Gestion des examens pour étudiants
  async getStudentExams(studentId: number): Promise<Exam[]> {
    const response = await fetch(`${API_BASE}/students/${studentId}/exams`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error('Erreur de récupération des examens');
    }

    return await response.json();
  }

  async startExam(studentId: number, examId: string) {
    const response = await fetch(`${API_BASE}/students/${studentId}/exams/${examId}/start`, {
      method: 'POST',
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erreur lors du démarrage de l\'examen');
    }

    return await response.json();
  }

  async completeExam(studentId: number, examId: string) {
    const response = await fetch(`${API_BASE}/students/${studentId}/exams/${examId}/complete`, {
      method: 'POST',
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erreur lors de la finalisation de l\'examen');
    }

    return await response.json();
  }

  // Gestion des examens pour administrateurs
  async getExams(): Promise<Exam[]> {
    const response = await fetch(`${API_BASE}/exams`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error('Erreur de récupération des examens');
    }

    const data = await response.json();
    return data.exams || data;
  }

  async createExam(examData: ExamCreateData): Promise<Exam> {
    const formData = new FormData();
    formData.append('title', examData.title);
    formData.append('description', examData.description);
    formData.append('duration_minutes', examData.duration_minutes.toString());
    formData.append('instructions', examData.instructions);
    formData.append('status', examData.status);
    formData.append('instructor_id', examData.instructor_id.toString());
    formData.append('selected_students', JSON.stringify(examData.selected_students));

    if (examData.pdf_file) {
      formData.append('pdf_file', examData.pdf_file);
    }

    const response = await fetch(`${API_BASE}/exams`, {
      method: 'POST',
      headers: this.getAuthHeadersFormData(),
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erreur lors de la création de l\'examen');
    }

    return await response.json();
  }

  async updateExam(examId: string, examData: Partial<ExamCreateData>): Promise<Exam> {
    const response = await fetch(`${API_BASE}/exams/${examId}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(examData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erreur lors de la mise à jour de l\'examen');
    }

    return await response.json();
  }

  async deleteExam(examId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/exams/${examId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erreur lors de la suppression de l\'examen');
    }
  }

  // Gestion des PDFs
  async uploadExamPDF(examId: string, pdfFile: File): Promise<void> {
    const formData = new FormData();
    formData.append('pdf_file', pdfFile);

    const response = await fetch(`${API_BASE}/exams/${examId}/pdf`, {
      method: 'POST',
      headers: this.getAuthHeadersFormData(),
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erreur lors de l\'upload du PDF');
    }
  }

  async downloadExamPDF(examId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE}/exams/${examId}/pdf`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error('Erreur lors du téléchargement du PDF');
    }

    return await response.blob();
  }

  getExamPDFUrl(examId: string): string {
    return `${API_BASE}/exams/${examId}/pdf`;
  }

  // Assignation d'examens aux étudiants
  async assignExamToStudents(examId: string, studentIds: number[]): Promise<void> {
    const response = await fetch(`${API_BASE}/exams/${examId}/assign`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ student_ids: studentIds })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erreur lors de l\'assignation de l\'examen');
    }
  }
}

export const apiService = new ApiService();
export default apiService;
