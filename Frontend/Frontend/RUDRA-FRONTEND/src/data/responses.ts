import type { CardData, Message, Role, User } from '@/types';

let id = 0;
export const uid = (p = 'id') => `${p}-${Date.now()}-${id++}`;
export const ts = () => Date.now();

const timetableCard = (): CardData => ({
  type: 'timetable',
  day: 'Today',
  slots: [
    { time: '09:00 - 10:00', course: 'Data Structures', room: 'CS-201', faculty: 'Dr. A. Sharma', status: 'done' },
    { time: '10:00 - 11:00', course: 'Operating Systems', room: 'CS-305', faculty: 'Prof. K. Rao', status: 'done' },
    { time: '11:15 - 12:15', course: 'Engineering Maths', room: 'CS-110', faculty: 'Dr. S. Iyer', status: 'live' },
    { time: '14:00 - 16:00', course: 'DBMS Lab', room: 'Lab-3', faculty: 'Dr. R. Menon', status: 'upcoming' },
    { time: '16:15 - 17:15', course: 'Technical Communication', room: 'CS-204', faculty: 'Prof. L. Das', status: 'upcoming' },
  ],
});

const attendanceCard = (): CardData => ({
  type: 'attendance',
  overall: 84,
  subjects: [
    { name: 'Data Structures', attended: 22, total: 24, percent: 92 },
    { name: 'Operating Systems', attended: 18, total: 22, percent: 82 },
    { name: 'DBMS', attended: 16, total: 22, percent: 73, warning: true },
    { name: 'Engineering Maths', attended: 20, total: 24, percent: 83 },
    { name: 'Technical Communication', attended: 19, total: 20, percent: 95 },
  ],
});

const busCard = (): CardData => ({
  type: 'bus',
  route: 'Route 7 — Via MG Road',
  busNumber: 'KA-01-AB-4521',
  driver: 'Ramesh',
  status: 'On Time',
  eta: '8 min',
  currentStop: 'MG Road Metro',
  nextStop: 'Campus Main Gate',
  stops: [
    { name: 'Whitefield Terminal', time: '08:00', passed: true },
    { name: 'Kadugodi', time: '08:10', passed: true },
    { name: 'Hope Farm', time: '08:18', passed: true },
    { name: 'MG Road Metro', time: '08:35', passed: false, current: true },
    { name: 'Campus Main Gate', time: '08:43', passed: false },
  ],
});

const facultyCard = (): CardData => ({
  type: 'faculty',
  members: [
    { name: 'Dr. Nagaratna P. Hegde', designation: 'Professor & HoD', dept: 'CSE', email: 'nagaratnaph@gmai.com', cabin: 'CSE HoD Office', courses: ['Artificial Intelligence', 'Discrete Maths'], avatar: 'NH' },
    { name: 'Dr. T. Adilakshmi', designation: 'Professor & Director', dept: 'CSE', email: 'hodcse@staff.vce.ac.in', cabin: 'CSE Director Office', courses: ['DBMS', 'Algorithms'], avatar: 'TA' },
    { name: 'Ms. L. Divya', designation: 'Assistant Professor', dept: 'IT', email: 'Divya.Lingineni@staff.vce.ac.in', cabin: 'IT Staff Room', courses: ['Web Technologies', 'Java'], avatar: 'LD' },
  ],
});

const placementCard = (): CardData => ({
  type: 'placement',
  drives: [
    { company: 'Google Cloud', role: 'Software Engineer', ctc: '24.0 LPA', date: 'Sept 15, 2026', status: 'Registration Open', logo: 'G' },
    { company: 'Microsoft', role: 'SDE-1', ctc: '22.5 LPA', date: 'Sept 22, 2026', status: 'Registration Open', logo: 'M' },
    { company: 'TCS Digital', role: 'Digital Engineer', ctc: '7.5 LPA', date: 'Oct 05, 2026', status: 'Upcoming', logo: 'T' },
  ],
});

const libraryCard = (): CardData => ({
  type: 'library',
  issued: [
    { title: 'Introduction to Algorithms (CLRS 4th Ed)', dueDate: '15 Aug 2026', fine: 0, status: 'Active' },
    { title: 'Database System Concepts', dueDate: '20 Aug 2026', fine: 0, status: 'Active' },
  ],
  dues: 0,
});

const circularCard = (): CardData => ({
  type: 'circular',
  notices: [
    { title: 'Odd Semester Supplementary Exams', date: '05 Aug 2026', priority: 'High', ref: 'CIRC-2026-88' },
    { title: 'Mandatory Anti-Ragging Affidavit Submission', date: '02 Aug 2026', priority: 'Medium', ref: 'CIRC-2026-85' },
  ],
});

const eventCard = (): CardData => ({
  type: 'event',
  events: [
    { title: 'HACK-RUDRA 2026 National Hackathon', date: '25 Aug 2026', location: 'Main Auditorium', category: 'Hackathon' },
    { title: 'AI & GenAI Masterclass Workshop', date: '30 Aug 2026', location: 'Seminar Hall 2', category: 'Workshop' },
  ],
});

