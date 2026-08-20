import type { AppNotification, QuickSuggestion } from '@/types';

export const quickSuggestions: QuickSuggestion[] = [
  { id: 'bus', icon: 'Bus', label: 'Track My Bus', prompt: 'Where is my campus bus right now?', color: 'text-sky-500 bg-sky-50 dark:bg-sky-500/10' },
  { id: 'timetable', icon: 'CalendarDays', label: "Today's Timetable", prompt: "What's my timetable for today?", color: 'text-violet-500 bg-violet-50 dark:bg-violet-500/10' },
  { id: 'attendance', icon: 'BookCheck', label: 'Attendance', prompt: 'Show my attendance summary', color: 'text-emerald-500 bg-emerald-50 dark:bg-emerald-500/10' },
  { id: 'library', icon: 'BookOpen', label: 'Library', prompt: 'What books do I have currently issued from the library?', color: 'text-amber-500 bg-amber-50 dark:bg-amber-500/10' },
  { id: 'circulars', icon: 'ScrollText', label: 'Circulars', prompt: 'Show me the latest college circulars', color: 'text-rose-500 bg-rose-50 dark:bg-rose-500/10' },
  { id: 'placements', icon: 'GraduationCap', label: 'Placements', prompt: 'What are the upcoming placement drives?', color: 'text-teal-500 bg-teal-50 dark:bg-teal-500/10' },
  { id: 'hostel', icon: 'Building2', label: 'Hostel', prompt: 'Show my hostel details and mess menu', color: 'text-indigo-500 bg-indigo-50 dark:bg-indigo-500/10' },
  { id: 'bonafide', icon: 'FileText', label: 'Bonafide Certificate', prompt: 'I need a bonafide certificate', color: 'text-orange-500 bg-orange-50 dark:bg-orange-500/10' },
  { id: 'faculty', icon: 'Users', label: 'Faculty Details', prompt: 'Show me the faculty for my branch', color: 'text-cyan-500 bg-cyan-50 dark:bg-cyan-500/10' },
  { id: 'events', icon: 'PartyPopper', label: 'Upcoming Events', prompt: 'What events are happening on campus this week?', color: 'text-pink-500 bg-pink-50 dark:bg-pink-500/10' },
];

export const sampleNotifications: AppNotification[] = [
  { id: 'n1', type: 'exam', title: 'Mid-Semester Exam Timetable Released', body: 'The mid-semester examination schedule for Autumn 2025 has been published. Check the dates for Data Structures, DBMS, and Operating Systems.', time: '2h ago', read: false },
  { id: 'n2', type: 'placement', title: 'Microsoft Hiring Deadline Tomorrow', body: 'Applications for the Microsoft SDE role close tomorrow at 11:59 PM. Ensure your resume is updated and submitted.', time: '5h ago', read: false },
  { id: 'n3', type: 'attendance', title: 'Attendance Warning — DBMS', body: 'Your attendance in Database Management Systems is at 72%, below the 75% requirement. Attend upcoming classes to avoid debarment.', time: '8h ago', read: false },
  { id: 'n4', type: 'workshop', title: 'AI/ML Workshop by IBM', body: 'A hands-on workshop on Agentic AI is scheduled for Friday, 3:00 PM in Auditorium B. Registration is free.', time: '1d ago', read: true },
  { id: 'n5', type: 'bus', title: 'Bus Route 7 Delayed', body: 'Route 7 (via MG Road) is running 20 minutes late due to traffic congestion near the flyover.', time: '1d ago', read: true },
  { id: 'n6', type: 'certificate', title: 'Bonafide Certificate Approved', body: 'Your bonafide certificate request (REF: BNF-2025-0418) has been approved. Collect it from the academic office.', time: '2d ago', read: true },
  { id: 'n7', type: 'leave', title: 'Leave Application Approved', body: 'Your medical leave for Aug 4–5 has been approved by Dr. R. Menon.', time: '3d ago', read: true },
];

