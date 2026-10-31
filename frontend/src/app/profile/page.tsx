'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import { 
  CareerProfile, 
  CareerExperience, 
  CareerProject, 
  CareerSkill, 
  CareerEducation, 
  CareerCertification 
} from '@/lib/types';
import { 
  UserCircle, 
  Briefcase, 
  FolderGit2, 
  Cpu, 
  GraduationCap, 
  Award, 
  Plus, 
  Trash2, 
  Edit3, 
  Save, 
  Loader2, 
  CheckCircle2,
  X
} from 'lucide-react';

export default function CareerProfilePage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const [profile, setProfile] = useState<CareerProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [savingBio, setSavingBio] = useState(false);
  const [activeTab, setActiveTab] = useState<'info' | 'experience' | 'projects' | 'skills' | 'education'>('info');

  // Bio state
  const [fullName, setFullName] = useState('');
  const [headline, setHeadline] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('');
  const [linkedin, setLinkedin] = useState('');
  const [github, setGithub] = useState('');
  const [summary, setSummary] = useState('');
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Experience modal
  const [expModalOpen, setExpModalOpen] = useState(false);
  const [editingExpId, setEditingExpId] = useState<number | null>(null);
  const [expType, setExpType] = useState<'PROFESSIONAL' | 'INTERNSHIP' | 'APPRENTICE'>('PROFESSIONAL');
  const [expTitle, setExpTitle] = useState('');
  const [expCompany, setExpCompany] = useState('');
  const [expLocation, setExpLocation] = useState('');
  const [expStartDate, setExpStartDate] = useState('');
  const [expEndDate, setExpEndDate] = useState('');
  const [expIsCurrent, setExpIsCurrent] = useState(false);
  const [expTechs, setExpTechs] = useState('');
  const [expBullets, setExpBullets] = useState('');

  // Project modal
  const [projModalOpen, setProjModalOpen] = useState(false);
  const [editingProjId, setEditingProjId] = useState<number | null>(null);
  const [projTitle, setProjTitle] = useState('');
  const [projRole, setProjRole] = useState('');
  const [projUrl, setProjUrl] = useState('');
  const [projTechs, setProjTechs] = useState('');
  const [projDesc, setProjDesc] = useState('');
  const [projHighlights, setProjHighlights] = useState('');

  // Skill modal
  const [skillModalOpen, setSkillModalOpen] = useState(false);
  const [skillName, setSkillName] = useState('');
  const [skillCat, setSkillCat] = useState<'LANGUAGES' | 'FRAMEWORKS' | 'DATABASES' | 'CLOUD' | 'TOOLS' | 'OTHER'>('LANGUAGES');
  const [skillProficiency, setSkillProficiency] = useState('Advanced');

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
      return;
    }
    if (user) {
      loadProfile();
    }
  }, [user, authLoading]);

  const loadProfile = async () => {
    try {
      const data = await api.get<CareerProfile>('/api/profile/');
      setProfile(data);
      setFullName(data.full_name || `${user?.first_name || ''} ${user?.last_name || ''}`.trim() || user?.username || '');
      setHeadline(data.headline || '');
      setEmail(data.email || user?.email || '');
      setPhone(data.phone || '');
      setLocation(data.location || '');
      setLinkedin(data.linkedin_url || '');
      setGithub(data.github_url || '');
      setSummary(data.summary || '');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveBio = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingBio(true);
    setSaveSuccess(false);
    try {
      const updated = await api.put<CareerProfile>('/api/profile/', {
        full_name: fullName,
        headline,
        email,
        phone,
        location,
        linkedin_url: linkedin,
        github_url: github,
        summary,
      });
      setProfile(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      alert(err.message || 'Failed to update profile bio.');
    } finally {
      setSavingBio(false);
    }
  };

  // Experience handlers
  const openExpModal = (exp?: CareerExperience) => {
    if (exp) {
      setEditingExpId(exp.id || null);
      setExpType(exp.experience_type);
      setExpTitle(exp.title);
      setExpCompany(exp.company);
      setExpLocation(exp.location || '');
      setExpStartDate(exp.start_date);
      setExpEndDate(exp.end_date || '');
      setExpIsCurrent(exp.is_current);
      setExpTechs(exp.technologies ? exp.technologies.join(', ') : '');
      setExpBullets(exp.bullet_points ? exp.bullet_points.join('\n') : '');
    } else {
      setEditingExpId(null);
      setExpType('PROFESSIONAL');
      setExpTitle('');
      setExpCompany('');
      setExpLocation('');
      setExpStartDate('');
      setExpEndDate('');
      setExpIsCurrent(false);
      setExpTechs('');
      setExpBullets('');
    }
    setExpModalOpen(true);
  };

  const handleSaveExp = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      experience_type: expType,
      title: expTitle,
      company: expCompany,
      location: expLocation,
      start_date: expStartDate,
      end_date: expEndDate,
      is_current: expIsCurrent,
      technologies: expTechs.split(',').map(s => s.trim()).filter(Boolean),
      bullet_points: expBullets.split('\n').map(s => s.trim()).filter(Boolean),
    };

    try {
      if (editingExpId) {
        await api.put(`/api/profile/experiences/${editingExpId}/`, payload);
      } else {
        await api.post('/api/profile/experiences/', payload);
      }
      setExpModalOpen(false);
      await loadProfile();
    } catch (err: any) {
      alert(err.message || 'Failed to save experience.');
    }
  };

  const handleDeleteExp = async (id: number) => {
    if (!confirm('Are you sure you want to delete this experience entry?')) return;
    try {
      await api.delete(`/api/profile/experiences/${id}/`);
      await loadProfile();
    } catch (err: any) {
      alert(err.message || 'Failed to delete experience.');
    }
  };

  // Project handlers
  const openProjModal = (proj?: CareerProject) => {
    if (proj) {
      setEditingProjId(proj.id || null);
      setProjTitle(proj.title);
      setProjRole(proj.role || '');
      setProjUrl(proj.url || '');
      setProjTechs(proj.technologies ? proj.technologies.join(', ') : '');
      setProjDesc(proj.description || '');
      setProjHighlights(proj.highlights ? proj.highlights.join('\n') : '');
    } else {
      setEditingProjId(null);
      setProjTitle('');
      setProjRole('');
      setProjUrl('');
      setProjTechs('');
      setProjDesc('');
      setProjHighlights('');
    }
    setProjModalOpen(true);
  };

  const handleSaveProj = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      title: projTitle,
      role: projRole,
      url: projUrl,
      technologies: projTechs.split(',').map(s => s.trim()).filter(Boolean),
      description: projDesc,
      highlights: projHighlights.split('\n').map(s => s.trim()).filter(Boolean),
    };

    try {
      if (editingProjId) {
        await api.put(`/api/profile/projects/${editingProjId}/`, payload);
      } else {
        await api.post('/api/profile/projects/', payload);
      }
      setProjModalOpen(false);
      await loadProfile();
    } catch (err: any) {
      alert(err.message || 'Failed to save project.');
    }
  };

  const handleDeleteProj = async (id: number) => {
    if (!confirm('Are you sure you want to delete this project?')) return;
    try {
      await api.delete(`/api/profile/projects/${id}/`);
      await loadProfile();
    } catch (err: any) {
      alert(err.message || 'Failed to delete project.');
    }
  };

  // Skill handlers
  const handleSaveSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!skillName.trim()) return;
    try {
      await api.post('/api/profile/skills/', {
        name: skillName.trim(),
        category: skillCat,
        proficiency_level: skillProficiency,
      });
      setSkillName('');
      setSkillModalOpen(false);
      await loadProfile();
    } catch (err: any) {
      alert(err.message || 'Failed to save skill.');
    }
  };

  const handleDeleteSkill = async (id: number) => {
    try {
      await api.delete(`/api/profile/skills/${id}/`);
      await loadProfile();
    } catch (err: any) {
      alert(err.message || 'Failed to delete skill.');
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <UserCircle className="w-7 h-7 text-indigo-400" />
            Complete Career Profile
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Maintain your comprehensive, reusable career database. Every generated resume retrieves evidence directly from this record.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('info')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === 'info'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <UserCircle className="w-4 h-4" />
          General & Bio
        </button>

        <button
          onClick={() => setActiveTab('experience')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === 'experience'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <Briefcase className="w-4 h-4" />
          Experience ({profile?.experiences?.length || 0})
        </button>

        <button
          onClick={() => setActiveTab('projects')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === 'projects'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <FolderGit2 className="w-4 h-4" />
          Projects ({profile?.projects?.length || 0})
        </button>

        <button
          onClick={() => setActiveTab('skills')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === 'skills'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <Cpu className="w-4 h-4" />
          Technical Skills ({profile?.skills?.length || 0})
        </button>
      </div>

      {/* TAB 1: GENERAL & BIO */}
      {activeTab === 'info' && (
        <form onSubmit={handleSaveBio} className="space-y-6 max-w-4xl">
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Contact & Headline Information</h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">Professional Headline</label>
                <input
                  type="text"
                  value={headline}
                  onChange={(e) => setHeadline(e.target.value)}
                  placeholder="e.g. Senior Backend Engineer | Java, Spring Boot, Microservices"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">Phone Number</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+1 (555) 000-0000"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">Location</label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="City, State / Country"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">LinkedIn Profile URL</label>
                <input
                  type="url"
                  value={linkedin}
                  onChange={(e) => setLinkedin(e.target.value)}
                  placeholder="https://linkedin.com/in/username"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1 sm:col-span-2">
                <label className="text-xs font-medium text-slate-300">GitHub Profile URL</label>
                <input
                  type="url"
                  value={github}
                  onChange={(e) => setGithub(e.target.value)}
                  placeholder="https://github.com/username"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="space-y-1 pt-2">
              <label className="text-xs font-medium text-slate-300">Career Summary / Executive Bio</label>
              <textarea
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                rows={4}
                placeholder="Overview of your core engineering background, foundational strengths, and technical goals..."
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              {saveSuccess && (
                <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  Profile bio saved successfully!
                </span>
              )}
              <button
                type="submit"
                disabled={savingBio}
                className="ml-auto px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-500/20 flex items-center gap-2 transition-all disabled:opacity-50"
              >
                {savingBio ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                Save Bio
              </button>
            </div>
          </div>
        </form>
      )}

      {/* TAB 2: EXPERIENCE */}
      {activeTab === 'experience' && (
        <div className="space-y-4 max-w-4xl">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Experience History ({profile?.experiences?.length || 0})
            </h3>
            <button
              onClick={() => openExpModal()}
              className="px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-1.5 transition-all"
            >
              <Plus className="w-4 h-4" />
              Add Experience
            </button>
          </div>

          <div className="space-y-3">
            {profile?.experiences && profile.experiences.length > 0 ? (
              profile.experiences.map((exp) => (
                <div
                  key={exp.id}
                  className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-md space-y-3"
                >
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <div>
                      <span className="text-sm font-bold text-white">{exp.title}</span>
                      <span className="text-xs text-slate-400 font-medium"> &mdash; {exp.company}</span>
                      <span className="ml-2 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                        {exp.experience_type}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-400">
                        {exp.start_date} &ndash; {exp.end_date || 'Present'}
                      </span>
                      <button
                        onClick={() => openExpModal(exp)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDeleteExp(exp.id!)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {exp.technologies && exp.technologies.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {exp.technologies.map((t, idx) => (
                        <span key={idx} className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                          {t}
                        </span>
                      ))}
                    </div>
                  )}

                  {exp.bullet_points && exp.bullet_points.length > 0 && (
                    <ul className="list-disc pl-4 space-y-1 text-xs text-slate-300">
                      {exp.bullet_points.map((b, idx) => (
                        <li key={idx}>{b}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))
            ) : (
              <div className="p-8 text-center bg-slate-900/60 rounded-2xl border border-slate-800 text-slate-400 text-xs">
                No experience records added yet. Click &quot;Add Experience&quot; to build your database.
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: PROJECTS */}
      {activeTab === 'projects' && (
        <div className="space-y-4 max-w-4xl">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Project Portfolio ({profile?.projects?.length || 0})
            </h3>
            <button
              onClick={() => openProjModal()}
              className="px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-1.5 transition-all"
            >
              <Plus className="w-4 h-4" />
              Add Project
            </button>
          </div>

          <div className="space-y-3">
            {profile?.projects && profile.projects.length > 0 ? (
              profile.projects.map((proj) => (
                <div
                  key={proj.id}
                  className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-md space-y-3"
                >
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <div>
                      <span className="text-sm font-bold text-white">{proj.title}</span>
                      {proj.role && <span className="text-xs text-slate-400 font-medium"> &mdash; {proj.role}</span>}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => openProjModal(proj)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDeleteProj(proj.id!)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {proj.technologies && proj.technologies.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {proj.technologies.map((t, idx) => (
                        <span key={idx} className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-indigo-300">
                          {t}
                        </span>
                      ))}
                    </div>
                  )}

                  {proj.description && <p className="text-xs text-slate-300">{proj.description}</p>}

                  {proj.highlights && proj.highlights.length > 0 && (
                    <ul className="list-disc pl-4 space-y-1 text-xs text-slate-300">
                      {proj.highlights.map((h, idx) => (
                        <li key={idx}>{h}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))
            ) : (
              <div className="p-8 text-center bg-slate-900/60 rounded-2xl border border-slate-800 text-slate-400 text-xs">
                No project records added yet. Click &quot;Add Project&quot; to catalogue your work.
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: SKILLS */}
      {activeTab === 'skills' && (
        <div className="space-y-6 max-w-4xl">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Technical Skill Inventory ({profile?.skills?.length || 0})
            </h3>
            <button
              onClick={() => setSkillModalOpen(true)}
              className="px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-1.5 transition-all"
            >
              <Plus className="w-4 h-4" />
              Add Skill
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {(['LANGUAGES', 'FRAMEWORKS', 'DATABASES', 'CLOUD', 'TOOLS', 'OTHER'] as const).map((category) => {
              const categorySkills = profile?.skills?.filter(s => s.category === category) || [];
              const categoryTitles: Record<string, string> = {
                LANGUAGES: 'Programming Languages',
                FRAMEWORKS: 'Frameworks & Libraries',
                DATABASES: 'Databases & Storage',
                CLOUD: 'Cloud & DevOps',
                TOOLS: 'Developer Tools',
                OTHER: 'Other Concepts',
              };

              return (
                <div key={category} className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider border-b border-slate-800 pb-1.5 flex justify-between">
                    <span>{categoryTitles[category]}</span>
                    <span className="text-slate-500">({categorySkills.length})</span>
                  </h4>
                  {categorySkills.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {categorySkills.map((s) => (
                        <span
                          key={s.id}
                          className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 border border-slate-700"
                        >
                          {s.name}
                          <button
                            onClick={() => handleDeleteSkill(s.id!)}
                            className="text-slate-500 hover:text-rose-400"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-[11px] text-slate-500 italic">No skills added in this category.</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* EXPERIENCE MODAL */}
      {expModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-xl rounded-2xl bg-slate-900 border border-slate-800 p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-2 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white">
                {editingExpId ? 'Edit Experience' : 'Add Experience Entry'}
              </h3>
              <button onClick={() => setExpModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveExp} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-semibold text-slate-300">Experience Type</label>
                  <select
                    value={expType}
                    onChange={(e: any) => setExpType(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                  >
                    <option value="PROFESSIONAL">Professional Experience</option>
                    <option value="INTERNSHIP">Internship Experience</option>
                    <option value="APPRENTICE">Apprentice Experience</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="font-semibold text-slate-300">Job Title</label>
                  <input
                    type="text"
                    value={expTitle}
                    onChange={(e) => setExpTitle(e.target.value)}
                    required
                    placeholder="e.g. Backend Developer"
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-semibold text-slate-300">Company</label>
                  <input
                    type="text"
                    value={expCompany}
                    onChange={(e) => setExpCompany(e.target.value)}
                    required
                    placeholder="e.g. Acme Corp"
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                  />
                </div>

                <div className="space-y-1">
                  <label className="font-semibold text-slate-300">Location</label>
                  <input
                    type="text"
                    value={expLocation}
                    onChange={(e) => setExpLocation(e.target.value)}
                    placeholder="e.g. New York, NY / Remote"
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-semibold text-slate-300">Start Date</label>
                  <input
                    type="text"
                    value={expStartDate}
                    onChange={(e) => setExpStartDate(e.target.value)}
                    required
                    placeholder="e.g. Jun 2022"
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                  />
                </div>

                <div className="space-y-1">
                  <label className="font-semibold text-slate-300">End Date</label>
                  <input
                    type="text"
                    value={expEndDate}
                    onChange={(e) => setExpEndDate(e.target.value)}
                    placeholder="e.g. Present or Dec 2023"
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-slate-300">Technologies Used (comma separated)</label>
                <input
                  type="text"
                  value={expTechs}
                  onChange={(e) => setExpTechs(e.target.value)}
                  placeholder="Java, Spring Boot, PostgreSQL, Docker, REST APIs"
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                />
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-slate-300">Responsibilities & Achievements (one bullet per line)</label>
                <textarea
                  value={expBullets}
                  onChange={(e) => setExpBullets(e.target.value)}
                  rows={4}
                  placeholder="Architected high-throughput microservices...&#10;Reduced latency by 35% through query indexing..."
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setExpModalOpen(false)}
                  className="px-3.5 py-1.5 text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold"
                >
                  Save Entry
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* PROJECT MODAL */}
      {projModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-xl rounded-2xl bg-slate-900 border border-slate-800 p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-2 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white">
                {editingProjId ? 'Edit Project' : 'Add Project Entry'}
              </h3>
              <button onClick={() => setProjModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveProj} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-semibold text-slate-300">Project Title</label>
                  <input
                    type="text"
                    value={projTitle}
                    onChange={(e) => setProjTitle(e.target.value)}
                    required
                    placeholder="e.g. Distributed Ledger Service"
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                  />
                </div>

                <div className="space-y-1">
                  <label className="font-semibold text-slate-300">Role</label>
                  <input
                    type="text"
                    value={projRole}
                    onChange={(e) => setProjRole(e.target.value)}
                    placeholder="e.g. Backend Lead"
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-slate-300">Repository / Demo URL</label>
                <input
                  type="url"
                  value={projUrl}
                  onChange={(e) => setProjUrl(e.target.value)}
                  placeholder="https://github.com/username/project"
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                />
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-slate-300">Technologies (comma separated)</label>
                <input
                  type="text"
                  value={projTechs}
                  onChange={(e) => setProjTechs(e.target.value)}
                  placeholder="Java, Spring Boot, Redis, Docker"
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                />
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-slate-300">Short Description</label>
                <textarea
                  value={projDesc}
                  onChange={(e) => setProjDesc(e.target.value)}
                  rows={2}
                  placeholder="Brief overview of project architecture and purpose..."
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                />
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-slate-300">Key Highlights (one per line)</label>
                <textarea
                  value={projHighlights}
                  onChange={(e) => setProjHighlights(e.target.value)}
                  rows={3}
                  placeholder="Integrated Redis distributed locking preventing concurrency races...&#10;Achieved 99.9% uptime processing 10k requests/min..."
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setProjModalOpen(false)}
                  className="px-3.5 py-1.5 text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold"
                >
                  Save Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* SKILL MODAL */}
      {skillModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl bg-slate-900 border border-slate-800 p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-2 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white">Add Technical Skill</h3>
              <button onClick={() => setSkillModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveSkill} className="space-y-3 text-xs">
              <div className="space-y-1">
                <label className="font-semibold text-slate-300">Category</label>
                <select
                  value={skillCat}
                  onChange={(e: any) => setSkillCat(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                >
                  <option value="LANGUAGES">Programming Languages</option>
                  <option value="FRAMEWORKS">Frameworks & Libraries</option>
                  <option value="DATABASES">Databases & Storage</option>
                  <option value="CLOUD">Cloud & DevOps</option>
                  <option value="TOOLS">Developer Tools</option>
                  <option value="OTHER">Other / Architecture</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-slate-300">Skill Name</label>
                <input
                  type="text"
                  value={skillName}
                  onChange={(e) => setSkillName(e.target.value)}
                  required
                  placeholder="e.g. Java, Spring Boot, PostgreSQL, Docker"
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                />
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-slate-300">Proficiency Level</label>
                <select
                  value={skillProficiency}
                  onChange={(e) => setSkillProficiency(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200"
                >
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                  <option value="Expert">Expert</option>
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setSkillModalOpen(false)}
                  className="px-3.5 py-1.5 text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold"
                >
                  Add Skill
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