const notificationCard = (): CardData => ({
  type: 'notification',
  items: [
    { text: 'Your attendance in DBMS is 73%. Submit medical certificate if absent.', time: '2 hours ago', unread: true },
    { text: 'Placement drive for Google Cloud is scheduled for Sept 15.', time: 'Yesterday', unread: false },
  ],
});

const certificateCard = (): CardData => ({
  type: 'certificate',
  requests: [
    { type: 'Bonafide Certificate', status: 'Ready to Download', date: 'Yesterday' },
    { type: 'Transcript', status: 'In Progress', date: '3 days ago' },
  ],
});

export function createUserMessage(content: string, attachments?: Message['attachments']): Message {
  return {
    id: uid('m'),
    role: 'user',
    content,
    createdAt: ts(),
    attachments,
  };
}

export function createAssistantMessage(content: string, cards?: CardData[]): Message {
  return {
    id: uid('m'),
    role: 'assistant',
    content,
    createdAt: ts(),
    cards,
    streaming: true,
  };
}

export function generateResponse(prompt: string, _role: Role, currentUser?: User | null): { content: string; cards?: CardData[]; userPatch?: Partial<User> } {
  const p = prompt.toLowerCase();

  // Explicit User Profile View Intent
  if (/my profile|show profile|my details|who am i|profile info/.test(p)) {
    if (!currentUser || currentUser.role === 'guest') {
      return { content: "You are currently logged in as a **Guest User**. Sign up or log in to view your complete academic profile." };
    }
    const isFaculty = currentUser.role === 'faculty';
    const profileDetails = isFaculty
      ? `👤 **Name:** ${currentUser.name}\n📧 **Teacher Mail:** ${currentUser.teacherMail || currentUser.email}\n🆔 **Teacher ID:** ${currentUser.teacherId || 'N/A'}\n🏢 **Department:** ${currentUser.department || 'N/A'}\n💼 **Designation:** ${currentUser.designation || 'N/A'}`
      : `👤 **Name:** ${currentUser.name}\n📧 **Email:** ${currentUser.email}\n🆔 **Roll Number:** ${currentUser.rollNo || '24VCE1001'}\n🎓 **Branch:** ${currentUser.branch || 'Computer Science & Engineering'}\n📅 **Year:** ${currentUser.year || '2nd Year'}\n🏷️ **Section:** ${currentUser.section || 'CSE-A'}`;

    return {
      content: `### 📋 Your Stored User Profile\n\n${profileDetails}\n\n*Your profile data is saved in Supabase PostgreSQL. Type e.g. "update my roll number to 24VCE889" to update details!*`,
    };
  }

  // Explicit Profile Update Intent ONLY when user explicitly says "update", "set", "change", or "my roll number is"
  const userPatch: Partial<User> = {};
  let updateMsg = '';

  const isExplicitUpdate = /update|set|change|my roll|my section|my branch|my email|my year/i.test(prompt);

  if (isExplicitUpdate) {
    const rollMatch = prompt.match(/(?:roll\s*(?:no|number)?\s*(?:is|to|=|:)?\s*)(1602[-\s]?\d{2}[-\s]?\d{3}[-\s]?\d{3,4}|\b[A-Z0-9-]{8,15}\b)/i);
    if (rollMatch) {
      const newRoll = rollMatch[1].trim();
      userPatch.rollNo = newRoll;
      updateMsg += `• **Roll Number** updated to \`${newRoll}\`\n`;
    }

    if (/computer\s*science|cse/i.test(prompt) && /branch|dept|department/i.test(prompt)) {
      userPatch.branch = 'Computer Science & Engineering'; updateMsg += `• **Branch** updated to \`Computer Science & Engineering\`\n`;
    } else if (/info|information\s*tech|it/i.test(prompt) && /branch|dept|department/i.test(prompt)) {
      userPatch.branch = 'Information Technology'; updateMsg += `• **Branch** updated to \`Information Technology\`\n`;
    }

    const secMatch = prompt.match(/(?:section|sec)\s*(?:is|to|=|:)?\s*([A-D])/i);
    if (secMatch) {
      const newSec = secMatch[1].toUpperCase();
      userPatch.section = newSec;
      updateMsg += `• **Section** updated to \`Section ${newSec}\`\n`;
    }

    if (updateMsg) {
      return {
        content: `✨ **Profile Updated & Saved to Supabase!**\n\n${updateMsg}\nType "show my profile" anytime to review your complete profile!`,
        userPatch
      };
    }
  }

  // Domain queries fallback
  if (/hod|faculty|professor|proffessor|poroffessor|teacher|assistant|assisitant|associate|email|divya|sharma|rao|menon|adilakshmi|hegde/i.test(p)) {
    return {
      content: `Here are the faculty members matching your query:\n\n**Dr. Nagaratna P. Hegde**\n• **Designation**: Professor & HoD\n• **Department**: Computer Science & Engineering\n• **Email**: \`nagaratnaph@gmai.com\`\n\n---\n\n**Dr. T. Adilakshmi**\n• **Designation**: Professor & Director - CSE\n• **Email**: \`hodcse@staff.vce.ac.in\`\n\n---\n\n**Ms. L. Divya**\n• **Designation**: Assistant Professor\n• **Department**: Information Technology\n• **Email**: \`Divya.Lingineni@staff.vce.ac.in\`\n\n---\n💡 **Suggested Next Questions:**\n1. 🔹 *"Who is the Director of CSE Department?"*\n2. 🔹 *"Show CSE Faculty Office Hours & Timetables"*\n3. 🔹 *"Get email contacts for all CSE Professors"`,
      cards: [facultyCard()]
    };
  }

  if (/attendance|mark|marks|grade|cgpa|sgpa/i.test(p)) {
    return {
      content: `### 📊 Academic Summary & Attendance\n\n• **Overall Attendance**: **85.0%**\n• **Cumulative CGPA**: **8.72**\n• **Previous SGPA**: **8.85**\n\n---\n💡 **Suggested Next Questions:**\n1. 🔹 *"Show my internal exam marks breakdown"*\n2. 🔹 *"What is my attendance percentage in DBMS?"*\n3. 🔹 *"When are the first Mid-Term Examinations?"*`,
      cards: [attendanceCard()]
    };
  }

  return {
    content: `I'm your **RUDRA Smart Campus Assistant**. You can ask me about faculty directory, HOD contact details, attendance, timetable, placement drives, library books, or fee dues!\n\n---\n💡 **Suggested Next Questions:**\n1. 🔹 *"Who is the HOD of CSE?"*\n2. 🔹 *"Show my student profile summary"*\n3. 🔹 *"Check my overall attendance percentage"*`
  };
}

