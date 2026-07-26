import { useState } from 'react'
import { motion } from 'framer-motion'
import { Save, Key, Settings2, Globe, Database } from 'lucide-react'
import toast from 'react-hot-toast'

export function Settings() {
  const [loading, setLoading] = useState(false)

  const handleSave = () => {
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      toast.success('Settings saved successfully')
    }, 800)
  }

  return (
    <div className="max-w-4xl mx-auto animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-muted-foreground mt-1">Configure your AetherLearn.ai Platform preferences</p>
        </div>
        <button
          onClick={handleSave}
          disabled={loading}
          className="btn-glow bg-primary text-white px-6 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2"
        >
          <Save className="w-4 h-4" />
          {loading ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Navigation Sidebar */}
        <div className="col-span-1 space-y-2">
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-primary text-white shadow-md shadow-primary/25 font-semibold text-sm">
            <Key className="w-4 h-4" /> API Keys
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-100 text-slate-600 font-medium text-sm transition-colors">
            <Settings2 className="w-4 h-4" /> Rendering Defaults
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-100 text-slate-600 font-medium text-sm transition-colors">
            <Globe className="w-4 h-4" /> API Configuration
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-100 text-slate-600 font-medium text-sm transition-colors">
            <Database className="w-4 h-4" /> Storage
          </button>
        </div>

        {/* Content Area */}
        <div className="col-span-2 space-y-6">
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="glass rounded-2xl p-6 border border-slate-200/80 shadow-md">
            <h3 className="text-lg font-bold text-slate-800 mb-4">Gemini API Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-semibold text-slate-700 mb-1.5 block">Gemini API Key</label>
                <input
                  type="password"
                  placeholder="AIzaSy..."
                  defaultValue="••••••••••••••••••••••••"
                  className="w-full bg-white border border-slate-200 shadow-sm rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 text-slate-800"
                />
                <p className="text-xs text-slate-400 mt-1.5">Required for content generation and agent reasoning.</p>
              </div>
              
              <div>
                <label className="text-sm font-semibold text-slate-700 mb-1.5 block">Primary Model</label>
                <select className="w-full bg-white border border-slate-200 shadow-sm rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 text-slate-800">
                  <option value="gemini-2.5-flash">Gemini 2.5 Flash (Recommended)</option>
                  <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                </select>
              </div>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }} className="glass rounded-2xl p-6 border border-slate-200/80 shadow-md">
            <h3 className="text-lg font-bold text-slate-800 mb-4">Firebase Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-semibold text-slate-700 mb-1.5 block">Project ID</label>
                <input
                  type="text"
                  placeholder="my-firebase-project"
                  defaultValue="math-tutor-platform"
                  className="w-full bg-white border border-slate-200 shadow-sm rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 text-slate-800"
                />
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
