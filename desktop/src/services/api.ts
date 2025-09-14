// API service for the Electron desktop app
const API_BASE_URL = 'http://localhost:8000/api/v1';

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
  description?: string;
  duration_minutes: number;
  instructions?: string;
  exam_status: 'assigned' | 'started' | 'completed' | 'failed';
  assigned_at: string;
  pdf_filename?: string;
}

class ApiService {
  private getAuthHeaders() {
    const token = localStorage.getItem('pf_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  async login(email: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: email,
        password: password
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Login failed: ${response.status}`);
    }

    return response.json();
  }

  async register(userData: {
    name: string;
    email: string;
    password: string;
    face_encoding?: string;
  }): Promise<{ access_token: string; token_type: string }> {
    const response = await fetch(`${API_BASE_URL}/auth/register-with-face`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Registration failed: ${response.status}`);
    }

    return response.json();
  }

  async getCurrentUser(): Promise<User> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: this.getAuthHeaders()
      });

      if (!response.ok) {
        if (response.status === 404) {
          // Fallback: try to decode JWT token locally
          const token = localStorage.getItem('pf_token');
          if (token) {
            try {
              const payload = JSON.parse(atob(token.split('.')[1]));
              return {
                id: payload.sub || 6,
                name: payload.name || 'Étudiant',
                email: payload.email || 'student@test.com',
                role: payload.role || 'student',
                is_active: payload.is_active !== false
              };
            } catch (e) {
              throw new Error('Invalid token');
            }
          }
          throw new Error('User not found');
        }
        throw new Error(`Failed to get user: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      // Fallback: try to decode JWT token locally
      const token = localStorage.getItem('pf_token');
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          return {
            id: payload.sub || 6,
            name: payload.name || 'Étudiant',
            email: payload.email || 'student@test.com',
            role: payload.role || 'student',
            is_active: payload.is_active !== false
          };
        } catch (e) {
          throw error;
        }
      }
      throw error;
    }
  }

  async getStudentExams(studentId: number): Promise<Exam[]> {
    const response = await fetch(`${API_BASE_URL}/exams/student/${studentId}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to get exams: ${response.status}`);
    }

    return response.json();
  }

  async getExam(examId: string): Promise<Exam> {
    const response = await fetch(`${API_BASE_URL}/exams/${examId}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to get exam: ${response.status}`);
    }

    return response.json();
  }

  async startExam(examId: string, studentId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/exams/${examId}/start`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ student_id: studentId })
    });

    if (!response.ok) {
      throw new Error(`Failed to start exam: ${response.status}`);
    }
  }

  async submitExam(examId: string, studentId: number, answers: any): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/exams/${examId}/submit`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ 
        student_id: studentId,
        answers: answers
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to submit exam: ${response.status}`);
    }
  }

  async getExamPDF(examId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/exams/${examId}/view`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to get exam PDF: ${response.status}`);
    }

    return response.blob();
  }
}

export const apiService = new ApiService();