export function extractCardsFromBackendData(rawData: any, query: string): CardData[] {
  if (!rawData || typeof rawData !== 'object') {
    const p = query.toLowerCase();
    if (/faculty|professor|hod|teacher/i.test(p)) return [facultyCard()];
    if (/timetable|schedule|class/i.test(p)) return [timetableCard()];
    if (/attendance|mark/i.test(p)) return [attendanceCard()];
    if (/event|workshop|hackathon/i.test(p)) return [eventCard()];
    if (/placement|drive|job/i.test(p)) return [placementCard()];
    if (/bus|transport|route/i.test(p)) return [busCard()];
    return [];
  }

  const cards: CardData[] = [];

  if (rawData.events_agent?.data?.events) {
    const eventsList = rawData.events_agent.data.events.map((e: any) => ({
      title: e.title || e.Event_Name || 'Campus Event',
      date: e.date || e.Start_Date || 'Upcoming',
      location: e.location || e.Venue || 'Campus Auditorium',
      category: e.category || e.Category || 'Event'
    }));
    cards.push({ type: 'event', events: eventsList });
  }

  if (rawData.faculty_agent?.data?.faculty_profile) {
    const f = rawData.faculty_agent.data.faculty_profile;
    cards.push({
      type: 'faculty',
      members: [{
        name: f.Name || 'Faculty Member',
        designation: f.Designation || f.Department || 'Faculty',
        dept: f.Department || 'VCE',
        email: f.Email || 'faculty@campus.edu',
        cabin: f.Cabin || 'Faculty Room',
        courses: f.Qualification ? [f.Qualification] : [],
        avatar: (f.Name || 'F').split(' ').map((n: string) => n[0]).join('').slice(0, 2).toUpperCase()
      }]
    });
  }

  if (rawData.timetable_agent?.data?.faculty_schedule) {
    const s = rawData.timetable_agent.data.faculty_schedule;
    const timeSlots = ["9:40 - 10:40", "10:40 - 11:40", "11:40 - 12:40", "1:20 - 2:20", "2:20 - 3:20", "3:20 - 4:20"];
    const slots = timeSlots.filter(t => s[t]).map((t, idx) => ({
      time: t,
      course: s[t],
      room: 'Main Block',
      faculty: s.Name || 'Faculty',
      status: idx === 0 ? 'done' : idx === 1 ? 'live' : 'upcoming'
    }));
    if (slots.length > 0) {
      cards.push({ type: 'timetable', day: 'Today', slots });
    }
  }

  if (cards.length === 0) {
    const p = query.toLowerCase();
    if (/faculty|professor|hod|teacher/i.test(p)) cards.push(facultyCard());
    else if (/timetable|schedule|class/i.test(p)) cards.push(timetableCard());
    else if (/attendance|mark/i.test(p)) cards.push(attendanceCard());
    else if (/event|workshop|hackathon/i.test(p)) cards.push(eventCard());
    else if (/placement|drive|job/i.test(p)) cards.push(placementCard());
    else if (/bus|transport|route/i.test(p)) cards.push(busCard());
    else if (/library|book/i.test(p)) cards.push(libraryCard());
    else if (/circular|notice/i.test(p)) cards.push(circularCard());
    else if (/certificate/i.test(p)) cards.push(certificateCard());
    else if (/notification/i.test(p)) cards.push(notificationCard());
  }

  return cards;
}

