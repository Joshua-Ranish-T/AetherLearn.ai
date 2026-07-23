import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import { FileText, Image, Upload, Type, BookOpen, ChevronRight, Loader2 } from 'lucide-react'
import { useCreateProject, useCreateProjectWithFile, useStartGeneration } from '@/hooks/useProjects'
import type { InputType } from '@/types'
import { cn } from '@/lib/utils'

const INPUT_TYPES: { type: InputType; label: string; description: string; icon: React.ElementType; accepts?: string }[] = [
  { type: 'topic', label: 'Educational Topic', description: 'Enter a topic and AI generates a full lesson', icon: BookOpen },
  { type: 'text', label: 'Educational Text', description: 'Paste your content or explanation', icon: Type },
  { type: 'pdf', label: 'PDF Document', description: 'Upload a PDF — OCR extracts content automatically', icon: FileText, accepts: '.pdf' },
  { type: 'image', label: 'Image / Screenshot', description: 'Upload a textbook page, whiteboard photo, or screenshot', icon: Image, accepts: 'image/*' },
  { type: 'handwritten', label: 'Handwritten Notes', description: 'Upload handwritten notes — AI reads and converts them', icon: Upload, accepts: 'image/*' },
]

const QUALITY_OPTIONS = [
  { value: 'low_quality', label: 'Draft', desc: 'Fast preview (~1min)' },
  { value: 'medium_quality', label: 'Standard', desc: 'Good quality (~3min)' },
  { value: 'high_quality', label: 'High', desc: 'Best quality (~8min)' },
]

