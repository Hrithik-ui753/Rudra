export type Role = 'student' | 'faculty' | 'guest';

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  avatar?: string;
  rollNo?: string;
  teacherId?: string;
  teacherMail?: string;
  branch?: string;
  year?: string;
  semester?: string;
  section?: string;
  department?: string;
  designation?: string;
  busRoute?: string;
  careerInterest?: string;
  language?: string;
}

export interface Attachment {
  id: string;
  name: string;
  type: string;
  size: number;
}

export type CardType =
  | 'timetable'
  | 'attendance'
  | 'bus'
  | 'faculty'
  | 'placement'
  | 'event'
  | 'book'
  | 'library'
  | 'circular'
  | 'notification'
  | 'certificate'
  | 'hostel'
  | 'markdown';

export interface CardData {
  type: CardType;
  [key: string]: unknown;
}

export interface Evidence {
  id: string;
  agent: string;
  source_type: string;
  source_name: string;
  source_file?: string;
  retrieval_method: string;
  records_matched: number;
  filters?: Record<string, unknown>;
  relevance?: number;
  verified?: boolean;
  metadata?: Record<string, unknown>;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  cards?: CardData[];
  attachments?: Attachment[];
  createdAt: number;
  streaming?: boolean;
  feedback?: 'up' | 'down' | null;
  suggestedFollowups?: string[];
  agentName?: string;
  evidence?: Evidence[];
  contextUsed?: boolean;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
  pinned?: boolean;
  suggestedFollowups?: string[];
}

export interface AppNotification {
  id: string;
  type: 'exam' | 'workshop' | 'placement' | 'attendance' | 'bus' | 'certificate' | 'leave' | 'event';
  title: string;
  body: string;
  time: string;
  read: boolean;
}

export interface QuickSuggestion {
  id: string;
  icon: string;
  label: string;
  prompt: string;
  color: string;
}