export const upcomingEvents = [
  { id: 'e1', title: 'IBM Agentic AI Workshop', date: 'Aug 9', time: '3:00 PM', venue: 'Auditorium B', tag: 'Workshop' },
  { id: 'e2', title: 'Inter-college Hackathon', date: 'Aug 12', time: '9:00 AM', venue: 'Innovation Lab', tag: 'Competition' },
  { id: 'e3', title: 'Cultural Night — Rangmanch', date: 'Aug 15', time: '6:30 PM', venue: 'Open Air Theatre', tag: 'Cultural' },
  { id: 'e4', title: 'Tech Talk: Future of LLMs', date: 'Aug 18', time: '5:00 PM', venue: 'Seminar Hall 2', tag: 'Talk' },
];

export const todaySchedule = [
  { id: 's1', time: '09:00', course: 'Data Structures', room: 'CS-201', faculty: 'Dr. A. Sharma' },
  { id: 's2', time: '11:00', course: 'Operating Systems', room: 'CS-305', faculty: 'Prof. K. Rao' },
  { id: 's3', time: '14:00', course: 'DBMS Lab', room: 'Lab-3', faculty: 'Dr. R. Menon' },
];

export const recentCirculars = [
  { id: 'c1', title: 'Revised Academic Calendar — Autumn 2025', date: 'Aug 5', ref: 'CIR/2025/041' },
  { id: 'c2', title: 'Library Timing Extended During Exams', date: 'Aug 3', ref: 'CIR/2025/040' },
  { id: 'c3', title: 'Scholarship Application Window Open', date: 'Aug 1', ref: 'CIR/2025/039' },
];

export const helpfulLinks = [
  { id: 'l1', label: 'Student Portal', icon: 'ExternalLink' },
  { id: 'l2', label: 'Examination Cell', icon: 'ExternalLink' },
  { id: 'l3', label: 'Academic Calendar 2025-26', icon: 'Download' },
  { id: 'l4', label: 'Anti-Ragging Helpline', icon: 'Phone' },
  { id: 'l5', label: 'Grievance Redressal', icon: 'MessageSquare' },
];

export const globalSearchItems = [
  { id: 'g1', type: 'Conversation', label: 'Bus timing for Route 7', icon: 'MessageSquare' },
  { id: 'g2', type: 'Faculty', label: 'Dr. Anjali Sharma — CSE', icon: 'User' },
  { id: 'g3', type: 'Faculty', label: 'Prof. Karthik Rao — CSE', icon: 'User' },
  { id: 'g4', type: 'Department', label: 'Computer Science & Engineering', icon: 'Building2' },
  { id: 'g5', type: 'Course', label: 'CS401 — Data Structures', icon: 'BookOpen' },
  { id: 'g6', type: 'Course', label: 'CS403 — Operating Systems', icon: 'BookOpen' },
  { id: 'g7', type: 'Event', label: 'IBM Agentic AI Workshop', icon: 'CalendarDays' },
  { id: 'g8', type: 'Circular', label: 'Revised Academic Calendar', icon: 'ScrollText' },
  { id: 'g9', type: 'Book', label: 'Introduction to Algorithms (CLRS)', icon: 'BookMarked' },
  { id: 'g10', type: 'Book', label: 'Database System Concepts', icon: 'BookMarked' },
];

export const branches = ['Computer Science & Engineering', 'Information Technology', 'Electronics & Communication', 'Mechanical Engineering', 'Electrical Engineering', 'Civil Engineering', 'Aerospace Engineering'];
export const departments = ['Computer Science & Engineering', 'Information Technology', 'Electronics & Communication', 'Mechanical Engineering', 'Electrical Engineering', 'Mathematics', 'Physics', 'Humanities'];
export const designations = ['Assistant Professor', 'Associate Professor', 'Professor', 'Lecturer', 'Visiting Faculty'];
export const years = ['1st Year', '2nd Year', '3rd Year', '4th Year'];
export const semesters = ['Semester 1', 'Semester 2', 'Semester 3', 'Semester 4', 'Semester 5', 'Semester 6', 'Semester 7', 'Semester 8'];
export const sections = ['A', 'B', 'C', 'D'];
export const careerInterests = ['Software Engineering', 'Data Science', 'AI/ML', 'Cybersecurity', 'Product Management', 'Higher Studies', 'Entrepreneurship', 'Core Engineering'];
export const languages = ['English', 'Hindi', 'Telugu', 'Tamil', 'Kannada', 'Bengali', 'Marathi'];