export function CreateProject() {
  const navigate = useNavigate()
  const [step, setStep] = useState<1 | 2 | 3>(1)
  const [selectedType, setSelectedType] = useState<InputType>('topic')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [inputText, setInputText] = useState('')
  const [quality, setQuality] = useState('medium_quality')
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)

  const createProject = useCreateProject()
  const createWithFile = useCreateProjectWithFile()
  const startGeneration = useStartGeneration()

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: selectedType === 'pdf' ? { 'application/pdf': ['.pdf'] } : { 'image/*': [] },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      setUploadedFile(acceptedFiles[0])
      if (!title) setTitle(acceptedFiles[0].name.replace(/\.[^/.]+$/, ''))
    },
  })

  const isFileInput = ['pdf', 'image', 'screenshot', 'handwritten'].includes(selectedType)

  const handleSubmit = async () => {
    try {
      let projectId: string

      if (isFileInput && uploadedFile) {
        const formData = new FormData()
        formData.append('title', title)
        formData.append('description', description)
        formData.append('input_type', selectedType)
        formData.append('file', uploadedFile)
        const project = await createWithFile.mutateAsync(formData)
        projectId = project.id
      } else {
        const project = await createProject.mutateAsync({
          title,
          description,
          input_type: selectedType,
          input_text: inputText,
        })
        projectId = project.id
      }

      // Start generation
      const job = await startGeneration.mutateAsync({
        project_id: projectId,
        quality: quality as 'low_quality' | 'medium_quality' | 'high_quality',
      })

      navigate(`/projects/${projectId}/generate?job=${job.id}`)
    } catch {
      // error handled in hooks
    }
  }

  const isLoading = createProject.isPending || createWithFile.isPending || startGeneration.isPending

  return (
    <div className="max-w-3xl mx-auto animate-slide-up">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Create Educational Video</h1>
        <p className="text-muted-foreground mt-1">AI will generate a fully animated Manim video from your content</p>
      </div>

      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-8">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center gap-2">
            <div className={cn(
              'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all',
              step >= s ? 'bg-primary text-white shadow-lg shadow-primary/30' : 'bg-white/10 text-muted-foreground'
            )}>
              {s}
            </div>
            {s < 3 && <div className={cn('w-12 h-0.5 transition-all', step > s ? 'bg-primary' : 'bg-white/10')} />}
          </div>
        ))}
        <span className="ml-2 text-xs text-muted-foreground">
          {['Select Input', 'Add Content', 'Configure'][step - 1]}
        </span>
      </div>

      <AnimatePresence mode="wait">
        {/* Step 1: Input type selection */}
        {step === 1 && (
          <motion.div key="step1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
            <div className="grid grid-cols-1 gap-3">
              {INPUT_TYPES.map(({ type, label, description, icon: Icon }) => (
                <motion.button
                  key={type}
                  whileHover={{ x: 4 }}
                  onClick={() => setSelectedType(type)}
                  className={cn(
                    'flex items-center gap-4 p-4 rounded-xl border text-left transition-all',
                    selectedType === type
                      ? 'bg-primary/15 border-primary/50 shadow-md shadow-primary/10'
                      : 'glass border-white/10 hover:border-white/20'
                  )}
                >
                  <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center shrink-0', selectedType === type ? 'bg-primary/20' : 'bg-white/10')}>
                    <Icon className={cn('w-5 h-5', selectedType === type ? 'text-primary' : 'text-muted-foreground')} />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{label}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
                  </div>
                  {selectedType === type && <ChevronRight className="w-4 h-4 text-primary" />}
                </motion.button>
              ))}
            </div>
            <div className="flex justify-end mt-6">
              <button onClick={() => setStep(2)} className="btn-glow bg-primary text-white px-6 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2">
                Continue <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 2: Content */}
        {step === 2 && (
          <motion.div key="step2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Project Title *</label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Introduction to Calculus: Derivatives"
                className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/30 transition-all"
              />
            </div>

            {isFileInput ? (
              <div>
                <label className="text-sm font-medium">Upload File *</label>
                <div
                  {...getRootProps()}
                  className={cn(
                    'mt-2 border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all',
                    isDragActive ? 'border-primary bg-primary/10' : 'border-white/20 hover:border-white/40',
                    uploadedFile && 'border-green-500/50 bg-green-500/5'
                  )}
                >
                  <input {...getInputProps()} />
                  {uploadedFile ? (
                    <div className="space-y-2">
                      <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center mx-auto">
                        <FileText className="w-6 h-6 text-green-400" />
                      </div>
                      <p className="font-medium text-sm">{uploadedFile.name}</p>
                      <p className="text-xs text-muted-foreground">{(uploadedFile.size / 1024).toFixed(1)} KB</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Upload className="w-10 h-10 text-muted-foreground mx-auto" />
                      <p className="text-sm font-medium">{isDragActive ? 'Drop here' : 'Drag & drop or click to browse'}</p>
                      <p className="text-xs text-muted-foreground">
                        {selectedType === 'pdf' ? 'PDF files only' : 'JPG, PNG, WebP supported'}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  {selectedType === 'topic' ? 'Educational Topic *' : 'Educational Content *'}
                </label>
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  rows={8}
                  placeholder={
                    selectedType === 'topic'
                      ? 'e.g., Explain the Pythagorean theorem with proof and real-world applications'
                      : 'Paste your educational content here...'
                  }
                  className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/30 transition-all resize-none"
                />
                <p className="text-xs text-muted-foreground text-right">{inputText.length} chars</p>
              </div>
            )}

            <div className="flex justify-between mt-4">
              <button onClick={() => setStep(1)} className="glass px-4 py-2.5 rounded-xl text-sm">Back</button>
              <button
                onClick={() => setStep(3)}
                disabled={!title || (isFileInput ? !uploadedFile : !inputText)}
                className="btn-glow bg-primary disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2"
              >
                Continue <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 3: Configure */}
        {step === 3 && (
          <motion.div key="step3" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-6">
            <div>
              <label className="text-sm font-medium mb-3 block">Render Quality</label>
              <div className="grid grid-cols-3 gap-3">
                {QUALITY_OPTIONS.map(({ value, label, desc }) => (
                  <button
                    key={value}
                    onClick={() => setQuality(value)}
                    className={cn(
                      'p-4 rounded-xl border text-center transition-all',
                      quality === value ? 'bg-primary/15 border-primary/50' : 'glass border-white/10'
                    )}
                  >
                    <p className="font-medium text-sm">{label}</p>
                    <p className="text-xs text-muted-foreground mt-1">{desc}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Summary */}
            <div className="glass rounded-xl p-5 space-y-3">
              <h3 className="font-semibold text-sm">Project Summary</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Title</span>
                  <span className="font-medium truncate max-w-48">{title}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Input Type</span>
                  <span className="capitalize">{selectedType}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Quality</span>
                  <span>{QUALITY_OPTIONS.find(q => q.value === quality)?.label}</span>
                </div>
              </div>
            </div>

            <div className="flex justify-between">
              <button onClick={() => setStep(2)} className="glass px-4 py-2.5 rounded-xl text-sm">Back</button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleSubmit}
                disabled={isLoading}
                className="btn-glow bg-gradient-to-r from-primary to-purple-hot text-white px-8 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 shadow-lg disabled:opacity-70"
              >
                {isLoading ? (
                  <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</>
                ) : (
                  <><span>🚀</span> Generate Video</>
                )}
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
